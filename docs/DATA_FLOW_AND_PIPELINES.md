# FIXORA — End-to-End Data Flow & Operational Pipelines

> **Comprehensive Life-of-a-Request Documentation: Workflows A through G**  
> *Precise tracing across Frontend Components, API Endpoints, Domain Services, Database Models, and Background Tasks.*

---

## Workflow A: User Registration, Organization, Workspace & Project Setup

```
[User Browser] ──> [React Frontend] ──> [FastAPI Router] ──> [Auth Service] ──> [Database Engine]
```

### Step-by-Step Data Flow
1. **User Registration & Login:**
   - **Frontend:** User navigates to `/login` or `/register` (`AuthPage.tsx`). Submits credentials (email, password).
   - **Network Request:** `POST /api/auth/register` or `POST /api/auth/token` with payload `{ "username": "user@example.com", "password": "..." }`.
   - **API Handler:** `backend/app/api/v1/auth.py` validates inputs via Pydantic schemas, hashes password using `passlib.context.CryptContext` (bcrypt), and queries `users` table via `AuthService`.
   - **Persistence:** Creates record in `users` table (`backend/app/models/user.py`), generates standard HMAC-SHA256 signed JSON Web Token (JWT) with user ID and workspace claims, returning `{ "accessToken": "...", "tokenType": "bearer" }`.
   - **Frontend State:** Token stored in `localStorage` (`fixora_token`); `apiClient` attaches `Authorization: Bearer <token>` header to all subsequent HTTP requests.

2. **Workspace & Project Creation:**
   - **Frontend:** Upon initial login or workspace switch, user fills the Project Creation Modal (`CreateProjectModal.tsx`), specifying project name, description, and operating mode (`development` vs `deployed`).
   - **Network Request:** `POST /api/projects` with payload `{ "name": "Payment Gateway", "description": "Core checkout microservice", "mode": "deployed" }`.
   - **Backend Processing:** `backend/app/api/v1/projects.py` maps the request to `ProjectService.create_project`.
   - **Database Insertion:** Inserts record into `projects` table with foreign key `workspace_id` derived from authenticated user context.
   - **Response & Navigation:** Returns created `Project` entity (`CamelModel`), prompting React Router to set active project context in global state and redirect to `/repositories`.

---

## Workflow B: Repository Ingestion (GitHub & ZIP Pipelines)

```
[Source Code] ──> [Ingestion Service] ──> [AST Parser] ──> [Vector Embedder] ──> [Qdrant & Neo4j]
```

### Route 1: GitHub Repository Connection
1. **Submission:** User enters a GitHub URL (e.g. `https://github.com/octocat/Hello-World`) in `ConnectRepositoryModal.tsx`.
2. **Endpoint:** `POST /api/repositories` with `{ "projectId": "...", "name": "...", "gitUrl": "...", "branch": "main" }`.
3. **Execution (`backend/app/services/repository_service.py`):**
   - Creates a `Repository` record in `repositories` table with status `pending`.
   - Creates an `IngestionJob` record in `ingestion_jobs` table.
   - Spawns background worker via `asyncio.create_task(RepositoryService.process_repository(repo_id))`.
4. **Processing Pipeline:**
   - **Clone/Fetch:** Uses `git.Repo.clone_from` with shallow depth (`--depth=1`) to a temporary isolated filesystem folder (`/tmp/fixora_repos/<uuid>`).
   - **AST Walking:** Recursively walks the directory tree, ignoring `.git`, `node_modules`, `__pycache__`, and binary assets.
   - **Parsing & Chunking:** Reads source files (`.py`, `.ts`, `.js`, `.go`, `.rs`), parses top-level declarations (classes, methods, functions) using syntax parsers, and splits code into cohesive chunks (typically 200–500 tokens).
   - **Embedding:** Generates 384-dimensional dense embeddings for each code snippet via `all-MiniLM-L6-v2`.
   - **Vector Persistence:** Upserts points into Qdrant collection `fixora_code_index` tagged with payload metadata: `{ "repo_id": "...", "file_path": "...", "start_line": ..., "end_line": ... }`.
   - **Graph Persistence:** Extracts import statements and function calls, populating directed edges in Neo4j (`(:File)-[:IMPORTS]->(:File)` and `(:Function)-[:CALLS]->(:Function)`).
