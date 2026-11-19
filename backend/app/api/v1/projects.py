from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.schemas.project import ProjectCreate, ProjectResponse
from app.schemas.common import ApiResponse, PaginatedResponse
from app.services.project_service import ProjectService

router = APIRouter()

@router.get("", response_model=PaginatedResponse[ProjectResponse])
async def list_projects(workspace_id: Optional[str] = Query(None, alias="workspaceId"), db: AsyncSession = Depends(get_db)):
    projects = await ProjectService.list_by_workspace(db, workspace_id)
    items = [ProjectResponse.model_validate(p) for p in projects]
    return PaginatedResponse(
        data=items,
        total=len(items),
        page=1,
        page_size=50,
        total_pages=1,
    )

@router.post("", response_model=ApiResponse[ProjectResponse])
async def create_project(data: ProjectCreate, db: AsyncSession = Depends(get_db)):
    p = await ProjectService.create(db, data)
    return ApiResponse(data=ProjectResponse.model_validate(p), message="Project created.")

@router.get("/{id}", response_model=ApiResponse[ProjectResponse])
async def get_project(id: str, db: AsyncSession = Depends(get_db)):
    p = await ProjectService.get_by_id(db, id)
    if not p:
        raise HTTPException(status_code=404, detail="Project not found")
    return ApiResponse(data=ProjectResponse.model_validate(p))
