# FIXORA — Database Architecture & Data Modeling Specification

> **Comprehensive Relational Schema, Multi-Model Storage Topologies & Entity Relationships**  
> *Detailed analysis of SQLAlchemy models, indexes, cascading behaviors, and polyglot persistence.*

---

## 1. Storage Topology Overview

FIXORA employs a polyglot persistence architecture designed for operational reliability, sub-millisecond retrieval, and horizontal scaling:

```
+-----------------------------------------------------------------------------------+
|                            STORAGE ARCHITECTURE TIERS                             |
+-----------------------------------------------------------------------------------+
| 1. Primary Relational Store: SQLite (Local/Demo) & PostgreSQL 16 (Enterprise)      |
|    - Engine: SQLAlchemy 2.0 Async (aiosqlite / asyncpg)                           |
|    - Scope: Users, Workspaces, Repos, Bugs, Patches, Incidents, Reports, Audits    |
+-----------------------------------------------------------------------------------+
| 2. Vector Database: Qdrant Engine (Port 6333)                                     |
|    - Schema: 384-dimensional dense vectors, HNSW index, cosine distance metric     |
|    - Scope: Source code AST chunks, architectural documentation, past postmortems  |
+-----------------------------------------------------------------------------------+
| 3. Topological Graph Store: Neo4j (Bolt :7687) / NetworkX (In-Memory)             |
|    - Schema: Labeled Property Graph ((:File)-[:IMPORTS]->(:File), (:Fn)-[:CALLS]) |
|    - Scope: Microservice service maps, caller/callee trees, dependency hierarchies|
+-----------------------------------------------------------------------------------+
| 4. Distributed Cache & Task Queue: Redis 7.2 (Port 6379)                          |
|    - Schema: Key-value, pub/sub, in-memory task queues                             |
|    - Scope: Session caching, rate limiting, agent state checkpoints               |
+-----------------------------------------------------------------------------------+
```

---

## 2. Complete Entity-Relationship Diagram (Mermaid ERD)

```mermaid
erDiagram
    users ||--o{ workspaces : "owns / members"
    workspaces ||--o{ projects : "contains"
    projects ||--o{ repositories : "manages"
    projects ||--o{ incidents : "records"
    projects ||--o{ knowledge_documents : "indexes"
    projects ||--o{ telemetry_logs : "collects"
    projects ||--o{ telemetry_metrics : "aggregates"
    projects ||--o{ telemetry_traces : "captures"
    projects ||--o{ reports : "publishes"

    repositories ||--o{ bugs : "discovers"
    repositories ||--o{ ingestion_jobs : "tracks"
    repositories ||--o{ code_chunks : "segments"

    incidents ||--o{ investigations : "triggers"
    bugs ||--o{ investigations : "triggers"

    investigations ||--o{ patches : "generates"
    patches ||--o{ test_runs : "validates"

    users ||--o{ audit_logs : "initiates"

    users {
        string id PK "UUID"
        string email UK "Unique indexed email"
        string hashed_password "Bcrypt hash"
        string full_name "User display name"
        string role "admin | engineer | viewer"
        boolean is_active "Active status"
        datetime created_at "Timestamp"
    }

    workspaces {
        string id PK "UUID"
        string name "Workspace name"
        string owner_id FK "References users.id"
        datetime created_at "Timestamp"
    }

    projects {
        string id PK "UUID"
        string workspace_id FK "References workspaces.id"
        string name "Project name"
        string description "Project description"
        string mode "development | deployed"
        datetime created_at "Timestamp"
    }

    repositories {
        string id PK "UUID"
        string project_id FK "References projects.id"
        string name "Repository name"
        string git_url "GitHub clone URL"
        string default_branch "main | master"
        string status "pending | indexing | ready | error"
        int file_count "Indexed file count"
        int lines_of_code "Total lines of code"
        datetime created_at "Timestamp"
        datetime updated_at "Timestamp"
    }

    ingestion_jobs {
        string id PK "UUID"
        string repository_id FK "References repositories.id"
        string status "pending | cloning | parsing | indexing | completed | failed"
        string stage "Current pipeline step"
        int progress_percent "0 to 100"
        string error_message "Failure diagnostics"
        datetime started_at "Timestamp"
        datetime completed_at "Timestamp"
    }

    bugs {
        string id PK "UUID"
        string repository_id FK "References repositories.id"
        string title "Defect title"
        string description "Technical summary"
        string severity "critical | high | medium | low"
        string status "detected | investigating | fixing | resolved"
        string file_path "Relative source path"
        int line_number "Target line number"
        datetime created_at "Timestamp"
    }

    incidents {
        string id PK "UUID"
        string project_id FK "References projects.id"
        string title "Incident summary"
        string description "Error context"
        string severity "P1 | P2 | P3 | P4"
        string status "open | investigating | mitigated | resolved"
        string error_signature "Hashed signature"
        int occurrence_count "Frequency counter"
        datetime started_at "Timestamp"
        datetime resolved_at "Timestamp"
    }

    investigations {
        string id PK "UUID"
        string incident_id FK "Nullable FK to incidents.id"
        string bug_id FK "Nullable FK to bugs.id"
        string repository_id FK "References repositories.id"
        string status "running | completed | failed"
        string current_stage "Current LangGraph Agent"
        json state_data "Serialized Agent State"
        datetime created_at "Timestamp"
        datetime completed_at "Timestamp"
    }

    patches {
        string id PK "UUID"
        string investigation_id FK "References investigations.id"
        string bug_id FK "Nullable FK to bugs.id"
        text diff_content "Unified diff string"
        string target_file "Target file path"
        string status "generated | validating | validated | approved | applied | rejected"
        boolean human_approved "Human gate flag"
        string pull_request_url "GitHub PR URL"
        datetime created_at "Timestamp"
    }

    test_runs {
        string id PK "UUID"
        string patch_id FK "References patches.id"
        string status "passed | failed | error | timeout"
        int exit_code "Process exit code"
        text stdout "Execution stdout"
        text stderr "Execution stderr"
        float execution_time_sec "Duration seconds"
        datetime executed_at "Timestamp"
    }

    knowledge_documents {
        string id PK "UUID"
        string project_id FK "References projects.id"
        string title "Document title"
        string doc_type "architecture | runbook | postmortem | api_spec"
        string file_path "Storage path"
        int chunk_count "Vector chunk count"
        datetime created_at "Timestamp"
    }

    reports {
        string id PK "UUID"
        string project_id FK "References projects.id"
        string incident_id FK "Nullable FK to incidents.id"
        string title "Postmortem Report Title"
        string executive_summary "High-level summary"
        string root_cause "Technical root cause"
        json action_items "Preventative action items"
        datetime generated_at "Timestamp"
    }

    audit_logs {
        string id PK "UUID"
        string user_id FK "References users.id"
        string action "Action identifier"
        string target_type "Entity type"
        string target_id "Target entity UUID"
        json metadata "Action context"
        datetime timestamp "Timestamp"
    }
```

