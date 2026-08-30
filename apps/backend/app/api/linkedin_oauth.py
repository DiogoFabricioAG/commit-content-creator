from fastapi import APIRouter, HTTPException, Query, Request, status
from fastapi.responses import RedirectResponse

from app.auth.session import OAUTH_STATE_COOKIE_NAME, SessionError, SessionManager
from app.config import Settings, get_settings
from app.integrations.convex_client import ConvexGateway
from app.linkedin.oauth import LinkedInOAuth
from app.linkedin.security import encrypt_token

router = APIRouter(prefix="/auth/linkedin", tags=["linkedin"])


def _frontend_base_url(settings: Settings) -> str:
    app_env = settings.app_env
    redirect_uri = settings.linkedin_redirect_uri
    return "https://laborin.meowlab.tech" if app_env == "production" else (
        "http://localhost:3000" if "localhost" in redirect_uri else "https://laborin.meowlab.tech"
    )


def _login_redirect(settings: Settings, error: str) -> RedirectResponse:
    response = RedirectResponse(
        url=f"{_frontend_base_url(settings)}/login?error={error}",
        status_code=status.HTTP_302_FOUND,
    )
    SessionManager(settings).clear_oauth_state_cookie(response)
    return response


def _dashboard_redirect(settings: Settings) -> RedirectResponse:
    response = RedirectResponse(
        url=f"{_frontend_base_url(settings)}/dashboard?tab=channels&status=linkedin_connected",
        status_code=status.HTTP_302_FOUND,
    )
    SessionManager(settings).clear_oauth_state_cookie(response)
    return response


@router.get("/login")
async def linkedin_login(request: Request) -> RedirectResponse:
    settings = get_settings()
    sessions = SessionManager(settings)
    oauth = LinkedInOAuth(settings)
    try:
        user_id = sessions.require_session_user_id(request)
        state, nonce = sessions.create_oauth_state(user_id, "linkedin")
    except SessionError:
        return _login_redirect(settings, "session_required")
    url = oauth.get_authorization_url(state)
    response = RedirectResponse(url, status_code=status.HTTP_302_FOUND)
    sessions.set_oauth_state_cookie(response, nonce)
    return response


@router.get("/callback")
async def linkedin_callback(
    request: Request,
    code: str = Query(...),
    state: str | None = Query(None),
) -> RedirectResponse:

    settings = get_settings()
    convex = ConvexGateway(settings)
    oauth = LinkedInOAuth(settings)
    sessions = SessionManager(settings)

    if not state:
        return _login_redirect(settings, "oauth_state_invalid")

    try:
        oauth_state = sessions.verify_oauth_state(
            state,
            "linkedin",
            request.cookies.get(OAUTH_STATE_COOKIE_NAME),
            request,
        )
        user_id = oauth_state.user_id
    except SessionError:
        return _login_redirect(settings, "oauth_state_invalid")

    if not convex.is_configured or not convex.get_user_by_id(user_id):
        return _login_redirect(settings, "session_user_missing")

    try:
        token_data = oauth.exchange_code_for_token(code)
    except Exception as error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"LinkedIn token exchange failed: {error}",
        ) from error

    if convex.is_configured:
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

    return _dashboard_redirect(settings)
