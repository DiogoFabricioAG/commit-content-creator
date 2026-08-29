import re
from typing import Any

from app.schemas.github import CommitFile

IGNORED_PATTERNS = [
    r"^.*-lock\.[a-z]+$",
    r"^.*\.lock$",
    r"^node_modules/",
    r"^vendor/",
    r"^\.next/",
    r"^dist/",
    r"^build/",
    r"^.*\.min\.(js|css)$",
    r"^.*\.map$",
    r"^\.pytest_cache/",
    r"^\.ruff_cache/",
    r"^\.venv/",
]

MAX_PATCH_LENGTH = 1500
MAX_FILES_PER_COMMIT = 15


def is_noisy_file(path: str) -> bool:
    normalized = path.replace("\\", "/").lower()
    return any(re.match(pattern, normalized) is not None for pattern in IGNORED_PATTERNS)


def normalize_commit_files(raw_files: list[dict[str, Any]]) -> list[CommitFile]:
    normalized_files: list[CommitFile] = []

    for file_info in raw_files:
        path = str(file_info.get("filename") or file_info.get("path") or "unknown")
        if is_noisy_file(path):
            continue

        raw_patch = file_info.get("patch")
        patch: str | None = None
        if isinstance(raw_patch, str):
            patch = (
                raw_patch[:MAX_PATCH_LENGTH] + "\n... [diff truncated]"
                if len(raw_patch) > MAX_PATCH_LENGTH
                else raw_patch
            )

        status = str(file_info.get("status") or "modified")
        additions = int(file_info.get("additions") or 0)
        deletions = int(file_info.get("deletions") or 0)

        normalized_files.append(
            CommitFile(
                path=path,
                status=status,
                additions=additions,
                deletions=deletions,
                patch=patch,
            )
        )

        if len(normalized_files) >= MAX_FILES_PER_COMMIT:
            break

    return normalized_files
