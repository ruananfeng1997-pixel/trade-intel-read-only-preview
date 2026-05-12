# Cloud Read-Only Preview — Render Deployable Repo Bundle

## Status

- **Bundle mode**: RENDER_DEPLOYABLE_REPO_BUNDLE
- **Target provider**: Render
- **Service type**: Render Web Service
- **Actual deployment**: NOT_DEPLOYED
- **Actual Render service**: NOT_CREATED
- **Actual public URL**: NOT_CREATED
- **Project state**: RUNTIME_HOLD

## Contents

| Path | Description |
|------|-------------|
| `render.yaml` | Render service definition |
| `requirements.txt` | Python dependencies (stdlib only) |
| `start_read_only_preview.py` | GET-only server entry point |
| `frontend/` | SaaS console HTML + JSON snapshot |
| `backend/` | Read-only HTTP API server + DB read-only API |
| `data/trade_intel.read_only_preview.sqlite3` | Read-only SQLite DB snapshot |
| `safety/` | Verifications, preflight reports, authorization docs |
| `env.render.example` | Render environment variable template |
| `README_RENDER_DEPLOYMENT.md` | This file |
| `RENDER_MANUAL_DEPLOYMENT_RUNBOOK.md` | Step-by-step manual deployment guide |
| `RENDER_POST_DEPLOY_VERIFICATION.md` | Post-deployment verification guide |
| `verify_render_public_preview.py` | Automated post-deployment verification script |
| `manifest.render_deployable.local.json` | Bundle manifest |

## Safety

- GET-only server (POST returns 405)
- No secrets, tokens, API keys, or webhook URLs
- Production / retry / auto-send: DISABLED
- Read-only DB snapshot (no writes)
- No webhook, no Enterprise WeChat, no source ingestion
