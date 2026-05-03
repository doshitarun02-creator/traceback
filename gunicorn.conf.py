"""
TraceBack — Gunicorn Configuration
=====================================
Used by Render's production deployment via the Procfile:
  web: gunicorn --config gunicorn.conf.py "app:create_app()"

Render injects the PORT environment variable automatically;
gunicorn reads it here so you never hard-code a port.

References:
  https://docs.gunicorn.org/en/stable/settings.html
"""

import multiprocessing
import os

# ── Network ───────────────────────────────────────────────────────────────────

# Render injects $PORT; fall back to 5000 for local testing.
_port = os.environ.get("PORT", "5000")
bind = f"0.0.0.0:{_port}"

# ── Workers ───────────────────────────────────────────────────────────────────

# Recommended formula: (2 × CPU cores) + 1
workers = 2
threads = 4

# Worker class: sync (default) is fine for Flask.
worker_class = "gthread"

# Maximum requests a worker handles before it is gracefully restarted.
# Prevents slow memory leaks from accumulating indefinitely.
max_requests = 1000
max_requests_jitter = 100       # randomised jitter prevents thundering-herd restarts

# ── Timeouts ──────────────────────────────────────────────────────────────────

# Seconds gunicorn waits for a worker to handle a request before killing it.
# Keep >= 30 s to accommodate AI (Gemini) API calls that may take several seconds.
timeout = 120

# Time (seconds) to wait for workers to finish in-flight requests on SIGTERM.
graceful_timeout = 30

# Idle keepalive connection timeout.
keepalive = 5

# ── Logging ───────────────────────────────────────────────────────────────────

# Log to stdout/stderr so Render's log aggregator captures everything.
accesslog = "-"
errorlog = "-"
loglevel = os.environ.get("LOG_LEVEL", "info")

# Include request timing in the access log.
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s %(L)ss'

# ── Process ───────────────────────────────────────────────────────────────────

# PID file path (optional — useful for systemd / local process management).
# pidfile = "/tmp/traceback.pid"

# Preload the app before forking workers.
# Saves memory (copy-on-write) but means code changes require a full restart.
preload_app = True

# Forward the X-Forwarded-For header from Render's reverse proxy.
forwarded_allow_ips = "*"
proxy_protocol = False
