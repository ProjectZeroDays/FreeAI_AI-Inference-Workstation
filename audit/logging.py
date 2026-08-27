"""Structured audit logger for FreeAI.

Writes append-only JSONL records to config/audit.jsonl.
All sensitive fields (API keys, passwords, tokens) are redacted before persistence.
"""
import json
import os
import re
import threading
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional

ROOT = Path(__file__).parent.parent
CONFIG_DIR = ROOT / "config"
DEFAULT_AUDIT_LOG = CONFIG_DIR / "audit.jsonl"

# Values to redact – matches common secret patterns
_REDACT_PATTERNS = [
    re.compile(r"(api[_-]?key|apikey|access[_-]?token|bearer|secret|password|passwd|pwd|auth[_-]?token)\s*[:=]\s*['\"]?([A-Za-z0-9_\-\.]{8,})['\"]?", re.I),
    re.compile(r"sk[-_][a-zA-Z0-9]{20,}"),
    re.compile(r"eyJ[A-Za-z0-9_-]+\.eyJ[A-Za-z0-9_-]+"),
]

_SENSITIVE_KEYS = {
    "api_key", "apikey", "access_token", "bearer", "secret",
    "password", "passwd", "pwd", "auth_token", "token",
    "private_key", "client_secret", "credentials",
}

_audit_log_path = str(DEFAULT_AUDIT_LOG)
_lock = threading.Lock()
_action_counts = {}


def _redact_value(value: str) -> str:
    """Redact known secret patterns from a string value."""
    if not isinstance(value, str):
        value = str(value)
    for pat in _REDACT_PATTERNS:
        value = pat.sub("[REDACTED]", value)
    return value


def _redact_dict(d: dict) -> dict:
    """Recursively redact sensitive keys and values."""
    out = {}
    for k, v in d.items():
        if k.lower() in _SENSITIVE_KEYS or "key" in k.lower() or "token" in k.lower() or "secret" in k.lower() or "password" in k.lower():
            out[k] = "[REDACTED]"
        elif isinstance(v, str):
            out[k] = _redact_value(v)
        elif isinstance(v, dict):
            out[k] = _redact_dict(v)
        elif isinstance(v, list):
            out[k] = [_redact_dict(i) if isinstance(i, dict) else (_redact_value(i) if isinstance(i, str) else i) for i in v]
        else:
            out[k] = v
    return out


def set_audit_log_path(path: str) -> None:
    """Override the default audit log path (useful for tests)."""
    global _audit_log_path
    _audit_log_path = path


def audit_log(
    action: str,
    resource: str = "",
    user: str = "anonymous",
    result: str = "ok",
    ip: str = "",
    details: Dict[str, Any] = None,
) -> Dict[str, Any]:
    """Write a single audit record (append-only).

    Args:
        action: One of the canonical action types.
        resource: The resource being acted on.
        user: User identifier.
        result: "ok", "error", "forbidden", "skip".
        ip: Client IP address.
        details: Arbitrary extra context (redacted before write).

    Returns:
        The constructed log entry (before writing).
    """
    valid_actions = {
        "login", "route_request", "agent_call", "workflow_exec",
        "config_change", "deploy", "admin_action",
    }
    if action not in valid_actions:
        action = "admin_action"

    entry = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "user": user,
        "action": action,
        "resource": resource,
        "result": result,
        "ip": ip,
        "details": _redact_dict(details or {}),
    }

    try:
        path = Path(_audit_log_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        with _lock:
            with open(path, "a", encoding="utf-8") as f:
                f.write(json.dumps(entry, ensure_ascii=False) + "\n")
        _action_counts[action] = _action_counts.get(action, 0) + 1
    except OSError:
        pass

    return entry


def read_audit_log(limit: int = 200, offset: int = 0) -> list:
    """Read audit log entries (newest-first, sliced)."""
    path = Path(_audit_log_path)
    if not path.exists():
        return []
    entries = []
    try:
        with open(path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    try:
                        entries.append(json.loads(line))
                    except json.JSONDecodeError:
                        continue
    except OSError:
        return []
    # newest first
    entries.reverse()
    total = len(entries)
    return entries[offset:offset + limit], total


def clear_audit_log() -> int:
    """Truncate the audit log. Returns number of entries removed."""
    path = Path(_audit_log_path)
    if not path.exists():
        return 0
    try:
        count = sum(1 for _ in open(path, encoding="utf-8"))
        path.write_text("", encoding="utf-8")
        return count
    except OSError:
        return 0


def get_action_summary() -> Dict[str, Any]:
    """Return counts per action from the current in-memory tracker."""
    return dict(_action_counts)


class AuditLogger:
    """Optional class-based wrapper for structured audit logging."""

    def __init__(self, log_path: str = None):
        if log_path:
            set_audit_log_path(log_path)

    def login(self, user: str, ip: str = "", success: bool = True):
        audit_log("login", resource="auth", user=user,
                  result="ok" if success else "error", ip=ip)

    def route_request(self, method: str, path: str, status: int, user: str = "anonymous", ip: str = ""):
        audit_log("route_request", resource=path, user=user,
                  result="ok" if status < 400 else "error", ip=ip,
                  details={"method": method, "status": status})

    def agent_call(self, agent: str, prompt: str, user: str = "anonymous", ip: str = "", success: bool = True):
        audit_log("agent_call", resource=f"agent:{agent}", user=user,
                  result="ok" if success else "error", ip=ip,
                  details={"prompt_preview": prompt[:200]})

    def workflow_exec(self, workflow: str, user: str = "anonymous", ip: str = "", success: bool = True):
        audit_log("workflow_exec", resource=f"workflow:{workflow}", user=user,
                  result="ok" if success else "error", ip=ip)

    def config_change(self, setting: str, old_val: Any, new_val: Any, user: str = "admin", ip: str = ""):
        audit_log("config_change", resource="config", user=user, ip=ip,
                  details={"setting": setting, "old": old_val, "new": new_val})

    def deploy(self, target: str, user: str = "admin", ip: str = "", success: bool = True):
        audit_log("deploy", resource=target, user=user,
                  result="ok" if success else "error", ip=ip)

    def admin_action(self, action: str, resource: str = "", user: str = "admin", ip: str = "", details: dict = None):
        audit_log("admin_action", resource=resource, user=user, ip=ip,
                  details={"sub_action": action, **(details or {})})
