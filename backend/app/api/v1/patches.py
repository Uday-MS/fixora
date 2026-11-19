from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Body, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.schemas.patch import PatchResponse, TestRunResponse
from app.schemas.common import ApiResponse, PaginatedResponse
from app.services.patch_service import PatchService

router = APIRouter()

@router.get("", response_model=PaginatedResponse[PatchResponse])
async def list_patches(
    project_id: Optional[str] = Query(None, alias="projectId"),
    repository_id: Optional[str] = Query(None, alias="repositoryId"),
    db: AsyncSession = Depends(get_db)
):
    patches = await PatchService.list_patches(db, project_id=project_id, repository_id=repository_id)
    items = [PatchResponse.model_validate(p) for p in patches]
    return PaginatedResponse(
        data=items,
        total=len(items),
        page=1,
        page_size=50,
        total_pages=1,
    )

@router.post("/research", response_model=ApiResponse[dict])
async def research_issue(
    payload: dict = Body(...),
    db: AsyncSession = Depends(get_db)
):
    """
    Executes AutoPatch Research workflow on the selected repository:
    Analyzes issue, searches repository code files, locates root cause and affected lines.
    """
    repository_id = payload.get("repositoryId")
    if not repository_id:
        raise HTTPException(status_code=400, detail="repositoryId is required")

    findings = await PatchService.research_issue(
        db=db,
        repository_id=repository_id,
        issue_number=payload.get("issueNumber"),
        description=payload.get("description"),
        target_file=payload.get("targetFile"),
    )
    return ApiResponse(data=findings, message="Research completed successfully.")

@router.post("/draft", response_model=ApiResponse[PatchResponse])
async def draft_patch(
    payload: dict = Body(...),
    db: AsyncSession = Depends(get_db)
):
    """
    Executes AutoPatch Drafting workflow:
    Generates actual unified diff and proposed code based on the real repository source.
    """
    repository_id = payload.get("repositoryId")
    file_path = payload.get("filePath")
    if not repository_id or not file_path:
        raise HTTPException(status_code=400, detail="repositoryId and filePath are required")

    patch = await PatchService.draft_patch(
        db=db,
        repository_id=repository_id,
        file_path=file_path,
        issue_number=payload.get("issueNumber"),
        title=payload.get("title"),
        description=payload.get("description"),
        user_guidance=payload.get("userGuidance"),
    )
    return ApiResponse(data=PatchResponse.model_validate(patch), message="Patch drafted successfully.")

@router.get("/{id}", response_model=ApiResponse[PatchResponse])
async def get_patch(id: str, db: AsyncSession = Depends(get_db)):
    patch = await PatchService.get_by_id(db, id)
    if not patch:
        raise HTTPException(status_code=404, detail="Patch not found")
    return ApiResponse(data=PatchResponse.model_validate(patch))

@router.post("/{id}/approve", response_model=ApiResponse[PatchResponse])
async def approve_patch(id: str, db: AsyncSession = Depends(get_db)):
    patch = await PatchService.approve(db, id)
    if not patch:
        raise HTTPException(status_code=404, detail="Patch not found")
    return ApiResponse(data=PatchResponse.model_validate(patch), message="Patch approved.")

@router.post("/{id}/reject", response_model=ApiResponse[PatchResponse])
async def reject_patch(id: str, payload: dict = Body(default={}), db: AsyncSession = Depends(get_db)):
    reason = payload.get("reason")
    patch = await PatchService.reject(db, id, reason)
    if not patch:
        raise HTTPException(status_code=404, detail="Patch not found")
    return ApiResponse(data=PatchResponse.model_validate(patch), message="Patch rejected.")

@router.post("/{id}/create-pr", response_model=ApiResponse[PatchResponse])
async def create_pull_request(id: str, db: AsyncSession = Depends(get_db)):
    patch = await PatchService.create_pr(db, id)
    if not patch:
        raise HTTPException(status_code=404, detail="Patch not found")
    return ApiResponse(data=PatchResponse.model_validate(patch), message="GitHub Pull Request created.")

@router.post("/{patch_id}/run-tests", response_model=ApiResponse[TestRunResponse])
async def run_tests(patch_id: str, db: AsyncSession = Depends(get_db)):
    tr = await PatchService.run_tests(db, patch_id)
    return ApiResponse(data=TestRunResponse.model_validate(tr), message="Tests executed successfully.")

@router.get("/{patch_id}/test-run", response_model=ApiResponse[TestRunResponse])
async def get_test_run(patch_id: str, db: AsyncSession = Depends(get_db)):
    tr = await PatchService.get_test_run(db, patch_id)
    if not tr:
        tr = await PatchService.run_tests(db, patch_id)
    return ApiResponse(data=TestRunResponse.model_validate(tr))
