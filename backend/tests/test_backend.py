import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from app.main import app

@pytest.mark.asyncio
async def test_health_check():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.get("/api/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "online"
        assert data["service"] == "FIXORA Core API"

@pytest.mark.asyncio
async def test_auth_login():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.post("/api/auth/login", json={
            "email": "alex.vance@fixora.dev",
            "password": "Fixora2026!"
        })
        assert response.status_code == 200
        data = response.json()
        assert "data" in data
        assert "accessToken" in data["data"]
        assert data["data"]["user"]["email"] == "alex.vance@fixora.dev"

@pytest.mark.asyncio
async def test_auth_me():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        # First login
        login_res = await ac.post("/api/auth/login", json={
            "email": "alex.vance@fixora.dev",
            "password": "Fixora2026!"
        })
        token = login_res.json()["data"]["accessToken"]

        # Call /api/auth/me
        me_res = await ac.get("/api/auth/me", headers={"Authorization": f"Bearer {token}"})
        assert me_res.status_code == 200
        assert me_res.json()["data"]["email"] == "alex.vance@fixora.dev"

@pytest.mark.asyncio
async def test_workspaces_crud():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        # List workspaces
        res = await ac.get("/api/workspaces")
        assert res.status_code == 200
        data = res.json()
        assert data["total"] >= 1
        assert any(w["slug"] == "core-infra-prod" for w in data["data"])

        # Create workspace
        create_res = await ac.post("/api/workspaces", json={
            "name": "Staging Cluster",
            "plan": "pro"
        })
        assert create_res.status_code == 200
        assert create_res.json()["data"]["name"] == "Staging Cluster"

@pytest.mark.asyncio
async def test_projects_crud():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        res = await ac.get("/api/projects")
        assert res.status_code == 200
        assert len(res.json()["data"]) >= 1

@pytest.mark.asyncio
async def test_repositories_endpoints():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        # List repos
        res = await ac.get("/api/repositories")
        assert res.status_code == 200
        repos = res.json()["data"]
        assert len(repos) >= 4
        assert any(r["id"] == "payment-service" for r in repos)

        # Get repo
        get_res = await ac.get("/api/repositories/payment-service")
        assert get_res.status_code == 200
        assert get_res.json()["data"]["name"] == "payment-service"

        # Get files
        files_res = await ac.get("/api/repositories/payment-service/files")
        assert files_res.status_code == 200
        assert len(files_res.json()["data"]) >= 1

        # Sync repo
        sync_res = await ac.post("/api/repositories/payment-service/sync")
        assert sync_res.status_code == 200

@pytest.mark.asyncio
async def test_bugs_endpoints():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        res = await ac.get("/api/bugs")
        assert res.status_code == 200
        bugs = res.json()["data"]
        assert len(bugs) >= 1
        assert any(b["id"] == "BUG-1842" for b in bugs)

@pytest.mark.asyncio
async def test_patches_endpoints():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        # List patches
        res = await ac.get("/api/patches")
        assert res.status_code == 200
        patches = res.json()["data"]
        assert len(patches) >= 1

        patch_id = patches[0]["id"]
        # Run tests
        test_res = await ac.post(f"/api/patches/{patch_id}/run-tests")
        assert test_res.status_code == 200
        assert test_res.json()["data"]["status"] == "passed"

        # Approve
        app_res = await ac.post(f"/api/patches/{patch_id}/approve")
        assert app_res.status_code == 200
        assert app_res.json()["data"]["status"] == "approved"

        # Create PR
        pr_res = await ac.post(f"/api/patches/{patch_id}/create-pr")
        assert pr_res.status_code == 200
        assert pr_res.json()["data"]["prNumber"] == 409

@pytest.mark.asyncio
async def test_incidents_endpoints():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        res = await ac.get("/api/incidents")
        assert res.status_code == 200
        assert len(res.json()["data"]) >= 1

@pytest.mark.asyncio
async def test_dashboard_stats():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        res = await ac.get("/api/dashboard/stats")
        assert res.status_code == 200
        data = res.json()["data"]
        assert data["totalRepositories"] >= 4
        assert data["testsPassRate"] >= 0.0

@pytest.mark.asyncio
async def test_dashboard_health():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        res = await ac.get("/api/dashboard/health")
        assert res.status_code == 200
        data = res.json()["data"]
        assert "sandboxPassRate" in data
        assert "totalRepositories" in data

@pytest.mark.asyncio
async def test_reports_endpoints():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        res = await ac.get("/api/reports")
        assert res.status_code == 200
        data = res.json()["data"]
        assert len(data) >= 1
        rep_id = data[0]["id"]

        pdf_res = await ac.get(f"/api/reports/{rep_id}/export-pdf")
        assert pdf_res.status_code == 200
        assert pdf_res.headers["content-type"] == "application/pdf"
        assert pdf_res.content.startswith(b"%PDF-1.4")

@pytest.mark.asyncio
async def test_repository_deletion_endpoint():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        # Create a temporary repository
        c_res = await ac.post("/api/repositories", json={
            "name": "temp-test-repo-to-delete",
            "url": "https://github.com/acme/temp-test-repo-to-delete",
            "branch": "main",
            "source": "github"
        })
        assert c_res.status_code == 200
        temp_id = c_res.json()["data"]["id"]

        # Delete it
        d_res = await ac.delete(f"/api/repositories/{temp_id}")
        assert d_res.status_code == 200
        assert d_res.json()["data"]["deleted"] is True

        # Verify 404 on get
        g_res = await ac.get(f"/api/repositories/{temp_id}")
        assert g_res.status_code == 404

@pytest.mark.asyncio
async def test_settings_endpoint():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        res = await ac.get("/api/settings")
        assert res.status_code == 200
        data = res.json()["data"]
        assert data["dockerMemoryLimit"] == "2048 MB"
        assert "diagnostics" in data

@pytest.mark.asyncio
async def test_settings_validate_endpoint():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        res = await ac.get("/api/settings/validate")
        assert res.status_code == 200
        data = res.json()["data"]
        assert "environmentFile" in data
        assert "database" in data
        assert "jwtAuthentication" in data
        assert data["database"]["connected"] is True
        assert data["jwtAuthentication"]["keyLengthChars"] >= 32

@pytest.mark.asyncio
async def test_autopatch_studio_endpoints():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        # 1. Fetch repositories
        r_res = await ac.get("/api/repositories")
        assert r_res.status_code == 200
        repos = r_res.json()["data"]
        assert len(repos) > 0
        repo_id = repos[0]["id"]

        # 2. Test Issues endpoint
        issues_res = await ac.get(f"/api/repositories/{repo_id}/issues?state=all")
        assert issues_res.status_code == 200
        assert "data" in issues_res.json()

        # 3. Test Patch Research
        res_res = await ac.post("/api/patches/research", json={
            "repositoryId": repo_id,
            "issueNumber": 1,
            "description": "Fix IndexError when list is empty"
        })
        assert res_res.status_code == 200
        res_data = res_res.json()["data"]
        assert res_data["issueNumber"] == 1
        assert "rootCause" in res_data
        assert "affectedFiles" in res_data

        target_file = res_data["affectedFiles"][0]["path"] if res_data["affectedFiles"] else "src/utils.py"

        # 4. Test Patch Draft
        draft_res = await ac.post("/api/patches/draft", json={
            "repositoryId": repo_id,
            "issueNumber": 1,
            "title": "Fix IndexError when list is empty",
            "filePath": target_file,
            "userGuidance": "Add defensive check before accessing index 0"
        })
        assert draft_res.status_code == 200
        draft_data = draft_res.json()["data"]
        assert "unifiedDiff" in draft_data
        assert "id" in draft_data
        assert draft_data["status"] == "draft"

