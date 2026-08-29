from convex.values import CoercibleToConvexValue

from app.config import Settings
from app.schemas.github import NormalizedGitHubEvent
from convex import ConvexClient


class ConvexGateway:
    """Lazily exposes the official Convex Python client to backend services."""

    def __init__(self, settings: Settings) -> None:
        self._client = ConvexClient(settings.convex_url) if settings.convex_url else None

    @property
    def is_configured(self) -> bool:
        return self._client is not None

    @property
    def client(self) -> ConvexClient:
        if self._client is None:
            raise RuntimeError("CONVEX_URL is required before using the Convex client")
        return self._client

    def record_github_event(self, event: NormalizedGitHubEvent) -> None:
        payload: dict[str, CoercibleToConvexValue] = {
            "deliveryId": event.delivery_id,
            "eventType": event.event_type,
            "repositoryFullName": event.repository_full_name,
            "commitShas": event.commit_shas,
        }
        if event.branch:
            payload["branch"] = event.branch
        if event.action:
            payload["action"] = event.action

        self.client.mutation("githubEvents:record", payload)
