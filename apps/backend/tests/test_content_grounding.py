from app.config import Settings
from app.github.client import GitHubClient
from app.intelligence.commit_analyzer.analyzer import CommitAnalyzer
from app.intelligence.content_generator.generator import ContentGenerator
from app.intelligence.story_detector.detector import StoryDetector


def test_push_payload_fallback_keeps_commit_context() -> None:
    payload = {
        "commits": [
            {
                "id": "abc123456789",
                "message": "feat(auth): add GitHub session guard",
                "author": {"name": "Diogo"},
                "added": ["apps/backend/app/auth/guard.py"],
                "modified": ["apps/backend/app/main.py"],
                "removed": [],
            }
        ]
    }

    commit = GitHubClient(Settings(app_env="test")).fetch_commit(
        "owner/repo",
        "abc123456789",
        payload,
    )

    assert commit.message == "feat(auth): add GitHub session guard"
    assert commit.author == "Diogo"
    assert [file.path for file in commit.files] == [
        "apps/backend/app/auth/guard.py",
        "apps/backend/app/main.py",
    ]


def test_single_commit_story_and_draft_are_human_readable() -> None:
    settings = Settings(app_env="test")
    commit = GitHubClient(settings).fetch_commit(
        "owner/repo",
        "abc123456789",
        {
            "message": "feat(auth): add GitHub session guard",
            "author": {"name": "Diogo"},
            "added": ["apps/backend/app/auth/guard.py"],
            "modified": ["apps/backend/app/main.py"],
            "removed": [],
        },
    )
    analysis = CommitAnalyzer(settings).analyze(commit)
    story = StoryDetector(settings).detect_story([commit], [analysis])
    draft = ContentGenerator(settings).generate_draft(story)

    assert "Shipping" not in story.title
    assert commit.sha[:7] not in story.title
    assert "GitHub session guard" in story.title
    assert "Feature or capability needed by users" not in draft.body
    assert "Implemented Commit" not in draft.body
    assert "GitHub" in draft.body


def test_legacy_draft_is_detected_before_delivery() -> None:
    assert ContentGenerator.is_legacy_draft(
        "Shipping: Commit 9075a85",
        "Commit 9075a85: Commit 9075a85\n\nModified 0 files",
    )
    assert not ContentGenerator.is_legacy_draft(
        "Cómo añadimos una sesión de GitHub",
        "El reto:\nEl producto necesitaba una sesión de GitHub.",
    )


def test_missing_commit_metadata_does_not_turn_sha_into_a_story() -> None:
    settings = Settings(app_env="test")
    commit = GitHubClient(settings).fetch_commit(
        "owner/repo",
        "8813e7f8829d9cb5f2da5e94bedfb9293bc30e0a",
        {"message": "Commit 8813e7f", "added": [], "modified": [], "removed": []},
    )
    analysis = CommitAnalyzer(settings).analyze(commit)
    story = StoryDetector(settings).detect_story([commit], [analysis])

    assert commit.message == "una actualización técnica"
    assert story.story_detected is False