5. **Completion:** Updates `Repository.status = "ready"` and `IngestionJob.status = "completed"`. Frontend polls or receives completion status and displays repository statistics (file count, lines of code, AST nodes).

### Route 2: Direct ZIP Archive Upload
1. **Upload:** User drags and drops a project `.zip` file in `ConnectRepositoryModal.tsx`.
2. **Endpoint:** `POST /api/repositories/upload-zip` (`multipart/form-data`).
3. **Zip Slip Security Shield:**
   - Backend checks total file size ($\le 50$ MB).
   - Reads zip file entries using `zipfile.ZipFile`.
   - **Path Traversal Defense:** Sanitizes every entry using `os.path.abspath` and ensures destination path starts with targeted sandbox extraction directory. Any path containing `..` or absolute root prefixes raises an immediate security exception, aborting extraction.
4. **Extraction & Indexing:** Extracted into isolated workspace directory, followed by the identical AST parsing, chunking, Qdrant vectorization, and BM25 index generation outlined above.

---

## Workflow C: Knowledge Base & Hybrid RAG Retrieval

```
[Technical Docs] ──> [Chunker & Embedder] ──> [Qdrant / BM25 / Neo4j] ──> [Reciprocal Rank Fusion] ──> [Reranker]
```

### Ingestion Flow
1. **Document Upload:** User uploads architectural guidelines, runbooks, or past postmortems in `KnowledgeBasePage.tsx`.
2. **Endpoint:** `POST /api/knowledge-base/upload`.
3. **Chunking & Indexing:** Document text is divided into overlapping semantic paragraphs (500 tokens, 50 token overlap) and stored in `knowledge_documents` table. Dense vectors are generated and indexed into Qdrant collection `knowledge_base`.

### Hybrid Retrieval Flow (RAG Search / Agent Grounding)
1. **Query Execution:** Initiated via user in `RAGSearchPage.tsx` or autonomously by the LangGraph `RetrievalAgent`.
2. **Three-Way Multi-Modal Retrieval:**
   - **Dense Vector Search:** Qdrant performs Approximate Nearest Neighbor (ANN) search via cosine similarity on the embedded query vector.
   - **Lexical BM25 Search:** Okapi BM25 algorithm computes term-frequency/inverse-document-frequency keyword scores across tokenized source code and documentation chunks.
   - **Topological Graph Traversal:** Neo4j (or in-memory NetworkX) executes graph queries to identify upstream callers and downstream dependents of the suspected code node.
3. **Reciprocal Rank Fusion (RRF):**
   Dense and lexical result sets are fused into a unified ranking using the RRF formula:
   $$RRF\_Score(d) = \sum_{m \in \{dense, lexical\}} \frac{1}{60 + rank_m(d)}$$
4. **Cross-Encoder Neural Reranking:**
   The top 50 fused candidates are scored by a cross-encoder model (`ms-marco-MiniLM-L-6-v2`) that evaluates query-passage pairs simultaneously, producing the final Top-5 high-relevance context snippets injected into the LLM prompt.

---

## Workflow D: Incident Intelligence & Telemetry Ingestion

```
[Telemetry Agent / OTel] ──> [FastAPI Telemetry Endpoints] ──> [Anomaly Scrubber] ──> [Incident Store]
```

### Telemetry Intake
1. **Event Dispatch:** Live services or OTel collectors send JSON batches to:
   - `POST /api/telemetry/{projectId}/logs`
   - `POST /api/telemetry/{projectId}/metrics`
   - `POST /api/telemetry/{projectId}/traces`
2. **Traceback Extraction & Scrubbing (`TelemetryService`):**
   - Regex engines extract file names, line numbers, HTTP status codes, and exception classes (e.g. `ZeroDivisionError`, `NullPointerException`, `ConnectionRefusedError`).
   - Sensitive credentials, auth headers, and PII are stripped.
3. **Anomaly Clustering & Incident Synthesis:**
   - Incoming anomalies are hashed by `(error_type, root_file, root_line)`.
   - If an open incident with the matching signature exists in the database within a 15-minute sliding window, its `occurrence_count` is incremented.
   - If no open incident matches, a new record is created in the `incidents` table with status `open`, severity `P1` or `P2`, and triggers the asynchronous Investigation Workflow.

