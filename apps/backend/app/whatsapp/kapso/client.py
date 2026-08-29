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

    def send_draft_for_approval(
        self,
        to_phone: str,
        story_title: str,
        post_body: str,
        version: int = 1,
    ) -> KapsoOutboundMessage:
        header = f'🔥 Encontré una historia para LinkedIn (V{version}):\n\n"{story_title}"'
        options = (
            "¿Qué hacemos con esto?\n\n"
            "Puedes responder naturalmente:\n"
            "• publícalo\n"
            "• no\n"
            "• hazlo más corto\n"
            "• cambia el inicio\n"
            "• déjalo para después"
        )
        full_message = f"{header}\n\n{post_body}\n\n{options}"
        return self.send_message(to_phone, full_message)

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
