# FIXORA — Feature Documentation & UI Architectural Guide

> **Comprehensive Walkthrough of All 18 Platform Views & Key Conceptual Distinctions**  
> *Detailed component mappings, backend API endpoints, user interactions, and architectural rationales.*

---

## 1. Key Conceptual Distinctions

To understand FIXORA's user interface and functional workflows, four architectural distinctions must be understood:

### A. AutoPatch Studio vs. Code Repairs
* **AutoPatch Studio (`/autopatch`):** The *interactive workspace* where engineers inspect candidate patches, review side-by-side AST-aligned code diffs, trigger sandboxed test runs, execute human approvals, and publish GitHub Pull Requests.
* **Code Repairs (`/code-repairs`):** The *comprehensive audit log & history ledger* of all patches ever generated across the workspace. It provides historical tracking, status filters (`applied`, `validated`, `pending_review`, `rejected`), branch references, and direct navigation links back into AutoPatch Studio.

### B. Knowledge Base vs. RAG Search
* **Knowledge Base (`/knowledge-base`):** The *corpus management interface* where teams upload, manage, index, and organize documentation, architecture decision records (ADRs), runbooks, API specifications, and past postmortems.
* **RAG Search (`/rag-search`):** The *active retrieval interface* where engineers run natural language and technical queries against the combined repository ASTs and knowledge corpus, viewing reciprocal rank fusion scores, semantic distances, and highlighted source passages.

### C. Incidents vs. Investigations
* **Incidents (`/incidents`):** The *operational operational event* triggered by production telemetry (e.g. error spike, service outage, unhandled traceback). It represents the "what happened and when."
* **Investigations (`/investigations`):** The *autonomous reasoning process* launched to solve an incident or bug. An investigation encapsulates the LangGraph multi-agent execution, state transitions, hypotheses, and diagnostic findings.

### D. Bugs vs. Incidents
* **Bugs (`/bugs`):** *Code-level defects* identified via static repository AST analysis, linting, or failing unit tests in pre-deployment mode (e.g. null pointer risk, off-by-one loop, unhandled edge condition).
* **Incidents (`/incidents`):** *Runtime operational events* occurring in deployed services monitored via live telemetry streams (e.g. 500 error spikes, latency anomalies).

---

## 2. Exhaustive Walkthrough of All 18 UI Sections

```
+-----------------------------------------------------------------------------------+
|                            FIXORA NAVIGATION STRUCTURE                            |
+-----------------------------------------------------------------------------------+
| 1. Landing (/)        | 7. Incidents (/incidents)        | 13. Traces (/traces)   |
| 2. Auth (/login)      | 8. AutoPatch (/autopatch)        | 14. Docs (/knowledge)  |
| 3. Dash (/dashboard)  | 9. Repairs (/code-repairs)       | 15. RAG (/rag-search)  |
| 4. Repos (/repos)     | 10. Bugs (/bugs)                 | 16. Health (/health)   |
| 5. Repo Detail (:id)  | 11. Logs (/logs)                 | 17. Reports (/reports) |
| 6. Invs (/invests)    | 12. Metrics (/metrics)           | 18. Config (/settings) |
+-----------------------------------------------------------------------------------+
```

### 1. Landing Page (`/`)
* **Component:** `frontend/src/pages/LandingPage.tsx`
* **Purpose:** High-impact public gateway communicating FIXORA’s value proposition to new visitors, developers, and leadership.
* **Key Features:** Hero section with animated interactive terminal demo, key value propositions (MTTR reduction, closed-loop repair), architecture highlights, and clear CTAs to Login or Register.

### 2. Authentication (`/login`, `/register`)
* **Component:** `frontend/src/pages/AuthPage.tsx`
* **API Endpoints:** `POST /api/auth/token`, `POST /api/auth/register`
* **Purpose:** Secure identity management and session establishment.
* **Key Features:** Form validation, JWT issuance, encrypted password verification, error handling for duplicate registrations, and automatic redirection to `/dashboard` upon authenticated state.

