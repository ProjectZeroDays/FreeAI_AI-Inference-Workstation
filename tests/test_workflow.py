"""Workflow engine tests: validation, retries, extraction, definitions,
versioning, pause/resume."""
import pytest
import time

requests = pytest.importorskip("requests")

try:
    from workflow.engine import (Step, Workflow, InlineStep,
                                  _extract_text, validate_workflow,
                                  from_definition,
                                  pause_workflow, resume_workflow,
                                  is_paused, get_pause_status,
                                  version_workflow, get_versions,
                                  _VERSIONS, _PAUSED, clear_versions)
except ImportError:
    from engine import (Step, Workflow, InlineStep,
                        _extract_text, validate_workflow,
                        from_definition,
                        pause_workflow, resume_workflow,
                        is_paused, get_pause_status,
                        version_workflow, get_versions,
                        _VERSIONS, _PAUSED, clear_versions)


def _noop(ctx):
    return {"prompt": ctx.get("spec", "")}


def test_extract_text_choices():
    assert _extract_text(
        {"response": {"choices": [{"text": "hi"}]}}) == "hi"


def test_extract_text_message_content():
    assert _extract_text({"response": {"choices": [
        {"message": {"content": "hello"}}]}}) == "hello"


def test_extract_text_legacy_content():
    assert _extract_text({"response": {"content": "yo"}}) == "yo"


def test_extract_text_empty():
    assert _extract_text({}) == ""
    assert _extract_text("not-a-dict") == ""


def test_validate_detects_missing_dependency():
    steps = [Step("b", "orchestrate", _noop, consumes=["a"])]
    warnings = validate_workflow(steps, initial_keys=[])
    assert any("'a'" in w for w in warnings)


def test_validate_ok_chain():
    steps = [
        Step("a", "analyze", _noop),
        Step("b", "orchestrate", _noop, consumes=["a"]),
    ]
    assert validate_workflow(steps, initial_keys=[]) == []


def test_validate_accepts_initial_context_keys():
    steps = [Step("b", "orchestrate", _noop, consumes=["spec"])]
    assert validate_workflow(steps, initial_keys=["spec"]) == []


def test_step_retries_then_raises(monkeypatch):
    calls = {"n": 0}

    def boom(*args, **kwargs):
        calls["n"] += 1
        raise ConnectionError("no backend")

    monkeypatch.setattr(requests, "post", boom)
    step = Step("s", "orchestrate", _noop)
    with pytest.raises(ConnectionError):
        step.run({"spec": "x"}, workflow_id="test")
    assert calls["n"] == 3


def test_inline_step_sends_payload_verbatim(monkeypatch):
    captured = {}

    def fake_post(url, json=None, timeout=None):
        captured["url"] = url
        captured["json"] = json

        class R:
            def raise_for_status(self):
                pass

            def json(self):
                return {"ok": True}

        return R()

    monkeypatch.setattr(requests, "post", fake_post)
    step = InlineStep("probe", "debug", {"code": "x", "error": "y"})
    out = step.run({}, workflow_id="t")
    assert out["probe"] == {"ok": True}
    assert captured["json"] == {"code": "x", "error": "y"}
    assert captured["url"].endswith("/agent/debug")


def test_definition_roundtrip():
    wf = from_definition({
        "name": "mini",
        "steps": [
            {"name": "one", "agent": "analyze",
             "payload": {"context": "c", "question": "q"}},
            {"name": "two", "agent": "orchestrate",
             "consumes": ["one"], "payload": {"prompt": "p"}},
        ],
    })
    assert wf.name == "mini"
    assert len(wf.steps) == 2
    assert isinstance(wf.steps[0], InlineStep)


# ── Pause / Resume tests ───────────────────────────────────────

@pytest.fixture(autouse=True)
def _cleanup_pause_and_version():
    """Ensure _PAUSED and _VERSIONS are cleared after each test."""
    yield
    _PAUSED.clear()
    clear_versions("test_pause_wf")
    clear_versions("test_pause_status_wf")
    clear_versions("test_version_wf")
    clear_versions("test_multi_ver_wf")
    clear_versions("class_ver_wf")
    clear_versions("test_empty_ver_wf")


def test_pause_and_resume_workflow():
    wf_name = "test_pause_wf"
    assert is_paused(wf_name) is False
    result = pause_workflow(wf_name)
    assert result is True
    assert is_paused(wf_name) is True
    resume_workflow(wf_name)
    assert is_paused(wf_name) is False


def test_get_pause_status():
    wf_name = "test_pause_status_wf"
    status = get_pause_status(wf_name)
    assert status["name"] == wf_name
    assert status["paused"] is False
    pause_workflow(wf_name)
    status = get_pause_status(wf_name)
    assert status["paused"] is True
    resume_workflow(wf_name)


def test_workflow_class_pause_resume():
    wf = Workflow("class_pause_wf", [Step("s", "a", _noop)])
    assert wf.get_pause_status()["paused"] is False
    wf.pause_workflow()
    assert wf.get_pause_status()["paused"] is True
    wf.resume_workflow()
    assert wf.get_pause_status()["paused"] is False


def test_paused_workflow_raises_on_execute(monkeypatch):
    monkeypatch.setattr(requests, "post", lambda *a, **kw: None)
    wf = Workflow("paused_exec_wf", [Step("s", "a", _noop)])
    pause_workflow("paused_exec_wf")
    with pytest.raises(RuntimeError, match="paused"):
        wf.execute({"spec": "test"})
    resume_workflow("paused_exec_wf")


# ── Versioning tests ────────────────────────────────────────────

def test_version_workflow_creates_memory_record():
    wf_name = "test_version_wf"
    clear_versions(wf_name)
    definition = {"name": wf_name, "steps": [{"name": "s1", "agent": "a"}]}
    result = version_workflow(wf_name, definition)
    assert "version" in result
    versions = get_versions(wf_name)
    assert len(versions) >= 1
    assert versions[0]["definition"] == definition
    clear_versions(wf_name)


def test_version_workflow_multiple_versions():
    wf_name = "test_multi_ver_wf"
    clear_versions(wf_name)
    version_workflow(wf_name, {"name": wf_name, "val": 1})
    time.sleep(0.01)
    version_workflow(wf_name, {"name": wf_name, "val": 2})
    versions = get_versions(wf_name)
    assert len(versions) >= 2
    assert versions[0]["definition"]["val"] == 1
    assert versions[1]["definition"]["val"] == 2
    clear_versions(wf_name)


def test_workflow_class_version_method():
    wf = Workflow("class_ver_wf", [Step("s", "a", _noop)])
    result = wf.version_workflow({"name": "class_ver_wf"})
    assert "version" in result
    versions = wf.get_versions()
    assert len(versions) >= 1
    assert wf.get_pause_status()["paused"] is False
    wf.pause_workflow()
    assert wf.get_pause_status()["paused"] is True
    wf.resume_workflow()
    assert wf.get_pause_status()["paused"] is False
    clear_versions("class_ver_wf")


def test_get_versions_empty():
    wf_name = "test_empty_ver_wf"
    clear_versions(wf_name)
    assert get_versions(wf_name) == []
