"""
Step 392U — DB read-only API functions.
Read-only SQLite queries. No HTTP server. No DB write. No send. No webhook.
"""

import json
import os
import sqlite3
import sys

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
DB_PATH = os.path.join(PROJECT_ROOT, "backend", "state", "trade_intel.local.sqlite3")

SAFETY_FIELDS = {
    "real_send": "NOT_RUN",
    "webhook_call": "NOT_RUN",
    "delivered_history_modified": False,
    "production": "DISABLED",
    "retry": "DISABLED",
    "auto_send_enabled": False,
}


def _connect():
    return sqlite3.connect(f"file:{DB_PATH}?mode=ro", uri=True)


def get_db_project_status():
    conn = _connect()
    c = conn.cursor()
    wl = c.execute("SELECT COUNT(*) FROM watchlists").fetchone()[0]
    de = c.execute("SELECT COUNT(*) FROM delivered_events").fetchone()[0]
    rq = c.execute("SELECT COUNT(*) FROM review_queue_candidates").fetchone()[0]
    sh = c.execute("SELECT COUNT(*) FROM scheduler_health_reports").fetchone()[0]
    conn.close()
    return {
        "watchlist_count": wl,
        "delivered_event_count": de,
        "review_queue_candidate_count": rq,
        "scheduler_health_report_count": sh,
        "api_mode": "READ_ONLY_DB_FUNCTIONS",
        **SAFETY_FIELDS,
    }


def list_db_watchlists():
    conn = _connect()
    c = conn.cursor()
    rows = c.execute("SELECT watchlist_id, display_name, ticker, asset_type, enabled, runtime_mode, production, retry FROM watchlists").fetchall()
    conn.close()
    return [{"watchlist_id": r[0], "display_name": r[1], "ticker": r[2], "asset_type": r[3], "enabled": bool(r[4]), "runtime_mode": r[5], "production": r[6], "retry": r[7]} for r in rows]


def get_db_watchlist(watchlist_id):
    conn = _connect()
    c = conn.cursor()
    r = c.execute("SELECT * FROM watchlists WHERE watchlist_id=?", (watchlist_id,)).fetchone()
    conn.close()
    if not r:
        return None
    return {"watchlist_id": r[1], "display_name": r[2], "ticker": r[3], "asset_type": r[4], "enabled": bool(r[7]), "production": r[11], "retry": r[12]}


def list_db_review_queue_candidates(watchlist_id=None):
    conn = _connect()
    c = conn.cursor()
    if watchlist_id:
        rows = c.execute("SELECT event_id, rank, event_type, score, priority, already_delivered, send_authorized, review_status FROM review_queue_candidates WHERE watchlist_id=?", (watchlist_id,)).fetchall()
    else:
        rows = c.execute("SELECT event_id, rank, event_type, score, priority, already_delivered, send_authorized, review_status FROM review_queue_candidates").fetchall()
    conn.close()
    return [{"event_id": r[0], "rank": r[1], "event_type": r[2], "score": r[3], "priority": r[4], "delivered": bool(r[5]), "send_authorized": bool(r[6]), "status": r[7]} for r in rows]


def list_db_delivered_events(watchlist_id=None):
    conn = _connect()
    c = conn.cursor()
    if watchlist_id:
        rows = c.execute("SELECT event_id, event_type, score, priority, delivered_at, delivery_channel FROM delivered_events WHERE watchlist_id=?", (watchlist_id,)).fetchall()
    else:
        rows = c.execute("SELECT event_id, event_type, score, priority, delivered_at, delivery_channel FROM delivered_events").fetchall()
    conn.close()
    return [{"event_id": r[0], "event_type": r[1], "score": r[2], "priority": r[3], "delivered_at": r[4], "channel": r[5]} for r in rows]


def get_db_scheduler_health_latest():
    conn = _connect()
    c = conn.cursor()
    r = c.execute("SELECT task_name, health_status, last_run_time, last_result, latest_dry_run_status, dry_run_age_minutes FROM scheduler_health_reports ORDER BY id DESC LIMIT 1").fetchone()
    conn.close()
    if not r:
        return None
    return {"task_name": r[0], "health_status": r[1], "last_run_time": r[2], "last_result": r[3], "latest_dry_run_status": r[4], "dry_run_age_minutes": r[5], **SAFETY_FIELDS}


def get_db_daily_health_latest():
    conn = _connect()
    c = conn.cursor()
    r = c.execute("SELECT summary_date, task_name, health_status, last_result, latest_dry_run_status, history_count FROM daily_health_summaries ORDER BY id DESC LIMIT 1").fetchone()
    conn.close()
    if not r:
        return None
    return {"summary_date": r[0], "task_name": r[1], "health_status": r[2], "last_result": r[3], "latest_dry_run_status": r[4], "history_count": r[5], **SAFETY_FIELDS}


def get_db_local_alert_latest():
    conn = _connect()
    c = conn.cursor()
    r = c.execute("SELECT task_name, health_status, alert_required, alert_level, enterprise_wechat_alert_sent, webhook_alert_sent FROM local_alert_reports ORDER BY id DESC LIMIT 1").fetchone()
    conn.close()
    if not r:
        return None
    return {"task_name": r[0], "health_status": r[1], "alert_required": bool(r[2]), "alert_level": r[3], "enterprise_wechat_alert_sent": bool(r[4]), "webhook_alert_sent": bool(r[5]), **SAFETY_FIELDS}


def get_db_import_status():
    conn = _connect()
    c = conn.cursor()
    stats = {}
    for t in ["watchlists","delivered_events","review_queue_candidates","dry_run_reports","scheduler_health_reports","daily_health_summaries","local_alert_reports","project_status_snapshots","api_snapshots","audit_log"]:
        stats[t] = c.execute(f"SELECT COUNT(*) FROM {t}").fetchone()[0]
    conn.close()
    return {"import_mode": "LOCAL_IMPORT_ONLY", "table_row_counts": stats, "total_rows": sum(stats.values()), **SAFETY_FIELDS}


def get_db_audit_log_summary():
    conn = _connect()
    c = conn.cursor()
    cnt = c.execute("SELECT COUNT(*) FROM audit_log").fetchone()[0]
    first = c.execute("SELECT action_type, created_at FROM audit_log ORDER BY id ASC LIMIT 1").fetchone()
    last = c.execute("SELECT action_type, created_at FROM audit_log ORDER BY id DESC LIMIT 1").fetchone()
    conn.close()
    return {"entry_count": cnt, "first_entry_type": first[0] if first else None, "first_entry_at": first[1] if first else None, "last_entry_type": last[0] if last else None, "last_entry_at": last[1] if last else None}


def build_all_db_snapshots():
    return {
        "api_mode": "READ_ONLY_DB_FUNCTIONS",
        "http_server_started": False,
        "post_endpoints_created": False,
        "project_status": get_db_project_status(),
        "watchlists": list_db_watchlists(),
        "review_queue_candidates": list_db_review_queue_candidates(),
        "delivered_events": list_db_delivered_events(),
        "scheduler_health_latest": get_db_scheduler_health_latest(),
        "daily_health_latest": get_db_daily_health_latest(),
        "local_alert_latest": get_db_local_alert_latest(),
        "import_status": get_db_import_status(),
        "audit_log_summary": get_db_audit_log_summary(),
    }
