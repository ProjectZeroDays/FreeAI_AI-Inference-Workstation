"""Tests for JWT authentication module."""
import pytest
import time
import sys
import os
from pathlib import Path

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT))

from auth.jwt import (  # noqa: E402
    generate_access_token,
    generate_refresh_token,
    decode_token,
    JWTAuth,
    check_login_rate_limit,
    record_login_attempt,
    is_jwt_token,
    ACCESS_TOKEN_EXPIRE_MINUTES,
    REFRESH_TOKEN_EXPIRE_DAYS,
)
from auth.users import (  # noqa: E402
    users_store,
    get_user,
    create_user,
    change_password,
    set_role,
    list_users,
    delete_user,
    require_role,
)


@pytest.fixture(autouse=True)
def _fresh_users(tmp_path, monkeypatch):
    """Use a temp users file for every test."""
    import auth.users as u_module
    import auth.jwt as jwt_module
    u_module._USERS_PATH = tmp_path / "auth-users.json"
    u_module._users = {}
    u_module._ensure_defaults()
    u_module.change_password("admin", u_module.get_default_admin_password(), "admin123")
    # Reset rate-limit state
    jwt_module._login_attempts.clear()
    yield
    u_module._users = {}
    jwt_module._login_attempts.clear()


@pytest.fixture
def jwt():
    return JWTAuth(secret="test-secret-for-unit-tests")


# ── JWT token tests ──────────────────────────────────────────────

def test_generate_access_token(jwt):
    tokens = jwt.create_token("alice", "developer")
    assert tokens["token_type"] == "bearer"
    assert "access_token" in tokens
    assert "refresh_token" in tokens
    assert tokens["expires_in"] == ACCESS_TOKEN_EXPIRE_MINUTES * 60


def test_decode_access_token(jwt):
    tokens = jwt.create_token("bob", "admin")
    payload = jwt.verify(tokens["access_token"])
    assert payload is not None
    assert payload["sub"] == "bob"
    assert payload["role"] == "admin"
    assert payload["type"] == "access"


def test_decode_refresh_token(jwt):
    tokens = jwt.create_token("bob", "admin")
    payload = jwt.verify(tokens["refresh_token"])
    assert payload is not None
    assert payload["type"] == "refresh"
    assert payload["sub"] == "bob"


def test_decode_invalid_token(jwt):
    assert jwt.verify("invalid.token.here") is None
    assert jwt.verify("") is None
    assert jwt.verify(None) is None


def test_decode_expired_token(jwt):
    import jwt as pyjwt_lib
    payload = {"sub": "hacker", "type": "access", "iat": int(time.time()) - 9999, "exp": int(time.time()) - 1}
    token = pyjwt_lib.encode(payload, "test-secret-for-unit-tests", algorithm="HS256")
    assert jwt.verify(token) is None


def test_is_jwt_token():
    assert is_jwt_token("a.b.c") is True
    assert is_jwt_token("not-a-token") is False
    assert is_jwt_token("") is False
    assert is_jwt_token(None) is False


# ── User store tests ─────────────────────────────────────────────

def test_default_admin_exists():
    user = get_user("admin")
    assert user is not None
    assert user["role"] == "admin"


def test_authenticate_admin():
    user, err = users_store.authenticate("admin", "admin123")
    assert user is not None
    assert err is None
    assert user["username"] == "admin"
    assert user["role"] == "admin"


def test_authenticate_wrong_password():
    user, err = users_store.authenticate("admin", "wrongpassword")
    assert user is None
    assert err == "invalid_credentials"


def test_authenticate_missing_user():
    user, err = users_store.authenticate("nobody", "any")
    assert user is None
    assert err == "invalid_credentials"


