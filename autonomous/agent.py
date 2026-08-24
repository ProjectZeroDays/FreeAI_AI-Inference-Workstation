#!/usr/bin/env python3
"""Autonomous full-lifecycle coding agent.

Phases: planning -> coding -> testing -> fixing -> documenting ->
        packaging -> done

Verification is real when ENABLE_SHELL_TOOLS=1 (compileall / pytest /
unittest / node --check run inside the sandboxed workspace); otherwise
a static placeholder/content scan gates the fix loop. Every LLM call
goes through the Agent API so router profiles, caching, and metrics
apply.
"""
import json
import os
import subprocess
import tarfile
import threading
import time
import uuid

import requests

try:
    from workflow.engine import _extract_text
except ImportError:
    from engine import _extract_text  # type: ignore

try:
    from autonomous.workspace import Workspace, WORKSPACES_DIR  # noqa: F401
    from autonomous.prompts import (PLAN_PROMPT, CODE_PROMPT, FIX_PROMPT,
                                    DOC_PROMPT, REVIEW_PROMPT, parse_plan,
                                    parse_file_blocks, parse_verdict,
                                    static_issues, detect_commands)
except ImportError:
    from workspace import Workspace, WORKSPACES_DIR  # noqa: F401
    from prompts import (PLAN_PROMPT, CODE_PROMPT, FIX_PROMPT,
                         DOC_PROMPT, REVIEW_PROMPT, parse_plan,
                         parse_file_blocks, parse_verdict,
                         static_issues, detect_commands)

AGENT_API = os.environ.get("AGENT_API", "http://localhost:8020")
ENABLE_SHELL = os.environ.get("ENABLE_SHELL_TOOLS", "0") == "1"
SHELL_TIMEOUT_S = int(os.environ.get("SHELL_TIMEOUT_S", "120"))
MAX_FIX_ROUNDS = int(os.environ.get("MAX_FIX_ROUNDS", "3"))

_LOCK = threading.Lock()
RUNS = {}
CANCEL = set()


def _cancelled(run_id):
    return run_id in CANCEL


def llm(prompt, profile="balanced", max_tokens=4096):
    r = requests.post(
        f"{AGENT_API}/agent/orchestrate",
        json={"prompt": prompt, "profile": profile,
              "max_tokens": max_tokens},
        timeout=660)
    r.raise_for_status()
    return _extract_text(r.json())


def tree_summary(files, cap=60):
    lines = [f"- {f['path']} ({f['bytes']}B)" for f in files[:cap]]
    if len(files) > cap:
        lines.append(f"... and {len(files) - cap} more")
    return "\n".join(lines) or "(empty)"


def code_sample(workspace, files, cap_chars=4000):
    parts, used = [], 0
    for f in files[:4]:
        try:
            body = workspace.read_file(f["path"])
        except OSError:
            continue
        chunk = f"--- {f['path']} ---\n{body[:1500]}"
        parts.append(chunk)
        used += len(chunk)
        if used > cap_chars:
            break
    return "\n\n".join(parts) or "(none)"


# ------------------------------------------------------------------
# Verification (real shell runs inside the workspace)
# ------------------------------------------------------------------

