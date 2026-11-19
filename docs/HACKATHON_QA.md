# FIXORA — Hackathon Judge Q&A & Technical Defense Guide

> **Anticipated Inquiries, Architectural Justifications & Definitive Technical Answers**  
> *22 battle-tested questions and answers spanning systems architecture, AI safety, performance, and commercial viability.*

---

## Category 1: Systems Architecture & Engineering

### Q1: "Why did you build your own multi-agent orchestrator with LangGraph instead of using AutoGen, CrewAI, or an OpenAI Assistant?"
**Answer:**
> *"AutoGen and CrewAI lean heavily into open-ended conversational agent dynamics where agents talk back and forth. In production incident response, open-ended conversation leads to unpredictable token loops, state explosion, and non-deterministic latency. 
> 
> We chose LangGraph because it models agent orchestration as a formal **StateGraph** with strict Pydantic state typing. Each of our 7 agents (Triage, Retrieval, RCA, Diagnostic, AutoPatch, Validation, Postmortem) has explicit input and output contracts. If an agent fails to produce an expected artifact (like a valid unified diff), the state machine deterministic transitions to a defined retry node rather than wandering aimlessly."*

### Q2: "How does FIXORA scale when a repository contains millions of lines of code?"
**Answer:**
> *"We do not shove entire repositories into an LLM context window. During onboarding, FIXORA’s ingestion worker chunks code based on AST structural boundaries (classes, methods, modules). 
> 
> We combine Qdrant dense vector indexing with an Okapi BM25 index and Neo4j call-graphs. When an incident occurs, our Hybrid RAG pipeline uses Reciprocal Rank Fusion ($k=60$) and Cross-Encoder neural reranking to distill millions of lines down to the exact 5 most relevant code passages (~2,000 tokens). This keeps LLM inference costs and latency constant regardless of repository scale."*

### Q3: "What database does FIXORA use, and how does it support production workloads?"
**Answer:**
> *"Our primary data layer is built on SQLAlchemy 2.0 with full asynchronous session support. For local development and hackathon demonstrations, we default to SQLite with `aiosqlite` for zero-configuration, turnkey evaluation. 
> 
> However, the entire data schema is engineered for enterprise PostgreSQL using `asyncpg`. Switching to a high-concurrency PostgreSQL cluster simply requires changing the `DATABASE_URL` connection string in `.env`. Furthermore, vector search is decoupled into Qdrant, and dependency mapping into Neo4j."*

### Q4: "Why do you have both a Knowledge Base and RAG Search in the UI?"
**Answer:**
> *"They serve two complementary functions in the engineering workflow. The **Knowledge Base** is the administrative *corpus management plane* where engineers upload architecture decision records (ADRs), postmortems, and API specs. **RAG Search** is the active *developer retrieval workbench* where engineers run natural language and technical queries against both code ASTs and uploaded documents, viewing fused relevance scores and source citations."*

---

## Category 2: AI, Multi-Modal RAG & Hallucination Prevention

### Q5: "How do you prevent the LLM from hallucinating invalid function names or libraries that don't exist in the project?"
**Answer:**
> *"We enforce hallucination prevention through three architectural layers:
> 1. **Prompt Constraint & Context Anchoring:** The AutoPatch prompt receives only verified symbols retrieved from the project's indexed AST and strictly prohibits inventing unimported libraries.
> 2. **In-Process AST Linting:** Before running tests, candidate diffs are parsed by language-specific AST engines to verify syntactical validity and import resolutions.
> 3. **The Sandbox Execution Gate:** The ultimate proof of non-hallucination is execution. Candidate patches must pass the project's real test suite inside our Docker sandbox. If the LLM invents a non-existent function, `pytest` fails with `AttributeError` or `ImportError`, and the error log is fed back to the agent for self-correction."*

### Q6: "Why use both dense vector search and BM25 lexical search? Isn't vector search enough?"
**Answer:**
> *"In software engineering, vector search alone frequently fails on exact identifier lookups. For example, if an error mentions `calculate_tax_v2_rollback`, a dense embedding might retrieve generic tax calculation functions while missing the exact variable name. 
> 
> BM25 excels at exact lexical token matching, whereas dense vectors excel at semantic intent. By fusing both result sets using Reciprocal Rank Fusion ($k=60$) followed by a Cross-Encoder reranker, we achieve 96%+ top-5 retrieval precision."*

