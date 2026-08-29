from typing import Literal

from pydantic import BaseModel, Field


class NormalizedGitHubEvent(BaseModel):
    delivery_id: str = Field(min_length=1)
    event_type: Literal["push", "pull_request"]
    repository_full_name: str = Field(min_length=1)
    branch: str | None = None
    commit_shas: list[str] = Field(default_factory=list, max_length=100)
    action: str | None = None
