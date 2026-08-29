# pyright: reportUnknownMemberType=false, reportUnknownVariableType=false

import hashlib
import hmac

import pytest
from app.config import get_settings
from app.main import app
from fastapi.testclient import TestClient

client = TestClient(app)


def _signed_headers(body: bytes, secret: str) -> dict[str, str]:
    digest = hmac.new(secret.encode(), body, hashlib.sha256).hexdigest()
    return {
        "content-type": "application/json",
        "x-github-delivery": "delivery-api-001",
        "x-github-event": "push",
        "x-hub-signature-256": f"sha256={digest}",
    }


def test_github_webhook_rejects_invalid_signature(monkeypatch: pytest.MonkeyPatch) -> None:
    secret = "local-test-secret"
    monkeypatch.setenv("GITHUB_WEBHOOK_SECRET", secret)
    monkeypatch.setenv("CONVEX_URL", "https://example.convex.cloud")
    get_settings.cache_clear()

    response = client.post(
        "/webhooks/github",
        content=b'{"ref":"refs/heads/main"}',
        headers={
            "x-github-delivery": "delivery-api-002",
            "x-github-event": "push",
            "x-hub-signature-256": "sha256=invalid",
        },
    )

    get_settings.cache_clear()
    assert response.status_code == 401


def test_github_webhook_requires_convex_after_signature_check(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    secret = "local-test-secret"
    body = b'{"ref":"refs/heads/main","repository":{"full_name":"demo/notifications"},"commits":[]}'
    monkeypatch.setenv("GITHUB_WEBHOOK_SECRET", secret)
    monkeypatch.delenv("CONVEX_URL", raising=False)
    get_settings.cache_clear()

    response = client.post(
        "/webhooks/github",
        content=body,
        headers=_signed_headers(body, secret),
    )

    get_settings.cache_clear()
    assert response.status_code == 503
