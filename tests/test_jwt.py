"""JWT token generation, verification, and refresh tests."""
import os
import sys
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

import pytest

from auth.jwt import (  # noqa: E402
    generate_access_token, generate_refresh_token, decode_token,
    is_jwt_token, JWTAuth, _get_secret,
)


def test_generate_access_token_has_correct_claims():
    token = generate_access_token("alice", "admin")
    payload = decode_token(token)
    assert payload is not None
    assert payload["sub"] == "alice"
    assert payload["role"] == "admin"
    assert payload["type"] == "access"
    assert "exp" in payload
    assert "iat" in payload


def test_generate_refresh_token_has_correct_claims():
    token = generate_refresh_token("alice")
    payload = decode_token(token)
    assert payload is not None
    assert payload["sub"] == "alice"
    assert payload["type"] == "refresh"
    assert "role" not in payload


def test_access_token_expires_in_15_min():
    token = generate_access_token("alice", "viewer")
    payload = decode_token(token)
    assert payload is not None
    expiry = payload["exp"] - payload["iat"]
    assert 899 <= expiry <= 901  # ~15 min = 900s


def test_refresh_token_expires_in_7_days():
    token = generate_refresh_token("alice")
    payload = decode_token(token)
    assert payload is not None
    expiry = payload["exp"] - payload["iat"]
    assert 604799 <= expiry <= 604801  # ~7 days = 604800s


def test_different_users_get_different_tokens():
    t1 = generate_access_token("alice", "admin")
    t2 = generate_access_token("bob", "developer")
    assert t1 != t2
    assert decode_token(t1)["sub"] == "alice"
    assert decode_token(t2)["sub"] == "bob"


def test_different_roles_preserved():
    t_admin = generate_access_token("alice", "admin")
    t_dev = generate_access_token("alice", "developer")
    assert decode_token(t_admin)["role"] == "admin"
    assert decode_token(t_dev)["role"] == "developer"


def test_decode_invalid_token_returns_none():
    assert decode_token("not-a-token") is None
    assert decode_token("") is None
    assert decode_token(None) is None


def test_decode_tampered_token_returns_none():
    token = generate_access_token("alice", "admin")
    parts = token.split(".")
    # tamper with payload
    tampered = parts[0] + "." + parts[1] + ".tampered_signature"
    assert decode_token(tampered) is None


def test_decode_expired_token_returns_none(monkeypatch):
    """Simulate an already-expired token."""
    import jwt as pyjwt
    secret = _get_secret()
    payload = {"sub": "alice", "role": "admin", "type": "access",
               "iat": int(time.time()) - 2000,
               "exp": int(time.time()) - 1000}
    expired = pyjwt.encode(payload, secret, algorithm="HS256")
    assert decode_token(expired) is None


def test_is_jwt_token_valid():
    token = generate_access_token("alice", "admin")
    assert is_jwt_token(token) is True


def test_is_jwt_token_invalid():
    assert is_jwt_token("") is False
    assert is_jwt_token("not-a-jwt") is False
    assert is_jwt_token("a.b") is False
    assert is_jwt_token("a.b.c.d") is False
    assert is_jwt_token(None) is False
    assert is_jwt_token(12345) is False


def test_jwt_auth_class_verify():
    auth = JWTAuth()
    token = auth.create_token("alice", "admin")
    payload = auth.verify(token["access_token"])
    assert payload is not None
    assert payload["sub"] == "alice"
    assert payload["role"] == "admin"


def test_jwt_auth_class_invalid_verify():
    auth = JWTAuth()
    assert auth.verify("garbage-token") is None


def test_jwt_auth_class_create_returns_bearer():
    auth = JWTAuth()
    tokens = auth.create_token("bob", "developer")
    assert tokens["token_type"] == "bearer"
    assert "access_token" in tokens
    assert "refresh_token" in tokens
    assert isinstance(tokens["expires_in"], int)
    assert tokens["expires_in"] == 15 * 60


def test_jwt_auth_class_different_secret():
    auth = JWTAuth(secret="freeai-test-jwt-secret-32-chars!!")
    token = auth.create_token("alice", "admin")
    other = JWTAuth(secret="freeai-test-jwt-secret-32-chars!!")
    payload = other.verify(token["access_token"])
    assert payload is not None
    assert payload["sub"] == "alice"
    # a different secret should fail
    bad = JWTAuth(secret="wrong-secret-for-testing-32ch!!!")
    assert bad.verify(token["access_token"]) is None


def test_token_unique_per_call(monkeypatch):
    import auth.jwt as jwt_mod
    call_count = [0]
    def fake_time():
        call_count[0] += 1
        return 1000.0 + call_count[0]
    monkeypatch.setattr(jwt_mod.time, "time", fake_time)
    t1 = generate_access_token("alice", "admin")
    t2 = generate_access_token("alice", "admin")
    assert t1 != t2  # different iat/exp make them unique
