from typing import Literal

from pydantic import BaseModel, Field


class ContentMedia(BaseModel):
    kind: Literal["image", "video", "architecture"]
    mime_type: str
    url: str | None = None
    alt_text: str = ""
    title: str | None = None
    provider_asset_id: str | None = None
    source: str = "generated"


class LinkedInDraftResult(BaseModel):
    title: str = Field(description="Headline / title of the post")
    body: str = Field(description="Full text of the LinkedIn post")
    format: Literal[
        "problem_solution",
        "before_after",
        "build_log",
        "architecture_breakdown",
        "failure_story",
        "mini_case_study",
    ] = Field(default="problem_solution")
    format_rationale: str = Field(
        default="", description="Why this format was chosen for the story"
    )
    grounded_claims: list[str] = Field(
        default_factory=list, description="List of factual claims grounded in repository evidence"
    )
    media: list[ContentMedia] = Field(
        default=[],
        description="Media assets attached to this version without embedding binary data",
    )
