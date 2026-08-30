from app.github.story_batching import (
    LARGE_COMMIT_LINE_THRESHOLD,
    select_narrative_batch,
    should_emit_narrative,
)
from app.schemas.github import NormalizedCommit


def _commit(*, additions: int = 20, deletions: int = 0) -> NormalizedCommit:
    return NormalizedCommit(
        sha="sha-1",
        author="Developer",
        message="feat: small change",
        committed_at=1,
        additions=additions,
        deletions=deletions,
        changed_files=1,
    )


def test_small_single_commit_waits_for_a_narrative_batch() -> None:
    assert should_emit_narrative([_commit()]) is False
    assert should_emit_narrative([_commit(), _commit()]) is True


def test_large_single_commit_can_be_published_immediately() -> None:
    assert should_emit_narrative([_commit(additions=LARGE_COMMIT_LINE_THRESHOLD)]) is True


def test_batch_selection_keeps_recent_unclustered_commits() -> None:
    records = [
        {"_id": "old", "createdAt": 1_000, "branch": "main"},
        {"_id": "previous", "createdAt": 10_000, "branch": "main"},
        {"_id": "current", "createdAt": 20_000, "branch": "main"},
        {"_id": "other-branch", "createdAt": 20_001, "branch": "dev"},
    ]
    selected = select_narrative_batch(
        records,
        clustered_commit_ids={"old"},
        current_commit_ids={"current"},
        branch="main",
        window_ms=15_000,
    )

    assert [record["_id"] for record in selected] == ["previous", "current"]
