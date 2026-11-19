import io
import os
import zipfile
import hashlib
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fastapi import HTTPException, UploadFile

from app.models.repository import Repository
from app.models.project import Project
from app.models.knowledge import KnowledgeDocument
from app.models.ingestion_job import IngestionJob
from app.schemas.ingestion import RepoZipAnalysis, DocumentUploadResponse

LANGUAGE_EXTENSIONS = {
    ".py": "Python",
    ".ts": "TypeScript",
    ".tsx": "TypeScript",
    ".js": "JavaScript",
    ".jsx": "JavaScript",
    ".go": "Go",
    ".rs": "Rust",
    ".java": "Java",
    ".c": "C",
    ".cpp": "C++",
    ".h": "C/C++",
    ".rb": "Ruby",
    ".php": "PHP",
    ".html": "HTML",
    ".css": "CSS",
    ".sql": "SQL",
    ".sh": "Shell",
}

IGNORE_PREFIXES = (
    ".git/",
    "__pycache__/",
    "node_modules/",
    ".venv/",
    "venv/",
    ".pytest_cache/",
    ".idea/",
    ".vscode/",
    ".DS_Store",
)

class IngestionService:

    @staticmethod
    async def create_job(
        db: AsyncSession,
        project_id: str,
        job_type: str,
        repository_id: Optional[str] = None,
        metadata_json: Optional[Dict[str, Any]] = None,
    ) -> IngestionJob:
        job = IngestionJob(
            project_id=project_id,
            repository_id=repository_id,
            job_type=job_type,
            status="processing",
            progress=10,
            started_at=datetime.now(timezone.utc),
            metadata_json=metadata_json or {},
        )
        db.add(job)
        await db.commit()
        await db.refresh(job)
        return job

    @staticmethod
    async def update_job(
        db: AsyncSession,
        job: IngestionJob,
        status: str,
        progress: int,
        items_processed: int = 0,
        total_items: int = 0,
        error_message: Optional[str] = None,
        metadata_json: Optional[Dict[str, Any]] = None,
    ) -> IngestionJob:
        job.status = status
        job.progress = progress
        job.items_processed = items_processed
        job.total_items = total_items
        if error_message:
            job.error_message = error_message
        if metadata_json:
            merged = job.metadata_json or {}
            merged.update(metadata_json)
            job.metadata_json = merged
        if status in ("completed", "failed"):
            job.completed_at = datetime.now(timezone.utc)
        await db.commit()
        await db.refresh(job)
        return job

    @staticmethod
    async def process_repository_zip(
        db: AsyncSession,
        repository_id: str,
        file: UploadFile,
    ) -> RepoZipAnalysis:
        # Validate repository
        repo_stmt = select(Repository).where(Repository.id == repository_id)
        repo_res = await db.execute(repo_stmt)
        repo = repo_res.scalars().first()
        if not repo:
            raise HTTPException(status_code=404, detail="Repository not found")

        # Read zip bytes
        zip_bytes = await file.read()
        if len(zip_bytes) > 50 * 1024 * 1024:
            raise HTTPException(status_code=400, detail="Repository ZIP exceeds 50MB limit")

        # Create ingestion job
        job = await IngestionService.create_job(
            db=db,
            project_id=repo.project_id,
            job_type="repo_zip",
            repository_id=repo.id,
            metadata_json={"filename": file.filename, "size_bytes": len(zip_bytes)},
        )

        try:
            with zipfile.ZipFile(io.BytesIO(zip_bytes), "r") as z:
                # Security check: Zip Slip vulnerability check
                for member in z.namelist():
                    if member.startswith("/") or ".." in member.split("/"):
                        raise HTTPException(status_code=400, detail=f"Malicious file path detected: {member}")

                file_list: List[str] = []
                language_counts: Dict[str, int] = {}
                total_lines = 0
                readme_content: Optional[str] = None
                readme_filename: Optional[str] = None

                has_readme = False
                has_tests = False
                has_manifest = False
                has_ci = False
                has_docker = False

                manifest_names = {
                    "requirements.txt",
                    "package.json",
                    "cargo.toml",
                    "go.mod",
                    "pom.xml",
                    "pyproject.toml",
                    "build.gradle",
                }

                all_members = [
                    m for m in z.namelist()
                    if not any(m.startswith(p) or f"/{p}" in m for p in IGNORE_PREFIXES) and not m.endswith("/")
                ]

                await IngestionService.update_job(
                    db=db,
                    job=job,
                    status="processing",
                    progress=30,
                    total_items=len(all_members),
                )

                for idx, name in enumerate(all_members):
                    base_name = os.path.basename(name).lower()
                    _, ext = os.path.splitext(name)
                    ext = ext.lower()

                    file_list.append(name)

                    # Structure checks
                    if base_name.startswith("readme"):
                        has_readme = True
                        if not readme_content:
                            try:
                                readme_content = z.read(name).decode("utf-8", errors="replace")
                                readme_filename = name
                            except Exception:
                                pass

                    if "test" in name.lower() or "spec" in name.lower():
                        has_tests = True

                    if base_name in manifest_names:
                        has_manifest = True

                    if ".github/workflows" in name or ".gitlab-ci.yml" in name:
                        has_ci = True

                    if "dockerfile" in base_name or "docker-compose" in base_name:
                        has_docker = True

                    # Language detection
                    if ext in LANGUAGE_EXTENSIONS:
                        lang = LANGUAGE_EXTENSIONS[ext]
                        language_counts[lang] = language_counts.get(lang, 0) + 1
                        try:
                            content = z.read(name).decode("utf-8", errors="ignore")
                            total_lines += len(content.splitlines())
                        except Exception:
                            pass

                await IngestionService.update_job(
                    db=db,
                    job=job,
                    status="processing",
                    progress=70,
                    items_processed=len(all_members),
                    total_items=len(all_members),
                )

                # Primary language determination
                primary_language = "Python"
                if language_counts:
                    primary_language = max(language_counts, key=language_counts.get)

                # Health score calculation
                health_score = 50
                if has_readme:
                    health_score += 15
                if has_tests:
                    health_score += 15
                if has_manifest:
                    health_score += 10
                if has_ci:
                    health_score += 10
                if has_docker:
                    health_score += 5
                health_score = max(20, min(98, health_score))

                health_status = "healthy"
                if health_score < 60:
                    health_status = "warning"
                elif health_score < 40:
                    health_status = "critical"

                # Update repository record
                repo.file_count = len(file_list)
                repo.language = primary_language
                repo.health_status = health_status
                
                structured_tree = []
                for fpath in file_list[:200]:
                    _, fext = os.path.splitext(fpath)
                    structured_tree.append({
                        "path": fpath,
                        "name": os.path.basename(fpath),
                        "type": "file",
                        "size": 1024,
                        "language": LANGUAGE_EXTENSIONS.get(fext.lower(), "Text"),
                    })
                repo.files_tree = structured_tree
                repo.last_synced_at = datetime.now(timezone.utc)

                # Ingest README into knowledge base if present
                if readme_content and readme_filename:
                    content_hash = hashlib.sha256(readme_content.encode("utf-8")).hexdigest()
                    existing_doc_stmt = select(KnowledgeDocument).where(
                        KnowledgeDocument.project_id == repo.project_id,
                        KnowledgeDocument.content_hash == content_hash,
                    )
                    existing_doc = (await db.execute(existing_doc_stmt)).scalars().first()
                    if not existing_doc:
                        doc = KnowledgeDocument(
                            project_id=repo.project_id,
                            title=f"README ({repo.name})",
                            source_type="readme",
                            content=readme_content,
                            file_path=readme_filename,
                            content_hash=content_hash,
                            file_size=len(readme_content.encode("utf-8")),
                            chunk_count=max(1, len(readme_content) // 500),
                            status="indexed",
                        )
                        db.add(doc)
                        try:
                            from app.rag.rag_engine import rag_engine
                            rag_engine.index_document(
                                document_id=doc.id,
                                project_id=repo.project_id,
                                title=doc.title,
                                source_type=doc.source_type,
                                file_path=doc.file_path,
                                content=readme_content,
                            )
                        except Exception:
                            pass

                # Ingest key source code files into knowledge base
                indexed_count = 0
                for code_path in file_list:
                    if indexed_count >= 15:
                        break
                    _, c_ext = os.path.splitext(code_path)
                    if c_ext.lower() in LANGUAGE_EXTENSIONS and not os.path.basename(code_path).lower().startswith("readme"):
                        try:
                            code_bytes = z.read(code_path)
                            if len(code_bytes) < 60000:
                                code_str = code_bytes.decode("utf-8", errors="ignore")
                                if len(code_str.strip()) > 30:
                                    c_hash = hashlib.sha256(code_str.encode("utf-8")).hexdigest()
                                    existing_c_stmt = select(KnowledgeDocument).where(
                                        KnowledgeDocument.project_id == repo.project_id,
                                        KnowledgeDocument.content_hash == c_hash,
                                    )
                                    if not (await db.execute(existing_c_stmt)).scalars().first():
                                        cdoc = KnowledgeDocument(
                                            project_id=repo.project_id,
                                            title=f"{os.path.basename(code_path)} ({repo.name})",
                                            source_type="code",
                                            content=code_str,
                                            file_path=code_path,
                                            content_hash=c_hash,
                                            file_size=len(code_bytes),
                                            chunk_count=max(1, len(code_str) // 500),
                                            status="indexed",
                                        )
                                        db.add(cdoc)
                                        try:
                                            from app.rag.rag_engine import rag_engine
                                            rag_engine.index_document(
                                                document_id=cdoc.id,
                                                project_id=repo.project_id,
                                                title=cdoc.title,
                                                source_type=cdoc.source_type,
                                                file_path=cdoc.file_path,
                                                content=code_str,
                                            )
                                        except Exception:
                                            pass
                                        indexed_count += 1
                        except Exception:
                            pass

                await db.commit()
                await db.refresh(repo)

                structure_checks = {
                    "hasReadme": has_readme,
                    "hasTests": has_tests,
                    "hasDependencyManifest": has_manifest,
                    "hasContinuousIntegration": has_ci,
                    "hasContainerization": has_docker,
                }

                await IngestionService.update_job(
                    db=db,
                    job=job,
                    status="completed",
                    progress=100,
                    items_processed=len(all_members),
                    total_items=len(all_members),
                    metadata_json={
                        "primaryLanguage": primary_language,
                        "healthScore": health_score,
                        "structureChecks": structure_checks,
                    },
                )

                return RepoZipAnalysis(
                    repositoryId=repo.id,
                    repositoryName=repo.name,
                    fileCount=len(file_list),
                    totalLines=total_lines,
                    primaryLanguage=primary_language,
                    languageBreakdown=language_counts,
                    healthScore=health_score,
                    healthStatus=health_status,
                    structureChecks=structure_checks,
                    files=file_list[:100],
                )

        except zipfile.BadZipFile:
            await IngestionService.update_job(
                db=db,
                job=job,
                status="failed",
                progress=0,
                error_message="Invalid or corrupted ZIP archive",
            )
            raise HTTPException(status_code=400, detail="Invalid ZIP archive")
        except HTTPException as he:
            await IngestionService.update_job(
                db=db,
                job=job,
                status="failed",
                progress=0,
                error_message=str(he.detail),
            )
            raise he
        except Exception as e:
            await IngestionService.update_job(
                db=db,
                job=job,
                status="failed",
                progress=0,
                error_message=str(e),
            )
            raise HTTPException(status_code=500, detail=f"Failed to process ZIP archive: {str(e)}")

    @staticmethod
    async def process_document_upload(
        db: AsyncSession,
        project_id: str,
        file: UploadFile,
        source_type: str = "documentation",
    ) -> DocumentUploadResponse:
        # Validate project
        proj_stmt = select(Project).where(Project.id == project_id)
        proj_res = await db.execute(proj_stmt)
        proj = proj_res.scalars().first()
        if not proj:
            raise HTTPException(status_code=404, detail="Project not found")

        raw_bytes = await file.read()
        file_size = len(raw_bytes)
        if file_size > 25 * 1024 * 1024:
            raise HTTPException(status_code=400, detail="Document exceeds 25MB file size limit")

        filename = file.filename or "uploaded_document"
        _, ext = os.path.splitext(filename)
        ext = ext.lower()

        allowed_extensions = {
            ".pdf", ".md", ".markdown", ".txt", ".docx",
            ".py", ".ts", ".js", ".json", ".yaml", ".yml", ".rst",
        }
        if ext not in allowed_extensions:
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported file format '{ext}'. Supported: PDF, Markdown, TXT, DOCX, Code/Config",
            )

        # Compute SHA-256 for duplicate detection
        content_hash = hashlib.sha256(raw_bytes).hexdigest()

        # Check for duplicate
        dup_stmt = select(KnowledgeDocument).where(
            KnowledgeDocument.project_id == project_id,
            KnowledgeDocument.content_hash == content_hash,
        )
        existing_dup = (await db.execute(dup_stmt)).scalars().first()
        if existing_dup:
            return DocumentUploadResponse(
                documentId=existing_dup.id,
                projectId=project_id,
                title=existing_dup.title,
                sourceType=existing_dup.source_type,
                fileSize=existing_dup.file_size,
                contentHash=content_hash,
                chunkCount=existing_dup.chunk_count,
                status=existing_dup.status,
                isDuplicate=True,
                message="Document with identical content already ingested in this project.",
            )

        # Content extraction based on extension
        extracted_text = ""
        page_count = 1

        if ext == ".pdf":
            try:
                import pypdf
                pdf_reader = pypdf.PdfReader(io.BytesIO(raw_bytes))
                page_count = len(pdf_reader.pages)
                extracted_pages = []
                for p in pdf_reader.pages:
                    text = p.extract_text()
                    if text:
                        extracted_pages.append(text)
                extracted_text = "\n\n".join(extracted_pages)
                if not extracted_text.strip():
                    extracted_text = f"PDF Document: {filename} ({page_count} pages, text stream empty)"
            except Exception as e:
                raise HTTPException(status_code=400, detail=f"Failed to extract text from PDF: {str(e)}")

        elif ext == ".docx":
            try:
                import docx
                doc_obj = docx.Document(io.BytesIO(raw_bytes))
                paragraphs = [p.text for p in doc_obj.paragraphs if p.text.strip()]
                extracted_text = "\n\n".join(paragraphs)
            except Exception as e:
                raise HTTPException(status_code=400, detail=f"Failed to extract text from DOCX: {str(e)}")

        else:
            try:
                extracted_text = raw_bytes.decode("utf-8")
            except UnicodeDecodeError:
                extracted_text = raw_bytes.decode("latin-1", errors="replace")

        if not extracted_text.strip():
            raise HTTPException(status_code=400, detail="Document content is empty or unextractable")

        chunk_count = max(1, len(extracted_text) // 500)

        # Create knowledge document
        title = os.path.splitext(filename)[0].replace("-", " ").replace("_", " ").title()
        doc = KnowledgeDocument(
            project_id=project_id,
            title=title,
            source_type=source_type,
            content=extracted_text,
            file_path=filename,
            content_hash=content_hash,
            file_size=file_size,
            chunk_count=chunk_count,
            status="indexed",
            metadata_json={
                "originalFilename": filename,
                "extension": ext,
                "characterCount": len(extracted_text),
                "wordCount": len(extracted_text.split()),
                "pageCount": page_count,
            },
        )
        db.add(doc)
        await db.commit()
        await db.refresh(doc)

        # Index document into Qdrant & BM25 via RAG Engine
        try:
            from app.rag.rag_engine import rag_engine
            rag_engine.index_document(
                document_id=doc.id,
                project_id=doc.project_id,
                title=doc.title,
                source_type=doc.source_type,
                file_path=doc.file_path,
                content=doc.content,
            )
        except Exception:
            pass

        # Ingestion job
        job = await IngestionService.create_job(
            db=db,
            project_id=project_id,
            job_type="doc_upload",
            metadata_json={
                "documentId": doc.id,
                "filename": filename,
                "fileSize": file_size,
                "chunkCount": chunk_count,
            },
        )
        await IngestionService.update_job(
            db=db,
            job=job,
            status="completed",
            progress=100,
            items_processed=1,
            total_items=1,
        )

        return DocumentUploadResponse(
            documentId=doc.id,
            projectId=project_id,
            title=doc.title,
            sourceType=doc.source_type,
            fileSize=doc.file_size,
            contentHash=content_hash,
            chunkCount=doc.chunk_count,
            status=doc.status,
            isDuplicate=False,
            message="Document successfully processed and indexed for RAG retrieval.",
        )
