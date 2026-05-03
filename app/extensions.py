# FIXED: Instantiated Gemini, Cloudinary, and Email services for use in routes.
"""
TraceBack — Flask Extension Instances
=======================================
All extensions are instantiated here WITHOUT the app object (two-step
initialisation pattern) to prevent circular imports.

They are bound to the app inside ``create_app()`` via ``ext.init_app(app)``.

Import pattern for the rest of the codebase:
    from app.extensions import mongo, limiter, mail
"""

from flask_pymongo import PyMongo
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_mail import Mail

from app.services.gemini_service import GeminiTriageService
from app.services.file_service import CloudinaryFileService
from app.services.email_service import EmailService
from app.services.i4c_formatter import I4CFormatter
import os



# ── MongoDB Atlas ──────────────────────────────────────────────────────────────
# Provides ``mongo.db`` for all database operations.
# Connection URI is read from ``app.config["MONGO_URI"]`` at init_app() time.
# The database name (``traceback``) is embedded in the URI.
mongo: PyMongo = PyMongo()


# ── Rate Limiter ───────────────────────────────────────────────────────────────
# Uses the client's IP address as the rate-limit key by default.
# Storage backend is configured via ``app.config["RATELIMIT_STORAGE_URI"]``:
#   - Development / single-worker: "memory://"
#   - Production (multi-worker gunicorn): Redis via REDIS_URL env var
# Apply per-route limits with: @limiter.limit("5 per minute")
# Exempt a route entirely with: @limiter.exempt
limiter: Limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"],
    storage_uri="memory://",          # overridden by init_app() config
    headers_enabled=True,             # exposes X-RateLimit-* headers
)


# ── Flask-Mail ─────────────────────────────────────────────────────────────────
# Used for:
#   - OTP / email verification
#   - Case status update notifications
#   - Password reset links
# SMTP credentials are read from config at init_app() time.
mail: Mail = Mail()


# ── TraceBack Services ─────────────────────────────────────────────────────────

# Gemini AI Triage
gemini_service = GeminiTriageService(
    api_key=os.environ.get("GEMINI_API_KEY", ""),
    model=os.environ.get("GEMINI_MODEL", "gemini-1.5-flash")
)

# Cloudinary File Storage
file_service = CloudinaryFileService(
    cloud_name=os.environ.get("CLOUDINARY_CLOUD_NAME", ""),
    api_key=os.environ.get("CLOUDINARY_API_KEY", ""),
    api_secret=os.environ.get("CLOUDINARY_API_SECRET", "")
)

# I4C Schema Formatter
i4c_formatter = I4CFormatter()

# Email Notifications (wraps Flask-Mail with TraceBack templates)
email_service = EmailService() # Initialised with defaults, config updated later if needed

