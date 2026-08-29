from app.config import Settings
from app.intelligence.commit_analyzer.analyzer import CommitAnalyzer
from app.intelligence.story_detector.detector import StoryDetector
from app.schemas.github import CommitFile, NormalizedCommit


def test_story_detector_multi_commit_arc() -> None:
    settings = Settings(app_env="test")
    analyzer = CommitAnalyzer(settings)
    detector = StoryDetector(settings)

    commits = [
        NormalizedCommit(
            sha="c1",
            author="Dev",
            message="feat: add notification polling",
            committed_at=100,
            additions=42,
            deletions=0,
            changed_files=1,
            files=[CommitFile(path="src/poller.ts")],
        ),
        NormalizedCommit(
            sha="c2",
            author="Dev",
            message="fix: prevent duplicate notification requests",
            committed_at=200,
            additions=18,
            deletions=5,
            changed_files=1,
            files=[CommitFile(path="src/poller.ts")],
        ),
        NormalizedCommit(
            sha="c3",
            author="Dev",
            message="refactor: replace polling with websocket events",
            committed_at=300,
            additions=76,
            deletions=61,
            changed_files=2,
            files=[CommitFile(path="src/socket.ts"), CommitFile(path="src/poller.ts")],
        ),
    ]

    analyses = [analyzer.analyze(c) for c in commits]
    story = detector.detect_story(commits, analyses)

    assert story.story_detected is True
    assert "WebSockets" in story.title or "polling" in story.title.lower()
    assert story.confidence >= 0.8
    assert len(story.related_commit_shas) == 3
