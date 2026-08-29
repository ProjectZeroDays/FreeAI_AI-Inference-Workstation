"""Todo-specific auth integration.

Provides register_user, login_user, get_current_user, and require_auth
that plug into the existing auth.jwt and auth.users modules.
"""
from __future__ import annotations

import functools
import time
import uuid
from typing import Callable, Optional

from auth.jwt import decode_token, generate_access_token, jwt_auth
from auth.users import authenticate as _auth_users, create_user as _create_user, get_user as _get_user
from todos.models import User


def register_user(username: str, email: str, password: str) -> tuple[Optional[User], str]:
    """Register a new user.

    Returns (User, "") on success or (None, error_string) on failure.
    """
    ok, err = _create_user(username, password, role="viewer")
    if not ok:
        return None, err
    user = User(
        user_id=uuid_generate(),
        username=username,
        email=email,
        role="viewer",
    )
    return user, ""


def login_user(username: str, password: str) -> tuple[Optional[dict], str]:
    """Authenticate a user and return JWT payload or error."""
    user_info, err = _auth_users(username, password)
    if err:
        return None, err
    token = generate_access_token(username, user_info["role"])
    return {
        "access_token": token,
        "token_type": "bearer",
        "user": {
            "username": user_info["username"],
            "role": user_info["role"],
        },
    }, ""


def get_current_user(token: str) -> Optional[User]:
    """Decode JWT and return a User object, or None if invalid/expired."""
    payload = decode_token(token)
    if not payload or payload.get("type") != "access":
        return None
    username = payload.get("sub")
    if not username:
        return None
    user_info = _get_user(username)
    if not user_info:
        return None
    return User(
        user_id=uuid_generate(),
        username=username,
        email="",
        role=user_info.get("role", "viewer"),
    )


def require_auth(f: Callable) -> Callable:
    """Decorator that validates the Bearer token from Authorization header.

    On success sets ``f._current_user`` on the function return context
    (caller inspectable) and passes the User through as first arg after
    the usual *args/**kwargs.  Returns 401 dict on failure when used
    with Flask; works stand-alone for any framework.
    """
    @functools.wraps(f)
    def wrapper(*args, **kwargs):
        try:
            from flask import request
        except ImportError:
            request = None

        if request is not None:
            auth_header = request.headers.get("Authorization", "").strip()
            token = auth_header[len("Bearer "):].strip() if auth_header.startswith("Bearer ") else ""
        else:
            token = kwargs.pop("token", "")

        user = get_current_user(token)
        if not user:
            if request is not None:
                return {"error": "unauthorized"}, 401
            return None
        return f(*args, user=user, **kwargs)

    return wrapper


def uuid_generate() -> str:
    """Return a short UUID v4 string for user_id."""
    return str(uuid.uuid4())
