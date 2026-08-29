from typing import Literal

from pydantic import BaseModel, Field


class CommitAnalysis(BaseModel):
    type: Literal[
        "feature",
        "bugfix",
        "refactor",
        "architecture_change",
        "performance",
        "security",
        "developer_experience",
        "docs",
        "maintenance",
        "experiment",
        "unknown",
    ] = "feature"
    summary: str = Field(description="One sentence summary of the technical change")
    problem: str | None = Field(default=None, description="The technical problem solved")
    solution: str | None = Field(default=None, description="The technical solution applied")
    impact: str | None = Field(default=None, description="Grounded technical impact of the change")
    technologies: list[str] = Field(
        default_factory=list, description="Technologies or libraries involved"
    )
    importance: float = Field(
        default=0.5, ge=0.0, le=1.0, description="Technical importance score (0.0 to 1.0)"
    )
    publishability: float = Field(
        default=0.5,
        ge=0.0,
        le=1.0,
        description="Potential public interest/learnings score (0.0 to 1.0)",
    )
    potential_story: bool = Field(
        default=False, description="Whether this change represents a good candidate for a story"
    )
