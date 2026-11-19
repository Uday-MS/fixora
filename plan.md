# PATCHPILOT — MASTER PROJECT PLAN
## Autonomous Software Intelligence, Bug Detection & Repair Platform

**Official Hackathon Project:** AutoPatch — Autonomous Software Bug Detection and Repair System  
**Hackathon:** INNOVEDGE Innovation & Entrepreneurship Hackathon 2026  
**Domain:** Software Engineering & Automation  
**Challenge Area:** Intelligent Debugging & Program Repair  
**Primary Objective:** Deliver a working, explainable, test-backed software bug detection and repair platform within the 24-hour hackathon.

---

# 1. INSTRUCTIONS TO THE AI CODING AGENT

You are the lead software architect, senior full-stack engineer, AI engineer, DevOps engineer and UI/UX designer responsible for building PatchPilot.

You must understand this complete plan before implementing the application.

Your responsibility is not to create a static dashboard or a basic AI chatbot. Your responsibility is to build a functional software engineering intelligence product.

## Mandatory development instructions

1. Read this entire `plan.md` before writing code.
2. Inspect the existing project directory and identify existing files, frameworks, dependencies and implementation status.
3. Do not overwrite working code without understanding it.
4. Preserve the product vision and all mandatory hackathon capabilities.
5. Prioritize a functional end-to-end workflow over disconnected features.
6. Build reusable, modular components.
7. Maintain clear separation between frontend, backend, AI services, database and integrations.
8. Never display fake successful results for operations that have not actually executed.
9. When an external integration is unavailable, provide an explicitly labelled demonstration mode rather than pretending it is connected.
10. Every interactive button must perform its intended action.
11. Provide proper loading states, error handling, empty states and success feedback.
12. Use environment variables for API keys and secrets.
13. Do not expose credentials or sensitive repository information in frontend code.
14. Validate generated patches before presenting them as successfully tested.
15. Require human approval before accepting changes or creating a GitHub pull request.
16. Keep the application runnable throughout development.
17. Do not spend excessive time on decorative UI while core functionality remains incomplete.
18. Maintain a `PROGRESS.md` file and update it after completing every significant milestone.
19. Maintain a `README.md` with setup and execution instructions.
20. When blocked by an unavailable integration, implement the closest safe working alternative and continue.

**Time constraint:** The team has approximately 20 hours remaining. Allocate time intelligently. Do not attempt to build every enterprise-scale capability at production scale. Deliver a coherent, demonstrable implementation of the entire product vision, prioritizing the official requirements.

---

# 2. PRODUCT IDENTITY

## Product name

PatchPilot

## Product subtitle

Autonomous Software Intelligence, Debugging & Repair Platform.

## Product description

PatchPilot is an AI-powered software engineering platform that understands source code, identifies bugs, investigates root causes, generates focused patches, executes validation tests and helps developers safely review and approve code changes.

It combines code intelligence, Retrieval-Augmented Generation, agentic investigation, software testing, repository integration and production observability into one engineering workspace.

The platform is designed to reduce manual debugging effort, improve root-cause analysis, reuse engineering knowledge and make software repair more explainable and reliable.

## Core philosophy

UNDERSTAND → DETECT → INVESTIGATE → EXPLAIN → REPAIR → VALIDATE → APPROVE.

PatchPilot must not simply generate code.

It must demonstrate why a problem exists, identify supporting evidence, explain the proposed solution, show the exact code changes and prove what happened when tests were executed.

---

# 3. PROBLEM WE ARE SOLVING

Software engineering teams face difficulties when identifying and resolving bugs.

Problems may include:

- Logical errors.
- Runtime crashes.
- Incorrect outputs.
- Edge-case failures.
- Performance problems.
- Security vulnerabilities.
- Regression bugs.
- Production incidents.
- Failures introduced by recent code changes.

Developers often use multiple disconnected tools to investigate these problems.

