from convex import ConvexClient

from app.config import Settings


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
