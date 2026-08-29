from typing import Literal

from pydantic import BaseModel, Field


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
