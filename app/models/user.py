"""
app/models/user.py
User Pydantic schemas and MongoDB helpers for TraceBack.
"""

from __future__ import annotations

import re
from datetime import datetime, timezone
from typing import List, Literal, Optional

import bcrypt
from bson import ObjectId
from pydantic import BaseModel, EmailStr, Field, field_validator

from app.extensions import mongo          # injected by app factory (Chunk 1)


# ─── Pydantic schemas ──────────────────────────────────────────────────────────

PHONE_RE = re.compile(r"^(?:\+91|91|0)?([6-9]\d{9})$")


class UserCreate(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    email: EmailStr
    phone: str = Field(..., description="+91 10-digit mobile number")
    password: str = Field(..., min_length=8, max_length=128)
    state: str = Field(..., min_length=2, max_length=60)
    language: str = Field(default="en", max_length=10)
    role: Literal["victim", "expert", "admin"] = "victim"

    @field_validator("phone")
    @classmethod
    def validate_phone(cls, v: str) -> str:
        m = PHONE_RE.match(v.strip())
        if not m:
            raise ValueError("Invalid Indian phone number. Must be 10 digits starting with 6-9.")
        return f"+91{m.group(1)}"


class UserLogin(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=1)


class UserOut(BaseModel):
    """Safe projection returned to callers — no password_hash."""
    id: str
    name: str
    email: str
    phone: str
    state: str
    language: str
    role: str
    is_verified: bool
    cases: List[str]
    created_at: datetime


# ─── MongoDB helpers ───────────────────────────────────────────────────────────

COLLECTION = "users"


def _col():
    return mongo.db[COLLECTION]


def _serialize(doc: dict) -> dict:
    """Convert ObjectId/datetime to JSON-safe types."""
    doc["id"] = str(doc.pop("_id"))
    doc.setdefault("cases", [])
    doc["cases"] = [str(c) for c in doc["cases"]]
    return doc


def find_by_email(email: str) -> Optional[dict]:
    """Return raw user document (includes password_hash) or None."""
    doc = _col().find_one({"email": email.lower().strip()})
    return doc


def create_user(data: UserCreate) -> UserOut:
    """
    Hash password, persist user, return safe UserOut dict.
    Raises ValueError if e-mail already registered.
    """
    if find_by_email(data.email):
        raise ValueError("A user with this e-mail already exists.")

    pw_hash = bcrypt.hashpw(data.password.encode(), bcrypt.gensalt()).decode()

    doc = {
        "name": data.name.strip(),
        "email": data.email.lower().strip(),
        "phone": data.phone,
        "password_hash": pw_hash,
        "state": data.state,
        "language": data.language,
        "role": data.role,
        "is_verified": False,
        "cases": [],
        "created_at": datetime.now(timezone.utc),
        "updated_at": datetime.now(timezone.utc),
    }

    result = _col().insert_one(doc)
    doc["_id"] = result.inserted_id
    return _serialize(doc)


def verify_user(email: str, password: str) -> Optional[dict]:
    """
    Return serialized user dict if credentials are valid, else None.
    Does NOT expose password_hash to the caller.
    """
    doc = find_by_email(email)
    if not doc:
        return None
    stored_hash: str = doc.get("password_hash", "")
    if not bcrypt.checkpw(password.encode(), stored_hash.encode()):
        return None
    doc.pop("password_hash", None)
    return _serialize(doc)


def add_case_to_user(user_id: str, case_id: str) -> None:
    _col().update_one(
        {"_id": ObjectId(user_id)},
        {
            "$addToSet": {"cases": case_id},
            "$set": {"updated_at": datetime.now(timezone.utc)},
        },
    )
