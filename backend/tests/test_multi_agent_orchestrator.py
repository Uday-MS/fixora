import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app
from app.orchestrator.sandbox.runner import sandbox_runner
from app.orchestrator.github.pr_manager import github_pr_manager
from app.orchestrator.graph import run_incident_investigation

def test_sandbox_runner_allowlist_and_safety():
    # 1. Disallowed command injection blocked
    res_disallowed = sandbox_runner.execute_validation(
        file_path="app.py",
        original_code="print('ok')",
        proposed_code="print('patched')",
        test_command="rm -rf /; echo hacked",
    )
    assert res_disallowed["tests_passed"] is False
    assert res_disallowed["security_verdict"] == "COMMAND_DISALLOWED"
    assert "Security violation" in res_disallowed["output"]

    # 2. Syntax check catches malformed Python code
    res_syntax = sandbox_runner.execute_validation(
        file_path="service.py",
        original_code="def run(): pass",
        proposed_code="def run( malformed syntax {}:",
        test_command="python -m unittest",
    )
    assert res_syntax["syntax_valid"] is False
    assert res_syntax["security_verdict"] == "SYNTAX_CHECK_FAILED"
    assert "SyntaxError" in res_syntax["output"]

    # 3. Safe allowlisted execution succeeds
    valid_code = "def add(a, b): return a + b"
    test_code = """
import unittest
from service import add

class TestAdd(unittest.TestCase):
    def test_add(self):
        self.assertEqual(add(2, 3), 5)

if __name__ == '__main__':
    unittest.main()
"""
    res_valid = sandbox_runner.execute_validation(
        file_path="service.py",
        original_code="def add(a, b): return 0",
        proposed_code=valid_code,
        test_code=test_code,
        test_command="python -m unittest",
    )
    assert res_valid["applied_cleanly"] is True
    assert res_valid["syntax_valid"] is True
    assert res_valid["tests_passed"] is True
    assert res_valid["passed_tests"] >= 1
    assert res_valid["security_verdict"] == "ALLOWED_SAFE_SANDBOX"

def test_github_pr_manager_human_approval_gate():
    # 1. Deny PR creation without explicit approval
    with pytest.raises(PermissionError) as exc_info:
        github_pr_manager.create_draft_pull_request(
            repository_name="payment-service",
            patch_id="patch-12345678",
            patch_title="Fix DB pool timeout",
            patch_description="Added bounded acquire timeout",
            unified_diff="--- a/pool.py\n+++ b/pool.py\n",
            validation_result={"tests_passed": True, "total_tests": 2, "passed_tests": 2},
            rca_result={"root_cause": "Exhausted connection pool"},
            human_approved=False,
        )
    assert "Human approval gate failed" in str(exc_info.value)

    # 2. Allow PR creation with explicit approval
    pr = github_pr_manager.create_draft_pull_request(
        repository_name="payment-service",
        patch_id="patch-12345678",
        patch_title="Fix DB pool timeout",
        patch_description="Added bounded acquire timeout",
        unified_diff="--- a/pool.py\n+++ b/pool.py\n",
        validation_result={"tests_passed": True, "total_tests": 2, "passed_tests": 2, "duration_seconds": 0.04},
        rca_result={"root_cause": "Exhausted connection pool", "evidence_strength": "STRONG", "confirmed_vs_hypothesis": "CONFIRMED"},
        human_approved=True,
        approved_by="Staff Engineer",
    )
    assert pr["status"] == "draft_created"
    assert pr["isDraft"] is True
    assert pr["branchName"].startswith("fixora/repair-")
    assert pr["branchName"] != "main"
    assert "Staff Engineer" in pr["approvedBy"]
    assert pr["prNumber"] == 409

