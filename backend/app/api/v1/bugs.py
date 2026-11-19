from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query, Body
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.schemas.bug import BugResponse
from app.schemas.common import ApiResponse, PaginatedResponse
from app.services.bug_service import BugService

router = APIRouter()

@router.get("", response_model=PaginatedResponse[BugResponse])
async def list_bugs(
    project_id: Optional[str] = Query(None, alias="projectId"),
    repository_id: Optional[str] = Query(None, alias="repositoryId"),
    db: AsyncSession = Depends(get_db),
):
    bugs = await BugService.list_bugs(db, project_id, repository_id)
    items = [BugResponse.model_validate(b) for b in bugs]
    return PaginatedResponse(
        data=items,
        total=len(items),
        page=1,
        page_size=50,
        total_pages=1,
    )

@router.get("/{id}", response_model=ApiResponse[BugResponse])
async def get_bug(id: str, db: AsyncSession = Depends(get_db)):
    bug = await BugService.get_by_id(db, id)
    if not bug:
        raise HTTPException(status_code=404, detail="Bug finding not found")
    return ApiResponse(data=BugResponse.model_validate(bug))

@router.patch("/{id}", response_model=ApiResponse[BugResponse])
async def update_bug_status(id: str, payload: dict = Body(...), db: AsyncSession = Depends(get_db)):
    status = payload.get("status", "dismissed")
    bug = await BugService.update_status(db, id, status)
    if not bug:
        raise HTTPException(status_code=404, detail="Bug not found")
    return ApiResponse(data=BugResponse.model_validate(bug), message="Bug status updated.")
