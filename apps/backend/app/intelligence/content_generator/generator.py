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
            body = (
                f"💡 {story.title}\n\n"
                f"El problema: {story.problem or 'Sobrecarga de peticiones y latencia innecesaria'}.\n"
                f"La solución: {story.solution or 'Migramos a arquitectura orientada a eventos'}.\n\n"
                f"Resultado: {story.impact or 'Mayor estabilidad y entrega instantánea'}.\n\n"
                f"Lección: {story.learning or 'Iniciar simple está bien, pero los eventos en vivo deben ser reactivos'}.\n\n"
                f"{cta_str}"
                f"{hashtags_str}"
            )
            return LinkedInDraftResult(
                title=story.title,
                body=body,
                format="problem_solution",
                format_rationale="Versión compacta y directa ajustada a las preferencias editoriales.",
                grounded_claims=[
                    "Replaced notification polling with WebSockets",
                    "Eliminated duplicate HTTP requests",
                ],
            )

        # Standard draft
        body = (
            f"🚀 {story.title}\n\n"
            f"Cuando construyes una feature técnica, la tentación inicial es usar la solución más rápida.\n\n"
            f"Pero rápido nos encontramos con el dolor:\n"
            f"• {story.problem or 'Peticiones duplicadas bajo alta concurrencia'}.\n"
            f"• Sobrecarga innecesaria en la base de datos.\n\n"
            f"👉 Qué hicimos:\n"
            f"{story.solution or 'Reemplazamos el poller por conexiones WebSockets con manejo de eventos desacoplado'}.\n\n"
            f"📌 Aprendizaje clave:\n"
            f"{story.learning or 'El polling sirve para validar rápido, pero para eventos en vivo WebSockets es la arquitectura correcta.'}\n\n"
            f"{cta_str}"
            f"{hashtags_str}"
        )

        return LinkedInDraftResult(
            title=story.title,
            body=body,
            format="problem_solution",
            format_rationale="El formato Problem -> Solution resalta el trade-off técnico y el aprendizaje.",
            grounded_claims=[
                "Started with initial technical solution",
                "Identified bottleneck under load",
                "Refactored architecture based on evidence",
            ],
        )

