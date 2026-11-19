from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.bug import Bug

class BugService:
    @staticmethod
    async def list_bugs(db: AsyncSession, project_id: Optional[str] = None, repository_id: Optional[str] = None) -> List[Bug]:
        stmt = select(Bug)
        if project_id:
            stmt = stmt.where(Bug.project_id == project_id)
        if repository_id:
            stmt = stmt.where(Bug.repository_id == repository_id)
        stmt = stmt.order_by(Bug.created_at.desc())
        res = await db.execute(stmt)
        return list(res.scalars().all())

    @staticmethod
    async def get_by_id(db: AsyncSession, bug_id: str) -> Optional[Bug]:
        stmt = select(Bug).where(Bug.id == bug_id)
        res = await db.execute(stmt)
        return res.scalars().first()

    @staticmethod
    async def update_status(db: AsyncSession, bug_id: str, status: str) -> Optional[Bug]:
        bug = await BugService.get_by_id(db, bug_id)
        if bug:
            bug.status = status
            await db.commit()
            await db.refresh(bug)
        return bug