---

## Workflow E: Multi-Agent Investigation (7-Stage LangGraph)

```
[Incident] ──> [Triage] ──> [Retrieval] ──> [RCA] ──> [Diagnostic] ──> [AutoPatch] ──> [Validation] ──> [Postmortem]
```

### Stage-by-Stage Agent Transitions
1. **Stage 1: Triage Agent:**
   - Evaluates incident severity, parses the raw stack trace, and determines the target repository and failing service module.
2. **Stage 2: Retrieval Agent:**
   - Triggers Workflow C (Hybrid RAG), pulling indexed source code chunks, call hierarchies, and related historical postmortems from Qdrant and Neo4j.
3. **Stage 3: Root Cause Analysis (RCA) Agent:**
   - Formulates precise hypothesis explaining *why* the failure occurred. Identifies the offending commit, AST node, and logical regression.
4. **Stage 4: Diagnostic Agent:**
   - Formulates a reproducible test scenario or assertions required to verify the defect in isolation.
5. **Stage 5: AutoPatch Agent:**
   - Generates candidate source code modifications formatted strictly as unified diffs (`--- a/... +++ b/...`).
6. **Stage 6: Validation Agent:**
   - Mounts the diff and project tests into the Docker Sandbox (Workflow F). If tests fail, loops back to Stage 5 with test output feedback (up to 3 iterations).
7. **Stage 7: Postmortem Agent:**
   - Summarizes incident impact, timeline, root cause, and remediation steps into a structured report stored in the database.

---

## Workflow F: AutoPatch & Sandboxed Validation

```
[Candidate Diff] ──> [Sandbox Runner] ──> [Docker Container :15s] ──> [Human Review] ──> [GitHub PR]
```

1. **Sandbox Execution (`backend/app/services/sandbox_service.py`):**
   - Initializes an ephemeral Docker container using an isolated test image (e.g., `python:3.12-slim`).
   - Applies strict isolation flags: `network_disabled=True`, `mem_limit="2048m"`, `cpu_quota=100000` (1 core), `user="sandboxuser"` (non-root).
   - Applies the unified patch to the source code tree.
   - Executes target test command with an enforce 15-second wall-clock timeout.
2. **Outcome Logging:**
   - Captures `stdout`, `stderr`, and container exit code.
   - Inserts record into `test_runs` table linked to the `Patch`.
   - If exit code == 0, updates `Patch.status = "validated"`.
3. **Human Approval Gate:**
   - The verified patch appears in `AutoPatchPage.tsx` with side-by-side visual diff highlighting.
   - The "Create Pull Request" button is strictly disabled until an engineer clicks **"Approve Patch"**.
   - Attempting to call `POST /api/patches/{id}/create-pr` without prior approval returns HTTP 400 Bad Request.
4. **Pull Request Synthesis:**
   - Upon human approval, `PatchService` utilizes GitPython and PyGithub to create a dedicated branch (e.g., `fixora/fix-incident-402`), commits the validated changes, pushes to remote, and opens a Draft Pull Request on GitHub with a link back to the FIXORA investigation.

---

## Workflow G: Postmortem Generation & Native PDF Export

```
[Investigation Summary] ──> [Reports Service] ──> [Native PDF Engine] ──> [application/pdf Download]
```

1. **Storage:** Postmortem report data generated by Stage 7 is persisted in the database with timestamps, root-cause statements, and action items.
2. **Client Request:** In `ReportsPage.tsx`, the user views available postmortems and clicks **"Export PDF"**.
3. **Endpoint Execution:** Calls `GET /api/reports/{id}/export-pdf`.
4. **Binary PDF Generation (`backend/app/api/v1/reports.py`):**
   - Loads the postmortem record.
   - Builds a clean, compliant `%PDF-1.4` binary stream containing headers, metadata, incident timeline, root cause description, and action items.
   - Sets HTTP response headers: `Content-Type: application/pdf` and `Content-Disposition: attachment; filename="fixora-postmortem-{id}.pdf"`.
5. **Delivery:** The browser triggers a native file download, delivering a tamper-proof incident postmortem report ready for executive and compliance distribution.
