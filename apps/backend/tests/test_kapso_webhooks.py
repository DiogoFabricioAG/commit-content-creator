import hashlib
import hmac

import pytest
from app.whatsapp.kapso.webhooks import (
    InvalidKapsoSignature,
    parse_kapso_inbound_message,
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
