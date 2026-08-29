from typing import Literal

from pydantic import BaseModel, Field


class NormalizedGitHubEvent(BaseModel):
    delivery_id: str = Field(min_length=1)
    event_type: Literal["push", "pull_request"]
    repository_full_name: str = Field(min_length=1)
    branch: str | None = None
    commit_shas: list[str] = Field(default_factory=list, max_length=100)
    action: str | None = None


class CommitFile(BaseModel):
    path: str
    status: str = "modified"
    additions: int = 0
    deletions: int = 0
    patch: str | None = None


class NormalizedCommit(BaseModel):
    sha: str
    author: str
    message: str
    committed_at: int
    branch: str | None = None
    additions: int = 0
    deletions: int = 0
    changed_files: int = 0
    files: list[CommitFile] = Field(default_factory=lambda: list[CommitFile]())
    status: Literal["fetched", "analyzing", "analyzed", "ignored", "failed"] = "fetched"
