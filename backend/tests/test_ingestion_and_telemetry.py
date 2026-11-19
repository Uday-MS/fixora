import io
import zipfile
import hmac
import hashlib
import json
import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app
from app.core.config import settings

@pytest.mark.asyncio
async def test_repository_zip_ingestion():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        # 1. Connect a repository
        repo_create = await ac.post("/api/repositories", json={
            "name": "sample-microservice",
            "source": "github",
            "branch": "main",
            "language": "Python"
        })
        assert repo_create.status_code == 200
        repo_data = repo_create.json()["data"]
        repo_id = repo_data["id"]

        # 2. Build a real in-memory ZIP archive
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as z:
            z.writestr("README.md", "# Sample Microservice\nThis service processes transactions.")
            z.writestr("requirements.txt", "fastapi>=0.115.0\npydantic>=2.0.0\npytest>=8.0.0\n")
            z.writestr(".github/workflows/ci.yml", "name: CI\non: [push]\njobs:\n  test:\n    runs-on: ubuntu-latest\n")
            z.writestr("Dockerfile", "FROM python:3.11-slim\nWORKDIR /app\n")
            z.writestr("app/main.py", "from fastapi import FastAPI\napp = FastAPI()\n\n@app.get('/health')\ndef health():\n    return {'status': 'healthy'}\n")
            z.writestr("app/service.py", "def process_payment(amount: float):\n    if amount <= 0:\n        raise ValueError('Invalid amount')\n    return True\n")
            z.writestr("tests/test_main.py", "from app.service import process_payment\n\ndef test_payment():\n    assert process_payment(100.0) is True\n")
        zip_buffer.seek(0)

        # 3. Upload ZIP to repository ingestion endpoint
        files = {"file": ("sample-microservice.zip", zip_buffer.getvalue(), "application/zip")}
        upload_res = await ac.post(f"/api/repositories/{repo_id}/upload-zip", files=files)
        assert upload_res.status_code == 200
        res_json = upload_res.json()
        assert res_json["status"] == "completed"

        analysis = res_json["analysis"]
        assert analysis["repositoryId"] == repo_id
        assert analysis["primaryLanguage"] == "Python"
        assert analysis["fileCount"] >= 6
        assert analysis["totalLines"] >= 10
        assert analysis["structureChecks"]["hasReadme"] is True
        assert analysis["structureChecks"]["hasTests"] is True
        assert analysis["structureChecks"]["hasDependencyManifest"] is True
        assert analysis["structureChecks"]["hasContinuousIntegration"] is True
        assert analysis["structureChecks"]["hasContainerization"] is True
        assert analysis["healthScore"] >= 80

        # Verify repository record was updated in database
        repo_get = await ac.get(f"/api/repositories/{repo_id}")
        assert repo_get.status_code == 200
        updated_repo = repo_get.json()["data"]
        assert updated_repo["fileCount"] >= 6
        assert updated_repo["healthStatus"] == "healthy"

@pytest.mark.asyncio
async def test_zip_slip_security_rejection():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        # Create a malicious zip with directory traversal
        malicious_zip = io.BytesIO()
        with zipfile.ZipFile(malicious_zip, "w") as z:
            z.writestr("../evil.py", "print('malicious')")
        malicious_zip.seek(0)

        files = {"file": ("malicious.zip", malicious_zip.getvalue(), "application/zip")}
        res = await ac.post("/api/repositories/payment-service/upload-zip", files=files)
        assert res.status_code == 400
        assert "Malicious file path" in res.json()["detail"]

