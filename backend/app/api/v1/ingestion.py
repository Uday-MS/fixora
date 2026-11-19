import os
from typing import List, Optional
from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc

from app.db.session import get_db
from app.models.ingestion_job import IngestionJob
from app.models.repository import Repository
from app.models.project import Project
from app.services.ingestion_service import IngestionService
from app.services.repository_service import ensure_project_id
from app.schemas.ingestion import (
    RepoZipUploadResponse,
    DocumentUploadResponse,
    IngestionJobResponse,
)

router = APIRouter()

@router.post("/repositories/upload-zip", response_model=RepoZipUploadResponse)
async def upload_standalone_repository_zip(
    file: UploadFile = File(...),
    name: Optional[str] = Form(None),
    projectId: Optional[str] = Form(None),
    db: AsyncSession = Depends(get_db),
):
    """
    Directly ingest a repository from a ZIP archive, creating the repository record automatically.
    """
    if not file.filename or not file.filename.endswith(".zip"):
        raise HTTPException(status_code=400, detail="Only .zip files are supported for repository upload")

    p_id = await ensure_project_id(db, projectId)

    repo_name = name or os.path.splitext(file.filename)[0]
    repo = Repository(
        project_id=p_id,
        name=repo_name,
        full_name=f"upload/{repo_name}",
        url=f"local://{file.filename}",
        branch="main",
        source="zip_upload",
        language="Unknown",
        health_status="healthy",
        issue_count=0,
        commit_count=1,
        file_count=0,
        files_tree=[],
    )
    db.add(repo)
    await db.commit()
    await db.refresh(repo)

    analysis = await IngestionService.process_repository_zip(
        db=db,
        repository_id=repo.id,
        file=file,
    )
    return RepoZipUploadResponse(
        jobId=analysis.repositoryId,
        status="completed",
        message=f"Repository '{analysis.repositoryName}' successfully ingested with {analysis.fileCount} files.",
        analysis=analysis,
    )

@router.post("/repositories/{repository_id}/upload-zip", response_model=RepoZipUploadResponse)
async def upload_repository_zip(
    repository_id: str,
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
):
    """
    Ingest a repository from a ZIP archive.
    Extracts structure, detects languages, counts lines of code, extracts README,
    and runs initial structural health analysis.
    """
    if not file.filename or not file.filename.endswith(".zip"):
        raise HTTPException(status_code=400, detail="Only .zip files are supported for repository upload")

    analysis = await IngestionService.process_repository_zip(
        db=db,
        repository_id=repository_id,
        file=file,
    )
    return RepoZipUploadResponse(
        jobId=analysis.repositoryId,
        status="completed",
        message=f"Repository '{analysis.repositoryName}' successfully ingested with {analysis.fileCount} files.",
        analysis=analysis,
    )

@router.post("/knowledge/upload", response_model=DocumentUploadResponse)
async def upload_knowledge_document(
    projectId: str = Form(...),
    sourceType: str = Form("documentation"),
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
):
    """
    Upload and index documentation for RAG.
    Supports PDF, Markdown, DOCX, TXT, and source code.
    Performs content hashing to detect and avoid duplicate ingestion.
    """
    return await IngestionService.process_document_upload(
        db=db,
        project_id=projectId,
        file=file,
        source_type=sourceType,
    )

@router.get("/ingestion/jobs", response_model=List[IngestionJobResponse])
async def list_ingestion_jobs(
    projectId: str = Query(...),
    status: Optional[str] = Query(None),
    limit: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
):
    """
    List background ingestion jobs with progress indicators.
    """
    stmt = select(IngestionJob).where(IngestionJob.project_id == projectId)
    if status:
        stmt = stmt.where(IngestionJob.status == status)
    stmt = stmt.order_by(desc(IngestionJob.created_at)).limit(limit)
    res = await db.execute(stmt)
    jobs = list(res.scalars().all())

    return [
        IngestionJobResponse(
            id=j.id,
            projectId=j.project_id,
            repositoryId=j.repository_id,
            jobType=j.job_type,
            status=j.status,
            progress=j.progress,
            itemsProcessed=j.items_processed,
            totalItems=j.total_items,
            errorMessage=j.error_message,
            metadataJson=j.metadata_json,
            startedAt=j.started_at,
            completedAt=j.completed_at,
            createdAt=j.created_at,
        )
        for j in jobs
    ]

@router.get("/ingestion/jobs/{job_id}", response_model=IngestionJobResponse)
async def get_ingestion_job(
    job_id: str,
    db: AsyncSession = Depends(get_db),
):
    """
    Get detailed status of a specific ingestion job.
    """
    stmt = select(IngestionJob).where(IngestionJob.id == job_id)
    res = await db.execute(stmt)
    job = res.scalars().first()
    if not job:
        raise HTTPException(status_code=404, detail="Ingestion job not found")

    return IngestionJobResponse(
        id=job.id,
        projectId=job.project_id,
        repositoryId=job.repository_id,
        jobType=job.job_type,
        status=job.status,
        progress=job.progress,
        itemsProcessed=job.items_processed,
        totalItems=job.total_items,
        errorMessage=job.error_message,
        metadataJson=job.metadata_json,
        startedAt=job.started_at,
        completedAt=job.completed_at,
        createdAt=job.created_at,
    )