Source code lives in GitHub. Documentation lives in separate knowledge bases. Logs and metrics live in monitoring platforms. Tests run in separate environments. Historical incident reports may be difficult to search.

Developers must manually connect these sources to understand what happened.

PatchPilot aims to unify this process through an AI-powered engineering intelligence system.

## Target users

1. Software developers.
2. Backend and frontend engineers.
3. Full-stack developers.
4. DevOps and SRE engineers.
5. Software engineering teams.
6. Startups maintaining multiple applications.
7. Students and developers working on complex software projects.

---

# 4. OFFICIAL HACKATHON REQUIREMENTS — NON-NEGOTIABLE

Implement every capability described in the official problem statement.

## 4.1 Code analysis

Allow users to:

- Upload source files.
- Upload a project ZIP.
- Connect a GitHub repository where integration is configured.
- Inspect the project structure.
- Identify important files.
- Extract functions and classes.
- Understand basic module dependencies.
- Identify relevant code sections.

## 4.2 Bug detection

Detect or flag:

- Logical mistakes.
- Runtime exceptions.
- Incorrect outputs.
- Edge-case problems.
- Suspicious code.
- Potential security weaknesses.
- Static-analysis findings.
- Failing tests.

Use deterministic tools whenever possible. Do not rely exclusively on LLM-generated guesses.

## 4.3 Root-cause analysis

For every detected issue, provide:

- What went wrong.
- Where it occurred.
- Why it may be occurring.
- What input or condition triggers it.
- Relevant code evidence.
- Related test evidence.
- Root-cause explanation.
- Confidence with an explanation of uncertainty.

## 4.4 Automatic patch generation

Generate focused patches.

Requirements:

- Preserve unrelated functionality.
- Display original and proposed code.
- Generate a unified diff.
- Explain each meaningful change.
- Allow users to review and reject changes.
- Avoid automatically modifying the original repository.

## 4.5 Testing and validation

Run:

- Existing project tests.
- Relevant targeted tests.
- Generated regression tests where feasible.
- Static analysis after patch generation.

Display:

- Test command.
- Execution status.
- Passed tests.
- Failed tests.
- Error output.
- Before-and-after comparison.

Do not claim a fix is successful when tests were not executed or failed.

## 4.6 Explanation and review

Provide an understandable issue report with:

- Bug description.
- File and line references.
- Root cause.
- Triggering conditions.
- Proposed patch.
- Before-and-after code.
- Test evidence.

## 4.7 Bug prioritization

Rank findings using:

- Severity.
- Potential impact.
- Reproducibility.
- Confidence.
- Security implications.

Use clear categories: Critical, High, Medium and Low.

## 4.8 Safe change history

Maintain a history of:

- Detected issues.
- Generated patches.
- Patch versions.
- Test executions.
- Accepted changes.
- Rejected changes.
- Pending approvals.

These eight capabilities take priority over every optional feature.

---

# 5. ADDITIONAL OPSMIND-INSPIRED FEATURES

In addition to the official AutoPatch requirements, integrate the following engineering intelligence capabilities.

These features extend AutoPatch into an incident investigation and operational intelligence platform.

## 5.1 Production observability

Integrate:

- OpenTelemetry.
- Prometheus.
- Grafana Loki.
- Grafana Tempo.

Collect and inspect:

- Application logs.
- Application metrics.
- Distributed traces.
- HTTP errors.
- Response latency.
- Service failures.
- Request correlation information.

For the hackathon, use a controlled instrumented demonstration application.

## 5.2 Incident intelligence

Create an incident workspace where engineers can:

- View active incidents.
- Submit an error or alert.
- Inspect related logs.
- Examine service metrics.
- Retrieve historical incidents.
- Correlate incidents with recent commits.
- Generate root-cause hypotheses.
- View suggested remediation.

## 5.3 Agentic investigation

Use LangGraph to orchestrate stateful investigation workflows.

Implement logical specialist responsibilities:

