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
