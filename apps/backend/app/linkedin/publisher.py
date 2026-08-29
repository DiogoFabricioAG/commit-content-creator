import hashlib
import time
from typing import Any, cast
from urllib.parse import quote

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
        media: list[dict[str, Any]] | None = None,
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

        content: dict[str, Any] | None = None
        if media:
            try:
                content = self._build_media_content(
                    media=media,
                    author_urn=author_urn,
                    token=token,
                    headers=headers,
                )
            except Exception as exc:
                return LinkedInPostResponse(
                    post_urn="",
                    status="failed",
                    error=f"Media upload failed: {exc}",
                )

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
        if content:
            payload["content"] = content

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

    def _build_media_content(
        self,
        *,
        media: list[dict[str, Any]],
        author_urn: str,
        token: str,
        headers: dict[str, str],
    ) -> dict[str, Any]:
        image = next((item for item in media if item.get("kind") == "image"), None)
        if not image:
            raise ValueError("Only image media is enabled in this slice")

        image_url = image.get("url")
        if not isinstance(image_url, str) or not image_url:
            raise ValueError("Image media requires a public URL")

        mime_type = str(image.get("mimeType") or "image/png")
        with httpx.Client(timeout=30.0) as client:
            source_response = client.get(image_url)
            source_response.raise_for_status()

            init_response = client.post(
                "https://api.linkedin.com/rest/images?action=initializeUpload",
                headers=headers,
                json={"initializeUploadRequest": {"owner": author_urn}},
            )
            init_response.raise_for_status()
            init_data = cast(dict[str, Any], init_response.json())
            raw_value = init_data.get("value")
            value = cast(dict[str, Any], raw_value) if isinstance(raw_value, dict) else None
            if value is None:
                raise ValueError("LinkedIn image initialization returned no value")

            upload_url = value.get("uploadUrl")
            image_urn = value.get("image")
            if not isinstance(upload_url, str) or not isinstance(image_urn, str):
                raise ValueError("LinkedIn image initialization returned incomplete data")

            upload_response = client.put(
                upload_url,
                headers={
                    "Authorization": f"Bearer {token}",
                    "Content-Type": mime_type,
                },
                content=source_response.content,
            )
            upload_response.raise_for_status()

            status_url = f"https://api.linkedin.com/rest/images/{quote(image_urn, safe='')}"
            for attempt in range(10):
                status_response = client.get(status_url, headers=headers)
                status_response.raise_for_status()
                raw_status_data = status_response.json()
                if not isinstance(raw_status_data, dict):
                    raise ValueError("LinkedIn image status returned invalid data")
                status_data = cast(dict[str, Any], raw_status_data)
                asset_status = status_data.get("status")
                if asset_status in {None, "AVAILABLE"}:
                    break
                if asset_status in {"CLIENT_ERROR", "SERVER_ERROR", "INCOMPLETE"}:
                    raise ValueError(f"LinkedIn image processing failed: {asset_status}")
                if attempt < 9:
                    time.sleep(0.5)
            else:
                raise ValueError("LinkedIn image did not become available in time")

        return {
            "media": {
                "id": image_urn,
                "altText": str(image.get("altText") or "Generated image for this post"),
            }
        }
