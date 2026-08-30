from app.intelligence.media.image_generator import OpenAIImageGenerator


def test_image_prompt_honors_user_request_and_requests_readable_text() -> None:
    prompt = OpenAIImageGenerator.build_prompt(
        "Pipeline de publicación",
        "El sistema transforma commits en contenido aprobado.",
        "El usuario valida el borrador por WhatsApp antes de publicarlo.",
        "genera una infografía con texto y adjúntala",
    )

    assert "genera una infografía con texto y adjúntala" in prompt
    assert "readable Spanish text" in prompt
    assert "no readable text" not in prompt
