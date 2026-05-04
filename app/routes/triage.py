# FIXED: Created triage route for real-time AI analysis of fraud descriptions.
"""
app/routes/triage.py
AI Triage routes for TraceBack.
"""

from flask import Blueprint, request
from app.extensions import gemini_service
from app.utils.response import success, error

triage_bp = Blueprint("triage", __name__)


@triage_bp.route("/analyze", methods=["POST"])
def analyze():
    """Analyze a fraud description using Gemini AI."""
    data = request.get_json()
    description = data.get("description")
    
    if not description or len(description) < 10:
        return error("Description too short for analysis.", 400)
    
    try:
        analysis = gemini_service.analyze_complaint({"description": description})
        return success(analysis)
    except Exception as e:
        return error(f"AI Analysis failed: {str(e)}", 500)
