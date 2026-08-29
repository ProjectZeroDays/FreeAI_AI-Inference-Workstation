"""RBAC (Role-Based Access Control) for FreeAI dashboard.

Provides @login_required, @require_role decorators, a permission map,
and a before_request hook that enforces them across all API routes.
Middleware is ONLY active when AUTH_JWT_SECRET is set.
"""
import functools
import threading
from typing import Callable

from auth.users import users_store, require_role as _require_role_checker


# ── Decorators ────────────────────────────────────────────────────

def login_required(f: Callable) -> Callable:
    """Require a valid Bearer JWT. Returns 401 JSON on failure."""
    @functools.wraps(f)
    def wrapper(*args, **kwargs):
        from flask import request, jsonify, g
        auth_header = request.headers.get("Authorization", "").strip()
        if not auth_header.startswith("Bearer "):
            return jsonify({"error": "unauthorized"}), 401
        token = auth_header[len("Bearer "):].strip()
        from auth.jwt import decode_token
        payload = decode_token(token)
        if not payload or payload.get("type") != "access":
            return jsonify({"error": "unauthorized"}), 401
        user_info = users_store.get_user(payload["sub"])
        if not user_info:
            return jsonify({"error": "unauthorized"}), 401
        g.current_user = {"username": payload["sub"], "role": user_info["role"]}
        return f(*args, **kwargs)
    return wrapper


def require_role(min_role: str) -> Callable:
    """Require the caller to have at least min_role. Returns 403 on failure."""
    def decorator(f: Callable) -> Callable:
        @functools.wraps(f)
        def wrapper(*args, **kwargs):
            from flask import request, jsonify, g
            auth_header = request.headers.get("Authorization", "").strip()
            if not auth_header.startswith("Bearer "):
                return jsonify({"error": "unauthorized"}), 401
            token = auth_header[len("Bearer "):].strip()
            from auth.jwt import decode_token
            payload = decode_token(token)
            if not payload or payload.get("type") != "access":
                return jsonify({"error": "unauthorized"}), 401
            user_info = users_store.get_user(payload["sub"])
            if not user_info:
                return jsonify({"error": "unauthorized"}), 401
            checker = _require_role_checker(min_role)
            if checker({"username": payload["sub"], "role": user_info["role"]}) is None:
                return jsonify({"error": "forbidden"}), 403
            g.current_user = {"username": payload["sub"], "role": user_info["role"]}
            return f(*args, **kwargs)
        return wrapper
    return decorator


# ── Permission map ────────────────────────────────────────────────
# Pattern: route_pattern -> {"method": "required_role_or_None"}
# None = public. Roles: admin > developer > viewer.

