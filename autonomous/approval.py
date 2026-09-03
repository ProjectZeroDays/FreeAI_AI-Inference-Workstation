"""Human-in-the-loop (HITL) authorization gates for autonomous agents.

Provides approval checkpoints for destructive or high-privilege operations
executed by GODMODE/campaign services and the autonomous SDLC agent.

Approval states: pending, approved, rejected, timeout
Operations are persisted to config/hitl_requests.json for audit trail.
"""
import json
import os
import threading
import time
from pathlib import Path
from typing import Dict, List, Optional

try:
    from fastapi import FastAPI, HTTPException
    from fastapi.middleware.cors import CORSMiddleware
    from pydantic import BaseModel
    HAS_FASTAPI = True
except ImportError:
    HAS_FASTAPI = False

ROOT = Path(__file__).parent.parent
CONFIG_DIR = ROOT / "config"
HITL_STATE_PATH = CONFIG_DIR / "hitl_requests.json"
HITL_ENABLED = os.environ.get("HITL_ENABLED", "1") == "1"
HITL_APPROVAL_TIMEOUT_S = int(os.environ.get("HITL_APPROVAL_TIMEOUT_S", "300"))

_APPROVAL_LOCK = threading.Lock()
_PENDING: Dict[str, Dict] = {}


# ── Danger levels ───────────────────────────────────────────────────
DANGEROUS_PATTERNS = {
    "file_deletion": [
        "rm -rf", "unlink", "remove.*recursive", "shred",
        "truncate", "dd if=/dev/zero", "mkfs",
    ],
    "network_exploit": [
        "exploit", "payload", "reverse_shell", "bind_shell",
        "metasploit", "msfconsole", "nc -e", "ncat --sh-exec",
    ],
    "credential_theft": [
        "dump", "hash", "credential", "passwd", "shadow",
        "sudo", "privilege_escalation", "kitkat",
    ],
    "persistence": [
        "crontab", "systemd", "startup", "autorun",
        "rc.local", "profile.d", "launchctl",
    ],
    "data_exfil": [
        "curl.*pipe", "nc.*send", "scp.*.", "rsync.*-",
        "base64.*encode.*pipe", "xxd.*pipe",
    ],
    "infrastructure_destroy": [
        "docker.*rm.*-f", "kubectl.*delete", "terraform.*destroy",
        "drop.*table", "truncate.*table", "DROP DATABASE",
    ],
}


