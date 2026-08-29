from app.config import Settings
from app.intelligence.digest.historical_digest import HistoricalDigestBuilder
from app.schemas.commit_analysis import CommitAnalysis
from app.schemas.github import CommitFile, NormalizedCommit
from app.schemas.preferences import EditorialPreferences


def _commit(sha: str, message: str, path: str) -> NormalizedCommit:
    return NormalizedCommit(
        sha=sha,
        author="Developer",
        message=message,
        committed_at=1,
        additions=10,
        deletions=2,
        changed_files=1,
        files=[CommitFile(path=path)],
    )


def test_historical_digest_compiles_many_commits_into_one_story() -> None:
    commits = [
        _commit("sha-1", "feat: add ingestion", "apps/backend/app/main.py"),
        _commit("sha-2", "fix: validate webhook", "apps/backend/app/github/webhooks.py"),
        _commit("sha-3", "docs: explain the flow", "docs/README.md"),
    ]
    analyses = [
        CommitAnalysis(
            type="feature",
            summary="Added ingestion",
            technologies=["FastAPI"],
            importance=0.8,
            publishability=0.8,
        ),
        CommitAnalysis(
            type="bugfix",
            summary="Validated webhooks",
            technologies=["Python"],
            importance=0.9,
            publishability=0.8,
        ),
    ]

    digest = HistoricalDigestBuilder(Settings(openai_api_key=None)).build(
        repository_full_name="owner/repo",
        branch="main",
        commits=commits,
        analyses=analyses,
        preferences=EditorialPreferences(post_length="concise"),
    )

    assert digest.commit_shas == ["sha-1", "sha-2", "sha-3"]
    assert digest.filtered_commits == ()
    assert len(digest.story.related_commit_shas) == 3
    assert "3 commits" in digest.story.summary
    assert digest.draft.title == digest.story.title


def test_historical_digest_filters_operational_only_commits_but_keeps_evidence() -> None:
    commits = [
        _commit("sha-lock", "chore: refresh lockfile", "pnpm-lock.yaml"),
        _commit("sha-feature", "feat: add dashboard", "apps/web/app/page.tsx"),
    ]

    digest = HistoricalDigestBuilder(Settings(openai_api_key=None)).build(
        repository_full_name="owner/repo",
        commits=commits,
    )

    assert digest.commit_shas == ["sha-feature"]
    assert [commit.sha for commit in digest.filtered_commits] == ["sha-lock"]


def test_historical_digest_does_not_drop_a_repository_made_only_of_noise() -> None:
    commits = [_commit("sha-lock", "chore: refresh lockfile", "pnpm-lock.yaml")]

    digest = HistoricalDigestBuilder(Settings(openai_api_key=None)).build(
        repository_full_name="owner/repo",
        commits=commits,
    )

    assert digest.commit_shas == ["sha-lock"]
    assert digest.filtered_commits == ()
