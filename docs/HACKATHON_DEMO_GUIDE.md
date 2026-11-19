# FIXORA — Hackathon Demonstration & Presentation Guide

> **The Definitive 5-to-7 Minute Stage Script & 2-Minute Emergency Fallback Plan**  
> *Engineered for maximum judge impact, clear value delivery, and flawless live execution.*

---

## 1. Master 5-to-7 Minute Live Demo Script

```
+-----------------------------------------------------------------------------------+
|                        5-TO-7 MINUTE DEMO TIMELINE                                |
+-----------------------------------------------------------------------------------+
| Part 1 (1:00) : The 2 AM Outage Problem & Central Command Dashboard               |
| Part 2 (1:00) : Connecting a Repository & AST Dual-Index Ingestion                |
| Part 3 (1:00) : Live Telemetry Ingestion & Incident Alert Triage                  |
| Part 4 (1:30) : LangGraph 7-Agent Autonomous Investigation in Action              |
| Part 5 (1:00) : AutoPatch Studio, Unified Diff & Docker Sandbox Test Run          |
| Part 6 (0:30) : Mandatory Human Approval Gate & GitHub PR Generation              |
| Part 7 (0:30) : Incident Postmortem & Native PDF Export Delivery                  |
+-----------------------------------------------------------------------------------+
```

---

### Part 1: The Problem & Dashboard Command Center (1:00)
* **Screen:** Open `http://localhost:5173/dashboard`
* **Speaker Action:** Point to the live KPI cards at the top of the dashboard.
* **Talking Script:**
  > *"Judges, imagine it's 2:00 AM. A microservice in your production cluster starts failing with 500 errors. Today, your on-call engineer wakes up, logs into Datadog, sifts through hundreds of error traces, navigates Git history to find the author, pulls down the repository, and tries to write a fix while under immense pressure. The industry average Mean Time to Resolution is over 4 hours.
  >
  > Welcome to **FIXORA** — the Autonomous Code Repair and Incident Intelligence Platform that closes this loop automatically. 
  > 
  > Here on the Dashboard, you see real metrics aggregating our live repositories, active incidents, and automated repairs. Notice that our MTTR is calculated empirically from real system events. Everything you see here is live and connected directly to our asynchronous backend."*

---

### Part 2: Repository Connection & AST Ingestion (1:00)
* **Screen:** Navigate to `http://localhost:5173/repositories`
* **Action:** Click the **"Connect Repository"** button. Point out the two tabs: **GitHub URL** and **Upload ZIP Archive**.
* **Talking Script:**
  > *"FIXORA operates across the entire development lifecycle. Connecting a repository is seamless. An engineer can paste a GitHub repository URL or drag and drop a project ZIP archive.
  >
  > Notice what happens behind the scenes: FIXORA doesn't just treat code as flat text. Our ingestion pipeline performs an Abstract Syntax Tree (AST) walk, extracts classes, methods, and call dependencies, and creates a dual-index: 384-dimensional dense vectors stored in Qdrant, alongside an Okapi BM25 lexical index and a Neo4j dependency call graph.
  >
  > Furthermore, for uploaded archives, our backend features built-in Zip Slip path traversal defenses, preventing malicious archives from escaping bounded directories."*

---

### Part 3: Operational Incident Triage (1:00)
* **Screen:** Navigate to `http://localhost:5173/incidents`
* **Action:** Click on the top **`P1 - Critical`** incident (e.g. `ZeroDivisionError in Checkout Calculation` or `Unhandled KeyError in Payment Webhook`).
* **Talking Script:**
  > *"Now let's look at post-deployment mode. When a live service throws an exception, our OpenTelemetry ingestion endpoints receive the log stream.
  > 
  > Here in the Incident Command Center, FIXORA has automatically extracted the traceback, clustered identical signatures to prevent alert fatigue, and isolated the offending file path and line number.
  >
  > Rather than paging a developer to manually reproduce this, we simply click **'Investigate'**."*

---

### Part 4: Multi-Agent Autonomous Investigation (1:30)
* **Screen:** Navigate to `http://localhost:5173/investigations`
* **Action:** Click on the active investigation. Open the **Investigation Detail Modal**.
* **Talking Script:**
  > *"This is where FIXORA is fundamentally different from a standard conversational chatbot. We don't ask an LLM to guess a solution in a chat window. 
  >
  > We orchestrate a deterministic, 7-stage state machine using LangGraph:
  > 1. Our **Triage Agent** normalizes the stack trace and scopes the defect.
  > 2. Our **Retrieval Agent** executes Hybrid RAG—combining dense vector search, BM25 lexical keyword matching, and Neo4j call graph traversal using Reciprocal Rank Fusion ($k=60$).
  > 3. Our **RCA Agent** formulates a deterministic hypothesis isolating the exact failing AST node.
  > 4. Our **Diagnostic Agent** designs an isolated regression test spec.
  > 5. Our **AutoPatch Agent** synthesizes a surgical unified diff.
  > 6. Our **Validation Agent** tests the fix inside an isolated Docker sandbox.
  > 7. And our **Postmortem Agent** compiles a comprehensive report."*

