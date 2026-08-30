from app.config import Settings
from app.github.processor import GitHubEventProcessor
from app.schemas.github import NormalizedGitHubEvent


def test_github_processor_skips_cleanly_when_convex_not_configured() -> None:
    settings = Settings(app_env="test", convex_url=None)
    processor = GitHubEventProcessor(settings)
    event = NormalizedGitHubEvent(
        delivery_id="del-test",
        event_type="push",
        repository_full_name="user/test-repo",
        commit_shas=["sha-123"],
    )
    result = processor.process_event(event)
    assert result["status"] == "skipped"
