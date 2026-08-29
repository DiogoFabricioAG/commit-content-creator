import json
import logging
import unicodedata
from typing import Any, cast

from fastapi import APIRouter, BackgroundTasks, HTTPException, Request, status

from app.config import get_settings
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
from app.schemas.story import StoryDetectionResult
from app.whatsapp.kapso.client import KapsoClient
from app.whatsapp.kapso.webhooks import (
    InvalidKapsoSignature,
    parse_kapso_inbound_messages,
    verify_kapso_signature,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/webhooks/kapso", tags=["kapso"])


def _requests_image_generation(message: str) -> bool:
    normalized = "".join(
        character
        for character in unicodedata.normalize("NFKD", message.lower())
        if not unicodedata.combining(character)
    )
    return any(
        phrase in normalized
        for phrase in (
            "genera una imagen",
            "genera imagen",
            "crea una imagen",
            "haz una imagen",
        )
    )


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
    commits = _normalized_commits_from_convex(convex.list_commits_by_ids(commit_ids))
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
) -> None:
    req_id = str(pending.get("_id"))
    post_id = str(pending.get("postId"))
    user_id = str(pending.get("userId"))
    post_version = convex.client.query(
        "postVersions:getLatestForPost", {"postId": post_id}
    )
    if not post_version:
        logger.warning("Approval %s has no post version", req_id)
        return

    title = str(post_version.get("title") or "Historia técnica")
    body = str(post_version.get("body") or "")
    version_num = int(post_version.get("version", 1))
    title, body, version_num = _regenerate_legacy_draft(
        convex=convex,
        content_gen=content_gen,
        story_detector=story_detector,
        commit_analyzer=commit_analyzer,
        pending=pending,
        title=title,
        body=body,
        version_num=version_num,
    )
    outbound = kapso_client.send_draft_for_approval(
        to_phone=inbound.from_phone,
        story_title=title,
        post_body=body,
        version=version_num,
    )
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


def _handle_inbound_whatsapp(inbound: KapsoInboundMessage) -> None:
    settings = get_settings()
    convex = ConvexGateway(settings)
    if not convex.is_configured:
        return

    agent = ApprovalAgent(settings)
    content_gen = ContentGenerator(settings)
    story_detector = StoryDetector(settings)
    commit_analyzer = CommitAnalyzer(settings)
    image_generator = OpenAIImageGenerator(settings)
    publisher = LinkedInPublisher(settings)
    kapso_client = KapsoClient(settings)

    # 1. Lookup all pending approvals for this phone. One inbound message opens
    # a single 24-hour window and releases every approval queued before it.
    pending_requests = convex.list_pending_approvals_for_phone(inbound.from_phone)
    if not pending_requests:
        logger.info("No pending approval found for phone %s", inbound.from_phone)
        return

    pending = pending_requests[-1]
    req_id = str(pending.get("_id"))
    post_id = str(pending.get("postId"))
    user_id = str(pending.get("userId"))
    current_version_id = str(pending.get("currentPostVersionId"))

    convex.open_whatsapp_window(
        user_id=user_id,
        recipient_phone=inbound.from_phone,
        inbound_message_id=inbound.message_id,
    )
    queued_requests = [
        request
        for request in pending_requests
        if not request.get("kapsoOutboundMessageId")
    ]
    if queued_requests:
        for queued_request in queued_requests:
            _deliver_queued_approval(
                convex=convex,
                kapso_client=kapso_client,
                pending=queued_request,
                inbound=inbound,
                content_gen=content_gen,
                story_detector=story_detector,
                commit_analyzer=commit_analyzer,
            )
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

    # Explicit media command. This remains inside the user-initiated 24-hour
    # window and attaches the generated asset to the current post version.
    if _requests_image_generation(inbound.body):
        convex.record_approval_message(
            approval_request_id=req_id,
            direction="inbound",
            message_id=inbound.message_id,
            content=inbound.body,
            interpreted_intent="generate_image",
            confidence=1.0,
        )
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
            )
            stored_media = convex.upload_media(
                content=generated_image.data,
                mime_type=generated_image.mime_type,
            )
            convex.record_media_asset(
                post_version_id=current_version_id,
                kind="image",
                storage_id=stored_media["storageId"],
                mime_type=generated_image.mime_type,
                url=stored_media["url"],
                alt_text=f"Ilustración sobre {latest_title}",
                source="openai",
                prompt=generated_image.prompt,
            )
            outbound = kapso_client.send_draft_for_approval(
                to_phone=inbound.from_phone,
                story_title=latest_title,
                post_body=draft_body,
                version=version_num,
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
                label="Generated image asset for the approved draft",
                status="completed",
                metadata={"postVersionId": current_version_id},
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

    # 2. Interpret intent
    button_decisions = {
        "approval_publish": ApprovalDecision(
            intent="approve",
            confidence=1.0,
            reasoning="Usuario pulsó el botón Publicar.",
        ),
        "approval_reject": ApprovalDecision(
            intent="reject",
            confidence=1.0,
            reasoning="Usuario pulsó el botón Descartar.",
        ),
    }
    button_decision = (
        button_decisions.get(inbound.button_id) if inbound.button_id else None
    )
    decision = button_decision or agent.interpret_message(inbound.body, draft_body)

    # Record message in Convex
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

    if inbound.button_id == "approval_review":
        outbound = kapso_client.send_revision_prompt(inbound.from_phone)
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
            kapso_client.send_published_confirmation(inbound.from_phone, pub_res.post_urn)
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
        outbound = kapso_client.send_draft_for_approval(
            to_phone=inbound.from_phone,
            story_title=new_draft.title,
            post_body=new_draft.body,
            version=new_version_num,
        )

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
        kapso_client.send_message(
            inbound.from_phone,
            "❌ Entendido, descarté la publicación de este borrador.",
        )

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
