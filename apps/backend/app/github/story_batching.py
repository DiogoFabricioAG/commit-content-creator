from collections.abc import Sequence
from typing import Any

from app.schemas.github import NormalizedCommit

STORY_BATCH_WINDOW_MS = 30 * 60 * 1000
STORY_BATCH_MAX_COMMITS = 8
LARGE_COMMIT_FILE_THRESHOLD = 8
LARGE_COMMIT_LINE_THRESHOLD = 300


def is_substantial_commit(commit: NormalizedCommit) -> bool:
    """Allow a genuinely large change to become a story on its own."""
    changed_lines = commit.additions + commit.deletions
    return (
        commit.changed_files >= LARGE_COMMIT_FILE_THRESHOLD
        or len(commit.files) >= LARGE_COMMIT_FILE_THRESHOLD
        or changed_lines >= LARGE_COMMIT_LINE_THRESHOLD
    )


def select_narrative_batch(
    records: Sequence[dict[str, Any]],
    *,
    clustered_commit_ids: set[str],
    current_commit_ids: set[str],
    branch: str | None,
    max_commits: int = STORY_BATCH_MAX_COMMITS,
    window_ms: int = STORY_BATCH_WINDOW_MS,
) -> list[dict[str, Any]]:
    """Select recent, unclustered commits that can form one narrative."""
    current_records = [
        record
        for record in records
        if str(record.get("_id") or "") in current_commit_ids
    ]
    latest_created_at = max(
        (int(record.get("createdAt") or 0) for record in current_records),
        default=0,
    )
    cutoff = latest_created_at - window_ms if latest_created_at else None

    candidates: list[dict[str, Any]] = []
    for record in records:
        commit_id = str(record.get("_id") or "")
        if not commit_id or commit_id in clustered_commit_ids:
            continue

        record_branch = record.get("branch")
        if branch and isinstance(record_branch, str) and record_branch != branch:
            continue

        created_at = int(record.get("createdAt") or 0)
        is_current = commit_id in current_commit_ids
        if not is_current and cutoff is not None and created_at < cutoff:
            continue
        candidates.append(record)

    candidates.sort(key=lambda record: int(record.get("createdAt") or 0))
    return candidates[-max_commits:]


def should_emit_narrative(commits: Sequence[NormalizedCommit]) -> bool:
    """Emit after a small batch, or immediately for a substantial single commit."""
    return len(commits) >= 2 or any(is_substantial_commit(commit) for commit in commits)
