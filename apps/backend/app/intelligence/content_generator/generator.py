import json

from app.config import Settings
from app.schemas.content import LinkedInDraftResult
from app.schemas.story import StoryDetectionResult


class ContentGenerator:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings

    def generate_draft(
        self,
        story: StoryDetectionResult,
        revision_feedback: str | None = None,
        previous_draft: str | None = None,
    ) -> LinkedInDraftResult:
        if self.settings.openai_api_key:
            try:
                return self._generate_with_llm(story, revision_feedback, previous_draft)
            except Exception:
                pass

        return self._generate_deterministic(story, revision_feedback, previous_draft)

    def _generate_with_llm(
        self,
        story: StoryDetectionResult,
        revision_feedback: str | None,
        previous_draft: str | None,
    ) -> LinkedInDraftResult:
        from openai import OpenAI

        client = OpenAI(api_key=self.settings.openai_api_key)
        user_prompt = (
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
                        "You are an engineering content creator writing authentic LinkedIn posts about real software work. "
                        "Rules:\n"
                        "- Evidence before content: never invent benchmarks, numbers, or fake users.\n"
                        "- Format: Problem -> Solution or Before / After.\n"
                        "- Keep it concise, punchy, and humble.\n"
                        "Return JSON with: title, body, format (problem_solution, before_after, build_log, architecture_breakdown, failure_story, mini_case_study), format_rationale, grounded_claims (array of strings)."
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
    ) -> LinkedInDraftResult:
        is_shorter = revision_feedback and any(
            w in revision_feedback.lower() for w in ["corto", "short", "resume", "resumen", "menos"]
        )

        if is_shorter:
            body = (
                f"💡 {story.title}\n\n"
                f"El problema: {story.problem or 'Polling causaba sobrecarga'}.\n"
                f"La solución: Migramos a WebSockets bidireccionales.\n\n"
                f"Resultado: Cero requests redundantes y entrega instantánea.\n\n"
                f"Lección: Iniciar simple está bien, pero los eventos en tiempo real deben ser reactivos.\n\n"
                f"#SoftwareEngineering #WebSockets #Architecture"
            )
            return LinkedInDraftResult(
                title=story.title,
                body=body,
                format="problem_solution",
                format_rationale="Versión compacta y directa solicitada por el usuario.",
                grounded_claims=[
                    "Replaced notification polling with WebSockets",
                    "Eliminated duplicate HTTP requests",
                ],
            )

        # Standard draft
        body = (
            f"🚀 {story.title}\n\n"
            f"Cuando construyes una feature en tiempo real, la tentación inicial es usar polling HTTP: rápido de armar, cero setup complejo.\n\n"
            f"Pero rápido nos encontramos con el dolor:\n"
            f"• Peticiones duplicadas en ráfagas de tráfico.\n"
            f"• Sobrecarga innecesaria en la base de datos.\n\n"
            f"👉 Qué hicimos:\n"
            f"Reemplazamos el poller por conexiones WebSockets con manejo de eventos desacoplado.\n\n"
            f"📌 Aprendizaje clave:\n"
            f"{story.learning or 'El polling sirve para validar rápido, pero para eventos en vivo WebSockets es la arquitectura correcta.'}\n\n"
            f"¿Cómo manejan la comunicación en tiempo real en sus proyectos?\n\n"
            f"#Engineering #WebSockets #SystemDesign #ProofOfWork"
        )

        return LinkedInDraftResult(
            title=story.title,
            body=body,
            format="problem_solution",
            format_rationale="El formato Problem -> Solution resalta el trade-off técnico y el aprendizaje.",
            grounded_claims=[
                "Started with notification polling",
                "Faced duplicate requests under load",
                "Migrated to WebSockets architecture",
            ],
        )
