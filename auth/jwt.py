"""JWT token generation, verification, and middleware for FreeAI services."""
import base64
import hashlib
import hmac
import json
import os
import time
import threading
from pathlib import Path

import jwt as pyjwt

# Token expiry durations (seconds)
ACCESS_TOKEN_EXPIRE_MINUTES = 15
REFRESH_TOKEN_EXPIRE_DAYS = 7

# Rate limiting for login attempts: max attempts per window
LOGIN_MAX_ATTEMPTS = 5
LOGIN_WINDOW_SECONDS = 60

# In-memory login attempt tracker: {ip: [(timestamp, success), ...]}
_login_attempts: dict = {}
_login_lock = threading.Lock()

_ROOT = Path(__file__).parent.parent
_CONFIG_DIR = _ROOT / "config"


def _get_secret() -> str:
    """Load JWT secret from env, then config/auth.json, then generate a
    deterministic fallback so tests work without config."""
    secret = os.environ.get("AUTH_JWT_SECRET", "").strip()
    if secret:
        return secret
    auth_cfg_path = _CONFIG_DIR / "auth.json"
    try:
        data = json.loads(auth_cfg_path.read_text(encoding="utf-8"))
        secret = data.get("jwt_secret", "").strip()
        if secret:
            return secret
    except (OSError, json.JSONDecodeError):
        pass
    # Deterministic fallback for test/dev — NOT for production
    return hashlib.sha256(b"freeai-jwt-fallback-secret").hexdigest()


def _sign_payload(payload: dict, secret: str, expiry: int) -> str:
    payload["iat"] = int(time.time())
    payload["exp"] = payload["iat"] + expiry
    return pyjwt.encode(payload, secret, algorithm="HS256")


def generate_access_token(username: str, role: str) -> str:
    """Create a short-lived access token (15 min)."""
    payload = {"sub": username, "role": role, "type": "access"}
    return _sign_payload(payload, _get_secret(), ACCESS_TOKEN_EXPIRE_MINUTES * 60)


def generate_refresh_token(username: str) -> str:
    """Create a long-lived refresh token (7 days)."""
    payload = {"sub": username, "type": "refresh"}
    return _sign_payload(payload, _get_secret(), REFRESH_TOKEN_EXPIRE_DAYS * 86400)


def decode_token(token: str, secret: str | None = None) -> dict | None:
    """Decode and verify a JWT. Returns payload dict or None on failure."""
    if not token:
        return None
    try:
        return pyjwt.decode(token, secret or _get_secret(), algorithms=["HS256"])
    except (pyjwt.ExpiredSignatureError, pyjwt.InvalidTokenError, ValueError):
        return None


def check_login_rate_limit(client_ip: str) -> bool:
    """Return True if the request is allowed (not rate-limited)."""
    now = time.time()
    with _login_lock:
        attempts = _login_attempts.get(client_ip, [])
        # Prune old entries
        attempts = [(ts, ok) for ts, ok in attempts if now - ts < LOGIN_WINDOW_SECONDS]
        _login_attempts[client_ip] = attempts
        if len(attempts) >= LOGIN_MAX_ATTEMPTS:
            return False
        return True


def record_login_attempt(client_ip: str, success: bool) -> None:
    """Record a login attempt for rate-limiting."""
    now = time.time()
    with _login_lock:
        attempts = _login_attempts.get(client_ip, [])
        attempts = [(ts, ok) for ts, ok in attempts if now - ts < LOGIN_WINDOW_SECONDS]
        attempts.append((now, success))
        _login_attempts[client_ip] = attempts


def is_jwt_token(token: str) -> bool:
    """Heuristic check whether a string looks like a JWT."""
    if not token or not isinstance(token, str):
        return False
    parts = token.split(".")
    return len(parts) == 3 and all(
        len(p) > 0 and all(c in "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789-_"
                           for c in p) for p in parts
    )


class JWTAuth:
    """Reusable JWT auth checker for FastAPI / Flask apps."""

    def __init__(self, secret: str | None = None, expiry_minutes: int = ACCESS_TOKEN_EXPIRE_MINUTES):
        self.secret = secret or _get_secret()
        self.expiry = expiry_minutes * 60

    def verify(self, token: str) -> dict | None:
        """Verify token and return payload, or None if invalid/expired."""
        try:
            return pyjwt.decode(token, self.secret, algorithms=["HS256"])
        except (pyjwt.ExpiredSignatureError, pyjwt.InvalidTokenError, ValueError):
            return None

    def create_token(self, username: str, role: str) -> dict:
        """Create access + refresh token pair."""
        access = _sign_payload(
            {"sub": username, "role": role, "type": "access"},
            self.secret, self.expiry
        )
        refresh = _sign_payload(
            {"sub": username, "type": "refresh"},
            self.secret, REFRESH_TOKEN_EXPIRE_DAYS * 86400
        )
        return {
            "access_token": access,
            "refresh_token": refresh,
            "token_type": "bearer",
            "expires_in": self.expiry,
        }


# Module-level singleton
jwt_auth = JWTAuth()
