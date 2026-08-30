import hashlib
import json
import logging
import uuid
from typing import Any

from fastapi import APIRouter, BackgroundTasks, HTTPException, Request, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

from app.auth.session import SessionManager
from app.config import Settings, get_settings
from app.github.client import GitHubClient
from app.integrations.convex_client import ConvexGateway
from app.intelligence.commit_analyzer.analyzer import CommitAnalyzer
from app.intelligence.digest.historical_digest import HistoricalDigestBuilder
from app.schemas.preferences import EditorialPreferences
from app.whatsapp.kapso.client import KapsoClient

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/portal", tags=["portal"])


class UpdateProfilePayload(BaseModel):
    display_name: str | None = Field(default=None, max_length=120)
    whatsapp_phone: str | None = Field(default=None, max_length=32)
    email: str | None = Field(default=None, max_length=120)


class CreateRepositoryPayload(BaseModel):
    full_name: str = Field(min_length=3, max_length=120)
    default_branch: str | None = Field(default="main", max_length=60)


class BuildHistoricalDigestPayload(BaseModel):
    repository_id: str = Field(min_length=1, max_length=128)
    branch: str | None = Field(default=None, max_length=120)
    max_commits: int = Field(default=500, ge=1, le=500)


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


def _digest_fingerprint(
    *,
    user_id: str,
    repository_full_name: str,
    branch: str | None,
    commit_shas: list[str],
    preferences: EditorialPreferences | None,
) -> str:
    payload = {
        "userId": user_id,
        "repository": repository_full_name,
        "branch": branch,
        "commits": commit_shas,
        "preferences": preferences.model_dump() if preferences else {},
    }
    return hashlib.sha256(
        json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()


def _run_historical_digest(
    settings: Settings,
    *,
    run_id: str,
    user_id: str,
    repository_id: str,
    repository_full_name: str,
    branch: str | None,
    max_commits: int,
) -> None:
    convex = ConvexGateway(settings)
    digest_id: str | None = None

    try:
        github_client = GitHubClient(settings)
        commits = github_client.fetch_repository_history(
            repository_full_name,
            branch=branch,
            max_commits=max_commits,
        )
        if not commits:
            raise ValueError("No se encontraron commits para compilar en este repositorio")

        preferences = convex.get_user_preferences(user_id)
        fingerprint = _digest_fingerprint(
            user_id=user_id,
            repository_full_name=repository_full_name,
            branch=branch,
            commit_shas=[commit.sha for commit in commits],
            preferences=preferences,
        )
        reservation = convex.reserve_historical_digest(
            user_id=user_id,
            repository_id=repository_id,
            repository_full_name=repository_full_name,
            branch=branch,
            fingerprint=fingerprint,
        )
        digest_id = str(reservation.get("digestId") or "") or None
        if reservation.get("existing"):
            convex.record_activity(
                user_id=user_id,
                type_="historical.digest.reused",
                label="La compilación histórica ya existía; se conserva una sola narrativa",
                status="completed",
                repository_id=repository_id,
                metadata={"runId": run_id, "digestId": digest_id},
            )
            return

        convex.record_activity(
            user_id=user_id,
            type_="historical.digest.fetched",
            label=f"Historial completo recuperado ({len(commits)} commits)",
            status="completed",
            repository_id=repository_id,
            metadata={"runId": run_id, "digestId": digest_id},
        )

        commit_ids_by_sha: dict[str, str] = {}
        for commit in commits:
            result = convex.record_commit(repository_id, commit)
            commit_id = result.get("commitId")
            if commit_id:
                commit_ids_by_sha[commit.sha] = str(commit_id)

        # Analyze a bounded set of representative commits. The digest still
        # includes every commit, while avoiding one paid LLM call per commit.
        representative_commits = commits[-24:]
        analyzer = CommitAnalyzer(settings)
        analyses = [analyzer.analyze(commit) for commit in representative_commits]
        for commit, analysis in zip(representative_commits, analyses, strict=True):
            commit_id = commit_ids_by_sha.get(commit.sha)
            if commit_id:
                convex.record_commit_analysis(
                    commit_id=commit_id,
                    repository_id=repository_id,
                    analysis=analysis,
                )

        digest = HistoricalDigestBuilder(settings).build(
            repository_full_name=repository_full_name,
            branch=branch,
            commits=commits,
            analyses=analyses,
            preferences=preferences,
        )
        included_ids = [
            commit_ids_by_sha[sha]
            for sha in digest.commit_shas
            if sha in commit_ids_by_sha
        ]
        filtered_shas = [commit.sha for commit in digest.filtered_commits]
        if not included_ids:
            raise ValueError("El digest no pudo asociar commits persistidos")

        story_id = convex.record_story(
            user_id=user_id,
            repository_id=repository_id,
            story=digest.story,
            related_commit_ids=included_ids,
            status="detected",
        )
        post_id = convex.record_post(
            user_id=user_id,
            story_id=story_id,
            format_=digest.draft.format,
            status="awaiting_approval",
        )
        version_id = convex.record_post_version(
            post_id=post_id,
            version=1,
            title=digest.draft.title,
            body=digest.draft.body,
            generation_reason="Historical digest compiled from repository evidence",
        )
        user = convex.get_user_by_id(user_id)
        user_phone = str(user.get("whatsappPhone")) if user and user.get("whatsappPhone") else ""
        if not user_phone:
            raise ValueError("El usuario no tiene un número de WhatsApp configurado")

        approval_id = convex.record_approval_request(
            user_id=user_id,
            post_id=post_id,
            current_post_version_id=version_id,
            recipient_phone=user_phone,
            status="pending",
        )

        delivery_status = "waiting"
        if convex.is_whatsapp_window_open(user_phone):
            outbound = KapsoClient(settings).send_draft_for_approval(
                to_phone=user_phone,
                story_title=digest.draft.title,
                post_body=digest.draft.body,
                version=1,
            )
            if outbound.message_id:
                convex.set_approval_outbound_message_id(
                    approval_request_id=approval_id,
                    kapso_message_id=outbound.message_id,
                )
                convex.record_approval_message(
                    approval_request_id=approval_id,
                    direction="outbound",
                    message_id=outbound.message_id,
                    content=outbound.body,
                )
            delivery_status = "completed"

        convex.complete_historical_digest(
            digest_id=digest_id or "",
            included_commit_shas=digest.commit_shas,
            filtered_commit_shas=filtered_shas,
            story_id=story_id,
            post_id=post_id,
            approval_request_id=approval_id,
            title=digest.draft.title,
            summary=digest.story.summary,
            status="awaiting_approval",
        )
        convex.record_activity(
            user_id=user_id,
            type_="historical.digest.completed",
            label=(
                "Narrativa histórica lista y enviada a WhatsApp"
                if delivery_status == "completed"
                else "Narrativa histórica lista; esperando ventana de WhatsApp"
            ),
            status=delivery_status,
            repository_id=repository_id,
            metadata={
                "runId": run_id,
                "digestId": digest_id,
                "storyId": story_id,
                "postId": post_id,
                "approvalRequestId": approval_id,
                "commitCount": len(digest.commit_shas),
                "filteredCommitCount": len(filtered_shas),
            },
        )
    except Exception as error:
        logger.exception("Historical digest failed for %s", repository_full_name)
        if digest_id:
            try:
                convex.fail_historical_digest(digest_id=digest_id, error=str(error))
            except Exception:
                logger.exception("Could not mark historical digest as failed")
        convex.record_activity(
            user_id=user_id,
            type_="historical.digest.failed",
            label=f"No se pudo compilar el historial: {str(error)[:120]}",
            status="failed",
            repository_id=repository_id,
            metadata={"runId": run_id},
        )


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


# Historical digest
@router.post("/digests", status_code=status.HTTP_202_ACCEPTED)
async def start_historical_digest(
    payload: BuildHistoricalDigestPayload,
    request: Request,
    background_tasks: BackgroundTasks,
) -> JSONResponse:
    user_id = _require_authenticated_user_id(request)
    settings = get_settings()
    convex = ConvexGateway(settings)
    if not convex.is_configured:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Convex is not configured",
        )

    repository = convex.get_repository_by_id_for_user(
        user_id=user_id,
        repository_id=payload.repository_id,
    )
    if not repository:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Repositorio no encontrado en tu espacio de trabajo",
        )

    repository_full_name = str(repository.get("fullName") or "").strip()
    if not repository_full_name:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="El repositorio no tiene un nombre válido",
        )
    branch = payload.branch or str(repository.get("defaultBranch") or "main")
    run_id = uuid.uuid4().hex[:12]
    convex.record_activity(
        user_id=user_id,
        type_="historical.digest.started",
        label=f"Compilando la historia completa de {repository_full_name}",
        status="started",
        repository_id=payload.repository_id,
        metadata={
            "runId": run_id,
            "branch": branch,
            "maxCommits": payload.max_commits,
        },
    )
    background_tasks.add_task(
        _run_historical_digest,
        settings,
        run_id=run_id,
        user_id=user_id,
        repository_id=payload.repository_id,
        repository_full_name=repository_full_name,
        branch=branch,
        max_commits=payload.max_commits,
    )
    return JSONResponse(
        {
            "status": "started",
            "runId": run_id,
            "repository": repository_full_name,
            "branch": branch,
            "message": (
                "Estamos leyendo el historial completo. Recibirás una sola narrativa por WhatsApp."
            ),
        },
        status_code=status.HTTP_202_ACCEPTED,
    )


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
