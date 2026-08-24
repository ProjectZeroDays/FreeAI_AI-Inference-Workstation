"""Autonomous SDLC tests — fully offline via scripted LLM responses."""
import io
import os
import tarfile

import pytest

requests = pytest.importorskip("requests")

from autonomous import agent as engine  # noqa: E402
from autonomous.workspace import Workspace  # noqa: E402
from autonomous.prompts import (parse_plan, parse_file_blocks,  # noqa: E402
                                parse_verdict, static_issues,
                                detect_commands)


# --------------------------- parser units ---------------------------

def test_parse_plan_handles_fenced_json():
    raw = "```json\n[{\"id\": \"a\", \"title\": \"T\", " \
          "\"detail\": \"d\", \"files\": [\"x.py\"]}]\n```"
    plan = parse_plan(raw)
    assert len(plan) == 1 and plan[0]["title"] == "T"


def test_parse_plan_garbage_returns_empty():
    assert parse_plan("no json here at all") == []


def test_parse_file_blocks_multiple():
    raw = ("=== FILE: a/main.py ===\nprint('hi')\n=== END ===\n"
           "=== FILE: b/util.py ===\nx = 1\n=== END ===")
    blocks = parse_file_blocks(raw)
    assert [p for p, _ in blocks] == ["a/main.py", "b/util.py"]
    assert blocks[0][1] == "print('hi')"


def test_verdict_parsing():
    assert parse_verdict("VERDICT: PASS\n") == ("pass", [])
    v, issues = parse_verdict("VERDICT: FIX\n- missing README\n"
                              "- bad import in main")
    assert v == "fix" and len(issues) == 2


def test_static_issues_detect_placeholders():
    files = [{"path": "m.py", "bytes": 30}]
    issues = static_issues(files,
                           lambda p: "def f():\n    TODO\n" if p == "m.py"
                           else "")
    assert any("m.py" in i and "placeholder" in i for i in issues)


def test_detect_commands_python_stack():
    cmds = detect_commands(["main.py", "tests/test_main.py"])
    labels = [c[0] for c in cmds]
    assert "python:syntax" in labels
    assert "python:pytest" in labels


# ------------------------- workspace safety -------------------------

def test_workspace_blocks_traversal(tmp_path, monkeypatch):
    import autonomous.workspace as wsm
    monkeypatch.setattr(wsm, "WORKSPACES_DIR", str(tmp_path))
    ws = Workspace("run1")
    ws.init()
    with pytest.raises(ValueError):
        ws.write_file("../escape.txt", "nope")
    with pytest.raises(ValueError):
        ws.write_file("/etc/passwd", "nope")
    with pytest.raises(ValueError):
        ws.write_file("C:/temp/evil.txt", "nope")


def test_workspace_roundtrip_and_filtering(tmp_path, monkeypatch):
    import autonomous.workspace as wsm
    monkeypatch.setattr(wsm, "WORKSPACES_DIR", str(tmp_path))
    ws = Workspace("run2")
    ws.init()
    ws.write_file("src/app.py", "print(1)\n")
    with open(ws.artifact_path(), "wb") as f:
        f.write(b"x")
    names = [f["path"] for f in ws.list_files()]
    assert names == ["src/app.py"]


# --------------------------- lifecycle ---------------------------

class ScriptedLLM:
    """Returns canned responses keyed by which prompt phase fires."""

    def __init__(self, buggy_first=False):
        self.buggy_first = buggy_first
        self.calls = []

    def __call__(self, prompt, profile="balanced", max_tokens=4096):
        self.calls.append(prompt)
        if "autonomous software planner" in prompt:
            return ('[{"id":"task_1","title":"core","detail":"build it",'
                    '"files":["app.py"]},'
                    '{"id":"task_2","title":"cli","detail":"entry",'
                    '"files":["__main__.py"]}]')
        if "Fix every finding" in prompt:
            return "=== FILE: app.py ===\nvalue = 41 + 1\n=== END ==="
        if "strict code reviewer" in prompt:
            return "VERDICT: PASS"
        if "technical writer" in prompt:
            return ("=== FILE: README.md ===\n# Generated project\n"
                    "works.\n=== END ===")
        if "autonomous coding agent" in prompt:
            if self.buggy_first and "task_1" in prompt:
                return ("=== FILE: app.py ===\nvalue = 1\n"
                        "# TODO implement real logic\n=== END ===")
            if "task_2" in prompt:
                return "=== FILE: __main__.py ===\nprint(value)\n=== END ==="
            return "=== FILE: app.py ===\nvalue = 42\n=== END ==="
        raise AssertionError(f"unexpected prompt: {prompt[:80]}")


@pytest.fixture()
def offline(monkeypatch, tmp_path):
    import autonomous.workspace as wsm
    monkeypatch.setattr(wsm, "WORKSPACES_DIR", str(tmp_path))
    monkeypatch.setattr(engine, "ENABLE_SHELL", False)
    yield monkeypatch


def test_full_lifecycle_happy_path(offline):
    scripted = ScriptedLLM()
    offline.setattr(engine, "llm", scripted)

    state = engine.run_agent("Build a tiny python module", run_id="happy1")
    assert state["status"] == "done", state.get("error")
    assert state["report"]["tasks_total"] == 2
    assert state["report"]["tasks_failed"] == 0
    paths = {f["path"] for f in state["files"]}
    assert {"app.py", "__main__.py", "README.md"} <= paths
    assert state["review"]["verdict"] == "pass"
    assert state["artifact"]

    tar_path = Workspace("happy1").artifact_path()
    with tarfile.open(tar_path) as tar:
        members = tar.getnames()
    assert any(m.endswith("app.py") for m in members)
    assert not any("_run.json" in m for m in members)


def test_fix_loop_repairs_placeholder(offline):
    scripted = ScriptedLLM(buggy_first=True)
    offline.setattr(engine, "llm", scripted)

    state = engine.run_agent("Build a tiny python module",
                             run_id="fixloop1")
    assert state["status"] == "done", state.get("error")
    assert state["fix_rounds"] >= 1
    body = Workspace("fixloop1").read_file("app.py")
    assert "TODO" not in body
    # fixer was invoked exactly once (clean on re-scan)
    fix_calls = [p for p in scripted.calls
                 if "Fix every finding" in p]
    assert len(fix_calls) == 1


def test_cancellation_between_phases(offline):
    scripted = ScriptedLLM()
    offline.setattr(engine, "llm", scripted)
    engine.CANCEL.add("cancel1")
    state = engine.run_agent("spec", run_id="cancel1")
    assert state["status"] in ("cancelled", "done")