_PERMISSION_MAP: list[dict] = [
    # ── Public (no auth) ────────────────────────────────────────
    {"pattern": "/", "methods": ["GET"], "role": None},
    {"pattern": "/dashboard", "methods": ["GET"], "role": None},
    {"pattern": "/static/", "methods": ["GET"], "role": None},
    {"pattern": "/auth/login", "methods": ["GET", "POST"], "role": None},
    {"pattern": "/auth/refresh", "methods": ["POST"], "role": None},
    {"pattern": "/auth/me", "methods": ["GET"], "role": None},
    {"pattern": "/health", "methods": ["GET"], "role": None},
    {"pattern": "/api/health", "methods": ["GET"], "role": None},
    {"pattern": "/api/health/full", "methods": ["GET"], "role": None},
    {"pattern": "/api/health/alerts", "methods": ["GET"], "role": None},
    {"pattern": "/api/stats", "methods": ["GET"], "role": None},
    {"pattern": "/api/services", "methods": ["GET"], "role": None},
    {"pattern": "/api/skills/aggregated", "methods": ["GET"], "role": None},
    {"pattern": "/api/providers", "methods": ["GET"], "role": None},
    {"pattern": "/api/models-status", "methods": ["GET"], "role": None},
    {"pattern": "/api/status", "methods": ["GET"], "role": None},
    {"pattern": "/api/i18n/locales", "methods": ["GET"], "role": None},
    {"pattern": "/api/i18n/strings/", "methods": ["GET"], "role": None},
    {"pattern": "/api/scheduler", "methods": ["GET"], "role": None},
    {"pattern": "/api/scheduler/jobs", "methods": ["GET"], "role": None},
    {"pattern": "/api/gpu", "methods": ["GET"], "role": None},
    {"pattern": "/api/gpu/metrics", "methods": ["GET"], "role": None},
    {"pattern": "/api/gateway/status", "methods": ["GET"], "role": None},
    {"pattern": "/api/gateway/messages", "methods": ["GET"], "role": None},
    {"pattern": "/api/gateway/stats", "methods": ["GET"], "role": None},
    # ── Viewer+ (any authenticated user) ────────────────────────
    {"pattern": "/api/config", "methods": ["GET"], "role": "viewer"},
    {"pattern": "/api/browser/settings", "methods": ["GET"], "role": "viewer"},
    {"pattern": "/api/skills", "methods": ["GET"], "role": "viewer"},
    {"pattern": "/api/skills/activity", "methods": ["GET"], "role": "viewer"},
    {"pattern": "/api/memory", "methods": ["GET"], "role": "viewer"},
    {"pattern": "/api/memory/preferences", "methods": ["GET"], "role": "viewer"},
    {"pattern": "/api/memory/projects", "methods": ["GET"], "role": "viewer"},
    {"pattern": "/api/memory/learnings", "methods": ["GET"], "role": "viewer"},
    {"pattern": "/api/memory/stats", "methods": ["GET"], "role": "viewer"},
    {"pattern": "/api/automations", "methods": ["GET"], "role": "viewer"},
    {"pattern": "/api/automations/history", "methods": ["GET"], "role": "viewer"},
    {"pattern": "/api/automations/stats", "methods": ["GET"], "role": "viewer"},
    {"pattern": "/api/gateway", "methods": ["GET"], "role": "viewer"},
    {"pattern": "/api/gateway/platforms", "methods": ["GET"], "role": "viewer"},
    {"pattern": "/api/hermes-status", "methods": ["GET"], "role": "viewer"},
    {"pattern": "/api/permissions", "methods": ["GET"], "role": "viewer"},
    {"pattern": "/api/subagents", "methods": ["GET"], "role": "viewer"},
    {"pattern": "/api/training", "methods": ["GET"], "role": "viewer"},
    {"pattern": "/api/training/datasets", "methods": ["GET"], "role": "viewer"},
    {"pattern": "/api/training/models", "methods": ["GET"], "role": "viewer"},
    {"pattern": "/api/providers/test", "methods": ["GET", "POST"], "role": "viewer"},
    {"pattern": "/api/shodan/search", "methods": ["GET", "POST"], "role": "viewer"},
    {"pattern": "/api/shodan/host/", "methods": ["GET"], "role": "viewer"},
    {"pattern": "/api/shodan/health", "methods": ["GET"], "role": "viewer"},
    {"pattern": "/api/shodan/key", "methods": ["GET", "PUT"], "role": "viewer"},
    # ── Developer+ (admin + developer) ──────────────────────────
    {"pattern": "/api/browser/settings", "methods": ["POST"], "role": "developer"},
    {"pattern": "/api/browser/reset", "methods": ["POST"], "role": "developer"},
    {"pattern": "/api/skills/save", "methods": ["POST"], "role": "developer"},
    {"pattern": "/api/skills/delete/", "methods": ["DELETE"], "role": "developer"},
    {"pattern": "/api/skills/scan", "methods": ["POST"], "role": "developer"},
    {"pattern": "/api/skills/log", "methods": ["POST"], "role": "developer"},
    {"pattern": "/api/skills/catalog", "methods": ["GET"], "role": "developer"},
    {"pattern": "/api/skills/catalog/refresh", "methods": ["POST"], "role": "developer"},
    {"pattern": "/api/health/trigger", "methods": ["POST"], "role": "developer"},
    {"pattern": "/api/config", "methods": ["POST"], "role": "developer"},
    {"pattern": "/api/memory/preferences", "methods": ["POST"], "role": "developer"},
    {"pattern": "/api/memory/projects", "methods": ["POST"], "role": "developer"},
    {"pattern": "/api/memory/projects/", "methods": ["DELETE"], "role": "developer"},
    {"pattern": "/api/memory/learnings", "methods": ["POST"], "role": "developer"},
    {"pattern": "/api/automations", "methods": ["POST"], "role": "developer"},
    {"pattern": "/api/automations/", "methods": ["POST"], "role": "developer"},
    {"pattern": "/api/automations/", "methods": ["DELETE"], "role": "developer"},
    {"pattern": "/api/gateway/platforms/", "methods": ["POST"], "role": "developer"},
    {"pattern": "/api/gateway/platforms/", "methods": ["DELETE"], "role": "developer"},
    {"pattern": "/api/gateway/messages", "methods": ["POST"], "role": "developer"},
    {"pattern": "/api/gateway/voice/transcribe", "methods": ["POST"], "role": "developer"},
    {"pattern": "/api/gateway/transfer", "methods": ["POST"], "role": "developer"},
    {"pattern": "/api/hermes/proxy/", "methods": ["GET", "POST", "PUT", "DELETE"], "role": "developer"},
    {"pattern": "/api/subagents", "methods": ["POST"], "role": "developer"},
    {"pattern": "/api/subagents/", "methods": ["DELETE"], "role": "developer"},
    {"pattern": "/api/subagents/", "methods": ["POST"], "role": "developer"},
    {"pattern": "/api/subagents/", "methods": ["GET"], "role": "developer"},
    {"pattern": "/api/training/datasets", "methods": ["POST"], "role": "developer"},
    {"pattern": "/api/training/datasets/", "methods": ["DELETE"], "role": "developer"},
    {"pattern": "/api/training/jobs", "methods": ["POST"], "role": "developer"},
    {"pattern": "/api/training/abliterate", "methods": ["POST"], "role": "developer"},
    {"pattern": "/api/training/models/", "methods": ["DELETE"], "role": "developer"},
    {"pattern": "/api/training/models/", "methods": ["POST"], "role": "developer"},
    {"pattern": "/api/gpu/scan", "methods": ["POST"], "role": "developer"},
    {"pattern": "/api/gpu/perf/enable", "methods": ["POST"], "role": "developer"},
    {"pattern": "/api/gpu/perf/disable", "methods": ["POST"], "role": "developer"},
    {"pattern": "/api/gpu/perf/recommend", "methods": ["GET"], "role": "developer"},
    {"pattern": "/api/permissions/check", "methods": ["POST"], "role": "developer"},
    {"pattern": "/api/sandbox", "methods": ["GET"], "role": "developer"},
    {"pattern": "/api/sandbox/run", "methods": ["POST"], "role": "developer"},
    {"pattern": "/api/scheduler/jobs", "methods": ["POST"], "role": "developer"},
    {"pattern": "/api/scheduler/jobs/", "methods": ["POST"], "role": "developer"},
    {"pattern": "/api/wiki/content/", "methods": ["POST"], "role": "developer"},
    {"pattern": "/api/wiki/blog", "methods": ["POST"], "role": "developer"},
    {"pattern": "/api/wiki/forum", "methods": ["POST"], "role": "developer"},
    {"pattern": "/api/upload", "methods": ["POST"], "role": "developer"},
    {"pattern": "/api/uploads", "methods": ["GET"], "role": "developer"},
    {"pattern": "/api/skills/", "methods": ["GET"], "role": "developer"},
    # ── Admin-only ──────────────────────────────────────────────
    {"pattern": "/auth/users", "methods": ["GET"], "role": "admin"},
    {"pattern": "/auth/users", "methods": ["POST"], "role": "admin"},
    {"pattern": "/auth/users/", "methods": ["DELETE"], "role": "admin"},
    {"pattern": "/api/secrets", "methods": ["GET"], "role": "admin"},
    {"pattern": "/api/secrets", "methods": ["POST"], "role": "admin"},
    {"pattern": "/api/secrets/", "methods": ["DELETE"], "role": "admin"},
    {"pattern": "/api/settings/llama-restart", "methods": ["POST"], "role": "admin"},
    {"pattern": "/api/services/restart", "methods": ["POST"], "role": "admin"},
    {"pattern": "/api/scheduler/jobs/", "methods": ["DELETE"], "role": "admin"},
    {"pattern": "/api/audits/clear", "methods": ["POST"], "role": "admin"},
]

