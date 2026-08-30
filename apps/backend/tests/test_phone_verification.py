from typing import Any

import pytest
from app.auth.session import (
    PHONE_CHALLENGE_COOKIE_NAME,
    SessionManager,
)
from app.config import Settings
from app.main import app
from fastapi.testclient import TestClient


class MockPhoneGateway:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self.user = {
            "_id": "user_phone_1",
            "displayName": "Phone owner",
            "whatsappPhone": "+51999888777",
        }
        self.window_open = True

    @property
    def is_configured(self) -> bool:
        return True

    def get_or_create_default_user(
        self,
        whatsapp_phone: str | None = None,
        display_name: str | None = None,
        email: str | None = None,
    ) -> str:
        del display_name, email
        if whatsapp_phone:
            self.user["whatsappPhone"] = whatsapp_phone
        return str(self.user["_id"])

    def is_whatsapp_window_open(self, recipient_phone: str) -> bool:
        return self.window_open and recipient_phone == self.user["whatsappPhone"]

    def get_user_by_id(self, user_id: str) -> dict[str, Any] | None:
        return self.user if user_id == self.user["_id"] else None


class MockKapsoClient:
    sent: list[tuple[str, str]] = []

    def __init__(self, settings: Settings) -> None:
        del settings

    def send_message(self, to_phone: str, body: str) -> Any:
        self.sent.append((to_phone, body))
        return type("Message", (), {"message_id": "kapso_test_1"})()


@pytest.fixture
def phone_client(monkeypatch: pytest.MonkeyPatch) -> TestClient:
    settings = Settings(
        app_env="test",
        session_secret="test-session-secret",
        convex_url="https://mock.convex.cloud",
    )
    MockKapsoClient.sent = []
    monkeypatch.setattr("app.api.session_auth.get_settings", lambda: settings)
    monkeypatch.setattr("app.api.session_auth.ConvexGateway", MockPhoneGateway)
    monkeypatch.setattr("app.api.session_auth.KapsoClient", MockKapsoClient)
    return TestClient(app)


def test_phone_login_requires_an_open_whatsapp_window(
    phone_client: TestClient,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    gateway = MockPhoneGateway(Settings())
    gateway.window_open = False

    def _mock_gw(settings: Settings) -> MockPhoneGateway:
        del settings
        return gateway

    monkeypatch.setattr("app.api.session_auth.ConvexGateway", _mock_gw)

    response = phone_client.post(
        "/auth/session/login",
        json={"phone": "+51999888777", "displayName": "Phone owner"},
    )

    assert response.status_code == 409
    assert response.json()["code"] == "whatsapp_window_closed"
    assert PHONE_CHALLENGE_COOKIE_NAME not in phone_client.cookies


def test_phone_otp_flow_issues_session_only_after_code_verification(
    phone_client: TestClient,
) -> None:
    login_response = phone_client.post(
        "/auth/session/login",
        json={"phone": "+51999888777", "displayName": "Phone owner"},
    )

    assert login_response.status_code == 202
    assert PHONE_CHALLENGE_COOKIE_NAME in phone_client.cookies
    assert len(MockKapsoClient.sent) == 1
    sent_body = MockKapsoClient.sent[0][1]
    verification_code = sent_body.split("código de verificación es ", 1)[1].split(".", 1)[0]

    assert phone_client.get("/auth/session/me").status_code == 401

    invalid_response = phone_client.post(
        "/auth/session/verify",
        json={"code": "000000" if verification_code != "000000" else "111111"},
    )
    assert invalid_response.status_code == 401

    verify_response = phone_client.post(
        "/auth/session/verify",
        json={"code": verification_code},
    )

    assert verify_response.status_code == 200
    assert verify_response.json()["userId"] == "user_phone_1"
    assert PHONE_CHALLENGE_COOKIE_NAME not in phone_client.cookies
    assert phone_client.get("/auth/session/me").status_code == 200


def test_phone_challenge_code_is_signed_and_not_stored_in_plaintext() -> None:
    settings = Settings(app_env="test", session_secret="test-session-secret")
    manager = SessionManager(settings)
    token = manager.create_phone_challenge("user_phone_1", "+51999888777", "123456")

    assert "123456" not in token
