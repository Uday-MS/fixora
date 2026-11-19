# FIXORA — Complete System Architecture & Visual Diagrams

> **Structural Topologies, Component Interactions & End-to-End Diagrams**  
> *Ten comprehensive Mermaid diagrams documenting the architectural fabric of FIXORA.*

---

## 1. High-Level System Architecture

```mermaid
flowchart TD
    subgraph ClientLayer ["Client & Interface Layer"]
        UI["React 19 + TypeScript SPA (Vite)"]
        UI_Dash["Dashboard & Health Monitoring"]
        UI_Studio["AutoPatch Studio & Diff Viewer"]
        UI_Inv["Investigation & Incident Command"]
        UI_RAG["RAG Search & Knowledge Base"]
    end

    subgraph GatewayLayer ["API Gateway & Application Server"]
        API["FastAPI Async REST Server (Uvicorn :8000)"]
        AuthMiddleware["JWT Authentication & RBAC Guard"]
        PydanticCamel["Pydantic v2 CamelModel Serialization"]
    end

    subgraph ServiceLayer ["Core Service Orchestration"]
        RepoSvc["Repository & Ingestion Service"]
        AgentSvc["LangGraph Multi-Agent Orchestrator"]
        RAGSvc["Hybrid RAG & Dependency Engine"]
        PatchSvc["AutoPatch & Sandbox Runner"]
        TelemSvc["Telemetry Ingestion & Anomaly Triage"]
        PostmortemSvc["Postmortem & PDF Generation Engine"]
    end

    subgraph PersistenceLayer ["Persistence & Vector Storage"]
        DB[(SQL Database: SQLite / PostgreSQL)]
        QdrantDB[(Qdrant Vector DB / In-Memory Fallback)]
        GraphDB[(Neo4j Call Graph / NetworkX Fallback)]
        RedisCache[(Redis Cache & Event Bus)]
    end

    subgraph ExecutionLayer ["Hardened Execution Sandbox"]
        DockerHost["Docker Engine Sandbox Runner"]
        SandBoxCont["Ephemeral Container (Non-root, 2GB RAM, 15s Timeout)"]
    end

    subgraph ExternalServices ["External Ecosystem"]
        GitHubAPI["GitHub REST API (PyGithub)"]
        LLMProvider["LLM Provider (OpenAI / Gemini / Anthropic)"]
        TelemetrySources["Telemetry Forwarders (OTel / Loki / Prometheus)"]
    end

    UI -->|JSON / REST| API
    API --> AuthMiddleware
    AuthMiddleware --> PydanticCamel
    PydanticCamel --> ServiceLayer

    RepoSvc --> DB
    RepoSvc --> QdrantDB
    RepoSvc --> GraphDB
    RepoSvc --> GitHubAPI

    TelemSvc --> DB
    TelemSvc --> AgentSvc
    TelemetrySources --> TelemSvc

    AgentSvc --> RAGSvc
    AgentSvc --> LLMProvider
    AgentSvc --> PatchSvc

    RAGSvc --> QdrantDB
    RAGSvc --> GraphDB

    PatchSvc --> DockerHost
    DockerHost --> SandBoxCont
    PatchSvc --> GitHubAPI

    PostmortemSvc --> DB
```

---

## 2. Frontend-to-Backend Communication Flow

```mermaid
sequenceDiagram
    autonumber
    actor User as Engineer / SRE
    participant UI as React 19 Frontend
    participant Client as API Client (api.ts)
    participant FastAPIRoute as FastAPI Endpoint (:8000)
    participant Auth as Auth & Context Dependency
    participant Service as Domain Service Layer
    participant DB as Async Database Session

    User->>UI: Triggers Action (e.g. Approve Patch)
    UI->>Client: Call patchService.approve(patchId)
    Client->>FastAPIRoute: POST /api/patches/{id}/approve (Bearer JWT)
    FastAPIRoute->>Auth: Verify Token & Workspace Access
    Auth-->>FastAPIRoute: Validated User & Workspace Context
    FastAPIRoute->>Service: PatchService.approve_patch(patch_id, user)
    Service->>DB: UPDATE patches SET status='approved'
    Service->>DB: INSERT audit_logs (action='patch_approved')
    DB-->>Service: Commit Confirmed
    Service-->>FastAPIRoute: PatchApprovalResponse (Pydantic)
    FastAPIRoute-->>Client: 200 OK (CamelCase JSON)
    Client-->>UI: Resolved Promise
    UI->>User: Update UI State to 'Approved' & Enable 'Create PR'
```

