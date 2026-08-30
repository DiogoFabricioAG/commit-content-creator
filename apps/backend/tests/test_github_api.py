# pyright: reportUnknownMemberType=false, reportUnknownVariableType=false

import hashlib
import hmac
from typing import Any

import pytest
from app.config import Settings, get_settings
from app.github.client import GitHubClient
from app.main import app
from app.schemas.github import CommitFile, NormalizedCommit
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


def test_repository_history_uses_metadata_and_limits_detail_requests(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    payloads = [
        [
            {
                "sha": f"sha-{index}",
                "commit": {
                    "message": f"feat: change {index}",
                    "author": {
                        "name": "Developer",
                        "date": "2025-01-01T00:00:00Z",
                    },
                },
            }
            for index in range(104, 4, -1)
        ],
        [
            {
                "sha": f"sha-{index}",
                "commit": {
                    "message": f"feat: change {index}",
                    "author": {
                        "name": "Developer",
                        "date": "2025-01-01T00:00:00Z",
                    },
                },
            }
            for index in range(4, -1, -1)
        ],
    ]
    page_calls: list[dict[str, Any]] = []

    class FakeResponse:
        status_code = 200
        headers: dict[str, str] = {}

        def __init__(self, payload: list[dict[str, Any]]) -> None:
            self.payload = payload

        def json(self) -> list[dict[str, Any]]:
            return self.payload

        def raise_for_status(self) -> None:
            return None

    class FakeClient:
        def __init__(self, **kwargs: Any) -> None:
            del kwargs

        def __enter__(self) -> "FakeClient":
            return self

        def __exit__(self, *args: Any) -> None:
            return None

        def get(
            self,
            url: str,
            *,
            headers: dict[str, str],
            params: dict[str, str | int],
        ) -> FakeResponse:
            del url, headers
            page_calls.append(params)
            return FakeResponse(payloads[int(params["page"]) - 1])

    monkeypatch.setattr("httpx.Client", FakeClient)
    client = GitHubClient(Settings(app_env="test"))
    detail_calls: list[str] = []

    def fake_fetch_commit(
        repository_full_name: str,
        sha: str,
        fallback_metadata: dict[str, Any] | None = None,
    ) -> Any:
        del repository_full_name
        detail_calls.append(sha)
        return NormalizedCommit(
            sha=sha,
            author="Developer",
            message=f"detail {sha}",
            committed_at=1,
            changed_files=1,
            files=[CommitFile(path="app.py", patch="diff")],
        )

    monkeypatch.setattr(client, "fetch_commit", fake_fetch_commit)

    commits = client.fetch_repository_history(
        "owner/repo",
        branch="main",
        max_commits=105,
    )

    assert len(commits) == 105
    assert len(page_calls) == 2
    assert len(detail_calls) == 12
    assert commits[0].sha == "sha-0"
    assert commits[-1].sha == "sha-104"
