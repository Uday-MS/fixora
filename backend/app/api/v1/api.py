from fastapi import APIRouter
from app.api.v1 import (
    auth,
    workspaces,
    projects,
    repositories,
    bugs,
    patches,
    incidents,
    investigations,
    knowledge,
    dashboard,
    settings,
    ingestion,
    telemetry,
    webhooks,
    service_map,
    reports,
)

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(workspaces.router, prefix="/workspaces", tags=["workspaces"])
api_router.include_router(projects.router, prefix="/projects", tags=["projects"])
api_router.include_router(repositories.router, prefix="/repositories", tags=["repositories"])
api_router.include_router(bugs.router, prefix="/bugs", tags=["bugs"])
api_router.include_router(patches.router, prefix="/patches", tags=["patches"])
api_router.include_router(incidents.router, prefix="/incidents", tags=["incidents"])
api_router.include_router(investigations.router, prefix="/investigations", tags=["investigations"])
api_router.include_router(knowledge.router, prefix="/knowledge", tags=["knowledge"])
api_router.include_router(dashboard.router, prefix="/dashboard", tags=["dashboard"])
api_router.include_router(settings.router, prefix="/settings", tags=["settings"])
api_router.include_router(ingestion.router, tags=["ingestion"])
api_router.include_router(telemetry.router, tags=["telemetry"])
api_router.include_router(webhooks.router, tags=["webhooks"])
api_router.include_router(service_map.router, tags=["service_map"])
api_router.include_router(reports.router, prefix="/reports", tags=["reports"])