@pytest.mark.asyncio
async def test_full_langgraph_incident_orchestration():
    error_context = {
        "message": "Database connection pool exhausted under 500 concurrent checkout requests",
        "service_name": "payment-service",
        "stack_trace": "Traceback (most recent call last):\n  File 'pool.py', line 14, in acquire\nTimeoutError: Connection pool exhausted",
        "environment": "production",
    }

    final_state = await run_incident_investigation(
        error_context=error_context,
        project_id="proj_demo_001",
        repository_id="payment-service",
        incident_id="inc_demo_001",
        operating_mode="post_deployment",
    )

    # 1. Triage Agent verification
    triage = final_state["triage_result"]
    assert triage["severity"] == "CRITICAL"
    assert triage["errorCategory"] == "database_connection_pool_exhaustion"
    assert triage["affectedService"] == "payment-service"

    # 2. Retrieval Agent verification
    evidence = final_state["retrieved_evidence"]
    assert isinstance(evidence, list)
    graph_ctx = final_state["graph_context"]
    assert len(graph_ctx) >= 1

    # 3. RCA Agent verification
    rca = final_state["rca_result"]
    assert rca["evidence_strength"] == "STRONG"
    assert rca["confirmed_vs_hypothesis"] == "CONFIRMED"
    assert "services/payment/pool.py" in rca["affected_file"]
    assert "c48a92f" in rca["related_commits"]

    # 4. Diagnostic Agent verification
    diagnostic = final_state["diagnostic_result"]
    assert diagnostic["hypothesis_verified"] is True

    # 5. AutoPatch Agent verification
    patch = final_state["patch_result"]
    assert "unified_diff" in patch
    assert "--- a/" in patch["unified_diff"]
    assert "+++ b/" in patch["unified_diff"]
    assert "ConnectionTimeoutError" in patch["proposed_code"]

    # 6. Validation Agent verification
    validation = final_state["validation_result"]
    assert validation["applied_cleanly"] is True
    assert validation["syntax_valid"] is True
    assert validation["tests_passed"] is True
    assert validation["passed_tests"] >= 1

    # 7. Postmortem Agent verification
    postmortem = final_state["postmortem_report"]
    assert "CRITICAL" in postmortem["title"]
    assert len(postmortem["timeline"]) >= 4
    assert len(postmortem["preventiveActions"]) >= 2
    assert final_state["approval_status"] == "pending_human_review"

@pytest.mark.asyncio
async def test_pre_deployment_investigation_mode():
    pre_deploy_context = {
        "message": "SyntaxError: invalid syntax in data serializer",
        "service_name": "data-pipeline",
        "stack_trace": "SyntaxError: invalid syntax at line 42",
        "environment": "development",
    }

    final_state = await run_incident_investigation(
        error_context=pre_deploy_context,
        project_id="proj_demo_001",
        repository_id="data-pipeline",
        operating_mode="pre_deployment",
    )

    triage = final_state["triage_result"]
    assert triage["operatingMode"] == "pre_deployment"
    assert triage["errorCategory"] == "code_syntax_validation"
    assert final_state["approval_status"] == "pending_human_review"

@pytest.mark.asyncio
async def test_investigation_api_and_db_persistence():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        # Trigger investigation via API
        payload = {
            "projectId": "proj_demo_001",
            "question": "What caused the database pool exhaustion in payment-service?",
            "incidentId": "inc_demo_001",
        }
        res = await ac.post("/api/investigations", json=payload)
        assert res.status_code == 200
        inv_data = res.json()["data"]

        assert inv_data["status"] == "completed"
        assert inv_data["patchId"] is not None
        assert "pool" in inv_data["rootCauseHypothesis"].lower() or "connection" in inv_data["rootCauseHypothesis"].lower()

        # Query created patch
        patch_id = inv_data["patchId"]
        patch_res = await ac.get(f"/api/patches/{patch_id}")
        assert patch_res.status_code == 200
        patch = patch_res.json()["data"]
        assert patch["status"] == "draft"
        assert "ConnectionTimeoutError" in patch["proposedCode"]

        # Human Approval Gate: Create PR while draft should be rejected
        fail_pr = await ac.post(f"/api/patches/{patch_id}/create-pr")
        assert fail_pr.status_code == 400
        assert "Human approval required" in fail_pr.json()["detail"]

        # Approve patch
        app_res = await ac.post(f"/api/patches/{patch_id}/approve")
        assert app_res.status_code == 200
        assert app_res.json()["data"]["status"] == "approved"

        # Now Create PR succeeds
        pr_res = await ac.post(f"/api/patches/{patch_id}/create-pr")
        assert pr_res.status_code == 200
        assert pr_res.json()["data"]["prNumber"] == 409
        assert "github.com" in pr_res.json()["data"]["prUrl"]
