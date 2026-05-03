"""
app/utils/response.py
Standardised JSON response helpers for TraceBack Flask routes.

All helpers return a (Response, status_code) tuple so Flask routes can do::

    return success(data, "Created", 201)
    return error("Not found", 404)
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from flask import jsonify


# ─── Success ───────────────────────────────────────────────────────────────────

def success(
    data: Any = None,
    message: str = "Success",
    status_code: int = 200,
):
    """
    Standard success envelope::

        {
            "success": true,
            "message": "...",
            "data": { ... }
        }

    Args:
        data:        Serialisable payload (dict, list, or None).
        message:     Human-readable success message.
        status_code: HTTP status code (default 200).

    Returns:
        (flask.Response, int) tuple.
    """
    payload: Dict[str, Any] = {
        "success": True,
        "message": message,
        "data": data,
    }
    return jsonify(payload), status_code


# ─── Error ─────────────────────────────────────────────────────────────────────

def error(
    message: str = "An error occurred",
    status_code: int = 400,
    errors: Optional[List[Dict[str, Any]]] = None,
):
    """
    Standard error envelope::

        {
            "success": false,
            "message": "...",
            "errors": [ { "field": "email", "msg": "required" }, ... ]
        }

    Args:
        message:     Top-level human-readable error.
        status_code: HTTP status code (default 400).
        errors:      Optional list of field-level validation errors.
                     Each item should have at least a "msg" key.

    Returns:
        (flask.Response, int) tuple.
    """
    payload: Dict[str, Any] = {
        "success": False,
        "message": message,
        "errors": errors or [],
    }
    return jsonify(payload), status_code


# ─── Paginated list ────────────────────────────────────────────────────────────

def paginated(
    data: List[Any],
    total: int,
    page: int,
    pages: int,
    message: str = "Success",
    status_code: int = 200,
):
    """
    Paginated response envelope::

        {
            "success": true,
            "message": "...",
            "data": [ ... ],
            "pagination": {
                "total": 120,
                "page":  2,
                "pages": 12,
                "per_page": 10     // inferred from len(data)
            }
        }

    Args:
        data:        Current page's items.
        total:       Total number of items across all pages.
        page:        Current page number (1-indexed).
        pages:       Total number of pages.
        message:     Human-readable message.
        status_code: HTTP status code (default 200).

    Returns:
        (flask.Response, int) tuple.
    """
    payload: Dict[str, Any] = {
        "success": True,
        "message": message,
        "data": data,
        "pagination": {
            "total": total,
            "page": page,
            "pages": pages,
            "per_page": len(data),
        },
    }
    return jsonify(payload), status_code


# ─── Convenience aliases ───────────────────────────────────────────────────────

def created(data: Any = None, message: str = "Created"):
    """Shortcut for 201 Created."""
    return success(data, message, 201)


def no_content():
    """204 No Content — empty body."""
    return "", 204


def not_found(resource: str = "Resource"):
    return error(f"{resource} not found.", 404)


def forbidden(message: str = "You do not have permission to perform this action."):
    return error(message, 403)


def unauthorised(message: str = "Authentication required."):
    return error(message, 401)


def validation_error(errors: List[Dict[str, Any]], message: str = "Validation failed."):
    return error(message, 422, errors)


def server_error(message: str = "Internal server error."):
    return error(message, 500)
