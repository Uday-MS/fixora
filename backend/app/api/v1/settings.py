from fastapi import APIRouter
from app.schemas.common import ApiResponse
from app.core.config import settings

router = APIRouter()

@router.get("", response_model=ApiResponse[dict])
async def get_settings():
    return ApiResponse(
        data={
            "dockerMemoryLimit": "2048 MB",
            "egressMode": "restricted_isolated",
            "modelProvider": "gpt-4o / gemini-1.5-pro",
            "ragVectorStore": "Qdrant",
            "sandboxStatus": "ready",
            "githubConfigured": bool(settings.GITHUB_TOKEN),
            "executionTimeoutSeconds": 15,
            "version": "1.0.0"
        }
    )
