# pyright: reportUnknownMemberType=false, reportUnknownVariableType=false

from typing import Any

import httpx
from app.config import Settings
from app.linkedin.publisher import LinkedInPublisher
from app.linkedin.security import encrypt_token
from cryptography.fernet import Fernet


def test_linkedin_publisher_uses_configured_api_version(monkeypatch: Any) -> None:
    captured: dict[str, Any] = {}

    class FakeResponse:
        status_code = 201
        headers = {"x-restli-id": "urn:li:share:live-test-123"}
        text = ""

    class FakeClient:
        def __init__(self, **kwargs: Any) -> None:
            captured["client_kwargs"] = kwargs

        def __enter__(self) -> "FakeClient":
            return self

        def __exit__(self, *args: Any) -> None:
            return None

        def post(self, url: str, *, headers: dict[str, str], json: dict[str, Any]) -> FakeResponse:
            captured["url"] = url
            captured["headers"] = headers
            captured["json"] = json
            return FakeResponse()

    monkeypatch.setattr(httpx, "Client", FakeClient)

    encryption_key = Fernet.generate_key().decode()
    settings = Settings(
        demo_mode=False,
        token_encryption_key=encryption_key,
        linkedin_api_version="202608",
    )
    encrypted_token = encrypt_token("live-token", encryption_key)

    result = LinkedInPublisher(settings).publish_post(
        author_urn="urn:li:person:test-member",
        commentary="Live publication contract test",
        encrypted_access_token=encrypted_token,
    )

    assert result.status == "published"
    assert result.post_urn == "urn:li:share:live-test-123"
    assert captured["url"] == "https://api.linkedin.com/rest/posts"
    assert captured["headers"] == {
        "Authorization": "Bearer live-token",
        "LinkedIn-Version": "202608",
        "X-Restli-Protocol-Version": "2.0.0",
        "Content-Type": "application/json",
    }