---

## 3. Database Architecture & Entity Relationships

```mermaid
erDiagram
    USERS ||--o{ WORKSPACES : owns
    WORKSPACES ||--o{ PROJECTS : contains
    PROJECTS ||--o{ REPOSITORIES : tracks
    REPOSITORIES ||--o{ BUGS : identifies
    BUGS ||--o{ INVESTIGATIONS : triggers
    INVESTIGATIONS ||--o{ PATCHES : generates
    PATCHES ||--o{ TEST_RUNS : validates
    PROJECTS ||--o{ INCIDENTS : records
    PROJECTS ||--o{ KNOWLEDGE_DOCUMENTS : indexes
    REPOSITORIES ||--o{ INGESTION_JOBS : executes
    PROJECTS ||--o{ TELEMETRY_LOGS : collects
    PROJECTS ||--o{ TELEMETRY_METRICS : aggregates
    PROJECTS ||--o{ TELEMETRY_TRACES : traces

    USERS {
        uuid id PK
        string email
        string hashed_password
        string role
        timestamp created_at
    }

    REPOSITORIES {
        uuid id PK
        uuid project_id FK
        string name
        string git_url
        string default_branch
        string status
        int stars_count
        timestamp indexed_at
    }

    BUGS {
        uuid id PK
        uuid repository_id FK
        string title
        string severity
        string status
        string file_path
        int line_number
    }

    INVESTIGATIONS {
        uuid id PK
        uuid bug_id FK
        uuid incident_id FK
        string status
        json state_data
        timestamp created_at
    }

    PATCHES {
        uuid id PK
        uuid investigation_id FK
        text diff_content
        string status
        boolean human_approved
        string pull_request_url
    }

    TEST_RUNS {
        uuid id PK
        uuid patch_id FK
        string status
        text stdout
        int exit_code
        float execution_time_sec
    }
```

---

## 4. GitHub Ingestion Pipeline

```mermaid
flowchart TD
    Start["User inputs GitHub Repo URL"] --> ValidateURL{"Validate URL & Credentials"}
    ValidateURL -- Invalid --> ReturnErr["Return 400 Bad Request"]
    ValidateURL -- Valid --> CreateJob["Create IngestionJob (status='processing')"]
    CreateJob --> CloneRepo["PyGithub / GitPython Shallow Clone (:depth 1)"]
    CloneRepo --> ASTWalk["AST File Walker & Parser"]
    
    subgraph Parsing ["AST & Syntax Processing"]
        ASTWalk --> FilterExt["Filter Code Files (.py, .ts, .js, .go, .rs)"]
        FilterExt --> ExtractSymbols["Extract Classes, Functions, and Imports"]
        ExtractSymbols --> ChunkCode["Chunk Code with Semantic Boundaries"]
    end

    subgraph Indexing ["Dual-Index Ingestion"]
        ChunkCode --> Embed["Generate Dense Embeddings (384-dim)"]
        Embed --> UpsertQdrant["Upsert into Qdrant Vector Store"]
        ChunkCode --> BuildBM25["Update Lexical BM25 Corpus Index"]
        ExtractSymbols --> BuildGraph["Extract Call-Graph into Neo4j / NetworkX"]
    end

    UpsertQdrant --> UpdateJob["Mark IngestionJob 'completed'"]
    BuildBM25 --> UpdateJob
    BuildGraph --> UpdateJob
    UpdateJob --> NotifyUI["UI Reflects Repository Ready for Analysis"]
```

---

## 5. ZIP Ingestion Pipeline & Security Sandbox

