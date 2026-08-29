import json
from typing import Any, cast

from fastapi import APIRouter, BackgroundTasks, HTTPException, Request, status

from app.config import get_settings
from app.github.webhooks import (
    InvalidGitHubPayload,
    InvalidGitHubSignature,
    normalize_github_event,
    verify_github_signature,
)
from app.integrations.convex_client import ConvexGateway
from app.schemas.github import NormalizedGitHubEvent

router = APIRouter(prefix="/webhooks/github", tags=["github"])


def _persist_event(event: NormalizedGitHubEvent) -> None:
    settings = get_settings()
    ConvexGateway(settings).record_github_event(event)


@router.post("", status_code=status.HTTP_202_ACCEPTED)
async def receive_github_webhook(
    request: Request,
    background_tasks: BackgroundTasks,
) -> dict[str, str]:
    settings = get_settings()
    body = await request.body()
    delivery_id = request.headers.get("x-github-delivery")
    event_type = request.headers.get("x-github-event")

    try:
        verify_github_signature(
            body,
            request.headers.get("x-hub-signature-256"),
            settings.github_webhook_secret,
        )
    except InvalidGitHubSignature as error:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(error)) from error

    if not settings.convex_url:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="CONVEX_URL is required to receive GitHub events",
        )

    if not event_type or event_type not in {"push", "pull_request"}:
        raise HTTPException(
            status_code=status.HTTP_202_ACCEPTED,
            detail="GitHub event ignored",
        )

    if not delivery_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="X-GitHub-Delivery is required",
        )

    try:
        raw_payload = json.loads(body)
        if not isinstance(raw_payload, dict):
            raise InvalidGitHubPayload("GitHub payload must be an object")
        payload = cast(dict[str, Any], raw_payload)
        event = normalize_github_event(
            event_type=event_type,
            delivery_id=delivery_id,
            payload=payload,
        )
    except (json.JSONDecodeError, InvalidGitHubPayload) as error:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(error)) from error

    background_tasks.add_task(_persist_event, event)
    return {"status": "accepted", "delivery_id": event.delivery_id}
