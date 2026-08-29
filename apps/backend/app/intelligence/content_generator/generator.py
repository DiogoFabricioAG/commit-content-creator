import json
import re
from typing import Literal, cast

from app.config import Settings
from app.schemas.content import LinkedInDraftResult
from app.schemas.preferences import EditorialPreferences
from app.schemas.story import StoryDetectionResult

ContentFormat = Literal[
    "problem_solution",
    "before_after",
    "build_log",
    "architecture_breakdown",
    "failure_story",
    "mini_case_study",
]


class ContentGenerator:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings

    def generate_draft(
        self,
        story: StoryDetectionResult,
        revision_feedback: str | None = None,
        previous_draft: str | None = None,
        preferences: EditorialPreferences | None = None,
    ) -> LinkedInDraftResult:
        prefs = preferences or EditorialPreferences()

        if self.settings.openai_api_key:
            try:
                draft = self._generate_with_llm(story, revision_feedback, previous_draft, prefs)
                if not self.is_legacy_draft(draft.title, draft.body):
                    return draft
            except Exception:
                pass

        return self._generate_deterministic(story, revision_feedback, previous_draft, prefs)

    @staticmethod
    def is_legacy_draft(title: str, body: str) -> bool:
        """Detect the pre-grounding template that must never reach a user."""
        content = f"{title}\n{body}"
        return bool(
            re.search(r"shipping\s*:\s*commit\s+[0-9a-f]{7,}", content, re.IGNORECASE)
            or re.search(
                r"commit\s+[0-9a-f]{7,}\s*:\s*commit\s+[0-9a-f]{7,}",
                content,
                re.IGNORECASE,
            )
            or re.search(r"\bcommit\s+[0-9a-f]{7,}\b", content, re.IGNORECASE)
            or "feature or capability needed by users" in content.lower()
            or "implemented commit" in content.lower()
            or bool(re.search(r"modified\s+0\s+files", content, re.IGNORECASE))
        )

    def _generate_with_llm(
        self,
        story: StoryDetectionResult,
        revision_feedback: str | None,
        previous_draft: str | None,
        preferences: EditorialPreferences,
    ) -> LinkedInDraftResult:
        from openai import OpenAI

        client = OpenAI(api_key=self.settings.openai_api_key)
        user_prompt = (
            f"Author Role: {preferences.role_title}\n"
            f"Language: {preferences.language}\n"
            f"Tone: {preferences.tone}\n"
            f"Target Audience: {preferences.target_audience}\n"
            f"Technical Level: {preferences.technical_level}\n"
            f"Post Length: {preferences.post_length}\n"
            f"Allowed Formats: {', '.join(preferences.allowed_formats)}\n"
            f"Avoid Words: {', '.join(preferences.avoid_words)}\n"
            f"Preferred CTA: {preferences.preferred_cta}\n"
            f"Hashtags: {' '.join(preferences.hashtags)}\n\n"
            f"Story Title: {story.title}\n"
            f"Summary: {story.summary}\n"
            f"Problem: {story.problem}\n"
            f"Attempts: {story.attempts}\n"
            f"Solution: {story.solution}\n"
            f"Learning: {story.learning}\n"
            f"Impact: {story.impact}\n"
        )
        if revision_feedback:
            user_prompt += (
                f"\nUser Feedback / Revision Request: {revision_feedback}\n"
                f"Previous Draft:\n{previous_draft or ''}\n"
            )

        response = client.chat.completions.create(
            model=self.settings.openai_model,
            messages=[
                {
                    "role": "system",
                    "content": (
                        f"You are an engineering content creator writing authentic LinkedIn posts in {preferences.language}. "
                        "Rules:\n"
                        "- Evidence before content: never invent benchmarks, numbers, or fake users.\n"
                        f"- Tone: {preferences.tone}. Technical Level: {preferences.technical_level}.\n"
                        f"- Never use these buzzwords: {', '.join(preferences.avoid_words)}.\n"
                        "- Choose the most natural format from the allowed formats: mini_case_study, build_log, before_after, architecture_breakdown, failure_story, or problem_solution.\n"
                        "- The title must describe the technical outcome, never just a SHA or 'Shipping: Commit ...'.\n"
                        "- Use concrete repository evidence; do not invent metrics, users, integrations, or outcomes.\n"
                        "- Return JSON with keys: title, body, format, format_rationale, grounded_claims."
                    ),
                },
                {"role": "user", "content": user_prompt},
            ],
            response_format={"type": "json_object"},
            temperature=0.4,
        )

        content = response.choices[0].message.content or "{}"
        data = json.loads(content)
        return LinkedInDraftResult.model_validate(data)

    def _generate_deterministic(
        self,
        story: StoryDetectionResult,
        revision_feedback: str | None,
        previous_draft: str | None,
        preferences: EditorialPreferences,
    ) -> LinkedInDraftResult:
        is_shorter = (
            preferences.post_length == "concise"
            or (revision_feedback and any(
                w in revision_feedback.lower() for w in ["corto", "short", "resume", "resumen", "menos"]
            ))
        )

        hashtags_str = " ".join(preferences.hashtags) if preferences.hashtags else "#SoftwareEngineering #ProofOfWork"
        format_name = self._select_format(story, preferences)

        cta_str = ""
        if preferences.preferred_cta == "discussion_question":
            cta_str = "¿Cómo manejan este trade-off en sus proyectos?\n\n"
        elif preferences.preferred_cta == "lesson_takeaway":
            cta_str = "📌 Conclusión: Medir siempre antes de optimizar.\n\n"

        if is_shorter:
            short_sections = [
                f"💡 {story.title}",
                story.summary,
                f"El reto: {story.problem or 'resolver una necesidad concreta del producto'}.",
                f"Qué hicimos: {story.solution or 'aplicamos el cambio y lo dejamos listo para validación'}.",
                f"Resultado: {story.impact or 'el cambio quedó incorporado al proyecto'}.",
                f"Aprendizaje: {story.learning or 'la evidencia concreta hace que una historia técnica sea entendible'}.",
            ]
            body = (
                "\n\n".join(short_sections)
                + "\n\n"
                f"{cta_str}"
                f"{hashtags_str}"
            )
            return LinkedInDraftResult(
                title=story.title,
                body=body,
                format=format_name,
                format_rationale=self._format_rationale(format_name),
                grounded_claims=self._grounded_claims(story),
            )

        # Standard draft: each option follows one of the narrative shapes used
        # in the demo examples, while keeping every claim grounded in the story.
        attempts = ""
        if story.attempts:
            attempts = "Cómo llegamos:\n" + "\n".join(
                f"• {attempt}" for attempt in story.attempts[:5]
            ) + "\n\n"
        problem = story.problem or "Resolver una necesidad concreta del producto."
        solution = story.solution or "Aplicamos el cambio y lo dejamos listo para validación."
        impact = story.impact or "El cambio quedó incorporado al proyecto."
        learning = story.learning or "La evidencia concreta hace que una historia técnica sea entendible."

        if format_name == "before_after":
            narrative = (
                f"Antes:\n{problem}\n\n"
                f"La decisión:\n{solution}\n\n"
                f"Después:\n{impact}"
            )
        elif format_name == "architecture_breakdown":
            narrative = (
                f"El cambio de arquitectura:\n{story.summary}\n\n"
                f"Qué estaba fallando:\n{problem}\n\n"
                f"Cómo lo resolvimos:\n{solution}\n\n"
                f"Qué aprendimos:\n{learning}\n\n"
                f"Resultado:\n{impact}"
            )
        elif format_name == "build_log":
            narrative = (
                f"{story.summary}\n\n"
                f"El reto:\n{problem}\n\n"
                f"{attempts}"
                f"La implementación:\n{solution}\n\n"
                f"Qué cambió:\n{impact}\n\n"
                f"Lo que nos llevamos:\n{learning}"
            )
        elif format_name == "failure_story":
            narrative = (
                f"El punto de partida:\n{problem}\n\n"
                f"Lo que intentamos:\n{attempts or solution}\n\n"
                f"La corrección:\n{solution}\n\n"
                f"La lección:\n{learning}\n\n"
                f"Resultado:\n{impact}"
            )
        else:
            narrative = (
                f"{story.summary}\n\n"
                f"El problema:\n{problem}\n\n"
                f"La solución:\n{solution}\n\n"
                f"Qué cambió:\n{impact}\n\n"
                f"Lo que aprendimos:\n{learning}"
            )

        body = f"{story.title}\n\n{narrative}\n\n{cta_str}{hashtags_str}"

        return LinkedInDraftResult(
            title=story.title,
            body=body,
            format=format_name,
            format_rationale=self._format_rationale(format_name),
            grounded_claims=self._grounded_claims(story),
        )

    @staticmethod
    def _select_format(
        story: StoryDetectionResult,
        preferences: EditorialPreferences,
    ) -> ContentFormat:
        candidates: dict[str, ContentFormat] = {
            "architecture_shift": "architecture_breakdown",
            "failure_learning": "failure_story",
            "build_log": "build_log",
            "before_after": "before_after",
        }
        preferred: ContentFormat = candidates.get(story.story_type, "mini_case_study")
        allowed = set(preferences.allowed_formats)
        if preferred in allowed:
            return preferred
        for fallback in ("mini_case_study", "problem_solution", "build_log"):
            if fallback in allowed:
                return cast(ContentFormat, fallback)
        return "problem_solution"


    @staticmethod
    def _format_rationale(format_name: ContentFormat) -> str:
        return {
            "before_after": "El formato Antes / Después hace visible el cambio y su resultado.",
            "build_log": "El build log cuenta el recorrido desde el reto hasta la implementación.",
            "architecture_breakdown": "El desglose de arquitectura explica la decisión y sus consecuencias.",
            "failure_story": "La historia de aprendizaje muestra el problema, la corrección y la lección.",
            "mini_case_study": "El mini caso conecta contexto, decisión, resultado y aprendizaje.",
        }.get(format_name, "El formato Problema / Solución resume el cambio con evidencia concreta.")

    @staticmethod
    def _grounded_claims(story: StoryDetectionResult) -> list[str]:
        return [
            claim
            for claim in (story.summary, story.solution, story.impact)
            if claim and claim.strip()
        ]