1. Triage Agent — understands the reported problem.
2. Code Analysis Agent — examines affected code and static-analysis findings.
3. Retrieval Agent — searches relevant code, documentation and incidents.
4. Root-Cause Agent — combines evidence and develops hypotheses.
5. Patch Agent — proposes a focused change.
6. Validation Agent — checks the candidate patch and test results.
7. Report Agent — prepares the final explanation.

These responsibilities may be implemented as nodes within one LangGraph workflow. Do not introduce unnecessary independent microservices or agents.

## 5.4 Engineering knowledge RAG

Index:

- Source code.
- README files.
- Technical documentation.
- Architecture documents.
- Troubleshooting guides.
- Historical incidents.
- Runbooks.
- Git commit information.
- Relevant issues and PR descriptions.

Implement:

- Document extraction.
- Code-aware chunking where feasible.
- Embeddings.
- Qdrant vector storage.
- Semantic retrieval.
- Metadata filtering.
- Evidence-grounded answers.
- Source references.

Start with dense vector retrieval. Add BM25, hybrid retrieval and reranking as time permits.

## 5.5 GitHub intelligence

Provide:

- Repository connection.
- Repository metadata.
- Commit inspection.
- Issue inspection.
- Pull request inspection.
- Changed-file inspection.
- Recent commit correlation.
- Draft pull request generation.

Prefer GitHub Apps with minimal permissions. If full GitHub App setup cannot be completed during the hackathon, support a clearly documented limited integration or repository ZIP workflow.

## 5.6 Service dependency intelligence

Extract basic relationships between modules and services.

Represent relationships using structured records initially.

Examples:

- Service A calls Service B.
- Checkout depends on Payment.
- Payment depends on Database.
- Module X imports Module Y.

Do not make a graph database a blocking requirement for the first implementation.

Neo4j can be introduced later when graph traversal provides a measurable benefit.

---

# 6. TECHNICAL STACK — PRIMARY DECISIONS

Use the following technologies unless an actual compatibility or execution blocker requires a documented alternative.

## Frontend

- Next.js.
- React.
- TypeScript.
- Tailwind CSS.
- shadcn/ui.
- Lucide icons.
- Recharts.
- Monaco Editor or a suitable diff viewer.

Reason: Structured frontend development, reusable components, responsive UI and good ecosystem support.

## Backend

- Python.
- FastAPI.
- Pydantic.
- SQLAlchemy.

Reason: Python provides a strong ecosystem for AI, RAG, code analysis and testing. FastAPI provides typed APIs and asynchronous request handling.

## Agent orchestration

- LangGraph.

Reason: Stateful workflows, conditional routing, tool execution, human approval and controlled agent collaboration.

## LLM

- OpenAI API initially.
- Model selection through environment configuration.
- Structured JSON outputs for findings and patches.

Reason: Reliable model integration with structured output capabilities.

## Embeddings

- An appropriate embedding model.
- Store vectors in Qdrant.

Reason: Learn and implement actual embedding-based retrieval rather than creating a keyword-only chatbot.

## Vector database

- Qdrant.

Reason: Vector similarity search, metadata filtering and support for hybrid retrieval workflows.

## Application database

- PostgreSQL.

Store:

- Users.
- Workspaces.
- Projects.
- Repository connections.
- Scans.
- Bugs.
- Root-cause reports.
- Patch records.
- Test runs.
- Incidents.
- Approval history.
- Audit events.

## Background jobs

- Redis.
- Celery.

Use background processing for ingestion, scans, indexing and longer-running analysis.

## Code intelligence

- Python AST.
- Tree-sitter where appropriate.
- Ruff.
- Bandit.
- Semgrep.
- Pytest.

## Execution isolation

- Docker.

Run candidate tests in restricted containers with resource limits, no privileged mode and controlled network access.

## Observability

- OpenTelemetry.
- Prometheus.
- Grafana Loki.
- Grafana Tempo.
- Grafana.

