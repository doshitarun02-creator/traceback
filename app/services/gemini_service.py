import json
import re
import logging
from datetime import datetime, timezone

logger = logging.getLogger(__name__)

try:
    import google.generativeai as genai
    GENAI_AVAILABLE = True
except ImportError:
    GENAI_AVAILABLE = False
    logger.warning("google-generativeai not installed. GeminiTriageService will use fallback only.")


class GeminiTriageService:

    def __init__(self, api_key: str, model: str = "gemini-1.5-flash"):
        self.api_key = api_key
        self.model_name = model
        self.model = None
        if GENAI_AVAILABLE and api_key:
            try:
                genai.configure(api_key=api_key)
                self.model = genai.GenerativeModel(
                    model_name=model,
                    generation_config=genai.types.GenerationConfig(
                        temperature=0.1,
                        response_mime_type="application/json",
                    ),
                )
                logger.info(f"GeminiTriageService initialised with model={model}")
            except Exception as e:
                logger.error(f"Failed to initialise Gemini model: {e}")

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def analyze_complaint(self, complaint_data: dict) -> dict:
        """
        Primary entry-point. Calls Gemini; falls back to rule-based triage
        if the API call fails or returns unparseable output.
        """
        if self.model is None:
            logger.warning("Gemini model unavailable — using fallback triage.")
            return self._fallback_triage(complaint_data)

        try:
            prompt = self._build_prompt(complaint_data)
            response = self.model.generate_content(prompt)
            raw_text = response.text
            result = self._parse_response(raw_text)
            if not result:
                raise ValueError("Empty parsed result from Gemini response.")
            result["source"] = "gemini"
            return result
        except Exception as e:
            logger.error(f"Gemini analyze_complaint failed: {e} — using fallback.")
            fallback = self._fallback_triage(complaint_data)
            fallback["source"] = "fallback"
            return fallback

    # ------------------------------------------------------------------
    # Prompt builder
    # ------------------------------------------------------------------

    def _build_prompt(self, data: dict) -> str:
        fraud_type      = data.get("fraud_type", "unknown")
        amount_lost     = data.get("amount_lost", 0)
        incident_date   = data.get("incident_date", "unknown")
        contact_channel = data.get("contact_channel", "unknown")
        description     = data.get("description", "No description provided.")

        prompt = (
            "You are an expert cybercrime triage analyst for TraceBack, India's cybercrime recovery platform.\n"
            "Analyze this fraud complaint and return a structured JSON response ONLY — no markdown, no explanation.\n\n"
            f"Complaint: fraud_type={fraud_type}, amount=₹{amount_lost}, date={incident_date}, channel={contact_channel}\n"
            f"Description: {description}\n\n"
            "Return JSON with EXACTLY this structure:\n"
            "{\n"
            '  "fraud_type_detected": "investment_scam|digital_arrest|upi_bank_fraud|sextortion|ecommerce|credit_card|other",\n'
            '  "urgency_score": "CRITICAL|HIGH|MEDIUM|LOW",\n'
            '  "urgency_color": "red|amber|yellow|green",\n'
            '  "hours_remaining": <int>,\n'
            '  "recommended_tier": "scout|trace|forge",\n'
            '  "i4c_compatibility": true|false,\n'
            '  "i4c_structured_data": {\n'
            '    "complaint_type": "",\n'
            '    "sub_category": "",\n'
            '    "accused_details": {},\n'
            '    "transaction_details": {}\n'
            "  },\n"
            '  "immediate_actions": ["Call 1930 immediately", "<action 2>", "<action 3>"],\n'
            '  "confidence_score": <float 0.0-1.0>,\n'
            '  "analysis_summary": "<2-3 sentences for victim in plain language>"\n'
            "}\n\n"
            "Rules:\n"
            "- CRITICAL if amount > ₹1,00,000 AND incident is < 24 hours ago.\n"
            "- forge tier if amount > ₹10,00,000.\n"
            "- trace tier if amount is ₹50,000–₹10,00,000.\n"
            "- scout tier if amount < ₹50,000.\n"
            "- The first immediate action MUST always be 'Call 1930 immediately'.\n"
            "- i4c_compatibility should be true when enough structured data is available.\n"
        )
        return prompt

    # ------------------------------------------------------------------
    # Response parser
    # ------------------------------------------------------------------

    def _parse_response(self, raw_text: str) -> dict | None:
        """Strip markdown code fences and parse JSON safely."""
        if not raw_text:
            return None
        # Remove ```json ... ``` or ``` ... ``` fences
        cleaned = re.sub(r"^```(?:json)?\s*", "", raw_text.strip(), flags=re.IGNORECASE)
        cleaned = re.sub(r"\s*```$", "", cleaned.strip())
        try:
            return json.loads(cleaned)
        except json.JSONDecodeError as e:
            logger.error(f"JSON parse error: {e} | raw_text[:200]={raw_text[:200]}")
            # Attempt to extract the first JSON object as a last resort
            match = re.search(r"\{.*\}", cleaned, re.DOTALL)
            if match:
                try:
                    return json.loads(match.group())
                except json.JSONDecodeError:
                    pass
            return None

    # ------------------------------------------------------------------
    # Deterministic fallback
    # ------------------------------------------------------------------

    def _fallback_triage(self, data: dict) -> dict:
        """
        Rule-based triage that always produces a valid result even when
        Gemini is unavailable or returns bad output.
        """
        amount       = float(data.get("amount_lost", 0) or 0)
        fraud_type   = str(data.get("fraud_type", "other")).lower().strip()
        description  = str(data.get("description", ""))
        incident_date_raw = data.get("incident_date")

        # ---- Tier & urgency by amount ----
        if amount > 1_000_000:
            tier = "forge"
        elif amount >= 50_000:
            tier = "trace"
        else:
            tier = "scout"

        # ---- Hours since incident ----
        hours_since = self._hours_since_incident(incident_date_raw)
        hours_remaining = max(0, 72 - int(hours_since)) if hours_since is not None else 48

        # ---- Urgency ----
        if amount > 100_000 and (hours_since is not None and hours_since < 24):
            urgency_score = "CRITICAL"
            urgency_color = "red"
        elif amount > 50_000 or (hours_since is not None and hours_since < 48):
            urgency_score = "HIGH"
            urgency_color = "amber"
        elif amount > 10_000:
            urgency_score = "MEDIUM"
            urgency_color = "yellow"
        else:
            urgency_score = "LOW"
            urgency_color = "green"

        # ---- Fraud type normalisation ----
        fraud_type_map = {
            "investment": "investment_scam",
            "digital_arrest": "digital_arrest",
            "upi": "upi_bank_fraud",
            "bank": "upi_bank_fraud",
            "sextortion": "sextortion",
            "ecommerce": "ecommerce",
            "credit": "credit_card",
        }
        detected_type = "other"
        for key, val in fraud_type_map.items():
            if key in fraud_type or key in description.lower():
                detected_type = val
                break

        # ---- I4C structured data ----
        i4c_data = {
            "complaint_type": "Cyber Financial Fraud",
            "sub_category": detected_type.replace("_", " ").title(),
            "accused_details": self._extract_accused_details(description),
            "transaction_details": {
                "amount": amount,
                "currency": "INR",
                "date": str(incident_date_raw or ""),
            },
        }

        return {
            "fraud_type_detected": detected_type,
            "urgency_score": urgency_score,
            "urgency_color": urgency_color,
            "hours_remaining": hours_remaining,
            "recommended_tier": tier,
            "i4c_compatibility": bool(amount and incident_date_raw),
            "i4c_structured_data": i4c_data,
            "immediate_actions": [
                "Call 1930 immediately",
                "Report on cybercrime.gov.in within the next few hours",
                "Do not transfer any more money or share OTPs",
            ],
            "confidence_score": 0.55,
            "analysis_summary": (
                f"This appears to be a {detected_type.replace('_', ' ')} case involving ₹{amount:,.0f}. "
                f"Urgency is {urgency_score.lower()} — please act quickly. "
                "Call the national cybercrime helpline 1930 immediately to freeze the fraudulent transaction."
            ),
            "source": "fallback",
        }

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _hours_since_incident(self, incident_date_raw) -> float | None:
        if not incident_date_raw:
            return None
        for fmt in ("%Y-%m-%dT%H:%M:%S", "%Y-%m-%d %H:%M:%S", "%Y-%m-%d", "%d-%m-%Y", "%d/%m/%Y"):
            try:
                incident_dt = datetime.strptime(str(incident_date_raw), fmt)
                # Treat as IST (UTC+5:30) → convert to UTC for comparison
                now_utc = datetime.now(timezone.utc).replace(tzinfo=None)
                diff = now_utc - incident_dt
                return diff.total_seconds() / 3600
            except ValueError:
                continue
        return None

    def _extract_accused_details(self, description: str) -> dict:
        details = {}
        upi_match = re.search(r"\b([\w.\-]+@[\w]+)\b", description)
        if upi_match:
            details["upi_id"] = upi_match.group(1)
        phone_match = re.search(r"\b(\+?91[-\s]?)?[6-9]\d{9}\b", description)
        if phone_match:
            details["phone"] = phone_match.group().strip()
        account_match = re.search(r"\b(\d{9,18})\b", description)
        if account_match:
            details["account_number"] = account_match.group(1)
        return details