---

## 3. Schema & Model Specifications

### Table: `repositories`
Defined in `backend/app/models/repository.py`:
- `id` (String, PK, default UUID4): Unique identifier.
- `project_id` (String, FK to `projects.id`, index=True, ondelete="CASCADE"): Multitenant project scoping.
- `name` (String, nullable=False): Repository name (e.g. `payment-service`).
- `git_url` (String, nullable=True): GitHub clone URL.
- `default_branch` (String, default="main"): Base branch for patches.
- `status` (String, default="pending"): State machine: `pending` $\rightarrow$ `indexing` $\rightarrow$ `ready` $\rightarrow$ `error`.
- `file_count` (Integer, default=0): Indexed file count.
- `lines_of_code` (Integer, default=0): Code volume metric.
- `created_at` / `updated_at` (DateTime, UTC): Audit timestamps.
- **Cascades:** Deleting a repository cascades to all linked `bugs`, `ingestion_jobs`, and `code_chunks`.

### Table: `patches`
Defined in `backend/app/models/patch.py`:
- `id` (String, PK, default UUID4): Unique patch identifier.
- `investigation_id` (String, FK to `investigations.id`, ondelete="CASCADE"): Originating investigation.
- `diff_content` (Text, nullable=False): Raw unified diff (`--- a/file +++ b/file @@ ... @@`).
- `target_file` (String, nullable=False): Target file receiving modification.
- `status` (String, default="generated"): State machine: `generated` $\rightarrow$ `validating` $\rightarrow$ `validated` $\rightarrow$ `approved` $\rightarrow$ `applied` $\rightarrow$ `rejected`.
- `human_approved` (Boolean, default=False): Enterprise safety gate. PR creation endpoint rejects unapproved patches with HTTP 400.
- `pull_request_url` (String, nullable=True): Resulting GitHub PR URL.
- **Cascades:** Deleting a patch cascades to all associated `test_runs`.

### Table: `test_runs`
Defined in `backend/app/models/test_run.py`:
- `id` (String, PK, default UUID4): Unique test run identifier.
- `patch_id` (String, FK to `patches.id`, ondelete="CASCADE"): Patch under validation.
- `status` (String, nullable=False): `passed`, `failed`, `error`, `timeout`.
- `exit_code` (Integer, nullable=False): Exit status code from the sandbox process.
- `stdout` (Text, nullable=True): Standard output log stream.
- `stderr` (Text, nullable=True): Standard error log stream.
- `execution_time_sec` (Float, default=0.0): Execution wall-clock duration.
- `executed_at` (DateTime, default=datetime.utcnow): Timestamp.

---

## 4. Auxiliary & Vector Database Schemas

### Qdrant Vector Collection: `fixora_code_index`
* **Vector Dimension:** 384 (Cosine distance).
* **Payload Fields:**
  - `repo_id` (Keyword, indexed for filtering): Foreign key to `repositories.id`.
  - `file_path` (Keyword): Relative file path in repository.
  - `start_line` / `end_line` (Integer): Exact line number boundaries.
  - `symbol_type` (Keyword): `function`, `class`, `method`, `module`.
  - `symbol_name` (Keyword): Extracted identifier name.
  - `code_snippet` (Text): Full source text.

### Neo4j Graph Schema (GraphRAG)
* **Node Labels:**
  - `(:Repository {id, name})`
  - `(:File {path, language})`
  - `(:Function {name, signature, start_line})`
  - `(:Class {name, file_path})`
* **Edge Relationships:**
  - `(:Repository)-[:CONTAINS]->(:File)`
  - `(:File)-[:DECLARES]->(:Function)`
  - `(:File)-[:IMPORTS]->(:File)`
  - `(:Function)-[:CALLS]->(:Function)`
  - `(:Function)-[:DEPENDS_ON]->(:Class)`
