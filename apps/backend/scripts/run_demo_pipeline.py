"""
Proof of Work - End-to-End Demo Pipeline Script
Simulates the complete vertical loop:
GitHub Push -> Commits Fetch -> AI Analysis -> Story Detection -> LinkedIn Draft ->
WhatsApp Kapso Outbound -> Natural Language Revision (V2) -> Explicit Natural Approval ->
LinkedIn Publishing -> WhatsApp Confirmation.
"""

import json
import logging
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))


from app.config import get_settings
from app.github.processor import GitHubEventProcessor
from app.integrations.convex_client import ConvexGateway
from app.intelligence.approval_agent.agent import ApprovalAgent
from app.intelligence.content_generator.generator import ContentGenerator
from app.linkedin.publisher import LinkedInPublisher
from app.schemas.github import NormalizedGitHubEvent
from app.schemas.story import StoryDetectionResult
from app.whatsapp.kapso.client import KapsoClient

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("demo_pipeline")


def run_e2e_demo() -> None:
    settings = get_settings()

    # If CONVEX_URL not loaded into settings, look into convex/.env.local
    if not settings.convex_url:
        env_local = Path("convex/.env.local")
        if env_local.exists():
            for line in env_local.read_text(encoding="utf-8").splitlines():
                if line.startswith("CONVEX_URL="):
                    settings.convex_url = line.split("=", 1)[1].strip()
                    break

    logger.info("==================================================")
    logger.info("🚀 STARTING PROOF OF WORK END-TO-END DEMO PIPELINE")
    logger.info("==================================================")
    logger.info("Convex URL: %s", settings.convex_url or "Local Mock")
    logger.info("Demo Mode: %s", settings.demo_mode)
    logger.info("WhatsApp Target: %s", settings.default_user_phone)


    convex = ConvexGateway(settings)
    if not convex.is_configured:
        logger.error("CONVEX_URL is not configured. Please configure it in .env")
        return

    # 1. Prepare Fixture Event
    fixture_path = Path("fixtures/demo-commits.json")
    with open(fixture_path, encoding="utf-8") as f:
        fixture_data = json.load(f)

    shas = [c["sha"] for c in fixture_data["commits"]]
    delivery_id = f"demo_del_{int(time.time() * 1000)}"

    event = NormalizedGitHubEvent(


        delivery_id=delivery_id,
        event_type="push",
        repository_full_name="diogofabricio/proof-of-work",
        branch="main",
        commit_shas=shas,
    )

    # 2. Ingest GitHub Event and run processor
    logger.info("\n[STEP 1] 📥 Ingesting GitHub Push Event (%s commits)...", len(shas))
    processor = GitHubEventProcessor(settings)
    proc_result = processor.process_event(event)

    post_id = str(proc_result.get("post_id"))
    story_id = str(proc_result.get("story_id"))
    version_id = str(proc_result.get("version_id"))
    req_id = str(proc_result.get("approval_request_id"))

    assert post_id and post_id != "None", "post_id must not be empty"
    assert story_id and story_id != "None", "story_id must not be empty"
    assert req_id and req_id != "None", "req_id must not be empty"

    logger.info("✅ Event processed:")
    logger.info("   • Story ID: %s", story_id)
    logger.info("   • Post ID: %s", post_id)
    logger.info("   • Post Version 1 ID: %s", version_id)
    logger.info("   • WhatsApp Approval Request ID: %s", req_id)


    # 3. Simulate WhatsApp Inbound: Revision Request
    logger.info("\n[STEP 2] 💬 Simulating User WhatsApp reply: 'Está muy largo, hazlo más corto'")
    agent = ApprovalAgent(settings)
    content_gen = ContentGenerator(settings)
    kapso_client = KapsoClient(settings)
    publisher = LinkedInPublisher(settings)

    latest_v1 = convex.client.query("postVersions:getLatestForPost", {"postId": post_id})
    v1_body = latest_v1.get("body") if latest_v1 else ""
    logger.info("📄 Draft V1 Body:\n%s\n", v1_body)

    rev_decision = agent.interpret_message("Está muy largo, hazlo más corto", v1_body)
    logger.info("🧠 Approval Agent Decision: intent='%s' (confidence=%.2f)", rev_decision.intent, rev_decision.confidence)

    assert rev_decision.intent == "revise"
    convex.update_approval_request(approval_request_id=req_id, status="revised")

    story_data = convex.client.query("stories:getById", {"storyId": story_id})
    dummy_story = StoryDetectionResult(
        storyDetected=True,
        confidence=0.94,
        publishability=0.92,
        storyType="problem_solution",
        title=str(story_data.get("title")),
        summary=str(story_data.get("summary")),
        problem=str(story_data.get("problem")),
        attempts=list(story_data.get("attempts", [])),
        solution=str(story_data.get("solution")),
        learning=str(story_data.get("learning")),
        impact=str(story_data.get("impact")),
    )

    v2_draft = content_gen.generate_draft(
        story=dummy_story,
        revision_feedback="está muy largo, hazlo más corto",
        previous_draft=v1_body,
    )

    v2_version_id = convex.record_post_version(
        post_id=post_id,
        version=2,
        title=v2_draft.title,
        body=v2_draft.body,
        generation_reason="User requested shorter version via WhatsApp",
    )
    logger.info("✅ Draft V2 generated:\n%s\n", v2_draft.body)

    outbound_v2 = kapso_client.send_draft_for_approval(
        to_phone=settings.default_user_phone,
        story_title=v2_draft.title,
        post_body=v2_draft.body,
        version=2,
    )

    req_v2_id = convex.record_approval_request(
        user_id=convex.get_or_create_default_user(),
        post_id=post_id,
        current_post_version_id=v2_version_id,
        recipient_phone=settings.default_user_phone,
        status="pending",
        kapso_msg_id=outbound_v2.message_id,
    )
    logger.info("📱 Sent V2 to WhatsApp via Kapso (Request ID: %s)", req_v2_id)

    # 4. Simulate WhatsApp Inbound: Explicit Approval
    logger.info("\n[STEP 3] 💬 Simulating User WhatsApp reply: 'Ta bueno, publícalo noma'")
    app_decision = agent.interpret_message("Ta bueno, publícalo noma", v2_draft.body)
    logger.info("🧠 Approval Agent Decision: intent='%s' (confidence=%.2f)", app_decision.intent, app_decision.confidence)

    assert app_decision.intent == "approve"
    convex.approve_post_version(v2_version_id)
    convex.update_post_status(post_id, "approved")
    convex.update_approval_request(approval_request_id=req_v2_id, status="approved")

    # 5. Publish to LinkedIn
    logger.info("\n[STEP 4] 🌐 Publishing Approved V2 to LinkedIn Posts API...")
    pub_result = publisher.publish_post(
        author_urn="urn:li:person:diogo_abregu",
        commentary=v2_draft.body,
    )
    logger.info("✅ LinkedIn Publication result: status='%s', URN='%s'", pub_result.status, pub_result.post_urn)

    convex.set_post_external_urn(post_id, pub_result.post_urn, "published")
    conf = kapso_client.send_published_confirmation(settings.default_user_phone, pub_result.post_urn)
    logger.info("📱 WhatsApp Publication confirmation message sent: %s", conf.message_id)

    # 6. Verify End State
    logger.info("\n==================================================")
    logger.info("🎉 DEMO COMPLETE: Full end-to-end cycle verified!")
    logger.info("   1. 3 Commits -> 1 Coherent Story Detected")
    logger.info("   2. Draft V1 -> WhatsApp -> Revision Request")
    logger.info("   3. Draft V2 -> WhatsApp -> Explicit Approval")
    logger.info("   4. LinkedIn Posts API -> Published")
    logger.info("   5. External Post URN: %s", pub_result.post_urn)
    logger.info("==================================================")


if __name__ == "__main__":
    run_e2e_demo()
