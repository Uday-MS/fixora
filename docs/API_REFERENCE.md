# FIXORA — Comprehensive API Reference & Endpoint Catalog

> **RESTful API Specifications, Authentication Schemes & Frontend-to-Backend Mappings**  
> *Every endpoint documented with HTTP method, parameters, request/response models, and caller bindings.*

---

## 1. Authentication & Security Schemes

The FIXORA API uses JSON Web Tokens (JWT) signed with HMAC-SHA256:
* **Header:** `Authorization: Bearer <access_token>`
* **Token Expiration:** 60 minutes
* **Payload Claims:** `{ "sub": "<user_id>", "email": "...", "workspace_id": "...", "role": "admin" }`
* **Data Conventions:** All responses adhere to `CamelModel` serialization—JSON keys are serialized in `camelCase`, while Python services operate internally with `snake_case`.

---

## 2. Exhaustive API Endpoint Catalog

### Authentication Endpoints (`backend/app/api/v1/auth.py`)

| Method | Endpoint | Auth | Purpose | Request Body | Response (Status & Schema) | Frontend Caller |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `POST` | `/api/auth/register` | Public | Register new user | `{ email, password, fullName }` | `201 Created`: `{ id, email, fullName, role }` | `authService.register` |
| `POST` | `/api/auth/token` | Public | OAuth2 password login | Form: `username`, `password` | `200 OK`: `{ accessToken, tokenType }` | `authService.login` |
| `GET` | `/api/auth/me` | Bearer | Get current user context | None | `200 OK`: `UserResponse` | `authService.getCurrentUser` |

---

### Dashboard Endpoints (`backend/app/api/v1/dashboard.py`)

| Method | Endpoint | Auth | Purpose | Query Params | Response (Status & Schema) | Frontend Caller |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `GET` | `/api/dashboard/stats` | Bearer | Fetch live workspace KPIs | `workspace_id` (optional) | `200 OK`: `{ activeIncidents, autonomousRepairs, pendingReview, repositoriesConnected, mttrMinutes, healthScore }` | `dashboardService.getStats` |

---

### Repository Endpoints (`backend/app/api/v1/repositories.py`)

| Method | Endpoint | Auth | Purpose | Request / Query | Response (Status & Schema) | Frontend Caller |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `GET` | `/api/repositories` | Bearer | List repositories | Query: `projectId` | `200 OK`: `List[RepositoryResponse]` | `repoService.list` |
| `POST` | `/api/repositories` | Bearer | Connect GitHub repo | `{ projectId, name, gitUrl, branch }` | `201 Created`: `RepositoryResponse` | `repoService.connectGithub` |
| `POST` | `/api/repositories/upload-zip` | Bearer | Upload repo ZIP | `multipart/form-data`: `file`, `projectId` | `201 Created`: `RepositoryResponse` | `repoService.uploadZip` |
| `GET` | `/api/repositories/{id}` | Bearer | Get repository detail | Path: `id` | `200 OK`: `RepositoryDetailResponse` | `repoService.getById` |
| `DELETE` | `/api/repositories/{id}` | Bearer | Delete repository & cascade | Path: `id` | `200 OK`: `{ status: "deleted", id }` | `repoService.delete` |
| `GET` | `/api/repositories/{id}/jobs` | Bearer | Get ingestion job status | Path: `id` | `200 OK`: `IngestionJobResponse` | `repoService.getJobStatus` |

---

### Incident Endpoints (`backend/app/api/v1/incidents.py`)

| Method | Endpoint | Auth | Purpose | Request / Query | Response (Status & Schema) | Frontend Caller |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `GET` | `/api/incidents` | Bearer | List incidents | Query: `projectId`, `status` | `200 OK`: `List[IncidentResponse]` | `incidentService.list` |
| `POST` | `/api/incidents` | Bearer | Create operational incident | `{ projectId, title, description, severity, errorSignature }` | `201 Created`: `IncidentResponse` | `incidentService.create` |
| `GET` | `/api/incidents/{id}` | Bearer | Get incident details | Path: `id` | `200 OK`: `IncidentDetailResponse` | `incidentService.getById` |
| `PATCH` | `/api/incidents/{id}/status` | Bearer | Update incident status | `{ status: "investigating" \| "resolved" }` | `200 OK`: `IncidentResponse` | `incidentService.updateStatus` |

---

### Investigation Endpoints (`backend/app/api/v1/investigations.py`)

| Method | Endpoint | Auth | Purpose | Request / Query | Response (Status & Schema) | Frontend Caller |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `GET` | `/api/investigations` | Bearer | List investigations | Query: `projectId`, `incidentId` | `200 OK`: `List[InvestigationResponse]` | `investigationService.list` |
| `POST` | `/api/investigations` | Bearer | Trigger LangGraph run | `{ incidentId, bugId, repositoryId }` | `201 Created`: `InvestigationResponse` | `investigationService.trigger` |
| `GET` | `/api/investigations/{id}` | Bearer | Get investigation progress | Path: `id` | `200 OK`: `InvestigationDetailResponse` (includes agent stages & logs) | `investigationService.getById` |

---

### Bug & Vulnerability Endpoints (`backend/app/api/v1/bugs.py`)

