from typing import Optional, List, Dict, Any
from datetime import datetime
from app.schemas.base import CamelModel

class InvestigationStage(CamelModel):
    name: str
    status: str
    output: Optional[str] = None
    evidence: Optional[List[Dict[str, Any]]] = None
    duration: Optional[float] = None
    started_at: Optional[str] = None
    completed_at: Optional[str] = None

class InvestigationBase(CamelModel):
    question: str
    status: str = "pending"
    current_stage: str = "triage"
    stages: Optional[List[Dict[str, Any]]] = None
    findings: Optional[str] = None
    root_cause_hypothesis: Optional[str] = None
    confidence: Optional[float] = 0.9
    patch_id: Optional[str] = None

class InvestigationCreate(CamelModel):
    question: str
    project_id: str
    repository_id: Optional[str] = None
    bug_id: Optional[str] = None
    incident_id: Optional[str] = None

class InvestigationResponse(InvestigationBase):
    id: str
    project_id: str
    bug_id: Optional[str] = None
    incident_id: Optional[str] = None
    created_at: datetime
    completed_at: Optional[datetime] = None
