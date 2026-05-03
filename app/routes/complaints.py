# FIXED: Implemented full complaint submission logic with file uploads and AI triage.
"""
app/routes/complaints.py
Complaint intake and case management routes for TraceBack.
"""

from flask import Blueprint, request, g
from pydantic import ValidationError
import json

from app.models.complaint import ComplaintCreate, VictimDetails, EvidenceFile, create_complaint
from app.models.user import add_case_to_user
from app.middleware.auth_middleware import token_required, get_current_user_id
from app.extensions import mongo, file_service, gemini_service, email_service
from app.utils.response import success, error, created, validation_error

complaints_bp = Blueprint("complaints", __name__)


@complaints_bp.route("/submit", methods=["POST"])
def submit():
    """
    Handle multi-part complaint submission.
    Expects 'json_data' (JSON string) and multiple files in the request.
    """
    # 1. Parse JSON data from form-data
    json_str = request.form.get("json_data")
    if not json_str:
        return error("Missing 'json_data' in form-data.", 400)
    
    try:
        raw_data = json.loads(json_str)
        # Handle evidence_files as empty list for validation initially
        if "evidence_files" not in raw_data:
            raw_data["evidence_files"] = []
        data = ComplaintCreate(**raw_data)
    except (json.JSONDecodeError, ValidationError) as e:
        return validation_error(getattr(e, "errors", lambda: str(e))())

    # 2. Extract User ID if logged in
    user_id = get_current_user_id()
    
    # 3. Handle File Uploads
    evidence_files = []
    files = request.files.getlist("evidence")
    if files:
        for file in files:
            if file.filename:
                url = file_service.upload_file(file, folder=f"cases/evidence")
                if url:
                    evidence_files.append(EvidenceFile(
                        filename=file.filename,
                        url=url,
                        mime_type=file.content_type or "application/octet-stream",
                        size_bytes=0 # We could get this from file.tell() if needed
                    ))
    
    # Update data with uploaded evidence
    data.evidence_files = evidence_files

    # 4. Create Complaint Record
    try:
        # The model helper expects VictimDetails object
        victim_info = data.victim
        complaint = create_complaint(
            data=data,
            user_id=user_id,
            victim=victim_info
        )
        
        # Link to user if logged in
        if user_id:
            add_case_to_user(user_id, complaint["case_id"])

    except Exception as e:
        return error(f"Failed to create complaint: {str(e)}", 500)

    # 5. Trigger AI Triage
    try:
        triage_report = gemini_service.analyze_complaint(complaint["description"])
        # Update complaint with triage report
        mongo.db.complaints.update_one(
            {"case_id": complaint["case_id"]},
            {"$set": {"triage_result": triage_report, "status": "triaged"}}
        )
        complaint["triage_result"] = triage_report
        complaint["status"] = "triaged"
    except Exception as e:
        print(f"AI Triage error: {e}")

    # 6. Send Confirmation Email
    if victim_info and victim_info.email:
        email_service.send_complaint_confirmation(
            victim_email=victim_info.email,
            victim_name=victim_info.name,
            case_id=complaint["case_id"],
            triage_result=complaint.get("triage_result") or {},
        )

    return created({
        "case_id": complaint["case_id"],
        "status": complaint["status"],
        "triage_report": complaint.get("triage_result")
    }, "Complaint submitted successfully.")


@complaints_bp.route("/<case_id>", methods=["GET"])
def get_complaint(case_id):
    """Retrieve details of a specific case by its Case ID."""
    case = mongo.db.complaints.find_one({"case_id": case_id.upper().strip()})
    if not case:
        return error("Case not found.", 404)
    
    # Serialize for return
    case["id"] = str(case.pop("_id"))
    if "user_id" in case and case["user_id"]:
        case["user_id"] = str(case["user_id"])
    
    return success(case)
