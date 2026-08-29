import urllib.parse

import httpx
from app.config import Settings
from app.schemas.linkedin import LinkedInTokenData


class LinkedInOAuth:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self.auth_url = "https://www.linkedin.com/oauth/v2/authorization"
        self.token_url = "https://www.linkedin.com/oauth/v2/accessToken"

    def get_authorization_url(self, state: str) -> str:
        params = {
            "response_type": "code",
            "client_id": self.settings.linkedin_client_id or "mock_client_id",
            "redirect_uri": self.settings.linkedin_redirect_uri,
            "state": state,
            "scope": "openid profile email w_member_social",
        }
        return f"{self.auth_url}?{urllib.parse.urlencode(params)}"

    def exchange_code_for_token(self, code: str) -> LinkedInTokenData:
        if self.settings.demo_mode or not self.settings.linkedin_client_secret:
            return LinkedInTokenData(
                access_token="mock_linkedin_token_abcdef123456",
                expires_in=5184000,
                scope="openid profile email w_member_social",
                member_id="mock_member_123",
                author_urn="urn:li:person:mock_member_123",
            )

        data = {
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": self.settings.linkedin_redirect_uri,
            "client_id": self.settings.linkedin_client_id,
            "client_secret": self.settings.linkedin_client_secret,
        }

        with httpx.Client(timeout=10.0) as client:
            response = client.post(self.token_url, data=data)
            response.raise_for_status()
            res_data = response.json()
            access_token = str(res_data.get("access_token"))

            # Fetch member info
            userinfo_res = client.get(
                "https://api.linkedin.com/v2/userinfo",
                headers={"Authorization": f"Bearer {access_token}"},
            )
            member_id = "unknown"
            author_urn = None
            if userinfo_res.status_code == 200:
                user_info = userinfo_res.json()
                member_id = str(user_info.get("sub") or "unknown")
                author_urn = f"urn:li:person:{member_id}"

            return LinkedInTokenData(
                access_token=access_token,
                expires_in=int(res_data.get("expires_in", 5184000)),
                scope=str(res_data.get("scope", "w_member_social")),
                member_id=member_id,
                author_urn=author_urn,
            )
