# FIXED: Implemented live stats route for the hero section.
"""
app/routes/cases.py
Case and statistics routes for TraceBack.
"""

from flask import Blueprint
from datetime import datetime, timezone
from app.extensions import mongo
from app.utils.response import success

cases_bp = Blueprint("cases", __name__)


@cases_bp.route("/stats/live", methods=["GET"])
def get_live_stats():
    """Return live counter data and platform statistics."""
    # Real-time counter logic based on 88,976 complaints/day
    complaints_per_day = 88976
    now = datetime.now(timezone.utc)
    start_of_day = now.replace(hour=0, minute=0, second=0, microsecond=0)
    elapsed_seconds = (now - start_of_day).total_seconds()
    
    current_count = int(elapsed_seconds * (complaints_per_day / 86400))
    
    # Fetch platform stats from DB
    total_complaints = mongo.db.complaints.count_documents({})
    total_recovered = mongo.db.complaints.aggregate([
        {"$group": {"_id": None, "total": {"$sum": "$funds_held"}}}
    ])
    total_recovered = list(total_recovered)
    total_recovered_amount = total_recovered[0]["total"] if total_recovered else 0

    return success({
        "live_complaints_today": current_count,
        "platform_total_cases": total_complaints,
        "platform_total_recovered": total_recovered_amount,
        "timestamp": now.isoformat()
    })