## Development and deployment

- Git.
- GitHub.
- Docker Compose.
- Environment variables.
- A deployable frontend and backend configuration.

Do not introduce Kafka, Kubernetes, Neo4j, Temporal or other additional infrastructure during the 20-hour build unless a critical requirement makes it necessary.

---

# 7. SYSTEM ARCHITECTURE

Use a modular monolith architecture for the application, with separate infrastructure containers and background workers.

Avoid premature microservices.

## High-level architecture

```text
                    PATCHPILOT WEB APPLICATION
                               |
                    Next.js + TypeScript
                               |
                         FastAPI Backend
                               |
          +--------------------+---------------------+
          |                    |                     |
     Authentication       Project Manager        API Layer
          |                    |                     |
          +--------------------+---------------------+
                               |
                       BACKGROUND WORKERS
                         Redis + Celery
                               |
              +----------------+----------------+
              |                |                |
         Repository       Document          Telemetry
          Ingestion       Ingestion          Ingestion
              |                |                |
              +----------------+----------------+
                               |
                      CODE INTELLIGENCE
                               |
                AST / Tree-sitter / Static Analysis
                               |
                        RAG ENGINE
                               |
                   Embedding Generation
                               |
                         QDRANT
                               |
                      LANGGRAPH WORKFLOW
                               |
       +-----------------------+------------------------+
       |              |              |                  |
    Triage       Retrieval      Root-Cause          Patch
      Node         Node           Node              Node
       |              |              |                  |
       +--------------+--------------+------------------+
                                      |
                               VALIDATION ENGINE
                                      |
                              ISOLATED DOCKER
                                      |
                               TEST RESULTS
                                      |
                              HUMAN APPROVAL
                                      |
                           GITHUB DRAFT PULL REQUEST
                                      |
                                AUDIT HISTORY

                  POSTGRESQL: STRUCTURED DATA
                  REDIS: JOBS AND CACHE
                  PROMETHEUS: METRICS
                  LOKI: LOGS
                  TEMPO: DISTRIBUTED TRACES
```

## Main backend modules

Organize code into logical modules:

- auth
- users
- workspaces
- projects
- repositories
- ingestion
- code_analysis
- bug_detection
- rag
- embeddings
- retrieval
- agents
- root_cause
- patch_generation
- validation
- incidents
- observability
- github
- analytics
- audit
- common

Keep modules independent enough to test, but avoid unnecessary abstraction.

---

# 8. COMPLETE USER WORKFLOW

## Workflow A — Repository analysis

```text
User logs in
     |
Creates workspace
     |
Creates project
     |
Uploads ZIP or connects GitHub
     |
Repository ingestion
     |
Project structure extraction
     |
Source code parsing
     |
Static analysis
     |
Bug identification
     |
Bug prioritization
     |
Persist scan findings
     |
Display findings dashboard
```

## Workflow B — RAG

```text
Source files / README / Documents / Incidents
                       |
                  Extraction
                       |
                    Parsing
                       |
                   Chunking
                       |
                   Embeddings
                       |
                    Qdrant
                       |
                User investigation
                       |
                Query embedding
                       |
                Vector retrieval
                       |
                Relevant evidence
                       |
             Grounded LLM explanation
                       |
              Source references
```

## Workflow C — Root-cause investigation

```text
Developer reports a problem
              |
        Triage and planning
              |
      Identify required evidence
              |
    +---------+----------+
    |         |          |
  Code      RAG       Telemetry
    |         |          |
    +---------+----------+
              |
     Recent Git changes
              |
       Evidence correlation
              |
     Root-cause hypothesis
              |
     Confidence and caveats
              |
      Investigation report
```

## Workflow D — Repair and validation

```text
Root-cause hypothesis
          |
     Patch generation
          |
    Unified code diff
          |
     Human review
          |
  Apply candidate patch
          |
    Isolated sandbox
          |
   Run relevant tests
          |
  Static analysis again
          |
   Compare test results
          |
    Display validation
          |
  Accept or reject patch
          |
  Optional draft GitHub PR
          |
      Audit history
```

