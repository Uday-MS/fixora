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
    """
    Bootstrap initial platform state.
    In production and development, if ADMIN_EMAIL and ADMIN_PASSWORD are set in the environment,
    creates the initial administrator account and organization if the database is currently empty.
    Never inserts hardcoded demo credentials or fake demonstration data.
    """
    if settings.ADMIN_EMAIL and settings.ADMIN_PASSWORD:
        async with AsyncSessionLocal() as session:
            user_check = await session.execute(select(User).limit(1))
            if user_check.scalars().first():
                return

            admin_email = settings.ADMIN_EMAIL.strip().lower()
            logger.info("Bootstrapping initial administrator from environment variables (%s)...", admin_email)

            admin_user = User(
                id=f"usr_{uuid.uuid4().hex[:12]}",
                email=admin_email,
                name="System Administrator",
                hashed_password=get_password_hash(settings.ADMIN_PASSWORD),
                role="admin",
                avatar_url=None,
                is_active=True,
            )
            session.add(admin_user)
            await session.flush()

            org = Organization(
                id=f"org_{uuid.uuid4().hex[:12]}",
                name="Fixora Organization",
                slug="fixora-org",
            )
            session.add(org)
            await session.flush()

            member = OrganizationMember(
                id=f"mem_{uuid.uuid4().hex[:12]}",
                organization_id=org.id,
                user_id=admin_user.id,
                role="owner",
            )
            session.add(member)

            workspace = Workspace(
                id=f"ws_{uuid.uuid4().hex[:12]}",
                organization_id=org.id,
                name="Default Workspace",
                slug="default-workspace",
                plan="enterprise",
                member_count=1,
            )
            session.add(workspace)
            await session.commit()
            logger.info("Administrator and initial workspace bootstrapped successfully.")
    else:
        logger.info("No ADMIN_EMAIL/ADMIN_PASSWORD configured. Initial user can register via /auth/register or UI.")

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Initialize DB tables and bootstrap administrator if configured
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

# CORS Security:
# In production, wildcard '*' and broad regex matches are disabled.
# Only explicit origins from settings.CORS_ORIGINS (or FRONTEND_URL) are allowed.
allow_origin_regex = None if settings.ENVIRONMENT.lower() == "production" else r"^https?:\/\/.*\.onrender\.com$"

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_origin_regex=allow_origin_regex,
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

    vector_status = "in-memory (fallback active)"
    try:
        from app.rag.qdrant_store import qdrant_store
        vector_status = "connected (remote)" if qdrant_store.is_remote else "in-memory (fallback active)"
    except Exception:
        vector_status = "in-memory (fallback active)"

    from app.orchestrator.sandbox.runner import sandbox_runner
    sandbox_info = sandbox_runner.get_runtime_status()

    return {
        "status": "online",
        "service": "FIXORA Core API",
        "version": settings.VERSION,
        "sandbox_mode": sandbox_info["mode"],
        "sandbox_status": sandbox_info["status"],
        "database": db_status,
        "components": {
            "database": db_status,
            "vector_search": vector_status,
            "sandbox_runtime": f"{sandbox_info['status']} ({sandbox_info['mode']})",
            "langgraph_orchestrator": "ready",
            "cross_encoder_reranker": "active",
        }
    }
