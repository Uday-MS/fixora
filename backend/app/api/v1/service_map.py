from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.services.service_map_service import ServiceMapService
from app.schemas.service_map import ServiceNodeCreate, ServiceNodeResponse, ServiceGraphResponse

router = APIRouter()

@router.get("/projects/{project_id}/services", response_model=ServiceGraphResponse)
async def get_service_graph(
    project_id: str,
    db: AsyncSession = Depends(get_db),
):
    """
    Get the service dependency topology graph for a project.
    """
    return await ServiceMapService.get_service_graph(db=db, project_id=project_id)

@router.post("/projects/{project_id}/services", response_model=ServiceNodeResponse)
async def create_service_node(
    project_id: str,
    payload: ServiceNodeCreate,
    db: AsyncSession = Depends(get_db),
):
    """
    Register a service node in the project topology.
    """
    node = await ServiceMapService.create_service_node(db=db, project_id=project_id, data=payload)
    return ServiceNodeResponse(
        id=node.id,
        projectId=node.project_id,
        repositoryId=node.repository_id,
        name=node.name,
        tier=node.tier,
        status=node.status,
        runtime=node.runtime,
        dependencies=node.dependencies,
        metadataJson=node.metadata_json,
        createdAt=node.created_at,
    )
