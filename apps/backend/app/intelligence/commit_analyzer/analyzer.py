import json
import re

from app.config import Settings
from app.schemas.commit_analysis import CommitAnalysis
from app.schemas.github import NormalizedCommit


class CommitAnalyzer:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings

    def analyze(self, commit: NormalizedCommit) -> CommitAnalysis:
        if self.settings.openai_api_key:
            try:
                analysis = self._analyze_with_llm(commit)
                if not self._is_placeholder_analysis(analysis, commit):
                    return analysis
            except Exception:
                pass

        return self._analyze_heuristic(commit)

    def _analyze_with_llm(self, commit: NormalizedCommit) -> CommitAnalysis:
        from openai import OpenAI

        client = OpenAI(api_key=self.settings.openai_api_key)
        prompt = (
            f"Analyze this technical commit and return structured JSON matching the schema.\n"
            f"Commit SHA: {commit.sha}\n"
            f"Message: {commit.message}\n"
            f"Changed files: {[f.path for f in commit.files]}\n"
            f"Additions: {commit.additions}, Deletions: {commit.deletions}\n"
        )

        response = client.chat.completions.create(
            model=self.settings.openai_model,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are an expert software engineer analyzing code commits. "
                        "Ground your analysis strictly in the provided commit message and files. "
                        "Output valid JSON only with keys: type, summary, problem, solution, "
                        "impact, technologies, importance (0.0 to 1.0), publishability (0.0 to 1.0), "
                        "potential_story (boolean)."
                    ),
                },
                {"role": "user", "content": prompt},
            ],
            response_format={"type": "json_object"},
        )

        content = response.choices[0].message.content or "{}"
        data = json.loads(content)
        return CommitAnalysis.model_validate(data)

    def _analyze_heuristic(self, commit: NormalizedCommit) -> CommitAnalysis:
        msg = commit.message.lower()
        subject = self._human_message(commit.message)
        scope = self._scope_for_commit(commit)
        technologies = self._detect_technologies(commit)

        commit_type = "feature"
        if msg.startswith("fix") or "bug" in msg or "prevent" in msg or "fix duplicate" in msg:
            commit_type = "bugfix"
        elif msg.startswith("refactor") or "replace" in msg:
            commit_type = "refactor"
        elif msg.startswith("perf") or "performance" in msg:
            commit_type = "performance"
        elif msg.startswith("docs"):
            commit_type = "docs"
        elif msg.startswith("test"):
            commit_type = "developer_experience"
        elif "architect" in msg:
            commit_type = "architecture_change"

        importance = min(0.9, 0.4 + (commit.additions + commit.deletions) / 200.0)
        publishability = min(0.95, 0.5 + (0.3 if commit_type in {"feature", "refactor"} else 0.1))
        potential_story = publishability >= 0.6 or len(commit.files) >= 2

        problem: str | None = None
        solution: str | None = None

        if commit_type == "bugfix":
            problem = f"Había un problema en {scope}: {subject}."
            solution = f"Corregimos {subject} en {scope}."
        elif commit_type == "refactor":
            problem = f"La implementación de {scope} necesitaba una estructura más mantenible."
            solution = f"Reorganizamos {scope} para {subject}."
        elif commit_type == "docs":
            problem = f"El proyecto necesitaba hacer más comprensible {subject}."
            solution = f"Documentamos {subject} dentro de {scope}."
        else:
            problem = f"El producto necesitaba {subject} en {scope}."
            solution = f"Añadimos {subject} en {scope}."

        summary = f"{self._summary_verb(commit_type, commit.message)} {subject} en {scope}."
        changed_paths = ", ".join(file.path for file in commit.files[:3])
        path_context = f" Archivos principales: {changed_paths}." if changed_paths else ""
        impact = (
            f"El cambio afectó {commit.changed_files} archivo(s) (+{commit.additions}/-{commit.deletions})."
            f"{path_context}"
        )

        return CommitAnalysis(
            type=commit_type,  # type: ignore[arg-type]
            summary=summary,
            problem=problem,
            solution=solution,
            impact=impact,
            technologies=technologies,
            importance=round(importance, 2),
            publishability=round(publishability, 2),
            potential_story=potential_story,
        )

    def _detect_technologies(self, commit: NormalizedCommit) -> list[str]:
        techs: set[str] = set()
        msg = commit.message.lower()
        if "websocket" in msg or "socket" in msg:
            techs.add("WebSockets")
        if "polling" in msg:
            techs.add("Polling")
        if "convex" in msg:
            techs.add("Convex")
        if "fastapi" in msg:
            techs.add("FastAPI")
        if "react" in msg or "next" in msg:
            techs.add("Next.js")

        for f in commit.files:
            path = f.path.lower()
            if path.endswith(".ts") or path.endswith(".tsx"):
                techs.add("TypeScript")
            if path.endswith(".py"):
                techs.add("Python")
            if "socket" in path:
                techs.add("WebSockets")
            if "poll" in path:
                techs.add("Polling")
            if "/backend/" in f"/{path}" or path.startswith("backend/"):
                techs.add("Backend")
            if "/web/" in f"/{path}" or path.startswith("web/"):
                techs.add("Next.js")
            if path.startswith("convex/") or "/convex/" in f"/{path}":
                techs.add("Convex")
            if "dockerfile" in path or path.endswith("compose.yaml"):
                techs.add("Docker")
            if path.startswith(".github/"):
                techs.add("GitHub Actions")

        return sorted(list(techs))

    @staticmethod
    def _human_message(message: str) -> str:
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
    def _scope_for_commit(commit: NormalizedCommit) -> str:
        paths = [file.path.lower() for file in commit.files]
        signals = " ".join([commit.message.lower(), *paths])
        if "convex" in signals:
            return "la persistencia en Convex"
        if "webhook" in signals or "github" in signals:
            return "la integración con GitHub"
        if "linkedin" in signals:
            return "la publicación en LinkedIn"
        if "whatsapp" in signals or "kapso" in signals:
            return "el flujo de aprobación por WhatsApp"
        if any(path.startswith("apps/web/") or path.startswith("web/") for path in paths):
            return "la experiencia web"
        if any(path.startswith("apps/backend/") or path.startswith("backend/") for path in paths):
            return "el backend"
        return "el producto"

    @staticmethod
    def _summary_verb(commit_type: str, message: str) -> str:
        action = message.strip().lower().split(":", 1)[-1].strip().split(" ", 1)[0]
        if action in {"update", "updates", "updated", "configure", "configured", "set"}:
            return "Ajustamos"
        if action in {"enable", "enabled", "improve", "improved"}:
            return "Mejoramos"
        return {
            "bugfix": "Corregimos",
            "refactor": "Reestructuramos",
            "docs": "Documentamos",
            "performance": "Optimizamos",
            "developer_experience": "Mejoramos la experiencia de desarrollo con",
        }.get(commit_type, "Añadimos")

    @staticmethod
    def _is_placeholder_analysis(
        analysis: CommitAnalysis,
        commit: NormalizedCommit,
    ) -> bool:
        content = " ".join(
            value.lower()
            for value in (analysis.summary, analysis.problem or "", analysis.solution or "")
        )
        return (
            f"commit {commit.sha[:7]}" in content
            or "feature or capability needed by users" in content
            or "implemented commit" in content
        )
