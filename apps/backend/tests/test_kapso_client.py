# pyright: reportUnknownMemberType=false, reportUnknownVariableType=false

from typing import Any

import httpx
from app.config import Settings
from app.whatsapp.kapso.client import KapsoClient


def test_send_message_uses_kapso_meta_whatsapp_api(monkeypatch: Any) -> None:
    captured: dict[str, Any] = {}

    class FakeResponse:
        def raise_for_status(self) -> None:
            return None

        def json(self) -> dict[str, list[dict[str, str]]]:
            return {"messages": [{"id": "wamid.test-123"}]}

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

    settings = Settings(
        demo_mode=False,
        kapso_api_key="test-api-key",
        kapso_phone_number_id="123456789",
    )
    result = KapsoClient(settings).send_message("+51999888777", "Hola desde la prueba")

    assert result.message_id == "wamid.test-123"
    assert captured["url"] == (
        "https://api.kapso.ai/meta/whatsapp/v24.0/123456789/messages"
    )
    assert captured["headers"] == {
        "X-API-Key": "test-api-key",
        "Content-Type": "application/json",
    }
    assert captured["json"] == {
        "messaging_product": "whatsapp",
        "recipient_type": "individual",
        "to": "+51999888777",
        "type": "text",
        "text": {"body": "Hola desde la prueba"},
    }
