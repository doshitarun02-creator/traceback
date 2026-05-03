#!/usr/bin/env python3
"""
seed.py — TraceBack MongoDB Seed Script
Drops and recreates all collections with fresh seed data on each run.
"""

import os
import sys
from datetime import datetime, timezone

import bcrypt
from bson import ObjectId
from dotenv import load_dotenv
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError

# ─── Load environment ────────────────────────────────────────────────────────
load_dotenv()
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
DB_NAME = os.getenv("DB_NAME", "traceback")

# ─── Helpers ─────────────────────────────────────────────────────────────────
def now():
    return datetime.now(timezone.utc)

def hash_password(plain: str) -> str:
    return bcrypt.hashpw(plain.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

def ts(year=2026, month=1, day=1, hour=0, minute=0):
    return datetime(year, month, day, hour, minute, tzinfo=timezone.utc)

# ─── IDs (pre-defined for cross-collection references) ───────────────────────
user_ids = {
    "admin":   ObjectId(),
    "rahul":   ObjectId(),
    "preethi": ObjectId(),
    "arif":    ObjectId(),
}

expert_ids = {
    "aditya":  ObjectId(),
    "priya":   ObjectId(),
    "rahulj":  ObjectId(),
    "sneha":   ObjectId(),
    "vikram":  ObjectId(),
    "ananya":  ObjectId(),
}

complaint_ids = {f"TB-2026-0000{i}": ObjectId() for i in range(1, 6)}

# ─── Seed Data ───────────────────────────────────────────────────────────────

USERS = [
    {
        "_id": user_ids["admin"],
        "email": "admin@traceback.in",
        "password_hash": hash_password("Admin@1234"),
        "name": "TraceBack Admin",
        "role": "admin",
        "state": None,
        "is_verified": True,
        "created_at": ts(2026, 1, 1),
        "updated_at": ts(2026, 1, 1),
    },
    {
        "_id": user_ids["rahul"],
        "email": "rahul.sharma@gmail.com",
        "password_hash": hash_password("User@1234"),
        "name": "Rahul Sharma",
        "role": "victim",
        "state": "Maharashtra",
        "is_verified": True,
        "created_at": ts(2026, 1, 10),
        "updated_at": ts(2026, 1, 10),
    },
    {
        "_id": user_ids["preethi"],
        "email": "preethi.k@gmail.com",
        "password_hash": hash_password("User@1234"),
        "name": "Preethi Krishnan",
        "role": "victim",
        "state": "Tamil Nadu",
        "is_verified": True,
        "created_at": ts(2026, 1, 12),
        "updated_at": ts(2026, 1, 12),
    },
    {
        "_id": user_ids["arif"],
        "email": "mohd.arif@gmail.com",
        "password_hash": hash_password("User@1234"),
        "name": "Mohammad Arif",
        "role": "victim",
        "state": "Uttar Pradesh",
        "is_verified": True,
        "created_at": ts(2026, 1, 15),
        "updated_at": ts(2026, 1, 15),
    },
]

EXPERTS = [
    {
        "_id": expert_ids["aditya"],
        "name": "Aditya Kumar",
        "avatar_initials": "AK",
        "avatar_color": "#4f46e5",
        "title": "Senior Cyber Investigator",
        "certifications": ["CHFI", "CEH"],
        "specialization": "Investment Fraud",
        "institution": "IIT Kanpur",
        "skills": ["OSINT", "Blockchain Tracing", "Fake Trading Apps"],
        "rate_per_hour": 3500,
        "cases_resolved": 214,
        "fraud_categories": ["investment"],
        "rating": 4.8,
        "is_verified": True,
        "is_online": True,
        "created_at": ts(2026, 1, 1),
        "updated_at": ts(2026, 1, 1),
    },
    {
        "_id": expert_ids["priya"],
        "name": "Priya Sharma",
        "avatar_initials": "PS",
        "avatar_color": "#10b981",
        "title": "Digital Arrest Specialist",
        "certifications": ["CHFI"],
        "specialization": "Digital Arrest",
        "institution": "Ex-Cybercell",
        "skills": ["CBI Impersonation", "FIR Drafting", "Police Liaison"],
        "rate_per_hour": 4200,
        "cases_resolved": 187,
        "fraud_categories": ["digital_arrest"],
        "rating": 4.8,
        "is_verified": True,
        "is_online": True,
        "created_at": ts(2026, 1, 1),
        "updated_at": ts(2026, 1, 1),
    },
    {
        "_id": expert_ids["rahulj"],
        "name": "Rahul Joshi",
        "avatar_initials": "RJ",
        "avatar_color": "#f59e0b",
        "title": "UPI & Mobile Forensics Expert",
        "certifications": ["CEH"],
        "specialization": "UPI Forensics",
        "institution": None,
        "skills": ["Cellebrite", "UPI Fraud", "SMS Recovery"],
        "rate_per_hour": 2800,
        "cases_resolved": 329,
        "fraud_categories": ["upi"],
        "rating": 4.8,
        "is_verified": True,
        "is_online": True,
        "created_at": ts(2026, 1, 1),
        "updated_at": ts(2026, 1, 1),
    },
    {
        "_id": expert_ids["sneha"],
        "name": "Sneha Nair",
        "avatar_initials": "SN",
        "avatar_color": "#ec4899",
        "title": "Sextortion & OSINT Specialist",
        "certifications": ["CHFI", "CEH"],
        "specialization": "Sextortion",
        "institution": None,
        "skills": ["Instagram Forensics", "Evidence Preservation", "Victim Psych"],
        "rate_per_hour": 3100,
        "cases_resolved": 156,
        "fraud_categories": ["sextortion"],
        "rating": 4.8,
        "is_verified": True,
        "is_online": True,
        "created_at": ts(2026, 1, 1),
        "updated_at": ts(2026, 1, 1),
    },
    {
        "_id": expert_ids["vikram"],
        "name": "Vikram Desai",
        "avatar_initials": "VD",
        "avatar_color": "#3b82f6",
        "title": "Banking Fraud Investigator",
        "certifications": ["CEH"],
        "specialization": "Credit Card Fraud",
        "institution": None,
        "skills": ["SWIFT Tracing", "Chargebacks", "Bank Ombudsman"],
        "rate_per_hour": 2600,
        "cases_resolved": 412,
        "fraud_categories": ["credit_card"],
        "rating": 4.8,
        "is_verified": True,
        "is_online": True,
        "created_at": ts(2026, 1, 1),
        "updated_at": ts(2026, 1, 1),
    },
    {
        "_id": expert_ids["ananya"],
        "name": "Ananya Reddy",
        "avatar_initials": "AR",
        "avatar_color": "#8b5cf6",
        "title": "E-Commerce & Crypto Forensicist",
        "certifications": ["CHFI"],
        "specialization": "E-Commerce Fraud",
        "institution": None,
        "skills": ["Crypto Tracing", "Marketplace Forensics", "Wallet Tracking"],
        "rate_per_hour": 2400,
        "cases_resolved": 278,
        "fraud_categories": ["ecommerce"],
        "rating": 4.8,
        "is_verified": True,
        "is_online": True,
        "created_at": ts(2026, 1, 1),
        "updated_at": ts(2026, 1, 1),
    },
]

COMPLAINTS = [
    {
        "_id": complaint_ids["TB-2026-00001"],
        "case_id": "TB-2026-00001",
        "user_id": user_ids["rahul"],
        "fraud_type": "investment_scam",
        "amount_lost": 640000,
        "state": "Maharashtra",
        "status": "active",
        "funds_held": 380000,
        "assigned_expert_id": expert_ids["aditya"],
        "triage": {
            "urgency": "CRITICAL",
            "recommended_tier": "trace",
            "i4c_compatibility": True,
            "triaged_at": ts(2026, 2, 2, 10, 30),
        },
        "timeline": [
            {"event": "submitted",              "timestamp": ts(2026, 2, 1, 9, 0),   "note": "Complaint submitted by victim."},
            {"event": "triaged",                "timestamp": ts(2026, 2, 2, 10, 30), "note": "AI triage complete. Urgency: CRITICAL."},
            {"event": "expert_assigned",        "timestamp": ts(2026, 2, 2, 14, 0),  "note": "Aditya Kumar assigned as lead expert."},
            {"event": "bank_freeze_requested",  "timestamp": ts(2026, 2, 3, 9, 15),  "note": "Freeze request sent to beneficiary bank."},
            {"event": "funds_held_380000",      "timestamp": ts(2026, 2, 4, 11, 0),  "note": "₹3,80,000 frozen by bank. Recovery in progress."},
        ],
        "created_at": ts(2026, 2, 1, 9, 0),
        "updated_at": ts(2026, 2, 4, 11, 0),
    },
    {
        "_id": complaint_ids["TB-2026-00002"],
        "case_id": "TB-2026-00002",
        "user_id": None,
        "fraud_type": "digital_arrest",
        "amount_lost": 120000,
        "state": "Karnataka",
        "status": "triaged",
        "funds_held": 0,
        "assigned_expert_id": None,
        "triage": {
            "urgency": "HIGH",
            "recommended_tier": "trace",
            "i4c_compatibility": False,
            "triaged_at": ts(2026, 2, 10, 16, 0),
        },
        "timeline": [
            {"event": "submitted", "timestamp": ts(2026, 2, 10, 14, 0), "note": "Complaint submitted by victim."},
            {"event": "triaged",   "timestamp": ts(2026, 2, 10, 16, 0), "note": "AI triage complete. Urgency: HIGH. Awaiting expert assignment."},
        ],
        "created_at": ts(2026, 2, 10, 14, 0),
        "updated_at": ts(2026, 2, 10, 16, 0),
    },
    {
        "_id": complaint_ids["TB-2026-00003"],
        "case_id": "TB-2026-00003",
        "user_id": user_ids["preethi"],
        "fraud_type": "upi_bank_fraud",
        "amount_lost": 45000,
        "state": "Tamil Nadu",
        "status": "resolved",
        "funds_held": 45000,
        "assigned_expert_id": expert_ids["rahulj"],
        "triage": {
            "urgency": "MEDIUM",
            "recommended_tier": "scout",
            "i4c_compatibility": False,
            "triaged_at": ts(2026, 2, 15, 11, 0),
        },
        "timeline": [
            {"event": "submitted", "timestamp": ts(2026, 2, 14, 10, 0),  "note": "Complaint submitted by victim."},
            {"event": "triaged",   "timestamp": ts(2026, 2, 15, 11, 0),  "note": "AI triage complete. Urgency: MEDIUM."},
            {"event": "resolved",  "timestamp": ts(2026, 2, 20, 15, 30), "note": "Full amount ₹45,000 recovered and returned to victim."},
        ],
        "created_at": ts(2026, 2, 14, 10, 0),
        "updated_at": ts(2026, 2, 20, 15, 30),
    },
    {
        "_id": complaint_ids["TB-2026-00004"],
        "case_id": "TB-2026-00004",
        "user_id": user_ids["arif"],
        "fraud_type": "sextortion",
        "amount_lost": 30000,
        "state": "Uttar Pradesh",
        "status": "pending",
        "funds_held": 0,
        "assigned_expert_id": None,
        "triage": {
            "urgency": "HIGH",
            "recommended_tier": "scout",
            "i4c_compatibility": False,
            "triaged_at": None,
        },
        "timeline": [
            {"event": "submitted", "timestamp": ts(2026, 3, 1, 8, 45), "note": "Complaint submitted. Awaiting triage."},
        ],
        "created_at": ts(2026, 3, 1, 8, 45),
        "updated_at": ts(2026, 3, 1, 8, 45),
    },
    {
        "_id": complaint_ids["TB-2026-00005"],
        "case_id": "TB-2026-00005",
        "user_id": None,
        "fraud_type": "ecommerce",
        "amount_lost": 12000,
        "state": "Delhi",
        "status": "closed",
        "funds_held": 0,
        "assigned_expert_id": expert_ids["ananya"],
        "triage": {
            "urgency": "LOW",
            "recommended_tier": "scout",
            "i4c_compatibility": False,
            "triaged_at": ts(2026, 3, 5, 12, 0),
        },
        "timeline": [
            {"event": "submitted", "timestamp": ts(2026, 3, 5, 10, 0),  "note": "Complaint submitted by victim."},
            {"event": "triaged",   "timestamp": ts(2026, 3, 5, 12, 0),  "note": "AI triage complete. Urgency: LOW."},
            {"event": "closed",    "timestamp": ts(2026, 3, 8, 17, 0),  "note": "Case closed — insufficient evidence to proceed."},
        ],
        "created_at": ts(2026, 3, 5, 10, 0),
        "updated_at": ts(2026, 3, 8, 17, 0),
    },
]

COUNTERS = [
    {"_id": "complaint_2026", "seq": 5},
]

# ─── Main Seeder ─────────────────────────────────────────────────────────────

def seed():
    print("\n🌱  TraceBack — MongoDB Seed Script")
    print("=" * 45)

    try:
        client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
        client.admin.command("ping")
        print(f"✅  Connected to MongoDB  →  {MONGO_URI}")
    except (ConnectionFailure, ServerSelectionTimeoutError) as exc:
        print(f"❌  Cannot connect to MongoDB: {exc}")
        sys.exit(1)

    db = client[DB_NAME]
    print(f"📦  Database: {DB_NAME}\n")

    # ── Users ──────────────────────────────────────────────────────────────
    db.users.drop()
    db.users.insert_many(USERS)
    print(f"👤  users         → {len(USERS)} documents seeded")

    # ── Experts ────────────────────────────────────────────────────────────
    db.experts.drop()
    db.experts.insert_many(EXPERTS)
    print(f"🔍  experts       → {len(EXPERTS)} documents seeded")

    # ── Complaints ─────────────────────────────────────────────────────────
    db.complaints.drop()
    db.complaints.insert_many(COMPLAINTS)
    print(f"📋  complaints    → {len(COMPLAINTS)} documents seeded")

    # ── Counters ───────────────────────────────────────────────────────────
    db.counters.drop()
    db.counters.insert_many(COUNTERS)
    print(f"🔢  counters      → {len(COUNTERS)} document  seeded")

    # ── Indexes (optional but recommended) ────────────────────────────────
    db.users.create_index("email", unique=True)
    db.complaints.create_index("case_id", unique=True)
    db.complaints.create_index("status")
    db.complaints.create_index("fraud_type")
    db.experts.create_index("fraud_categories")
    print("\n🗂️   Indexes created on users.email, complaints.case_id/status/fraud_type, experts.fraud_categories")

    print("\n✅  Seed complete — all collections refreshed.\n")
    client.close()


if __name__ == "__main__":
    seed()