### 3. Dashboard (`/dashboard`)
* **Component:** `frontend/src/pages/DashboardPage.tsx`
* **API Endpoints:** `GET /api/dashboard/stats`, `GET /api/incidents`, `GET /api/patches`
* **Purpose:** Central command center displaying live operational health, repository statuses, and real-time remediation metrics.
* **Key Features:** Real metrics computed directly from database records (Active Incidents, Autonomous Repairs, Pending Review, Repositories Connected), quick-action links to start investigations, and recent activity audit stream.

### 4. Repositories (`/repositories`)
* **Component:** `frontend/src/pages/RepositoriesPage.tsx`
* **API Endpoints:** `GET /api/repositories`, `POST /api/repositories`, `POST /api/repositories/upload-zip`, `DELETE /api/repositories/{id}`
* **Purpose:** Unified repository hub for connecting GitHub repos, uploading ZIP archives, tracking ingestion progress, and launching scans.
* **Key Features:** "Connect Repository" modal supporting Git URL and ZIP drag-and-drop, real-time ingestion status indicators (`pending`, `indexing`, `ready`), and safe repository deletion with cascading resource cleanup.

### 5. Repository Detail (`/repositories/:id`)
* **Component:** `frontend/src/pages/RepositoryDetailPage.tsx`
* **API Endpoints:** `GET /api/repositories/{id}`, `GET /api/bugs?repository_id={id}`
* **Purpose:** Deep-dive view of an individual code repository.
* **Key Features:** Source branch breakdown, AST statistics (number of indexed symbols, functions, chunks), detected bug lists, and direct trigger to run full AST vulnerability scans.

### 6. Investigations (`/investigations`)
* **Component:** `frontend/src/pages/InvestigationsPage.tsx`
* **API Endpoints:** `GET /api/investigations`, `POST /api/investigations`
* **Purpose:** Multi-agent autonomous investigation operations center.
* **Key Features:** Interactive card list of active and completed investigations, progress meters reflecting the 7 LangGraph agent stages, detailed modal with agent logs and intermediate hypotheses, and "New Investigation" launcher.

### 7. Incidents (`/incidents`)
* **Component:** `frontend/src/pages/IncidentsPage.tsx`
* **API Endpoints:** `GET /api/incidents`, `POST /api/incidents`
* **Purpose:** Live operational incident triage center.
* **Key Features:** Severity badges (`P1 - Critical`, `P2 - Major`, `P3 - Minor`), status toggles (`open`, `investigating`, `resolved`), stack trace viewer with syntax highlighting, and "Investigate" button launching LangGraph agent workflows.

### 8. AutoPatch Studio (`/autopatch`)
* **Component:** `frontend/src/pages/AutoPatchPage.tsx`
* **API Endpoints:** `GET /api/patches/{id}`, `POST /api/patches/{id}/test`, `POST /api/patches/{id}/approve`, `POST /api/patches/{id}/create-pr`
* **Purpose:** Interactive engineering studio for reviewing, verifying, and publishing autonomous code repairs.
* **Key Features:** Side-by-side and unified diff viewer (`react-diff-viewer-continued`), Docker sandbox test execution logs (`stdout`/`stderr`), "Approve Patch" human gate toggle, and "Create GitHub PR" action.

### 9. Code Repairs (`/code-repairs`)
* **Component:** `frontend/src/pages/CodeRepairsPage.tsx`
* **API Endpoints:** `GET /api/patches`
* **Purpose:** Comprehensive historical audit ledger of all generated fixes.
* **Key Features:** Filter by status (`all`, `validated`, `approved`, `pending_review`), execution time metrics, target repository attribution, and direct "Open in AutoPatch Studio" deep links.

