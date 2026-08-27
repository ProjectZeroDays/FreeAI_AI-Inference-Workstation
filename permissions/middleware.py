"""RBAC middleware — Flask decorators for role and permission checks."""
import functools
from flask import request, jsonify, session

from .rbac import check_permission, check_role, get_roles, ROLE_HIERARCHY


def _get_current_role() -> str:
    return session.get("role", check_role("admin"))


SKIP_AUTH_ROUTES = {
    "/",
    "/dashboard",
    "/static",
    "/api/i18n/locales",
    "/api/i18n/strings",
    "/api/permissions",
    "/api/permissions/check",
    "/api/health",
    "/api/services",
    "/api/rbac/roles",
    "/api/rbac/check",
}


def _is_public_endpoint() -> bool:
    rule = request.endpoint or ""
    path = request.path
    if any(path.startswith(s) for s in SKIP_AUTH_ROUTES):
        return True
    if rule.startswith("static"):
        return True
    return False


def require_role(min_role: str):
    """Decorator: only allow requests from users with at least min_role."""
    def decorator(f):
        @functools.wraps(f)
        def wrapper(*args, **kwargs):
            if _is_public_endpoint():
                return f(*args, **kwargs)
            role = _get_current_role()
            role_level = ROLE_HIERARCHY.get(role, 0)
            min_level = ROLE_HIERARCHY.get(min_role, 0)
            if role_level < min_level:
                return jsonify({"error": "forbidden", "required": min_role, "has": role}), 403
            return f(*args, **kwargs)
        return wrapper
    return decorator


def require_permission(resource: str, action: str):
    """Decorator: only allow requests where the user has (resource, action) permission."""
    def decorator(f):
        @functools.wraps(f)
        def wrapper(*args, **kwargs):
            if _is_public_endpoint():
                return f(*args, **kwargs)
            role = _get_current_role()
            if not check_permission(resource, action, role):
                return jsonify({
                    "error": "forbidden",
                    "resource": resource,
                    "action": action,
                    "role": role,
                }), 403
            return f(*args, **kwargs)
        return wrapper
    return decorator
