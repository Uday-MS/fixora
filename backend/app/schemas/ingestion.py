from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import Field
from app.schemas.base import CamelModel

class IngestionJobResponse(CamelModel):
    id: str
    projectId: str
    repositoryId: Optional[str] = None
    jobType: str
    status: str
    progress: int
    itemsProcessed: int
    totalItems: int
    errorMessage: Optional[str] = None
    metadataJson: Optional[Dict[str, Any]] = None
    startedAt: Optional[datetime] = None
    completedAt: Optional[datetime] = None
    createdAt: datetime

class RepoZipAnalysis(CamelModel):
    repositoryId: str
    repositoryName: str
    fileCount: int
    totalLines: int
    primaryLanguage: str
    languageBreakdown: Dict[str, int]
    healthScore: int
    healthStatus: str
    structureChecks: Dict[str, bool]
    files: List[str]

class RepoZipUploadResponse(CamelModel):
    jobId: str
    status: str
    message: str
    analysis: RepoZipAnalysis

class DocumentUploadResponse(CamelModel):
    documentId: str
    projectId: str
    title: str
    sourceType: str
    fileSize: int
    contentHash: str
    chunkCount: int
    status: str
    isDuplicate: bool = False
    message: str

class GitHubWebhookResponse(CamelModel):
    received: bool
    event: str
    action: Optional[str] = None
    repository: Optional[str] = None
    status: str
