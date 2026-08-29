from typing import Literal

from pydantic import BaseModel, Field


class LinkedInTokenData(BaseModel):
    access_token: str
    expires_in: int
    scope: str
    member_id: str | None = None
    author_urn: str | None = None


class LinkedInPostPayload(BaseModel):
    author_urn: str = Field(description="URN of the author, e.g. urn:li:person:abcdef")
    commentary: str = Field(description="The text body of the post")
    visibility: Literal["PUBLIC", "CONNECTIONS"] = "PUBLIC"


class LinkedInPostResponse(BaseModel):
    post_urn: str = Field(description="Created LinkedIn Post URN, e.g. urn:li:share:1234567")
    status: Literal["published", "failed"] = "published"
    error: str | None = None