def run_verification(workspace) -> dict:
    files = workspace.list_files()
    commands = detect_commands([f["path"] for f in files])

    if not commands:
        issues = static_issues(files, lambda p: workspace.read_file(p))
        return {"ran": False, "results": [], "issues": issues}

    results = []
    for label, command in commands:
        if label == "python:pytest" and any(
                r["label"] == "python:pytest" and r["exit"] == 0
                for r in results):
            continue  # pytest passed; skip unittest fallback
        try:
            proc = subprocess.run(command, cwd=workspace.root,
                                  capture_output=True, text=True,
                                  timeout=SHELL_TIMEOUT_S)
            exit_code, out, err = proc.returncode, \
                proc.stdout[-4000:], proc.stderr[-2000:]
        except subprocess.TimeoutExpired:
            exit_code, out, err = -1, "", f"timeout after {SHELL_TIMEOUT_S}s"
        except FileNotFoundError as exc:
            exit_code, out, err = -1, "", f"tool missing: {exc}"
        results.append({"label": label, "command": command,
                        "exit": exit_code,
                        "output": (out + ("\n" + err if err else "")).strip()
                        [-3000:]})
        if exit_code != 0 and err:
            pass

    issues = []
    for r in results:
        if r["exit"] != 0:
            issues.append(f"[{r['label']}] {r['label']} failed "
                          f"(exit {r['exit']}):\n{r['output'][:1200]}")
    if not issues:
        issues.extend(static_issues(files,
                                    lambda p: workspace.read_file(p)))
    return {"ran": True, "results": results, "issues": issues}


def package_artifact(workspace, run_id) -> str:
    """Tar the project (excluding internal files) into _artifact.tar.gz."""
    art = workspace.artifact_path()
    with tarfile.open(art, "w:gz") as tar:
        for f in workspace.list_files():
            full = os.path.join(workspace.root, f["path"])
            arcname = os.path.join(run_id, f["path"])
            tar.add(full, arcname=arcname)
    return art


# ------------------------------------------------------------------
# Lifecycle runner
# ------------------------------------------------------------------

