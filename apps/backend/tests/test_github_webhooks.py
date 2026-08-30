import hashlib
import hmac

import pytest
from app.github.webhooks import (
    InvalidGitHubPayload,
    InvalidGitHubSignature,
    normalize_github_event,
    verify_github_signature,
)


def test_github_signature_uses_raw_body_and_sha256() -> None:
    body = b'{"zen":"keep it simple"}'
    secret = "local-test-secret"
    digest = hmac.new(secret.encode(), body, hashlib.sha256).hexdigest()

    verify_github_signature(body, f"sha256={digest}", secret)


def test_github_signature_rejects_modified_body() -> None:
    with pytest.raises(InvalidGitHubSignature):
        verify_github_signature(
            b'{"changed":true}',
            "sha256=not-the-real-signature",
            "local-test-secret",
        )


def test_push_event_is_normalized_for_convex() -> None:
    event = normalize_github_event(
        event_type="push",
        delivery_id="delivery-001",
        payload={
            "ref": "refs/heads/main",
            "repository": {"full_name": "demo/notifications"},
            "commits": [{"id": "sha-001"}, {"id": "sha-002"}],
        },
    )

    assert event.model_dump() == {
        "delivery_id": "delivery-001",
        "event_type": "push",
        "repository_full_name": "demo/notifications",
        "branch": "main",
        "commit_shas": ["sha-001", "sha-002"],
        "action": None,
    }


def test_normalize_large_push_keeps_newest_processing_budget() -> None:
    payload = {
        "ref": "refs/heads/main",
        "repository": {"full_name": "demo/large-repo"},
        "commits": [{"id": f"sha-{index}"} for index in range(103)],
    }

    event = normalize_github_event(
        event_type="push",
        delivery_id="delivery-large",
        payload=payload,
    )

    assert len(event.commit_shas) == 100
    assert event.commit_shas[0] == "sha-3"
    assert event.commit_shas[-1] == "sha-102"


def test_unsupported_event_is_rejected_before_persistence() -> None:
    with pytest.raises(InvalidGitHubPayload):
        normalize_github_event(
            event_type="issues",
            delivery_id="delivery-002",
            payload={"repository": {"full_name": "demo/notifications"}},
        )