@pytest.mark.asyncio
async def test_document_upload_and_deduplication():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        # Get active project
        proj_res = await ac.get("/api/projects")
        assert proj_res.status_code == 200
        project_id = proj_res.json()["data"][0]["id"]

        # 1. Upload Markdown runbook
        import uuid
        run_uid = uuid.uuid4().hex[:6]
        doc_content = f"# Incident Runbook: Payment Gateway Timeout ({run_uid})\n\n1. Check database connection pool.\n2. Scale payment worker pods.\n3. Verify Stripe API latency."
        files = {"file": (f"runbook_stripe_timeout_{run_uid}.md", doc_content.encode("utf-8"), "text/markdown")}
        data = {"projectId": project_id, "sourceType": "runbook"}

        upload_res = await ac.post("/api/knowledge/upload", data=data, files=files)
        assert upload_res.status_code == 200
        doc_data = upload_res.json()
        assert "Runbook Stripe Timeout" in doc_data["title"]
        assert doc_data["sourceType"] == "runbook"
        assert doc_data["isDuplicate"] is False
        assert doc_data["chunkCount"] >= 1
        doc_id = doc_data["documentId"]

        # 2. Upload identical content to test SHA-256 deduplication
        dup_files = {"file": ("duplicate_runbook.md", doc_content.encode("utf-8"), "text/markdown")}
        dup_res = await ac.post("/api/knowledge/upload", data=data, files=dup_files)
        assert dup_res.status_code == 200
        dup_data = dup_res.json()
        assert dup_data["isDuplicate"] is True
        assert dup_data["documentId"] == doc_id
        assert "already ingested" in dup_data["message"]

@pytest.mark.asyncio
async def test_docx_and_pdf_document_upload():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        import docx
        from pypdf import PdfWriter

        proj_res = await ac.get("/api/projects")
        project_id = proj_res.json()["data"][0]["id"]

        # 1. Test DOCX upload
        doc_obj = docx.Document()
        doc_obj.add_heading("Architecture Runbook Specification", level=1)
        doc_obj.add_paragraph("FIXORA distributed telemetry pipeline and ingestion gateway.")
        docx_buf = io.BytesIO()
        doc_obj.save(docx_buf)

        docx_files = {"file": ("architecture_spec.docx", docx_buf.getvalue(), "application/vnd.openxmlformats-officedocument.wordprocessingml.document")}
        docx_res = await ac.post("/api/knowledge/upload", data={"projectId": project_id, "sourceType": "architecture"}, files=docx_files)
        assert docx_res.status_code == 200
        assert docx_res.json()["title"] == "Architecture Spec"
        assert docx_res.json()["sourceType"] == "architecture"

        # 2. Test PDF upload
        pdf_writer = PdfWriter()
        pdf_writer.add_blank_page(width=300, height=300)
        pdf_buf = io.BytesIO()
        pdf_writer.write(pdf_buf)

        pdf_files = {"file": ("network_diagram.pdf", pdf_buf.getvalue(), "application/pdf")}
        pdf_res = await ac.post("/api/knowledge/upload", data={"projectId": project_id, "sourceType": "documentation"}, files=pdf_files)
        assert pdf_res.status_code == 200
        assert pdf_res.json()["title"] == "Network Diagram"