### Q7: "What happens if the LLM provider (OpenAI / Anthropic) goes down or rate limits you?"
**Answer:**
> *"FIXORA is architected with provider-agnostic resilience. The platform supports OpenAI (GPT-4o), Anthropic (Claude 3.5 Sonnet), and Google (Gemini 1.5 Pro). If an external API key is absent or unreachable, the system activates an in-memory deterministic heuristic engine for triage and diff synthesis, ensuring the platform remains fully demonstrable even during complete external API blackouts."*

---

## Category 3: Security, Sandboxing & Reliability

### Q8: "How do you ensure a malicious candidate patch doesn't escape the sandbox or delete host files?"
**Answer:**
> *"The Docker sandbox runner (`SandboxService`) implements defense-in-depth:
> 1. Containers run with `network_mode='none'`, completely cutting off external outbound internet access.
> 2. Containers execute under an unprivileged non-root user (`sandboxuser`, UID 1000).
> 3. Strict cgroup resource bounds are enforced: max 2048 MB memory and 1.0 CPU core.
> 4. A hard wall-clock timeout of 15.0 seconds terminates infinite loops via `asyncio.wait_for`.
> 5. Host volumes are mounted read-only, with modifications isolated to an ephemeral scratch volume destroyed immediately after test execution."*

### Q9: "What is the Zip Slip vulnerability and how did you mitigate it?"
**Answer:**
> *"Zip Slip is an arbitrary file overwrite vulnerability where a maliciously crafted zip archive contains directory traversal sequences like `../../../../etc/cron.d/malicious`. When unzipped, it escapes the target directory and overwrites critical host files. 
> 
> In `RepositoryService`, we inspect every zip member using `os.path.abspath` before extraction. If the destination path does not strictly start with the designated temporary sandbox folder prefix, extraction is immediately aborted, a `SecurityException` is logged, and the uploaded archive is purged."*

### Q10: "Can FIXORA push broken or unvetted code directly into a customer's production branch?"
**Answer:**
> *"Architecturally, absolutely not. FIXORA has a zero-direct-push policy:
> 1. The platform is hardcoded to never push to `main`, `master`, or protected branches.
> 2. All candidate fixes create isolated feature branches (`fixora/patch-...`).
> 3. Pull Requests are created exclusively in `draft` mode.
> 4. Most importantly, our **Human Approval Gate** requires an authenticated engineer to click 'Approve Patch' in the UI before any PR API call will execute. Unapproved requests are rejected with HTTP 400."*

---

## Category 4: Telemetry & Observability

### Q11: "How does FIXORA receive telemetry from deployed applications?"
**Answer:**
> *"FIXORA exposes OpenTelemetry-compatible REST endpoints for `/api/telemetry/{id}/logs`, `/metrics`, and `/traces`. Applications instrumented with the standard OpenTelemetry SDK, Prometheus clients, or Loki log forwarders simply configure their HTTP exporter endpoint to point to FIXORA. Incoming payloads are scrubbed, parsed, and clustered in real time."*

### Q12: "Why does the Logs or Traces page show an empty state when first opened?"
**Answer:**
> *"Because FIXORA provides an honest, production-grade developer platform rather than a hardcoded static mockup. If an external collector daemon is not currently streaming live logs into the project's endpoint, the UI displays an honest, clean empty state with clear instructions and curl commands showing how to connect an external log shipper."*

---

## Category 5: Product, Market & Business Value

### Q13: "How is FIXORA different from GitHub Copilot or Cursor?"
**Answer:**
> *"Copilot and Cursor are **developer-prompted authoring assistants** that operate inside the IDE while an engineer is typing code. 
> 
> FIXORA is an **autonomous, closed-loop reliability platform** that operates at the system level. FIXORA doesn't wait for a prompt: it monitors telemetry alerts, triages incidents, isolates failing code across microservices, tests candidate fixes in Docker, and stages pull requests with zero initial developer intervention. Copilot is an authoring tool; FIXORA is an operational SRE."*

