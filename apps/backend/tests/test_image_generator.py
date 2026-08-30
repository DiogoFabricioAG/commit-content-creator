from app.intelligence.media.image_generator import OpenAIImageGenerator
from app.schemas.preferences import EditorialPreferences


def test_image_prompt_honors_user_request_and_requests_readable_text() -> None:
    prompt = OpenAIImageGenerator.build_prompt(
        "Pipeline de publicación",
        "El sistema transforma commits en contenido aprobado.",
        "El usuario valida el borrador por WhatsApp antes de publicarlo.",
        "genera una infografía con texto y adjúntala",
    )

    assert "genera una infografía con texto y adjúntala" in prompt
    assert "All visible text must be written in Spanish" in prompt
    assert "readable text" in prompt
    assert "no readable text" not in prompt


def test_image_prompt_uses_configured_english_language() -> None:
    prompt = OpenAIImageGenerator.build_prompt(
        "Approval flow migration",
        "The agent interprets natural-language requests.",
        "The WhatsApp approval flow now uses the Responses API.",
        "Create an infographic with readable labels.",
        preferences=EditorialPreferences(language="en"),
    )

    assert "All visible text must be written in English" in prompt
    assert "Do not translate the visible text into another language" in prompt
    assert "The configured post length is standard" in prompt
    assert "Spanish" not in prompt
