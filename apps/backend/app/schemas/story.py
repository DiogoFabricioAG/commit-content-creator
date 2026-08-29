from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class StoryDetectionResult(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    story_detected: bool = Field(
        alias="storyDetected", description="Whether a coherent story was detected"
    )
    confidence: float = Field(
        ge=0.0, le=1.0, description="Confidence in the detected story (0.0 to 1.0)"
    )
    publishability: float = Field(
        ge=0.0, le=1.0, description="Overall publishability score (0.0 to 1.0)"
    )
    story_type: Literal[
        "problem_solution",
        "before_after",
        "architecture_shift",
        "failure_learning",
        "build_log",
        "mini_case_study",
    ] = Field(alias="storyType", default="problem_solution")
    title: str = Field(description="Catchy but grounded story title")
    summary: str = Field(description="High-level overview of the story arc")
    problem: str | None = Field(default=None, description="The core technical problem/challenge")
    attempts: list[str] = Field(
        default_factory=list, description="Attempts, iterations, or previous approaches"
    )
    solution: str | None = Field(default=None, description="The final working solution")
    learning: str | None = Field(default=None, description="Engineering takeaway or insight")
    impact: str | None = Field(default=None, description="Observable result or benefit")
    related_commit_shas: list[str] = Field(
        default_factory=list,
        alias="relatedCommitShas",
        description="SHAs of commits forming this story",
    )
