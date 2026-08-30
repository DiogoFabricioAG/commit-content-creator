from typing import Literal

from pydantic import BaseModel, Field


class EditorialPreferences(BaseModel):
    role_title: str = Field(default="Software Engineer", description="User role or engineering focus")
    language: Literal["es", "en", "pt"] = Field(default="es")
    tone: Literal[
        "humble_builder",
        "deep_technical",
        "direct_minimal",
        "storyteller",
        "pragmatic_lead",
        "startup_founder",
    ] = Field(default="humble_builder")
    target_audience: Literal[
        "senior_engineers",
        "tech_founders",
        "recruiters",
        "junior_developers",
        "general_tech",
    ] = Field(default="senior_engineers")
    technical_level: Literal["high", "medium", "accessible"] = Field(default="high")
    post_length: Literal["concise", "standard", "deep_dive"] = Field(default="standard")
    avoid_words: list[str] = Field(
        default_factory=lambda: [
            "revolucionario",
            "game-changer",
            "mágico",
            "secreto",
            "infalible",
            "delve",
            "seamlessly",
            "paradigma",
            "disruptivo",
        ]
    )
    preferred_cta: Literal[
        "discussion_question",
        "github_link",
        "lesson_takeaway",
        "custom_cta",
        "none",
    ] = Field(default="discussion_question")
    custom_cta: str | None = Field(default=None, description="Custom call-to-action text if preferred_cta is custom_cta")
    custom_rules: list[str] = Field(
        default_factory=list,
        description="Custom author-specific writing directives (e.g. 'Use bullet points for trade-offs')",
    )
    include_code_snippets: bool = Field(
        default=True,
        description="Whether the generator should include code or pseudo-diff snippets when appropriate",
    )
    include_metrics: bool = Field(
        default=True,
        description="Whether the generator should highlight metrics, diff stats, or performance numbers",
    )
    hashtags: list[str] = Field(
        default_factory=lambda: ["#SoftwareEngineering", "#Architecture", "#ProofOfWork", "#BuildInPublic"]
    )
    allowed_formats: list[str] = Field(
        default_factory=lambda: [
            "problem_solution",
            "before_after",
            "build_log",
            "mini_case_study",
            "architecture_breakdown",
            "failure_story",
            "benchmark_metric",
        ]
    )
    auto_publish: bool = Field(default=False)
    onboarding_completed: bool = Field(default=False)
