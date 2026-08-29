from app.config import Settings
from app.intelligence.commit_analyzer.analyzer import CommitAnalyzer
from app.schemas.github import CommitFile, NormalizedCommit


def test_commit_analyzer_heuristic() -> None:
    settings = Settings(app_env="test")
    analyzer = CommitAnalyzer(settings)

    commit = NormalizedCommit(
        sha="abc1234",
        author="Dev",
        message="feat: add notification polling",
        committed_at=1724930000000,
        additions=42,
        deletions=0,
        changed_files=1,
        files=[
            CommitFile(
                path="src/notifications/poller.ts",
                status="added",
                additions=42,
                deletions=0,
            )
        ],
    )

    analysis = analyzer.analyze(commit)
    assert analysis.type == "feature"
    assert "TypeScript" in analysis.technologies or "Polling" in analysis.technologies
    assert 0.0 <= analysis.importance <= 1.0
    assert 0.0 <= analysis.publishability <= 1.0
