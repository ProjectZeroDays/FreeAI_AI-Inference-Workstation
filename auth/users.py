"""In-memory user store backed by config/auth-users.json.

Users are hashed with bcrypt.  The store is loaded once at import time and
reloaded on demand via reload().
"""
import hashlib
import json
import os
import time
import threading
from pathlib import Path

import bcrypt

from auth.jwt import _get_secret

_ROOT = Path(__file__).parent.parent
_CONFIG_DIR = _ROOT / "config"
_USERS_PATH = _CONFIG_DIR / "auth-users.json"

ROLES = {"admin", "developer", "viewer"}
_DEFAULT_ROLE = "viewer"

# In-memory user cache: {username: {"password_hash": "...", "role": "..."}}
_users: dict = {}
_lock = threading.Lock()


def _hash_password(plaintext: str) -> str:
    """Hash a plaintext password with bcrypt and return the base64-encoded hash."""
    raw = bcrypt.hashpw(plaintext.encode("utf-8"), bcrypt.gensalt())
    return raw.decode("utf-8")


def _load_users() -> dict:
    """Load users from config/auth-users.json. Returns empty dict on failure."""
    try:
        data = json.loads(_USERS_PATH.read_text(encoding="utf-8"))
        raw = data.get("users", {})
        out = {}
        for username, info in raw.items():
            pwd_hash = info.get("password_hash", "")
            role = info.get("role", _DEFAULT_ROLE)
            if role not in ROLES:
                role = _DEFAULT_ROLE
            out[username] = {"password_hash": pwd_hash, "role": role}
        return out
    except (OSError, json.JSONDecodeError, TypeError, KeyError):
        return {}


def _ensure_defaults() -> None:
    """Create the default admin user if the file doesn't exist or has no users."""
    global _users
    with _lock:
        if _users:
            return
        _users = _load_users()
        if not _users:
            # Create default admin
            default_hash = _hash_password("admin123")
            _users["admin"] = {"password_hash": default_hash, "role": "admin"}
            _save_users()


def _save_users() -> None:
    """Persist current _users to disk."""
    try:
        out = {"users": {u: info for u, info in _users.items()}}
        _USERS_PATH.parent.mkdir(parents=True, exist_ok=True)
        _USERS_PATH.write_text(json.dumps(out, indent=2), encoding="utf-8")
    except OSError:
        pass


_ensure_defaults()


def reload() -> dict:
    """Reload users from disk and return the new dict."""
    global _users
    with _lock:
        _users = _load_users()
        if not _users:
            _ensure_defaults()
        return dict(_users)


def get_user(username: str) -> dict | None:
    """Return user info dict or None."""
    with _lock:
        return _users.get(username)


def authenticate(username: str, password: str) -> tuple[dict | None, str | None]:
    """Verify username/password. Returns (user_info, error_msg).

    user_info is {"username": ..., "role": ...} on success, None on failure.
    """
    user = get_user(username)
    if not user:
        return None, "invalid_credentials"
    if not bcrypt.checkpw(
        password.encode("utf-8"), user["password_hash"].encode("utf-8")
    ):
        return None, "invalid_credentials"
    return {"username": username, "role": user["role"]}, None


def create_user(username: str, password: str, role: str = "developer") -> tuple[bool, str]:
    """Create a new user. Returns (ok, error_msg)."""
    if role not in ROLES:
        return False, "invalid_role"
    with _lock:
        if username in _users:
            return False, "user_exists"
        _users[username] = {
            "password_hash": _hash_password(password),
            "role": role,
        }
    _save_users()
    return True, ""


def change_password(username: str, old_password: str, new_password: str) -> tuple[bool, str]:
    """Change a user's password. Returns (ok, error_msg)."""
    user = get_user(username)
    if not user:
        return False, "user_not_found"
    if not bcrypt.checkpw(
        old_password.encode("utf-8"), user["password_hash"].encode("utf-8")
    ):
        return False, "invalid_password"
    if len(new_password) < 4:
        return False, "password_too_short"
    with _lock:
        _users[username]["password_hash"] = _hash_password(new_password)
    _save_users()
    return True, ""


def set_role(username: str, role: str) -> tuple[bool, str]:
    """Set role for a user. Admin-only operation. Returns (ok, error_msg)."""
    if role not in ROLES:
        return False, "invalid_role"
    with _lock:
        if username not in _users:
            return False, "user_not_found"
        _users[username]["role"] = role
    _save_users()
    return True, ""


def list_users() -> list[dict]:
    """Return list of username/role (no hashes)."""
    with _lock:
        return [
            {"username": u, "role": info["role"]}
            for u, info in _users.items()
        ]


def delete_user(username: str) -> tuple[bool, str]:
    """Delete a user. Returns (ok, error_msg)."""
    with _lock:
        if username not in _users:
            return False, "user_not_found"
        if username == "admin":
            return False, "cannot_delete_admin"
        del _users[username]
    _save_users()
    return True, ""


# Module-level singleton for easy import
class UsersStore:
    """Thin wrapper exposing module functions as bound methods."""
    authenticate = staticmethod(authenticate)
    create_user = staticmethod(create_user)
    change_password = staticmethod(change_password)
    set_role = staticmethod(set_role)
    list_users = staticmethod(list_users)
    delete_user = staticmethod(delete_user)
    get_user = staticmethod(get_user)
    reload = staticmethod(reload)


users_store = UsersStore()


def require_role(required_role: str):
    """Return a callable that checks if the current user has at least
    the required role.  Intended for use as a FastAPI Depends or manual check."""
    role_order = {"viewer": 0, "developer": 1, "admin": 2}
    min_level = role_order.get(required_role, 0)

    def _check(user_info: dict | None) -> dict | None:
        if not user_info:
            return None
        user_level = role_order.get(user_info.get("role", "viewer"), 0)
        if user_level >= min_level:
            return user_info
        return None

    return _check
