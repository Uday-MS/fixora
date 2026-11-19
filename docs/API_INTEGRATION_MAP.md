# FIXORA Complete API Integration Map

**Date:** 2026-11-19  
**Platform Version:** FIXORA v1.0.0-rc2  

---

## 1. Complete Route Mapping (Frontend to Backend to Database)

| Frontend View | Route | Service Invocation | HTTP Method & URL | Backend Router | Database Tables Touched | Persistence Behavior |
|---|---|---|---|---|---|---|
| **Dashboard** | `/dashboard` | `dashboardService.getStats()` | `GET /api/dashboard/stats` | `dashboard.py` | `repositories`, `bugs`, `patches`, `incidents`, `test_runs` | Aggregates live counts; computes pass rates and MTTR |
| **Dashboard** | `/dashboard` | `repositoryService.list()` | `GET /api/repositories` | `repositories.py` | `repositories` | Fetches monitored repositories list |
| **Dashboard** | `/dashboard` | `incidentService.list()` | `GET /api/incidents` | `incidents.py` | `incidents` | Queries active production incidents |
| **Connected Repos** | `/repositories` | `repositoryService.list()` | `GET /api/repositories` | `repositories.py` | `repositories` | Reads repositories ordered by `created_at DESC` |
| **Connect Repo** | (Modal) | `repositoryService.create()` | `POST /api/repositories` | `repositories.py` | `repositories`, `knowledge_documents` | Real GitHub tree fetch or manual record creation |
| **Upload ZIP** | (Modal) | `repositoryService.uploadStandaloneZip()` | `POST /api/repositories/upload-zip` | `ingestion.py` | `repositories`, `knowledge_documents` | Zip Slip safe extraction, AST language scan, Qdrant/BM25 indexing |
| **Sync Repo** | `/repositories` | `repositoryService.sync()` | `POST /api/repositories/{id}/sync` | `repositories.py` | `repositories` | Synchronizes latest git commits and trees |
| **Delete Repo** | `/repositories` | `repositoryService.delete()` | `DELETE /api/repositories/{id}` | `repositories.py` | `repositories`, `bugs`, `patches`, `test_runs`, `knowledge_documents` | Cascading delete of repo and all linked artifacts |
| **Repo Detail** | `/repositories/:id` | `repositoryService.get()`, `getFiles()` | `GET /api/repositories/{id}`, `GET /api/repositories/{id}/files` | `repositories.py` | `repositories` | Returns repository metadata and structured AST file tree |
| **Issues & Bugs** | `/bugs` | `bugService.list()` | `GET /api/bugs` | `bugs.py` | `bugs` | Queries AST defect findings |
| **Incident Intel** | `/incidents` | `incidentService.list()` | `GET /api/incidents` | `incidents.py` | `incidents` | Queries active & resolved incident alerts |
| **Resolve Incident**| `/incidents` | `incidentService.resolve()` | `POST /api/incidents/{id}/resolve` | `incidents.py` | `incidents` | Sets `status = 'resolved'`, records `resolved_at` |
| **Investigate Inc.**| `/incidents` | `investigationService.create()` | `POST /api/investigations` | `investigations.py` | `investigations`, `bugs`, `patches`, `test_runs` | Executes 7-agent LangGraph lifecycle for the incident |
| **Investigations** | `/investigations` | `investigationService.list()` | `GET /api/investigations` | `investigations.py` | `investigations` | Lists multi-agent investigation sessions |
| **Launch AI Inv.** | `/investigations` | `investigationService.create()` | `POST /api/investigations` | `investigations.py` | `investigations`, `bugs`, `patches`, `test_runs` | Spawns LangGraph pipeline targeting specified repository |
| **Inv. Detail** | `/investigations/:id`| `investigationService.get()` | `GET /api/investigations/{id}` | `investigations.py` | `investigations` | Retrieves stage waterfall, evidence, and root-cause |
| **Code Repairs** | `/code-repairs` | `patchService.list()` | `GET /api/patches` | `patches.py` | `patches` | Lists audit trail of synthesized code repairs |
| **AutoPatch Studio**| `/autopatch` | `patchService.list()`, `get()` | `GET /api/patches`, `GET /api/patches/{id}` | `patches.py` | `patches` | Retrieves patch unified diff and explanation |
| **Run Tests** | `/autopatch` | `patchService.runTests()` | `POST /api/patches/{id}/run-tests` | `patches.py` | `test_runs`, `patches` | Executes tests inside isolated Docker sandbox container |
| **Approve Patch** | `/autopatch` | `patchService.approve()` | `POST /api/patches/{id}/approve` | `patches.py` | `patches` | Sets `status = 'approved'` (human gate sign-off) |
| **Create PR** | `/autopatch` | `patchService.createPR()` | `POST /api/patches/{id}/create-pr` | `patches.py` | `patches` | Creates GitHub draft pull request (blocks if unapproved) |
| **Observability Logs**| `/observability/logs` | `telemetryService.getLogs()` | `GET /api/telemetry/{id}/logs` | `telemetry.py` | `telemetry_logs` | Real-time Loki log tailing with tracebacks |
| **Observability Metrics**| `/observability/metrics`| `telemetryService.getMetrics()` | `GET /api/telemetry/{id}/metrics`| `telemetry.py` | `telemetry_metrics` | Time-series metrics (P99, latency, error budget) |
| **Observability Traces**| `/observability/traces` | `telemetryService.getTraces()` | `GET /api/telemetry/{id}/traces` | `telemetry.py` | `telemetry_traces` | Distributed spans waterfall |
| **Knowledge Base** | `/knowledge` | `knowledgeService.listDocuments()` | `GET /api/knowledge/documents` | `knowledge.py` | `knowledge_documents` | Lists indexed documents |
| **Upload Document**| `/knowledge` | `knowledgeService.uploadDocument()` | `POST /api/knowledge/upload` | `knowledge.py` | `knowledge_documents` | Extracts text (PDF/DOCX/MD) and indexes to Qdrant |
| **RAG Ask** | `/knowledge`, `/rag-search` | `knowledgeService.ask()` | `POST /api/knowledge/ask` | `knowledge.py` | `knowledge_documents`, Qdrant | Dense + BM25 hybrid retrieval with citations |
| **Engineering Health**| `/analytics/health` | `api.get('/dashboard/health')` | `GET /api/dashboard/health` | `dashboard.py` | `repositories`, `patches`, `test_runs`, `incidents` | Calculates empirical health score & sandbox pass rates |
| **Postmortems** | `/reports` | `api.get('/reports')` | `GET /api/reports` | `reports.py` | `incidents`, `investigations`, `patches` | Formatted post-incident team review reports |
| **Export PDF** | `/reports` | Direct download / `window.open` | `GET /api/reports/{id}/export-pdf` | `reports.py` | `incidents`, `investigations`, `patches` | Streams valid binary PDF (%PDF-1.4) download |
| **Integrations** | `/settings/integrations`| `api.get('/health')`, `api.get('/settings')` | `GET /api/health`, `GET /api/settings` | `main.py`, `settings.py` | System health | Probes DB, Qdrant, Docker runtime, GitHub config |
| **Settings** | `/settings` | `api.get('/settings')` | `GET /api/settings` | `settings.py` | System settings | Returns runtime limits and policies |
