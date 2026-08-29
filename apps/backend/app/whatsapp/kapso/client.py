from typing import Any

import httpx
from app.config import Settings
from app.schemas.kapso import KapsoOutboundMessage


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
            response.raise_for_status()
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
    ) -> KapsoOutboundMessage:
        """Send reply buttons while the user-initiated WhatsApp window is open."""
        if not 1 <= len(buttons) <= 3:
            raise ValueError("WhatsApp interactive messages require one to three buttons")

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
            "recipient_type": "individual",
            "to": to_phone,
            "type": "interactive",
            "interactive": {
                "type": "button",
                "body": {"text": body},
                "action": {"buttons": normalized_buttons},
            },
        }

        with httpx.Client(timeout=10.0) as client:
            response = client.post(
                f"{self.base_url}/v24.0/{self.settings.kapso_phone_number_id}/messages",
                headers=headers,
                json=payload,
            )
            response.raise_for_status()
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
            response.raise_for_status()
            data = response.json()
            messages = data.get("messages", [])
            message_id = messages[0].get("id") if messages else data.get("id")
            return KapsoOutboundMessage(
                to_phone=to_phone,
                body=caption,
                message_id=message_id,
                message_type="image",
            )

    def send_draft_for_approval(
        self,
        to_phone: str,
        story_title: str,
        post_body: str,
        version: int = 1,
        image_url: str | None = None,
    ) -> KapsoOutboundMessage:
        header = f'🔥 Encontré una historia para LinkedIn (V{version}):\n\n"{story_title}"'
        full_message = (
            f"{header}\n\n{post_body}\n\n"
            "Revisa el borrador y elige una acción. También puedes responder con texto."
        )
        if image_url:
            self.send_image(
                to_phone,
                image_url,
                "🖼️ Imagen propuesta para acompañar la publicación.",
            )
        return self.send_interactive_buttons(
            to_phone,
            full_message,
            [
                {"id": "approval_review", "title": "Revisar"},
                {"id": "approval_publish", "title": "Publicar"},
                {"id": "approval_reject", "title": "Descartar"},
            ],
        )

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
