from typing import Optional, List, Dict, Any
from datetime import datetime
from app.schemas.base import CamelModel

class BugEvidence(CamelModel):
    id: str
    type: str  # code_snippet, test_output, log_entry, trace, document
    content: str
    source: str
    relevance_score: Optional[float] = None

class BugBase(CamelModel):
    title: str
    description: str
    file_path: str
    line_start: int = 1
    line_end: int = 1
    category: str = "logical_error"
    severity: str = "medium"
    confidence: float = 0.9
    root_cause: Optional[str] = None
    trigger_conditions: Optional[List[str]] = None
    evidence: Optional[List[Dict[str, Any]]] = None
    suggested_fix: Optional[str] = None
    patch_id: Optional[str] = None
    status: str = "detected"
    source: str = "static_analyzer"

class BugCreate(BugBase):
    project_id: str
    repository_id: str

class BugResponse(BugBase):
    id: str
    project_id: str
    repository_id: str
    created_at: datetime
    updated_at: datetime
