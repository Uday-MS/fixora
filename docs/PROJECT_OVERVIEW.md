# FIXORA — Project Overview & Strategic Architecture

> **Autonomous Code Repair & Incident Intelligence Platform**  
> *Closing the loop between production telemetry, root-cause diagnostics, and automated patch synthesis.*

---

## 1. Executive Summary & Pitch Variants

### The 30-Second Elevator Pitch
> *"When a production service crashes at 2 AM, engineering teams lose hours correlating dispersed logs, triaging traces, and navigating massive repositories to locate the defect. **FIXORA** is an Autonomous Code Repair and Incident Intelligence Platform that closes this loop automatically. It continuously monitors live telemetry, pinpoints anomalies, initiates a 7-stage multi-agent LangGraph investigation across code and knowledge graphs, isolates the offending commit and AST node, generates an exact unified diff patch, validates it inside an isolated Docker sandbox, and prepares a verified GitHub pull request—requiring only one-click human approval."*

### The 1-Minute Technical Overview
> *"Modern software operations are fragmented: monitoring alerts in Datadog or Sentry require human engineers to manually inspect codebases, write reproducing tests, and craft fixes. FIXORA unifies incident intelligence with autonomous program repair. 
> 
> Operating in both pre-deployment (static repository scanning and test repair) and post-deployment (live telemetry ingestion of logs, metrics, and traces) modes, FIXORA executes an event-driven workflow. When an alert or bug is detected, our LangGraph-orchestrated multi-agent pipeline activates. A hybrid RAG engine (combining Qdrant dense vector search, BM25 lexical search with Reciprocal Rank Fusion, and Neo4j topological dependency graphs) feeds deep contextual grounding to our specialized Root Cause Analysis agent. 
> 
> Once the root cause is isolated, the AutoPatch engine generates candidate code fixes, which are executed and validated inside a hardened Docker sandbox with strictly bounded resource limits. A human-in-the-loop approval gate ensures zero unauthorized code modifications reach production: once approved by an engineer, FIXORA publishes an automated pull request and exports a comprehensive postmortem report."*

### The Detailed Explanation for Technical Judges
> *"FIXORA addresses the fundamental operational bottleneck of software engineering: Mean Time to Resolution (MTTR). Traditional APM tools only observe failures; coding copilots only generate code upon prompt. FIXORA bridges the chasm between **Observability** and **Remediation**.
>
> Built on a modern asynchronous architecture (FastAPI, React 19, SQLAlchemy 2.0, Qdrant, and LangGraph), FIXORA treats software reliability as a closed-loop control system:
> 1. **Ingestion & Topology Mapping:** Repositories (GitHub or local ZIP archives) are parsed into Abstract Syntax Trees (ASTs), chunked into semantic units, embedded into 384-dimensional dense vectors, and mapped into topological dependency call-graphs.
> 2. **Telemetry Ingestion & Anomaly Triage:** The platform ingests OpenTelemetry-compatible traces, Prometheus-style metrics, and Loki-structured logs, parsing tracebacks and identifying error spikes.
> 3. **Seven-Stage Deterministic Agent Pipeline:** Orchestrated via LangGraph StateGraph, dedicated agents (Triage, Retrieval, RCA, Diagnostic, AutoPatch, Validation, and Postmortem) collaborate with strict state schema contracts, eliminating free-form conversational drift.
> 4. **Sandboxed Verification:** Patches are not trusted blindly. They are mounted into an isolated, non-root Docker container with CPU, memory, and timeout constraints, running the project's actual unit and integration test suites.
> 5. **Governed Delivery:** In strict adherence to enterprise safety standards, FIXORA enforces a mandatory human approval gate before any branch mutation or pull request creation occurs."*

---

## 2. The Core Problem Statement

### The Triaging & Incident Response Crisis
In contemporary microservice and cloud-native architectures, an outage or defect introduces cognitive overload:
1. **Dispersed Context:** Telemetry data lives in monitoring silos (Datadog, Grafana, CloudWatch), while source code resides in Git repositories, and architectural context is buried in Confluence or Markdown docs.
2. **High Mean Time to Detect (MTTD) & Resolve (MTTR):** On average, over 70% of outage resolution time is spent diagnosing *where* and *why* a failure occurred, rather than drafting the actual code fix.
3. **Repetitive Regression Fatigue:** Engineers frequently spend high-value sprint cycles diagnosing recurring null pointer exceptions, unhandled boundary cases, and schema mismatch regressions.
4. **Context Switching:** On-call engineers woken at night lack immediate mental context on services authored by other team members, leading to rushed, unverified hotfixes that can trigger secondary outages.

---

## 3. Who FIXORA is Built For

| Target Persona | Key Pain Points Addressed | FIXORA Value Delivered |
| :--- | :--- | :--- |
| **Site Reliability Engineers (SREs)** | Unclear alert attribution, high alert fatigue, tedious postmortem writing. | Automated telemetry correlation, instant root-cause hypotheses, one-click PDF postmortem generation. |
| **DevOps & Platform Teams** | Brittle CI/CD pipelines, unauthorized hotfix risks, inconsistent staging verification. | Sandboxed patch validation, strict human approval gates, zero unvetted pushes to `main`. |
| **Backend & Full-Stack Developers** | Painful bug reproduction, tracing microservice dependencies, manual patch authoring. | Unified diff generation, AST-aware dependency retrieval, automated test run verification. |
| **Engineering Leadership (VPs/CTOs)** | High MTTR metrics, SLA breach penalties, lost developer productivity. | Drastic reduction in MTTR, standardized incident postmortems, comprehensive system health auditing. |