```mermaid
flowchart TD
    UploadZip["User uploads .zip file via UI"] --> CheckSize{"Size <= 50MB?"}
    CheckSize -- No --> RejectSize["Return 413 Payload Too Large"]
    CheckSize -- Yes --> TempDir["Write to Isolated Temporary Dir"]
    
    subgraph SecurityDefense ["Zip Slip & Security Defense"]
        TempDir --> InspectZip["Inspect ZipArchive File Names"]
        InspectZip --> PathCheck{"Contains '../' or Absolute Path?"}
        PathCheck -- Malicious --> AbortJob["Abort & Log Security Exception"]
        PathCheck -- Safe --> ExtractSafe["Extract Files to Bounded Sandboxed Path"]
    end

    ExtractSafe --> ScanTree["Walk Extracted Code Tree"]
    ScanTree --> ASTIndex["Execute AST Chunking & Semantic Indexing"]
    ASTIndex --> Vectorize["Store in Qdrant & BM25 Indexes"]
    Vectorize --> CleanupDisk["Clean Temporary Extraction Directory"]
    CleanupDisk --> CompleteZip["Mark Repository Active"]
```

---

## 6. Knowledge Base & Hybrid RAG Pipeline

```mermaid
flowchart LR
    subgraph Ingestion ["Knowledge & Doc Ingestion"]
        DocUpload["Markdown / Architecture Docs"] --> DocChunker["Document Chunker (500 tokens)"]
        DocChunker --> DocEmbed["384-dim Embedder"]
        DocEmbed --> QdrantDoc["Qdrant Collection: 'knowledge_base'"]
    end

    subgraph HybridSearch ["Hybrid Retrieval Pipeline"]
        Query["Incident Context or Search Query"] --> VectorSearch["Qdrant Dense Cosine Search"]
        Query --> BM25Search["BM25 Lexical Keyword Search"]
        Query --> GraphSearch["Neo4j Dependency Subgraph Search"]
        
        VectorSearch --> RRF["Reciprocal Rank Fusion (RRF k=60)"]
        BM25Search --> RRF
        
        RRF --> TopK["Fused Top-50 Candidates"]
        TopK --> CrossEncoder["Cross-Encoder Neural Reranker"]
        CrossEncoder --> TopN["Top-5 Precision Passages"]
    end

    subgraph Grounding ["Agent Grounding"]
        TopN --> Synthesis["Prompt Context Assembly"]
        GraphSearch --> Synthesis
        Synthesis --> RCAAgent["RCA & Patch Generation Agent"]
    end
```

---

## 7. AI Investigation Multi-Agent Pipeline (LangGraph)

```mermaid
stateDiagram-v2
    [*] --> TriageAgent: Incident or Bug Triggered
    
    TriageAgent --> RetrievalAgent: Severity & Target Scope Identified
    note right of TriageAgent
        Parses stack traces, extracts
        error code & affected microservices.
    end note

    RetrievalAgent --> RCAAgent: Hybrid RAG & Dependency Context Loaded
    note right of RetrievalAgent
        Gathers code chunks, call graphs,
        and past postmortem documents.
    end note

    RCAAgent --> DiagnosticAgent: Hypothesis & Failing Node Isolated
    note right of RCAAgent
        Determines root cause: null deref,
        type mismatch, race condition, etc.
    end note

    DiagnosticAgent --> AutoPatchAgent: Repro Test Spec Synthesized
    note right of DiagnosticAgent
        Designs a targeted regression test
        verifying the reproduction path.
    end note

    AutoPatchAgent --> ValidationAgent: Unified Diff Synthesized
    note right of AutoPatchAgent
        Generates clean AST-aligned
        unified patch.
    end note

    ValidationAgent --> PostmortemAgent: Tests Pass in Docker Sandbox
    ValidationAgent --> AutoPatchAgent: Tests Fail (Retry Loop <= 3)
    note right of ValidationAgent
        Compiles and executes test suite
        in hardened non-root container.
    end note

    PostmortemAgent --> [*]: Postmortem & Draft PR Staged
    note right of PostmortemAgent
        Generates timeline, impact radius,
        and binary PDF postmortem.
    end note
```

---

## 8. AutoPatch Validation Pipeline & Sandbox Execution

