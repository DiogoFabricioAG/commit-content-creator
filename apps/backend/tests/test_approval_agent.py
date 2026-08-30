import json
from typing import Any

from app.config import Settings
from app.intelligence.approval_agent.agent import ApprovalAgent


class _FakeResponses:
    def __init__(self, captured: dict[str, Any]) -> None:
        self.captured = captured

    def create(self, **kwargs: Any) -> Any:
        self.captured.update(kwargs)
        tool_call = type(
            "FakeToolCall",
            (),
            {
                "type": "function_call",
                "name": "request_visual_asset",
                "arguments": json.dumps(
                    {
                        "kind": "infographic",
                        "instruction": (
                            "Convierte el cambio en una infografía con texto legible "
                            "y métricas reales del borrador."
                        ),
                        "attach_to_draft": True,
                    }
                ),
            },
        )()
        return type(
            "FakeResponse",
            (),
            {"output": [tool_call], "output_text": ""},
        )()


class _FakeOpenAI:
    def __init__(self, *, api_key: str) -> None:
        del api_key
        captured: dict[str, Any] = {}
        self.responses = _FakeResponses(captured)
        self.captured = captured


def test_agent_uses_gpt_tool_call_for_natural_visual_request(monkeypatch: Any) -> None:
    fake_client: _FakeOpenAI | None = None

    def build_client(*, api_key: str) -> _FakeOpenAI:
        nonlocal fake_client
        fake_client = _FakeOpenAI(api_key=api_key)
        return fake_client

    monkeypatch.setattr("openai.OpenAI", build_client)
    settings = Settings(app_env="test", openai_api_key="test-key")
    agent = ApprovalAgent(settings)

    request = (
        "Quiero que esto se entienda de un vistazo: acompáñalo con una pieza visual "
        "que explique el problema, el cambio y el resultado."
    )
    decision = agent.interpret_message(request)

    assert fake_client is not None
    assert decision.intent == "generate_visual"
    assert decision.visual_request is not None
    assert decision.visual_request.kind == "infographic"
    assert decision.visual_request.instruction == request
    tools = fake_client.captured["tools"]
    assert tools[0]["name"] == "request_visual_asset"
    assert tools[0]["strict"] is True
    assert (
        tools[0]["parameters"]["properties"]["instruction"]["maxLength"]
        == 2000
    )
    assert fake_client.captured["text"] == {"format": {"type": "json_object"}}
    assert fake_client.captured["instructions"]
    assert "json" in fake_client.captured["input"]
    assert "temperature" not in fake_client.captured


def test_agent_does_not_guess_from_keywords_without_gpt() -> None:
    settings = Settings(app_env="test")
    agent = ApprovalAgent(settings)

    decision = agent.interpret_message("haz algo visual con esto")

    assert decision.intent == "clarify"
    assert decision.feedback == "haz algo visual con esto"


def test_revision_feedback_uses_conversation_state_without_keyword_matching() -> None:
    settings = Settings(app_env="test")
    agent = ApprovalAgent(settings)

    decision = agent.interpret_message(
        "Enfatiza el beneficio para el equipo y conserva el tono cercano.",
        awaiting_revision_feedback=True,
    )

    assert decision.intent == "revise"
    assert decision.feedback == "Enfatiza el beneficio para el equipo y conserva el tono cercano."
