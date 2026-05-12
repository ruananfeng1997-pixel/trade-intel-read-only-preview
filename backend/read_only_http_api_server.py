"""
Step 394E — Read-only HTTP API server.
GET-only. Localhost only. No DB write. No POST. No send. No webhook.
"""

import json
import os
import sys
from http.server import HTTPServer, BaseHTTPRequestHandler
from socketserver import ThreadingMixIn
from urllib.parse import urlparse


class ThreadedHTTPServer(ThreadingMixIn, HTTPServer):
    allow_reuse_address = True
    daemon_threads = True

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, os.path.join(PROJECT_ROOT, "backend", "app"))

import db_read_only_api

HOST = "127.0.0.1"
PORT = 18080

SAFETY_FIELDS = {
    "api_mode": "READ_ONLY_HTTP_GET_SERVER",
    "http_server_started": True,
    "post_endpoints_created": False,
    "real_send": "NOT_RUN",
    "webhook_call": "NOT_RUN",
    "production": "DISABLED",
    "retry": "DISABLED",
    "auto_send_enabled": False,
}


class ReadOnlyHandler(BaseHTTPRequestHandler):
    def _json(self, data, code=200):
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        response = {**data, **SAFETY_FIELDS} if isinstance(data, dict) else data
        if isinstance(response, dict):
            response["http_server_started"] = True
            response["post_endpoints_created"] = False
        self.wfile.write(json.dumps(response, ensure_ascii=False, indent=2).encode("utf-8"))

    def _405(self):
        self.send_response(405)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Allow", "GET")
        self.end_headers()
        self.wfile.write(json.dumps({
            "error": "Method not allowed", "allowed": ["GET"],
            **SAFETY_FIELDS,
        }, ensure_ascii=False).encode("utf-8"))

    def do_GET(self):
        parsed = urlparse(self.path)
        path = parsed.path.rstrip("/")

        # Route matching
        try:
            if path == "/api/db/status":
                self._json(db_read_only_api.get_db_project_status())
            elif path == "/api/db/watchlists":
                self._json(db_read_only_api.list_db_watchlists())
            elif path.startswith("/api/db/watchlists/"):
                wid = path.split("/api/db/watchlists/")[-1]
                result = db_read_only_api.get_db_watchlist(wid)
                if result is None:
                    self._json({"error": "Watchlist not found"}, 404)
                else:
                    self._json(result)
            elif path == "/api/db/review-queue":
                self._json(db_read_only_api.list_db_review_queue_candidates())
            elif path == "/api/db/delivered-events":
                self._json(db_read_only_api.list_db_delivered_events())
            elif path == "/api/db/scheduler-health":
                result = db_read_only_api.get_db_scheduler_health_latest()
                self._json(result if result else {"error": "No data"})
            elif path == "/api/db/daily-health":
                result = db_read_only_api.get_db_daily_health_latest()
                self._json(result if result else {"error": "No data"})
            elif path == "/api/db/local-alerts":
                result = db_read_only_api.get_db_local_alert_latest()
                self._json(result if result else {"error": "No data"})
            elif path == "/api/db/import-status":
                self._json(db_read_only_api.get_db_import_status())
            elif path == "/api/db/audit-log-summary":
                self._json(db_read_only_api.get_db_audit_log_summary())
            elif path == "/api/db/dashboard-snapshot":
                snap = db_read_only_api.build_all_db_snapshots()
                self._json(snap)
            else:
                self._json({"error": "Not found", "path": path}, 404)
        except Exception as e:
            self._json({"error": str(e), "path": path}, 500)

    def do_POST(self):
        self._405()

    def do_PUT(self):
        self._405()

    def do_PATCH(self):
        self._405()

    def do_DELETE(self):
        self._405()

    def log_message(self, format, *args):
        return  # Suppress console logging


def start_server():
    server = ThreadedHTTPServer((HOST, PORT), ReadOnlyHandler)
    print(f"[INFO] Read-only HTTP API server on http://{HOST}:{PORT}")
    print(f"[INFO] GET-only | No POST | No DB write | No send")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n[INFO] Server stopped.")
        server.server_close()


if __name__ == "__main__":
    start_server()
