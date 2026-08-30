import uuid

import httpx
from fastapi import APIRouter, Query, status
from fastapi.responses import RedirectResponse

from app.config import get_settings
from app.integrations.convex_client import ConvexGateway

router = APIRouter(prefix="/auth/github", tags=["github"])


@router.get("/login")
async def github_login(userId: str | None = Query(None)) -> RedirectResponse:
    settings = get_settings()
    nonce = str(uuid.uuid4())
    state = f"{userId}:{nonce}" if userId else nonce

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
        return RedirectResponse(url=url, status_code=status.HTTP_302_FOUND)

    # Fallback to GitHub App installation link
    app_url = settings.github_app_url or "https://github.com/apps/laborin-ver1/installations/new"
    return RedirectResponse(url=app_url, status_code=status.HTTP_302_FOUND)


@router.get("/callback")
async def github_callback(
    code: str | None = Query(None),
    state: str | None = Query(None),
    installation_id: str | None = Query(None),
) -> RedirectResponse:
    settings = get_settings()
    convex = ConvexGateway(settings)

    base_url = "https://laborin.meowlab.tech"
    if settings.app_env != "production" and "localhost" in settings.linkedin_redirect_uri:
        base_url = "http://localhost:3000"

    user_id = None
    if state and ":" in state:
        extracted = state.split(":")[0]
        if extracted and len(extracted) > 5:
            user_id = extracted

    if convex.is_configured and not user_id:
        user_id = convex.get_or_create_default_user()

    # If installed via GitHub App
    if installation_id and not code:
        if convex.is_configured and user_id:
            convex.record_activity(
                user_id=user_id,
                type_="github.app.installed",
                label=f"GitHub App installed with ID {installation_id}",
                status="completed",
            )
        user_param = f"&userId={user_id}" if user_id else ""
        return RedirectResponse(
            url=f"{base_url}/dashboard?tab=channels&status=github_connected{user_param}",
            status_code=status.HTTP_302_FOUND,
        )

    if not code:
        user_param = f"&userId={user_id}" if user_id else ""
        return RedirectResponse(
            url=f"{base_url}/dashboard?tab=channels&status=github_connected{user_param}",
            status_code=status.HTTP_302_FOUND,
        )

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

    user_param = f"&userId={user_id}" if user_id else ""
    return RedirectResponse(
        url=f"{base_url}/dashboard?tab=channels&status=github_connected{user_param}",
        status_code=status.HTTP_302_FOUND,
    )