def _load_requests() -> dict:
    if HITL_STATE_PATH.exists():
        try:
            return json.loads(HITL_STATE_PATH.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            return {}
    return {}


def _save_requests(reqs: dict):
    HITL_STATE_PATH.parent.mkdir(parents=True, exist_ok=True)
    HITL_STATE_PATH.write_text(json.dumps(reqs, indent=2), encoding="utf-8")


def _detect_danger(command: str, context: str = "") -> List[str]:
    """Return list of matched danger patterns for a command."""
    matches = []
    cmd_lower = command.lower()
    ctx_lower = context.lower()
    combined = cmd_lower + " " + ctx_lower
    for category, patterns in DANGEROUS_PATTERNS.items():
        for pat in patterns:
            if pat.lower() in combined:
                matches.append(category)
                break
    return list(set(matches))


def request_approval(
    operator: str,
    action: str,
    target: str,
    command: str = "",
    context: str = "",
    risk_level: str = "medium",
) -> dict:
    """Submit an approval request. Returns the request dict."""
    if not HITL_ENABLED:
        return {"request_id": "auto-approved", "status": "approved",
                "auto_approved": True, "action": action,
                "reason": "HITL disabled"}

    req_id = f"{int(time.time())}_{os.getpid()}_{len(_PENDING)}"
    matches = _detect_danger(command, context) if command else []
    req = {
        "request_id": req_id,
        "operator": operator,
        "action": action,
        "target": target,
        "command": command,
        "context": context,
        "risk_level": risk_level,
        "danger_patterns": matches,
        "status": "pending",
        "created_at": time.time(),
        "expires_at": time.time() + HITL_APPROVAL_TIMEOUT_S,
        "approved_by": None,
        "approved_at": None,
        "rejection_reason": None,
    }
    with _APPROVAL_LOCK:
        _PENDING[req_id] = req
    _persist()
    return req


def approve_request(request_id: str, approver: str = "admin") -> dict:
    """Approve a pending request."""
    with _APPROVAL_LOCK:
        req = _PENDING.get(request_id)
        if not req:
            raise ValueError(f"Request not found: {request_id}")
        if req["status"] != "pending":
            raise ValueError(f"Request already {req['status']}")
        req["status"] = "approved"
        req["approved_by"] = approver
        req["approved_at"] = time.time()
    _persist()
    return dict(req)


def reject_request(request_id: str, reason: str = "", approver: str = "admin") -> dict:
    """Reject a pending request."""
    with _APPROVAL_LOCK:
        req = _PENDING.get(request_id)
        if not req:
            raise ValueError(f"Request not found: {request_id}")
        if req["status"] != "pending":
            raise ValueError(f"Request already {req['status']}")
        req["status"] = "rejected"
        req["approved_by"] = approver
        req["approved_at"] = time.time()
        req["rejection_reason"] = reason
    _persist()
    return dict(req)


def _persist():
    try:
        HITL_STATE_PATH.parent.mkdir(parents=True, exist_ok=True)
        HITL_STATE_PATH.write_text(
            json.dumps(dict(_PENDING), indent=2), encoding="utf-8")
    except OSError:
        pass


def check_approval_required(command: str, context: str = "") -> Optional[dict]:
    """Check if a command requires approval. Returns None if safe,
    or the pending approval request if one exists or was auto-created."""
    if not HITL_ENABLED:
        return None
    matches = _detect_danger(command, context)
    if not matches:
        return None
    # Auto-create approval request for dangerous commands
    req = request_approval(
        operator=os.environ.get("AGENT_OPERATOR", "unknown"),
        action="execute_command",
        target=context or command[:80],
        command=command,
        context=context,
        risk_level="high" if len(matches) > 1 else "medium",
    )
    return req


def is_approved(request_id: str) -> bool:
    """Check if a request ID has been approved."""
    if not HITL_ENABLED:
        return True
    with _APPROVAL_LOCK:
        req = _PENDING.get(request_id)
        if req is None:
            return True
        if req["status"] == "approved":
            return True
        if req["status"] == "rejected":
            return False
        if time.time() > req.get("expires_at", 0):
            req["status"] = "timeout"
            _persist()
            return False
    return False


def list_pending() -> List[dict]:
    """List all pending approval requests."""
    with _APPROVAL_LOCK:
        return [dict(r) for r in _PENDING.values()
                if r["status"] == "pending"]


def purge_expired():
    """Remove expired/timeout requests."""
    now = time.time()
    with _APPROVAL_LOCK:
        expired = [k for k, v in _PENDING.items()
                   if v["status"] == "pending" and v.get("expires_at", 0) < now]
        for k in expired:
            _PENDING[k]["status"] = "timeout"
        _persist()
    return len(expired)


# ── FastAPI app ────────────────────────────────────────────────────
if HAS_FASTAPI:
    app = FastAPI(title="HITL Approval API", version="1.0")
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:8030", "http://127.0.0.1:8030"],
        allow_methods=["*"],
        allow_headers=["*"],
    )

    class ApproveRequest(BaseModel):
        approver: str = "admin"

    class RejectRequest(BaseModel):
        approver: str = "admin"
        reason: str = ""

    @app.get("/health")
    def health():
        return {"status": "ok", "hitl_enabled": HITL_ENABLED}

    @app.get("/api/hitl/pending")
    def pending():
        return {"requests": list_pending()}

    @app.post("/api/hitl/{request_id}/approve")
    def approve(request_id: str, req: ApproveRequest):
        try:
            return approve_request(request_id, req.approver)
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))

    @app.post("/api/hitl/{request_id}/reject")
    def reject(request_id: str, req: RejectRequest):
        try:
            return reject_request(request_id, req.reason, req.approver)
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))

    @app.delete("/api/hitl/purge")
    def purge():
        return {"purged": purge_expired()}


if __name__ == "__main__":
    if HAS_FASTAPI:
        import uvicorn
        port = int(os.environ.get("HITL_PORT", "8197"))
        print(f"[hitl] Starting HITL Approval API on :{port}")
        uvicorn.run(app, host="0.0.0.0", port=port)
    else:
        print("[hitl] FastAPI not available. Use functions directly.")
