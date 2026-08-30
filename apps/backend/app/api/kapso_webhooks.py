import json
import logging
import re
import unicodedata
from typing import Any, cast

import httpx
from fastapi import APIRouter, BackgroundTasks, HTTPException, Request, status

from app.config import get_settings
from app.github.client import GitHubClient
from app.integrations.convex_client import ConvexGateway
from app.intelligence.approval_agent.agent import ApprovalAgent
from app.intelligence.commit_analyzer.analyzer import CommitAnalyzer
from app.intelligence.content_generator.generator import ContentGenerator
from app.intelligence.media.image_generator import (
    ImageGenerationUnavailable,
    OpenAIImageGenerator,
)
from app.intelligence.story_detector.detector import StoryDetector
from app.linkedin.publisher import LinkedInPublisher
from app.schemas.approval import ApprovalDecision
from app.schemas.github import CommitFile, NormalizedCommit
from app.schemas.kapso import KapsoInboundMessage
from app.schemas.preferences import EditorialPreferences
from app.schemas.story import StoryDetectionResult
from app.whatsapp.kapso.client import KapsoClient
from app.whatsapp.kapso.webhooks import (
    InvalidKapsoSignature,
    parse_kapso_inbound_messages,
    verify_kapso_signature,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/webhooks/kapso", tags=["kapso"])


def _inbound_context_message_id(inbound: KapsoInboundMessage) -> str | None:
    raw_payload = inbound.raw_payload
    containers: list[dict[str, Any]] = [raw_payload]
    raw_data = raw_payload.get("data")
    if isinstance(raw_data, dict):
        containers.append(cast(dict[str, Any], raw_data))

    for container in containers:
        raw_message = container.get("message")
        message = (
            cast(dict[str, Any], raw_message)
            if isinstance(raw_message, dict)
            else container
        )
        raw_context = message.get("context") or container.get("context")
        if not isinstance(raw_context, dict):
            continue
        context = cast(dict[str, Any], raw_context)
        for key in ("id", "message_id", "messageId"):
            value = context.get(key)
            if isinstance(value, str) and value.strip():
                return value.strip()
    return None


def approval_action_from_inbound(inbound: KapsoInboundMessage) -> str | None:
    """Return a stable approval action across Kapso webhook payload variants."""
    candidates = (inbound.button_id, inbound.button_title, inbound.body)
    for candidate in candidates:
        if not isinstance(candidate, str):
            continue
        normalized = "".join(
            character
            for character in unicodedata.normalize("NFKD", candidate.lower())
            if not unicodedata.combining(character)
        ).strip()
        if normalized in {"approval_publish", "publicar", "publicalo"}:
            return "publish"
        if normalized in {"approval_review", "revisar", "review"}:
            return "review"
        if normalized in {"approval_reject", "descartar", "descartalo"}:
            return "reject"
    return None


def is_revision_prompt(content: Any) -> bool:
    if not isinstance(content, str):
        return False
    normalized = "".join(
        character
        for character in unicodedata.normalize("NFKD", content.lower())
        if not unicodedata.combining(character)
    )
    return "dime que quieres cambiar" in normalized


def _request_waiting_for_revision_feedback(
    convex: ConvexGateway,
    approval_request: dict[str, Any],
) -> bool:
    messages = convex.list_approval_messages_for_request(
        str(approval_request.get("_id"))
    )
    for message in reversed(messages):
        direction = message.get("direction")
        if direction == "inbound":
            return False
        if direction == "outbound":
            return is_revision_prompt(message.get("content"))
    return False


def _normalized_commits_from_convex(records: list[dict[str, Any]]) -> list[NormalizedCommit]:
    commits: list[NormalizedCommit] = []
    for record in records:
        raw_files_value: Any = record.get("files")
        files: list[CommitFile] = []
        if isinstance(raw_files_value, list):
            raw_files = cast(list[Any], raw_files_value)
            for raw_file_value in raw_files:
                if not isinstance(raw_file_value, dict):
                    continue
                raw_file = cast(dict[str, Any], raw_file_value)
                files.append(
                    CommitFile(
                        path=str(raw_file.get("path") or "unknown file"),
                        status=str(raw_file.get("status") or "modified"),
                        additions=int(raw_file.get("additions") or 0),
                        deletions=int(raw_file.get("deletions") or 0),
                        patch=(
                            str(raw_file.get("patch"))
                            if raw_file.get("patch") is not None
                            else None
                        ),
                    )
                )
        commits.append(
            NormalizedCommit(
                sha=str(record.get("sha") or "unknown"),
                author=str(record.get("author") or "unknown author"),
                message=str(record.get("message") or "una mejora técnica"),
                committed_at=int(record.get("committedAt") or 0),
                branch=(
                    str(record.get("branch"))
                    if record.get("branch") is not None
                    else None
                ),
                additions=int(record.get("additions") or 0),
                deletions=int(record.get("deletions") or 0),
                changed_files=int(record.get("changedFiles") or len(files)),
                files=files,
                status="fetched",
            )
        )
    return commits


def _regenerate_legacy_draft(
    *,
    convex: ConvexGateway,
    content_gen: ContentGenerator,
    story_detector: StoryDetector,
    commit_analyzer: CommitAnalyzer,
    github_client: GitHubClient,
    pending: dict[str, Any],
    title: str,
    body: str,
    version_num: int,
) -> tuple[str, str, int]:
    if not ContentGenerator.is_legacy_draft(title, body):
        return title, body, version_num

    post_id = str(pending.get("postId"))
    user_id = str(pending.get("userId"))
    post = cast(
        dict[str, Any] | None,
        convex.client.query("posts:getById", {"postId": post_id}),
    )
    story_id = str(post.get("storyId")) if post else ""
    story_data = cast(
        dict[str, Any] | None,
        (
            convex.client.query("stories:getById", {"storyId": story_id})
            if story_id
            else None
        ),
    )
    related_ids: Any = story_data.get("relatedCommitIds") if story_data else None
    related_ids_list = cast(list[Any], related_ids) if isinstance(related_ids, list) else []
    commit_ids: list[str] = [str(commit_id) for commit_id in related_ids_list]
    commit_records = convex.list_commits_by_ids(commit_ids)
    commits = _normalized_commits_from_convex(commit_records)
    repository_id = str(story_data.get("repositoryId")) if story_data else ""
    repository = (
        cast(
            dict[str, Any] | None,
            convex.client.query("repositories:getById", {"repositoryId": repository_id}),
        )
        if repository_id
        else None
    )
    repository_full_name = str(repository.get("fullName")) if repository else ""
    if repository_full_name:
        refreshed_commits: list[NormalizedCommit] = []
        for index, record in enumerate(commit_records):
            sha = str(record.get("sha") or "")
            if not sha:
                continue
            refreshed = github_client.fetch_commit(repository_full_name, sha)
            if refreshed.files or not re.fullmatch(
                r"commit\s+[0-9a-f]{7,}", refreshed.message, re.IGNORECASE
            ):
                refreshed_commits.append(refreshed)
            elif index < len(commits):
                refreshed_commits.append(commits[index])
        if refreshed_commits:
            commits = refreshed_commits
    if not commits:
        logger.warning(
            "Legacy draft %s has no commits available for regeneration", post_id
        )
        return title, body, version_num

    analyses = [commit_analyzer.analyze(commit) for commit in commits]
    story = story_detector.detect_story(commits, analyses)
    preferences = convex.get_user_preferences(user_id)
    regenerated = content_gen.generate_draft(story, preferences=preferences)
    new_version_num = version_num + 1
    new_version_id = convex.record_post_version(
        post_id=post_id,
        version=new_version_num,
        title=regenerated.title,
        body=regenerated.body,
        generation_reason="Regenerated legacy draft with grounded repository context",
    )
    convex.update_approval_request(
        approval_request_id=str(pending.get("_id")),
        status="pending",
        current_post_version_id=new_version_id,
    )
    convex.record_activity(
        user_id=user_id,
        type_="post.generation.completed",
        label=f"Legacy draft regenerated as grounded V{new_version_num}",
        status="completed",
        metadata={"postId": post_id, "versionId": new_version_id},
    )
    return regenerated.title, regenerated.body, new_version_num


def _deliver_queued_approval(
    *,
    convex: ConvexGateway,
    kapso_client: KapsoClient,
    pending: dict[str, Any],
    inbound: KapsoInboundMessage,
    content_gen: ContentGenerator,
    story_detector: StoryDetector,
    commit_analyzer: CommitAnalyzer,
    github_client: GitHubClient,
) -> bool:
    req_id = str(pending.get("_id"))
    post_id = str(pending.get("postId"))
    user_id = str(pending.get("userId"))
    post_version = convex.client.query(
        "postVersions:getLatestForPost", {"postId": post_id}
    )
    if not post_version:
        logger.warning("Approval %s has no post version", req_id)
        return False

    title = str(post_version.get("title") or "Historia técnica")
    body = str(post_version.get("body") or "")
    version_num = int(post_version.get("version", 1))
    title, body, version_num = _regenerate_legacy_draft(
        convex=convex,
        content_gen=content_gen,
        story_detector=story_detector,
        commit_analyzer=commit_analyzer,
        github_client=github_client,
        pending=pending,
        title=title,
        body=body,
        version_num=version_num,
    )
    try:
        outbound = kapso_client.send_draft_for_approval(
            to_phone=inbound.from_phone,
            story_title=title,
            post_body=body,
            version=version_num,
        )
    except httpx.HTTPStatusError as error:
        logger.warning("Could not deliver queued approval %s: %s", req_id, error)
        convex.record_activity(
            user_id=user_id,
            type_="approval.whatsapp.failed",
            label="WhatsApp delivery temporarily rejected by Kapso",
            status="failed",
            metadata={"approvalRequestId": req_id},
        )
        return False
    if outbound.message_id:
        convex.set_approval_outbound_message_id(
            approval_request_id=req_id,
            kapso_message_id=outbound.message_id,
        )

    convex.record_approval_message(
        approval_request_id=req_id,
        direction="inbound",
        message_id=inbound.message_id,
        content=inbound.body,
        interpreted_intent="session_started",
        confidence=1.0,
    )
    if outbound.message_id:
        convex.record_approval_message(
            approval_request_id=req_id,
            direction="outbound",
            message_id=outbound.message_id,
            content=outbound.body,
        )
    convex.record_activity(
        user_id=user_id,
        type_="approval.whatsapp.sent",
        label=f"Sent draft V{version_num} to WhatsApp ({inbound.from_phone}) via Kapso",
        status="completed",
        metadata={
            "approvalRequestId": req_id,
            "trigger": "inbound_user_message",
        },
    )
    return True


def _handle_inbound_whatsapp(inbound: KapsoInboundMessage) -> None:
    settings = get_settings()
    convex = ConvexGateway(settings)
    if not convex.is_configured:
        return

    agent = ApprovalAgent(settings)
    content_gen = ContentGenerator(settings)
    story_detector = StoryDetector(settings)
    commit_analyzer = CommitAnalyzer(settings)
    github_client = GitHubClient(settings)
    image_generator = OpenAIImageGenerator(settings)
    publisher = LinkedInPublisher(settings)
    kapso_client = KapsoClient(settings)

    # 1. Lookup all pending approvals for this phone. One inbound message opens
    # a single 24-hour window and releases every approval queued before it.
    pending_requests = convex.list_pending_approvals_for_phone(inbound.from_phone)
    if not pending_requests:
        # A first inbound message is also the proof that the person controls
        # this WhatsApp number. Open the free 24-hour conversation window so
        # the browser can request an OTP without using a paid template.
        user_id = convex.get_or_create_default_user(
            whatsapp_phone=inbound.from_phone,
        )
        convex.open_whatsapp_window(
            user_id=user_id,
            recipient_phone=inbound.from_phone,
            inbound_message_id=inbound.message_id,
        )
        kapso_client.send_message(
            inbound.from_phone,
            (
                "✅ Número recibido. Vuelve a LaborIN y solicita tu código de acceso "
                "para terminar la verificación."
            ),
        )
        logger.info("Opened WhatsApp onboarding window for %s", inbound.from_phone)
        return

    pending = pending_requests[-1]
    context_message_id = _inbound_context_message_id(inbound)
    if context_message_id:
        pending = next(
            (
                request
                for request in pending_requests
                if request.get("kapsoOutboundMessageId") == context_message_id
            ),
            pending,
        )
    else:
        pending = next(
            (
                request
                for request in reversed(pending_requests)
                if _request_waiting_for_revision_feedback(convex, request)
            ),
            pending,
        )
    req_id = str(pending.get("_id"))
    post_id = str(pending.get("postId"))
    user_id = str(pending.get("userId"))
    current_version_id = str(pending.get("currentPostVersionId"))

    convex.open_whatsapp_window(
        user_id=user_id,
        recipient_phone=inbound.from_phone,
        inbound_message_id=inbound.message_id,
    )

    approval_action = approval_action_from_inbound(inbound)
    awaiting_revision_feedback = _request_waiting_for_revision_feedback(
        convex, pending
    )

    # Approval actions always take precedence over queue delivery. Previously
    # this path re-sent every already-delivered legacy draft before handling a
    # button, causing duplicate stories and preventing publish/reject/review.
    is_approval_action = approval_action is not None or awaiting_revision_feedback

    queued_requests = [
        request
        for request in pending_requests
        if not request.get("kapsoOutboundMessageId")
    ]
    if queued_requests and not is_approval_action:
        for queued_request in queued_requests:
            delivered = _deliver_queued_approval(
                convex=convex,
                kapso_client=kapso_client,
                pending=queued_request,
                inbound=inbound,
                content_gen=content_gen,
                story_detector=story_detector,
                commit_analyzer=commit_analyzer,
                github_client=github_client,
            )
            if not delivered:
                break
        return

    # Fetch post and latest version for decisions on the current approval.
    post = convex.client.query("posts:getById", {"postId": post_id})
    latest_version = convex.client.query("postVersions:getLatestForPost", {"postId": post_id})
    draft_body = latest_version.get("body") if latest_version else ""
    version_num = int(latest_version.get("version", 1)) if latest_version else 1
    latest_title = "Historia técnica"
    if latest_version:
        raw_title = latest_version.get("title")
        if isinstance(raw_title, str) and raw_title.strip():
            latest_title = raw_title.strip()

    original_version_num = version_num
    latest_title, draft_body, version_num = _regenerate_legacy_draft(
        convex=convex,
        content_gen=content_gen,
        story_detector=story_detector,
        commit_analyzer=commit_analyzer,
        github_client=github_client,
        pending=pending,
        title=latest_title,
        body=str(draft_body or ""),
        version_num=version_num,
    )
    if version_num != original_version_num:
        # The user may have replied to the old draft. Do not interpret that
        # reply as approval for content they have not seen yet.
        try:
            outbound = kapso_client.send_draft_for_approval(
                to_phone=inbound.from_phone,
                story_title=latest_title,
                post_body=draft_body,
                version=version_num,
            )
        except httpx.HTTPStatusError as error:
            logger.warning("Could not resend recovered draft: %s", error)
            return
        if outbound.message_id:
            convex.set_approval_outbound_message_id(
                approval_request_id=req_id,
                kapso_message_id=outbound.message_id,
            )
            convex.record_approval_message(
                approval_request_id=req_id,
                direction="outbound",
                message_id=outbound.message_id,
                content=outbound.body,
            )
        convex.record_activity(
            user_id=user_id,
            type_="approval.whatsapp.sent",
            label=f"Sent regenerated draft V{version_num} to WhatsApp",
            status="completed",
            metadata={
                "approvalRequestId": req_id,
                "trigger": "legacy_draft_recovery",
            },
        )
        return

    # Buttons are deterministic actions. Every free-form WhatsApp message is
    # interpreted by the AI agent, which can request a visual tool call.
    button_decisions = {
        "publish": ApprovalDecision(
            intent="approve",
            confidence=1.0,
            reasoning="Usuario pulsó el botón Publicar.",
        ),
        "reject": ApprovalDecision(
            intent="reject",
            confidence=1.0,
            reasoning="Usuario pulsó el botón Descartar.",
        ),
        "review": ApprovalDecision(
            intent="revise",
            confidence=1.0,
            reasoning="Usuario pulsó el botón Revisar.",
        ),
    }
    decision = button_decisions.get(approval_action or "")
    if decision is None:
        decision = agent.interpret_message(
            inbound.body,
            draft_body,
            awaiting_revision_feedback=awaiting_revision_feedback,
        )

    convex.record_approval_message(
        approval_request_id=req_id,
        direction="inbound",
        message_id=inbound.message_id,
        content=inbound.body,
        interpreted_intent=decision.intent,
        confidence=decision.confidence,
    )
    convex.record_activity(
        user_id=user_id,
        type_="approval.intent.detected",
        label=f"WhatsApp reply classified as '{decision.intent}' (confidence: {int(decision.confidence * 100)}%)",
        status="completed",
        metadata={
            "intent": decision.intent,
            "message": inbound.body,
            "confidence": str(decision.confidence),
        },
    )

    # A visual tool call stays inside the user-initiated 24-hour window and
    # creates a new post version with the generated asset attached.
    if decision.intent == "generate_visual":
        visual_request = decision.visual_request
        if visual_request is None:
            logger.warning("Visual intent without a structured visual request")
            kapso_client.send_message(
                inbound.from_phone,
                "Entendí que quieres un recurso visual, pero necesito que me indiques qué debería mostrar.",
            )
            return
        try:
            story_id = str(post.get("storyId")) if post else ""
            story_data = (
                cast(
                    dict[str, Any] | None,
                    convex.client.query("stories:getById", {"storyId": story_id}),
                )
                if story_id
                else None
            )
            story_summary = draft_body[:500]
            if story_data:
                raw_summary = story_data.get("summary")
                if isinstance(raw_summary, str) and raw_summary.strip():
                    story_summary = raw_summary.strip()
            generated_image = image_generator.generate_for_story(
                story_title=latest_title,
                story_summary=story_summary,
                post_body=draft_body,
                user_request=visual_request.instruction,
                visual_kind=visual_request.kind,
                preferences=convex.get_user_preferences(user_id) or EditorialPreferences(),
            )
            stored_media = convex.upload_media(
                content=generated_image.data,
                mime_type=generated_image.mime_type,
            )
            visual_version_num = version_num + 1
            visual_version_id = convex.record_post_version(
                post_id=post_id,
                version=visual_version_num,
                title=latest_title,
                body=draft_body,
                generation_reason=f"Visual asset requested: {inbound.body}",
            )
            convex.record_media_asset(
                post_version_id=visual_version_id,
                kind="image",
                storage_id=stored_media["storageId"],
                mime_type=generated_image.mime_type,
                url=stored_media["url"],
                alt_text=f"Ilustración sobre {latest_title}",
                source="openai",
                prompt=generated_image.prompt,
            )
            convex.update_approval_request(
                approval_request_id=req_id,
                status="pending",
                current_post_version_id=visual_version_id,
            )
            outbound = kapso_client.send_draft_for_approval(
                to_phone=inbound.from_phone,
                story_title=latest_title,
                post_body=draft_body,
                version=visual_version_num,
                image_url=stored_media["url"],
            )
            if outbound.message_id:
                convex.set_approval_outbound_message_id(
                    approval_request_id=req_id,
                    kapso_message_id=outbound.message_id,
                )
            convex.record_activity(
                user_id=user_id,
                type_="media.image.generated",
                label=f"Generated {visual_request.kind} asset for the draft",
                status="completed",
                metadata={
                    "postVersionId": visual_version_id,
                    "version": str(visual_version_num),
                    "visualKind": visual_request.kind,
                },
            )
            if outbound.message_id:
                convex.record_approval_message(
                    approval_request_id=req_id,
                    direction="outbound",
                    message_id=outbound.message_id,
                    content=outbound.body,
                )
        except ImageGenerationUnavailable as error:
            logger.warning("Image generation unavailable: %s", error)
            kapso_client.send_message(
                inbound.from_phone,
                "No pude generar la imagen todavía. Revisa que la API de imágenes esté configurada e inténtalo de nuevo.",
            )
        except Exception:
            logger.exception("Image generation or storage failed")
            kapso_client.send_message(
                inbound.from_phone,
                "La imagen no se pudo adjuntar en este intento. El borrador sigue disponible; inténtalo de nuevo en unos segundos.",
            )
        return

    if approval_action == "review":
        try:
            outbound = kapso_client.send_revision_prompt(inbound.from_phone)
        except httpx.HTTPStatusError as error:
            logger.warning("Could not send revision prompt: %s", error)
            return
        if outbound.message_id:
            convex.record_approval_message(
                approval_request_id=req_id,
                direction="outbound",
                message_id=outbound.message_id,
                content=outbound.body,
            )
        return

    # 3. Handle Decision
    if decision.intent == "approve":
        # Safe approval: Explicit approval
        convex.approve_post_version(current_version_id)
        convex.update_post_status(post_id, "approved")
        convex.update_approval_request(approval_request_id=req_id, status="approved")

        convex.record_activity(
            user_id=user_id,
            type_="linkedin.publish.started",
            label="Publishing approved post to LinkedIn",
            status="started",
        )

        # Publish to LinkedIn
        social_acc = convex.get_social_account(user_id, "linkedin")
        raw_urn = social_acc.get("authorUrn") if social_acc else None
        author_urn = str(raw_urn) if raw_urn else "urn:li:person:developer"
        enc_token = str(social_acc.get("accessTokenEncrypted")) if social_acc else None
        media_assets = convex.list_media_for_post_version(current_version_id)

        pub_res = publisher.publish_post(
            author_urn=author_urn,
            commentary=draft_body,
            encrypted_access_token=enc_token,
            media=media_assets,
        )

        if pub_res.status == "published":
            convex.set_post_external_urn(post_id, pub_res.post_urn, "published")
            convex.record_activity(
                user_id=user_id,
                type_="linkedin.publish.completed",
                label=f"Post live on LinkedIn ({pub_res.post_urn})",
                status="completed",
                metadata={"externalPostUrn": pub_res.post_urn},
            )
            try:
                kapso_client.send_published_confirmation(inbound.from_phone, pub_res.post_urn)
            except httpx.HTTPStatusError as error:
                logger.warning("LinkedIn published but WhatsApp confirmation failed: %s", error)
        else:
            convex.update_post_status(post_id, "failed")
            convex.record_activity(
                user_id=user_id,
                type_="linkedin.publish.failed",
                label=f"LinkedIn publish failed: {pub_res.error}",
                status="failed",
            )

    elif decision.intent == "revise":
        convex.update_approval_request(approval_request_id=req_id, status="revised")
        convex.record_activity(
            user_id=user_id,
            type_="post.revision.started",
            label=f"Generating revision V{version_num + 1} with user feedback",
            status="started",
        )

        # Fetch underlying story
        story_id = str(post.get("storyId")) if post else None
        story_data = (
            convex.client.query("stories:getById", {"storyId": story_id}) if story_id else None
        )

        dummy_story = StoryDetectionResult(
            storyDetected=True,
            confidence=0.9,
            publishability=0.9,
            storyType="problem_solution",
            title=str(story_data.get("title")) if story_data else "Technical Story",
            summary=str(story_data.get("summary")) if story_data else "Summary",
            problem=str(story_data.get("problem")) if (story_data and story_data.get("problem")) else "Problem",
            attempts=cast(list[str], story_data.get("attempts")) if (story_data and isinstance(story_data.get("attempts"), list)) else [],
            solution=str(story_data.get("solution")) if (story_data and story_data.get("solution")) else "Solution",
            learning=str(story_data.get("learning")) if (story_data and story_data.get("learning")) else "Learning",
            impact=str(story_data.get("impact")) if (story_data and story_data.get("impact")) else "Impact",
        )

        new_draft = content_gen.generate_draft(
            story=dummy_story,
            revision_feedback=decision.feedback or inbound.body,
            previous_draft=draft_body,
            preferences=convex.get_user_preferences(user_id),
        )

        new_version_num = version_num + 1
        new_version_id = convex.record_post_version(
            post_id=post_id,
            version=new_version_num,
            title=new_draft.title,
            body=new_draft.body,
            generation_reason=f"Revision request: {inbound.body}",
        )

        convex.record_activity(
            user_id=user_id,
            type_="post.revision.completed",
            label=f"LinkedIn draft V{new_version_num} generated",
            status="completed",
            metadata={"postId": post_id, "versionId": new_version_id},
        )

        # Send new draft to WhatsApp
        try:
            outbound = kapso_client.send_draft_for_approval(
                to_phone=inbound.from_phone,
                story_title=new_draft.title,
                post_body=new_draft.body,
                version=new_version_num,
            )
        except httpx.HTTPStatusError as error:
            logger.warning("Revision was saved but WhatsApp delivery failed: %s", error)
            return

        new_req_id = convex.record_approval_request(
            user_id=user_id,
            post_id=post_id,
            current_post_version_id=new_version_id,
            recipient_phone=inbound.from_phone,
            status="pending",
            kapso_msg_id=outbound.message_id,
        )


        convex.record_activity(
            user_id=user_id,
            type_="approval.whatsapp.sent",
            label=f"Sent draft V{new_version_num} to WhatsApp ({inbound.from_phone})",
            status="completed",
            metadata={"approvalRequestId": new_req_id},
        )

    elif decision.intent == "reject":
        convex.update_approval_request(approval_request_id=req_id, status="rejected")
        convex.update_post_status(post_id, "rejected")
        try:
            kapso_client.send_message(
                inbound.from_phone,
                "❌ Entendido, descarté la publicación de este borrador.",
            )
        except httpx.HTTPStatusError as error:
            logger.warning("Draft rejected but WhatsApp confirmation failed: %s", error)

    else:
        # clarify or hold
        convex.update_approval_request(approval_request_id=req_id, status=decision.intent)
        kapso_client.send_clarification(inbound.from_phone)


@router.post("", status_code=status.HTTP_200_OK)
async def receive_kapso_webhook(
    request: Request,
    background_tasks: BackgroundTasks,
) -> dict[str, str]:
    settings = get_settings()
    body = await request.body()

    signature = request.headers.get("x-webhook-signature")
    if settings.kapso_webhook_secret:
        try:
            verify_kapso_signature(body, signature, settings.kapso_webhook_secret)
        except InvalidKapsoSignature as error:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail=str(error)
            ) from error

    try:
        raw_payload = json.loads(body)
        if not isinstance(raw_payload, dict):
            raise ValueError("Payload must be a JSON object")
        payload = cast(dict[str, Any], raw_payload)
    except Exception as error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=f"Invalid JSON: {error}"
        ) from error

    inbounds = parse_kapso_inbound_messages(payload)
    if not inbounds:
        return {"status": "ignored", "reason": "Not an inbound user message"}

    for inbound in inbounds:
        background_tasks.add_task(_handle_inbound_whatsapp, inbound)
    return {
        "status": "accepted",
        "message_id": inbounds[0].message_id,
        "message_count": str(len(inbounds)),
    }
