"""
app/utils/constants.py
Static reference data for TraceBack.
"""

from typing import Dict, List


# ─── Fraud Types ───────────────────────────────────────────────────────────────

FRAUD_TYPES: List[Dict[str, str]] = [
    {"key": "upi_fraud",           "label": "UPI / Payment Fraud"},
    {"key": "bank_fraud",          "label": "Banking / Debit-Credit Card Fraud"},
    {"key": "investment_fraud",    "label": "Investment / Share Market Fraud"},
    {"key": "loan_fraud",          "label": "Loan / KYC Fraud"},
    {"key": "job_fraud",           "label": "Job / Employment Fraud"},
    {"key": "romance_scam",        "label": "Romance / Honey-trap Scam"},
    {"key": "lottery_fraud",       "label": "Lottery / Prize Fraud"},
    {"key": "tech_support_fraud",  "label": "Tech Support / Remote Access Fraud"},
    {"key": "impersonation",       "label": "Impersonation / Identity Theft"},
    {"key": "phishing",            "label": "Phishing / Vishing / Smishing"},
    {"key": "social_media_fraud",  "label": "Social Media Account Fraud"},
    {"key": "otp_fraud",           "label": "OTP / SIM Swap Fraud"},
    {"key": "courier_fraud",       "label": "Courier / Parcel Scam"},
    {"key": "insurance_fraud",     "label": "Insurance Mis-selling / Fraud"},
    {"key": "crypto_fraud",        "label": "Cryptocurrency / NFT Fraud"},
    {"key": "emi_fraud",           "label": "EMI / Finance Scheme Fraud"},
    {"key": "matrimony_fraud",     "label": "Matrimony / Dating Site Fraud"},
    {"key": "real_estate_fraud",   "label": "Real Estate / Property Fraud"},
    {"key": "charity_fraud",       "label": "Fake Charity / NGO Fraud"},
    {"key": "other",               "label": "Other / Unknown"},
]


# ─── Indian States & UTs ───────────────────────────────────────────────────────

INDIAN_STATES: List[str] = [
    # 28 States
    "Andhra Pradesh",
    "Arunachal Pradesh",
    "Assam",
    "Bihar",
    "Chhattisgarh",
    "Goa",
    "Gujarat",
    "Haryana",
    "Himachal Pradesh",
    "Jharkhand",
    "Karnataka",
    "Kerala",
    "Madhya Pradesh",
    "Maharashtra",
    "Manipur",
    "Meghalaya",
    "Mizoram",
    "Nagaland",
    "Odisha",
    "Punjab",
    "Rajasthan",
    "Sikkim",
    "Tamil Nadu",
    "Telangana",
    "Tripura",
    "Uttar Pradesh",
    "Uttarakhand",
    "West Bengal",
    # 8 Union Territories
    "Andaman and Nicobar Islands",
    "Chandigarh",
    "Dadra and Nagar Haveli and Daman and Diu",
    "Delhi (NCT)",
    "Jammu and Kashmir",
    "Ladakh",
    "Lakshadweep",
    "Puducherry",
]


# ─── Banks ─────────────────────────────────────────────────────────────────────

BANKS: List[str] = [
    "State Bank of India (SBI)",
    "HDFC Bank",
    "ICICI Bank",
    "Punjab National Bank (PNB)",
    "Axis Bank",
    "Kotak Mahindra Bank",
    "Bank of Baroda",
    "Canara Bank",
    "Union Bank of India",
    "IndusInd Bank",
    "Yes Bank",
    "IDFC First Bank",
    "Federal Bank",
    "South Indian Bank",
    "Bank of India",
    "Central Bank of India",
    "UCO Bank",
    "Indian Bank",
    "Indian Overseas Bank",
    "Bandhan Bank",
]


# ─── Service Tiers ─────────────────────────────────────────────────────────────

TIERS: Dict[str, Dict] = {
    "scout": {
        "display": "Scout",
        "price_inr": 0,
        "description": (
            "Free tier — AI-assisted case filing, automated triage, "
            "and a personalised recovery roadmap."
        ),
        "features": [
            "Case filing & tracking",
            "AI fraud classification",
            "Recovery checklist",
            "Community forum access",
        ],
    },
    "trace": {
        "display": "Trace",
        "price_inr": 999,
        "description": (
            "₹999 / case — Everything in Scout plus one verified expert "
            "consultation (45 min) and assisted complaint drafting for "
            "Cyber Cell / RBI / TRAI."
        ),
        "features": [
            "Everything in Scout",
            "1× expert consultation (45 min)",
            "Official complaint drafting",
            "Priority queue",
            "Email & WhatsApp updates",
        ],
    },
    "forge": {
        "display": "Forge",
        "price_inr": 4999,
        "description": (
            "₹4 999 / case — Full-service investigation. Dedicated expert, "
            "evidence packaging, FIR filing support, legal liaison, and "
            "fund-recovery tracking."
        ),
        "features": [
            "Everything in Trace",
            "Dedicated expert (unlimited hours)",
            "Evidence packaging & chain-of-custody",
            "FIR / NCRP filing support",
            "Legal escalation liaison",
            "Fund-recovery tracker",
            "Monthly status report",
        ],
    },
}


# ─── Urgency Levels ────────────────────────────────────────────────────────────

URGENCY_LEVELS: Dict[str, Dict] = {
    "CRITICAL": {
        "label": "Critical",
        "color": "#dc2626",      # red-600
        "bg_color": "#fee2e2",   # red-100
        "hours_window": 2,
        "description": "Active account compromise or ongoing transaction fraud. Respond within 2 hours.",
        "sla_hours": 2,
    },
    "HIGH": {
        "label": "High",
        "color": "#ea580c",      # orange-600
        "bg_color": "#ffedd5",   # orange-100
        "hours_window": 12,
        "description": "Recent fraud within 48 hours. High recovery probability. Respond within 12 hours.",
        "sla_hours": 12,
    },
    "MEDIUM": {
        "label": "Medium",
        "color": "#ca8a04",      # yellow-600
        "bg_color": "#fef9c3",   # yellow-100
        "hours_window": 48,
        "description": "Fraud reported within 7 days. Standard investigation timeline.",
        "sla_hours": 48,
    },
    "LOW": {
        "label": "Low",
        "color": "#16a34a",      # green-600
        "bg_color": "#dcfce7",   # green-100
        "hours_window": 120,
        "description": "Older fraud or advisory request. Recovery less likely but documentation important.",
        "sla_hours": 120,
    },
}


# ─── Convenience lookups ───────────────────────────────────────────────────────

FRAUD_TYPE_KEYS: List[str] = [ft["key"] for ft in FRAUD_TYPES]
FRAUD_TYPE_MAP: Dict[str, str] = {ft["key"]: ft["label"] for ft in FRAUD_TYPES}
