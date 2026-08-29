"""RBAC (Role-Based Access Control) tests."""
import sys
from pathlib import Path

import pytest

flask = pytest.importorskip("flask")

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT))

from auth.rbac import (  # noqa: E402
    get_permission_map,
    set_permission_map,
    resolve_route_permission,
)
from auth.users import users_store, create_user  # noqa: E402


@pytest.fixture(autouse=True)
def _fresh_users(tmp_path, monkeypatch):
    """Use a temp users file for every test."""
    import auth.users as u_module
    import auth.jwt as jwt_module
    u_module._USERS_PATH = tmp_path / "auth-users.json"
    u_module._users = {}
    u_module._ensure_defaults()
    jwt_module._login_attempts.clear()
    yield
    u_module._users = {}
    jwt_module._login_attempts.clear()
    u_module._ensure_defaults()


@pytest.fixture
def jwt_client(tmp_path, monkeypatch):
    """Flask test client with JWT auth enabled (gates RBAC middleware)."""
    monkeypatch.setenv("AUTH_JWT_SECRET", "rbac-test-secret")
    import dashboard.backend as dash
    import auth.jwt as jwt_mod
    jwt_mod._login_attempts.clear()
    # Reinitialize jwt_auth singleton with test secret
    test_jwt = jwt_mod.JWTAuth(secret="rbac-test-secret")
    jwt_mod.jwt_auth = test_jwt
    # Also patch the backend's reference (it imports the module-level name)
    dash.jwt_auth = test_jwt
    dash.app.config["TESTING"] = True
    dash._AUTH_MODULE_AVAILABLE = True
    dash._AUTH_ENABLED = True
    dash._RBAC_ENABLED = True
    monkeypatch.setattr(dash, "CONFIG_DIR", tmp_path)
    monkeypatch.setattr(dash, "SKILLS_DIR", tmp_path / "skills")
    monkeypatch.setattr(dash, "ACTIVITY_LOG", tmp_path / "activity_log.jsonl")
    monkeypatch.setattr(dash, "UPLOAD_DIR", tmp_path / "uploads")
    monkeypatch.setattr(dash, "SALAD_API_KEY", "")
    monkeypatch.setattr(dash, "AIKIDO_API_KEY", "")
    monkeypatch.setattr(dash, "AIKIDO_APP_ID", "")
    dash._SUBAGENTS.clear()
    with dash.app.test_client() as c:
        yield c


def _login(jwt_client, username="admin", password="admin123"):
    res = jwt_client.post(
        "/auth/login",
        json={"username": username, "password": password},
        content_type="application/json",
    )
    assert res.status_code == 200
    return res.get_json()["access_token"]


def _header(token):
    return {"Authorization": f"Bearer {token}"}


# ── Permission map tests ─────────────────────────────────────────

def test_health_is_public():
    assert resolve_route_permission("/api/health", "GET") is None


def test_stats_is_public():
    assert resolve_route_permission("/api/stats", "GET") is None


def test_services_is_public():
    assert resolve_route_permission("/api/services", "GET") is None


def test_config_get_requires_viewer():
    assert resolve_route_permission("/api/config", "GET") == "viewer"


def test_config_post_requires_developer():
    assert resolve_route_permission("/api/config", "POST") == "developer"


def test_auth_users_get_requires_admin():
    assert resolve_route_permission("/auth/users", "GET") == "admin"


def test_auth_users_post_requires_admin():
    assert resolve_route_permission("/auth/users", "POST") == "admin"


def test_subagents_get_requires_viewer():
    assert resolve_route_permission("/api/subagents", "GET") == "viewer"


def test_subagents_post_requires_developer():
    assert resolve_route_permission("/api/subagents", "POST") == "developer"


def test_secrets_requires_admin():
    assert resolve_route_permission("/api/secrets", "GET") == "admin"
    assert resolve_route_permission("/api/secrets", "POST") == "admin"


# ── Middleware integration tests ─────────────────────────────────

def test_middleware_allows_public_health(jwt_client):
    res = jwt_client.get("/api/health")
    assert res.status_code == 200


def test_middleware_allows_login_page(jwt_client):
    res = jwt_client.get("/auth/login")
    assert res.status_code == 200


def test_middleware_rejects_unauthed_config(jwt_client):
    """Authenticated but no token on a viewer-gated route."""
    res = jwt_client.get("/api/config")
    assert res.status_code == 401


def test_middleware_allows_viewer_on_viewer_route(jwt_client):
    create_user("viewer1", "viewpass", "viewer")
    import auth.users as u_mod
    u_mod._ensure_defaults()
    token = _login(jwt_client, username="viewer1", password="viewpass")
    res = jwt_client.get("/api/config", headers=_header(token))
    assert res.status_code == 200


def test_middleware_rejects_viewer_on_developer_route(jwt_client):
    create_user("viewer1", "viewpass", "viewer")
    import auth.users as u_mod
    u_mod._ensure_defaults()
    token = _login(jwt_client, username="viewer1", password="viewpass")
    res = jwt_client.post("/api/config", json={}, headers=_header(token))
    assert res.status_code == 403


def test_middleware_rejects_developer_on_admin_route(jwt_client):
    create_user("dev1", "devpass", "developer")
    import auth.users as u_mod
    u_mod._ensure_defaults()
    token = _login(jwt_client, username="dev1", password="devpass")
    res = jwt_client.get("/auth/users", headers=_header(token))
    assert res.status_code == 403


def test_middleware_admin_can_access_everything(jwt_client):
    token = _login(jwt_client)
    h = _header(token)
    # Public route
    assert jwt_client.get("/api/health", headers=h).status_code == 200
    # Viewer route
    assert jwt_client.get("/api/config", headers=h).status_code == 200
    # Admin route
    assert jwt_client.get("/auth/users", headers=h).status_code == 200


def test_public_health_no_token_required(jwt_client):
    """Public routes must work without any Authorization header."""
    res = jwt_client.get("/api/health")
    assert res.status_code == 200


def test_public_stats_no_token_required(jwt_client):
    res = jwt_client.get("/api/stats")
    assert res.status_code == 200


def test_permission_map_mutable():
    original = get_permission_map()
    set_permission_map(original)
    assert len(get_permission_map()) == len(original)