```mermaid
sequenceDiagram
    autonumber
    participant AutoPatch as AutoPatch Agent
    participant Runner as Docker Sandbox Runner
    participant Docker as Ephemeral Docker Container
    participant FS as Ephemeral Volume
    participant DB as Patches Table

    AutoPatch->>Runner: Submit Unified Diff + Target Repo
    Runner->>FS: Mount Target Source Code in Ephemeral Volume
    Runner->>FS: Apply Unified Diff (`git apply`)
    alt Diff Application Fails
        Runner-->>AutoPatch: Diff Syntax / Hunk Reject Error
    else Diff Applied Cleanly
        Runner->>Docker: Launch Container (pytest runner)
        Note over Docker: CPU=1.0, RAM=2048MB, Network=None, Timeout=15s
        Docker->>Docker: Execute Test Suite (`pytest -k target_test`)
        alt Tests Fail
            Docker-->>Runner: Exit Code != 0 + stderr output
            Runner->>DB: Log TestRun (status='failed')
            Runner-->>AutoPatch: Return Failure Feedback for Diff Regeneration
        else Tests Pass
            Docker-->>Runner: Exit Code 0 + stdout passing summary
            Runner->>DB: Log TestRun (status='passed')
            Runner->>DB: Update Patch (status='validated', ready_for_review=True)
            Runner-->>AutoPatch: Verification Success
        end
    end
```

---

## 9. Observability & Telemetry Ingestion Pipeline

```mermaid
flowchart TD
    subgraph Sources ["Telemetry Producers"]
        OTel["OpenTelemetry Collector / App SDK"]
        Loki["Grafana Loki Log Shipper"]
        Prom["Prometheus Alertmanager Webhooks"]
    end

    subgraph IngestionEndpoints ["FastAPI Ingestion Gateway"]
        EndpointLog["POST /api/telemetry/{proj_id}/logs"]
        EndpointMetric["POST /api/telemetry/{proj_id}/metrics"]
        EndpointTrace["POST /api/telemetry/{proj_id}/traces"]
    end

    OTel --> EndpointTrace
    Loki --> EndpointLog
    Prom --> EndpointMetric

    subgraph Processing ["Processing & Anomaly Clustering"]
        EndpointLog --> ParseLog["Traceback Parser & Regex Scrubber"]
        EndpointMetric --> ThresholdCheck{"Error Rate > 5% or Latency > 2s?"}
        EndpointTrace --> TraceLink["Span Error Extraction"]

        ParseLog --> AnomalyCluster["Anomaly Clustering Engine (Deduplication)"]
        ThresholdCheck -- Breach --> AnomalyCluster
        TraceLink --> AnomalyCluster
    end

    subgraph IncidentCreation ["Incident Lifecycle"]
        AnomalyCluster --> MatchActive{"Active Incident Exists for Signature?"}
        MatchActive -- Yes --> IncrementCount["Increment Incident Occurrence Counter"]
        MatchActive -- No --> CreateIncident["Create New Incident (status='open')"]
        CreateIncident --> TriggerAgent["Dispatch Async Multi-Agent Investigation"]
    end
```

---

## 10. Postmortem & Binary PDF Export Pipeline

```mermaid
flowchart LR
    subgraph Trigger ["Incident Resolution"]
        InvestigationDone["Investigation & Patch Validated"] --> PostmortemGen["Postmortem Agent Synthesizes Analysis"]
        PostmortemGen --> SaveRecord["Save Postmortem to DB (reports table)"]
    end

    subgraph UserAction ["User Interaction"]
        WebUI["Reports Page (ReportsPage.tsx)"] --> ClickExport["Click 'Export PDF' Button"]
        ClickExport --> APICall["GET /api/reports/{id}/export-pdf"]
    end

    subgraph PDFEngine ["Backend PDF Generator"]
        APICall --> FetchReport["Load Postmortem Data & Incident Timestamps"]
        FetchReport --> FormatText["Format Summary, Root Cause & Action Items"]
        FormatText --> BinaryStream["Generate Native %PDF-1.4 Binary Byte Stream"]
        BinaryStream --> Response["HTTP 200: application/pdf; filename='fixora-postmortem.pdf'"]
    end

    Response --> BrowserDownload["Browser Triggers File Download Dialog"]
```
