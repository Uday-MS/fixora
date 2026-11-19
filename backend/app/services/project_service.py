from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.models.project import Project
from app.models.repository import Repository
from app.models.bug import Bug
from app.schemas.project import ProjectCreate

class ProjectService:
    @staticmethod
    async def list_by_workspace(db: AsyncSession, workspace_id: Optional[str] = None) -> List[Project]:
        stmt = select(Project)
        if workspace_id:
            stmt = stmt.where(Project.workspace_id == workspace_id)
        stmt = stmt.order_by(Project.created_at.desc())
        res = await db.execute(stmt)
        return list(res.scalars().all())

    @staticmethod
    async def get_by_id(db: AsyncSession, project_id: str) -> Optional[Project]:
        stmt = select(Project).where(Project.id == project_id)
        res = await db.execute(stmt)
        return res.scalars().first()

    @staticmethod
    async def create(db: AsyncSession, data: ProjectCreate) -> Project:
        proj = Project(
            workspace_id=data.workspace_id,
            name=data.name,
            description=data.description,
            status=data.status,
        )
        db.add(proj)
        await db.commit()
        await db.refresh(proj)
        return proj
