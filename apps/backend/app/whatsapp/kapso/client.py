import logging
from typing import Any

import httpx
from app.config import Settings
from app.schemas.kapso import KapsoOutboundMessage

logger = logging.getLogger(__name__)

MAX_WHATSAPP_TEXT_LENGTH = 4096
MAX_INTERACTIVE_BODY_LENGTH = 1024


class KapsoClient:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self.base_url = "https://api.kapso.ai/meta/whatsapp"

    def send_message(self, to_phone: str, body: str) -> KapsoOutboundMessage:
        # In demo / test mode or when live credentials are incomplete, return a safe simulation.
        if (
            not self.settings.kapso_api_key
            or not self.settings.kapso_phone_number_id
            or self.settings.demo_mode
        ):
            msg_id = f"kapso_sim_{abs(hash(to_phone + body))}"
            return KapsoOutboundMessage(
                to_phone=to_phone,
                body=body,
                message_id=msg_id,
            )

        headers = {
            "X-API-Key": self.settings.kapso_api_key,
            "Content-Type": "application/json",
        }
        payload = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": to_phone,
            "type": "text",
            "text": {"body": body},
        }

        with httpx.Client(timeout=10.0) as client:
            response = client.post(
                f"{self.base_url}/v24.0/{self.settings.kapso_phone_number_id}/messages",
                headers=headers,
                json=payload,
            )
            try:
                response.raise_for_status()
            except httpx.HTTPStatusError:
                logger.exception(
                    "Kapso text message failed: status=%s body=%s",
                    response.status_code,
                    response.text[:1000],
                )
                raise
            data = response.json()
            messages = data.get("messages", [])
            message_id = messages[0].get("id") if messages else data.get("id")
            return KapsoOutboundMessage(
                to_phone=to_phone,
                body=body,
                message_id=message_id,
            )

    def send_interactive_buttons(
        self,
        to_phone: str,
        body: str,
        buttons: list[dict[str, str]],
        image_url: str | None = None,
    ) -> KapsoOutboundMessage:
        """Send reply buttons, optionally with an image header."""
        if not 1 <= len(buttons) <= 3:
            raise ValueError("WhatsApp interactive messages require one to three buttons")
        if not 1 <= len(body) <= MAX_INTERACTIVE_BODY_LENGTH:
            raise ValueError(
                "WhatsApp interactive message bodies require one to 1024 characters"
            )

        normalized_buttons: list[dict[str, Any]] = []
        for button in buttons:
            button_id = button.get("id", "").strip()
            title = button.get("title", "").strip()
            if not button_id or not title:
                raise ValueError("WhatsApp buttons require a non-empty id and title")
            normalized_buttons.append(
                {
                    "type": "reply",
                    "reply": {"id": button_id, "title": title[:20]},
                }
            )

        if (
            not self.settings.kapso_api_key
            or not self.settings.kapso_phone_number_id
            or self.settings.demo_mode
        ):
            msg_id = f"kapso_sim_{abs(hash(to_phone + body + str(normalized_buttons)))}"
            return KapsoOutboundMessage(
                to_phone=to_phone,
                body=body,
                message_id=msg_id,
                message_type="interactive",
            )

        headers = {
            "X-API-Key": self.settings.kapso_api_key,
            "Content-Type": "application/json",
        }
        payload: dict[str, Any] = {
            "messaging_product": "whatsapp",
            "to": to_phone,
            "type": "interactive",
            "interactive": {
                "type": "button",
                "body": {"text": body},
                "action": {"buttons": normalized_buttons},
            },
        }
        if image_url:
            payload["interactive"]["header"] = {
                "type": "image",
                "image": {"link": image_url},
            }

        with httpx.Client(timeout=10.0) as client:
            response = client.post(
                f"{self.base_url}/v24.0/{self.settings.kapso_phone_number_id}/messages",
                headers=headers,
                json=payload,
            )
            try:
                response.raise_for_status()
            except httpx.HTTPStatusError:
                logger.exception(
                    "Kapso interactive message failed: status=%s body=%s",
                    response.status_code,
                    response.text[:1000],
                )
                raise
            data = response.json()
            messages = data.get("messages", [])
            message_id = messages[0].get("id") if messages else data.get("id")
            return KapsoOutboundMessage(
                to_phone=to_phone,
                body=body,
                message_id=message_id,
                message_type="interactive",
            )

    def send_image(
        self,
        to_phone: str,
        image_url: str,
        caption: str = "",
    ) -> KapsoOutboundMessage:
        if (
            not self.settings.kapso_api_key
            or not self.settings.kapso_phone_number_id
            or self.settings.demo_mode
        ):
            msg_id = f"kapso_sim_{abs(hash(to_phone + image_url + caption))}"
            return KapsoOutboundMessage(
                to_phone=to_phone,
                body=caption,
                message_id=msg_id,
                message_type="image",
            )

        headers = {
            "X-API-Key": self.settings.kapso_api_key,
            "Content-Type": "application/json",
        }
        image: dict[str, str] = {"link": image_url}
        if caption:
            image["caption"] = caption
        payload: dict[str, Any] = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": to_phone,
            "type": "image",
            "image": image,
        }

        with httpx.Client(timeout=10.0) as client:
            response = client.post(
                f"{self.base_url}/v24.0/{self.settings.kapso_phone_number_id}/messages",
                headers=headers,
                json=payload,
            )
            try:
                response.raise_for_status()
            except httpx.HTTPStatusError:
                logger.exception(
                    "Kapso image message failed: status=%s body=%s",
                    response.status_code,
                    response.text[:1000],
                )
                raise
            data = response.json()
            messages = data.get("messages", [])
            message_id = messages[0].get("id") if messages else data.get("id")
            return KapsoOutboundMessage(
                to_phone=to_phone,
                body=caption,
                message_id=message_id,
                message_type="image",
            )

    @staticmethod
    def _split_text(body: str, max_length: int) -> list[str]:
        """Split text at readable boundaries without exceeding a provider limit."""
        if not body:
            return [""]

        remaining = body.strip()
        chunks: list[str] = []
        while len(remaining) > max_length:
            boundary = max(
                remaining.rfind("\n\n", 0, max_length + 1),
                remaining.rfind("\n", 0, max_length + 1),
                remaining.rfind(" ", 0, max_length + 1),
            )
            if boundary < max_length // 2:
                boundary = max_length
            chunks.append(remaining[:boundary].rstrip())
            remaining = remaining[boundary:].lstrip()

        if remaining:
            chunks.append(remaining)
        return chunks

    def _send_text_chunks(self, to_phone: str, body: str) -> KapsoOutboundMessage:
        """Send a complete draft as readable text messages within WhatsApp limits."""
        outbound: KapsoOutboundMessage | None = None
        chunks = self._split_text(body, MAX_WHATSAPP_TEXT_LENGTH)
        for chunk in chunks:
            outbound = self.send_message(to_phone, chunk)
        if outbound is None:
            raise RuntimeError("Could not send WhatsApp text chunks")
        return outbound

    def send_draft_for_approval(
        self,
        to_phone: str,
        story_title: str,
        post_body: str,
        version: int = 1,
        image_url: str | None = None,
    ) -> KapsoOutboundMessage:
        if version <= 1:
            header = f'🔥 Encontré una historia para LinkedIn (V1):\n\n"{story_title}"'
        else:
            header = (
                f'🔄 Aquí tienes los cambios propuestos para la V{version}:\n\n'
                f'"{story_title}"'
            )
        draft_message = f"{header}\n\n{post_body}".strip()
        action_message = (
            "✅ Borrador completo enviado arriba.\n\n"
            "¿Qué deseas hacer con esta versión?"
        )
        full_message = (
            f"{draft_message}\n\n"
            "Revisa el borrador y elige una acción. También puedes responder con texto."
        )
        buttons = [
            {"id": "approval_review", "title": "Revisar"},
            {"id": "approval_publish", "title": "Publicar"},
            {"id": "approval_reject", "title": "Descartar"},
        ]
        full_message_sent = False

        if len(full_message) > MAX_INTERACTIVE_BODY_LENGTH:
            logger.info(
                "Draft for %s is %s chars; sending full content before compact buttons",
                to_phone,
                len(full_message),
            )
            try:
                self._send_text_chunks(to_phone, draft_message)
                full_message_sent = True
            except httpx.HTTPStatusError:
                logger.exception("Could not send long WhatsApp draft for %s", to_phone)

        interactive_body = (
            action_message
            if len(full_message) > MAX_INTERACTIVE_BODY_LENGTH
            else full_message
        )
        try:
            return self.send_interactive_buttons(
                to_phone,
                interactive_body,
                buttons,
                image_url=image_url,
            )
        except httpx.HTTPStatusError:
            # An invalid media URL or a provider-side validation issue should
            # not remove the buttons when the compact payload can still work.
            logger.warning(
                "Interactive WhatsApp draft rejected for %s; retrying without media",
                to_phone,
            )
            try:
                return self.send_interactive_buttons(
                    to_phone,
                    interactive_body,
                    buttons,
                )
            except (httpx.HTTPStatusError, ValueError):
                logger.warning("Could not deliver interactive buttons to %s", to_phone)

            if not full_message_sent:
                self._send_text_chunks(to_phone, draft_message)
            return self.send_message(to_phone, action_message)

    def send_published_confirmation(
        self,
        to_phone: str,
        post_urn: str,
    ) -> KapsoOutboundMessage:
        message = (
            f"✅ ¡Publicado con éxito en LinkedIn!\n\n"
            f"ID de publicación: {post_urn}\n"
            f"Tu Proof of Work está en vivo 🚀"
        )
        return self.send_message(to_phone, message)

    def send_clarification(self, to_phone: str) -> KapsoOutboundMessage:
        message = (
            "🤔 No estoy seguro de si deseas publicarlo o hacer cambios.\n\n"
            "Por favor responde:\n"
            "• 'Publicar' para subirlo a LinkedIn\n"
            "• 'Hazlo más corto' o describe los cambios que deseas\n"
            "• 'No' para cancelar"
        )
        return self.send_message(to_phone, message)

    def send_revision_prompt(self, to_phone: str) -> KapsoOutboundMessage:
        message = (
            "✍️ Claro. Dime qué quieres cambiar del borrador y preparo una nueva versión.\n\n"
            "Por ejemplo: hazlo más corto, cambia el inicio o usa un tono más técnico."
        )
        return self.send_message(to_phone, message)