---

# 9. DATABASE DESIGN

Use PostgreSQL for structured application information.

Recommended entities:

| Table | Purpose |
|---|---|
| users | User accounts |
| workspaces | Tenant/workspace information |
| workspace_members | User access |
| projects | Software projects |
| repositories | GitHub and uploaded repository metadata |
| scans | Scan execution records |
| bugs | Detected issues |
| bug_evidence | Supporting code and document evidence |
| patches | Proposed code changes |
| test_runs | Validation execution records |
| incidents | Incident information |
| commits | Repository commit metadata |
| pull_requests | PR records |
| approvals | Human decisions |
| audit_logs | Important actions |

Use workspace and project identifiers to scope all queries.

Use JSONB for flexible analysis metadata where appropriate.

Qdrant should store vector points with metadata such as:

- workspace_id
- project_id
- source_type
- source_id
- file_path
- language
- chunk_index
- content
- commit_sha where relevant

Never rely on the vector database alone for tenant authorization. Enforce access control in the backend.

---

# 10. BUG REPORT DATA CONTRACT

All detected findings should follow a consistent structure.

```json
{
  "id": "BUG-001",
  "title": "Invalid input validation",
  "description": "Negative values are accepted.",
  "file_path": "app/calculator.py",
  "line_start": 12,
  "line_end": 18,
  "category": "logical_error",
  "severity": "high",
  "confidence": 0.92,
  "root_cause": "Input values are not checked against the allowed range.",
  "trigger_conditions": [
    "Negative marks",
    "Marks greater than 100"
  ],
  "evidence": [],
  "suggested_fix": "Validate marks before calculation.",
  "patch_id": null,
  "status": "detected"
}
```

Confidence must represent an explicitly defined assessment, not an arbitrary percentage presented as measured accuracy.

Use separate labels for:

- Static analyzer finding.
- Reproduced failure.
- LLM hypothesis.
- Test-verified defect.

This distinction is essential for trustworthy reporting.

---

# 11. USER INTERFACE REQUIREMENTS

Build a polished, responsive web application.

## Main navigation

1. Overview.
2. Projects.
3. Repository Intelligence.
4. Bug Analysis.
5. AI Investigation.
6. Incidents.
7. Observability.
8. Patch Center.
9. Validation Center.
10. Pull Requests.
11. Knowledge Base.
12. Analytics.
13. Settings.

## Overview dashboard

Show:

- Total projects.
- Scans performed.
- Detected bugs.
- Critical/high-priority findings.
- Open incidents.
- Patches awaiting review.
- Tests passed/failed.
- Recent activity.

Only show data backed by actual database records or clearly labelled demo fixtures.

## Repository Intelligence

Show:

- Repository details.
- Branch and commit.
- File explorer.
- File metadata.
- Language distribution.
- Static analysis findings.

## Bug Analysis

Show:

- Bug list.
- Severity.
- Confidence.
- File path.
- Line number.
- Explanation.
- Root cause.
- Trigger conditions.
- Suggested patch.

Allow filtering by severity, category and status.

## AI Investigation

Show:

- Investigation question.
- Execution steps.
- Retrieved evidence.
- Sources and file references.
- Root-cause hypotheses.
- Uncertainty.
- Recommended actions.

## Patch Center

Show:

- Original code.
- Proposed code.
- Unified diff.
- Explanation of changes.
- Review status.
- Approve/reject actions.

## Validation Center

Show:

- Execution status.
- Test command.
- Test output.
- Passed/failed count.
- Static analysis comparison.
- Validation result.

## Incident Intelligence

Show:

- Incident list.
- Severity.
- Affected service.
- Error information.
- Related traces.
- Related logs.
- Related commits.
- Historical incident matches.

---

