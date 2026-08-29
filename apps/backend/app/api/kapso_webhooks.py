import json
import logging
from typing import Any, cast

from fastapi import APIRouter, BackgroundTasks, HTTPException, Request, status

from app.config import get_settings
from app.integrations.convex_client import ConvexGateway
from app.intelligence.approval_agent.agent import ApprovalAgent
from app.intelligence.content_generator.generator import ContentGenerator
from app.linkedin.publisher import LinkedInPublisher
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


def _handle_inbound_whatsapp(inbound: KapsoInboundMessage) -> None:
    settings = get_settings()
    convex = ConvexGateway(settings)
    if not convex.is_configured:
        return

    agent = ApprovalAgent(settings)
    content_gen = ContentGenerator(settings)
    publisher = LinkedInPublisher(settings)
    kapso_client = KapsoClient(settings)

    # 1. Lookup pending approval for this phone
    pending = convex.get_pending_approval_for_phone(inbound.from_phone)
    if not pending:
        logger.info("No pending approval found for phone %s", inbound.from_phone)
        return

    req_id = str(pending.get("_id"))
    post_id = str(pending.get("postId"))
    user_id = str(pending.get("userId"))
    current_version_id = str(pending.get("currentPostVersionId"))

    # Fetch post and latest version
    post = convex.client.query("posts:getById", {"postId": post_id})
    latest_version = convex.client.query("postVersions:getLatestForPost", {"postId": post_id})
    draft_body = latest_version.get("body") if latest_version else ""
    version_num = int(latest_version.get("version", 1)) if latest_version else 1

    # 2. Interpret intent
    decision = agent.interpret_message(inbound.body, draft_body)

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

        pub_res = publisher.publish_post(
            author_urn=author_urn,
            commentary=draft_body,
            encrypted_access_token=enc_token,
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
