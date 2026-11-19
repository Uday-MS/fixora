from typing import Optional
from datetime import datetime
from app.schemas.base import CamelModel

class PatchBase(CamelModel):
    title: str
    description: str
    file_path: str
    original_code: str
    proposed_code: str
    unified_diff: str
    explanation: str
    status: str = "draft"
    test_run_id: Optional[str] = None
    pr_url: Optional[str] = None
    pr_number: Optional[int] = None
    reviewed_at: Optional[datetime] = None
    reviewed_by: Optional[str] = None

class PatchCreate(PatchBase):
    bug_id: str
    project_id: str
    repository_id: str

class PatchResponse(PatchBase):
    id: str
    bug_id: str
    project_id: str
    repository_id: str
    created_at: datetime

class TestRunResponse(CamelModel):
    id: str
    patch_id: str
    command: str
    status: str
    total_tests: int
    passed_tests: int
    failed_tests: int
    output: str
    duration: Optional[float] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
