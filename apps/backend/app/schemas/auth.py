from pydantic import BaseModel, Field


class SessionLoginRequest(BaseModel):
    phone: str = Field(min_length=8, max_length=32)
    display_name: str | None = Field(default=None, max_length=120)
