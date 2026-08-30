import hashlib
import hmac
from collections.abc import Mapping
from typing import Any, cast

from app.schemas.github import NormalizedGitHubEvent


class InvalidGitHubSignature(ValueError):
    """Raised when a GitHub webhook cannot be authenticated."""


class InvalidGitHubPayload(ValueError):
    """Raised when a supported GitHub event cannot be normalized."""


def verify_github_signature(body: bytes, signature: str | None, secret: str | None) -> None:
    if not secret or not signature:
        raise InvalidGitHubSignature("GitHub signature and webhook secret are required")

    if not signature.startswith("sha256="):
        raise InvalidGitHubSignature("GitHub signature must use sha256")

    expected = (
        "sha256="
        + hmac.new(
            secret.encode("utf-8"),
            body,
            hashlib.sha256,
        ).hexdigest()
    )

    if not hmac.compare_digest(expected, signature):
        raise InvalidGitHubSignature("GitHub signature does not match")


def normalize_github_event(
    *,
    event_type: str,
    delivery_id: str,
    payload: Mapping[str, Any],
) -> NormalizedGitHubEvent:
    if not delivery_id:
        raise InvalidGitHubPayload("GitHub delivery id is required")

    repository = _mapping_value(payload, "repository")
    repository_full_name = _string_value(repository, "full_name")

    if event_type == "push":
        ref = _string_value(payload, "ref")
        commits = payload.get("commits", [])
        if not isinstance(commits, list):
            raise InvalidGitHubPayload("GitHub push commits must be a list")

        commit_shas: list[str] = []
        for raw_commit in cast(list[Any], commits):
            if not isinstance(raw_commit, Mapping):
                continue
            commit = cast(Mapping[str, Any], raw_commit)
            commit_id = commit.get("id")
            if isinstance(commit_id, str):
                commit_shas.append(commit_id)

        # Very large pushes can contain more than the per-event processing
        # budget. Keep the newest commits so the webhook is accepted and the
        # processor does not leave the delivery in a failed state.
        return NormalizedGitHubEvent(
            delivery_id=delivery_id,
            event_type="push",
            repository_full_name=repository_full_name,
            branch=ref.removeprefix("refs/heads/"),
            commit_shas=commit_shas[-100:],
        )

    if event_type == "pull_request":
        pull_request = _mapping_value(payload, "pull_request")
        head = _mapping_value(pull_request, "head")
        head_sha = head.get("sha")
        return NormalizedGitHubEvent(
            delivery_id=delivery_id,
            event_type="pull_request",
            repository_full_name=repository_full_name,
            branch=_optional_string(head, "ref"),
            commit_shas=[head_sha] if isinstance(head_sha, str) else [],
            action=_optional_string(payload, "action"),
        )

    raise InvalidGitHubPayload(f"Unsupported GitHub event type: {event_type}")


def _mapping_value(payload: Mapping[str, Any], key: str) -> Mapping[str, Any]:
    value = payload.get(key)
    if not isinstance(value, Mapping):
        raise InvalidGitHubPayload(f"GitHub payload field {key} must be an object")
    return cast(Mapping[str, Any], value)


def _string_value(payload: Mapping[str, Any], key: str) -> str:
    value = payload.get(key)
    if not isinstance(value, str) or not value:
        raise InvalidGitHubPayload(f"GitHub payload field {key} must be a non-empty string")
    return value


def _optional_string(payload: Mapping[str, Any], key: str) -> str | None:
    value = payload.get(key)
    return value if isinstance(value, str) else None
