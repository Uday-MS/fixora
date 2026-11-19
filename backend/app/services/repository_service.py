from typing import List, Optional, Dict, Any
from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.repository import Repository
from app.models.project import Project
from app.schemas.repository import RepositoryCreate

class RepositoryService:
    @staticmethod
    async def list_repositories(db: AsyncSession, project_id: Optional[str] = None) -> List[Repository]:
        stmt = select(Repository)
        if project_id:
            stmt = stmt.where(Repository.project_id == project_id)
        stmt = stmt.order_by(Repository.created_at.desc())
        res = await db.execute(stmt)
        return list(res.scalars().all())

    @staticmethod
    async def get_by_id(db: AsyncSession, repo_id: str) -> Optional[Repository]:
        stmt = select(Repository).where(Repository.id == repo_id)
        res = await db.execute(stmt)
        return res.scalars().first()

    @staticmethod
    async def connect_repository(db: AsyncSession, data: RepositoryCreate) -> Repository:
        token = getattr(data, "token", None)
        owner = "acme"
        name = data.name or "service-repo"
        url = data.url or f"https://github.com/acme/{name}"

        if data.url and ("github.com" in data.url or "/" in data.url.strip()):
            try:
                from app.services.github_service import GitHubService
                owner, parsed_name = GitHubService.parse_repo_url(data.url)
                name = data.name or parsed_name
                url = f"https://github.com/{owner}/{name}"
            except Exception:
                pass

        # Ensure a project exists to attach to
        project_id = data.project_id
        if not project_id:
            p_stmt = select(Project).limit(1)
            p_res = await db.execute(p_stmt)
            default_p = p_res.scalars().first()
            project_id = default_p.id if default_p else "default-project"

        repo = Repository(
            project_id=project_id,
            name=name,
            full_name=f"{owner}/{name}",
            url=url,
            branch=data.branch or "main",
            source=data.source or "github",
            language=data.language or "Python",
            health_status="healthy",
            issue_count=0,
            commit_count=1,
            file_count=0,
            last_synced_at=datetime.now(timezone.utc),
            files_tree=[],
        )
        db.add(repo)
        await db.commit()
        await db.refresh(repo)

        # Attempt real GitHub ingestion if a GitHub URL was provided
        if "github.com" in url:
            try:
                from app.services.github_service import GitHubService
                repo = await GitHubService.sync_repository_from_github(db, repo, token=token)
            except Exception as e:
                # Log but keep created record
                import logging
                logging.getLogger("fixora.repository").warning("Initial GitHub sync warning: %s", str(e))

        return repo

    @staticmethod
    async def sync_repository(db: AsyncSession, repo_id: str) -> Optional[Repository]:
        repo = await RepositoryService.get_by_id(db, repo_id)
        if not repo:
            return None

        if repo.source == "github" and repo.url and "github.com" in repo.url:
            try:
                from app.services.github_service import GitHubService
                repo = await GitHubService.sync_repository_from_github(db, repo)
                return repo
            except Exception as e:
                import logging
                logging.getLogger("fixora.repository").warning("GitHub sync error: %s", str(e))

        repo.last_synced_at = datetime.now(timezone.utc)
        await db.commit()
        await db.refresh(repo)
        return repo

    @staticmethod
    async def delete_repository(db: AsyncSession, repo_id: str) -> bool:
        from app.models.bug import Bug
        from app.models.patch import Patch
        from app.models.test_run import TestRun
        from app.models.knowledge import KnowledgeDocument
        from sqlalchemy import delete

        repo = await RepositoryService.get_by_id(db, repo_id)
        if not repo:
            return False

        # 1. Find all bugs for this repository
        b_stmt = select(Bug.id).where(Bug.repository_id == repo_id)
        b_res = await db.execute(b_stmt)
        bug_ids = list(b_res.scalars().all())

        # 2. Find and delete patches and test runs associated with those bugs or repo
        p_stmt = select(Patch.id).where((Patch.repository_id == repo_id) | (Patch.bug_id.in_(bug_ids)))
        p_res = await db.execute(p_stmt)
        patch_ids = list(p_res.scalars().all())

        if patch_ids:
            await db.execute(delete(TestRun).where(TestRun.patch_id.in_(patch_ids)))
            await db.execute(delete(Patch).where(Patch.id.in_(patch_ids)))

        # 3. Delete bugs
        if bug_ids:
            await db.execute(delete(Bug).where(Bug.id.in_(bug_ids)))

        # 4. Clean up any knowledge documents associated with this repository name
        await db.execute(
            delete(KnowledgeDocument).where(
                (KnowledgeDocument.title.contains(f"({repo.name})")) |
                (KnowledgeDocument.file_path.contains(repo.name))
            )
        )

        # 5. Delete repository itself
        await db.delete(repo)
        await db.commit()
        return True
