"""RBAC engine — role hierarchy, permission matrix, config-backed defaults."""
import json
import threading
from pathlib import Path

CONFIG_DIR = Path(__file__).resolve().parent.parent / "config"
DEFAULT_CONFIG_PATH = CONFIG_DIR / "rbac.json"

ROLE_HIERARCHY = {
    "superadmin": 5,
    "admin": 4,
    "godmode": 4,
    "developer": 3,
    "viewer": 2,
    "readonly": 1,
}

DEFAULT_PERMISSIONS = {
    "superadmin": ["*"],
    "admin": ["route", "agent/*", "workflow/*", "rbac/*", "config/*", "admin/*", "godmode/*", "catalog/*", "mcp/*"],
    "godmode": ["route", "agent/*", "workflow/*", "rbac/*", "config/*", "admin/*", "godmode/*", "catalog/*", "mcp/*"],
    "developer": ["route", "agent/*", "workflow/*", "status", "metrics", "health", "catalog/*"],
    "viewer": ["status", "metrics", "health", "models", "logs", "catalog/skills"],
    "readonly": ["status", "health"],
}

_DEFAULT_USERS = {
    "admin": "admin",
    "operator": "developer",
    "viewer": "viewer",
    "guest": "readonly",
}

_lock = threading.Lock()
_roles: dict[str, list[str]] = {}
_users: dict[str, str] = {}


def _load_config(path: Path) -> dict:
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text())
    except (json.JSONDecodeError, OSError):
        return {}


def init(config_path: Path | None = None) -> None:
    global _roles, _users
    path = config_path or DEFAULT_CONFIG_PATH
    raw = _load_config(path)
    with _lock:
        if raw:
            _roles = {k: v if isinstance(v, list) else [v] for k, v in raw.items()}
        else:
            _roles = dict(DEFAULT_PERMISSIONS)
        _users = dict(_DEFAULT_USERS)


def get_role_level(role: str) -> int:
    return ROLE_HIERARCHY.get(role, 0)


def has_role_inheritance(lower: str, higher: str) -> bool:
    return get_role_level(higher) >= get_role_level(lower)


def get_roles() -> dict[str, list[str]]:
    with _lock:
        return dict(_roles)


def get_users() -> dict[str, str]:
    with _lock:
        return dict(_users)


def set_user_role(username: str, role: str) -> str:
    with _lock:
        _users[username] = role
        return _users[username]


def remove_user(username: str) -> bool:
    with _lock:
        if username in _users:
            del _users[username]
            return True
        return False


def check_permission(resource: str, action: str, role: str) -> bool:
    with _lock:
        perms = _roles.get(role, [])
    if "*" in perms:
        return True
    for pattern in perms:
        if pattern == "*":
            return True
        if pattern.endswith("/*"):
            prefix = pattern[:-1]
            if resource == prefix.rstrip("/") or resource.startswith(prefix + "/"):
                return True
        elif ":" in pattern:
            res, act = pattern.split(":", 1)
            if resource == res and (act == "*" or act == action):
                return True
        elif resource == pattern:
            return True
    return False


def check_role(user: str) -> str:
    with _lock:
        return _users.get(user, _DEFAULT_USERS.get(user, "viewer"))


def update_permissions(new_roles: dict[str, list[str]]) -> dict[str, list[str]]:
    with _lock:
        _roles.clear()
        _roles.update(new_roles)
        return dict(_roles)


def save_config(path: Path | None = None) -> None:
    p = path or DEFAULT_CONFIG_PATH
    p.parent.mkdir(parents=True, exist_ok=True)
    with _lock:
        data = dict(_roles)
    p.write_text(json.dumps(data, indent=2))


init()
