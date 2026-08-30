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
        user_request: str = "",
        visual_kind: str = "image",
    ) -> GeneratedImage:
        if not self.settings.openai_api_key:
            raise ImageGenerationUnavailable("OPENAI_API_KEY is required for image generation")

        from openai import OpenAI

        prompt = self.build_prompt(
            story_title,
            story_summary,
            post_body,
            user_request,
            visual_kind,
        )
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
    def build_prompt(
        story_title: str,
        story_summary: str,
        post_body: str,
        user_request: str = "",
        visual_kind: str = "image",
    ) -> str:
        requested_format = user_request.strip()[:2000] or "Create a visual summary of the story."
        format_label = visual_kind.replace("_", " ")
        return (
            f"Create a polished {format_label} in Spanish for a software engineering LinkedIn post, "
            "not a generic decorative illustration. Follow the user's visual request exactly. "
            "Include a concise, legible title, 3 to 5 information blocks, short labels, "
            "and a clear visual hierarchy. Use readable Spanish text taken from the story and "
            "show the problem, technical change, impact, and learning when those facts are available. "
            "If the request asks for architecture, show labeled nodes and arrows. If it asks for a "
            "flow, show the stages in order. Do not invent metrics, logos, products, or facts that are "
            "not present in the story. Use a modern blue and violet palette, strong contrast, and a "
            "professional 1536x1024 LinkedIn-feed composition.\n\n"
            f"User's visual request (follow this): {requested_format}\n\n"
            f"Story: {story_title}\n"
            f"Summary: {story_summary}\n"
            f"Post context: {post_body[:1200]}"
        )
