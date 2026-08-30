from typing import Any

from fastapi import APIRouter, HTTPException, Request, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

from app.auth.session import SessionManager
from app.config import get_settings
from app.integrations.convex_client import ConvexGateway
from app.schemas.preferences import EditorialPreferences

router = APIRouter(prefix="/api/portal", tags=["portal"])


class UpdateProfilePayload(BaseModel):
    display_name: str | None = Field(default=None, max_length=120)
    whatsapp_phone: str | None = Field(default=None, max_length=32)
    email: str | None = Field(default=None, max_length=120)


class CreateRepositoryPayload(BaseModel):
    full_name: str = Field(min_length=3, max_length=120)
    default_branch: str | None = Field(default="main", max_length=60)


def _require_authenticated_user_id(request: Request) -> str:
    settings = get_settings()
    sessions = SessionManager(settings)
    user_id = sessions.get_session_user_id(request)
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="A valid LaborIN session cookie is required",
        )
    return user_id


# Profile
@router.get("/profile")
async def get_profile(request: Request) -> JSONResponse:
    user_id = _require_authenticated_user_id(request)
    settings = get_settings()
    convex = ConvexGateway(settings)
    if not convex.is_configured:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Convex is not configured",
        )

    user = convex.get_user_by_id(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    return JSONResponse({"userId": user_id, "user": user})


@router.patch("/profile")
async def update_profile(
    payload: UpdateProfilePayload, request: Request
) -> JSONResponse:
    user_id = _require_authenticated_user_id(request)
    settings = get_settings()
    convex = ConvexGateway(settings)
    if not convex.is_configured:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Convex is not configured",
        )

    updated_id = convex.update_user_profile(
        user_id=user_id,
        display_name=payload.display_name.strip() if payload.display_name else None,
        whatsapp_phone=payload.whatsapp_phone.strip() if payload.whatsapp_phone else None,
        email=payload.email.strip() if payload.email else None,
    )
    return JSONResponse({"userId": updated_id, "status": "updated"})


# Editorial Preferences
@router.get("/preferences")
async def get_preferences(request: Request) -> JSONResponse:
    user_id = _require_authenticated_user_id(request)
    settings = get_settings()
    convex = ConvexGateway(settings)
    if not convex.is_configured:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Convex is not configured",
        )

    preferences = convex.get_user_preferences(user_id)
    return JSONResponse(
        {
            "userId": user_id,
            "preferences": preferences.model_dump() if preferences else None,
        }
    )


@router.put("/preferences")
async def save_preferences(
    payload: EditorialPreferences, request: Request
) -> JSONResponse:
    user_id = _require_authenticated_user_id(request)
    settings = get_settings()
    convex = ConvexGateway(settings)
    if not convex.is_configured:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Convex is not configured",
        )

    saved_id = convex.save_user_preferences(user_id, payload)
    return JSONResponse({"userId": user_id, "preferenceId": saved_id, "status": "saved"})


# Repositories
@router.get("/repositories")
async def list_repositories(request: Request) -> JSONResponse:
    user_id = _require_authenticated_user_id(request)
    settings = get_settings()
    convex = ConvexGateway(settings)
    if not convex.is_configured:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Convex is not configured",
        )

    repositories = convex.list_repositories_for_user(user_id)
    return JSONResponse({"userId": user_id, "repositories": repositories})


@router.post("/repositories")
async def add_repository(
    payload: CreateRepositoryPayload, request: Request
) -> JSONResponse:
    user_id = _require_authenticated_user_id(request)
    settings = get_settings()
    convex = ConvexGateway(settings)
    if not convex.is_configured:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Convex is not configured",
        )

    repo_id = convex.get_or_create_repository(
        user_id=user_id,
        full_name=payload.full_name.strip(),
        default_branch=payload.default_branch.strip() if payload.default_branch else "main",
    )
    return JSONResponse({"userId": user_id, "repositoryId": repo_id, "status": "created"})


@router.delete("/repositories/{repository_id}")
async def remove_repository(
    repository_id: str, request: Request
) -> JSONResponse:
    user_id = _require_authenticated_user_id(request)
    settings = get_settings()
    convex = ConvexGateway(settings)
    if not convex.is_configured:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Convex is not configured",
        )

    try:
        removed_id = convex.remove_repository_for_user(
            user_id=user_id, repository_id=repository_id
        )
        return JSONResponse({"userId": user_id, "repositoryId": removed_id, "status": "removed"})
    except Exception as error:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(error),
        ) from error


# Social Accounts (Sanitized metadata, no secret token leaks)
@router.get("/social-accounts")
async def get_social_accounts(request: Request) -> JSONResponse:
    user_id = _require_authenticated_user_id(request)
    settings = get_settings()
    convex = ConvexGateway(settings)
    if not convex.is_configured:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Convex is not configured",
        )

    linkedin = convex.get_social_account(user_id=user_id, provider="linkedin")
    sanitized_linkedin: dict[str, Any] | None = None
    if linkedin:
        sanitized_linkedin = {
            "provider": linkedin.get("provider", "linkedin"),
            "connected": True,
            "authorUrn": linkedin.get("authorUrn"),
            "scopes": linkedin.get("scopes", []),
            "updatedAt": linkedin.get("updatedAt"),
        }

    return JSONResponse(
        {
            "userId": user_id,
            "linkedin": sanitized_linkedin,
        }
    )


# Live Activity Stream
@router.get("/activity")
async def list_activity(request: Request, limit: int = 50) -> JSONResponse:
    user_id = _require_authenticated_user_id(request)
    settings = get_settings()
    convex = ConvexGateway(settings)
    if not convex.is_configured:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Convex is not configured",
        )

    events = convex.list_activity_for_user(user_id=user_id, limit=limit)
    return JSONResponse({"userId": user_id, "events": events})


# Posts & Approvals
@router.get("/posts")
async def list_posts(request: Request, limit: int = 50) -> JSONResponse:
    user_id = _require_authenticated_user_id(request)
    settings = get_settings()
    convex = ConvexGateway(settings)
    if not convex.is_configured:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Convex is not configured",
        )

    posts = convex.list_posts_for_user(user_id=user_id, limit=limit)
    return JSONResponse({"userId": user_id, "posts": posts})


@router.get("/approvals")
async def list_approvals(request: Request) -> JSONResponse:
    user_id = _require_authenticated_user_id(request)
    settings = get_settings()
    convex = ConvexGateway(settings)
    if not convex.is_configured:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Convex is not configured",
        )

    approvals = convex.list_approval_requests_for_user(user_id=user_id)
    return JSONResponse({"userId": user_id, "approvals": approvals})
