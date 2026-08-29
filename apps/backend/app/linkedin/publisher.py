import hashlib
from typing import Any

import httpx
from app.config import Settings
from app.linkedin.security import decrypt_token
from app.schemas.linkedin import LinkedInPostResponse


class LinkedInPublisher:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings

    def publish_post(
        self,
        *,
        author_urn: str,
        commentary: str,
        encrypted_access_token: str | None = None,
        visibility: str = "PUBLIC",
    ) -> LinkedInPostResponse:
        # In demo / test mode or without live credentials, return safe simulated post URN
        if not encrypted_access_token or self.settings.demo_mode:
            post_hash = hashlib.sha256(commentary.encode()).hexdigest()[:10]
            mock_urn = f"urn:li:share:pow_demo_{post_hash}"
            return LinkedInPostResponse(
                post_urn=mock_urn,
                status="published",
            )

        token = decrypt_token(encrypted_access_token, self.settings.token_encryption_key)
        headers = {
            "Authorization": f"Bearer {token}",
            "LinkedIn-Version": self.settings.linkedin_api_version,
            "X-Restli-Protocol-Version": "2.0.0",
            "Content-Type": "application/json",
        }

        # LinkedIn Posts API payload
        payload: dict[str, Any] = {
            "author": author_urn,
            "commentary": commentary,
            "visibility": visibility,
            "distribution": {
                "feedDistribution": "MAIN_FEED",
                "targetEntities": [],
                "thirdPartyDistributionChannels": [],
            },
            "lifecycleState": "PUBLISHED",
            "isReshareDisabledByAuthor": False,
        }

        url = "https://api.linkedin.com/rest/posts"
        try:
            with httpx.Client(timeout=10.0) as client:
                response = client.post(url, headers=headers, json=payload)
                if response.status_code in {200, 201}:
                    post_urn = (
                        response.headers.get("x-restli-id")
                        or response.headers.get("x-linkedin-id")
                        or f"urn:li:share:{hashlib.sha256(commentary.encode()).hexdigest()[:8]}"
                    )
                    return LinkedInPostResponse(
                        post_urn=post_urn,
                        status="published",
                    )
                return LinkedInPostResponse(
                    post_urn="",
                    status="failed",
                    error=f"HTTP {response.status_code}: {response.text}",
                )
        except Exception as exc:
            return LinkedInPostResponse(
                post_urn="",
                status="failed",
                error=str(exc),
            )
