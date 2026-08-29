from typing import Literal

from pydantic import BaseModel, Field


class EditorialPreferences(BaseModel):
    role_title: str = Field(default="Software Engineer", description="User role or engineering focus")
    language: Literal["es", "en", "pt"] = Field(default="es")
    tone: Literal["humble_builder", "deep_technical", "direct_minimal", "storyteller"] = Field(
        default="humble_builder"
    )
    target_audience: Literal["senior_engineers", "tech_founders", "recruiters", "general_tech"] = Field(
        default="senior_engineers"
    )
    technical_level: Literal["high", "medium", "accessible"] = Field(default="high")
    post_length: Literal["concise", "standard", "deep_dive"] = Field(default="standard")
    avoid_words: list[str] = Field(
        default_factory=lambda: ["revolucionario", "game-changer", "mágico", "secreto", "infalible"]
    )
    preferred_cta: Literal["discussion_question", "github_link", "lesson_takeaway", "none"] = Field(
        default="discussion_question"
    )
    hashtags: list[str] = Field(
        default_factory=lambda: ["#SoftwareEngineering", "#Architecture", "#ProofOfWork"]
    )
    allowed_formats: list[str] = Field(
        default_factory=lambda: [
            "problem_solution",
            "before_after",
            "build_log",
            "mini_case_study",
            "architecture_breakdown",
        ]
    )
    auto_publish: bool = Field(default=False)
    onboarding_completed: bool = Field(default=False)
