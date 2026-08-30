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


def test_send_draft_for_approval_uses_interactive_buttons(monkeypatch: Any) -> None:
    captured: dict[str, Any] = {}

    class FakeResponse:
        def raise_for_status(self) -> None:
            return None

        def json(self) -> dict[str, list[dict[str, str]]]:
            return {"messages": [{"id": "wamid.button-123"}]}

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
    result = KapsoClient(settings).send_draft_for_approval(
        to_phone="+51999888777",
        story_title="Historia de prueba",
        post_body="Resumen técnico.",
    )

    assert result.message_id == "wamid.button-123"
    assert result.message_type == "interactive"
    assert captured["json"]["type"] == "interactive"
    assert captured["json"]["interactive"]["type"] == "button"
    assert "Encontré una historia para LinkedIn (V1)" in captured["json"]["interactive"]["body"]["text"]
    assert [
        button["reply"]["id"]
        for button in captured["json"]["interactive"]["action"]["buttons"]
    ] == ["approval_review", "approval_publish", "approval_reject"]


def test_send_draft_v2_keeps_text_image_and_buttons_in_one_message(monkeypatch: Any) -> None:
    captured: list[dict[str, Any]] = []

    class FakeResponse:
        def raise_for_status(self) -> None:
            return None

        def json(self) -> dict[str, list[dict[str, str]]]:
            return {"messages": [{"id": "wamid.v2-123"}]}

    class FakeClient:
        def __init__(self, **kwargs: Any) -> None:
            del kwargs

        def __enter__(self) -> "FakeClient":
            return self

        def __exit__(self, *args: Any) -> None:
            return None

        def post(self, url: str, *, headers: dict[str, str], json: dict[str, Any]) -> FakeResponse:
            del url, headers
            captured.append(json)
            return FakeResponse()

    monkeypatch.setattr(httpx, "Client", FakeClient)

    settings = Settings(
        demo_mode=False,
        kapso_api_key="test-api-key",
        kapso_phone_number_id="123456789",
    )
    result = KapsoClient(settings).send_draft_for_approval(
        to_phone="+51999888777",
        story_title="Historia revisada",
        post_body="Cambios propuestos.",
        version=2,
        image_url="https://cdn.example/visual.png",
    )

    assert result.message_id == "wamid.v2-123"
    assert len(captured) == 1
    interactive = captured[0]["interactive"]
    assert "Aquí tienes los cambios propuestos para la V2" in interactive["body"]["text"]
    assert "Encontré una historia para LinkedIn (V1)" not in interactive["body"]["text"]
    assert interactive["header"] == {
        "type": "image",
        "image": {"link": "https://cdn.example/visual.png"},
    }


def test_send_long_draft_preserves_full_text_and_buttons(monkeypatch: Any) -> None:
    captured: list[dict[str, Any]] = []

    class FakeResponse:
        def raise_for_status(self) -> None:
            return None

        def json(self) -> dict[str, list[dict[str, str]]]:
            return {"messages": [{"id": f"wamid.long-{len(captured)}"}]}

    class FakeClient:
        def __init__(self, **kwargs: Any) -> None:
            del kwargs

        def __enter__(self) -> "FakeClient":
            return self

        def __exit__(self, *args: Any) -> None:
            return None

        def post(self, url: str, *, headers: dict[str, str], json: dict[str, Any]) -> FakeResponse:
            del url, headers
            captured.append(json)
            return FakeResponse()

    monkeypatch.setattr(httpx, "Client", FakeClient)

    settings = Settings(
        demo_mode=False,
        kapso_api_key="test-api-key",
        kapso_phone_number_id="123456789",
    )
    result = KapsoClient(settings).send_draft_for_approval(
        to_phone="+51999888777",
        story_title="Historia larga",
        post_body="Qué cambió:\n\n" + ("Resultado verificable. " * 350),
    )

    assert result.message_type == "interactive"
    assert captured[-1]["type"] == "interactive"
    interactive = captured[-1]["interactive"]
    assert len(interactive["body"]["text"]) <= 1024
    assert "Borrador completo enviado arriba" in interactive["body"]["text"]
    assert [
        button["reply"]["id"]
        for button in interactive["action"]["buttons"]
    ] == ["approval_review", "approval_publish", "approval_reject"]

    text_messages = captured[:-1]
    assert text_messages
    assert all(message["type"] == "text" for message in text_messages)
    assert all(len(message["text"]["body"]) <= 4096 for message in text_messages)
    assert "Historia larga" in "\n".join(
        message["text"]["body"] for message in text_messages
    )
    assert "Resultado verificable." in "\n".join(
        message["text"]["body"] for message in text_messages
    )