_permission_lock = threading.Lock()


def get_permission_map() -> list[dict]:
    """Return a copy of the permission map."""
    with _permission_lock:
        return list(_PERMISSION_MAP)


def set_permission_map(new_map: list[dict]) -> None:
    """Replace the permission map (used by tests)."""
    with _permission_lock:
        _PERMISSION_MAP[:] = new_map


def resolve_route_permission(path: str, method: str) -> str | None:
    """Return the required role for a path+method, or None (public).
    Prefers the longest matching pattern."""
    with _permission_lock:
        best_match: dict | None = None
        best_len = 0
        for entry in _PERMISSION_MAP:
            pattern = entry["pattern"]
            allowed_methods = entry["methods"]
            matches = False
            if path == pattern:
                matches = True
            elif pattern.endswith("/") and path.startswith(pattern):
                matches = True
            elif pattern != "/" and path.startswith(pattern + "/"):
                matches = True
            elif pattern != "/" and path.startswith(pattern):
                matches = True

            if matches:
                method_ok = False
                if allowed_methods is None:
                    method_ok = True
                elif isinstance(allowed_methods, list):
                    if "*" in allowed_methods:
                        method_ok = True
                    elif method in allowed_methods:
                        method_ok = True
                elif allowed_methods == method:
                    method_ok = True

                if method_ok and len(pattern) > best_len:
                    best_len = len(pattern)
                    best_match = entry

        if best_match is not None:
            return best_match["role"]
        return None


