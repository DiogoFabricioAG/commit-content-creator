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


def test_linkedin_publisher_uploads_image_before_creating_post(monkeypatch: Any) -> None:
    calls: list[tuple[str, str]] = []

    class FakeResponse:
        def __init__(
            self,
            *,
            status_code: int = 200,
            payload: dict[str, Any] | None = None,
            content: bytes = b"png-bytes",
            headers: dict[str, str] | None = None,
        ) -> None:
            self.status_code = status_code
            self._payload = payload or {}
            self.content = content
            self.headers = headers or {}
            self.text = ""

        def raise_for_status(self) -> None:
            return None

        def json(self) -> dict[str, Any]:
            return self._payload

    class FakeClient:
        def __init__(self, **kwargs: Any) -> None:
            return None

        def __enter__(self) -> "FakeClient":
            return self

        def __exit__(self, *args: Any) -> None:
            return None

        def get(self, url: str, **kwargs: Any) -> FakeResponse:
            calls.append(("GET", url))
            if url == "https://cdn.example/image.png":
                return FakeResponse(content=b"generated-png")
            return FakeResponse(payload={"status": "AVAILABLE"})

        def put(self, url: str, **kwargs: Any) -> FakeResponse:
            calls.append(("PUT", url))
            assert kwargs["content"] == b"generated-png"
            return FakeResponse(status_code=201)

        def post(self, url: str, **kwargs: Any) -> FakeResponse:
            calls.append(("POST", url))
            if "images?action=initializeUpload" in url:
                return FakeResponse(
                    payload={
                        "value": {
                            "uploadUrl": "https://upload.example/image",
                            "image": "urn:li:image:test-image",
                        }
                    }
                )
            assert kwargs["json"]["content"]["media"]["id"] == "urn:li:image:test-image"
            return FakeResponse(
                status_code=201,
                headers={"x-restli-id": "urn:li:share:image-test"},
            )

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
        commentary="Image publication contract test",
        encrypted_access_token=encrypted_token,
        media=[
            {
                "kind": "image",
                "url": "https://cdn.example/image.png",
                "mimeType": "image/png",
                "altText": "A generated engineering illustration",
            }
        ],
    )

    assert result.status == "published"
    assert result.post_urn == "urn:li:share:image-test"
    assert calls == [
        ("GET", "https://cdn.example/image.png"),
        ("POST", "https://api.linkedin.com/rest/images?action=initializeUpload"),
        ("PUT", "https://upload.example/image"),
        ("GET", "https://api.linkedin.com/rest/images/urn%3Ali%3Aimage%3Atest-image"),
        ("POST", "https://api.linkedin.com/rest/posts"),
    ]
