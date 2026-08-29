import hashlib
import hmac

import pytest
from app.whatsapp.kapso.webhooks import (
    InvalidKapsoSignature,
    parse_kapso_inbound_message,
    parse_kapso_inbound_messages,
    verify_kapso_signature,
)


def test_verify_kapso_signature() -> None:
    secret = "test_kapso_secret"
    body = b'{"event": "whatsapp.message.received"}'
    valid_sig = "sha256=" + hmac.new(secret.encode(), body, hashlib.sha256).hexdigest()

    # Valid
    verify_kapso_signature(body, valid_sig, secret)

    # Invalid
    with pytest.raises(InvalidKapsoSignature):
        verify_kapso_signature(body, "sha256=invalidsig", secret)


def test_parse_kapso_inbound_message() -> None:
    payload = {
        "event": "whatsapp.message.received",
        "data": {
            "from": "+51999888777",
            "message": {"id": "msg_123", "body": "Ta bueno publícalo"},
        },
    }
    inbound = parse_kapso_inbound_message(payload)
    assert inbound is not None
    assert inbound.from_phone == "+51999888777"
    assert inbound.body == "Ta bueno publícalo"


def test_parse_kapso_v2_message_uses_kapso_phone_number() -> None:
    payload = {
        "event": "whatsapp.message.received",
        "data": {
            "phone_number_id": "123456789",
            "message": {
                "id": "wamid.v2-123",
                "type": "text",
                "text": {"body": "publícalo"},
                "kapso": {
                    "direction": "inbound",
                    "origin": "cloud_api",
                    "phone_number": "+51923790280",
                },
            },
            "conversation": {"phone_number": "+51923790280"},
        },
    }

    inbound = parse_kapso_inbound_message(payload)

    assert inbound is not None
    assert inbound.message_id == "wamid.v2-123"
    assert inbound.from_phone == "+51923790280"
    assert inbound.body == "publícalo"


def test_parse_kapso_normalizes_meta_phone_number_without_plus() -> None:
    payload = {
        "data": {
            "message": {
                "id": "wamid.meta-123",
                "from": "51923790280",
                "text": {"body": "publícalo"},
            }
        }
    }

    inbound = parse_kapso_inbound_message(payload)

    assert inbound is not None
    assert inbound.from_phone == "+51923790280"


def test_parse_kapso_buffered_v2_messages() -> None:
    payload = {
        "type": "whatsapp.message.received",
        "batch": True,
        "data": [
            {
                "message": {
                    "id": "wamid.batch-1",
                    "text": {"body": "sí"},
                    "kapso": {"phone_number": "+51923790280"},
                }
            },
            {
                "message": {
                    "id": "wamid.batch-2",
                    "text": {"body": "publícalo"},
                    "kapso": {"phone_number": "+51923790280"},
                }
            },
        ],
    }

    inbounds = parse_kapso_inbound_messages(payload)

    assert [inbound.message_id for inbound in inbounds] == [
        "wamid.batch-1",
        "wamid.batch-2",
    ]