def apply_rbac_middleware(app) -> None:
    """Attach a before_request handler that enforces RBAC.

    Auth status is checked at REQUEST time (not import time) so that
    test fixtures can monkeypatch AUTH_JWT_SECRET and have it take effect.
    Skips non-API page routes entirely.
    """
    import os
    from flask import request, jsonify, g

    @app.before_request
    def _rbac_before_request():
        if not bool(os.environ.get("AUTH_JWT_SECRET", "").strip()):
            return None
        path = request.path
        if not (path.startswith("/api/") or path.startswith("/auth/")):
            return None
        required = resolve_route_permission(path, request.method)
        if required is None:
            return None
        auth_header = request.headers.get("Authorization", "").strip()
        if not auth_header.startswith("Bearer "):
            return jsonify({"error": "unauthorized"}), 401
        from auth.jwt import decode_token
        token = auth_header[len("Bearer "):].strip()
        payload = decode_token(token)
        if not payload or payload.get("type") != "access":
            return jsonify({"error": "unauthorized"}), 401
        user_info = users_store.get_user(payload["sub"])
        if not user_info:
            return jsonify({"error": "unauthorized"}), 401
        checker = _require_role_checker(required)
        if checker({"username": payload["sub"], "role": user_info["role"]}) is None:
            return jsonify({"error": "forbidden"}), 403
        g.current_user = {"username": payload["sub"], "role": user_info["role"]}
        return None
