import uuid

from fastapi import APIRouter, HTTPException, Query, status
from fastapi.responses import RedirectResponse

from app.config import get_settings
from app.integrations.convex_client import ConvexGateway
from app.linkedin.oauth import LinkedInOAuth
from app.linkedin.security import encrypt_token

router = APIRouter(prefix="/auth/linkedin", tags=["linkedin"])


@router.get("/login")
async def linkedin_login() -> RedirectResponse:
    settings = get_settings()
    oauth = LinkedInOAuth(settings)
    state = str(uuid.uuid4())
    url = oauth.get_authorization_url(state)
    return RedirectResponse(url)


@router.get("/callback")
async def linkedin_callback(
    code: str = Query(...),
    state: str = Query(...),
) -> RedirectResponse:

    settings = get_settings()
    convex = ConvexGateway(settings)
    oauth = LinkedInOAuth(settings)

    try:
        token_data = oauth.exchange_code_for_token(code)
    except Exception as error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"LinkedIn token exchange failed: {error}",
        ) from error

    if convex.is_configured:
        user_id = convex.get_or_create_default_user()
        encrypted_token = encrypt_token(
            token_data.access_token,
            settings.token_encryption_key,
        )
        scopes_list = [s.strip() for s in token_data.scope.split(" ") if s.strip()]
        convex.upsert_social_account(
            user_id=user_id,
            provider="linkedin",
            access_token_encrypted=encrypted_token,
            scopes=scopes_list,
            provider_member_id=token_data.member_id,
            author_urn=token_data.author_urn,
            expires_at=token_data.expires_in,
        )

        convex.record_activity(
            user_id=user_id,
            type_="linkedin.account.connected",
            label="LinkedIn account connected and encrypted token stored",
            status="completed",
        )

    redirect_target = "https://laborin.meowlab.tech/dashboard?tab=onboarding&status=linkedin_connected"
    if settings.app_env != "production" and "localhost" in settings.linkedin_redirect_uri:
        redirect_target = "http://localhost:3000/dashboard?tab=onboarding&status=linkedin_connected"

    return RedirectResponse(url=redirect_target, status_code=status.HTTP_302_FOUND)

