from typing import Literal

from pydantic import BaseModel, Field


class VisualRequest(BaseModel):
    kind: Literal["image", "infographic", "architecture_diagram", "flow_diagram"] = Field(
        description="The visual asset requested by the user"
    )
    instruction: str = Field(
        min_length=1,
        max_length=2000,
        description="The user's visual direction, preserved as a complete instruction",
    )
    attach_to_draft: bool = Field(
        default=True,
        description="Whether the generated visual should be attached to the current draft",
    )


class ApprovalDecision(BaseModel):
    intent: Literal[
        "approve",
        "reject",
        "revise",
        "clarify",
        "hold",
        "generate_visual",
    ] = Field(
        description="The classified intent of the user's message"
    )
    feedback: str | None = Field(
        default=None, description="Specific feedback or edit instructions provided by the user"
    )
    confidence: float = Field(
        default=0.9, ge=0.0, le=1.0, description="Confidence score of the intent classification"
    )
    reasoning: str | None = Field(
        default=None, description="Brief explanation of why this intent was recognized"
    )
    visual_request: VisualRequest | None = Field(
        default=None,
        description="Structured visual generation request when intent is generate_visual",
    )
