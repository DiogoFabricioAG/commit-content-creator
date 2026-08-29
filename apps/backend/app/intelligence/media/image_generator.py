import base64
from dataclasses import dataclass

from app.config import Settings


class ImageGenerationUnavailable(RuntimeError):
    """Raised when the image provider is not configured or returns no image."""


@dataclass(frozen=True)
class GeneratedImage:
    data: bytes
    mime_type: str
    prompt: str


class OpenAIImageGenerator:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings

    def generate_for_story(
        self,
        *,
        story_title: str,
        story_summary: str,
        post_body: str,
    ) -> GeneratedImage:
        if not self.settings.openai_api_key:
            raise ImageGenerationUnavailable("OPENAI_API_KEY is required for image generation")

        from openai import OpenAI

        prompt = self._build_prompt(story_title, story_summary, post_body)
        client = OpenAI(api_key=self.settings.openai_api_key)
        result = client.images.generate(
            model=self.settings.openai_image_model,
            prompt=prompt,
            size=self.settings.openai_image_size,
            quality=self.settings.openai_image_quality,
        )

        if not result.data or not result.data[0].b64_json:
            raise ImageGenerationUnavailable("OpenAI returned no image data")

        try:
            image_bytes = base64.b64decode(result.data[0].b64_json, validate=True)
        except (ValueError, TypeError) as error:
            raise ImageGenerationUnavailable("OpenAI returned invalid Base64 image data") from error

        if not image_bytes:
            raise ImageGenerationUnavailable("OpenAI returned an empty image")

        return GeneratedImage(data=image_bytes, mime_type="image/png", prompt=prompt)

    @staticmethod
    def _build_prompt(story_title: str, story_summary: str, post_body: str) -> str:
        return (
            "Create a clean editorial illustration for a software engineering LinkedIn post. "
            "Use an abstract visual metaphor for the technical change, with a modern blue and "
            "violet palette, strong contrast, no logos, no readable text, no code screenshots, "
            "and no invented product UI. Keep it professional and suitable for a 1536x1024 feed image.\n\n"
            f"Story: {story_title}\n"
            f"Summary: {story_summary}\n"
            f"Post context: {post_body[:1200]}"
        )
