from typing import Any

from app.config import Settings
from app.integrations.convex_client import ConvexGateway
from app.schemas.github import CommitFile, NormalizedCommit


def test_record_commit_omits_null_optional_file_patch() -> None:
    captured: dict[str, Any] = {}

    class FakeClient:
        def mutation(self, name: str, payload: dict[str, Any]) -> dict[str, str]:
            captured["name"] = name
            captured["payload"] = payload
            return {"commitId": "commit-1"}

    gateway = ConvexGateway(Settings(convex_url="https://example.convex.cloud"))
    gateway._client = FakeClient()  # type: ignore[assignment]

    result = gateway.record_commit(
        "repository-1",
        NormalizedCommit(
            sha="sha-1",
            author="Developer",
            message="feat: add fallback",
            committed_at=1,
            files=[CommitFile(path="README.md")],
        ),
    )

    assert result == {"commitId": "commit-1"}
    assert captured["name"] == "commits:record"
    assert captured["payload"]["files"] == [
        {
            "path": "README.md",
            "status": "modified",
            "additions": 0,
            "deletions": 0,
        }
    ]
