from app.config import Settings
from app.intelligence.approval_agent.agent import ApprovalAgent


def test_approval_agent_intents() -> None:
    settings = Settings(app_env="test")
    agent = ApprovalAgent(settings)

    # Approve
    assert agent.interpret_message("Ta bueno, publícalo noma").intent == "approve"
    assert agent.interpret_message("Sí, ahora sí").intent == "approve"
    assert agent.interpret_message("publícalo").intent == "approve"
    assert agent.interpret_message("👍").intent == "approve"

    # Revise
    assert agent.interpret_message("Está muy largo, hazlo más corto").intent == "revise"
    assert agent.interpret_message("Quita la segunda parte").intent == "revise"
    assert agent.interpret_message("cambia el inicio").intent == "revise"
    assert agent.interpret_message("Revisar").intent == "revise"

    # Reject
    assert agent.interpret_message("No publiques eso").intent == "reject"
    assert agent.interpret_message("cancela").intent == "reject"

    # Hold
    assert agent.interpret_message("Déjalo para mañana").intent == "hold"

    # Ambiguous -> Clarify (Critical Safety Rule)
    assert agent.interpret_message("mmm no sé").intent == "clarify"
    assert agent.interpret_message("hola qué tal").intent == "clarify"
