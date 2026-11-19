from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.schemas.dashboard import DashboardStats
from app.schemas.common import ApiResponse
from app.services.dashboard_service import DashboardService

router = APIRouter()

@router.get("/stats", response_model=ApiResponse[DashboardStats])
async def get_stats(db: AsyncSession = Depends(get_db)):
    stats = await DashboardService.get_stats(db)
    return ApiResponse(data=stats)

@router.get("/health", response_model=ApiResponse[dict])
async def get_health_metrics(db: AsyncSession = Depends(get_db)):
    health = await DashboardService.get_health_metrics(db)
    return ApiResponse(data=health)
