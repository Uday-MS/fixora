from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.schemas.repository import RepositoryCreate, RepositoryResponse, RepositoryFile
from app.schemas.common import ApiResponse, PaginatedResponse
from app.services.repository_service import RepositoryService

router = APIRouter()

@router.get("", response_model=PaginatedResponse[RepositoryResponse])
async def list_repositories(project_id: Optional[str] = Query(None, alias="projectId"), db: AsyncSession = Depends(get_db)):
    repos = await RepositoryService.list_repositories(db, project_id)
    items = [RepositoryResponse.model_validate(r) for r in repos]
    return PaginatedResponse(
        data=items,
        total=len(items),
        page=1,
        page_size=50,
        total_pages=1,
    )

@router.post("", response_model=ApiResponse[RepositoryResponse])
async def connect_repository(data: RepositoryCreate, db: AsyncSession = Depends(get_db)):
    repo = await RepositoryService.connect_repository(db, data)
    return ApiResponse(data=RepositoryResponse.model_validate(repo), message="Repository connected.")

@router.get("/{id}", response_model=ApiResponse[RepositoryResponse])
async def get_repository(id: str, db: AsyncSession = Depends(get_db)):
    repo = await RepositoryService.get_by_id(db, id)
    if not repo:
        raise HTTPException(status_code=404, detail="Repository not found")
    return ApiResponse(data=RepositoryResponse.model_validate(repo))

@router.post("/{id}/sync", response_model=ApiResponse[RepositoryResponse])
async def sync_repository(id: str, db: AsyncSession = Depends(get_db)):
    repo = await RepositoryService.sync_repository(db, id)
    if not repo:
        raise HTTPException(status_code=404, detail="Repository not found")
    return ApiResponse(data=RepositoryResponse.model_validate(repo), message="Repository synced.")

@router.delete("/{id}", response_model=ApiResponse[dict])
async def delete_repository(id: str, db: AsyncSession = Depends(get_db)):
    success = await RepositoryService.delete_repository(db, id)
    if not success:
        raise HTTPException(status_code=404, detail="Repository not found")
    return ApiResponse(data={"id": id, "deleted": True}, message="Repository deleted successfully.")

@router.get("/{id}/files", response_model=ApiResponse[List[RepositoryFile]])
async def get_repository_files(id: str, db: AsyncSession = Depends(get_db)):
    import os
    repo = await RepositoryService.get_by_id(db, id)
    if not repo:
        raise HTTPException(status_code=404, detail="Repository not found")
    
    raw_files = repo.files_tree or []
    normalized: List[RepositoryFile] = []
    for f in raw_files:
        if isinstance(f, dict):
            normalized.append(RepositoryFile.model_validate(f))
        elif isinstance(f, str):
            _, ext = os.path.splitext(f)
            lang = "Python" if ext in (".py",) else "Go" if ext in (".go",) else "TypeScript" if ext in (".ts", ".tsx") else "Text"
            normalized.append(RepositoryFile(
                path=f,
                name=os.path.basename(f),
                type="directory" if f.endswith("/") else "file",
                size=1024,
                language=lang,
            ))
    return ApiResponse(data=normalized)
