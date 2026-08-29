from app.config import Settings
from app.intelligence.content_generator.generator import ContentGenerator
from app.schemas.story import StoryDetectionResult


def test_content_generator_and_revision() -> None:
    settings = Settings(app_env="test")
    generator = ContentGenerator(settings)

    story = StoryDetectionResult(
        storyDetected=True,
        confidence=0.9,
        publishability=0.9,
        storyType="problem_solution",
        title="Why we replaced polling with WebSockets",
        summary="From polling overhead to real-time events.",
        problem="High polling traffic caused duplicate requests",
        attempts=["Basic poller"],
        solution="WebSockets",
        learning="Event-driven architectures scale better",
        impact="Reduced overhead",
        relatedCommitShas=["c1", "c2", "c3"],
    )

    draft_v1 = generator.generate_draft(story)
    assert len(draft_v1.body) > 50
    assert "WebSockets" in draft_v1.body

    # Revision V2 (shorter)
    draft_v2 = generator.generate_draft(
        story,
        revision_feedback="está muy largo, hazlo más corto",
        previous_draft=draft_v1.body,
    )
    assert len(draft_v2.body) < len(draft_v1.body)
