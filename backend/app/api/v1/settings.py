from fastapi import APIRouter
from app.schemas.common import ApiResponse
from app.core.config import settings

router = APIRouter()

@router.get("", response_model=ApiResponse[dict])
async def get_settings():
    from app.rag.qdrant_store import qdrant_store
    from app.orchestrator.sandbox.runner import sandbox_runner
    sandbox_info = sandbox_runner.get_runtime_status()

    return ApiResponse(
        data={
            "dockerMemoryLimit": settings.DOCKER_MEMORY_LIMIT,
            "egressMode": "restricted_isolated",
            "modelProvider": f"{settings.OPENAI_MODEL} / {settings.GEMINI_MODEL}",
            "ragVectorStore": "Qdrant (remote)" if qdrant_store.is_remote else "In-Memory Fallback (ephemeral)",
            "sandboxStatus": sandbox_info["mode"],
            "githubConfigured": bool(settings.GITHUB_TOKEN),
            "executionTimeoutSeconds": settings.SANDBOX_TIMEOUT_SECONDS,
            "version": settings.VERSION,
            "diagnostics": settings.get_configuration_summary(),
        }
    )

@router.get("/validate", response_model=ApiResponse[dict])
async def validate_environment_and_services():
    """Runs live connectivity and configuration checks for all platform components."""
    results = await settings.run_live_connectivity_checks()
    return ApiResponse(data=results)
