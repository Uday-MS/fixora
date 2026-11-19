from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.schemas.incident import IncidentResponse, IncidentCreate
from app.schemas.common import ApiResponse, PaginatedResponse
from app.services.incident_service import IncidentService

router = APIRouter()

@router.post("", response_model=ApiResponse[IncidentResponse])
async def create_incident(data: IncidentCreate, db: AsyncSession = Depends(get_db)):
    inc = await IncidentService.create(db, data)
    return ApiResponse(data=IncidentResponse.model_validate(inc), message="Incident created.")

@router.get("", response_model=PaginatedResponse[IncidentResponse])
async def list_incidents(db: AsyncSession = Depends(get_db)):
    incidents = await IncidentService.list_incidents(db)
    items = [IncidentResponse.model_validate(i) for i in incidents]
    return PaginatedResponse(
        data=items,
        total=len(items),
        page=1,
        page_size=50,
        total_pages=1,
    )

@router.get("/{id}", response_model=ApiResponse[IncidentResponse])
async def get_incident(id: str, db: AsyncSession = Depends(get_db)):
    inc = await IncidentService.get_by_id(db, id)
    if not inc:
        raise HTTPException(status_code=404, detail="Incident not found")
    return ApiResponse(data=IncidentResponse.model_validate(inc))

@router.post("/{id}/resolve", response_model=ApiResponse[IncidentResponse])
async def resolve_incident(id: str, db: AsyncSession = Depends(get_db)):
    inc = await IncidentService.resolve(db, id)
    if not inc:
        raise HTTPException(status_code=404, detail="Incident not found")
    return ApiResponse(data=IncidentResponse.model_validate(inc), message="Incident resolved.")