def test_authenticate_first_login_required():
    """Fresh default admin should require password change on first login."""
    import auth.users as u_module
    import tempfile
    # Use a fresh temp path so _load_users returns empty
    u_module._USERS_PATH = Path(tempfile.mkstemp(suffix="-auth-users.json")[1])
    u_module._users = {}
    u_module._ensure_defaults()
    user, err = users_store.authenticate("admin", u_module.get_default_admin_password())
    assert user is None
    assert err == "first_login_required"
    # After changing password, login should succeed
    ok, err2 = change_password("admin", u_module.get_default_admin_password(), "newpass")
    assert ok is True
    user2, err3 = users_store.authenticate("admin", "newpass")
    assert user2 is not None
    assert err3 is None
    # Cleanup temp file
    u_module._USERS_PATH.unlink(missing_ok=True)


def test_create_user():
    ok, err = create_user("dev1", "devpass123", "developer")
    assert ok is True
    assert err == ""
    user = get_user("dev1")
    assert user is not None
    assert user["role"] == "developer"


def test_create_user_defaults_to_viewer():
    ok, err = create_user("viewer1", "viewpass")
    assert ok is True
    user = get_user("viewer1")
    assert user["role"] == "developer"  # create_user defaults to developer


def test_create_duplicate_user():
    create_user("dup1", "pass1")
    ok, err = create_user("dup1", "pass2")
    assert ok is False
    assert err == "user_exists"


def test_change_password():
    create_user("pw1", "oldpass")
    ok, err = change_password("pw1", "oldpass", "newpass")
    assert ok is True
    user, err2 = users_store.authenticate("pw1", "newpass")
    assert user is not None
    user2, err3 = users_store.authenticate("pw1", "oldpass")
    assert user2 is None


def test_change_password_wrong_old():
    create_user("pw2", "oldpass")
    ok, err = change_password("pw2", "wrongold", "newpass")
    assert ok is False
    assert err == "invalid_password"


def test_set_role():
    create_user("role1", "pass", "viewer")
    ok, err = set_role("role1", "developer")
    assert ok is True
    user = get_user("role1")
    assert user["role"] == "developer"


def test_list_users():
    create_user("l1", "pass")
    create_user("l2", "pass")
    users = list_users()
    usernames = {u["username"] for u in users}
    assert "admin" in usernames
    assert "l1" in usernames
    assert "l2" in usernames
    # No hashes in the list
    for u in users:
        assert "password_hash" not in u


def test_delete_user():
    create_user("del1", "pass")
    ok, err = delete_user("del1")
    assert ok is True
    assert get_user("del1") is None


def test_cannot_delete_admin():
    ok, err = delete_user("admin")
    assert ok is False
    assert err == "cannot_delete_admin"
    assert get_user("admin") is not None


# ── Rate limiting tests ──────────────────────────────────────────

def test_rate_limit_allows_first_attempts():
    ip = "127.0.0.99"
    for _ in range(5):
        assert check_login_rate_limit(ip) is True


def test_rate_limit_blocks_after_max():
    ip = "127.0.0.100"
    # Simulate 5 successful login checks + records
    for _ in range(5):
        assert check_login_rate_limit(ip) is True
        record_login_attempt(ip, True)
    # 6th attempt should be blocked
    assert check_login_rate_limit(ip) is False


def test_rate_limit_independent_per_ip():
    ip1, ip2 = "10.0.0.1", "10.0.0.2"
    for _ in range(5):
        check_login_rate_limit(ip1)
        record_login_attempt(ip1, True)
    assert check_login_rate_limit(ip1) is False
    # ip2 should still be allowed
    assert check_login_rate_limit(ip2) is True


# ── require_role tests ───────────────────────────────────────────

def test_require_role_admin_allows_admin():
    checker = require_role("admin")
    assert checker({"username": "a", "role": "admin"}) is not None
    assert checker({"username": "a", "role": "developer"}) is None
    assert checker({"username": "a", "role": "viewer"}) is None
    assert checker(None) is None


def test_require_role_developer_allows_admin_and_dev():
    checker = require_role("developer")
    assert checker({"username": "a", "role": "admin"}) is not None
    assert checker({"username": "a", "role": "developer"}) is not None
    assert checker({"username": "a", "role": "viewer"}) is None
