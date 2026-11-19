# FIXORA — Complete Render Production Deployment Runbook

> **Step-by-step manual execution checklist for deploying FIXORA (Frontend, Backend, and PostgreSQL) on Render.**

This runbook guides you through deploying FIXORA to production using Render's Infrastructure-as-Code Blueprint (`render.yaml`) or via the manual Render Dashboard.

---

## Pre-Deployment Summary

| Component | Render Resource Type | Plan | Estimated Cost |
| :--- | :--- | :--- | :--- |
| **Backend API (`fixora-api`)** | Web Service (Python 3.12 / FastAPI) | Free or Starter | $0/mo (Free) or $7/mo (Starter - Always On) |
| **Frontend UI (`fixora-ui`)** | Static Site (React 19 / Vite) | Free | $0/mo (Global CDN, Free SSL) |
| **Database (`fixora-postgres`)** | Managed PostgreSQL 16 | Free or Starter | $0/mo (Free, 30 days) or $7/mo (Starter - Persistent) |
| **Vector DB (Qdrant)** | Qdrant Cloud or In-Memory fallback | Free Tier | $0/mo (cloud.qdrant.io) |

---

## Deployment Option A: 1-Click Render Blueprint (Recommended)

Render provides automated Blueprint provisioning via the `render.yaml` file located in the root of your GitHub repository.

### Step 1: Push Code to GitHub
Ensure the latest commits (including `render.yaml`) are on your `main` branch:
- **Repository:** `https://github.com/Uday-MS/fixora.git`
- **Branch:** `main`

