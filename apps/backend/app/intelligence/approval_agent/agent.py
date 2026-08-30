import json
import re

from app.config import Settings
from app.schemas.approval import ApprovalDecision


class ApprovalAgent:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings

    def interpret_message(
        self,
        message: str,
        current_draft: str | None = None,
    ) -> ApprovalDecision:
        if self.settings.openai_api_key:
            try:
                return self._interpret_with_llm(message, current_draft)
            except Exception:
                pass

        return self._interpret_heuristic(message)

    def _interpret_with_llm(
        self,
        message: str,
        current_draft: str | None,
    ) -> ApprovalDecision:
        from openai import OpenAI

        client = OpenAI(api_key=self.settings.openai_api_key)
        response = client.chat.completions.create(
            model=self.settings.openai_model,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are an Approval Intent Classifier for a WhatsApp publishing assistant. "
                        "Classify user responses regarding a LinkedIn post draft.\n"
                        "Possible intents:\n"
                        "- approve: Explicit approval to publish now (e.g. 'publícalo', 'ta bueno dale', 'sí, ahora sí', 'aprobado', 'go').\n"
                        "- revise: User requests changes or corrections (e.g. 'está muy largo', 'hazlo más corto', 'quita la segunda parte', 'cambia el inicio').\n"
                        "- reject: Explicit decision NOT to publish (e.g. 'no publiques eso', 'cancela', 'no').\n"
                        "- hold: Delay or save for later (e.g. 'déjalo para mañana', 'luego lo veo').\n"
                        "- clarify: Ambiguous, unclear, questions, or low confidence.\n\n"
                        "CRITICAL RULE: If intent is ambiguous or not 100% clear approval, NEVER classify as approve. Output JSON with keys: intent, feedback (string or null), confidence (0.0 to 1.0), reasoning."
                    ),
                },
                {
                    "role": "user",
                    "content": f"User WhatsApp message: {message}\nCurrent Draft:\n{current_draft or ''}",
                },
            ],
            response_format={"type": "json_object"},
            temperature=0.0,
        )

        content = response.choices[0].message.content or "{}"
        data = json.loads(content)
        return ApprovalDecision.model_validate(data)

    def _interpret_heuristic(self, message: str) -> ApprovalDecision:
        clean = message.strip().lower()

        # Approval patterns (explicit approval)
        approve_patterns = [
            r"\b(ta\s+bueno|publ[ií]calo|publicalo|publica|dale|aprobado|aprobada|adelante|go|s[ií],?\s+ahora\s+s[ií]|lito|listo|de\s+una|m[aá]ndalo)\b",
            r"^(s[ií]|si|ok|yes|👍|🚀|✅)$",
        ]

        # Revision patterns
        revise_patterns = [
            r"\b(revisar?|review|corto|largo|resume|resumen|cambia|quita|agrega|modifica|mejora|segundo\s+p[aá]rrafo|inicio|final|tono|m[aá]s\s+t[eé]cnico|corporativo)\b",
            r"\b(hazlo|hazla|ponle|s[aá]cale)\b",
        ]

        # Rejection patterns
        reject_patterns = [
            r"\b(no\s+publiques|no\s+lo\s+publiques|cancela|cancelar|rechazado|no\s+quiero|b[oó]rralo|desc[aá]rtalo)\b",
            r"^no$",
        ]

        # Hold / Defer patterns
        hold_patterns = [
            r"\b(ma[ñn]ana|despu[eé]s|luego|m[aá]s\s+tarde|pausa|espera|gu[aá]rdalo)\b",
        ]

        # 1. Check Rejection first
        if any(re.search(p, clean) for p in reject_patterns):
            return ApprovalDecision(
                intent="reject",
                feedback=message,
                confidence=0.95,
                reasoning="Usuario rechazó explícitamente la publicación.",
            )

        # 2. Check Revision
        if any(re.search(p, clean) for p in revise_patterns):
            return ApprovalDecision(
                intent="revise",
                feedback=message,
                confidence=0.92,
                reasoning="Usuario solicitó cambios o ajustes al borrador.",
            )

        # 3. Check Hold
        if any(re.search(p, clean) for p in hold_patterns):
            return ApprovalDecision(
                intent="hold",
                feedback=message,
                confidence=0.90,
                reasoning="Usuario solicitó pausar o revisar más tarde.",
            )

        # 4. Check Explicit Approval
        if any(re.search(p, clean) for p in approve_patterns):
            return ApprovalDecision(
                intent="approve",
                confidence=0.95,
                reasoning="Usuario aprobó explícitamente la publicación.",
            )

        # 5. Fallback to Clarify (Safe: Never publish on ambiguous input)
        return ApprovalDecision(
            intent="clarify",
            feedback=message,
            confidence=0.5,
            reasoning="Respuesta ambigua o no reconocida; se requiere aclaración.",
        )
