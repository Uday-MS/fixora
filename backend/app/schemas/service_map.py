from typing import Optional, List, Dict, Any
from datetime import datetime
from app.schemas.base import CamelModel

class ServiceNodeCreate(CamelModel):
    name: str
    tier: str = "backend"  # frontend, backend, gateway, worker, database, cache
    status: str = "healthy"
    runtime: str = "python"
    repositoryId: Optional[str] = None
    dependencies: Optional[List[str]] = None
    metadataJson: Optional[Dict[str, Any]] = None

class ServiceNodeResponse(CamelModel):
    id: str
    projectId: str
    repositoryId: Optional[str] = None
    name: str
    tier: str
    status: str
    runtime: str
    dependencies: Optional[List[str]] = None
    metadataJson: Optional[Dict[str, Any]] = None
    createdAt: datetime

class ServiceGraphEdge(CamelModel):
    source: str
    target: str

class ServiceGraphResponse(CamelModel):
    nodes: List[ServiceNodeResponse]
    edges: List[ServiceGraphEdge]
