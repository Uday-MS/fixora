from typing import Optional
from datetime import datetime
from app.schemas.base import CamelModel

class ProjectBase(CamelModel):
    name: str
    description: Optional[str] = None
    status: str = "active"

class ProjectCreate(ProjectBase):
    workspace_id: str

class ProjectResponse(ProjectBase):
    id: str
    workspace_id: str
    repository_count: int = 0
    bug_count: int = 0
    created_at: datetime
    updated_at: datetime
