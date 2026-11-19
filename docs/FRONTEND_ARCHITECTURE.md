# FIXORA Frontend Architecture & Stitch Design System

## Overview
FIXORA is built using **React 19, TypeScript, Vite, and Tailwind CSS**, strictly adhering to the **Google Stitch "Warm Minimal + Signal Orange"** engineering design system.

## Design Tokens & Theme Fidelity
- **Typography:**
  - Headings: `Manrope` (600, 700, 800)
  - Interface Body: `Inter` (400, 500, 600)
  - Code & Telemetry: `JetBrains Mono` (400, 500, 600)
- **Palette (Warm Minimal + Signal Orange):**
  - Background: `#FFF8F1`
  - Surface Lowest (Cards): `#FFFFFF`
  - Surface Low: `#F9F3EB`
  - Surface Container High: `#EDE7E0`
  - Primary Accent (Signal Orange): `#F28C28`
  - Deep Text: `#1D1B17`
  - Inverse Surface (Terminal & Diff): `#33302B`
  - Critical Outage: `#BA1A1A` / Container: `#FFDAD6`

## Implemented Screens (16 Core Areas)
1. **Landing & Case Study (`/landing`, `/`)**: Architectural showcase, CLI quick-install, live Case Study #1842.
2. **Authentication & Onboarding (`/login`, `/onboarding`)**: Secure workspace login and multi-step onboarding wizard.
3. **Engineering Control Dashboard (`/dashboard`)**:
   - Zone 0: Telemetry strip with region and cluster uptime.
   - Zone 1: Welcome cockpit with live diagnostics launcher.
   - Zone 2: 4 Bento KPI metric cards with AST index health and anomaly distribution.
   - Zone 3: Two-column operational core (Connected Repositories table + MTTR reduction histogram).
   - Zone 4: Active SEV-1 incident box (#1842) with 5-agent pipeline and recent activity feed.
4. **Connected Repositories Management (`/repositories`)**: Grid of monitored codebases, AST node statistics, branch tracking, and sync status.
5. **Repository Architecture & File Explorer (`/repositories/:id`)**: Dual-pane file hierarchy browser and AST symbol viewer.
6. **AI Multi-Agent Investigation Workspace (`/investigations`, `/investigations/:id`)**:
   - 5-Agent pipeline: Triage -> Retrieval -> Root Cause -> Patch Synthesis -> Docker Validation.
   - Root-cause correlation with GitHub PRs and commit hashes.
7. **AutoPatch Studio & Repair Workspace (`/autopatch`, `/code-repairs`)**:
   - Unified split AST code diff viewer.
   - Isolated Docker container execution verification.
   - 1-click GitHub Draft PR generation.
8. **Issues & Bug Prioritization (`/bugs`)**: Ranked bug database by severity, confidence, and detection source.
9. **Production Incident Intelligence (`/incidents`)**: Active incident triage and automated postmortem initiation.
10. **Application Logs (`/observability/logs`)**: Real-time Loki-compatible streaming log viewer with filter queries.
11. **Telemetry Metrics (`/observability/metrics`)**: Prometheus error rates, p99 latencies, and connection pool saturation.
12. **Distributed Traces (`/observability/traces`)**: Tempo distributed trace hierarchy across services.
13. **RAG Knowledge Base (`/knowledge`)**: Qdrant vector index over technical runbooks and architecture docs.
14. **Semantic RAG Search (`/rag-search`)**: Evidence-grounded similarity query engine with source attribution.
15. **Engineering Health Analytics (`/analytics/health`)**: Reliability metrics, MTTR reduction, and non-regressive validation rates.
16. **Settings & Integrations (`/settings`, `/integrations`)**: Configurable sandbox resource limits, API keys, and GitHub/Otel connectors.

## Reusable Components
- `Button` (primary, secondary, ghost, danger, outline)
- `Badge` (critical, warning, success, accent, info, outline)
- `Card`, `CardHeader`, `CardTitle`
- `StatusDot` (healthy, warning, critical, active, idle)
- `DataTable` (generic, typed, sortable, responsive)
- `MetricCard` (Bento KPI metrics with trends and micro-bars)
- `SearchInput` (with keyboard shortcut hints)
- `DiffViewer` (AST unified before-and-after code diffs)
- `EmptyState`, `LoadingState`, `ErrorState`
- `ConnectRepoModal` (GitHub repo URL + ZIP drag-and-drop)
