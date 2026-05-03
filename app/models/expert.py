"""
app/models/expert.py
Expert Pydantic schema and MongoDB helpers for TraceBack.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import List, Optional

from bson import ObjectId
from pydantic import BaseModel, Field

from app.extensions import mongo


# ─── Pydantic schema ───────────────────────────────────────────────────────────

class ExpertCreate(BaseModel):
    # Identity
    name: str = Field(..., min_length=2, max_length=100)
    avatar_initials: str = Field(
        ..., min_length=1, max_length=3, description="e.g. 'RS' for Rahul Sharma"
    )
    avatar_color: str = Field(
        ...,
        pattern=r"^#[0-9a-fA-F]{6}$",
        description="Hex color for avatar background, e.g. #4f46e5",
    )

    # Professional
    title: str = Field(..., max_length=100, description="e.g. 'Cyber Fraud Investigator'")
    specialization: str = Field(..., max_length=200)
    certifications: List[str] = Field(default_factory=list)
    skills: List[str] = Field(default_factory=list)
    fraud_categories: List[str] = Field(
        default_factory=list,
        description="Subset of FRAUD_TYPES keys this expert handles",
    )

    # Availability & pricing
    rate_per_hour: float = Field(..., ge=0, description="Rate in INR per hour")
    is_online: bool = False
    is_verified: bool = False


class ExpertOut(ExpertCreate):
    id: str
    cases_resolved: int = 0
    rating: float = Field(default=0.0, ge=0, le=5)
    created_at: datetime
    updated_at: datetime


# ─── MongoDB helpers ───────────────────────────────────────────────────────────

COLLECTION = "experts"


def _col():
    return mongo.db[COLLECTION]


def _serialize(doc: dict) -> dict:
    doc["id"] = str(doc.pop("_id"))
    return doc


def create_expert(data: ExpertCreate) -> dict:
    doc = data.model_dump()
    doc.update(
        {
            "cases_resolved": 0,
            "rating": 0.0,
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc),
        }
    )
    result = _col().insert_one(doc)
    doc["_id"] = result.inserted_id
    return _serialize(doc)


def find_expert_by_id(expert_id: str) -> Optional[dict]:
    try:
        doc = _col().find_one({"_id": ObjectId(expert_id)})
    except Exception:
        return None
    return _serialize(doc) if doc else None


def list_experts(
    fraud_category: Optional[str] = None,
    online_only: bool = False,
    page: int = 1,
    per_page: int = 20,
) -> dict:
    query: dict = {"is_verified": True}
    if fraud_category:
        query["fraud_categories"] = fraud_category
    if online_only:
        query["is_online"] = True

    skip = (page - 1) * per_page
    cursor = (
        _col()
        .find(query)
        .sort([("rating", -1), ("cases_resolved", -1)])
        .skip(skip)
        .limit(per_page)
    )
    items = [_serialize(d) for d in cursor]
    total = _col().count_documents(query)
    return {
        "items": items,
        "total": total,
        "page": page,
        "pages": -(-total // per_page),
    }


def update_expert_stats(expert_id: str, rating_delta: float, resolved: bool = True) -> Optional[dict]:
    """
    Called after a case is closed.  Increments cases_resolved and
    recalculates rolling average rating.
    """
    doc = find_expert_by_id(expert_id)
    if not doc:
        return None

    n = doc["cases_resolved"]
    old_rating = doc["rating"]

    new_n = n + (1 if resolved else 0)
    # Bayesian rolling mean: ((old_rating * n) + new_rating) / (n + 1)
    new_rating = ((old_rating * n) + rating_delta) / new_n if new_n > 0 else 0.0

    updated = _col().find_one_and_update(
        {"_id": ObjectId(expert_id)},
        {
            "$set": {
                "cases_resolved": new_n,
                "rating": round(new_rating, 2),
                "updated_at": datetime.now(timezone.utc),
            }
        },
        return_document=True,
    )
    return _serialize(updated) if updated else None