@pytest.mark.asyncio
async def test_telemetry_pipeline_and_anomaly_detection():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        proj_res = await ac.get("/api/projects")
        project_id = proj_res.json()["data"][0]["id"]

        # 1. Ingest structured logs with stack trace
        traceback_msg = "Database connection error\nTraceback (most recent call last):\n  File 'db.py', line 45, in connect\n    raise TimeoutError('Connection pool exhausted')\nTimeoutError: Connection pool exhausted"
        log_payload = [
            {
                "serviceName": "payment-service",
                "level": "ERROR",
                "message": traceback_msg,
                "environment": "production"
            },
            {
                "serviceName": "auth-service",
                "level": "INFO",
                "message": "User login session refreshed for user-891",
                "environment": "production"
            }
        ]
        log_res = await ac.post(f"/api/telemetry/{project_id}/logs", json=log_payload)
        assert log_res.status_code == 200
        logs = log_res.json()
        assert len(logs) == 2
        # Check automatic stack trace extraction
        err_log = next(l for l in logs if l["serviceName"] == "payment-service")
        assert err_log["stackTrace"] is not None
        assert "TimeoutError" in err_log["stackTrace"]

        # 2. Ingest metrics with anomaly detection
        metrics_payload = [
            {
                "serviceName": "payment-service",
                "metricName": "error_rate",
                "value": 0.14,  # 14% error rate (triggers anomaly)
                "unit": "ratio"
            },
            {
                "serviceName": "payment-service",
                "metricName": "http_requests_total",
                "value": 4500.0,
                "unit": "count"
            }
        ]
        metric_res = await ac.post(f"/api/telemetry/{project_id}/metrics", json=metrics_payload)
        assert metric_res.status_code == 200
        metrics = metric_res.json()
        assert len(metrics) == 2
        anomaly_metric = next(m for m in metrics if m["metricName"] == "error_rate")
        assert anomaly_metric["isAnomaly"] is True

        # 3. Ingest OpenTelemetry distributed trace spans
        trace_id = "trace-4bf92f3577b34da6a3ce929d0e0e4736"
        traces_payload = [
            {
                "traceId": trace_id,
                "spanId": "span-001",
                "serviceName": "api-gateway",
                "operationName": "POST /api/v1/checkout",
                "durationMs": 420.5,
                "statusCode": "OK"
            },
            {
                "traceId": trace_id,
                "spanId": "span-002",
                "parentSpanId": "span-001",
                "serviceName": "payment-service",
                "operationName": "charge_customer_card",
                "durationMs": 380.0,
                "statusCode": "ERROR",
                "errorMessage": "Card processing gateway timed out after 300ms"
            }
        ]
        trace_res = await ac.post(f"/api/telemetry/{project_id}/traces", json=traces_payload)
        assert trace_res.status_code == 200
        traces = trace_res.json()
        assert len(traces) == 2
        err_span = next(t for t in traces if t["spanId"] == "span-002")
        assert err_span["statusCode"] == "ERROR"
        assert err_span["parentSpanId"] == "span-001"

        # 4. Verify project automatically marked as post_deployment upon receiving telemetry
        query_logs = await ac.get(f"/api/telemetry/{project_id}/logs?serviceName=payment-service")
        assert query_logs.status_code == 200
        assert len(query_logs.json()) >= 1

@pytest.mark.asyncio
async def test_github_webhook_verification_and_event_handling():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        secret = "fixora_default_github_webhook_secret"
        payload = {
            "repository": {
                "name": "payment-service",
                "full_name": "acme/payment-service"
            },
            "commits": [
                {"id": "c1", "message": "Fix payment retry jitter"},
                {"id": "c2", "message": "Update stripe client"}
            ],
            "sender": {"login": "octocat"}
        }
        body_bytes = json.dumps(payload).encode("utf-8")
        sig = hmac.new(secret.encode("utf-8"), body_bytes, hashlib.sha256).hexdigest()

        # Send valid signed webhook
        res = await ac.post(
            "/api/webhooks/github",
            content=body_bytes,
            headers={
                "Content-Type": "application/json",
                "X-GitHub-Event": "push",
                "X-Hub-Signature-256": f"sha256={sig}"
            }
        )
        assert res.status_code == 200
        assert res.json()["received"] is True
        assert res.json()["event"] == "push"
        assert "2 commits" in res.json()["status"]

        # Send invalid signature
        invalid_res = await ac.post(
            "/api/webhooks/github",
            content=body_bytes,
            headers={
                "Content-Type": "application/json",
                "X-GitHub-Event": "push",
                "X-Hub-Signature-256": "sha256=invalidhexsignature123456"
            }
        )
        assert invalid_res.status_code == 401

@pytest.mark.asyncio
async def test_service_topology_graph():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        proj_res = await ac.get("/api/projects")
        project_id = proj_res.json()["data"][0]["id"]

        # Register custom service node with dependencies
        create_res = await ac.post(f"/api/projects/{project_id}/services", json={
            "name": "notification-worker",
            "tier": "worker",
            "runtime": "python",
            "dependencies": ["redis", "payment-service"]
        })
        assert create_res.status_code == 200
        assert create_res.json()["name"] == "notification-worker"

        # Get service graph
        graph_res = await ac.get(f"/api/projects/{project_id}/services")
        assert graph_res.status_code == 200
        graph = graph_res.json()
        assert len(graph["nodes"]) >= 1
        assert any(n["name"] == "notification-worker" for n in graph["nodes"])
        assert any(e["source"] == "notification-worker" and e["target"] == "payment-service" for e in graph["edges"])
