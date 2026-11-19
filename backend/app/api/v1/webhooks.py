import json
from fastapi import APIRouter, Depends, Request, Header, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.services.github_service import GitHubService
from app.schemas.ingestion import GitHubWebhookResponse

router = APIRouter()

@router.post("/webhooks/github", response_model=GitHubWebhookResponse)
async def github_webhook(
    request: Request,
    x_github_event: str = Header(..., alias="X-GitHub-Event"),
    x_hub_signature_256: str = Header(None, alias="X-Hub-Signature-256"),
    db: AsyncSession = Depends(get_db),
):
    """
    Receive and verify GitHub webhooks for push, pull_request, issues, and deployments.
    """
    body_bytes = await request.body()

    # Verify signature if signature header is provided
    if x_hub_signature_256:
        is_valid = GitHubService.verify_webhook_signature(body_bytes, x_hub_signature_256)
        if not is_valid:
            raise HTTPException(status_code=401, detail="Invalid GitHub webhook signature")

    try:
        payload = json.loads(body_bytes.decode("utf-8"))
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid JSON payload")

    return await GitHubService.process_webhook_event(
        db=db,
        event_name=x_github_event,
        payload=payload,
    )