| Method | Endpoint | Auth | Purpose | Request / Query | Response (Status & Schema) | Frontend Caller |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `GET` | `/api/bugs` | Bearer | List detected bugs | Query: `repositoryId`, `severity` | `200 OK`: `List[BugResponse]` | `bugService.list` |
| `POST` | `/api/bugs` | Bearer | Manually report bug | `{ repositoryId, title, description, severity, filePath, lineNumber }` | `201 Created`: `BugResponse` | `bugService.create` |
| `GET` | `/api/bugs/{id}` | Bearer | Get bug details | Path: `id` | `200 OK`: `BugDetailResponse` | `bugService.getById` |

---

### AutoPatch & Code Repair Endpoints (`backend/app/api/v1/patches.py`)

| Method | Endpoint | Auth | Purpose | Request / Query | Response (Status & Schema) | Frontend Caller |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `GET` | `/api/patches` | Bearer | List all repairs | Query: `investigationId`, `status` | `200 OK`: `List[PatchResponse]` | `patchService.list` |
| `GET` | `/api/patches/{id}` | Bearer | Get patch & diff detail | Path: `id` | `200 OK`: `PatchDetailResponse` | `patchService.getById` |
| `POST` | `/api/patches/{id}/test` | Bearer | Run sandbox test validation | Path: `id` | `200 OK`: `TestRunResponse` (`status`, `stdout`, `exitCode`) | `patchService.runTest` |
| `POST` | `/api/patches/{id}/approve` | Bearer | Human approval gate | Path: `id` | `200 OK`: `{ status: "approved", humanApproved: true }` | `patchService.approve` |
| `POST` | `/api/patches/{id}/create-pr`| Bearer | Publish GitHub Draft PR | Path: `id` | `200 OK`: `{ pullRequestUrl: "...", branchName: "..." }` | `patchService.createPR` |

---

### Knowledge Base & RAG Endpoints (`backend/app/api/v1/rag.py` & `knowledge.py`)

| Method | Endpoint | Auth | Purpose | Request / Query | Response (Status & Schema) | Frontend Caller |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `GET` | `/api/knowledge-base` | Bearer | List indexed docs | Query: `projectId` | `200 OK`: `List[KnowledgeDocResponse]` | `knowledgeService.list` |
| `POST` | `/api/knowledge-base/upload`| Bearer | Ingest Markdown/spec doc | `multipart/form-data`: `file`, `docType` | `201 Created`: `KnowledgeDocResponse` | `knowledgeService.upload` |
| `DELETE`| `/api/knowledge-base/{id}` | Bearer | Delete document | Path: `id` | `200 OK`: `{ status: "deleted" }` | `knowledgeService.delete` |
| `POST` | `/api/rag/search` | Bearer | Execute hybrid retrieval | `{ query, projectId, topK, mode: "hybrid" \| "dense" \| "lexical" }` | `200 OK`: `RAGSearchResponse` (items, rrfScores, sources) | `ragService.search` |

---

### Telemetry Ingestion Endpoints (`backend/app/api/v1/telemetry.py`)

| Method | Endpoint | Auth | Purpose | Request Body | Response (Status & Schema) | Sender / Caller |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `POST` | `/api/telemetry/{id}/logs` | Bearer | Ingest structured logs | `{ logs: [ { timestamp, level, message, traceback, service } ] }` | `202 Accepted`: `{ ingested: 10, anomaliesDetected: 1 }` | Loki / Agent / Test |
| `POST` | `/api/telemetry/{id}/metrics` | Bearer | Ingest time-series metrics | `{ metrics: [ { name, value, timestamp, tags } ] }` | `202 Accepted`: `{ ingested: 50 }` | Prometheus / Metricbeat |
| `POST` | `/api/telemetry/{id}/traces` | Bearer | Ingest OpenTelemetry spans | `{ traces: [ { traceId, spanId, name, durationMs, error } ] }` | `202 Accepted`: `{ ingested: 12 }` | OTel Collector / HTTP SDK |
| `GET` | `/api/telemetry/{id}/logs` | Bearer | Query recent logs | Query: `level`, `limit` | `200 OK`: `List[TelemetryLogResponse]` | `telemetryService.getLogs` |
| `GET` | `/api/telemetry/{id}/metrics` | Bearer | Query metric points | Query: `name`, `timeRange` | `200 OK`: `List[TelemetryMetricResponse]` | `telemetryService.getMetrics` |
| `GET` | `/api/telemetry/{id}/traces` | Bearer | Query span traces | Query: `status`, `limit` | `200 OK`: `List[TelemetryTraceResponse]` | `telemetryService.getTraces` |

---

### Reports & PDF Postmortem Endpoints (`backend/app/api/v1/reports.py`)

| Method | Endpoint | Auth | Purpose | Request / Query | Response (Status & Schema) | Frontend Caller |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `GET` | `/api/reports` | Bearer | List incident reports | Query: `projectId` | `200 OK`: `List[ReportResponse]` | `reportService.list` |
| `GET` | `/api/reports/{id}` | Bearer | Get report detail | Path: `id` | `200 OK`: `ReportDetailResponse` | `reportService.getById` |
| `GET` | `/api/reports/{id}/export-pdf`| Bearer | Download native `%PDF-1.4` binary stream | Path: `id` | `200 OK`: `application/pdf` binary stream | Direct browser download / `reportService.downloadPdf` |
