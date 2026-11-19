from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.workspace import Workspace
from app.schemas.workspace import WorkspaceCreate

class WorkspaceService:
    @staticmethod
    async def list_all(db: AsyncSession) -> List[Workspace]:
        stmt = select(Workspace).order_by(Workspace.created_at.desc())
        res = await db.execute(stmt)
        return list(res.scalars().all())

    @staticmethod
    async def get_by_id(db: AsyncSession, workspace_id: str) -> Optional[Workspace]:
        stmt = select(Workspace).where(Workspace.id == workspace_id)
        res = await db.execute(stmt)
        return res.scalars().first()

    @staticmethod
    async def create(db: AsyncSession, data: WorkspaceCreate) -> Workspace:
        base_slug = data.slug or data.name.lower().replace(" ", "-").replace("/", "-")
        slug = base_slug
        counter = 1
        while True:
            stmt = select(Workspace).where(Workspace.slug == slug)
            res = await db.execute(stmt)
            if not res.scalars().first():
                break
            counter += 1
            slug = f"{base_slug}-{counter}"

        ws = Workspace(
            name=data.name,
            slug=slug,
            plan=data.plan or "pro",
            member_count=1,
        )
        db.add(ws)
        await db.commit()
        await db.refresh(ws)
        return ws
