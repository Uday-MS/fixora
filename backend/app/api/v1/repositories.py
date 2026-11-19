from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.schemas.repository import RepositoryCreate, RepositoryResponse, RepositoryFile
from app.schemas.common import ApiResponse, PaginatedResponse
from app.services.repository_service import RepositoryService

router = APIRouter()

@router.get("", response_model=PaginatedResponse[RepositoryResponse])
async def list_repositories(project_id: Optional[str] = Query(None, alias="projectId"), db: AsyncSession = Depends(get_db)):
    repos = await RepositoryService.list_repositories(db, project_id)
    items = [RepositoryResponse.model_validate(r) for r in repos]
    return PaginatedResponse(
        data=items,
        total=len(items),
        page=1,
        page_size=50,
        total_pages=1,
    )

@router.post("", response_model=ApiResponse[RepositoryResponse])
async def connect_repository(data: RepositoryCreate, db: AsyncSession = Depends(get_db)):
    repo = await RepositoryService.connect_repository(db, data)
    return ApiResponse(data=RepositoryResponse.model_validate(repo), message="Repository connected.")

@router.get("/{id}", response_model=ApiResponse[RepositoryResponse])
async def get_repository(id: str, db: AsyncSession = Depends(get_db)):
    repo = await RepositoryService.get_by_id(db, id)
    if not repo:
        raise HTTPException(status_code=404, detail="Repository not found")
    return ApiResponse(data=RepositoryResponse.model_validate(repo))

@router.post("/{id}/sync", response_model=ApiResponse[RepositoryResponse])
async def sync_repository(id: str, db: AsyncSession = Depends(get_db)):
    repo = await RepositoryService.sync_repository(db, id)
    if not repo:
        raise HTTPException(status_code=404, detail="Repository not found")
    return ApiResponse(data=RepositoryResponse.model_validate(repo), message="Repository synced.")

@router.delete("/{id}", response_model=ApiResponse[dict])
async def delete_repository(id: str, db: AsyncSession = Depends(get_db)):
    success = await RepositoryService.delete_repository(db, id)
    if not success:
        raise HTTPException(status_code=404, detail="Repository not found")
    return ApiResponse(data={"id": id, "deleted": True}, message="Repository deleted successfully.")

@router.get("/{id}/files", response_model=ApiResponse[List[RepositoryFile]])
async def get_repository_files(id: str, db: AsyncSession = Depends(get_db)):
    import os
    repo = await RepositoryService.get_by_id(db, id)
    if not repo:
        raise HTTPException(status_code=404, detail="Repository not found")
    
    raw_files = repo.files_tree or []
    normalized: List[RepositoryFile] = []
    for f in raw_files:
        if isinstance(f, dict):
            normalized.append(RepositoryFile.model_validate(f))
        elif isinstance(f, str):
            _, ext = os.path.splitext(f)
            lang = "Python" if ext in (".py",) else "Go" if ext in (".go",) else "TypeScript" if ext in (".ts", ".tsx") else "Text"
            normalized.append(RepositoryFile(
                path=f,
                name=os.path.basename(f),
                type="directory" if f.endswith("/") else "file",
                size=1024,
                language=lang,
            ))
    return ApiResponse(data=normalized)

@router.get("/{id}/issues", response_model=ApiResponse[List[dict]])
async def get_repository_issues(
    id: str,
    state: str = Query("all", pattern="^(open|closed|all)$"),
    db: AsyncSession = Depends(get_db)
):
    """
    Fetches real GitHub issues for this repository.
    Filters out pull requests.
    """
    from app.services.github_service import GitHubService
    repo = await RepositoryService.get_by_id(db, id)
    if not repo:
        raise HTTPException(status_code=404, detail="Repository not found")

    if repo.source != "github" or not repo.url or "github.com" not in repo.url:
        return ApiResponse(data=[], message="Repository is not linked to GitHub.")

    try:
        owner, repo_name = GitHubService.parse_repo_url(repo.url)
        issues = await GitHubService.fetch_repository_issues(owner, repo_name, state=state)
        return ApiResponse(data=issues)
    except HTTPException:
        raise
    except Exception as e:
        return ApiResponse(data=[], message=f"Failed to fetch issues: {str(e)}")

@router.get("/{id}/branches", response_model=ApiResponse[List[str]])
async def get_repository_branches(id: str, db: AsyncSession = Depends(get_db)):
    """
    Fetches branch list for this repository.
    """
    from app.services.github_service import GitHubService
    repo = await RepositoryService.get_by_id(db, id)
    if not repo:
        raise HTTPException(status_code=404, detail="Repository not found")

    default_branch = repo.branch or "main"
    if repo.source != "github" or not repo.url or "github.com" not in repo.url:
        return ApiResponse(data=[default_branch])

    try:
        owner, repo_name = GitHubService.parse_repo_url(repo.url)
        branches = await GitHubService.fetch_repository_branches(owner, repo_name)
        if default_branch not in branches:
            branches.insert(0, default_branch)
        return ApiResponse(data=branches)
    except Exception:
        return ApiResponse(data=[default_branch])

@router.get("/{id}/commits", response_model=ApiResponse[List[dict]])
async def get_repository_commits(
    id: str,
    branch: Optional[str] = Query(None),
    limit: int = Query(10, le=50),
    db: AsyncSession = Depends(get_db)
):
    """
    Fetches recent commit history for this repository.
    """
    from app.services.github_service import GitHubService
    repo = await RepositoryService.get_by_id(db, id)
    if not repo:
        raise HTTPException(status_code=404, detail="Repository not found")

    target_branch = branch or repo.branch or "main"
    if repo.source != "github" or not repo.url or "github.com" not in repo.url:
        return ApiResponse(data=[])

    try:
        owner, repo_name = GitHubService.parse_repo_url(repo.url)
        commits = await GitHubService.fetch_recent_commits(owner, repo_name, branch=target_branch, limit=limit)
        return ApiResponse(data=commits)
    except Exception:
        return ApiResponse(data=[])

@router.get("/{id}/file-content", response_model=ApiResponse[dict])
async def get_repository_file_content(
    id: str,
    path: str = Query(..., description="Relative file path"),
    branch: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db)
):
    """
    Fetches real content of a file from this repository.
    """
    from app.services.github_service import GitHubService
    repo = await RepositoryService.get_by_id(db, id)
    if not repo:
        raise HTTPException(status_code=404, detail="Repository not found")

    target_branch = branch or repo.branch or "main"
    content = None

    if repo.source == "github" and repo.url and "github.com" in repo.url:
        owner, repo_name = GitHubService.parse_repo_url(repo.url)
        content = await GitHubService.fetch_file_content(owner, repo_name, path, branch=target_branch)

    if content is None:
        raise HTTPException(status_code=404, detail=f"File '{path}' could not be retrieved from repository.")

    return ApiResponse(data={"path": path, "content": content})
