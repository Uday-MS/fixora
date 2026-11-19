from typing import Optional, List
from datetime import datetime
from app.schemas.base import CamelModel

class IncidentBase(CamelModel):
    title: str
    description: str
    severity: str = "sev2"
    status: str = "active"
    affected_service: str
    error_message: Optional[str] = None
    related_commits: Optional[List[str]] = None
    related_bug_ids: Optional[List[str]] = None

class IncidentCreate(IncidentBase):
    project_id: str

class IncidentResponse(IncidentBase):
    id: str
    project_id: str
    started_at: datetime
    resolved_at: Optional[datetime] = None
    created_at: datetime
