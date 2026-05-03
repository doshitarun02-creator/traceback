# FIXED: Updated JWT config keys to match app/config.py (JWT_ACCESS_TOKEN_EXPIRES and JWT_REFRESH_TOKEN_EXPIRES)
"""
app/middleware/auth_middleware.py
JWT-based authentication decorators and token helpers for TraceBack.

Expects the following config keys in Flask app.config:
    JWT_SECRET_KEY        — signing secret (set via env var)
    JWT_ACCESS_EXPIRES    — timedelta for access token  (default 15 min)
    JWT_REFRESH_EXPIRES   — timedelta for refresh token (default 7 days)

Usage::

    @app.route("/protected")
    @token_required
    def protected():
        return jsonify({"user": request.current_user})

    @app.route("/admin-only")
    @admin_required
    def admin_only():
        return jsonify({"msg": "welcome admin"})
"""

from __future__ import annotations

import os
from datetime import datetime, timedelta, timezone
from functools import wraps
from typing import Any, Callable, Dict, Optional

import jwt
from bson import ObjectId
from flask import current_app, g, request

from app.utils.response import error as err_response


# ─── Token generation ──────────────────────────────────────────────────────────

DEFAULT_ACCESS_EXPIRES  = timedelta(minutes=15)
DEFAULT_REFRESH_EXPIRES = timedelta(days=7)


def _secret() -> str:
    secret = current_app.config.get("JWT_SECRET_KEY") or os.environ.get("JWT_SECRET_KEY", "")
    if not secret:
        raise RuntimeError("JWT_SECRET_KEY is not configured.")
    return secret


def generate_tokens(user_id: str, role: str) -> Dict[str, str]:
    """
    Generate a short-lived access token and a long-lived refresh token.

    Returns::

        {
            "access_token":  "<jwt>",
            "refresh_token": "<jwt>",
            "token_type":    "Bearer",
            "expires_in":    900      // seconds
        }
    """
    now = datetime.now(timezone.utc)

    access_expires: timedelta = current_app.config.get(
        "JWT_ACCESS_TOKEN_EXPIRES", DEFAULT_ACCESS_EXPIRES
    )
    refresh_expires: timedelta = current_app.config.get(
        "JWT_REFRESH_TOKEN_EXPIRES", DEFAULT_REFRESH_EXPIRES
    )

    access_payload = {
        "sub":  user_id,
        "role": role,
        "type": "access",
        "iat":  now,
        "exp":  now + access_expires,
    }

    refresh_payload = {
        "sub":  user_id,
        "role": role,
        "type": "refresh",
        "iat":  now,
        "exp":  now + refresh_expires,
    }

    access_token  = jwt.encode(access_payload,  _secret(), algorithm="HS256")
    refresh_token = jwt.encode(refresh_payload, _secret(), algorithm="HS256")

    return {
        "access_token":  access_token,
        "refresh_token": refresh_token,
        "token_type":    "Bearer",
        "expires_in":    int(access_expires.total_seconds()),
    }


# ─── Token extraction helper ───────────────────────────────────────────────────

def _extract_bearer_token() -> Optional[str]:
    """Pull token from Authorization header or 'token' query param."""
    auth_header = request.headers.get("Authorization", "")
    if auth_header.startswith("Bearer "):
        return auth_header[7:].strip()
    # Allow ?token=<jwt> for WebSocket / EventSource requests
    return request.args.get("token")


def _decode_token(token: str, expected_type: str = "access") -> Dict[str, Any]:
    """
    Decode and validate a JWT.
    Raises jwt.PyJWTError subclasses on any failure.
    """
    payload = jwt.decode(token, _secret(), algorithms=["HS256"])
    if payload.get("type") != expected_type:
        raise jwt.InvalidTokenError(
            f"Expected token type '{expected_type}', got '{payload.get('type')}'"
        )
    return payload


# ─── Decorators ───────────────────────────────────────────────────────────────

def token_required(f: Callable) -> Callable:
    """
    Verify JWT access token, attach decoded payload to *flask.g.current_user*
    and set *flask.g.user_id* / *flask.g.role* for convenience.

    On failure returns a 401 JSON error via :func:`app.utils.response.error`.
    """
    @wraps(f)
    def decorated(*args: Any, **kwargs: Any) -> Any:
        token = _extract_bearer_token()

        if not token:
            return err_response("Authentication token is missing.", 401)

        try:
            payload = _decode_token(token, expected_type="access")
        except jwt.ExpiredSignatureError:
            return err_response("Token has expired. Please log in again.", 401)
        except jwt.InvalidTokenError as exc:
            return err_response(f"Invalid token: {exc}", 401)

        # Attach to Flask application context
        g.current_user = payload
        g.user_id      = payload["sub"]
        g.role         = payload.get("role", "victim")

        return f(*args, **kwargs)

    return decorated


def admin_required(f: Callable) -> Callable:
    """
    Extends :func:`token_required` — additionally enforces role == 'admin'.
    """
    @wraps(f)
    @token_required
    def decorated(*args: Any, **kwargs: Any) -> Any:
        if g.role != "admin":
            return err_response("Admin privileges required.", 403)
        return f(*args, **kwargs)

    return decorated


def expert_required(f: Callable) -> Callable:
    """
    Extends :func:`token_required` — enforces role in {'expert', 'admin'}.
    Admins are allowed through so they can impersonate experts in support flows.
    """
    @wraps(f)
    @token_required
    def decorated(*args: Any, **kwargs: Any) -> Any:
        if g.role not in ("expert", "admin"):
            return err_response("Expert or admin privileges required.", 403)
        return f(*args, **kwargs)

    return decorated


# ─── Refresh token helper ─────────────────────────────────────────────────────

def refresh_access_token(refresh_token: str) -> Dict[str, str]:
    """
    Validate *refresh_token* and issue a new access token.
    Raises ValueError with a human-readable message on failure.
    """
    try:
        payload = _decode_token(refresh_token, expected_type="refresh")
    except jwt.ExpiredSignatureError:
        raise ValueError("Refresh token has expired. Please log in again.")
    except jwt.InvalidTokenError as exc:
        raise ValueError(f"Invalid refresh token: {exc}")

    user_id: str = payload["sub"]
    role: str    = payload.get("role", "victim")

    return generate_tokens(user_id, role)


def role_required(role_name: str) -> Callable:
    """ Enforce a specific role. """
    def decorator(f: Callable) -> Callable:
        @wraps(f)
        @token_required
        def decorated(*args: Any, **kwargs: Any) -> Any:
            if g.role != role_name and g.role != "admin":
                return err_response(f"{role_name.capitalize()} privileges required.", 403)
            return f(*args, **kwargs)
        return decorated
    return decorator


def get_current_user_id() -> Optional[str]:
    """
    Extract user_id from token without enforcing it (for optional auth routes).
    Returns None if token is missing or invalid.
    """
    token = _extract_bearer_token()
    if not token:
        return None
    try:
        payload = _decode_token(token, expected_type="access")
        return payload["sub"]
    except Exception:
        return None
