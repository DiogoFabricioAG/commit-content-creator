import json

from app.config import Settings
from app.schemas.commit_analysis import CommitAnalysis
from app.schemas.github import NormalizedCommit


class CommitAnalyzer:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings

    def analyze(self, commit: NormalizedCommit) -> CommitAnalysis:
        if self.settings.openai_api_key:
            try:
                return self._analyze_with_llm(commit)
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
            temperature=0.2,
        )

        content = response.choices[0].message.content or "{}"
        data = json.loads(content)
        return CommitAnalysis.model_validate(data)

    def _analyze_heuristic(self, commit: NormalizedCommit) -> CommitAnalysis:
        msg = commit.message.lower()
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
            problem = f"Issue encountered: {commit.message}"
            solution = f"Fixed in {', '.join([f.path for f in commit.files[:2]])}"
        elif commit_type == "refactor":
            problem = "Previous architecture had limitations or scaling overhead"
            solution = f"Refactored: {commit.message}"
        else:
            problem = "Feature or capability needed by users"
            solution = f"Implemented {commit.message}"

        summary = f"Commit {commit.sha[:7]}: {commit.message}"
        impact = f"Modified {commit.changed_files} files (+{commit.additions}/-{commit.deletions})"

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

        return sorted(list(techs))
