import json

from app.config import Settings
from app.schemas.content import LinkedInDraftResult
from app.schemas.preferences import EditorialPreferences
from app.schemas.story import StoryDetectionResult


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
                return self._generate_with_llm(story, revision_feedback, previous_draft, prefs)
            except Exception:
                pass

        return self._generate_deterministic(story, revision_feedback, previous_draft, prefs)

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
                        "- Format: Problem -> Solution or Before / After.\n"
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
                format="problem_solution",
                format_rationale="Versión compacta y directa ajustada a las preferencias editoriales.",
                grounded_claims=self._grounded_claims(story),
            )

        # Standard draft
        attempts = ""
        if story.attempts:
            attempts = "Cómo llegamos:\n" + "\n".join(
                f"• {attempt}" for attempt in story.attempts[:5]
            ) + "\n\n"
        body = (
            f"🚀 {story.title}\n\n"
            f"{story.summary}\n\n"
            f"El reto:\n{story.problem or 'Resolver una necesidad concreta del producto.'}\n\n"
            f"{attempts}"
            f"Qué hicimos:\n{story.solution or 'Aplicamos el cambio y lo dejamos listo para validación.'}\n\n"
            f"Resultado:\n{story.impact or 'El cambio quedó incorporado al proyecto.'}\n\n"
            f"Aprendizaje clave:\n{story.learning or 'La evidencia concreta hace que una historia técnica sea entendible.'}\n\n"
            f"{cta_str}"
            f"{hashtags_str}"
        )

        return LinkedInDraftResult(
            title=story.title,
            body=body,
            format="problem_solution",
            format_rationale="El formato Problem -> Solution resalta el trade-off técnico y el aprendizaje.",
            grounded_claims=self._grounded_claims(story),
        )

    @staticmethod
    def _grounded_claims(story: StoryDetectionResult) -> list[str]:
        return [
            claim
            for claim in (story.summary, story.solution, story.impact)
            if claim and claim.strip()
        ]
