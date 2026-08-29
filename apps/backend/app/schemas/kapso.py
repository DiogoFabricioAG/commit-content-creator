from typing import Any

from pydantic import BaseModel, Field


class KapsoInboundMessage(BaseModel):
    message_id: str = Field(min_length=1)
    from_phone: str = Field(min_length=1)
    body: str
    timestamp: int | None = None
    raw_payload: dict[str, Any] = Field(default_factory=dict)


class KapsoOutboundMessage(BaseModel):
    to_phone: str
    body: str
    message_id: str | None = None
