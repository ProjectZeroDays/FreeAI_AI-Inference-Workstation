"""RBAC API endpoints — Flask Blueprint."""
from flask import Blueprint, request, jsonify

from .rbac import (
    get_roles,
    get_users,
    set_user_role,
    remove_user,
    check_permission,
    check_role,
    update_permissions,
    ROLE_HIERARCHY,
)

rbac_bp = Blueprint("rbac", __name__, url_prefix="/api/rbac")

# GODMODE state (imported lazily to avoid circular deps)
_godmode_state = None


def _get_godmode():
    global _godmode_state
    if _godmode_state is None:
        try:
            import importlib.util
            spec = importlib.util.spec_from_file_location(
                "godmode",
                str(__import__("pathlib").Path(__file__).parent.parent / "agents" / "godmode.py")
            )
            mod = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(mod)
            _godmode_state = mod
        except Exception:
            _godmode_state = {"is_enabled": False, "state": {}}
    return _godmode_state


@rbac_bp.route("/godmode")
def godmode_status():
    gm = _get_godmode()
    if hasattr(gm, "is_enabled"):
        return jsonify({"godmode_enabled": gm.is_enabled()})
    return jsonify({"godmode_enabled": False, "note": "godmode module unavailable"})


@rbac_bp.route("/godmode/toggle", methods=["POST"])
def godmode_toggle():
    data = request.get_json(silent=True) or {}
    gm = _get_godmode()
    agent = data.get("agent", "")
    model = data.get("model", "")
    enable = data.get("enable", True)
    if hasattr(gm, "toggle_godmode"):
        result = gm.toggle_godmode(agent=agent, model=model, enable=enable)
        return jsonify(result)
    return jsonify({"error": "godmode module unavailable"}), 503


@rbac_bp.route("/godmode/campaign", methods=["POST"])
def godmode_campaign():
    data = request.get_json(silent=True) or {}
    gm = _get_godmode()
    if hasattr(gm, "set_campaign"):
        result = gm.set_campaign(data.get("name", ""), data.get("enable", True))
        return jsonify(result)
    return jsonify({"error": "godmode module unavailable"}), 503


@rbac_bp.route("/godmode/enable")
def godmode_enable():
    gm = _get_godmode()
    if hasattr(gm, "enable_godmode"):
        return jsonify(gm.enable_godmode())
    return jsonify({"error": "godmode module unavailable"}), 503


@rbac_bp.route("/godmode/disable")
def godmode_disable():
    gm = _get_godmode()
    if hasattr(gm, "disable_godmode"):
        return jsonify(gm.disable_godmode())
    return jsonify({"error": "godmode module unavailable"}), 503


@rbac_bp.route("/roles")
def list_roles():
    roles = get_roles()
    hierarchy = ROLE_HIERARCHY
    result = []
    for name, perms in roles.items():
        result.append({
            "name": name,
            "level": hierarchy.get(name, 0),
            "permissions": perms,
        })
    result.sort(key=lambda r: r["level"], reverse=True)
    return jsonify({"roles": result, "hierarchy": hierarchy})


@rbac_bp.route("/users", methods=["GET"])
def list_users():
    users = get_users()
    return jsonify({"users": users})


@rbac_bp.route("/users", methods=["POST"])
def add_user():
    data = request.get_json(silent=True) or {}
    username = data.get("username")
    role = data.get("role")
    if not username:
        return jsonify({"error": "username required"}), 400
    if role not in ROLE_HIERARCHY:
        return jsonify({"error": f"invalid role: {role}"}), 400
    new_role = set_user_role(username, role)
    return jsonify({"username": username, "role": new_role, "action": "added"})


@rbac_bp.route("/users/<username>", methods=["DELETE"])
def delete_user(username):
    removed = remove_user(username)
    if not removed:
        return jsonify({"error": "user not found"}), 404
    return jsonify({"username": username, "action": "deleted"})


@rbac_bp.route("/permissions", methods=["GET"])
def get_permissions():
    roles = get_roles()
    return jsonify({"permissions": roles})


@rbac_bp.route("/permissions", methods=["PUT"])
def set_permissions():
    data = request.get_json(silent=True) or {}
    new_roles = data.get("roles", {})
    if not isinstance(new_roles, dict):
        return jsonify({"error": "roles must be an object"}), 400
    updated = update_permissions(new_roles)
    return jsonify({"permissions": updated})


@rbac_bp.route("/check", methods=["POST"])
def check():
    data = request.get_json(silent=True) or {}
    resource = data.get("resource", "")
    action = data.get("action", "read")
    user = data.get("user")
    role = data.get("role")

    if user and not role:
        role = check_role(user)
    if not role:
        role = "admin"

    allowed = check_permission(resource, action, role)
    return jsonify({
        "allowed": allowed,
        "resource": resource,
        "action": action,
        "role": role,
    })
