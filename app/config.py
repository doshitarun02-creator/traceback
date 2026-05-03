"""
TraceBack — Configuration Classes
===================================
Three configuration tiers that share a common base:

  BaseConfig        — defaults shared across all environments
  DevelopmentConfig — local development (verbose logging, no SSL)
  ProductionConfig  — Render deployment (strict security, gunicorn)
  TestingConfig     — pytest suite (in-memory DB, TESTING=True)

Usage in the factory:
  app.config.from_object(config_map[env_name])
"""

import os
from datetime import timedelta


class BaseConfig:
    """Shared defaults. Never instantiated directly."""

    # ── Core Flask ─────────────────────────────────────────────────────────
    SECRET_KEY: str = os.environ.get("SECRET_KEY", "change-me-in-production")
    JSON_SORT_KEYS: bool = False
    MAX_CONTENT_LENGTH: int = 16 * 1024 * 1024  # 16 MB upload limit

    # ── MongoDB Atlas ─────────────────────────────────────────────────────
    # Flask-PyMongo specifically looks for MONGO_URI.
    # We read from MONGODB_URI (Render default) or MONGO_URI.
    MONGO_URI: str = os.environ.get(
        "MONGODB_URI", 
        os.environ.get("MONGO_URI", "mongodb://localhost:27017/traceback")
    )
    # Flask-PyMongo uses MONGO_URI; the db name is embedded in the URI.
    # Atlas URI format:
    #   mongodb+srv://<user>:<pass>@<cluster>.mongodb.net/traceback?retryWrites=true&w=majority

    # ── JWT ───────────────────────────────────────────────────────────────
    JWT_SECRET_KEY: str = os.environ.get("JWT_SECRET_KEY", "change-me-jwt-secret")
    JWT_ACCESS_TOKEN_EXPIRES: timedelta = timedelta(
        hours=int(os.environ.get("JWT_ACCESS_EXPIRE_HOURS", 24))
    )
    JWT_REFRESH_TOKEN_EXPIRES: timedelta = timedelta(
        days=int(os.environ.get("JWT_REFRESH_EXPIRE_DAYS", 30))
    )
    JWT_ALGORITHM: str = os.environ.get("JWT_ALGORITHM", "HS256")

    # ── CORS ──────────────────────────────────────────────────────────────
    CORS_ORIGINS: list[str] = os.environ.get(
        "CORS_ORIGINS", "http://localhost:5173"
    ).split(",")

    # ── Rate Limiting (Flask-Limiter) ─────────────────────────────────────
    RATELIMIT_STORAGE_URI: str = os.environ.get(
        "RATELIMIT_STORAGE_URI", "memory://"
    )
    RATELIMIT_DEFAULT: str = os.environ.get("RATELIMIT_DEFAULT", "200 per day;50 per hour")
    RATELIMIT_HEADERS_ENABLED: bool = True

    # ── Flask-Mail (SMTP) ─────────────────────────────────────────────────
    MAIL_SERVER: str = os.environ.get("MAIL_SERVER", "smtp.gmail.com")
    MAIL_PORT: int = int(os.environ.get("MAIL_PORT", 587))
    MAIL_USE_TLS: bool = os.environ.get("MAIL_USE_TLS", "true").lower() == "true"
    MAIL_USE_SSL: bool = os.environ.get("MAIL_USE_SSL", "false").lower() == "true"
    MAIL_USERNAME: str | None = os.environ.get("MAIL_USERNAME")
    MAIL_PASSWORD: str | None = os.environ.get("MAIL_PASSWORD")
    MAIL_DEFAULT_SENDER: str = os.environ.get(
        "MAIL_DEFAULT_SENDER", "noreply@traceback.in"
    )

    # ── Cloudinary (Evidence / Document Storage) ──────────────────────────
    CLOUDINARY_CLOUD_NAME: str = os.environ.get("CLOUDINARY_CLOUD_NAME", "")
    CLOUDINARY_API_KEY: str = os.environ.get("CLOUDINARY_API_KEY", "")
    CLOUDINARY_API_SECRET: str = os.environ.get("CLOUDINARY_API_SECRET", "")

    # ── Google Gemini AI ──────────────────────────────────────────────────
    GEMINI_API_KEY: str = os.environ.get("GEMINI_API_KEY", "")
    GEMINI_MODEL: str = os.environ.get("GEMINI_MODEL", "gemini-1.5-flash")

    # ── Bcrypt ────────────────────────────────────────────────────────────
    BCRYPT_LOG_ROUNDS: int = int(os.environ.get("BCRYPT_LOG_ROUNDS", 12))

    # ── Application-specific ──────────────────────────────────────────────
    APP_NAME: str = "TraceBack"
    APP_VERSION: str = os.environ.get("APP_VERSION", "1.0.0")
    SUPPORT_EMAIL: str = os.environ.get("SUPPORT_EMAIL", "support@traceback.in")
    FRONTEND_URL: str = os.environ.get("FRONTEND_URL", "http://localhost:5000")


class DevelopmentConfig(BaseConfig):
    """Local development — verbose, relaxed security, no SSL enforcement."""

    DEBUG: bool = True
    TESTING: bool = False

    # Detailed MongoDB query logging
    MONGO_LOG_LEVEL: str = "DEBUG"

    # Relaxed rate limits so manual testing isn't throttled
    RATELIMIT_DEFAULT: str = "10000 per day;1000 per hour"

    # Disable email sending in dev; print to console instead
    MAIL_SUPPRESS_SEND: bool = True
    MAIL_DEBUG: bool = True


class ProductionConfig(BaseConfig):
    """
    Render deployment via gunicorn.
    All sensitive values MUST be provided as Render environment variables —
    never hard-coded here.
    """

    DEBUG: bool = False
    TESTING: bool = False

    # Force HTTPS redirects
    PREFERRED_URL_SCHEME: str = "https"
    SESSION_COOKIE_SECURE: bool = True
    SESSION_COOKIE_HTTPONLY: bool = True
    SESSION_COOKIE_SAMESITE: str = "Lax"

    # Use Redis on Render for distributed rate limiting across gunicorn workers
    RATELIMIT_STORAGE_URI: str = os.environ.get(
        "REDIS_URL", "memory://"
    )

    # Tighter bcrypt rounds for production
    BCRYPT_LOG_ROUNDS: int = int(os.environ.get("BCRYPT_LOG_ROUNDS", 14))


class TestingConfig(BaseConfig):
    """
    pytest suite — fast, isolated, no external calls.
    Uses a separate test database so production/dev data is never touched.
    """

    DEBUG: bool = True
    TESTING: bool = True

    # Isolated test database
    MONGO_URI: str = os.environ.get(
        "TEST_MONGO_URI", "mongodb://localhost:27017/traceback_test"
    )

    # Disable CSRF/rate-limit during tests
    WTF_CSRF_ENABLED: bool = False
    RATELIMIT_ENABLED: bool = False

    # Never actually send emails during tests
    MAIL_SUPPRESS_SEND: bool = True

    # Faster bcrypt for test speed
    BCRYPT_LOG_ROUNDS: int = 4

    # Short-lived tokens make expiry tests faster
    JWT_ACCESS_TOKEN_EXPIRES: timedelta = timedelta(seconds=30)
    JWT_REFRESH_TOKEN_EXPIRES: timedelta = timedelta(minutes=5)


# ── Config registry ───────────────────────────────────────────────────────────
config_map: dict[str, type[BaseConfig]] = {
    "development": DevelopmentConfig,
    "production": ProductionConfig,
    "testing": TestingConfig,
}
