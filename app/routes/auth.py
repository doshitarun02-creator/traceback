# FIXED: Implemented full login and register logic with JWT token generation and validation.
"""
app/routes/auth.py
Authentication routes for TraceBack.
"""

from flask import Blueprint, request, g
from pydantic import ValidationError

from app.models.user import UserCreate, UserLogin, create_user, verify_user, find_by_email
from app.middleware.auth_middleware import generate_tokens, token_required
from app.utils.response import success, error, created, validation_error, unauthorised

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/register", methods=["POST"])
def register():
    """Register a new victim user."""
    try:
        data = UserCreate(**request.get_json())
    except ValidationError as e:
        return validation_error(e.errors())
    except Exception:
        return error("Invalid request body.")

    try:
        user = create_user(data)
        tokens = generate_tokens(user["id"], user["role"])
        return created({
            "user": user,
            **tokens
        }, "Registration successful.")
    except ValueError as e:
        return error(str(e), 409)


@auth_bp.route("/login", methods=["POST"])
def login():
    """Authenticate user and return JWT tokens."""
    try:
        data = UserLogin(**request.get_json())
    except ValidationError as e:
        return validation_error(e.errors())
    except Exception:
        return error("Invalid request body.")

    user = verify_user(data.email, data.password)
    if not user:
        return unauthorised("Invalid email or password.")

    tokens = generate_tokens(user["id"], user["role"])
    return success({
        "user": user,
        **tokens
    }, "Login successful.")


@auth_bp.route("/me", methods=["GET"])
@token_required
def get_me():
    """Return currently authenticated user details."""
    # g.user_id is set by token_required
    user = find_by_email(g.current_user["sub"]) # sub is the user_id
    if not user:
        return error("User not found.", 404)
    
    # Simple serialization for return
    user["id"] = str(user.pop("_id"))
    user.pop("password_hash", None)
    return success(user)
