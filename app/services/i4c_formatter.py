import re
import logging

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# I4C Complaint-type mapping
# ---------------------------------------------------------------------------
FRAUD_TYPE_TO_I4C = {
    "investment_scam":  {
        "complaint_type": "Online Financial Fraud",
        "sub_category":   "Investment Fraud / Trading Scam",
    },
    "digital_arrest": {
        "complaint_type": "Cyber Crime Against Person",
        "sub_category":   "Online Blackmailing / Digital Arrest Scam",
    },
    "upi_bank_fraud": {
        "complaint_type": "Online Financial Fraud",
        "sub_category":   "UPI / Mobile Banking Fraud",
    },
    "sextortion": {
        "complaint_type": "Cyber Crime Against Person",
        "sub_category":   "Sextortion / Cyber Blackmail",
    },
    "ecommerce": {
        "complaint_type": "Online Financial Fraud",
        "sub_category":   "Online Shopping / E-Commerce Fraud",
    },
    "credit_card": {
        "complaint_type": "Online Financial Fraud",
        "sub_category":   "Credit / Debit Card Fraud",
    },
    "other": {
        "complaint_type": "Cyber Crime",
        "sub_category":   "Other Cyber Crime",
    },
}

# Mandatory I4C fields (top-level keys expected in the output)
REQUIRED_FIELDS = [
    "complaint_type",
    "sub_category",
    "accused_details",
    "transaction_details",
    "evidence_summary",
    "victim_info",
]


class I4CFormatter:
    """
    Formats a TraceBack complaint dict into the structured payload required
    by India's I4C (Indian Cyber Crime Coordination Centre) submission schema.
    """

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def format_for_i4c(self, complaint: dict) -> dict:
        """
        Map a raw complaint dict → I4C-compatible structured dict.

        Expected keys in `complaint`:
            fraud_type, amount_lost, incident_date, contact_channel,
            description, victim_name, victim_email, victim_phone,
            utr_number (optional), bank_name (optional),
            accused_upi (optional), accused_phone (optional),
            accused_account (optional)
        """
        fraud_type = str(complaint.get("fraud_type", "other")).lower().strip()
        i4c_meta = FRAUD_TYPE_TO_I4C.get(fraud_type, FRAUD_TYPE_TO_I4C["other"])

        formatted = {
            "complaint_type":    i4c_meta["complaint_type"],
            "sub_category":      i4c_meta["sub_category"],
            "accused_details":   self._structure_accused_details(complaint),
            "transaction_details": self._structure_transaction_details(complaint),
            "evidence_summary":  self._generate_evidence_summary(complaint),
            "victim_info":       self._structure_victim_info(complaint),
            "incident_date":     str(complaint.get("incident_date", "")),
            "contact_channel":   str(complaint.get("contact_channel", "")),
        }
        return formatted

    def validate_i4c_schema(self, formatted: dict) -> tuple[bool, list[str]]:
        """
        Validate that the formatted dict contains all required I4C fields
        and that critical sub-fields are non-empty.

        Returns:
            (is_valid: bool, missing_fields: list[str])
        """
        missing = []

        for field in REQUIRED_FIELDS:
            if field not in formatted or not formatted[field]:
                missing.append(field)

        # Deep validation on nested dicts
        tx = formatted.get("transaction_details", {})
        if not tx.get("amount"):
            missing.append("transaction_details.amount")

        accused = formatted.get("accused_details", {})
        if not any([accused.get("upi_id"), accused.get("phone"), accused.get("account_number")]):
            # Not hard-fail — it's common to not have accused info at the time of filing
            logger.warning("I4C validation: no accused contact info available.")

        is_valid = len(missing) == 0
        if not is_valid:
            logger.warning(f"I4C schema validation failed. Missing fields: {missing}")
        return is_valid, missing

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _structure_accused_details(self, complaint: dict) -> dict:
        """
        Detect UPI IDs, phone numbers, and account numbers from both
        explicit fields and free-text description.
        """
        description = str(complaint.get("description", ""))
        accused = {}

        # ---- Explicit fields take priority ----
        if complaint.get("accused_upi"):
            accused["upi_id"] = complaint["accused_upi"].strip()
        if complaint.get("accused_phone"):
            accused["phone"] = str(complaint["accused_phone"]).strip()
        if complaint.get("accused_account"):
            accused["account_number"] = str(complaint["accused_account"]).strip()
        if complaint.get("accused_bank"):
            accused["bank_name"] = complaint["accused_bank"].strip()
        if complaint.get("accused_name"):
            accused["name"] = complaint["accused_name"].strip()

        # ---- Auto-detect from description ----
        if not accused.get("upi_id"):
            upi_match = re.search(r"\b([\w.\-]+@[a-zA-Z]+)\b", description)
            if upi_match:
                accused["upi_id"] = upi_match.group(1)

        if not accused.get("phone"):
            phone_match = re.search(r"\b(\+?91[-\s]?)?[6-9]\d{9}\b", description)
            if phone_match:
                accused["phone"] = re.sub(r"\s+", "", phone_match.group())

        if not accused.get("account_number"):
            # Heuristic: standalone digit strings of 9–18 characters
            acc_match = re.search(r"\b(\d{9,18})\b", description)
            if acc_match:
                accused["account_number"] = acc_match.group(1)

        return accused

    def _structure_transaction_details(self, complaint: dict) -> dict:
        """Build structured transaction block expected by I4C."""
        amount = complaint.get("amount_lost", 0)
        try:
            amount = float(amount)
        except (ValueError, TypeError):
            amount = 0.0

        tx = {
            "amount": amount,
            "currency": "INR",
            "date": str(complaint.get("incident_date", "")),
        }

        if complaint.get("utr_number"):
            tx["utr"] = str(complaint["utr_number"]).strip()
        if complaint.get("bank_name"):
            tx["bank"] = complaint["bank_name"].strip()
        if complaint.get("transaction_id"):
            tx["transaction_id"] = str(complaint["transaction_id"]).strip()
        if complaint.get("contact_channel"):
            tx["payment_channel"] = complaint["contact_channel"]

        # Auto-detect UTR from description (22-char alphanumeric typical for IMPS/UPI)
        if not tx.get("utr"):
            description = str(complaint.get("description", ""))
            utr_match = re.search(r"\b([A-Z0-9]{12,22})\b", description)
            if utr_match:
                tx["utr"] = utr_match.group(1)

        return tx

    def _generate_evidence_summary(self, complaint: dict) -> str:
        """Return first 500 characters of description as evidence summary."""
        description = str(complaint.get("description", "")).strip()
        if not description:
            return "No description provided."
        summary = description[:500]
        if len(description) > 500:
            summary += "…"
        return summary

    def _structure_victim_info(self, complaint: dict) -> dict:
        """Extract victim contact information."""
        return {
            "name":  str(complaint.get("victim_name", "")).strip(),
            "email": str(complaint.get("victim_email", "")).strip(),
            "phone": str(complaint.get("victim_phone", "")).strip(),
            "city":  str(complaint.get("victim_city", "")).strip(),
            "state": str(complaint.get("victim_state", "")).strip(),
        }