# 12. UI/UX DESIGN SYSTEM

## Theme name

Porcelain & Signal.

## Visual personality

Premium, editorial, intelligent, approachable, engineering-focused.

Do not use the standard dark-purple AI dashboard aesthetic.

## Color tokens

```css
:root {
  --background: #F7F5EF;
  --surface: #FFFFFF;
  --foreground: #18243A;
  --primary: #4666D5;
  --primary-foreground: #FFFFFF;
  --coral: #FF765E;
  --mint: #B8DCCB;
  --amber: #E6B85C;
  --border: #DCE3EE;
  --muted: #39475D;
}
```

## Design rules

- Light mode by default.
- Warm ivory page background.
- White cards and panels.
- Ink navy headings.
- Cobalt primary actions.
- Coral reserved for critical alerts.
- Mint for successful operations.
- Amber for warnings.
- Subtle borders and restrained shadows.
- Avoid excessive gradients.
- Avoid unnecessary glassmorphism.
- Avoid excessive rounded cards.
- Prioritize readability and information density.

## Typography

- Manrope for headings.
- Inter for general interface text.
- JetBrains Mono for code.

## Responsive behavior

The application must work on desktop and laptop screens. Important pages should remain usable on smaller screens.

---

# 13. SECURITY REQUIREMENTS

Security is a mandatory engineering requirement.

1. Use secure authentication.
2. Enforce workspace-level authorization.
3. Never expose API keys in frontend code.
4. Store secrets in environment variables or a secure secret store.
5. Redact secrets from logs and LLM prompts.
6. Validate uploaded files and archive paths.
7. Prevent path traversal and archive extraction attacks.
8. Treat repository files, comments, documentation and logs as untrusted inputs.
9. Protect against prompt injection.
10. Use tool allowlists.
11. Do not give agents unrestricted shell access.
12. Do not expose production credentials to agents.
13. Run tests in restricted containers.
14. Disable privileged Docker execution.
15. Set CPU, memory and time limits.
16. Restrict sandbox networking.
17. Require approval before accepting patches.
18. Record important actions in audit history.
19. Apply rate limits to sensitive endpoints.
20. Never execute untrusted code directly on the application host.

The default production integration must be read-only.

Patch generation and testing must operate on isolated copies.

---

# 14. EVALUATION AND QUALITY

Build a basic evaluation framework.

Measure:

## Retrieval

- Recall@K.
- Precision@K where ground truth is available.
- MRR.
- nDCG.

## Bug detection

- Correct findings.
- False positives.
- Reproducible defects.
- Severity classification quality.

## Root-cause analysis

- Agreement with known root cause.
- Evidence relevance.
- Citation correctness.
- Unsupported claim rate.

## Patch validation

- Patch application success.
- Targeted test result.
- Regression test result.
- Static analysis after patch.

Do not invent evaluation results.

Create a small known-bug demonstration dataset and use it to measure actual behavior.

---

# 15. TWENTY-HOUR HACKATHON EXECUTION PLAN

The implementation order is critical.

Do not attempt to implement every optional capability before establishing a working product.

## Stage 1 — Foundation (Hour 0–1.5)

- Inspect existing workspace.
- Create project structure.
- Initialize Git.
- Configure Next.js.
- Configure FastAPI.
- Configure environment files.
- Configure Docker Compose.
- Establish frontend/backend communication.

**Deliverable:** Running application skeleton.

## Stage 2 — UI and database (Hour 1.5–3)

- Implement application layout.
- Build sidebar and navigation.
- Build overview dashboard.
- Build project creation.
- Configure PostgreSQL.
- Create database models.
- Add initial API endpoints.

**Deliverable:** Navigable application with persistent projects.

## Stage 3 — Repository ingestion (Hour 3–5)

- Implement ZIP upload.
- Add file validation.
- Extract repository structure.
- Parse supported source files.
- Display file tree.
- Add GitHub integration if credentials are available.

