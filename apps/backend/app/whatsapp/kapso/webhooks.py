import hashlib
import hmac
from typing import Any, cast

from app.schemas.kapso import KapsoInboundMessage


class InvalidKapsoSignature(ValueError):
    """Raised when a Kapso webhook cannot be authenticated."""


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


def parse_kapso_inbound_message(payload: dict[str, Any]) -> KapsoInboundMessage | None:
    raw_data = payload.get("data")
    data = cast(dict[str, Any], raw_data) if isinstance(raw_data, dict) else payload

    raw_message = data.get("message")
    message = cast(dict[str, Any], raw_message) if isinstance(raw_message, dict) else data

    from_phone = ""
    for candidate in [
        message.get("from"),
        message.get("from_phone"),
        message.get("sender"),
        data.get("from"),
        data.get("from_phone"),
        payload.get("from"),
    ]:
        if isinstance(candidate, str) and candidate.strip():
            from_phone = candidate.strip()
            break

    body = ""
    raw_text = message.get("text")
    text_obj = cast(dict[str, Any], raw_text) if isinstance(raw_text, dict) else None
    for candidate in [
        message.get("body"),
        text_obj.get("body") if text_obj else None,
        message.get("content"),
        data.get("body"),
        data.get("text"),
        payload.get("body"),
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

    if not from_phone or not body:
        return None

    return KapsoInboundMessage(
        message_id=message_id,
        from_phone=from_phone,
        body=body,
        timestamp=int(data.get("timestamp") or 0),
        raw_payload=payload,
    )
