"""
FIXORA Backend Diagnostic Script
Tests every endpoint using FastAPI TestClient to identify exact errors.
"""
import sys
import os
import json
import traceback

# Set up path
sys.path.insert(0, os.path.dirname(__file__))

from httpx import ASGITransport, AsyncClient
import asyncio

async def run_diagnostics():
    # Import app after path setup
    from app.main import app
    
    results = []
    
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # 1. Health check
        print("=" * 60)
        print("FIXORA BACKEND DIAGNOSTIC REPORT")
        print("=" * 60)
        
        # Helper to test an endpoint
        async def test_endpoint(method, url, label, json_body=None, headers=None):
            try:
                if method == "GET":
                    r = await client.get(url, headers=headers)
                elif method == "POST":
                    r = await client.post(url, json=json_body, headers=headers)
                elif method == "PATCH":
                    r = await client.patch(url, json=json_body, headers=headers)
                elif method == "DELETE":
                    r = await client.delete(url, headers=headers)
                
                status = r.status_code
                try:
                    body = r.json()
                except:
                    body = r.text[:500]
                
                result = {
                    "label": label,
                    "method": method,
                    "url": url,
                    "status": status,
                    "ok": 200 <= status < 300,
                    "body_preview": str(body)[:300],
                }
                results.append(result)
                
                icon = "✅" if result["ok"] else "❌"
                print(f"\n{icon} [{status}] {method} {url}")
                print(f"   Label: {label}")
                if not result["ok"]:
                    print(f"   Body: {str(body)[:300]}")
                return r
            except Exception as e:
                result = {
                    "label": label,
                    "method": method,
                    "url": url,
                    "status": "EXCEPTION",
                    "ok": False,
                    "body_preview": f"{type(e).__name__}: {str(e)}\n{traceback.format_exc()[:500]}",
                }
                results.append(result)
                print(f"\n💥 [EXCEPTION] {method} {url}")
                print(f"   Label: {label}")
                print(f"   Error: {type(e).__name__}: {str(e)}")
                print(f"   Traceback:\n{traceback.format_exc()[:500]}")
                return None

        # === HEALTH ===
        await test_endpoint("GET", "/api/health", "Health Check")
        
        # === AUTH ===
        admin_email = os.environ.get("ADMIN_EMAIL", "testadmin@fixora.dev")
        admin_pass = os.environ.get("ADMIN_PASSWORD", "TestAdminPass2026!")
        r = await test_endpoint("POST", "/api/auth/login", "Login", 
                                json_body={"email": admin_email, "password": admin_pass})
        
        auth_headers = {}
        if r and r.status_code == 200:
            token = r.json().get("data", {}).get("access_token") or r.json().get("data", {}).get("accessToken")
            if token:
                auth_headers = {"Authorization": f"Bearer {token}"}
                print(f"   🔑 Got auth token")
        
        await test_endpoint("GET", "/api/auth/me", "Get Current User", headers=auth_headers)
        
        # === REPOSITORIES ===
        await test_endpoint("GET", "/api/repositories", "List Repositories")
        await test_endpoint("GET", "/api/repositories?projectId=proj_demo_001", "List Repos (with project filter)")
        await test_endpoint("GET", "/api/repositories/payment-service", "Get Repository by ID")
        await test_endpoint("GET", "/api/repositories/payment-service/files", "Get Repository Files")
        
        # === CONNECT REPO ===
        await test_endpoint("POST", "/api/repositories", "Connect GitHub Repository",
                           json_body={
                               "url": "https://github.com/Uday-MS/AI_Research_paper_exp.git",
                               "name": "AI_Research_paper_exp",
                               "branch": "main",
                               "source": "github",
                           })
        
        # === BUGS ===
        await test_endpoint("GET", "/api/bugs", "List Bugs")
        await test_endpoint("GET", "/api/bugs/BUG-1842", "Get Bug by ID")
        
        # === PATCHES ===
        await test_endpoint("GET", "/api/patches", "List Patches")
        await test_endpoint("GET", "/api/patches/patch_1842", "Get Patch by ID")
        
        # === INCIDENTS ===
        await test_endpoint("GET", "/api/incidents", "List Incidents")
        await test_endpoint("GET", "/api/incidents/INC-1842", "Get Incident by ID")
        
        # === INVESTIGATIONS ===
        await test_endpoint("GET", "/api/investigations", "List Investigations")
        await test_endpoint("GET", "/api/investigations/INV-1842", "Get Investigation by ID")
        
        # === KNOWLEDGE ===
        await test_endpoint("GET", "/api/knowledge/documents", "List Knowledge Documents")
        
        # === DASHBOARD ===
        await test_endpoint("GET", "/api/dashboard/stats", "Dashboard Stats")
        
        # === SETTINGS ===
        await test_endpoint("GET", "/api/settings", "Settings")
        
        # === TELEMETRY ===
        await test_endpoint("GET", "/api/telemetry/proj_demo_001/logs", "Telemetry Logs")
        await test_endpoint("GET", "/api/telemetry/proj_demo_001/metrics", "Telemetry Metrics")
        await test_endpoint("GET", "/api/telemetry/proj_demo_001/traces", "Telemetry Traces")
        
    # === SUMMARY ===
    print("\n" + "=" * 60)
    print("DIAGNOSTIC SUMMARY")
    print("=" * 60)
    
    passed = sum(1 for r in results if r["ok"])
    failed = sum(1 for r in results if not r["ok"])
    print(f"\nTotal: {len(results)} | Passed: {passed} | Failed: {failed}")
    
    if failed > 0:
        print("\n--- FAILED ENDPOINTS ---")
        for r in results:
            if not r["ok"]:
                print(f"\n  ❌ [{r['status']}] {r['method']} {r['url']}")
                print(f"     {r['label']}")
                print(f"     {r['body_preview'][:200]}")
    
    return results

if __name__ == "__main__":
    results = asyncio.run(run_diagnostics())