---

### Part 5: AutoPatch Studio & Sandboxed Verification (1:00)
* **Screen:** Navigate to `http://localhost:5173/autopatch`
* **Action:** Highlight the side-by-side code diff viewer. Click the **"Run Sandbox Tests"** button.
* **Talking Script:**
  > *"Welcome to AutoPatch Studio. Here, the engineer can inspect the exact unified diff synthesized by the platform. Green lines indicate surgical defensive checks added, with red lines showing the removed defect.
  >
  > Crucially, FIXORA never trusts LLM code blindly. When I click **'Run Sandbox Tests'**, our Docker runner mounts this diff into an ephemeral container with strict resource limits: non-root user, 2GB memory ceiling, disabled networking, and a 15-second execution timeout.
  >
  > Look at the execution log right here in the UI: Pytest runs, the assertions execute, and we get an exit code 0 confirming the fix passes all regression tests!"*

---

### Part 6: Mandatory Human Approval Gate & GitHub PR (0:30)
* **Screen:** Stay on `http://localhost:5173/autopatch`
* **Action:** Show that the **"Create Pull Request"** button requires approval. Click **"Approve Patch"**, then click **"Create GitHub PR"**.
* **Talking Script:**
  > *"In enterprise environments, autonomous agents must never commit directly to production branches. FIXORA enforces a strict **Human-in-the-Loop Approval Gate**. 
  >
  > If an API caller attempts to generate a PR without approval, our backend rejects it with an HTTP 400 Bad Request. Once our engineer clicks 'Approve Patch', the gate unlocks, and with one click on 'Create GitHub PR', FIXORA pushes to an isolated feature branch and opens a verified Draft Pull Request on GitHub!"*

---

### Part 7: Postmortem Report & Binary PDF Export (0:30)
* **Screen:** Navigate to `http://localhost:5173/reports`
* **Action:** Click on the incident report, then click the **"Export PDF"** button. Show the downloaded PDF file in the browser tray.
* **Talking Script:**
  > *"Finally, no incident lifecycle is complete without learning from failure. FIXORA automatically compiles an executive postmortem detailing the incident timeline, root cause, and preventative action items. 
  >
  > With a single click on 'Export PDF', our backend streams a native, binary `%PDF-1.4` document ready for executive review and compliance archiving.
  >
  > In under 5 minutes, FIXORA took an unhandled production crash, investigated the root cause, synthesized and tested an AST diff in Docker, opened a GitHub PR, and published an audit-ready postmortem. That is the future of autonomous engineering."*

---

## 2. Emergency 2-Minute Fallback Demo Script (Time Crunch / Wi-Fi Glitch)

If presenting under strict 2-minute time constraints:
1. **(0:00 - 0:30) Dashboard & Problem:**  
   *"Software downtime costs \$300K/hour because engineers spend 70% of MTTR diagnosing root causes. FIXORA closes this loop autonomously. Here on our live dashboard, you see real-time incident and remediation health metrics."*
2. **(0:30 - 1:00) Incident to 7-Agent LangGraph:**  
   *(Click Incidents $\rightarrow$ Investigations)*  
   *"When telemetry detects an unhandled exception, our LangGraph 7-stage multi-agent pipeline activates, combining dense vector search, BM25 lexical ranking, and Neo4j dependency call-graphs to isolate the root cause."*
3. **(1:00 - 1:30) AutoPatch Studio & Docker Sandbox:**  
   *(Click AutoPatch Studio $\rightarrow$ Run Sandbox Tests)*  
   *"In AutoPatch Studio, you see the exact unified diff. We validate this patch inside an isolated Docker container with memory and timeout limits. Tests pass with exit code 0."*
4. **(1:30 - 2:00) Human Gate & PDF Export:**  
   *(Click Approve Patch $\rightarrow$ Reports $\rightarrow$ Export PDF)*  
   *"Zero unvetted code reaches production: our mandatory human approval gate governs PR creation, and our native binary PDF generator downloads an instant incident postmortem for compliance. That is FIXORA."*
