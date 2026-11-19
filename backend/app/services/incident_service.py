from typing import List, Optional
from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.incident import Incident
from app.schemas.incident import IncidentCreate

class IncidentService:
    @staticmethod
    async def create(db: AsyncSession, data: IncidentCreate) -> Incident:
        inc = Incident(
            project_id=data.project_id,
            title=data.title,
            description=data.description,
            severity=data.severity,
            status=data.status,
            affected_service=data.affected_service,
            error_message=data.error_message,
            related_commits=data.related_commits or [],
            related_bug_ids=data.related_bug_ids or [],
        )
        db.add(inc)
        await db.commit()
        await db.refresh(inc)
        return inc

    @staticmethod
    async def list_incidents(db: AsyncSession, project_id: Optional[str] = None) -> List[Incident]:
        stmt = select(Incident)
        if project_id:
            stmt = stmt.where(Incident.project_id == project_id)
        stmt = stmt.order_by(Incident.started_at.desc())
        res = await db.execute(stmt)
        return list(res.scalars().all())

    @staticmethod
    async def get_by_id(db: AsyncSession, incident_id: str) -> Optional[Incident]:
        stmt = select(Incident).where(Incident.id == incident_id)
        res = await db.execute(stmt)
        return res.scalars().first()

    @staticmethod
    async def resolve(db: AsyncSession, incident_id: str) -> Optional[Incident]:
        inc = await IncidentService.get_by_id(db, incident_id)
        if inc:
            inc.status = "resolved"
            inc.resolved_at = datetime.now(timezone.utc)
            await db.commit()
            await db.refresh(inc)
        return inc
