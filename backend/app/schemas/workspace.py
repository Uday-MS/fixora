from typing import Optional, List
from datetime import datetime
from app.schemas.base import CamelModel

class WorkspaceBase(CamelModel):
    name: str
    slug: str
    plan: str = "pro"
    member_count: int = 1

class WorkspaceCreate(CamelModel):
    name: str
    slug: Optional[str] = None
    plan: Optional[str] = "pro"

class WorkspaceResponse(WorkspaceBase):
    id: str
    created_at: datetime
