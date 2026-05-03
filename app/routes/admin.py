# FIXED: Implemented admin dashboard statistics with role-based access control.
"""
app/routes/admin.py
Admin dashboard routes for TraceBack.
"""

from flask import Blueprint
from app.middleware.auth_middleware import token_required, role_required
from app.extensions import mongo
from app.utils.response import success

admin_bp = Blueprint("admin", __name__)


@admin_bp.route("/dashboard", methods=["GET"])
@token_required
@role_required("admin")
def dashboard_stats():
    """Return comprehensive dashboard statistics for admins."""
    # Aggregate case status counts
    status_counts = list(mongo.db.complaints.aggregate([
        {"$group": {"_id": "$status", "count": {"$sum": 1}}}
    ]))
    
    # Aggregate fraud type counts
    fraud_counts = list(mongo.db.complaints.aggregate([
        {"$group": {"_id": "$fraud_type", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}}
    ]))
    
    # Total losses vs recovered
    financials = list(mongo.db.complaints.aggregate([
        {"$group": {
            "_id": None,
            "total_lost": {"$sum": "$amount_lost"},
            "total_held": {"$sum": "$funds_held"}
        }}
    ]))
    
    return success({
        "status_distribution": {s["_id"]: s["count"] for s in status_counts},
        "fraud_distribution": {f["_id"]: f["count"] for f in fraud_counts},
        "financial_overview": financials[0] if financials else {"total_lost": 0, "total_held": 0}
    })
