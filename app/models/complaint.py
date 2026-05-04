"""
app/models/complaint.py
Complaint Pydantic schemas and MongoDB helpers for TraceBack.
Handles 3-step complaint form + case ID generation.
"""

from __future__ import annotations

import re
from datetime import date, datetime, timezone
from typing import Any, Dict, List, Literal, Optional

from bson import ObjectId
from pydantic import BaseModel, Field, field_validator

from app.extensions import mongo


# ─── Case ID generator ─────────────────────────────────────────────────────────

def _next_case_id() -> str:
    """
    Atomically increment a per-year counter and return TB-{YEAR}-{XXXXX}.
    Uses MongoDB 'counters' collection with findOneAndUpdate + upsert.
    """
    year = datetime.now(timezone.utc).year
    counter_key = f"complaint_{year}"

    result = mongo.db["counters"].find_one_and_update(
        {"_id": counter_key},
        {"$inc": {"seq": 1}},
        upsert=True,
        return_document=True,          # pymongo ReturnDocument.AFTER equivalent
    )
    seq: int = result["seq"]
    return f"TB-{year}-{seq:05d}"


# ─── Pydantic schemas ──────────────────────────────────────────────────────────

UPI_RE   = re.compile(r"^[\w.\-+]+@[a-zA-Z]{3,}$")
PHONE_RE = re.compile(r"^(?:\+91|91|0)?([6-9]\d{9})$")


class VictimDetails(BaseModel):
    """Embedded sub-doc — victim info attached to complaint."""
    name: str = Field(..., min_length=2, max_length=100)
    email: str
    phone: str
    state: str
    language: str = "en"


class EvidenceFile(BaseModel):
    filename: str
    url: str          # Cloudinary / GCS signed URL stored at upload time
    mime_type: str
    size_bytes: int
    uploaded_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class TimelineEntry(BaseModel):
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    actor: str                            # user_id or "system"
    action: str
    note: Optional[str] = None


# ── Step 1 — Incident Details ──────────────────────────────────────────────────

class ComplaintCreate(BaseModel):
    # Step 1 — Incident
    fraud_type: str = Field(..., description="Key from FRAUD_TYPES constant")
    amount_lost: float = Field(..., ge=0, description="Amount in INR")
    incident_date: date
    contact_channel: str = Field(
        ...,
        description="Channel used by fraudster: phone/whatsapp/email/social/other",
    )

    # Step 2 — Fraudster & Transaction
    fraudster_contact: str = Field(
        ...,
        min_length=3,
        max_length=200,
        description="Phone / UPI / email / URL of fraudster",
    )
    transaction_id: Optional[str] = Field(
        None,
        max_length=100,
        description="UTR / TXN / cheque number",
    )
    bank_name: Optional[str] = Field(None, max_length=100)
    description: str = Field(..., min_length=5, max_length=5000)

    # Step 3 — Supporting Info & Consent
    evidence_files: List[EvidenceFile] = Field(default_factory=list)
    consent_dpdp: bool = Field(
        ..., description="Consent under DPDP Act 2023 — must be True to submit"
    )

    # Victim details (populated server-side from JWT, but accepted as override for
    # admin/expert submissions on behalf of a victim)
    victim: Optional[VictimDetails] = None

    @field_validator("consent_dpdp")
    @classmethod
    def must_consent(cls, v: bool) -> bool:
        if not v:
            raise ValueError("DPDP consent is required to file a complaint.")
        return v

    @field_validator("incident_date")
    @classmethod
    def not_future(cls, v: date) -> date:
        # Allow up to 1 day in future (timezone tolerance)
        from datetime import timedelta
        if v > date.today() + timedelta(days=1):
            raise ValueError("Incident date cannot be in the future.")
        return v


# ─── MongoDB helpers ───────────────────────────────────────────────────────────

COLLECTION = "complaints"

STATUS_FLOW = Literal[
    "submitted",
    "under_review",
    "assigned",
    "in_progress",
    "escalated",
    "resolved",
    "closed",
    "rejected",
]


def _col():
    return mongo.db[COLLECTION]


def _serialize(doc: dict) -> dict:
    doc["id"] = str(doc.pop("_id"))
    return doc


def create_complaint(data: ComplaintCreate, user_id: str, victim: VictimDetails) -> dict:
    """
    Persist a new complaint, auto-generate case_id.
    Returns serialized complaint document.
    """
    case_id = _next_case_id()

    timeline_entry = TimelineEntry(actor=user_id, action="complaint_filed").model_dump()

    doc = {
        "case_id": case_id,
        # Step 1
        "fraud_type": data.fraud_type,
        "amount_lost": data.amount_lost,
        "incident_date": str(data.incident_date),
        "contact_channel": data.contact_channel,
        # Step 2
        "fraudster_contact": data.fraudster_contact,
        "transaction_id": data.transaction_id,
        "bank_name": data.bank_name,
        "description": data.description,
        # Step 3
        "evidence_files": [f.model_dump() for f in data.evidence_files],
        "consent_dpdp": data.consent_dpdp,
        # Victim
        "victim": victim.model_dump(),
        "user_id": user_id,
        # System fields
        "status": "submitted",
        "triage_result": {},          # populated by AI triage service
        "timeline": [timeline_entry],
        "assigned_expert_id": None,
        "created_at": datetime.now(timezone.utc),
        "updated_at": datetime.now(timezone.utc),
    }

    _col().insert_one(doc)
    return _serialize(doc)


def find_by_case_id(case_id: str) -> Optional[dict]:
    doc = _col().find_one({"case_id": case_id.upper().strip()})
    if doc:
        return _serialize(doc)
    return None


def find_by_user(user_id: str, page: int = 1, per_page: int = 10) -> Dict[str, Any]:
    skip = (page - 1) * per_page
    cursor = (
        _col()
        .find({"user_id": user_id})
        .sort("created_at", -1)
        .skip(skip)
        .limit(per_page)
    )
    items = [_serialize(d) for d in cursor]
    total = _col().count_documents({"user_id": user_id})
    return {
        "items": items,
        "total": total,
        "page": page,
        "pages": -(-total // per_page),   # ceil division
    }


def update_status(
    case_id: str,
    new_status: str,
    actor: str,
    note: Optional[str] = None,
) -> Optional[dict]:
    """Update complaint status and append a timeline entry."""
    entry = TimelineEntry(actor=actor, action=f"status_changed_to_{new_status}", note=note)

    result = _col().find_one_and_update(
        {"case_id": case_id.upper().strip()},
        {
            "$set": {
                "status": new_status,
                "updated_at": datetime.now(timezone.utc),
            },
            "$push": {"timeline": entry.model_dump()},
        },
        return_document=True,
    )
    if result:
        return _serialize(result)
    return None


def set_triage_result(case_id: str, triage: dict) -> Optional[dict]:
    """Attach AI triage result to complaint."""
    result = _col().find_one_and_update(
        {"case_id": case_id.upper().strip()},
        {
            "$set": {
                "triage_result": triage,
                "updated_at": datetime.now(timezone.utc),
            }
        },
        return_document=True,
    )
    if result:
        return _serialize(result)
    return None
