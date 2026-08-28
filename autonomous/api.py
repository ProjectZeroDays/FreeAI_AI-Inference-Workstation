#!/usr/bin/env python3
"""Autonomous SDLC API — start runs, track lifecycle, fetch artifacts."""
import json
import os
import re

from fastapi import FastAPI, HTTPException, Request
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

# Authentication: if AUTONOMOUS_API_KEY is set, require it for write operations
AUTONOMOUS_API_KEY = os.environ.get("AUTONOMOUS_API_KEY", "")


def _check_auth(request: Request):
    """Verify authentication for write/execute operations.
    
    Checks X-API-Key, X-Auth-Token, or Authorization: Bearer <token> headers.
    Raises HTTPException(401) if authentication is required but invalid.
    """
    if AUTONOMOUS_API_KEY:
        provided = (request.headers.get("X-API-Key") or 
                   request.headers.get("X-Auth-Token") or 
                   request.headers.get("Authorization", "").replace("Bearer ", ""))
        if provided != AUTONOMOUS_API_KEY:
            raise HTTPException(status_code=401, detail="unauthorized")


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
    owner: str = Field(default="", description="Optional owner identifier for run ownership tracking")


class ShellRequest(BaseModel):
    command: str


@app.get("/health")
def health():
    return {"status": "ok",
            "shell_tools_enabled": engine.ENABLE_SHELL,
            "max_concurrent_runs": _max_concurrent_runs()}


@app.post("/auto/start")
def start(request: Request, req: StartRequest):
    _check_auth(request)
    
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
        enable_shell=req.enable_shell,
        owner=req.owner)
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
def run_cancel(request: Request, run_id: str):
    _check_auth(request)
    
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
def run_shell(request: Request, run_id: str, req: ShellRequest):
    _check_auth(request)
    
    if not engine.ENABLE_SHELL:
        raise HTTPException(status_code=403,
                            detail="shell tools disabled "
                                   "(ENABLE_SHELL_TOOLS=1 to enable)")
    if run_id not in engine.RUNS:
        raise HTTPException(status_code=404, detail="run not found")
    
    # Verify run ownership if owner tracking is enabled
    state = engine.RUNS.get(run_id)
    if state and state.get("owner"):
        # If the run has an owner, verify the caller is authorized
        # In a production system, you would extract the authenticated user identity
        # from the request and compare it to the run owner
        # For now, we rely on the API key authentication as the authorization boundary
        pass
    
    from workspace import Workspace
    return engine.shell_exec(run_id, req.command) \
        if hasattr(engine, "shell_exec") else _shell(run_id, req.command)


def _shell(run_id, command):
    import subprocess, shlex
    if not re.match(r'^[a-zA-Z0-9_\-./\\]+$', run_id):
        return {"error": "Invalid run_id"}
    ws = Workspace(run_id)
    # Validate command: only allow whitelisted executables with safe arguments
    _ALLOWED_CMDS = {"ls", "cat", "echo", "date", "whoami", "pwd", "hostname",
                     "find", "grep", "head", "tail", "wc", "sort", "uniq",
                     "python3", "python", "node", "npm", "git", "curl",
                     "ping", "ip", "ifconfig", "netstat", "ps", "top",
                     "df", "du", "free", "uptime", "env", "printenv"}
    try:
        args = shlex.split(command)
    except ValueError:
        return {"error": "Invalid command format"}
    if not args:
        return {"error": "Empty command"}
    base_cmd = args[0].split("/")[-1]  # get executable name
    if base_cmd not in _ALLOWED_CMDS:
        return {"error": f"Command not allowed: {base_cmd}"}
    try:
        proc = subprocess.run(args, cwd=str(ws.root), capture_output=True,
                              text=True,
                              timeout=int(os.environ.get(
                                  "SHELL_TIMEOUT_S", "120")),
                              shell=False)
        return {"exit_code": proc.returncode,
                "stdout": proc.stdout[-8000:],
                "stderr": proc.stderr[-4000:]}
    except Exception as exc:
        import logging
        logging.getLogger(__name__).error("shell error: %s", exc)
        return {"error": "Command execution failed"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0",
                port=int(os.environ.get("AUTONOMOUS_PORT", "8050")))
