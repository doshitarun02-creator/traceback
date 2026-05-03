"""
TraceBack — Flask Application Factory
======================================
Initialises all extensions, registers blueprints, configures CORS,
and mounts the static frontend (traceback_v1.html).
"""

import os
from flask import Flask, jsonify, send_from_directory
from flask_cors import CORS
from dotenv import load_dotenv

from app.config import config_map
from app.extensions import mongo, limiter, mail


def create_app(config_name: str | None = None) -> Flask:
    """
    Application factory.

    Parameters
    ----------
    config_name : str, optional
        One of ``"development"``, ``"production"``, or ``"testing"``.
        Falls back to the ``FLASK_ENV`` environment variable, then
        ``"development"``.
    """
    load_dotenv()

    if config_name is None:
        config_name = os.environ.get("FLASK_ENV", "development")

    app = Flask(
        __name__,
        # Serve static files from app/static/ at /static/
        static_folder=os.path.join(os.path.dirname(__file__), "..", "static"),
        static_url_path="/static",
    )

    # ── Configuration ─────────────────────────────────────────────────────────
    app.config.from_object(config_map[config_name])

    # ── Extensions ────────────────────────────────────────────────────────────
    mongo.init_app(app)
    limiter.init_app(app)
    mail.init_app(app)

    # ── CORS ──────────────────────────────────────────────────────────────────
    CORS(
        app,
        resources={r"/api/*": {"origins": app.config["CORS_ORIGINS"]}},
        supports_credentials=True,
    )

    # ── Blueprints ────────────────────────────────────────────────────────────
    from app.routes.auth import auth_bp
    from app.routes.complaints import complaints_bp
    from app.routes.experts import experts_bp
    from app.routes.cases import cases_bp
    from app.routes.admin import admin_bp
    from app.routes.triage import triage_bp

    app.register_blueprint(auth_bp, url_prefix="/api/auth")
    app.register_blueprint(complaints_bp, url_prefix="/api/complaints")
    app.register_blueprint(experts_bp, url_prefix="/api/experts")
    app.register_blueprint(cases_bp, url_prefix="/api/cases")
    app.register_blueprint(admin_bp, url_prefix="/api/admin")
    app.register_blueprint(triage_bp, url_prefix="/api/triage")

    # ── Frontend entry point ──────────────────────────────────────────────────
    @app.route("/", defaults={"path": ""})
    @app.route("/<path:path>")
    def serve_frontend(path: str):
        """
        Catch-all route that serves the single-page frontend.
        API routes registered at /api/* take priority over this handler.
        Static assets at /static/* are handled by Flask's built-in static file
        serving before this catch-all is reached.
        """
        static_dir = app.static_folder
        frontend_file = "traceback_v1.html"
        return send_from_directory(static_dir, frontend_file)

    # ── Health check ──────────────────────────────────────────────────────────
    @app.route("/health")
    @limiter.exempt
    def health():
        """
        Lightweight liveness probe used by Render and uptime monitors.
        Returns HTTP 200 with a JSON body so load balancers can confirm the
        process is alive and the database connection is reachable.
        """
        try:
            # Ping MongoDB to verify the connection is live.
            mongo.db.command("ping")
            db_status = "connected"
        except Exception as exc:  # pragma: no cover
            db_status = f"error: {exc}"

        return jsonify(
            {
                "status": "ok",
                "service": "traceback-api",
                "environment": config_name,
                "database": db_status,
            }
        ), 200

    return app
