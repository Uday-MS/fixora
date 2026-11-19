from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.schemas.investigation import InvestigationResponse, InvestigationCreate
from app.schemas.common import ApiResponse, PaginatedResponse
from app.services.investigation_service import InvestigationService

router = APIRouter()

@router.get("", response_model=PaginatedResponse[InvestigationResponse])
async def list_investigations(db: AsyncSession = Depends(get_db)):
    invs = await InvestigationService.list_investigations(db)
    items = [InvestigationResponse.model_validate(i) for i in invs]
    return PaginatedResponse(
        data=items,
        total=len(items),
        page=1,
        page_size=50,
        total_pages=1,
    )

@router.get("/{id}", response_model=ApiResponse[InvestigationResponse])
async def get_investigation(id: str, db: AsyncSession = Depends(get_db)):
    inv = await InvestigationService.get_by_id(db, id)
    if not inv:
        raise HTTPException(status_code=404, detail="Investigation not found")
    return ApiResponse(data=InvestigationResponse.model_validate(inv))

@router.post("", response_model=ApiResponse[InvestigationResponse])
async def create_investigation(payload: InvestigationCreate, db: AsyncSession = Depends(get_db)):
    """
    Triggers FIXORA's LangGraph 7-agent autonomous incident intelligence pipeline:
    Triage -> Retrieval -> RCA -> Diagnostic -> AutoPatch -> Validation -> Postmortem
    """
    inv = await InvestigationService.create_and_run(
        db=db,
        project_id=payload.project_id,
        question=payload.question,
        repository_id=payload.repository_id,
        bug_id=payload.bug_id,
        incident_id=payload.incident_id,
    )
    return ApiResponse(data=InvestigationResponse.model_validate(inv), message="Investigation executed successfully.")
