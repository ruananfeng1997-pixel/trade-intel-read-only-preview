#!/usr/bin/env python3
"""
start_read_only_preview.py — GET-only server entry point for Render.

LOCAL_ONLY / NO_ACTUAL_CLOUD_RESOURCES / NO_SEND / NO_PRODUCTION.

Only accepts GET requests. POST/PUT/PATCH/DELETE return 405.
No send, webhook, production, retry, source ingestion, or DB write.
"""

import os
import sys

# Ensure bundled backend is importable
BUNDLE_DIR = os.path.dirname(os.path.abspath(__file__))
BACKEND_DIR = os.path.join(BUNDLE_DIR, "backend")
if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)

# -- Configuration ---------------------------------------------------------
HOST = "0.0.0.0"
PORT = int(os.environ.get("PORT", "10000"))
APP_MODE = os.environ.get("APP_MODE", "READ_ONLY_PREVIEW")

# -- Safety assertions -----------------------------------------------------
assert APP_MODE == "READ_ONLY_PREVIEW", f"APP_MODE must be READ_ONLY_PREVIEW, got {APP_MODE}"
assert os.environ.get("PRODUCTION", "DISABLED") == "DISABLED", "PRODUCTION must be DISABLED"
assert os.environ.get("RETRY", "DISABLED") == "DISABLED", "RETRY must be DISABLED"
assert os.environ.get("AUTO_SEND_ENABLED", "false").lower() == "false", "AUTO_SEND must be false"

# -- Resolve DB path -------------------------------------------------------
data_dir = os.path.join(BUNDLE_DIR, "data")
db_path = os.path.join(data_dir, "trade_intel.read_only_preview.sqlite3")
if not os.path.exists(db_path):
    print(f"ERROR: Read-only DB not found at {db_path}")
    sys.exit(1)
os.environ["TRADE_INTEL_DB_PATH"] = db_path

# -- Start the packaged read-only server -----------------------------------
try:
    import read_only_http_api_server
except ImportError as e:
    print(f"ERROR: Could not import read_only_http_api_server: {e}")
    sys.exit(1)

# Set module-level config before calling start_server()
read_only_http_api_server.HOST = HOST
read_only_http_api_server.PORT = PORT
read_only_http_api_server.start_server()
