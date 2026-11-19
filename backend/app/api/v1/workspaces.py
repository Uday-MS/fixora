from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.schemas.workspace import WorkspaceCreate, WorkspaceResponse
from app.schemas.common import ApiResponse, PaginatedResponse
from app.services.workspace_service import WorkspaceService

router = APIRouter()

@router.get("", response_model=PaginatedResponse[WorkspaceResponse])
async def list_workspaces(db: AsyncSession = Depends(get_db)):
    items = await WorkspaceService.list_all(db)
    res_items = [WorkspaceResponse.model_validate(w) for w in items]
    return PaginatedResponse(
        data=res_items,
        total=len(res_items),
        page=1,
        page_size=50,
        total_pages=1,
    )

@router.post("", response_model=ApiResponse[WorkspaceResponse])
async def create_workspace(data: WorkspaceCreate, db: AsyncSession = Depends(get_db)):
    ws = await WorkspaceService.create(db, data)
    return ApiResponse(data=WorkspaceResponse.model_validate(ws), message="Workspace created.")

@router.get("/{id}", response_model=ApiResponse[WorkspaceResponse])
async def get_workspace(id: str, db: AsyncSession = Depends(get_db)):
    ws = await WorkspaceService.get_by_id(db, id)
    if not ws:
        raise HTTPException(status_code=404, detail="Workspace not found")
    return ApiResponse(data=WorkspaceResponse.model_validate(ws))
