from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Body
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.schemas.patch import PatchResponse, TestRunResponse
from app.schemas.common import ApiResponse, PaginatedResponse
from app.services.patch_service import PatchService

router = APIRouter()

@router.get("", response_model=PaginatedResponse[PatchResponse])
async def list_patches(db: AsyncSession = Depends(get_db)):
    patches = await PatchService.list_patches(db)
    items = [PatchResponse.model_validate(p) for p in patches]
    return PaginatedResponse(
        data=items,
        total=len(items),
        page=1,
        page_size=50,
        total_pages=1,
    )

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
        # Generate default pass for Demo Benchmark
        tr = await PatchService.run_tests(db, patch_id)
    return ApiResponse(data=TestRunResponse.model_validate(tr))