### Step 2: Access Render Dashboard
1. Open your browser and navigate to: **[https://dashboard.render.com](https://dashboard.render.com)**.
2. Sign in with your GitHub account (**`Uday-MS`**).

### Step 3: Launch New Blueprint Instance
1. In the top-right corner of the Render Dashboard, click the **New +** button.
2. Select **Blueprint** from the dropdown menu.
3. If prompted, connect your GitHub account or grant Render access to the repository: **`Uday-MS/fixora`**.
4. Select the **`fixora`** repository.
5. In the **Branch** field, ensure **`main`** is selected.
6. Render will automatically read `render.yaml` and show the 3 resources to be provisioned:
   - `fixora-api` (Python Web Service)
   - `fixora-ui` (Static Site)
   - `fixora-postgres` (PostgreSQL Database)
7. Click **Apply**.

---

## Deployment Option B: Manual Service Creation (Step-by-Step)

If you prefer to configure each service manually in the Render Dashboard, follow these steps:

### Step 1: Provision Managed PostgreSQL Database
1. Navigate to: **[https://dashboard.render.com](https://dashboard.render.com)**
2. Click **New +** → **PostgreSQL**.
3. Fill in the following fields:
   - **Name:** `fixora-postgres`
   - **Database:** `fixora`
   - **User:** `fixora`
   - **Region:** `Oregon (US West)` *(keep all services in the same region for lowest latency)*
   - **PostgreSQL Version:** `16`
   - **Plan:** Select **Free** (for testing) or **Starter** ($7/mo for permanent persistence).
4. Click **Create Database**.
5. Once provisioned, locate the **Connections** section on the database page:
   - Copy the **Internal Database URL** (e.g., `postgresql://fixora:password@dpg-xxx-a/fixora`).
   - *Note: This URL will be used as `DATABASE_URL` in the backend service.*

---

### Step 2: Provision Backend Web Service (`fixora-api`)
1. Click **New +** → **Web Service**.
2. Select your repository: **`Uday-MS/fixora`**.
3. Configure the service settings:
   - **Name:** `fixora-api`
   - **Region:** `Oregon (US West)` *(must match PostgreSQL region)*
   - **Branch:** `main`
   - **Root Directory:** `backend`
   - **Runtime:** `Python`
   - **Build Command:**
     ```bash
     pip install --upgrade pip && pip install -r requirements.txt
     ```
   - **Start Command:**
     ```bash
     alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port $PORT
     ```
   - **Plan:** Select **Free** or **Starter**.
4. Scroll down and expand **Advanced**:
   - **Health Check Path:** `/api/health`
   - **Auto-Deploy:** `Yes`
5. In the **Environment Variables** section, add the following key-value pairs:

| Key | Value / Source | Secret? |
| :--- | :--- | :--- |
| `PYTHON_VERSION` | `3.12.0` | No |
| `ENVIRONMENT` | `production` | No |
| `DATABASE_URL` | Paste the **Internal Database URL** from Step 1 | **Yes** |
| `JWT_SECRET` | Click **Generate** (minimum 32 random characters required) | **Yes** |
| `ALGORITHM` | `HS256` | No |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | `1440` | No |
| `REFRESH_TOKEN_EXPIRE_DAYS` | `7` | No |
| `CORS_ORIGINS` | `https://fixora-ui.onrender.com` | No |
| `FRONTEND_URL` | `https://fixora-ui.onrender.com` | No |
| `ADMIN_EMAIL` | Platform administrator email for secure initial bootstrap | No |
| `ADMIN_PASSWORD` | Platform administrator password for secure initial bootstrap (min 12 chars) | **Yes** |
| `GITHUB_TOKEN` | Enter your Personal Access Token (`ghp_...`) | **Yes** |
| `GITHUB_WEBHOOK_SECRET` | Click **Generate** (used to verify HMAC signatures) | **Yes** |
| `GEMINI_API_KEY` | Enter your Google Gemini API key (`AIza...`) | **Yes** |
| `GEMINI_MODEL` | `gemini-flash-latest` | No |
| `OPENAI_API_KEY` | Enter your OpenAI API key (`sk-...`) *(optional)* | **Yes** |
| `OPENAI_MODEL` | `gpt-4o-mini` | No |
| `QDRANT_URL` | *(Optional)* Remote Qdrant URL (falls back to in-memory) | No |
| `QDRANT_API_KEY` | *(Optional)* Remote Qdrant API Key | **Yes** |
| `REDIS_URL` | *(Optional)* Redis connection string (optional) | No |
| `NEO4J_URI` | *(Optional)* Remote Neo4j connection URI (falls back to in-memory topology) | No |
| `NEO4J_USER` | *(Optional)* Remote Neo4j username | No |
| `NEO4J_PASSWORD` | *(Optional)* Remote Neo4j password | **Yes** |
| `SANDBOX_WORKER_URL` | *(Optional)* Dedicated containerized test runner URL | No |
| `SANDBOX_WORKER_TOKEN` | *(Optional)* Bearer token for dedicated sandbox worker | **Yes** |

6. Click **Create Web Service**.
7. Wait for the build to finish. Once deployed, note down your backend public URL (e.g. `https://fixora-api.onrender.com`).

---

### Step 3: Provision Frontend Static Site (`fixora-ui`)
1. Click **New +** → **Static Site**.
2. Select your repository: **`Uday-MS/fixora`**.
3. Configure the static site settings:
   - **Name:** `fixora-ui`
   - **Branch:** `main`
   - **Root Directory:** `frontend`
   - **Build Command:**
     ```bash
     npm install && npm run build
     ```
   - **Publish Directory:** `dist`
4. Expand **Advanced**:
   - Scroll to **Redirects / Rewrites** and click **Add Rule**:
     - **Type:** `Rewrite`
     - **Source:** `/*`
     - **Destination:** `/index.html`
     - *(This is required for client-side React Router navigation so refreshing routes like `/autopatch` works cleanly).*
5. In the **Environment Variables** section, add:
   - **Key:** `VITE_API_URL`
   - **Value:** `https://fixora-api.onrender.com/api` *(replace with your actual backend URL from Step 2, appending `/api`)*
6. Click **Create Static Site**.
7. Wait for the build to finish. Once deployed, note down your frontend URL (e.g. `https://fixora-ui.onrender.com`).

---

### Step 4: Update CORS & Webhook Settings (Post-Creation)
1. Go to **Render Dashboard** → **`fixora-api`** → **Environment**.
2. Update `CORS_ORIGINS` to include your new frontend domain:
   - **Key:** `CORS_ORIGINS`
   - **Value:** `https://fixora-ui.onrender.com,http://localhost:5173`
3. Click **Save Changes** (Render will trigger a zero-downtime redeploy).

---

## External Provider Configurations

### A. GitHub Webhook Setup (Optional for Live Telemetry)
If you want GitHub push and issue events to trigger automated ingestion:
1. Open your repository on GitHub: `https://github.com/Uday-MS/fixora/settings/hooks`.
2. Click **Add webhook**.
3. **Payload URL:** `https://fixora-api.onrender.com/api/webhooks/github`
4. **Content type:** `application/json`
5. **Secret:** Paste the exact value configured in `GITHUB_WEBHOOK_SECRET`.
6. **Which events?** Select *Send me everything* or check *Pushes*, *Pull requests*, *Issues*.
7. Click **Add webhook**.

### B. Qdrant Cloud Setup (Optional for Distributed Vector Search)
By default, FIXORA automatically runs with an in-memory vector store fallback. If you want a persistent cloud vector database:
1. Visit: **[https://cloud.qdrant.io](https://cloud.qdrant.io)**
2. Create a free 1GB cluster.
3. Copy the Cluster URL and API Key.
4. In Render Dashboard → `fixora-api` → Environment:
   - `QDRANT_URL`: `https://xxx.qdrant.tech:6333`
   - `QDRANT_API_KEY`: `your_qdrant_api_key`
5. Save changes.

---

## Verification & Sanity Checks

Once deployed, verify your production installation by performing these checks:

### 1. Backend Health Check
Open in your browser:
```
https://fixora-api.onrender.com/api/health
```
**Expected Response:**
```json
{
  "status": "online",
  "service": "FIXORA Core API",
  "version": "1.0.0",
  "database": "connected",
  "sandbox_status": "blocked_by_configuration",
  "sandbox_runtime": "Container isolation unavailable on web service host"
}
```
*(Note: If a Docker daemon or `SANDBOX_WORKER_URL` is configured, `sandbox_status` will report `"ready"` and `sandbox_runtime` will report the isolated container environment).*

### 2. Live Configuration Diagnostics (Admin Only)
Endpoint:
```
https://fixora-api.onrender.com/api/settings/validate
```
*Note: This endpoint is protected by `require_admin` authorization. Pass your administrator JWT in the `Authorization: Bearer <token>` header, or inspect diagnostics directly in the Frontend Settings page as an administrator.*

**Expected Result:**
- `database.connected`: `true`
- `jwtAuthentication.status`: `Configured and verified`
- `github.status`: `Configured and connectivity tested` (Authenticated as `@Uday-MS`)
- `sandbox.isolated`: `false` (or `true` if external sandbox worker configured)

### 3. Frontend Application Check
1. Open your frontend URL: `https://fixora-ui.onrender.com`.
2. Authenticate into the platform:
   - Sign in using your `ADMIN_EMAIL` and `ADMIN_PASSWORD` configured during Step 2.
   - *Security Note: Public registrations are strictly restricted to standard `user` accounts to eliminate privilege-escalation risks.*
3. Verify that the Dashboard loads cleanly without errors.
4. Navigate to **Repositories** and verify that your connected GitHub repositories appear.
5. Open **AutoPatch Studio** (`/autopatch`) and verify that issues load directly from GitHub.

---

## Troubleshooting Guide

| Issue | Cause | Fix |
| :--- | :--- | :--- |
| **Backend 502 / Bad Gateway** | FastAPI crashed on startup | Check Render runtime logs under `fixora-api` → **Logs**. Ensure `DATABASE_URL` uses the Internal Connection URL and `requirements.txt` installed cleanly. Verify `JWT_SECRET` has at least 32 characters in production. |
| **Frontend 404 on page refresh** | Missing SPA rewrite rule | Go to `fixora-ui` → **Redirects / Rewrites** → Ensure rule `/* -> /index.html (Rewrite)` is present. |
| **CORS Error in Browser** | `CORS_ORIGINS` mismatch | Ensure `CORS_ORIGINS` on `fixora-api` is set to `https://fixora-ui.onrender.com`. |
| **Database connection error** | PostgreSQL SSL mode parameter | FIXORA automatically converts `sslmode=require` to `ssl=require` for asyncpg. Ensure the connection string from Render is pasted completely. |
| **Cold Starts (Free tier)** | Render Free web services spin down after 15 min | Upgrade `fixora-api` to the **Starter** plan ($7/mo) for 24/7 uptime and 0ms cold starts. |