def run_agent(spec, profile="balanced", max_tasks=8,
              enable_shell=False, run_id=None):
    run_id = run_id or uuid.uuid4().hex[:12]
    use_shell = bool(enable_shell and ENABLE_SHELL)
    started = time.time()
    state = {
        "run_id": run_id,
        "spec": spec,
        "profile": profile,
        "enable_shell": use_shell,
        "status": "planning",
        "tasks": [],
        "files": [],
        "verification": None,
        "review": None,
        "fix_rounds": 0,
        "artifact": None,
        "report": {},
        "error": None,
        "created_at": started,
        "updated_at": started,
    }
    with _LOCK:
        RUNS[run_id] = state
    workspace = Workspace(run_id)
    workspace.init()

    def touch(status=None):
        if status:
            state["status"] = status
        state["updated_at"] = time.time()
        try:
            with open(os.path.join(workspace.root, "_run.json"), "w",
                      encoding="utf-8") as f:
                json.dump(state, f, indent=2, default=str)
        except OSError:
            pass

    def write_blocks(blocks) -> int:
        written = 0
        for path, content in blocks:
            try:
                workspace.write_file(path, content)
                written += 1
            except ValueError:
                continue
        state["files"] = workspace.list_files()
        return written

    try:
        # ------------------------- planning -------------------------
        raw = llm(PLAN_PROMPT.format(spec=spec, max_tasks=max_tasks),
                  profile=profile, max_tokens=2048)
        tasks = parse_plan(raw) or [{
            "id": "task_1", "title": "implement the spec",
            "detail": spec, "files": []}]
        state["tasks"] = [{"id": t["id"], "title": t["title"],
                           "detail": t["detail"], "status": "pending",
                           "files_written": [], "error": None}
                          for t in tasks]
        touch("coding")

        # -------------------------- coding --------------------------
        for task in state["tasks"]:
            if _cancelled(run_id):
                raise KeyboardInterrupt()
            prompt = CODE_PROMPT.format(
                spec=spec, tree=tree_summary(workspace.list_files()),
                task_id=task["id"], title=task["title"],
                detail=task["detail"])
            blocks = parse_file_blocks(llm(prompt, profile=profile,
                                           max_tokens=6144))
            task["files_written"] = [p for p, _ in blocks] if blocks else []
            n = write_blocks(blocks)
            task["status"] = "done" if n else ("failed")
            task["error"] = None if n else "no FILE blocks parsed"
            touch()

        # ------------------- testing / fix loop ---------------------
        while True:
            if _cancelled(run_id):
                raise KeyboardInterrupt()
            touch("testing")
            verification = (run_verification(workspace) if use_shell
                            else {"ran": False, "results": [],
                                  "issues": static_issues(
                                      workspace.list_files(),
                                      lambda p: workspace.read_file(p))})
            state["verification"] = verification
            touch()

            clean = not verification["issues"]
            if clean or state["fix_rounds"] >= MAX_FIX_ROUNDS:
                break

            state["fix_rounds"] += 1
            touch("fixing")
            fix_raw = llm(FIX_PROMPT.format(
                spec=spec, tree=tree_summary(workspace.list_files()),
                issues="\n\n".join(verification["issues"])[:6000]),
                profile=profile, max_tokens=6144)
            if not write_blocks(parse_file_blocks(fix_raw)):
                break  # model produced nothing fixable; stop looping

        # -------------------- optional review -----------------------
        touch("reviewing")
        review_raw = llm(REVIEW_PROMPT.format(
            spec=spec, tree=tree_summary(workspace.list_files()),
            sample=code_sample(workspace, workspace.list_files())),
            profile=profile, max_tokens=1024)
        verdict, issues = parse_verdict(review_raw)
        state["review"] = {"verdict": verdict, "issues": issues}
        touch()

        # ----------------------- documenting ------------------------
        if not _cancelled(run_id):
            touch("documenting")
            doc_blocks = parse_file_blocks(llm(DOC_PROMPT.format(
                spec=spec, tree=tree_summary(workspace.list_files()),
                sample=code_sample(workspace, workspace.list_files())),
                profile=profile, max_tokens=3072))
            write_blocks(doc_blocks)

        # ----------------------- packaging --------------------------
        if _cancelled(run_id):
            raise KeyboardInterrupt()
        touch("packaging")
        artifact = package_artifact(workspace, run_id)
        state["artifact"] = os.path.basename(artifact)

        total_bytes = sum(f["bytes"] for f in state["files"])
        failed = [t for t in state["tasks"] if t["status"] == "failed"]
        state["report"] = {
            "duration_s": round(time.time() - started, 1),
            "tasks_total": len(state["tasks"]),
            "tasks_failed": len(failed),
            "files": len(state["files"]),
            "bytes": total_bytes,
            "fix_rounds": state["fix_rounds"],
            "verification_ran": state["verification"]["ran"]
            if state["verification"] else False,
            "review_verdict": verdict,
            "artifact": state["artifact"],
        }
        if _cancelled(run_id):
            state["status"] = "cancelled"
        elif failed and len(failed) == len(state["tasks"]):
            state["status"] = "failed"
            state["error"] = "all tasks failed to produce files"
        else:
            state["status"] = "done"
    except KeyboardInterrupt:
        state["status"] = "cancelled"
    except Exception as exc:
        state["status"] = "failed"
        state["error"] = str(exc)
    finally:
        CANCEL.discard(run_id)
        touch()
    return state


def start_async(spec, **kwargs):
    run_id = uuid.uuid4().hex[:12]
    placeholder = {
        "run_id": run_id, "spec": spec, "status": "queued",
        "tasks": [], "files": [], "verification": None, "review": None,
        "fix_rounds": 0, "artifact": None, "report": {}, "error": None,
        "enable_shell": bool(kwargs.get("enable_shell", False)
                             and ENABLE_SHELL),
        "created_at": time.time(), "updated_at": time.time(),
    }
    with _LOCK:
        RUNS[run_id] = placeholder
    threading.Thread(target=run_agent,
                     kwargs={**kwargs, "spec": spec, "run_id": run_id},
                     daemon=True).start()
    return run_id


def cancel(run_id):
    with _LOCK:
        if run_id in RUNS:
            CANCEL.add(run_id)
            return True
    return False


def list_runs():
    with _LOCK:
        return [{k: r[k] for k in ("run_id", "spec", "status",
                                   "created_at")}
                for r in sorted(RUNS.values(),
                                key=lambda s: s["created_at"],
                                reverse=True)]
