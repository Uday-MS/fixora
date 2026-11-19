from typing import Optional, List, Any
from datetime import datetime
from app.schemas.base import CamelModel

class RepositoryFile(CamelModel):
    path: str
    name: str
    type: str  # file, directory
    language: Optional[str] = None
    size: Optional[int] = None
    children: Optional[List['RepositoryFile']] = None

class RepositoryBase(CamelModel):
    name: str
    full_name: str
    source: str = "github"
    branch: str = "main"
    language: str = "Python"
    health_status: str = "healthy"
    issue_count: int = 0
    commit_count: int = 0
    file_count: int = 0
    url: Optional[str] = None

class RepositoryCreate(CamelModel):
    name: Optional[str] = None
    url: Optional[str] = None
    branch: Optional[str] = "main"
    project_id: Optional[str] = None
    token: Optional[str] = None
    source: Optional[str] = "github"
    language: Optional[str] = "Python"

class RepositoryResponse(RepositoryBase):
    id: str
    project_id: str
    last_synced_at: Optional[datetime] = None
