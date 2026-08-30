import json
import logging
from typing import Any, cast

from app.config import Settings
from app.schemas.approval import ApprovalDecision, VisualRequest

logger = logging.getLogger(__name__)


VISUAL_REQUEST_TOOL: dict[str, Any] = {
    "type": "function",
    "name": "request_visual_asset",
    "description": (
        "Request a visual asset when the user naturally asks for an image, infographic, "
        "architecture diagram, flow diagram, illustration, or to create and attach a visual "
        "to the draft. Understand the meaning of the request; do not require exact keywords. "
        "Preserve the user's complete visual direction in instruction."
    ),
    "strict": True,
    "parameters": {
        "type": "object",
        "properties": {
            "kind": {
                "type": "string",
                "enum": [
                    "image",
                    "infographic",
                    "architecture_diagram",
                    "flow_diagram",
                ],
                "description": "The visual format that best matches the user's request",
            },
            "instruction": {
                "type": "string",
                "description": "The full visual instruction extracted from the user's message",
            },
            "attach_to_draft": {
                "type": "boolean",
                "description": "Whether the generated visual should be attached to the draft",
            },
        },
        "required": ["kind", "instruction", "attach_to_draft"],
        "additionalProperties": False,
    },
}


class ApprovalAgent:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings

    def interpret_message(
        self,
        message: str,
        current_draft: str | None = None,
        awaiting_revision_feedback: bool = False,
    ) -> ApprovalDecision:
        if not self.settings.openai_api_key:
            return self._safe_fallback(message, awaiting_revision_feedback)

        try:
            return self._interpret_with_llm(
                message,
                current_draft,
                awaiting_revision_feedback=awaiting_revision_feedback,
            )
        except Exception as error:
            logger.warning("Approval agent could not interpret WhatsApp message: %s", error)
            return self._safe_fallback(message, awaiting_revision_feedback)

    def _interpret_with_llm(
        self,
        message: str,
        current_draft: str | None,
        *,
        awaiting_revision_feedback: bool,
    ) -> ApprovalDecision:
        from openai import OpenAI

        client = OpenAI(api_key=self.settings.openai_api_key)
        response = client.responses.create(
            model=self.settings.openai_model,
            instructions=(
                "You are LaborIN's natural-language WhatsApp publishing agent. "
                "Understand Spanish conversationally and classify the user's intent "
                "without requiring exact words or keyword commands.\n"
                "Possible intents:\n"
                "- approve: Explicit approval to publish now (e.g. 'publícalo', 'ta bueno dale', 'sí, ahora sí', 'aprobado', 'go').\n"
                "- revise: User requests changes or corrections (e.g. 'está muy largo', 'hazlo más corto', 'quita la segunda parte', 'cambia el inicio').\n"
                "- reject: Explicit decision NOT to publish (e.g. 'no publiques eso', 'cancela', 'no').\n"
                "- hold: Delay or save for later (e.g. 'déjalo para mañana', 'luego lo veo').\n"
                "- clarify: Ambiguous, unclear, questions, or low confidence.\n\n"
                "- generate_visual: The user asks to create, attach, or include a visual asset "
                "such as an image, infographic, architecture diagram, flow diagram, or illustration. "
                "When this applies, call request_visual_asset and preserve the user's complete "
                "visual direction in its instruction.\n\n"
                "If awaiting revision feedback is true, interpret a normal non-empty response "
                "as revision feedback unless the user clearly approves or rejects publication.\n"
                "If intent is ambiguous or not 100% clear approval, NEVER classify as approve. "
                "When no tool is needed, output JSON with keys: intent, feedback (string or null), "
                "confidence (0.0 to 1.0), reasoning."
            ),
            input=(
                f"User WhatsApp message: {message}\n"
                f"Current Draft:\n{current_draft or ''}\n"
                f"Awaiting revision feedback: {str(awaiting_revision_feedback).lower()}\n"
                "If no tool is needed, return the classification as json."
            ),
            tools=cast(Any, [VISUAL_REQUEST_TOOL]),
            tool_choice="auto",
            parallel_tool_calls=False,
            text={"format": {"type": "json_object"}},
        )

        for raw_output_item in response.output:
            tool_call = cast(Any, raw_output_item)
            if (
                getattr(tool_call, "type", None) != "function_call"
                or getattr(tool_call, "name", None) != "request_visual_asset"
            ):
                continue
            tool_arguments = json.loads(tool_call.arguments)
            visual_request = VisualRequest.model_validate(tool_arguments)
            return ApprovalDecision(
                intent="generate_visual",
                confidence=0.98,
                reasoning="GPT interpretó que el usuario pidió un recurso visual.",
                visual_request=visual_request,
            )

        content = response.output_text or "{}"
        data = json.loads(content)
        return ApprovalDecision.model_validate(data)

    @staticmethod
    def _safe_fallback(
        message: str,
        awaiting_revision_feedback: bool,
    ) -> ApprovalDecision:
        if awaiting_revision_feedback and message.strip():
            return ApprovalDecision(
                intent="revise",
                feedback=message,
                confidence=0.7,
                reasoning="Se tomó el mensaje como feedback del borrador pendiente de revisión.",
            )
        return ApprovalDecision(
            intent="clarify",
            feedback=message,
            confidence=0.0,
            reasoning="El agente de IA no está disponible; no se adivinó una acción por palabras clave.",
        )
