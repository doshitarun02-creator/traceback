# FIXED: Implemented expert listing route with category filtering.
"""
app/routes/experts.py
Expert network routes for TraceBack.
"""

from flask import Blueprint, request
from app.models.expert import list_experts
from app.utils.response import success

experts_bp = Blueprint("experts", __name__)


@experts_bp.route("/", methods=["GET"])
def get_experts():
    """List all verified experts, optionally filtered by fraud category."""
    category = request.args.get("category")
    if category == 'all': category = None
    
    online_only = request.args.get("online_only", "false").lower() == "true"
    page = int(request.args.get("page", 1))
    
    result = list_experts(
        fraud_category=category,
        online_only=online_only,
        page=page
    )
    
    return success({
        "experts": result["items"],
        "total": result["total"],
        "page": result["page"],
        "pages": result["pages"]
    })
