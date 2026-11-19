# FIXORA Diagnostic Report: Full-Stack Codebase Inspection

**Date:** 2026-11-19  
**Investigator:** Principal Software Architect & QA Automation Team  
**Scope:** Complete Codebase, Database Schema, API Contracts, UI State, and Integration Pipelines  

---

## 1. Executive Summary

A comprehensive line-by-line audit of the FIXORA platform was conducted. While the application architecture, design system (Warm Minimal + Signal Orange), and core models are well-structured, several critical defects, data integrity issues, and disconnected features were identified:

1. **Repository Deletion Failure:** There is no `DELETE /api/repositories/{id}` endpoint in the backend router, causing HTTP 405/404 when users attempt to delete a repository.
2. **Dashboard Discrepancies & Undefined Values:** `DashboardPage.tsx` references `stats.resolvedBugs` and `stats.activeInvestigations`, but the backend schema provides `autonomousRepairs` and `pendingReview`. Furthermore, `DashboardService.get_stats` used fallback constants (`or 12`, `or 46`, `or 8`, `autonomous_repairs=38`), fabricating metrics even when database counts are zero.
3. **AI Investigation Failures:** `InvestigationService.create_and_run` hardcodes `repository_id = "payment-service"`. If a user creates an investigation on a custom project without `payment-service`, the foreign key constraint on `Bug.repository_id` triggers an `IntegrityError`. `InvestigationCreate` schema lacks `repositoryId`.
4. **Duplicate Navigation & Pages:** Both `/code-repairs` and `/autopatch` render the exact same component (`AutoPatchPage`), and sidebar menu items contain hardcoded static badge counts (`12`, `46`, `3`, `2`, `8`).
5. **Database Contamination & Test Artifacts:** Running `pytest` directly targeted `fixora.db` without database isolation, accumulating duplicate test records (multiple `Checkout Cart Service` projects and `sample-microservice` repositories).
6. **Static & Unconnected Postmortem/Health Pages:** `ReportsPage.tsx` contains hardcoded static HTML with a non-functional "Export PDF" button (no backend endpoint existed). `HealthPage.tsx` displays hardcoded numbers (`38`, `18 mins`, `100%`) without querying the database.

---

## 2. Feature-by-Feature Diagnostic Matrix

| Feature / Page | Frontend Status | Backend Status | Dependencies | Observed Problem | Root Cause (Code Evidence) | Proposed Repair |
|---|---|---|---|---|---|---|
| **Repository Management** (`/repositories`) | WORKING | PARTIAL (Missing DELETE) | PostgreSQL/SQLite `repositories` table | Deleting a repository fails with error | `backend/app/api/v1/repositories.py` has no `@router.delete("/{id}")` route. Service lacks cascading deletion. | Add `@router.delete("/{id}")` in FastAPI, implement cascade deletion in `RepositoryService`, and update UI list. |
| **Dashboard** (`/dashboard`) | BROKEN (undefined metrics) | PARTIAL (Fabricated counts) | `DashboardService`, DB aggregation | "Autonomous Repairs" and "Pending Review" show `undefined`; repo count suspicious | `DashboardPage.tsx:163,178` reads `stats.resolvedBugs` instead of `stats.autonomousRepairs`. `DashboardService.py:12-28` uses `or 12`, `or 46` fallbacks. | Align frontend property names to `autonomousRepairs` & `pendingReview`. Remove constant fallbacks in `DashboardService`. |
| **AI Investigations** (`/investigations`) | BROKEN (hardcoded project/repo) | BROKEN (Foreign key failure) | LangGraph, DB `investigations`, `bugs`, `patches` | Launching an investigation fails on custom projects | `investigation_service.py:64` defaults `repo_name = "payment-service"`. `Bug.repository_id` foreign key fails if `payment-service` doesn't exist. `InvestigationCreate` schema lacks `repository_id`. | Add `repository_id` to `InvestigationCreate`. Dynamically select project's repo or validate existence. Handle empty repos gracefully. |
| **Code Repairs vs AutoPatch** (`/code-repairs`, `/autopatch`) | DUPLICATED | WORKING (Patches API) | `patches`, `test_runs`, Docker Sandbox | Both routes render the same page; sidebar has redundant entries | `App.tsx:112-125` routes both `/code-repairs` and `/autopatch` to `<AutoPatchPage />`. | Differentiate: `AutoPatchPage` handles patch creation, interactive diff, sandbox test run, and PR gate. Create `CodeRepairsPage` as dedicated historical audit log. |
| **Incident Intelligence** (`/incidents`) | WORKING | WORKING | `incidents` table, telemetry | Works with seeded data, but lacks direct investigation dispatch from incident card | `IncidentsPage.tsx` resolves incidents, but lacks "Investigate Incident" linking to `investigationService.create` with `incidentId`. | Wire "Investigate" action on incident cards to launch LangGraph investigation referencing the incident. |
| **Postmortems & Reports** (`/reports`) | STATIC MOCK | MISSING | `investigations`, `incidents`, PDF generator | "Export PDF" button does nothing; report text is hardcoded | `ReportsPage.tsx` has static JSX with no `onClick` or API integration. No `/api/reports` or `/api/reports/{id}/export-pdf` routes exist. | Implement `reports.py` router with dynamic list and real streaming PDF generation. Connect frontend with real download handler. |
| **Engineering Health** (`/analytics/health`) | STATIC MOCK | MISSING | `bugs`, `patches`, `test_runs`, `incidents` | Displays hardcoded `38`, `18 mins`, `100%` | `HealthPage.tsx` renders static cards with no API call. | Add `GET /api/dashboard/health` returning empirical calculations (sandbox pass rate, MTTR, resolution rate). Wire `HealthPage.tsx`. |
| **Observability (Logs, Metrics, Traces)** | PARTIAL | WORKING | Telemetry tables, OpenTelemetry pipeline | When no telemetry is sent, shows raw empty or stale demo logs | `LogsPage.tsx`, `MetricsPage.tsx`, `TracesPage.tsx` lack clear "No Telemetry Connected" onboarding state. | Add informative empty state with instructions for hooking up OpenTelemetry collectors. |
| **Sidebar Navigation** | STATIC BADGES | N/A | React Router | Shows hardcoded badge numbers (`12`, `46`, `3`, `2`, `8`) | `Sidebar.tsx:51-56` has hardcoded integers in `NAV_SECTIONS`. | Remove deceptive static badges or drive them dynamically from active project stats. |

---

## 3. Database State & Cleanup Plan

### Current Table Analysis (`fixora.db`):
- `repositories`: 20 rows (contains 7 duplicated `sample-microservice` and 5 duplicated `cart-service` created by automated tests, plus 2 copies of user repo `AI_Research_paper_exp`).
- `projects`: 7 rows (contains 6 duplicate `Checkout Cart Service` rows from `test_backend.py`).
- `workspaces`: 20 rows (polluted by pytest fixture calls).

### Required Actions:
1. **Database Backup:** Create timestamped snapshot `fixora.db.backup_<timestamp>`.
2. **Pytest Isolation:** Configure `conftest.py` to use a distinct `test_fixora.db` so test runs never pollute the development/production database.
3. **Safe Cleanup Script:** Deduplicate repositories, clean orphaned test workspaces/projects while preserving:
   - User account `alex.vance@fixora.dev`
   - Real user repository `Uday-MS/AI_Research_paper_exp`
   - Standard reference project `ShopSphere Platform` and its seeded schema.
