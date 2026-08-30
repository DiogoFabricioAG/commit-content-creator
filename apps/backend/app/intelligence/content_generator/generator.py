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
    "benchmark_metric",
]

TONE_DESCRIPTIONS: dict[str, str] = {
    "humble_builder": "Humble Builder (transparent about challenges, honest about mistakes, grounded problem-solving without grandiosity)",
    "deep_technical": "Deep Technical (deep engineering focus, data structures, algorithms, architectural trade-offs, systems internals)",
    "direct_minimal": "Direct & Minimalist (concise, high signal-to-noise ratio, bullet points, zero fluff, straight to the solution)",
    "storyteller": "Compelling Storyteller (engaging narrative hook, engineering tension, problem discovery, breakthrough moment, resolution)",
    "pragmatic_lead": "Pragmatic Engineering Lead (focus on maintainability, developer velocity, technical debt, and team trade-offs)",
    "startup_founder": "Technical Founder (speed of shipping, balance of clean architecture with user impact, product engineering)",
}

AUDIENCE_GUIDANCE: dict[str, str] = {
    "senior_engineers": "Target Senior Engineers & Staff Architects: use precise technical vocabulary, trade-offs, and scalability considerations.",
    "tech_founders": "Target CTOs & Technical Founders: highlight engineering velocity, architectural durability, and product impact.",
    "recruiters": "Target Recruiters & Hiring Managers: highlight ownership, engineering craftsmanship, and problem-solving caliber.",
    "junior_developers": "Target Junior Developers & Learners: be pedagogical, clear, and instructive regarding the 'why' behind decisions.",
    "general_tech": "Target General Tech Community: accessible yet rigorous, communicating technical depth clearly.",
}

