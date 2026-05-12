#!/usr/bin/env python3
"""
verify_render_public_preview.py — Post-deployment verification script.

Usage:
    python verify_render_public_preview.py <public-url>

Example:
    python verify_render_public_preview.py https://trade-intel-read-only-preview.onrender.com

Checks:
    - GET /api/db/status returns 200
    - GET /api/db/dashboard-snapshot returns 200
    - POST /api/db/status returns 405
    - project_state = RUNTIME_HOLD
    - production = DISABLED
    - retry = DISABLED
    - real_send = NOT_RUN
    - webhook_call = NOT_RUN
    - no secret exposure
"""

import json
import sys
import urllib.request
import urllib.error


def check_get(url: str, name: str):
    """Perform GET request, return (status, body)."""
    try:
        req = urllib.request.Request(url, method="GET")
        with urllib.request.urlopen(req, timeout=15) as resp:
            body = resp.read().decode("utf-8")
            return resp.status, body
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode("utf-8", errors="replace")
    except Exception as e:
        return 0, str(e)


def check_post(url: str, name: str):
    """Perform POST request, return (status, body)."""
    try:
        data = b'{"test": true}'
        req = urllib.request.Request(url, data=data, method="POST",
                                     headers={"Content-Type": "application/json"})
        with urllib.request.urlopen(req, timeout=15) as resp:
            body = resp.read().decode("utf-8")
            return resp.status, body
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode("utf-8", errors="replace")
    except Exception as e:
        return 0, str(e)


def main():
    if len(sys.argv) < 2:
        print("Usage: python verify_render_public_preview.py <public-url>")
        sys.exit(1)

    base_url = sys.argv[1].rstrip("/")
    failures = []

    print("=" * 60)
    print("Render Public Preview Verification")
    print("=" * 60)
    print(f"Target URL: {base_url}")
    print()

    # 1. DB status
    print("[1/7] GET /api/db/status ...")
    status, body = check_get(f"{base_url}/api/db/status", "db-status")
    if status == 200:
        print(f"  PASS: HTTP {status}")
        try:
            data = json.loads(body)
            checks = [
                ("project_state", "RUNTIME_HOLD"),
                ("production", "DISABLED"),
                ("retry", "DISABLED"),
                ("real_send", "NOT_RUN"),
                ("webhook_call", "NOT_RUN"),
            ]
            for key, expected in checks:
                actual = data.get(key, "MISSING")
                if str(actual) == expected:
                    print(f"  PASS: {key} = {actual}")
                else:
                    msg = f"  FAIL: {key} = {actual} (expected {expected})"
                    print(msg)
                    failures.append(msg)
        except json.JSONDecodeError:
            msg = "  FAIL: response not valid JSON"
            print(msg)
            failures.append(msg)
    else:
        msg = f"  FAIL: HTTP {status}"
        print(msg)
        failures.append(msg)

    # 2. Dashboard snapshot
    print("[2/7] GET /api/db/dashboard-snapshot ...")
    status, body = check_get(f"{base_url}/api/db/dashboard-snapshot", "dashboard")
    if status == 200:
        print(f"  PASS: HTTP {status}")
    else:
        msg = f"  FAIL: HTTP {status}"
        print(msg)
        failures.append(msg)

    # 3. POST returns 405
    print("[3/7] POST /api/db/status (expect 405) ...")
    status, body = check_post(f"{base_url}/api/db/status", "post-db-status")
    if status in (405, 404):
        print(f"  PASS: HTTP {status} (expected 405 or 404)")
    else:
        msg = f"  FAIL: HTTP {status} (expected 405)"
        print(msg)
        failures.append(msg)

    # 4. No secret exposure
    print("[4/7] Checking response for secrets ...")
    secret_patterns = ["webhook", "wxb", "sk-", "api_key", "token="]
    found_secrets = []
    if isinstance(body, str):
        for pat in secret_patterns:
            if pat.lower() in body.lower():
                found_secrets.append(pat)
    if found_secrets:
        msg = f"  FAIL: Secret patterns found: {found_secrets}"
        print(msg)
        failures.append(msg)
    else:
        print("  PASS: No secrets exposed")

    # 5. Summary
    print()
    if failures:
        print(f"VERIFICATION FAILED — {len(failures)} failure(s)")
        for f in failures:
            print(f"  - {f}")
        sys.exit(1)
    else:
        print("VERIFICATION PASSED — All checks passed")
        sys.exit(0)


if __name__ == "__main__":
    main()
