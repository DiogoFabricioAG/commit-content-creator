import hashlib
import hmac
from typing import Any, cast

from app.schemas.kapso import KapsoInboundMessage


class InvalidKapsoSignature(ValueError):
    """Raised when a Kapso webhook cannot be authenticated."""


def _normalize_phone_number(phone: str) -> str:
    normalized = phone.strip()
    if normalized.isdigit():
        return f"+{normalized}"
    return normalized


def verify_kapso_signature(
    body: bytes,
    signature: str | None,
    secret: str | None,
) -> None:
    if not secret or not signature:
        raise InvalidKapsoSignature("Kapso signature and webhook secret are required")

    expected = (
        "sha256="
        + hmac.new(
            secret.encode("utf-8"),
            body,
            hashlib.sha256,
        ).hexdigest()
    )

    # Compare directly or with prefix
    sig = signature if signature.startswith("sha256=") else f"sha256={signature}"

    if not hmac.compare_digest(expected, sig):
        raise InvalidKapsoSignature("Kapso signature does not match")


def _parse_kapso_message(payload: dict[str, Any]) -> KapsoInboundMessage | None:
    raw_data = payload.get("data")
    data = cast(dict[str, Any], raw_data) if isinstance(raw_data, dict) else payload

    raw_message = data.get("message")
    message = cast(dict[str, Any], raw_message) if isinstance(raw_message, dict) else data
    raw_kapso = message.get("kapso")
    kapso = cast(dict[str, Any], raw_kapso) if isinstance(raw_kapso, dict) else {}
    raw_conversation = data.get("conversation")
    conversation = (
        cast(dict[str, Any], raw_conversation)
        if isinstance(raw_conversation, dict)
        else {}
    )

    from_phone = ""
    for candidate in [
        message.get("from"),
        message.get("from_phone"),
        message.get("sender"),
        message.get("phone_number"),
        kapso.get("phone_number"),
        kapso.get("from"),
        data.get("from"),
        data.get("from_phone"),
        conversation.get("phone_number"),
        payload.get("from"),
    ]:
        if isinstance(candidate, str) and candidate.strip():
            from_phone = candidate.strip()
            break

    body = ""
    raw_text = message.get("text")
    text_obj = cast(dict[str, Any], raw_text) if isinstance(raw_text, dict) else None
    raw_interactive = message.get("interactive")
    interactive = (
        cast(dict[str, Any], raw_interactive)
        if isinstance(raw_interactive, dict)
        else {}
    )
    raw_button_reply = interactive.get("button_reply")
    button_reply = (
        cast(dict[str, Any], raw_button_reply)
        if isinstance(raw_button_reply, dict)
        else {}
    )
    raw_interactive_data = message.get("interactive_data") or kapso.get(
        "interactive_data"
    )
    interactive_data = (
        cast(dict[str, Any], raw_interactive_data)
        if isinstance(raw_interactive_data, dict)
        else {}
    )
    raw_data_button_reply = interactive_data.get("button_reply")
    data_button_reply = (
        cast(dict[str, Any], raw_data_button_reply)
        if isinstance(raw_data_button_reply, dict)
        else {}
    )
    button_id = (
        button_reply.get("id")
        or data_button_reply.get("id")
        or message.get("reply_option_id")
        or kapso.get("reply_option_id")
        or message.get("button_id")
        or kapso.get("button_id")
    )
    button_title = (
        button_reply.get("title")
        or data_button_reply.get("title")
        or message.get("reply_option_title")
        or kapso.get("reply_option_title")
        or message.get("button_title")
        or kapso.get("button_title")
    )
    for candidate in [
        message.get("body"),
        text_obj.get("body") if text_obj else None,
        message.get("content"),
        message.get("text_body"),
        kapso.get("content"),
        data.get("body"),
        data.get("text"),
        payload.get("body"),
        button_title,
    ]:
        if isinstance(candidate, str) and candidate.strip():
            body = candidate.strip()
            break

    message_id = str(
        message.get("id")
        or message.get("message_id")
        or data.get("id")
        or f"msg_{abs(hash(body + from_phone))}"
    )
    timestamp_value = message.get("timestamp") or data.get("timestamp")
    message_type = str(
        message.get("type") or ("interactive" if button_id else "text")
    )

    if not from_phone or not body:
        return None

    return KapsoInboundMessage(
        message_id=message_id,
        from_phone=_normalize_phone_number(from_phone),
        body=body,
        timestamp=int(timestamp_value or 0),
        message_type=message_type,
        button_id=str(button_id) if button_id else None,
        button_title=str(button_title) if button_title else None,
        raw_payload=payload,
    )


def parse_kapso_inbound_messages(payload: dict[str, Any]) -> list[KapsoInboundMessage]:
    raw_data = payload.get("data")
    if isinstance(raw_data, list):
        parsed_messages: list[KapsoInboundMessage] = []
        for raw_item in cast(list[Any], raw_data):
            if isinstance(raw_item, dict):
                inbound = _parse_kapso_message(cast(dict[str, Any], raw_item))
                if inbound:
                    parsed_messages.append(inbound)
        return parsed_messages

    inbound = _parse_kapso_message(payload)
    return [inbound] if inbound else []


def parse_kapso_inbound_message(payload: dict[str, Any]) -> KapsoInboundMessage | None:
    messages = parse_kapso_inbound_messages(payload)
    return messages[0] if messages else None


def requests_image_generation(message: str) -> bool:
    lowered = message.lower()
    return "imagen" in lowered or "image" in lowered or "foto" in lowered or "picture" in lowered

