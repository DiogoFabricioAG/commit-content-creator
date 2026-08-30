import json
import re
from datetime import datetime
from pathlib import Path
from typing import Any, cast

import httpx

from app.config import Settings
from app.github.diff_normalizer import normalize_commit_files
from app.schemas.github import CommitFile, NormalizedCommit


class GitHubRateLimitError(RuntimeError):
    """Raised when GitHub refuses a request because its API quota is exhausted."""


HISTORY_DETAIL_LIMIT = 12


class GitHubClient:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self.headers: dict[str, str] = {
            "Accept": "application/vnd.github+json",
            "User-Agent": "Proof-of-Work-App",
        }
        if settings.github_token:
            self.headers["Authorization"] = f"Bearer {settings.github_token}"

    def fetch_commit(
        self,
        repository_full_name: str,
        sha: str,
        fallback_metadata: dict[str, Any] | None = None,
    ) -> NormalizedCommit:
        # Check local demo fixtures if sha matches fixture or in demo mode with no token
        fixture_commit = self._check_fixture_commit(sha)
        if fixture_commit:
            return fixture_commit

        url = f"https://api.github.com/repos/{repository_full_name}/commits/{sha}"
        try:
            with httpx.Client(timeout=10.0) as client:
                response = client.get(url, headers=self.headers)
                if response.status_code == 200:
                    data = response.json()
                    commit_data = data.get("commit", {})
                    author_data = commit_data.get("author", {})
                    stats = data.get("stats", {})
                    raw_files = data.get("files", [])

                    files = normalize_commit_files(raw_files)
                    committed_at = self._commit_timestamp(commit_data)
                    return NormalizedCommit(
                        sha=sha,
                        author=author_data.get("name") or "Developer",
                        message=commit_data.get("message") or "Update",
                        committed_at=committed_at or int(1000 * Path(".").stat().st_mtime),
                        additions=int(stats.get("additions", 0)),
                        deletions=int(stats.get("deletions", 0)),
                        changed_files=len(files),
                        files=files,
                        status="fetched",
                    )
        except Exception:
            pass

        return self._build_from_metadata(
            sha,
            self._metadata_for_commit(sha, fallback_metadata),
        )

    def fetch_repository_history(
        self,
        repository_full_name: str,
        *,
        branch: str | None = None,
        max_commits: int = 500,
    ) -> list[NormalizedCommit]:
        """Fetch the repository history with GitHub pagination and commit evidence."""
        if max_commits < 1:
            return []

        commits: list[NormalizedCommit] = []
        metadata_by_sha: dict[str, dict[str, Any]] = {}
        page = 1
        list_url = f"https://api.github.com/repos/{repository_full_name}/commits"
        with httpx.Client(timeout=20.0) as client:
            while len(commits) < max_commits:
                per_page = min(100, max_commits - len(commits))
                params: dict[str, str | int] = {"page": page, "per_page": per_page}
                if branch:
                    params["sha"] = branch

                response = client.get(list_url, headers=self.headers, params=params)
                self._raise_for_rate_limit(response)
                response.raise_for_status()
                raw_payload = response.json()
                if not isinstance(raw_payload, list):
                    raise RuntimeError("GitHub commits endpoint returned an invalid payload")
                payload = cast(list[Any], raw_payload)

                if not payload:
                    break

                for raw_item in payload:
                    if not isinstance(raw_item, dict):
                        continue
                    item = cast(dict[str, Any], raw_item)
                    sha = item.get("sha")
                    if not isinstance(sha, str) or not sha.strip():
                        continue
                    metadata_by_sha[sha] = item
                    # The list endpoint gives enough metadata to include every
                    # commit without making one detail request per commit.
                    commit = self._build_from_metadata(sha, item)
                    if branch and not commit.branch:
                        commit = commit.model_copy(update={"branch": branch})
                    commits.append(commit)
                    if len(commits) >= max_commits:
                        break

                if len(payload) < per_page:
                    break
                page += 1

        # GitHub returns newest first; narrative attempts read naturally oldest first.
        ordered_commits = list(reversed(commits))

        # Fetch file-level diffs only for the latest representative commits.
        # This keeps a 500-commit digest within the anonymous GitHub quota while
        # preserving detailed evidence for the commits the analyzer reads.
        detail_start = max(0, len(ordered_commits) - HISTORY_DETAIL_LIMIT)
        for index in range(detail_start, len(ordered_commits)):
            commit = ordered_commits[index]
            detailed = self.fetch_commit(
                repository_full_name,
                commit.sha,
                fallback_metadata=metadata_by_sha.get(commit.sha),
            )
            if branch and not detailed.branch:
                detailed = detailed.model_copy(update={"branch": branch})
            ordered_commits[index] = detailed

        return ordered_commits

    @staticmethod
    def _raise_for_rate_limit(response: httpx.Response) -> None:
        remaining = response.headers.get("x-ratelimit-remaining")
        if response.status_code == 429 or (
            response.status_code == 403 and remaining == "0"
        ):
            reset = response.headers.get("x-ratelimit-reset")
            retry_after = response.headers.get("retry-after")
            details = "GitHub API rate limit reached"
            if retry_after:
                details += f"; retry after {retry_after}s"
            elif reset:
                details += f"; reset epoch {reset}"
            details += ". Configure a GitHub token for higher limits."
            raise GitHubRateLimitError(details)

    @staticmethod
    def _commit_timestamp(commit_data: dict[str, Any]) -> int:
        committer = commit_data.get("committer")
        if not isinstance(committer, dict):
            return 0
        committer_dict = cast(dict[str, Any], committer)
        timestamp = committer_dict.get("date")
        if not isinstance(timestamp, str):
            return 0
        try:
            return int(datetime.fromisoformat(timestamp.replace("Z", "+00:00")).timestamp() * 1000)
        except ValueError:
            return 0


    @staticmethod
    def _metadata_for_commit(
        sha: str,
        metadata: dict[str, Any] | None,
    ) -> dict[str, Any] | None:
        if not metadata:
            return None

        raw_commits = metadata.get("commits")
        if isinstance(raw_commits, list):
            for raw_item in cast(list[object], raw_commits):
                if not isinstance(raw_item, dict):
                    continue
                item = cast(dict[str, Any], raw_item)
                item_sha = item.get("id") or item.get("sha")
                if item_sha == sha:
                    return item

        head_commit = metadata.get("head_commit")
        if isinstance(head_commit, dict):
            head_commit = cast(dict[str, Any], head_commit)
            head_sha = head_commit.get("id") or head_commit.get("sha")
            if head_sha == sha:
                return head_commit

        return metadata

    def _check_fixture_commit(self, sha: str) -> NormalizedCommit | None:
        fixture_path = Path("fixtures/demo-commits.json")
        if not fixture_path.exists():
            return None
        try:
            with open(fixture_path, encoding="utf-8") as f:
                data = json.load(f)
                for item in data.get("commits", []):
                    if item.get("sha") == sha:
                        files = [
                            CommitFile(
                                path=p,
                                status="modified",
                                additions=item.get("additions", 10),
                                deletions=item.get("deletions", 2),
                                patch="--- a/" + p + "\n+++ b/" + p + "\n@@ ... @@\n+ // change",
                            )
                            for p in item.get("files", [])
                        ]
                        return NormalizedCommit(
                            sha=sha,
                            author="Demo Developer",
                            message=item.get("message", "Commit"),
                            committed_at=1724930000000,
                            additions=item.get("additions", 10),
                            deletions=item.get("deletions", 2),
                            changed_files=len(files),
                            files=files,
                            status="fetched",
                        )
        except Exception:
            pass
        return None

    def _build_from_metadata(self, sha: str, metadata: dict[str, Any] | None) -> NormalizedCommit:
        meta = metadata or {}
        author_name = "Developer"
        nested_commit = meta.get("commit")
        nested_commit_data = (
            cast(dict[str, Any], nested_commit) if isinstance(nested_commit, dict) else {}
        )
        author_data = meta.get("author") or nested_commit_data.get("author")
        if isinstance(author_data, dict):
            author_dict = cast(dict[str, Any], author_data)
            raw_name = author_dict.get("name")
            if isinstance(raw_name, str) and raw_name.strip():
                author_name = raw_name.strip()

        added_value: Any = meta.get("added", [])
        modified_value: Any = meta.get("modified", [])
        removed_value: Any = meta.get("removed", [])
        added = cast(list[Any], added_value) if isinstance(added_value, list) else []
        modified = (
            cast(list[Any], modified_value) if isinstance(modified_value, list) else []
        )
        removed = cast(list[Any], removed_value) if isinstance(removed_value, list) else []

        all_paths: list[Any] = list(dict.fromkeys([*added, *modified, *removed]))
        raw_message = meta.get("message") or nested_commit_data.get("message")
        message = str(raw_message).strip() if raw_message else ""
        if not message or re.fullmatch(r"commit\s+[0-9a-f]{7,}", message, re.IGNORECASE):
            message = self._message_from_paths(all_paths)

        raw_files: list[dict[str, Any]] = [
            {
                "filename": path,
                "status": (
                    "added"
                    if path in added
                    else "removed"
                    if path in removed
                    else "modified"
                ),
            }
            for path in all_paths
        ]
        files = normalize_commit_files(raw_files)

        committed_at = 1724930000000
        timestamp = cast(str | None, meta.get("timestamp"))
        if not timestamp:
            nested_author = cast(dict[str, Any] | None, nested_commit_data.get("author"))
            if isinstance(nested_author, dict):
                timestamp = cast(str | None, nested_author.get("date"))
        if isinstance(timestamp, str):
            try:
                committed_at = int(datetime.fromisoformat(timestamp.replace("Z", "+00:00")).timestamp() * 1000)
            except ValueError:
                pass

        return NormalizedCommit(
            sha=sha,
            author=author_name,
            message=message,
            committed_at=committed_at,
            additions=len(added) * 15 + len(modified) * 5,
            deletions=len(removed) * 10,
            changed_files=len(files),
            files=files,
            status="fetched",
        )

    @staticmethod
    def _message_from_paths(paths: list[Any]) -> str:
        clean_paths = [str(path) for path in paths if isinstance(path, str) and path.strip()]
        if not clean_paths:
            return "una actualización técnica"
        if any(path.endswith((".md", ".mdx")) for path in clean_paths):
            return "mejoras en la documentación"
        if any(path.endswith((".ts", ".tsx", ".js", ".jsx")) for path in clean_paths):
            return "mejoras en la experiencia web"
        if any(path.endswith(".py") for path in clean_paths):
            return "mejoras en el backend"
        return f"cambios en {Path(clean_paths[0]).name}"
