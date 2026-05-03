# TraceBack — Windows Production Runner
# ======================================
# This script uses Waitress to serve the Flask app on Windows.

from waitress import serve
from run import app
import os

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    print(f"🚀 TraceBack Production Server starting on http://localhost:{port}")
    print("Environment: Production (Windows/Waitress)")
    
    serve(app, host='0.0.0.0', port=port, threads=4)
