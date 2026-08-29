from collections import Counter
from collections.abc import Sequence
from dataclasses import dataclass

from app.config import Settings
from app.intelligence.content_generator.generator import ContentGenerator
from app.schemas.commit_analysis import CommitAnalysis
from app.schemas.content import LinkedInDraftResult
from app.schemas.github import NormalizedCommit
from app.schemas.preferences import EditorialPreferences
from app.schemas.story import StoryDetectionResult

_NOISE_SUFFIXES = (
    ".lock",
    ".lockb",
    ".pyc",
)
_NOISE_PATH_PARTS = (
    "/__pycache__/",
    "/.next/",
    "/node_modules/",
    "/dist/",
    "/build/",
    "/coverage/",
)
_NOISE_FILENAMES = {
    "package-lock.json",
    "pnpm-lock.yaml",
    "yarn.lock",
    "poetry.lock",
    "uv.lock",
}


@dataclass(frozen=True)
class HistoricalDigest:
    repository_full_name: str
    branch: str | None
    included_commits: tuple[NormalizedCommit, ...]
    filtered_commits: tuple[NormalizedCommit, ...]
    story: StoryDetectionResult
    draft: LinkedInDraftResult

    @property
    def commit_shas(self) -> list[str]:
        return [commit.sha for commit in self.included_commits]


class HistoricalDigestBuilder:
    """Compile a repository history into one grounded story and one draft."""

    def __init__(self, settings: Settings) -> None:
        self.content_generator = ContentGenerator(settings)

    def build(
        self,
        *,
        repository_full_name: str,
        commits: Sequence[NormalizedCommit],
        analyses: Sequence[CommitAnalysis] = (),
        branch: str | None = None,
        preferences: EditorialPreferences | None = None,
    ) -> HistoricalDigest:
        included, filtered = self._select_evidence(commits)
        story = self._build_story(repository_full_name, included, analyses)
        draft = self.content_generator.generate_draft(story, preferences=preferences)
        return HistoricalDigest(
            repository_full_name=repository_full_name,
            branch=branch,
            included_commits=tuple(included),
            filtered_commits=tuple(filtered),
            story=story,
            draft=draft,
        )

    @classmethod
    def _select_evidence(
        cls, commits: Sequence[NormalizedCommit]
    ) -> tuple[list[NormalizedCommit], list[NormalizedCommit]]:
        included = [commit for commit in commits if not cls._is_noise_only(commit)]
        filtered = [commit for commit in commits if cls._is_noise_only(commit)]
        # Never produce an empty digest just because a small repository only
        # contains operational files. The fallback preserves all evidence.
        if not included and commits:
            return list(commits), []
        return included, filtered

    @classmethod
    def _is_noise_only(cls, commit: NormalizedCommit) -> bool:
        if not commit.files:
            return False
        return all(cls._is_noise_path(item.path) for item in commit.files)

    @classmethod
    def _is_noise_path(cls, path: str) -> bool:
        normalized_path = path.replace("\\", "/").lower().strip("/")
        normalized = f"/{normalized_path}/"
        filename = normalized_path.rsplit("/", 1)[-1]
        if filename in _NOISE_FILENAMES:
            return True
        if filename.endswith(_NOISE_SUFFIXES):
            return True
        return any(part in normalized for part in _NOISE_PATH_PARTS)

    @staticmethod
    def _build_story(
        repository_full_name: str,
        commits: Sequence[NormalizedCommit],
        analyses: Sequence[CommitAnalysis],
    ) -> StoryDetectionResult:
        if not commits:
            return StoryDetectionResult(
                storyDetected=False,
                confidence=0.0,
                publishability=0.0,
                storyType="build_log",
                title="No hay cambios para compilar",
                summary="El repositorio no tiene commits de evidencia disponibles.",
                relatedCommitShas=[],
            )

        type_counts = Counter(analysis.type for analysis in analyses)
        technologies = sorted(
            {
                technology
                for analysis in analyses
                for technology in analysis.technologies
            }
        )
        commit_messages = [commit.message.strip() for commit in commits if commit.message.strip()]
        attempts = commit_messages[-8:]
        total_additions = sum(commit.additions for commit in commits)
        total_deletions = sum(commit.deletions for commit in commits)
        type_summary = ", ".join(
            f"{kind} ({count})" for kind, count in type_counts.most_common(4)
        ) or "cambios de implementación"
        technology_summary = ", ".join(technologies[:8]) or "las tecnologías del repositorio"
        strongest_analysis = max(
            analyses,
            key=lambda analysis: analysis.importance,
            default=None,
        )

        return StoryDetectionResult(
            storyDetected=True,
            confidence=0.9 if len(commits) > 1 else 0.82,
            publishability=0.88 if len(commits) > 1 else 0.75,
            storyType="build_log",
            title=f"La evolución de {repository_full_name}",
            summary=(
                f"Compilamos {len(commits)} commits verificables en una sola historia de producto. "
                f"El arco reúne {type_summary} y muestra una construcción iterativa."
            ),
            problem=(
                f"El trabajo de {repository_full_name} se construyó por incrementos y estaba distribuido "
                f"en {len(commits)} cambios que debían leerse como una historia continua."
            ),
            attempts=attempts,
            solution=(
                f"Agrupamos los cambios de forma trazable y conservamos la evidencia de cada commit. "
                f"El historial muestra una evolución basada en {technology_summary}."
            ),
            learning=(
                "Un historial técnico comunica mejor cuando conecta decisiones, implementación y resultado "
                "sin convertir cada commit en una publicación aislada."
            ),
            impact=(
                f"Digest de {len(commits)} commits: +{total_additions}/-{total_deletions} líneas agregadas o eliminadas."
                + (
                    f" La evidencia de mayor peso fue: {strongest_analysis.summary}."
                    if strongest_analysis
                    else ""
                )
            ),
            relatedCommitShas=[commit.sha for commit in commits],
        )