---

## 4. Why FIXORA is Not Just Another "RAG Chatbot"

Most AI developer tools operate as conversational chatbots (e.g., ChatGPT, basic Copilot chat) that suffer from three fatal flaws in production engineering: lack of execution feedback, hallucinated syntax, and absence of operational context. FIXORA is architecturally distinct:

```
Conversational Chatbot:
User Prompt  ──>  LLM Generation  ──>  Unverified Text Output  ──>  Manual Copy/Paste by Dev

FIXORA Autonomous Loop:
Telemetry/Issue ──> Hybrid RAG ──> Multi-Agent RCA ──> Diff Generation ──> Docker Sandbox Test ──> Human Gate ──> GitHub PR
```

1. **Deterministic Agent State Machine:** FIXORA uses LangGraph with structured Pydantic state transitions. Agents cannot deviate, chat aimlessly, or skip critical diagnostic steps.
2. **Hybrid Multi-Stage Retrieval:** Rather than simple vector cosine similarity, FIXORA combines dense vector search with BM25 lexical keyword matching (RRF $k=60$) and Neo4j topological dependency traversal.
3. **Execution-Grounded Validation:** FIXORA does not assume an LLM's code fix works. It compiles, executes, and validates the candidate patch inside an isolated Docker sandbox against automated regression tests before presenting it to an engineer.
4. **Full Lifecycle Governance:** Incorporates audit logs, cryptographic HMAC verification, human approval checkpoints, and git-native integration.

---

## 5. Two Operating Modes: Pre-Deployment vs. Post-Deployment

FIXORA is designed to operate seamlessly across the entire Software Development Lifecycle (SDLC):

### Mode 1: Pre-Deployment (Repository Analysis & Code Repair)
* **Trigger:** Code pushes, pull requests, repository uploads (ZIP or GitHub URL), or scheduled static audits.
* **Telemetry Required:** None.
* **Mechanism:** 
  - Scans repository source files, imports, and AST structures.
  - Detects syntax errors, antipatterns, missing exception handlers, and failing test suites.
  - Generates repairs for broken test cases or failing unit assertions.
  - Indexes architecture documents (`.md`, `.rst`, `.txt`) into the Knowledge Base for developer semantic search.

### Mode 2: Post-Deployment (Incident Intelligence & AutoPatch)
* **Trigger:** Telemetry ingestion (HTTP error spikes, Loki crash logs, unhandled exception traces, OpenTelemetry span latency anomalies).
* **Telemetry Required:** Active log/metric/trace ingestion via REST endpoints or webhook forwarders.
* **Mechanism:**
  - Ingests telemetry, clusters error signatures, and instantiates an `Incident`.
  - Maps stack traces back to repository source files indexed during onboarding.
  - Traces downstream impact across interconnected microservices.
  - Executes full multi-agent investigation, produces candidate patches, and runs sandbox verification.

---

## 6. What Autonomous Code Repair & Incident Intelligence Mean in FIXORA

### Autonomous Code Repair (AutoPatch)
*Autonomous Code Repair* in FIXORA is **not** unconstrained code rewriting. It is a rigorous, AST-grounded engineering workflow:
1. **Target Localization:** Identifying the exact file, class, and line range causing a regression.
2. **Context Assembly:** Gathering the local AST block, caller functions, dependent type definitions, and historical incident knowledge.
3. **Unified Diff Synthesis:** Prompting an LLM with strict instructions to output standard unified diff format (`--- a/file`, `+++ b/file`, `@@ -x,y +x,y @@`).
4. **Syntactic & Functional Verification:** Applying the diff to a temporary workspace branch, compiling the modified code, and running target test suites inside Docker.
5. **Human Gate:** The fix is presented to the engineer in an interactive side-by-side diff viewer. Only upon explicit human approval is a GitHub Pull Request opened.

### Incident Intelligence
*Incident Intelligence* in FIXORA is the automated transformation of raw operational noise into actionable, structured engineering context:
1. **Stack Trace Extraction:** Regex-based and heuristic extraction of file paths, line numbers, and exception types from raw unstructured logs.
2. **Anomaly Clustering:** Aggregating duplicate error bursts within time windows to prevent alert storms.
3. **Historical Correlation:** Querying vector memory to identify if a similar incident has occurred previously and retrieving the historical fix.
4. **Postmortem Automation:** Synthesizing root-cause timeline, impact radius, affected endpoints, and preventative action items into a clean PDF postmortem.

---

## 7. Complete Value Delivered to Engineering Teams

```
+---------------------------------------------------------------------------------+
|                                 FIXORA PLATFORM                                 |
+---------------------------------------------------------------------------------+
|   Pre-Deployment: Static Audits | Pre-Commit Checks | Test Suite Regeneration   |
+---------------------------------------------------------------------------------+
|   Post-Deployment: Anomaly Detection | Telemetry Triage | Root-Cause Analysis   |
+---------------------------------------------------------------------------------+
|   Remediation: Sandboxed AutoPatch | Human-in-the-Loop PR | Postmortem Reports  |
+---------------------------------------------------------------------------------+
                                         |
                                         v
   [ 70% Reduction in MTTR ]  [ Zero Unvetted Pushes ]  [ 100% Postmortem Audit ]
```
