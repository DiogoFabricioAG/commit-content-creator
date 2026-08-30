from typing import Any

import pytest
from app.auth.session import SESSION_COOKIE_NAME, SessionManager
from app.config import Settings
from app.main import app
from fastapi.testclient import TestClient


class MockDigestGateway:
    def __init__(self, settings: Settings) -> None:
        del settings
        self.activities: list[dict[str, Any]] = []

    @property
    def is_configured(self) -> bool:
        return True

    def get_repository_by_id_for_user(
        self, *, user_id: str, repository_id: str
    ) -> dict[str, Any] | None:
        if user_id != "user_demo" or repository_id != "repo_demo":
            return None
        return {
            "_id": "repo_demo",
            "userId": "user_demo",
            "fullName": "demo/project",
            "defaultBranch": "main",
        }

    def record_activity(self, **payload: Any) -> None:
        self.activities.append(payload)


def test_digest_route_requires_an_authenticated_session() -> None:
    client = TestClient(app)

    response = client.post(
        "/api/portal/digests",
        json={"repository_id": "repo_demo"},
    )

    assert response.status_code == 401


def test_digest_route_queues_a_user_owned_repository(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    settings = Settings(
        app_env="test",
        session_secret="test-session-secret",
        convex_url="https://mock.convex.cloud",
    )
    gateway = MockDigestGateway(settings)
    scheduled: list[dict[str, Any]] = []

    def gateway_factory(current_settings: Settings) -> MockDigestGateway:
        del current_settings
        return gateway

    def fake_digest_runner(*args: Any, **kwargs: Any) -> None:
        scheduled.append({"args": args, "kwargs": kwargs})

    monkeypatch.setattr("app.api.portal.get_settings", lambda: settings)
    monkeypatch.setattr("app.api.portal.ConvexGateway", gateway_factory)
    monkeypatch.setattr("app.api.portal._run_historical_digest", fake_digest_runner)

    client = TestClient(app)
    client.cookies.set(SESSION_COOKIE_NAME, SessionManager(settings).create_session("user_demo"))
    response = client.post(
        "/api/portal/digests",
        json={"repository_id": "repo_demo", "branch": "main", "max_commits": 25},
    )

    assert response.status_code == 202
    assert response.json()["repository"] == "demo/project"
    assert scheduled
    assert scheduled[0]["kwargs"]["repository_id"] == "repo_demo"
    assert gateway.activities[0]["type_"] == "historical.digest.started"
