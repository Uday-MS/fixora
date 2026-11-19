import os
import pytest_asyncio
from sqlalchemy import select

# Ensure tests run against an isolated test database, preserving fixora.db
os.environ["DATABASE_URL"] = "sqlite+aiosqlite:///./test_fixora.db"
os.environ["ENVIRONMENT"] = "development"
os.environ["ADMIN_EMAIL"] = "testadmin@fixora.dev"
os.environ["ADMIN_PASSWORD"] = "TestAdminPass2026!"

from app.core.config import settings
settings.DATABASE_URL = "sqlite+aiosqlite:///./test_fixora.db"
settings.ENVIRONMENT = "development"
settings.ADMIN_EMAIL = "testadmin@fixora.dev"
settings.ADMIN_PASSWORD = "TestAdminPass2026!"

from app.db.session import init_db, AsyncSessionLocal
from app.core.security import get_password_hash
from app.models.user import User
from app.models.organization import Organization, OrganizationMember
from app.models.workspace import Workspace
from app.models.project import Project
from app.models.repository import Repository
from app.models.bug import Bug
from app.models.patch import Patch
from app.models.test_run import TestRun
from app.models.incident import Incident
from app.models.investigation import Investigation
from app.models.knowledge import KnowledgeDocument

async def seed_test_suite_fixtures():
    """Seeds test benchmark state into isolated test database."""
    async with AsyncSessionLocal() as session:
        user_check = await session.execute(select(User).limit(1))
        if user_check.scalars().first():
            return

        # 1. User
        admin_user = User(
            id="usr_demo_001",
            email="testadmin@fixora.dev",
            name="Test Administrator",
            hashed_password=get_password_hash("TestAdminPass2026!"),
            role="admin",
            avatar_url=None,
            is_active=True,
        )
        session.add(admin_user)
        await session.flush()

        # 2. Org & Workspace
        org = Organization(
            id="org_demo_001",
            name="Acme Global Engineering",
            slug="acme-corp",
        )
        session.add(org)
        await session.flush()

        member = OrganizationMember(
            id="mem_demo_001",
            organization_id=org.id,
            user_id=admin_user.id,
            role="owner",
        )
        session.add(member)

        workspace = Workspace(
            id="ws_demo_001",
            organization_id=org.id,
            name="Core Infra / Prod",
            slug="core-infra-prod",
            plan="enterprise",
            member_count=6,
        )
        session.add(workspace)
        await session.flush()

        # 3. Project
        project = Project(
            id="proj_demo_001",
            workspace_id=workspace.id,
            name="ShopSphere Platform",
            description="High-throughput e-commerce microservices with autonomous SRE monitoring.",
            status="active",
        )
        session.add(project)
        await session.flush()

        # 4. Repositories
        repo1 = Repository(
            id="payment-service",
            project_id=project.id,
            name="payment-service",
            full_name="acme/payment-service",
            url="https://github.com/acme/payment-service",
            branch="main",
            source="github",
            language="Go 1.22",
            health_status="critical",
            issue_count=3,
            commit_count=184,
            file_count=42,
            files_tree=[
                {"path": "src/gateway/pool_manager.go", "name": "pool_manager.go", "type": "file", "size": 14200, "language": "Go"},
                {"path": "src/gateway/circuit_breaker.go", "name": "circuit_breaker.go", "type": "file", "size": 8400, "language": "Go"},
                {"path": "src/handlers/checkout.go", "name": "checkout.go", "type": "file", "size": 22100, "language": "Go"},
                {"path": "tests/integration/pool_test.go", "name": "pool_test.go", "type": "file", "size": 18400, "language": "Go"},
            ]
        )
        repo2 = Repository(
            id="checkout-platform",
            project_id=project.id,
            name="checkout-platform",
            full_name="acme/checkout-platform",
            url="https://github.com/acme/checkout-platform",
            branch="release-2.4",
            source="github",
            language="Rust 1.76",
            health_status="warning",
            issue_count=2,
            commit_count=98,
            file_count=35,
        )
        repo3 = Repository(
            id="authentication-api",
            project_id=project.id,
            name="authentication-api",
            full_name="acme/authentication-api",
            url="https://github.com/acme/authentication-api",
            branch="main",
            source="github",
            language="Node 20 / TS",
            health_status="healthy",
            issue_count=0,
            commit_count=112,
            file_count=28,
        )
        repo4 = Repository(
            id="user-management",
            project_id=project.id,
            name="user-management",
            full_name="acme/user-management",
            url="https://github.com/acme/user-management",
            branch="staging",
            source="github",
            language="Python 3.11",
            health_status="healthy",
            issue_count=1,
            commit_count=76,
            file_count=24,
        )
        session.add_all([repo1, repo2, repo3, repo4])
        await session.flush()

        # 5. Bugs
        bug1 = Bug(
            id="BUG-1842",
            project_id=project.id,
            repository_id=repo1.id,
            title="Connection Pool Timeout Starvation in AcquireConnection",
            description="Channel acquire blocks indefinitely under burst load with missing acquire timeout context.",
            file_path="src/gateway/pool_manager.go",
            line_start=140,
            line_end=148,
            category="runtime_exception",
            severity="critical",
            confidence=0.984,
            root_cause="PR #312 removed the timeout fallback, causing thread deadlock under >150 concurrent transactions.",
            trigger_conditions=["Concurrent checkout operations > 150", "Payment DB latency spike > 500ms"],
            status="patch_generated",
            source="static_analyzer",
        )
        session.add(bug1)
        await session.flush()

        # 6. Patches & TestRuns
        patch1 = Patch(
            id="patch_1842",
            bug_id=bug1.id,
            project_id=project.id,
            repository_id=repo1.id,
            title="Inject Adaptive Timeout & Dynamic Fallback in AcquireConnection",
            description="AST surgical mutation adding select case with exponential timeout and pool saturation metric.",
            file_path="src/gateway/pool_manager.go",
            original_code="case conn := <-p.idlePool:\n    return conn, nil",
            proposed_code="case conn := <-p.idlePool:\n    return p.verifyHealth(ctx, conn)\ncase <-time.After(p.acquireTimeout):\n    telemetry.RecordPoolSaturation()\n    return p.spawnDynamicFallback(ctx)",
            unified_diff="--- a/src/gateway/pool_manager.go\n+++ b/src/gateway/pool_manager.go\n@@ -140,5 +140,8 @@\n   select {\n-  case conn := <-p.idlePool:\n-    return conn, nil\n+  case conn := <-p.idlePool:\n+    return p.verifyHealth(ctx, conn)\n+  case <-time.After(p.acquireTimeout):\n+    telemetry.RecordPoolSaturation()\n+    return p.spawnDynamicFallback(ctx)\n   case <-ctx.Done():\n     return nil, ctx.Err()\n   }",
            explanation="1. Injects acquireTimeout channel selection to prevent thread hanging.\n2. Calls spawnDynamicFallback() to serve queries from warm read replicas.\n3. Records Prometheus saturation metric.",
            status="approved",
            pr_number=409,
            pr_url="https://github.com/acme/payment-service/pull/409",
        )
        session.add(patch1)
        await session.flush()

        test_run1 = TestRun(
            id="tr_1842",
            patch_id=patch1.id,
            command="go test -v ./tests/integration/...",
            status="passed",
            total_tests=18,
            passed_tests=18,
            failed_tests=0,
            output="=== RUN   TestPoolStarvationUnderLoad\n=== RUN   TestCircuitBreakerFallback\n--- PASS: 18/18 integration tests in 1m 18s\nP99 Latency stabilized at 41ms",
            duration=78.2,
        )
        session.add(test_run1)

        # 7. Incidents
        inc1 = Incident(
            id="INC-1842",
            project_id=project.id,
            title="payment-service HTTP 503 Gateway Timeout Outage",
            description="Customer checkout flows failing with HTTP 503 gateway timeouts due to database connection exhaustion.",
            severity="sev1",
            status="active",
            affected_service="payment-service",
            error_message="fatal: AcquireConnection pool starvation timeout (threshold 5000ms exceeded)",
            related_commits=["a7b9c1d"],
            related_bug_ids=[bug1.id],
        )
        session.add(inc1)

        # 8. Investigation
        inv1 = Investigation(
            id="INV-1842",
            project_id=project.id,
            bug_id=bug1.id,
            incident_id=inc1.id,
            question="Why is payment-service throwing HTTP 503 errors under checkout spikes?",
            status="in_progress",
            current_stage="validation",
            confidence=0.984,
            patch_id=patch1.id,
            findings="PR #312 accidentally omitted the connection wait timeout channel.",
            root_cause_hypothesis="Connection pool starvation caused by unbounded channel acquire under >150 transactions.",
            stages=[
                {"num": "01", "name": "Triage Agent", "status": "completed", "desc": "Ingested Sentry HTTP 503 stack trace"},
                {"num": "02", "name": "Retrieval Agent", "status": "completed", "desc": "Correlated PR #312 commit a7b9c1d"},
                {"num": "03", "name": "Root Cause Agent", "status": "completed", "desc": "Isolated line 142 unhandled channel acquire"},
                {"num": "04", "name": "AST Patch Agent", "status": "completed", "desc": "Synthesized exponential backoff & dynamic fallback"},
                {"num": "05", "name": "Validation Agent", "status": "running", "desc": "Executing 18 integration tests in isolated Docker container"},
            ]
        )
        session.add(inv1)

        # 9. Knowledge Docs
        doc1 = KnowledgeDocument(
            id="doc_001",
            project_id=project.id,
            title="Payment Gateway Runbook & Failover Protocols",
            source_type="runbook",
            content="Standard operating procedure for connection pool saturation and circuit breaker degradation.",
            file_path="docs/runbooks/payment_gateway.md",
            chunk_count=24,
            status="indexed",
        )
        doc2 = KnowledgeDocument(
            id="doc_002",
            project_id=project.id,
            title="Database Replica Connection Pooling Architecture",
            source_type="architecture",
            content="Go database pooling guidelines: drivers must configure acquireTimeout with exponential backoff.",
            file_path="docs/architecture/db_pooling.md",
            chunk_count=18,
            status="indexed",
        )
        session.add_all([doc1, doc2])

        await session.commit()

@pytest_asyncio.fixture(scope="session", autouse=True)
async def setup_test_db():
    await init_db()
    await seed_test_suite_fixtures()