### 10. Bug Tracker (`/bugs`)
* **Component:** `frontend/src/pages/BugsPage.tsx`
* **API Endpoints:** `GET /api/bugs`, `POST /api/bugs`, `GET /api/bugs/{id}`
* **Purpose:** Pre-deployment software defect management.
* **Key Features:** AST-detected bugs, file path and line location pointers, severity classifications, and one-click triggers to dispatch AutoPatch repair routines.

### 11. Telemetry Logs (`/logs`)
* **Component:** `frontend/src/pages/LogsPage.tsx`
* **API Endpoints:** `GET /api/telemetry/{projectId}/logs`
* **Purpose:** Live operational log ingestion stream and search.
* **Key Features:** Log level filters (`ERROR`, `WARN`, `INFO`), timestamp sorting, regex search, structured JSON log payload inspection, and honest empty states when external log shippers are inactive.

### 12. Telemetry Metrics (`/metrics`)
* **Component:** `frontend/src/pages/MetricsPage.tsx`
* **API Endpoints:** `GET /api/telemetry/{projectId}/metrics`
* **Purpose:** System performance, error rate, and throughput monitoring.
* **Key Features:** Time-series charts visualizing request latency, 5xx error spikes, CPU/memory utilization, and threshold breach indicators.

### 13. Distributed Traces (`/traces`)
* **Component:** `frontend/src/pages/TracesPage.tsx`
* **API Endpoints:** `GET /api/telemetry/{projectId}/traces`
* **Purpose:** OpenTelemetry span visualization across distributed microservices.
* **Key Features:** Waterfall timeline chart of HTTP/RPC calls, error span highlighting, duration breakdown, and span tag inspection.

### 14. Knowledge Base (`/knowledge-base`)
* **Component:** `frontend/src/pages/KnowledgeBasePage.tsx`
* **API Endpoints:** `GET /api/knowledge-base`, `POST /api/knowledge-base/upload`, `DELETE /api/knowledge-base/{id}`
* **Purpose:** Architectural and operational documentation management.
* **Key Features:** Document upload modal supporting Markdown and text files, vector indexing status indicators, document chunk count summaries, and document previewing.

### 15. RAG Search (`/rag-search`)
* **Component:** `frontend/src/pages/RAGSearchPage.tsx`
* **API Endpoints:** `POST /api/rag/search`
* **Purpose:** Semantic and lexical code/documentation search workbench.
* **Key Features:** Hybrid search query input, toggle between Vector / Lexical / Hybrid modes, relevance score indicators (RRF $k=60$), and highlighted code/document context excerpts.

### 16. Engineering Health (`/health`)
* **Component:** `frontend/src/pages/HealthPage.tsx`
* **API Endpoints:** `GET /api/health`, `GET /api/projects/{id}/health-score`
* **Purpose:** Aggregate architectural and reliability scorecard.
* **Key Features:** Composite health score (0-100), MTTR reduction metrics, test coverage tracking, code vulnerability index, and actionable system improvement recommendations.

### 17. Postmortems & Reports (`/reports`)
* **Component:** `frontend/src/pages/ReportsPage.tsx`
* **API Endpoints:** `GET /api/reports`, `GET /api/reports/{id}/export-pdf`
* **Purpose:** Executive incident documentation and compliance archiving.
* **Key Features:** Chronological incident postmortem lists, executive summary view, impact timeline, root cause breakdown, and one-click "Export PDF" generating compliant `%PDF-1.4` files.

### 18. Settings & Integrations (`/settings`)
* **Component:** `frontend/src/pages/SettingsPage.tsx`
* **API Endpoints:** `GET /api/integrations`, `POST /api/integrations/github`, `POST /api/integrations/telemetry`
* **Purpose:** Workspace configuration, credentials, and third-party connection hub.
* **Key Features:** GitHub Personal Access Token (PAT) setup, webhook URL configuration with secret generation, LLM provider selection (OpenAI, Gemini, Anthropic), and sandbox resource limit configurations.