**Deliverable:** User can provide and inspect an actual code project.

## Stage 4 — Bug detection (Hour 5–7)

- Integrate Ruff.
- Integrate Bandit.
- Add Semgrep if available.
- Run available project tests.
- Normalize findings.
- Implement bug prioritization.
- Store findings in PostgreSQL.

**Deliverable:** Real scan findings displayed in the application.

## Stage 5 — RAG (Hour 7–9)

- Implement extraction.
- Implement chunking.
- Generate embeddings.
- Configure Qdrant.
- Implement vector retrieval.
- Store source metadata.
- Add evidence-backed explanations.

**Deliverable:** Working RAG over project code and documentation.

## Stage 6 — Root-cause and patch generation (Hour 9–11)

- Connect LLM.
- Implement structured bug reports.
- Build root-cause analysis.
- Generate focused code changes.
- Produce unified diffs.
- Build patch review UI.

**Deliverable:** User can investigate a finding and inspect a proposed patch.

## Stage 7 — Validation and approval (Hour 11–13)

- Create isolated test workspace.
- Apply candidate patches to copies.
- Execute targeted tests.
- Compare baseline and patched results.
- Record validation history.
- Implement accept/reject actions.

**Deliverable:** Working patch-to-validation workflow.

## Stage 8 — Agent orchestration (Hour 13–14.5)

- Build LangGraph workflow.
- Implement triage.
- Implement retrieval.
- Implement root-cause reasoning.
- Implement patch and validation nodes.
- Add workflow status and error handling.

**Deliverable:** Integrated investigation workflow.

## Stage 9 — Observability and incidents (Hour 14.5–16.5)

- Instrument demonstration application.
- Configure OpenTelemetry.
- Configure Prometheus.
- Configure Loki.
- Configure Tempo.
- Retrieve selected telemetry.
- Implement incident creation.
- Correlate a known incident with code changes.

**Deliverable:** Demonstrable incident investigation workflow.

## Stage 10 — GitHub, polish and demo (Hour 16.5–18.5)

- Complete GitHub workflow where credentials permit.
- Implement draft PR generation.
- Complete approval history.
- Polish dashboard.
- Fix major integration bugs.
- Improve loading and error states.

**Deliverable:** Cohesive working product.

## Stage 11 — Final verification (Hour 18.5–20)

- Test complete workflow from start to finish.
- Verify every official requirement.
- Prepare seeded demonstration project.
- Check environment variables.
- Prepare backup demonstration data.
- Capture actual screenshots.
- Complete README.
- Prepare presentation and demo script.

**Deliverable:** Hackathon-ready application.

The above is a target schedule, not a reason to skip verification. If a stage takes longer, protect the official bug detection, root-cause, patch and test workflow first.

---

# 16. PRIORITY RULES UNDER TIME PRESSURE

## P0 — Must work

- Upload source files or ZIP.
- Understand project structure.
- Detect actual issues.
- Explain root causes.
- Generate focused patches.
- Display before/after changes.
- Execute tests.
- Show test evidence.
- Prioritize bugs.
- Maintain patch history.
- Accept/reject patches.

## P1 — Strong differentiators

- GitHub integration.
- Qdrant vector RAG.
- Evidence references.
- LangGraph investigation.
- Historical incident retrieval.
- Basic log/metric/trace integration.
- Draft PR creation.

## P2 — Advanced extensions

- BM25 and hybrid retrieval.
- Cross-encoder reranking.
- Advanced GraphRAG.
- Complex autonomous remediation.
- Advanced analytics.
- Multiple independently deployed agents.
- Kubernetes deployment automation.
- High-volume streaming telemetry.

P2 items must not delay P0 completion.

The architecture must leave room for these extensions.

---

# 17. DEMONSTRATION SCENARIO

Create a sample application named ShopSphere.

It should include:

- FastAPI backend.
- Checkout endpoint.
- Payment service.
- Inventory service.
- PostgreSQL integration where feasible.
- Tests.
- Documentation.
- Git history.
- A deliberately introduced bug.

