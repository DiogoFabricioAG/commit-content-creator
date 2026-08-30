from pydantic import BaseModel, Field


class SessionLoginRequest(BaseModel):
    phone: str = Field(min_length=8, max_length=32)
    display_name: str | None = Field(default=None, max_length=120)


class SessionVerificationRequest(BaseModel):
    code: str = Field(min_length=6, max_length=6, pattern=r"^\d{6}$")