LANGUAGE_NAMES: dict[str, str] = {
    "es": "Spanish",
    "en": "English",
    "pt": "Portuguese",
}


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

        tone_desc = TONE_DESCRIPTIONS.get(preferences.tone, preferences.tone)
        audience_desc = AUDIENCE_GUIDANCE.get(preferences.target_audience, preferences.target_audience)
        language_name = LANGUAGE_NAMES.get(preferences.language, preferences.language)

        custom_rules_str = ""
        if preferences.custom_rules:
            custom_rules_str = "\nAuthor Custom Style Rules:\n" + "\n".join(
                f"- {rule}" for rule in preferences.custom_rules
            )

        code_instruction = (
            "- Include concise code or configuration snippets if it makes the technical solution concrete."
            if preferences.include_code_snippets
            else "- Focus on conceptual and architectural explanations rather than code blocks."
        )

        metrics_instruction = (
            "- Highlight concrete numbers, diff stats, latency, or throughput if present in story evidence."
            if preferences.include_metrics
            else "- Focus on the qualitative and architectural outcomes."
        )

        user_prompt = (
            f"Author Role: {preferences.role_title}\n"
            f"Language: {language_name} ({preferences.language})\n"
            f"Tone of Voice: {tone_desc}\n"
            f"Target Audience: {audience_desc}\n"
            f"Technical Depth: {preferences.technical_level}\n"
            f"Post Length: {preferences.post_length}\n"
            f"Allowed Formats: {', '.join(preferences.allowed_formats)}\n"
            f"Forbidden Buzzwords: {', '.join(preferences.avoid_words)}\n"
            f"Preferred CTA Mode: {preferences.preferred_cta}\n"
            + (f"Custom CTA Text: {preferences.custom_cta}\n" if preferences.custom_cta else "")
            + f"Hashtags: {' '.join(preferences.hashtags)}\n"
            + f"{custom_rules_str}\n\n"
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
                        f"You are LaborIN's engineering content creator writing authentic LinkedIn posts in {language_name}.\n"
                        "Core Directives:\n"
                        f"- Write every sentence, heading, bullet, call to action, and hashtag context in {language_name}. "
                        "Do not fall back to Spanish or mix languages unless the user explicitly asks for a quoted term.\n"
                        "- Evidence before content: NEVER invent benchmarks, fake metrics, or unverified claims.\n"
                        f"- Tone: {tone_desc}.\n"
                        f"- Audience: {audience_desc}.\n"
                        f"- Technical Depth: {preferences.technical_level}.\n"
                        f"- Forbidden Buzzwords: NEVER use these words or cliches: {', '.join(preferences.avoid_words)}.\n"
                        f"{code_instruction}\n"
                        f"{metrics_instruction}\n"
                        "- Choose the most natural format from the allowed formats: "
                        f"{', '.join(preferences.allowed_formats)}.\n"
                        "- The title must describe the technical outcome clearly (never 'Shipping: Commit ...' or SHA hashes).\n"
                        "- If Preferred CTA is discussion_question, finish with a thought-provoking engineering question.\n"
                        "- If Preferred CTA is custom_cta, incorporate the author's custom CTA text naturally.\n"
                        "- Return JSON with keys: title, body, format, format_rationale, grounded_claims."
                    ),
                },
                {"role": "user", "content": user_prompt},
            ],
            response_format={"type": "json_object"},
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
            or (
                revision_feedback is not None
                and any(
                    w in revision_feedback.lower()
                    for w in ["corto", "short", "resume", "resumen", "menos", "conciso"]
                )
            )
        )

        hashtags_str = (
            " ".join(preferences.hashtags)
            if preferences.hashtags
            else "#SoftwareEngineering #ProofOfWork"
        )
        format_name = self._select_format(story, preferences)

        cta_str = ""
        if preferences.preferred_cta == "custom_cta" and preferences.custom_cta:
            cta_str = f"{preferences.custom_cta.strip()}\n\n"
        elif preferences.preferred_cta == "discussion_question":
            cta_str = "¿Cómo han abordado este trade-off en sus arquitecturas de producción?\n\n"
        elif preferences.preferred_cta == "lesson_takeaway":
            cta_str = "📌 Conclusión técnica: Medir el impacto real y aislar responsabilidades antes de optimizar.\n\n"
        elif preferences.preferred_cta == "github_link":
            cta_str = "🔗 Detalles del commit y pull request en el repositorio.\n\n"

        if is_shorter:
            short_sections = [
                f"💡 {story.title}",
                story.summary,
                f"El reto: {story.problem or 'resolver una necesidad concreta del sistema'}.",
                f"La solución: {story.solution or 'implementamos el cambio con validación estricta'}.",
                f"Impacto: {story.impact or 'el cambio quedó incorporado de forma segura'}.",
                f"Aprendizaje: {story.learning or 'la evidencia técnica hace que cada decisión sea transparente'}.",
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

        # Standard draft according to selected format
        attempts = ""
        if story.attempts:
            attempts = "Camino de iteración:\n" + "\n".join(
                f"• {attempt}" for attempt in story.attempts[:5]
            ) + "\n\n"
        problem = story.problem or "Resolver una necesidad concreta del producto y sistema."
        solution = story.solution or "Aplicamos el cambio y lo dejamos listo para validación y tests."
        impact = story.impact or "El cambio quedó incorporado al proyecto con aislamiento verificado."
        learning = story.learning or "La evidencia concreta hace que una historia técnica sea entendible."

        if format_name == "before_after":
            narrative = (
                f"Antes del cambio:\n{problem}\n\n"
                f"La decisión técnica:\n{solution}\n\n"
                f"Después / Resultado:\n{impact}"
            )
        elif format_name == "architecture_breakdown":
            narrative = (
                f"Desglose de Arquitectura:\n{story.summary}\n\n"
                f"Punto de dolor:\n{problem}\n\n"
                f"Implementación técnica:\n{solution}\n\n"
                f"Aprendizaje clave:\n{learning}\n\n"
                f"Resultado:\n{impact}"
            )
        elif format_name == "build_log":
            narrative = (
                f"Ship Log / Diario de Construcción:\n{story.summary}\n\n"
                f"El reto de partida:\n{problem}\n\n"
                f"{attempts}"
                f"Qué se implementó:\n{solution}\n\n"
                f"Resultado en producción:\n{impact}\n\n"
                f"Lección aprendida:\n{learning}"
            )
        elif format_name == "failure_story":
            narrative = (
                f"El error / Caso de estudio:\n{problem}\n\n"
                f"Lo que se intentó:\n{attempts or solution}\n\n"
                f"La corrección definitiva:\n{solution}\n\n"
                f"La lección aprendida:\n{learning}\n\n"
                f"Impacto:\n{impact}"
            )
        elif format_name == "benchmark_metric":
            narrative = (
                f"Optimización & Métricas:\n{story.summary}\n\n"
                f"Cuello de botella:\n{problem}\n\n"
                f"Solución técnica aplicada:\n{solution}\n\n"
                f"Impacto y rendimiento:\n{impact}\n\n"
                f"Conclusión:\n{learning}"
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
            "performance_optimization": "benchmark_metric",
        }
        preferred: ContentFormat = candidates.get(story.story_type, "mini_case_study")
        allowed = set(preferences.allowed_formats)
        if preferred in allowed:
            return preferred
        for fallback in ("mini_case_study", "problem_solution", "build_log", "before_after"):
            if fallback in allowed:
                return cast(ContentFormat, fallback)
        return "problem_solution"

    @staticmethod
    def _format_rationale(format_name: ContentFormat) -> str:
        return {
            "before_after": "El formato Antes / Después hace visible la transformación y su resultado tangible.",
            "build_log": "El build log cuenta el recorrido cronológico desde el reto hasta la implementación.",
            "architecture_breakdown": "El desglose de arquitectura explica las decisiones de diseño y sus trade-offs.",
            "failure_story": "La historia de aprendizaje muestra el error original, la corrección y la lección técnica.",
            "benchmark_metric": "El formato de métricas destaca la optimización, latencia y rendimiento.",
            "mini_case_study": "El mini caso conecta contexto, decisión de ingeniería, impacto y aprendizaje.",
        }.get(format_name, "El formato Problema / Solución resume el cambio con evidencia concreta.")

    @staticmethod
    def _grounded_claims(story: StoryDetectionResult) -> list[str]:
        return [
            claim
            for claim in (story.summary, story.solution, story.impact)
            if claim and claim.strip()
        ]
