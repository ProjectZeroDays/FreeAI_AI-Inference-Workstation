"""Flask middleware for automatic audit logging of all API requests.

Hooks into the Flask app via @app.before_request and @app.after_request
to log every request to /api/* (skipping health checks and static files).
"""
import fnmatch
import re
from datetime import datetime, timezone

from flask import request
from .logging import audit_log

# Routes and patterns to skip
_SKIP_PATHS = {"/health", "/api/health", "/static/"}
_SKIP_PATTERNS = [
    "*/health",
    "*/static/*",
    "*/favicon.ico",
]

# Route-to-action mapping for common patterns
_ROUTE_ACTION_MAP = [
    (r"^/api/agents", "agent_call"),
    (r"^/api/workflows", "workflow_exec"),
    (r"^/api/config", "config_change"),
    (r"^/api/deploy", "deploy"),
    (r"^/api/admin", "admin_action"),
    (r"^/api/auth", "login"),
    (r"^/api/login", "login"),
    (r"^/api/settings", "config_change"),
    (r"^/api/providers", "route_request"),
    (r"^/api/subagents", "agent_call"),
    (r"^/api/skills", "route_request"),
    (r"^/api/audit", "admin_action"),
]

# Pre-compile patterns
_COMPILED_ROUTES = [(re.compile(pat), action) for pat, action in _ROUTE_ACTION_MAP]


def _should_skip(path: str) -> bool:
    if path in _SKIP_PATHS:
        return True
    for pat in _SKIP_PATTERNS:
        if fnmatch.fnmatch(path, pat):
            return True
    return False


def _resolve_action(path: str) -> str:
    for pattern, action in _COMPILED_ROUTES:
        if pattern.match(path):
            return action
    return "route_request"


def _get_user_from_request(request):
    """Extract user identity from request headers or context."""
    # Check for auth token header
    token = request.headers.get("X-Auth-Token", "")
    if token:
        return "authed"
    # Check for user in JSON body
    if request.is_json:
        data = request.get_json(silent=True) or {}
        return data.get("user") or data.get("username") or "anonymous"
    return "anonymous"


def _get_ip(request):
    """Best-effort client IP extraction."""
    return (
        request.headers.get("X-Forwarded-For", "").split(",")[0].strip()
        or request.headers.get("X-Real-IP", "")
        or request.remote_addr
        or "127.0.0.1"
    )


def attach_audit_middleware(app):
    """Attach before/after request hooks to a Flask app for audit logging.

    Call this once after creating the Flask app:
        from audit.middleware import attach_audit_middleware
        attach_audit_middleware(app)
    """

    @app.before_request
    def _audit_before():
        path = request.path
        if path.startswith("/api/") and not _should_skip(path):
            request._audit_start = datetime.now(timezone.utc).timestamp()
            request._audit_user = _get_user_from_request(request)
            request._audit_ip = _get_ip(request)

    @app.after_request
    def _audit_after(response):
        start = getattr(request, "_audit_start", None)
        if start is None:
            return response
        path = request.path
        if not path.startswith("/api/"):
            return response
        if _should_skip(path):
            return response

        duration_ms = int((datetime.now(timezone.utc).timestamp() - start) * 1000)
        status = response.status_code
        action = _resolve_action(path)
        user = getattr(request, "_audit_user", "anonymous")
        ip = getattr(request, "_audit_ip", "127.0.0.1")

        audit_log(
            action=action,
            resource=path,
            user=user,
            result="ok" if status < 400 else "error",
            ip=ip,
            details={
                "method": request.method,
                "status": status,
                "duration_ms": duration_ms,
                "content_type": response.content_type,
            },
        )
        return response

    return app
