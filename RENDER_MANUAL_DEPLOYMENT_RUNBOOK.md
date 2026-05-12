# Render Manual Deployment Runbook

## Prerequisites

- Render account
- GitHub account
- This repo bundle (`backend/output/render_deployable_repo_bundle/`)

## Steps

### Step 1: Create GitHub repository

Create a new GitHub repository (public or private).

### Step 2: Upload bundle contents

Copy all contents of `backend/output/render_deployable_repo_bundle/` into the root of the GitHub repository.

Required structure in GitHub repo:

```
render.yaml
requirements.txt
start_read_only_preview.py
env.render.example
README_RENDER_DEPLOYMENT.md
frontend/
backend/
data/
safety/
```

### Step 3: Push to GitHub

```bash
cd /path/to/your-repo
git add .
git commit -m "Cloud Read-Only Preview — Render deployable repo bundle"
git push origin main
```

### Step 4: Log into Render

Go to https://dashboard.render.com

### Step 5: Create Web Service

1. Click **New +** → **Web Service**
2. Connect your GitHub repository
3. Render auto-detects `render.yaml`
4. Verify settings:

| Setting | Value |
|---------|-------|
| Name | `trade-intel-read-only-preview` |
| Runtime | `Python` |
| Build Command | `pip install -r requirements.txt` |
| Start Command | `python start_read_only_preview.py` |
| Health Check Path | `/api/db/status` |
| Plan | Free or Starter |

### Step 6: Configure Environment Variables

Set these non-secret env vars in Render dashboard:

| Key | Value |
|-----|-------|
| APP_MODE | READ_ONLY_PREVIEW |
| PROJECT_STATE | RUNTIME_HOLD |
| PRODUCTION | DISABLED |
| RETRY | DISABLED |
| AUTO_SEND_ENABLED | false |
| REAL_SEND | NOT_RUN |
| WEBHOOK_CALL | NOT_RUN |

Do NOT configure:
- Any webhook URL
- Any API key
- Any secret/token
- Any send authorization

### Step 7: Deploy

Click **Deploy** or Render auto-deploys on push.

### Step 8: Note Public URL

After deployment, Render provides a public URL like:
`https://trade-intel-read-only-preview.onrender.com`

### Step 9: Verify

Follow `RENDER_POST_DEPLOY_VERIFICATION.md` to verify the deployment.

## Rollback / Stop

- To stop: Render Dashboard → Service → **Suspend**
- To rollback: Deploy previous commit or redeploy local bundle

## Safety

- This runbook does NOT perform any actual deployment
- All Render service and resource creation happens only when the user follows these steps manually