## Recommended bug

Introduce a payment timeout or input-validation bug with a known, reproducible trigger.

For example:

A checkout operation accepts invalid payment input or incorrectly handles a downstream payment timeout.

Ensure the bug is reproducible with a test before demonstrating its repair.

## Demo sequence

1. Open PatchPilot.
2. Create a ShopSphere project.
3. Upload its source ZIP or connect the GitHub repository.
4. Run a scan.
5. Show detected bugs.
6. Open an issue.
7. Show the exact affected code.
8. Explain the root cause.
9. Retrieve related documentation or code evidence through RAG.
10. Generate a proposed patch.
11. Show the original and proposed code.
12. Review the patch.
13. Execute the original failing test.
14. Apply the candidate patch in isolation.
15. Execute the test again.
16. Show the result.
17. Accept or reject the change.
18. Show the change history.
19. If operational integration is available, demonstrate a related incident using logs, metrics and traces.
20. Finish with measurable evaluation results.

Do not fabricate a successful result. Prepare a known-good demonstration and a backup path.

---

# 18. SUCCESS CRITERIA

PatchPilot is considered ready for hackathon presentation when:

- A user can provide a real source project.
- The application can inspect its structure.
- At least one genuine bug or analyzer finding can be identified.
- The bug report contains an understandable explanation.
- A root-cause hypothesis includes evidence.
- A focused patch can be generated.
- The proposed change is visible as a diff.
- The original project remains unchanged until approval.
- Tests can run against a candidate copy.
- Results are displayed accurately.
- Severity and confidence are visible.
- Change history is recorded.
- The UI is usable and responsive.
- The application has a convincing end-to-end demonstration.

Additional OpsMind-inspired capabilities should be demonstrated where implemented.

---

# 19. FUTURE PRODUCT ROADMAP

After the hackathon, extend PatchPilot with:

- Advanced GraphRAG using Neo4j.
- More sophisticated service dependency graphs.
- High-volume telemetry ingestion using Kafka.
- Durable agent workflows using Temporal.
- Kubernetes-based deployment.
- Advanced sandbox isolation with gVisor or Firecracker.
- Multi-language code analysis.
- More advanced vulnerability detection.
- Automated regression test generation.
- Improved retrieval evaluation.
- Cross-project engineering knowledge.
- Multi-team collaboration.
- Production incident integrations.
- Human-approved rollback and deployment workflows.

These are future capabilities, not blockers for the hackathon.

---

# 20. FINAL INSTRUCTION TO ANTIGRAVITY

You must treat this file as the master source of truth for the project.

Begin by:

1. Inspecting the existing workspace.
2. Creating a concise implementation plan.
3. Identifying available dependencies and credentials.
4. Setting up the application.
5. Implementing the first end-to-end vertical slice.
6. Updating PROGRESS.md.
7. Running tests after each significant implementation.
8. Continuing through the remaining milestones.

Do not stop after producing a plan or mockup.

Do not build a generic AI chatbot.

Do not build a dashboard where buttons are decorative.

Do not generate fake bug reports or fake test results.

Do not remove official hackathon requirements to simplify development.

If a feature cannot be completed within the available time, document the limitation and provide a safe, working fallback.

Always prefer real, demonstrable functionality over impressive but non-functional complexity.

The final result must be a coherent product that judges can operate, understand and evaluate.

## THE FINAL PRODUCT VISION

PatchPilot should help a developer move from:

"I know something is wrong with my software."

To:

"I understand exactly what is wrong, why it happened, what code needs to change, and whether the proposed repair actually works."

**UNDERSTAND THE CODE. FIND THE BUG. PROVE THE CAUSE. GENERATE THE FIX. VALIDATE THE REPAIR. KEEP THE DEVELOPER IN CONTROL.**

END OF MASTER PROJECT PLAN.