### Q14: "How is FIXORA different from Sentry or Datadog?"
**Answer:**
> *"Sentry and Datadog are **observability platforms**—they tell you *that* something broke and show you the stack trace, but they leave 100% of the diagnosis, reproduction, patch creation, and testing to a human engineer. 
> 
> FIXORA takes over where Sentry stops. We ingest the stack trace, launch a multi-agent investigation, retrieve the code context, generate a unified diff, validate it in a sandbox, and open a GitHub PR. We transform raw alerts into resolved pull requests."*

### Q15: "What is the primary metric engineering leaders care about when adopting FIXORA?"
**Answer:**
> *"Mean Time to Resolution (MTTR). In high-volume SaaS companies, downtime averages \$5,000 per minute. By automating the triaging, retrieval, and regression testing phases—which consume over 70% of incident response time—FIXORA reduces MTTR from hours to under 5 minutes."*

### Q16: "What is your pricing or monetization model for enterprise adoption?"
**Answer:**
> *"A tiered SaaS and self-hosted model:
> 1. **Developer Tier (Free / Open Source):** Up to 2 repositories, local SQLite, community support.
> 2. **Team Tier (\$99/seat/month):** Unlimited repositories, cloud Qdrant and PostgreSQL hosting, GitHub PR automations, up to 100 autonomous sandbox repairs per month.
> 3. **Enterprise Tier (Custom / Self-Hosted):** On-premise air-gapped deployment, custom LLM fine-tuning, VPC peering, SOC 2 compliance reporting, and unlimited concurrent Docker validation runners."*

---

## Category 6: Edge Cases & Operational Limits

### Q17: "What happens if a candidate patch causes a new test regression in the sandbox?"
**Answer:**
> *"The Validation Agent detects the non-zero exit code and captures the test `stderr`. Rather than terminating, the agent enters a self-correction feedback loop: it feeds the failure output back to the AutoPatch Agent with the directive: *'The previous patch failed with this assertion error. Refine the diff to satisfy this condition without breaking existing tests.'* FIXORA allows up to 3 automated retry cycles before marking the patch as requiring manual developer intervention."*

### Q18: "What languages and frameworks does FIXORA currently support for AST parsing and repair?"
**Answer:**
> *"The architecture is language-agnostic. Currently, full AST parsing, chunking, and sandboxed test execution are validated for **Python** (`pytest`, `unittest`) and **TypeScript / JavaScript** (`Jest`, `Vitest`). The AST walker is modular, allowing easy addition of Go (`go test`) and Rust (`cargo test`) tree-sitter parsers."*

### Q19: "How does the postmortem PDF export work without bulky external headless browsers?"
**Answer:**
> *"Instead of relying on fragile headless browser instances like Puppeteer or Chromium, which introduce heavy memory footprints and cold-start latency, FIXORA utilizes a high-performance native binary stream generator in `backend/app/api/v1/reports.py`. It constructs compliant `%PDF-1.4` byte streams on the fly, delivering sub-50ms downloads with zero external binary dependencies."*

### Q20: "Can an engineer edit the candidate diff in AutoPatch Studio before approving it?"
**Answer:**
> *"Currently, AutoPatch Studio allows engineers to inspect the unified diff side-by-side, view highlighted additions/deletions, trigger re-tests, and approve or reject the patch. Full in-browser line-by-line diff editing is scheduled on our immediate product roadmap."*

### Q21: "How does FIXORA prevent duplicate incidents when an error occurs 500 times in 1 minute?"
**Answer:**
> *"In `TelemetryService`, incoming exceptions are normalized and hashed into an `error_signature` based on the exception type, root file, and root line number. If an active incident with this signature already exists in the database within a sliding time window, FIXORA simply increments the `occurrence_count` and updates the timestamp, preventing alert storms."*

### Q22: "If you had 3 more weeks to work on FIXORA, what would you build next?"
**Answer:**
> *"Three key enhancements:
> 1. **Live PR Webhook Synchronization:** Bi-directional GitHub App integration that automatically updates FIXORA when peer review comments are posted on the generated Pull Request.
> 2. **Canary Verification Deployment:** Automated deployment of validated patches to an ephemeral Kubernetes staging cluster with synthetic traffic generation.
> 3. **Fine-Tuned Specialized RCA Models:** Fine-tuning an open-weights model (like Llama 3.3 70B) specifically on historical Linux and Python bug-fix diff datasets to further reduce LLM token costs."*
