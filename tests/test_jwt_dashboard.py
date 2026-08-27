"""Tests for JWT authentication in the dashboard backend."""
import json
import sys
import time
from pathlib import Path

import pytest

flask = pytest.importorskip("flask")

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT))

from dashboard import backend as dash  # noqa: E402


@pytest.fixture(autouse=True)
def _setup_jwt(tmp_path, monkeypatch):
    """Enable JWT auth with a test secret and temp users file."""
    monkeypatch.setenv("AUTH_JWT_SECRET", "test-jwt-secret-for-unit-tests")
    # Point users file at tmpdir
    import auth.users as u_mod
    import auth.jwt as jwt_mod
    u_mod._USERS_PATH = tmp_path / "auth-users.json"
    u_mod._users = {}
    u_mod._ensure_defaults()
    jwt_mod._login_attempts.clear()
    # Reinitialize jwt_auth singleton with test secret
    jwt_mod.jwt_auth = jwt_mod.JWTAuth(secret="test-jwt-secret-for-unit-tests")
    # Also update the dashboard's reference
    dash.jwt_auth = jwt_mod.jwt_auth
    dash._AUTH_MODULE_AVAILABLE = True
    dash._AUTH_ENABLED = True
    dash.app.config["TESTING"] = True
    yield
    # Cleanup
    u_mod._users = {}
    jwt_mod._login_attempts.clear()


@pytest.fixture
def client(tmp_path, monkeypatch):
    monkeypatch.setattr(dash, "CONFIG_DIR", tmp_path)
    monkeypatch.setattr(dash, "SKILLS_DIR", tmp_path / "skills")
    monkeypatch.setattr(dash, "ACTIVITY_LOG", tmp_path / "activity_log.jsonl")
    monkeypatch.setattr(dash, "UPLOAD_DIR", tmp_path / "uploads")
    monkeypatch.setattr(dash, "SALAD_API_KEY", "")
    monkeypatch.setattr(dash, "AIKIDO_API_KEY", "")
    monkeypatch.setattr(dash, "AIKIDO_APP_ID", "")
    dash._SUBAGENTS.clear()
    dash.app.config["TESTING"] = True
    with dash.app.test_client() as c:
        yield c


def _login(client, username="admin", password="admin123"):
    return client.post(
        "/auth/login",
        json={"username": username, "password": password},
        content_type="application/json",
    )


def _auth_header(client):
    res = _login(client)
    assert res.status_code == 200
    data = res.get_json()
    return data["access_token"]


# ── Login / Logout ───────────────────────────────────────────────

def test_login_page(client):
    res = client.get("/auth/login")
    assert res.status_code == 200


def test_login_success(client):
    res = _login(client)
    assert res.status_code == 200
    data = res.get_json()
    assert data["token_type"] == "bearer"
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["expires_in"] == 900
    assert data["user"]["username"] == "admin"
    assert data["user"]["role"] == "admin"


def test_login_wrong_password(client):
    res = client.post("/auth/login", json={
        "username": "admin", "password": "wrong"})
    assert res.status_code == 401
    assert res.get_json()["error"] == "invalid credentials"


def test_login_missing_fields(client):
    res = client.post("/auth/login", json={"username": "admin"})
    assert res.status_code == 400
    res = client.post("/auth/login", json={})
    assert res.status_code == 400


def test_login_nonexistent_user(client):
    res = client.post("/auth/login", json={
        "username": "nobody", "password": "x"})
    assert res.status_code == 401


def test_logout(client):
    res = client.post("/auth/logout")
    assert res.status_code == 200
    assert res.get_json()["ok"] is True


# ── Token refresh ────────────────────────────────────────────────

def test_refresh_token(client):
    login_res = _login(client)
    data = login_res.get_json()
    res = client.post("/auth/refresh", json={
        "refresh_token": data["refresh_token"]})
    assert res.status_code == 200
    fresh = res.get_json()
    assert "access_token" in fresh
    assert fresh["token_type"] == "bearer"


def test_refresh_invalid_token(client):
    res = client.post("/auth/refresh", json={
        "refresh_token": "bad.token.here"})
    assert res.status_code == 401


def test_refresh_missing_token(client):
    res = client.post("/auth/refresh", json={})
    assert res.status_code == 400


# ── /auth/me ─────────────────────────────────────────────────────

def test_auth_me_unauthenticated(client):
    res = client.get("/auth/me")
    assert res.status_code == 200
    assert res.get_json()["authenticated"] is False


def test_auth_me_with_token(client):
    token = _auth_header(client)
    # Debug: verify token decodes correctly
    from auth.jwt import decode_token
    payload = decode_token(token)
    assert payload is not None, f"token failed to decode: {token[:50]}"
    assert payload.get("type") == "access"
    res = client.get("/auth/me", headers={
        "Authorization": f"Bearer {token}"})
    assert res.status_code == 200, f"me failed: {res.get_data(as_text=True)}"
    data = res.get_json()
    assert data["authenticated"] is True


def test_auth_me_bad_token(client):
    res = client.get("/auth/me", headers={
        "Authorization": "Bearer invalid"})
    assert res.status_code == 401


# ── User management (admin only) ─────────────────────────────────

def test_list_users_requires_admin(client):
    res = client.get("/auth/users")
    assert res.status_code == 401
    token = _auth_header(client)
    res = client.get("/auth/users", headers={
        "Authorization": f"Bearer {token}"})
    assert res.status_code == 200
    assert "users" in res.get_json()


def test_create_user_requires_admin(client):
    token = _auth_header(client)
    res = client.post("/auth/users",
        headers={"Authorization": f"Bearer {token}"},
        json={"username": "dev1", "password": "devpass", "role": "developer"})
    assert res.status_code == 200
    assert res.get_json()["ok"] is True
    assert res.get_json()["username"] == "dev1"


def test_create_user_missing_fields(client):
    token = _auth_header(client)
    res = client.post("/auth/users",
        headers={"Authorization": f"Bearer {token}"},
        json={"username": "x"})
    assert res.status_code == 400


def test_delete_user(client):
    token = _auth_header(client)
    # create first
    client.post("/auth/users",
        headers={"Authorization": f"Bearer {token}"},
        json={"username": "todelete", "password": "pass"})
    res = client.delete("/auth/users/todelete",
        headers={"Authorization": f"Bearer {token}"})
    assert res.status_code == 200
    assert res.get_json()["ok"] is True
    # verify gone
    res = client.delete("/auth/users/todelete",
        headers={"Authorization": f"Bearer {token}"})
    assert res.get_json()["error"] == "user_not_found"


# ── Rate limiting ────────────────────────────────────────────────

def test_rate_limit_on_login(client, monkeypatch):
    import auth.jwt as jwt_mod
    # Pre-fill rate limit bucket for 127.0.0.1
    jwt_mod._login_attempts["127.0.0.1"] = [
        (time.time(), True) for _ in range(5)
    ]
    res = client.post("/auth/login", json={
        "username": "admin", "password": "admin123"})
    assert res.status_code == 429
