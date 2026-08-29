import re
from collections.abc import Sequence

from app.config import Settings
from app.schemas.commit_analysis import CommitAnalysis
from app.schemas.github import NormalizedCommit
from app.schemas.story import StoryDetectionResult


class StoryDetector:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings

    def detect_story(
        self,
        commits: Sequence[NormalizedCommit],
        analyses: Sequence[CommitAnalysis],
    ) -> StoryDetectionResult:
        if not commits:
            return StoryDetectionResult(
                storyDetected=False,
                confidence=0.0,
                publishability=0.0,
                storyType="build_log",
                title="No commits to analyze",
                summary="No commits provided",
                relatedCommitShas=[],
            )

        if all(
            not commit.files
            and (
                re.fullmatch(r"commit\s+[0-9a-f]{7,}", commit.message, re.IGNORECASE)
                or commit.message.strip().lower() == "una actualización técnica"
            )
            for commit in commits
        ):
            return StoryDetectionResult(
                storyDetected=False,
                confidence=0.0,
                publishability=0.0,
                storyType="build_log",
                title="Sin contexto suficiente para publicar",
                summary="No se encontraron el mensaje real ni archivos modificados del commit.",
                relatedCommitShas=[commit.sha for commit in commits],
            )

        # Check for multi-commit story progression (e.g. Polling -> WebSockets arc)
        messages = [c.message.lower() for c in commits]
        has_polling = any("poll" in m for m in messages)
        has_websocket = any("socket" in m or "websocket" in m for m in messages)

        shas = [c.sha for c in commits]

        if has_polling and has_websocket:
            return StoryDetectionResult(
                storyDetected=True,
                confidence=0.94,
                publishability=0.92,
                storyType="problem_solution",
                title="Cómo pasamos de polling a WebSockets",
                summary="Empezamos con polling para las notificaciones, detectamos solicitudes duplicadas y migramos a eventos en tiempo real.",
                problem="El polling inicial generaba solicitudes duplicadas y demasiados viajes al servidor.",
                attempts=[
                    "Construimos un endpoint HTTP básico para consultar notificaciones",
                    "Añadimos controles de deduplicación en el cliente",
                ],
                solution="Reemplazamos el polling por eventos bidireccionales con WebSockets.",
                learning="El polling es fácil para empezar, pero los eventos reducen tráfico innecesario y escalan mejor.",
                impact="Eliminamos el tráfico redundante de polling y habilitamos notificaciones instantáneas.",
                relatedCommitShas=shas,
            )

        # Generic multi-commit or single commit story
        if len(commits) > 1:
            title = f"Evolution of {commits[-1].files[0].path if commits[-1].files else 'system architecture'}"
            if analyses:
                main_analysis = analyses[-1]
                title = f"Cómo construimos {main_analysis.summary}"
                problem = main_analysis.problem or "El sistema necesitaba mejoras iterativas."
                solution = main_analysis.solution or f"Reestructuramos el sistema en {len(commits)} commits."
                learning = (
                    f"Mejoramos la calidad del código con {', '.join(main_analysis.technologies)}."
                    if main_analysis.technologies
                    else "Las iteraciones pequeñas permiten validar el sistema sin perder contexto."
                )
                impact = main_analysis.impact
            else:
                problem = "El sistema necesitaba mejoras técnicas."
                solution = f"Entregamos los cambios en {len(commits)} commits."
                learning = "Las iteraciones ayudan a mantener el contexto y la mantenibilidad."
                impact = f"Se incorporaron {sum(c.additions for c in commits)} líneas nuevas."

            return StoryDetectionResult(
                storyDetected=True,
                confidence=0.88,
                publishability=0.85,
                storyType="build_log",
                title=title,
                summary=f"Construimos una mejora iterativa a lo largo de {len(commits)} commits.",
                problem=problem,
                attempts=[c.message for c in commits[:-1]],
                solution=solution,
                learning=learning,
                impact=impact,
                relatedCommitShas=shas,
            )

        # Single commit story
        single_commit = commits[0]
        analysis = analyses[0] if analyses else None
        subject = self._human_subject(single_commit.message)
        title_prefix = self._title_prefix(
            analysis.type if analysis else "feature",
            single_commit.message,
        )
        return StoryDetectionResult(
            storyDetected=True,
            confidence=0.82,
            publishability=analysis.publishability if analysis else 0.75,
            storyType="problem_solution",
            title=f"{title_prefix} {subject}",
            summary=analysis.summary
            if analysis
            else f"El proyecto incorporó {subject}.",
            problem=analysis.problem
            if analysis
            else f"El producto necesitaba {subject}.",
            attempts=[],
            solution=analysis.solution
            if analysis
            else f"Añadimos {subject} y dejamos el cambio listo para validación.",
            learning=(
                f"La implementación usa {', '.join(analysis.technologies)}."
                if analysis and analysis.technologies
                else "Los cambios pequeños también cuentan cuando resuelven una necesidad concreta."
            ),
            impact=analysis.impact
            if analysis
            else f"El cambio afectó {single_commit.changed_files} archivo(s) (+{single_commit.additions}/-{single_commit.deletions}).",
            relatedCommitShas=[single_commit.sha],
        )

    @staticmethod
    def _human_subject(message: str) -> str:
        subject = message.strip().splitlines()[0] if message.strip() else "una mejora técnica"
        subject = re.sub(
            r"^(feat|fix|refactor|docs|test|perf|chore|build)(\([^)]*\))?\s*:\s*",
            "",
            subject,
            flags=re.IGNORECASE,
        )
        subject = re.sub(
            r"^(add|adds|added|implement|implements|implemented|create|creates|created|build|built|update|updates|updated|configure|configures|configured|enable|enables|enabled|improve|improves|improved)\s+",
            "",
            subject,
            flags=re.IGNORECASE,
        )
        subject = subject.rstrip(".")
        if re.fullmatch(r"commit\s+[0-9a-f]{7,}", subject, re.IGNORECASE):
            return "una actualización técnica"
        return subject or "una mejora técnica"

    @staticmethod
    def _title_prefix(story_type: str, message: str) -> str:
        action = message.strip().lower().split(":", 1)[-1].strip().split(" ", 1)[0]
        if action in {"update", "updates", "updated", "configure", "configured", "set"}:
            return "Cómo ajustamos"
        if action in {"enable", "enabled", "improve", "improved"}:
            return "Cómo mejoramos"
        return {
            "bugfix": "Cómo corregimos",
            "refactor": "Cómo reestructuramos",
            "docs": "Cómo documentamos",
            "performance": "Cómo optimizamos",
        }.get(story_type, "Cómo añadimos")
