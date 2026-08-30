from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit

import httpx
from fastapi import APIRouter, Query, Request, status
from fastapi.responses import RedirectResponse

from app.auth.session import (
    OAUTH_STATE_COOKIE_NAME,
    SessionError,
    SessionManager,
)
from app.config import Settings, get_settings
from app.integrations.convex_client import ConvexGateway

router = APIRouter(prefix="/auth/github", tags=["github"])


def _frontend_base_url(settings: Settings) -> str:
    app_env = settings.app_env
    redirect_uri = settings.github_redirect_uri
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


def _dashboard_redirect(
    settings: Settings,
    *,
    status_value: str,
) -> RedirectResponse:
    response = RedirectResponse(
        url=f"{_frontend_base_url(settings)}/dashboard?tab=channels&status={status_value}",
        status_code=status.HTTP_302_FOUND,
    )
    SessionManager(settings).clear_oauth_state_cookie(response)
    return response


@router.get("/login")
async def github_login(request: Request) -> RedirectResponse:
    settings = get_settings()
    sessions = SessionManager(settings)
    try:
        user_id = sessions.require_session_user_id(request)
        state, nonce = sessions.create_oauth_state(user_id, "github")
    except SessionError:
        return _login_redirect(settings, "session_required")

    if settings.github_client_id:
        redirect_uri = settings.github_redirect_uri
        if settings.app_env == "production" or "laborin.meowlab.tech" in str(settings.linkedin_redirect_uri):
            redirect_uri = "https://laborin.meowlab.tech/auth/github/callback"

        url = (
            f"https://github.com/login/oauth/authorize"
            f"?client_id={settings.github_client_id}"
            f"&redirect_uri={redirect_uri}"
            f"&scope=read:user,repo,read:org"
            f"&state={state}"
        )
        response = RedirectResponse(url=url, status_code=status.HTTP_302_FOUND)
        sessions.set_oauth_state_cookie(response, nonce)
        return response

    # Fallback to GitHub App installation link
    app_url = settings.github_app_url or "https://github.com/apps/laborin-ver1/installations/new"
    parts = urlsplit(app_url)
    query = dict(parse_qsl(parts.query, keep_blank_values=True))
    query["state"] = state
    app_url_with_state = urlunsplit(
        (parts.scheme, parts.netloc, parts.path, urlencode(query), parts.fragment)
    )
    response = RedirectResponse(url=app_url_with_state, status_code=status.HTTP_302_FOUND)
    sessions.set_oauth_state_cookie(response, nonce)
    return response


@router.get("/callback")
async def github_callback(
    request: Request,
    code: str | None = Query(None),
    state: str | None = Query(None),
    installation_id: str | None = Query(None),
) -> RedirectResponse:
    settings = get_settings()
    convex = ConvexGateway(settings)

    if not state:
        return _login_redirect(settings, "oauth_state_invalid")

    sessions = SessionManager(settings)
    try:
        oauth_state = sessions.verify_oauth_state(
            state,
            "github",
            request.cookies.get(OAUTH_STATE_COOKIE_NAME),
            request,
        )
        user_id = oauth_state.user_id
    except SessionError:
        return _login_redirect(settings, "oauth_state_invalid")

    if not convex.is_configured or not convex.get_user_by_id(user_id):
        return _login_redirect(settings, "session_user_missing")

    # If installed via GitHub App
    if installation_id and not code:
        convex.record_activity(
            user_id=user_id,
            type_="github.app.installed",
            label=f"GitHub App installed with ID {installation_id}",
            status="completed",
        )
        return _dashboard_redirect(settings, status_value="github_connected")

    if not code:
        return _dashboard_redirect(settings, status_value="github_connected")

    # Exchange code for access token if client credentials exist
    access_token = None
    if settings.github_client_id and settings.github_client_secret:
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                res = await client.post(
                    "https://github.com/login/oauth/access_token",
                    headers={"Accept": "application/json"},
                    json={
                        "client_id": settings.github_client_id,
                        "client_secret": settings.github_client_secret,
                        "code": code,
                    },
                )
                res.raise_for_status()
                token_data = res.json()
                access_token = token_data.get("access_token")
        except Exception:
            pass

    if access_token and convex.is_configured and user_id:
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                # Fetch user profile
                user_res = await client.get(
                    "https://api.github.com/user",
                    headers={
                        "Authorization": f"Bearer {access_token}",
                        "Accept": "application/vnd.github+json",
                        "User-Agent": "ProofOfWork-App",
                    },
                )
                if user_res.status_code == 200:
                    gh_user = user_res.json()
                    # Sync repositories
                    repos_res = await client.get(
                        "https://api.github.com/user/repos?per_page=30&sort=updated",
                        headers={
                            "Authorization": f"Bearer {access_token}",
                            "Accept": "application/vnd.github+json",
                            "User-Agent": "ProofOfWork-App",
                        },
                    )
                    if repos_res.status_code == 200:
                        repos = repos_res.json()
                        for repo in repos:
                            full_name = repo.get("full_name")
                            default_branch = repo.get("default_branch", "main")
                            if full_name:
                                convex.get_or_create_repository(
                                    user_id=user_id,
                                    full_name=full_name,
                                    default_branch=default_branch,
                                )

                    convex.record_activity(
                        user_id=user_id,
                        type_="github.account.connected",
                        label=f"GitHub account @{gh_user.get('login', 'developer')} connected",
                        status="completed",
                    )
        except Exception:
            pass

    return _dashboard_redirect(settings, status_value="github_connected")
