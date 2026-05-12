# Render Post-Deployment Verification

After deployment, verify the following:

## 1. Health Check

```bash
curl https://<your-render-service>.onrender.com/api/db/status
```

Expected: HTTP 200, JSON body with `project_state = "RUNTIME_HOLD"`

## 2. Dashboard Snapshot

```bash
curl https://<your-render-service>.onrender.com/api/db/dashboard-snapshot
```

Expected: HTTP 200, JSON dashboard data

## 3. All GET Endpoints

Verify all 11 GET endpoints return HTTP 200.

## 4. POST Returns 405

```bash
curl -X POST https://<your-render-service>.onrender.com/api/db/status
```

Expected: HTTP 405 Method Not Allowed

## 5. Safety Variable Verification

Via the DB status endpoint, verify:

```json
{
  "project_state": "RUNTIME_HOLD",
  "real_send": "NOT_RUN",
  "webhook_call": "NOT_RUN",
  "production": "DISABLED",
  "retry": "DISABLED",
  "auto_send_enabled": false
}
```

## 6. No Secret Exposure

Check response bodies do NOT contain:
- webhook URLs
- API keys
- tokens
- secrets

## 7. Automated Verification

An automated verification script is included:

```bash
cd backend/output/render_deployable_repo_bundle/
python verify_render_public_preview.py <public-url>
```
