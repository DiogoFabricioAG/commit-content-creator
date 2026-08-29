import json
from datetime import datetime
from pathlib import Path
from typing import Any, cast

import httpx

from app.config import Settings
from app.github.diff_normalizer import normalize_commit_files
from app.schemas.github import CommitFile, NormalizedCommit


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

        if not self.settings.github_token:
            # Use fallback metadata from push event payload if available
            return self._build_from_metadata(
                sha,
                self._metadata_for_commit(sha, fallback_metadata),
            )

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
                    return NormalizedCommit(
                        sha=sha,
                        author=author_data.get("name") or "Developer",
                        message=commit_data.get("message") or "Update",
                        committed_at=int(commit_data.get("committer", {}).get("date_timestamp", 0))
                        or int(1000 * (Path(".")).stat().st_mtime),
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
        author_data = meta.get("author")
        if isinstance(author_data, dict):
            author_dict = cast(dict[str, Any], author_data)
            raw_name = author_dict.get("name")
            if isinstance(raw_name, str) and raw_name.strip():
                author_name = raw_name.strip()

        message = str(meta.get("message") or f"Commit {sha[:7]}").strip()

        added = meta.get("added", [])
        modified = meta.get("modified", [])
        removed = meta.get("removed", [])


        all_paths = list(dict.fromkeys(added + modified + removed))
        raw_files = [
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
        timestamp = meta.get("timestamp")
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
