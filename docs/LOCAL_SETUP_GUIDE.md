# FIXORA — Local Setup, Installation & Configuration Guide

> **Developer Onboarding, Environment Configuration & Turnkey Local Runbook**  
> *Everything required to run FIXORA from zero dependencies to full full-stack execution.*

---

## 1. Prerequisites & System Requirements

Before running FIXORA, ensure your workstation meets the following minimum prerequisites:
* **Operating System:** macOS (Apple Silicon or Intel), Linux (Ubuntu 22.04+), or Windows (via WSL2).
* **Python:** Version `3.12.x` (Recommended: install via `pyenv` or `asdf`).
* **Node.js:** Version `20.x` or higher (LTS recommended) + `npm 10.x`.
* **Git:** Version `2.40+`.
* **Docker Engine (Optional for initial demo, Required for live sandbox execution):** Docker Desktop or OrbStack.

---

## 2. Step-by-Step Installation Runbook

```
+-----------------------------------------------------------------------------------+
|                            TURNKEY QUICK-START WORKFLOW                           |
+-----------------------------------------------------------------------------------+
| 1. Clone & Enter Repository                                                       |
| 2. Backend Environment Setup (Python 3.12 virtualenv + pip install)               |
| 3. Environment Variables (.env) Configuration                                     |
| 4. Frontend Installation (npm install)                                            |
| 5. Launch Backend Server (Uvicorn :8000)                                          |
| 6. Launch Frontend Dev Server (Vite :5173)                                        |
+-----------------------------------------------------------------------------------+
```

### Step 1: Navigate to Workspace Root
```bash
cd /Users/udayms/NEW/FIXORA
```

### Step 2: Backend Setup
```bash
# Create Python 3.12 virtual environment
python3 -m venv backend/venv

# Activate virtual environment
source backend/venv/bin/activate

# Upgrade pip and install all backend dependencies
pip install --upgrade pip
pip install -e backend
```

### Step 3: Configure Environment Variables
Copy the template configuration:
```bash
cp .env.example .env
```
*(By default, `.env` is configured for instant zero-dependency SQLite and in-memory vector mode, requiring no external databases to boot immediately).*

### Step 4: Frontend Setup
```bash
# Navigate to frontend directory and install dependencies
cd frontend
npm install
cd ..
```

### Step 5: Start the Backend Server
```bash
PYTHONPATH=backend backend/venv/bin/uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```
The FastAPI REST documentation will now be available at:  
👉 **`http://127.0.0.1:8000/docs`**

### Step 6: Start the Frontend Application
Open a second terminal window and run:
```bash
npm --prefix frontend run dev
```
The FIXORA web application will be live at:  
👉 **`http://localhost:5173`**

---

## 3. Environment Variable Reference (`.env.example`)

| Variable Name | Default Value | Description & Options |
| :--- | :--- | :--- |
| `DATABASE_URL` | `sqlite+aiosqlite:///./fixora.db` | Primary database connection string. For PostgreSQL, set `postgresql+asyncpg://postgres:postgres@localhost:5432/fixora`. |
| `SECRET_KEY` | `dev-secret-key-32-chars-long-example` | Cryptographic secret for signing user JWT tokens (HMAC-SHA256). |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | `60` | Duration before user login token expires. |
| `QDRANT_URL` | `http://localhost:6333` | URL for Qdrant vector database. If unreachable, the platform automatically activates in-memory vector mode. |
| `NEO4J_URI` | `bolt://localhost:7687` | URI for Neo4j Graph database. If unreachable, platform uses in-memory NetworkX graphs. |
| `NEO4J_USER` / `NEO4J_PASSWORD` | `neo4j` / `password` | Credentials for the Neo4j instance. |
| `REDIS_URL` | `redis://localhost:6379/0` | Redis caching and broker connection. |
| `GITHUB_TOKEN` | *Empty / Optional* | Personal Access Token (`ghp_...`). Allows cloning private repos and opening real pull requests. |
| `OPENAI_API_KEY` | *Empty / Optional* | API key for OpenAI LLM provider (GPT-4o). Heuristic fallback engages if unset. |
| `ANTHROPIC_API_KEY` | *Empty / Optional* | API key for Anthropic Claude 3.5 Sonnet. |
| `GEMINI_API_KEY` | *Empty / Optional* | API key for Google Gemini 1.5 Pro. |
| `SANDBOX_DOCKER_IMAGE` | `python:3.12-slim` | Base container image used to execute candidate regression tests. |

---

## 4. Optional Enterprise Infrastructure (Docker Compose)

If you wish to run the full enterprise storage tier (PostgreSQL, Qdrant, Neo4j, and Redis) locally via containers:

```bash
docker compose up -d postgres qdrant neo4j redis
```

Once running, update your `.env` with:
```bash
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/fixora
QDRANT_URL=http://localhost:6333
NEO4J_URI=bolt://localhost:7687
REDIS_URL=redis://localhost:6379/0
```

---

## 5. Running Automated Verification Suites

### Run Backend Pytest Suite
```bash
PYTHONPATH=backend backend/venv/bin/pytest backend/tests -v
```
*(Executes all 39 tests against isolated `test_fixora.db`).*

### Run Frontend Production Build & TypeScript Verification
```bash
npm --prefix frontend run build
```
*(Verifies 0 TypeScript type errors and outputs production distribution bundle).*

---

## 6. Troubleshooting Common Issues

### Issue 1: `connect EPERM 127.0.0.1:8000` on Frontend
* **Cause:** Running inside strict local sandboxes or macOS socket permission locks.
* **Fix:** Ensure backend server is bound to loopback `127.0.0.1` and verify port 8000 is open.

### Issue 2: Port 8000 or 5173 Already in Use
* **Cause:** Lingering background processes from prior sessions.
* **Fix:** Kill previous processes occupying the ports:
  ```bash
  lsof -ti:8000 | xargs kill -9
  lsof -ti:5173 | xargs kill -9
  ```
