from typing import Literal

from pydantic import BaseModel, Field


class ApprovalDecision(BaseModel):
    intent: Literal["approve", "reject", "revise", "clarify", "hold"] = Field(
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
