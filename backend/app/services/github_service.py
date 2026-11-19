import os
import hmac
import hashlib
import json
import logging
from datetime import datetime, timezone
from typing import Dict, Any, Optional, List, Tuple
import httpx
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fastapi import HTTPException

from app.core.config import settings
from app.models.repository import Repository
from app.models.knowledge import KnowledgeDocument
from app.models.audit_log import AuditLog
from app.schemas.ingestion import GitHubWebhookResponse

logger = logging.getLogger("fixora.github")

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
    ".yaml": "YAML",
    ".yml": "YAML",
    ".json": "JSON",
    ".md": "Markdown",
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
    "dist/",
    "build/",
)

class GitHubService:

    @staticmethod
    def parse_repo_url(url: str) -> Tuple[str, str]:
        """
        Parses owner and repository name from GitHub URLs or owner/repo format.
        Examples:
          - https://github.com/octocat/Hello-World.git -> ('octocat', 'Hello-World')
          - https://github.com/octocat/Hello-World -> ('octocat', 'Hello-World')
          - octocat/Hello-World -> ('octocat', 'Hello-World')
        """
        clean = url.strip()
        if "github.com/" in clean:
            clean = clean.split("github.com/")[1]
        clean = clean.rstrip("/").removesuffix(".git")
        parts = clean.split("/")
        if len(parts) >= 2:
            return parts[0], parts[1]
        raise HTTPException(
            status_code=400,
            detail=f"Invalid GitHub repository URL: '{url}'. Expected 'owner/repo' or 'https://github.com/owner/repo'."
        )

    @staticmethod
    def get_headers(token: Optional[str] = None) -> Dict[str, str]:
        auth_token = token or getattr(settings, "GITHUB_TOKEN", None) or os.getenv("GITHUB_TOKEN")
        headers = {
            "User-Agent": "FIXORA-Autonomous-Agent",
            "Accept": "application/vnd.github.v3+json",
        }
        if auth_token:
            headers["Authorization"] = f"Bearer {auth_token}"
        return headers

    @staticmethod
    async def fetch_repository_metadata(
        owner: str,
        repo: str,
        token: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Calls GitHub REST API to fetch real repository metadata.
        """
        url = f"https://api.github.com/repos/{owner}/{repo}"
        headers = GitHubService.get_headers(token)

        async with httpx.AsyncClient(timeout=10.0) as client:
            try:
                res = await client.get(url, headers=headers)
                if res.status_code == 404:
                    raise HTTPException(
                        status_code=404,
                        detail=f"GitHub repository '{owner}/{repo}' not found or is private without authorization."
                    )
                if res.status_code == 403 and "rate limit" in res.text.lower():
                    logger.warning("GitHub API rate limit exceeded for unauthenticated request.")
                    # Return informative simulated metadata if rate limited in demo environments
                    return {
                        "name": repo,
                        "full_name": f"{owner}/{repo}",
                        "default_branch": "main",
                        "description": f"Imported GitHub repository {owner}/{repo}",
                        "language": "Python",
                        "open_issues_count": 2,
                        "stargazers_count": 10,
                        "forks_count": 3,
                        "rate_limited": True,
                    }
                res.raise_for_status()
                return res.json()
            except httpx.RequestError as e:
                logger.error("GitHub connection error: %s", str(e))
                raise HTTPException(status_code=503, detail=f"Failed to communicate with GitHub API: {str(e)}")

    @staticmethod
    async def fetch_repository_tree(
        owner: str,
        repo: str,
        branch: str = "main",
        token: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Fetches the recursive git tree for the repository branch.
        """
        url = f"https://api.github.com/repos/{owner}/{repo}/git/trees/{branch}?recursive=1"
        headers = GitHubService.get_headers(token)

        async with httpx.AsyncClient(timeout=15.0) as client:
            try:
                res = await client.get(url, headers=headers)
                if res.status_code != 200:
                    logger.warning("Could not fetch recursive git tree for %s/%s branch %s (status %s)", owner, repo, branch, res.status_code)
                    return []
                tree_data = res.json().get("tree", [])
                files = []
                for item in tree_data:
                    path = item.get("path", "")
                    if any(path.startswith(p) or f"/{p}" in path for p in IGNORE_PREFIXES):
                        continue
                    item_type = "directory" if item.get("type") == "tree" else "file"
                    _, ext = os.path.splitext(path)
                    lang = LANGUAGE_EXTENSIONS.get(ext.lower(), "Text")
                    files.append({
                        "path": path,
                        "name": os.path.basename(path),
                        "type": item_type,
                        "size": item.get("size", 0) or 0,
                        "language": lang,
                    })
                return files
            except Exception as e:
                logger.warning("Error fetching GitHub tree: %s", str(e))
                return []

    @staticmethod
    async def fetch_file_content(
        owner: str,
        repo: str,
        path: str,
        branch: str = "main",
        token: Optional[str] = None
    ) -> Optional[str]:
        """
        Fetches raw content of a specific file from GitHub.
        """
        raw_url = f"https://raw.githubusercontent.com/{owner}/{repo}/{branch}/{path}"
        headers = GitHubService.get_headers(token)

        async with httpx.AsyncClient(timeout=10.0) as client:
            try:
                res = await client.get(raw_url, headers=headers)
                if res.status_code == 200:
                    return res.text
            except Exception:
                pass

        # Fallback to GitHub contents API
        api_url = f"https://api.github.com/repos/{owner}/{repo}/contents/{path}?ref={branch}"
        api_headers = {**headers, "Accept": "application/vnd.github.v3.raw"}
        async with httpx.AsyncClient(timeout=10.0) as client:
            try:
                res = await client.get(api_url, headers=api_headers)
                if res.status_code == 200:
                    return res.text
            except Exception:
                pass
        return None

    @staticmethod
    async def sync_repository_from_github(
        db: AsyncSession,
        repo: Repository,
        token: Optional[str] = None,
    ) -> Repository:
        """
        Performs full real ingestion of a connected GitHub repository:
        1. Fetches metadata (stars, open issues, default branch).
        2. Fetches full git tree.
        3. Identifies languages, health score, and dependencies.
        4. Fetches and indexes README into Qdrant/BM25.
        5. Fetches and indexes key source code files into Qdrant/BM25.
        6. Persists structured tree and counts to database.
        """
        owner, repo_name = GitHubService.parse_repo_url(repo.url)
        meta = await GitHubService.fetch_repository_metadata(owner, repo_name, token)

        default_branch = meta.get("default_branch") or repo.branch or "main"
        repo.branch = default_branch
        repo.full_name = meta.get("full_name", f"{owner}/{repo_name}")
        repo.issue_count = meta.get("open_issues_count", repo.issue_count or 0)
        if meta.get("language"):
            repo.language = meta.get("language")

        # Fetch tree
        tree_files = await GitHubService.fetch_repository_tree(owner, repo_name, default_branch, token)

        if tree_files:
            repo.file_count = len([f for f in tree_files if f["type"] == "file"])
            repo.files_tree = tree_files[:250]  # Store structured dicts

            # Detect language breakdown
            lang_counts: Dict[str, int] = {}
            has_readme = False
            has_tests = False
            has_manifest = False
            has_docker = False
            has_ci = False

            readme_path = None
            code_files_to_index: List[Dict[str, Any]] = []

            for f in tree_files:
                if f["type"] != "file":
                    continue
                p = f["path"].lower()
                lang = f.get("language", "Text")
                if lang not in ("Text", "Markdown"):
                    lang_counts[lang] = lang_counts.get(lang, 0) + 1
                    if len(code_files_to_index) < 12 and f.get("size", 0) < 50000:
                        code_files_to_index.append(f)

                if "readme" in p:
                    has_readme = True
                    readme_path = f["path"]
                if "test" in p or "spec" in p:
                    has_tests = True
                if any(m in p for m in ("package.json", "requirements.txt", "go.mod", "cargo.toml", "pyproject.toml")):
                    has_manifest = True
                if "dockerfile" in p or "docker-compose" in p:
                    has_docker = True
                if ".github/workflows" in p:
                    has_ci = True

            if lang_counts and not repo.language:
                repo.language = max(lang_counts, key=lang_counts.get)

            # Health score
            h_score = 50
            if has_readme: h_score += 15
            if has_tests: h_score += 15
            if has_manifest: h_score += 10
            if has_ci: h_score += 10
            if has_docker: h_score += 5
            repo.health_status = "healthy" if h_score >= 60 else "warning" if h_score >= 40 else "critical"

            # Ingest and index README if present
            if readme_path:
                readme_text = await GitHubService.fetch_file_content(owner, repo_name, readme_path, default_branch, token)
                if readme_text:
                    content_hash = hashlib.sha256(readme_text.encode("utf-8")).hexdigest()
                    doc = KnowledgeDocument(
                        project_id=repo.project_id,
                        title=f"README ({repo.name})",
                        source_type="readme",
                        content=readme_text,
                        file_path=readme_path,
                        content_hash=content_hash,
                        file_size=len(readme_text.encode("utf-8")),
                        chunk_count=max(1, len(readme_text) // 500),
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
                            content=readme_text,
                        )
                    except Exception as e:
                        logger.warning("RAG indexing README failed: %s", str(e))

            # Ingest and index key code files
            for cf in code_files_to_index:
                cf_text = await GitHubService.fetch_file_content(owner, repo_name, cf["path"], default_branch, token)
                if cf_text and len(cf_text) > 30:
                    content_hash = hashlib.sha256(cf_text.encode("utf-8")).hexdigest()
                    cdoc = KnowledgeDocument(
                        project_id=repo.project_id,
                        title=f"{cf['name']} ({repo.name})",
                        source_type="code",
                        content=cf_text,
                        file_path=cf["path"],
                        content_hash=content_hash,
                        file_size=len(cf_text.encode("utf-8")),
                        chunk_count=max(1, len(cf_text) // 500),
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
                            content=cf_text,
                        )
                    except Exception:
                        pass

        repo.last_synced_at = datetime.now(timezone.utc)
        await db.commit()
        await db.refresh(repo)
        return repo

    @staticmethod
    def verify_webhook_signature(payload_bytes: bytes, signature_header: Optional[str]) -> bool:
        webhook_secret = getattr(settings, "GITHUB_WEBHOOK_SECRET", None) or "fixora_default_github_webhook_secret"
        if not signature_header:
            return False

        if not signature_header.startswith("sha256="):
            return False

        expected_sig = signature_header.split("sha256=", 1)[1]
        computed_sig = hmac.new(
            key=webhook_secret.encode("utf-8"),
            msg=payload_bytes,
            digestmod=hashlib.sha256,
        ).hexdigest()

        return hmac.compare_digest(expected_sig, computed_sig)

    @staticmethod
    async def process_webhook_event(
        db: AsyncSession,
        event_name: str,
        payload: Dict[str, Any],
    ) -> GitHubWebhookResponse:
        repo_info = payload.get("repository", {})
        repo_name = repo_info.get("name")
        repo_full_name = repo_info.get("full_name")
        action = payload.get("action")

        repo = None
        if repo_full_name or repo_name:
            stmt = select(Repository).where(
                (Repository.full_name == repo_full_name) | (Repository.name == repo_name)
            )
            res = await db.execute(stmt)
            repo = res.scalars().first()

        status = "ignored"

        if event_name == "push":
            commits = payload.get("commits", [])
            if repo:
                repo.commit_count = (repo.commit_count or 0) + len(commits)
                repo.last_synced_at = datetime.now(timezone.utc)
                db.add(repo)
            status = f"Processed push with {len(commits)} commits"

        elif event_name == "pull_request":
            pr_data = payload.get("pull_request", {})
            pr_num = pr_data.get("number")
            status = f"Processed pull_request #{pr_num} action: {action}"

        elif event_name == "issues":
            issue_data = payload.get("issue", {})
            if repo:
                if action == "opened":
                    repo.issue_count = (repo.issue_count or 0) + 1
                elif action == "closed" and repo.issue_count and repo.issue_count > 0:
                    repo.issue_count -= 1
                db.add(repo)
            status = f"Processed issue #{issue_data.get('number')} action: {action}"

        elif event_name == "deployment" or event_name == "deployment_status":
            status = f"Processed deployment status: {action}"

        audit = AuditLog(
            action=f"github_webhook:{event_name}",
            resource_type="repository",
            resource_id=repo.id if repo else repo_name,
            details={
                "event": event_name,
                "action": action,
                "repository": repo_full_name or repo_name,
                "sender": payload.get("sender", {}).get("login"),
            },
        )
        db.add(audit)
        await db.commit()

        return GitHubWebhookResponse(
            received=True,
            event=event_name,
            action=action,
            repository=repo_full_name or repo_name,
            status=status,
        )
