#!/usr/bin/env python3
"""Autonomous SDLC API — start runs, track lifecycle, fetch artifacts."""
import json
import os

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field

try:
    from autonomous import agent as engine
except ImportError:
    import agent as engine  # type: ignore

app = FastAPI(title="FreeAI Autonomous SDLC", version="1.0")

_SETTINGS_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "config", "runtime-settings.json")


def _max_concurrent_runs() -> int:
    """Concurrency cap from the shared settings file (dashboard-editable)."""
    try:
        with open(_SETTINGS_PATH) as f:
            return max(1, int(json.load(f).get("max_concurrent_runs", 3)))
    except (OSError, ValueError, TypeError):
        return 3


class StartRequest(BaseModel):
    spec: str
    profile: str = "balanced"
    max_tasks: int = 8
    enable_shell: bool = False


class ShellRequest(BaseModel):
    command: str


@app.get("/health")
def health():
    return {"status": "ok",
            "shell_tools_enabled": engine.ENABLE_SHELL,
            "max_concurrent_runs": _max_concurrent_runs()}


@app.post("/auto/start")
def start(req: StartRequest):
    if not req.spec.strip():
        raise HTTPException(status_code=400, detail="spec is required")

    terminal = {"done", "failed", "cancelled"}
    active = sum(1 for r in engine.RUNS.values()
                 if r.get("status") not in terminal)
    cap = _max_concurrent_runs()
    if active >= cap:
        raise HTTPException(
            status_code=429,
            detail=f"concurrency cap reached ({active}/{cap} active) — "
                   f"raise 'max_concurrent_runs' in dashboard Settings")

    run_id = engine.start_async(
        req.spec, profile=req.profile,
        max_tasks=max(1, min(req.max_tasks, 16)),
        enable_shell=req.enable_shell)
    return {"run_id": run_id}


@app.get("/auto/runs")
def runs():
    return {"runs": engine.list_runs()}


@app.get("/auto/runs/{run_id}")
def run_detail(run_id: str):
    state = engine.RUNS.get(run_id)
    if not state:
        raise HTTPException(status_code=404, detail="run not found")
    return state


@app.post("/auto/runs/{run_id}/cancel")
def run_cancel(run_id: str):
    if not engine.cancel(run_id):
        raise HTTPException(status_code=404, detail="run not found")
    return {"status": "cancelling"}


@app.get("/auto/runs/{run_id}/artifact")
def run_artifact(run_id: str):
    from workspace import Workspace

    state = engine.RUNS.get(run_id)
    path = Workspace(run_id).artifact_path()
    if not (state or os.path.exists(path)) or not os.path.exists(path):
        raise HTTPException(status_code=404,
                            detail="artifact not ready")
    return FileResponse(path, media_type="application/gzip",
                        filename=f"{run_id}.tar.gz")


@app.post("/auto/runs/{run_id}/shell")
def run_shell(run_id: str, req: ShellRequest):
    if not engine.ENABLE_SHELL:
        raise HTTPException(status_code=403,
                            detail="shell tools disabled "
                                   "(ENABLE_SHELL_TOOLS=1 to enable)")
    if run_id not in engine.RUNS:
        raise HTTPException(status_code=404, detail="run not found")
    from workspace import Workspace
    return engine.shell_exec(run_id, req.command) \
        if hasattr(engine, "shell_exec") else _shell(run_id, req.command)


def _shell(run_id, command):
    import subprocess
    ws = Workspace(run_id)
    try:
        proc = subprocess.run(command, cwd=ws.root, capture_output=True,
                              text=True,
                              timeout=int(os.environ.get(
                                  "SHELL_TIMEOUT_S", "120")),
                              shell=True)
        return {"exit_code": proc.returncode,
                "stdout": proc.stdout[-8000:],
                "stderr": proc.stderr[-4000:]}
    except Exception as exc:
        return {"error": str(exc)}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0",
                port=int(os.environ.get("AUTONOMOUS_PORT", "8050")))
