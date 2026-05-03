"""
app/utils/validators.py
Input validation helpers for TraceBack.
All functions are pure (no I/O) and return bool or sanitized str.
"""

from __future__ import annotations

import html
import re

# ─── Phone ─────────────────────────────────────────────────────────────────────

# Valid Indian mobile prefix: starts with 6, 7, 8, or 9
_PHONE_RE = re.compile(r"^(?:\+91|91|0)?([6-9]\d{9})$")


def validate_indian_phone(phone: str) -> bool:
    """
    Return True if *phone* is a valid Indian mobile number.

    Accepts:
    - Raw 10-digit numbers starting with 6-9 (e.g. 9876543210)
    - Numbers prefixed with +91, 91, or 0 (e.g. +919876543210)

    Rejects landlines, short numbers, and international prefixes
    other than +91.
    """
    return bool(_PHONE_RE.match(phone.strip()))


# ─── UPI ID ────────────────────────────────────────────────────────────────────

# username@bank — username: alphanumeric, dots, hyphens, plus signs
# bank handle: letters only, 3+ chars
_UPI_RE = re.compile(r"^[\w.\-+]{3,256}@[a-zA-Z]{3,64}$")


def validate_upi_id(upi: str) -> bool:
    """
    Return True if *upi* matches the VPA (Virtual Payment Address) format
    used by UPI — e.g. user@oksbi, 9876543210@paytm, name.surname@upi.
    """
    return bool(_UPI_RE.match(upi.strip()))


# ─── PAN ───────────────────────────────────────────────────────────────────────

# Format: AAAAA9999A — 5 uppercase alpha, 4 digits, 1 uppercase alpha
_PAN_RE = re.compile(r"^[A-Z]{5}[0-9]{4}[A-Z]$")


def validate_pan(pan: str) -> bool:
    """
    Return True if *pan* is a syntactically valid Indian PAN card number.
    Does NOT verify with income-tax database.
    """
    return bool(_PAN_RE.match(pan.strip().upper()))


# ─── IFSC ──────────────────────────────────────────────────────────────────────

# Format: AAAA0XXXXXX — 4 alpha (bank code), literal 0, 6 alphanumeric (branch)
_IFSC_RE = re.compile(r"^[A-Z]{4}0[A-Z0-9]{6}$")


def validate_ifsc(ifsc: str) -> bool:
    """
    Return True if *ifsc* is a syntactically valid RBI IFSC code.
    Does NOT check against live RBI registry.
    """
    return bool(_IFSC_RE.match(ifsc.strip().upper()))


# ─── HTML sanitizer ────────────────────────────────────────────────────────────

# Strip tags — allow NO HTML through; escape all special chars.
_TAG_RE = re.compile(r"<[^>]+>")
_WHITESPACE_RE = re.compile(r"\s+")

MAX_INPUT_LENGTH = 5_000   # default cap for free-text fields


def sanitize_input(text: str, max_length: int = MAX_INPUT_LENGTH) -> str:
    """
    Strip HTML tags, escape remaining special characters, collapse
    whitespace, and truncate to *max_length* characters.

    Usage::

        description = sanitize_input(request.form["description"])
    """
    if not isinstance(text, str):
        return ""

    # 1. Remove HTML tags
    cleaned = _TAG_RE.sub("", text)

    # 2. Escape remaining HTML-special chars (&, <, >, ", \'  etc.)
    cleaned = html.escape(cleaned, quote=True)

    # 3. Collapse multiple whitespace to single space and strip edges
    cleaned = _WHITESPACE_RE.sub(" ", cleaned).strip()

    # 4. Hard-truncate
    return cleaned[:max_length]
