from typing import Any

import pytest
from app.auth.session import SESSION_COOKIE_NAME, SessionManager
from app.config import Settings
from app.main import app
from fastapi.testclient import TestClient


class MockConvexPortalGateway:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self.users: dict[str, dict[str, Any]] = {
            "user_alice": {"_id": "user_alice", "displayName": "Alice", "whatsappPhone": "+51999111222"},
            "user_bob": {"_id": "user_bob", "displayName": "Bob", "whatsappPhone": "+51999333444"},
        }
        self.repositories: dict[str, dict[str, Any]] = {
            "repo_alice_01": {
                "_id": "repo_alice_01",
                "userId": "user_alice",
                "fullName": "alice/project",
                "enabled": True,
            },
            "repo_bob_02": {
                "_id": "repo_bob_02",
                "userId": "user_bob",
                "fullName": "bob/secret-project",
                "enabled": True,
            },
        }

    @property
    def is_configured(self) -> bool:
        return True

    def get_user_by_id(self, user_id: str) -> dict[str, Any] | None:
        return self.users.get(user_id)

    def list_repositories_for_user(self, user_id: str) -> list[dict[str, Any]]:
        return [r for r in self.repositories.values() if r.get("userId") == user_id and r.get("enabled")]

    def get_or_create_repository(self, *, user_id: str, full_name: str, default_branch: str | None = "main") -> str:
        repo_id = f"repo_{user_id}_{len(self.repositories) + 1}"
        self.repositories[repo_id] = {
            "_id": repo_id,
            "userId": user_id,
            "fullName": full_name,
            "defaultBranch": default_branch or "main",
            "enabled": True,
        }
        return repo_id

    def remove_repository_for_user(self, *, user_id: str, repository_id: str) -> str:
        repo = self.repositories.get(repository_id)
        if not repo:
            raise ValueError("Repository not found")
        if repo.get("userId") != user_id:
            raise PermissionError("Unauthorized: You do not own this repository")
        repo["enabled"] = False
        return repository_id


@pytest.fixture
def client_with_mock_convex(monkeypatch: pytest.MonkeyPatch) -> TestClient:
    settings = Settings(
        app_env="test",
        session_secret="test-secret-key-32-bytes-minimum-length-ok",
        convex_url="https://mock.convex.cloud",
    )

    def _mock_gateway(s: Settings) -> MockConvexPortalGateway:
        return MockConvexPortalGateway(s)

    monkeypatch.setattr("app.api.portal.get_settings", lambda: settings)
    monkeypatch.setattr("app.api.session_auth.get_settings", lambda: settings)
    monkeypatch.setattr("app.api.portal.ConvexGateway", _mock_gateway)
    monkeypatch.setattr("app.api.session_auth.ConvexGateway", _mock_gateway)
    return TestClient(app)


def test_portal_routes_reject_unauthenticated_requests(client_with_mock_convex: TestClient) -> None:
    # 1. Profile
    res = client_with_mock_convex.get("/api/portal/profile")
    assert res.status_code == 401
    assert "session" in res.json()["detail"].lower()

    # 2. Preferences
    res = client_with_mock_convex.get("/api/portal/preferences")
    assert res.status_code == 401

    # 3. Repositories list
    res = client_with_mock_convex.get("/api/portal/repositories")
    assert res.status_code == 401

    # 4. Add repository
    res = client_with_mock_convex.post("/api/portal/repositories", json={"full_name": "attacker/repo"})
    assert res.status_code == 401

    # 5. Delete repository
    res = client_with_mock_convex.delete("/api/portal/repositories/repo_alice_01")
    assert res.status_code == 401

    # 6. Social accounts
    res = client_with_mock_convex.get("/api/portal/social-accounts")
    assert res.status_code == 401


def test_portal_routes_reject_forged_or_tampered_cookie(client_with_mock_convex: TestClient) -> None:
    client_with_mock_convex.cookies.set(SESSION_COOKIE_NAME, "forged.payload.fake_signature")

    res = client_with_mock_convex.get("/api/portal/profile")
    assert res.status_code == 401


def test_cross_tenant_repository_deletion_rejected_on_live_route(client_with_mock_convex: TestClient) -> None:
    settings = Settings(
        app_env="test",
        session_secret="test-secret-key-32-bytes-minimum-length-ok",
    )
    sessions = SessionManager(settings)

    # Bob logs in and gets a legitimate signed session cookie
    bob_cookie_value = sessions.create_session("user_bob")
    client_with_mock_convex.cookies.set(SESSION_COOKIE_NAME, bob_cookie_value)

    # Bob verifies his profile -> OK
    res = client_with_mock_convex.get("/api/portal/profile")
    assert res.status_code == 200
    assert res.json()["userId"] == "user_bob"

    # Bob tries to DELETE Alice's repository -> Negative test: 403 Forbidden!
    del_res = client_with_mock_convex.delete("/api/portal/repositories/repo_alice_01")
    assert del_res.status_code == 403
    assert "Unauthorized" in del_res.json()["detail"]


def test_authenticated_user_only_receives_own_repositories(client_with_mock_convex: TestClient) -> None:
    settings = Settings(
        app_env="test",
        session_secret="test-secret-key-32-bytes-minimum-length-ok",
    )
    sessions = SessionManager(settings)

    # Alice logs in
    alice_cookie_value = sessions.create_session("user_alice")
    client_with_mock_convex.cookies.set(SESSION_COOKIE_NAME, alice_cookie_value)

    # Alice requests repositories
    res = client_with_mock_convex.get("/api/portal/repositories")
    assert res.status_code == 200
    data = res.json()
    assert data["userId"] == "user_alice"
    # Alice should see her own repository, but NOT Bob's secret repository
    repo_names = [r["fullName"] for r in data["repositories"]]
    assert "alice/project" in repo_names
    assert "bob/secret-project" not in repo_names
