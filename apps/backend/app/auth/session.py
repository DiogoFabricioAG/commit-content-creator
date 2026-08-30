import base64
import hashlib
import hmac
import json
import secrets
import time
from dataclasses import dataclass
from typing import Any, cast

from fastapi import Request

from app.config import Settings

SESSION_COOKIE_NAME = "laborin_session"
OAUTH_STATE_COOKIE_NAME = "laborin_oauth_state"
SESSION_TTL_SECONDS = 60 * 60 * 24 * 7
OAUTH_STATE_TTL_SECONDS = 60 * 10


class SessionError(ValueError):
    """Raised when a signed session or OAuth state cannot be trusted."""


@dataclass(frozen=True)
class OAuthState:
    user_id: str
    nonce: str


class SessionManager:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings

    def create_session(self, user_id: str) -> str:
        now = int(time.time())
        return self._sign(
            {
                "typ": "session",
                "sub": user_id,
                "iat": now,
                "exp": now + SESSION_TTL_SECONDS,
            }
        )

    def get_session_user_id(self, request: Request) -> str | None:
        token = request.cookies.get(SESSION_COOKIE_NAME)
        if not token:
            return None
        try:
            payload = self._verify(token, expected_type="session")
        except SessionError:
            return None
        subject = payload.get("sub")
        return str(subject) if isinstance(subject, str) and subject.strip() else None

    def require_session_user_id(self, request: Request) -> str:
        user_id = self.get_session_user_id(request)
        if not user_id:
            raise SessionError("A valid LaborIN session is required")
        return user_id

    def create_oauth_state(self, user_id: str, provider: str) -> tuple[str, str]:
        now = int(time.time())
        nonce = secrets.token_urlsafe(24)
        return (
            self._sign(
                {
                    "typ": "oauth_state",
                    "sub": user_id,
                    "provider": provider,
                    "nonce": nonce,
                    "iat": now,
                    "exp": now + OAUTH_STATE_TTL_SECONDS,
                }
            ),
            nonce,
        )

    def verify_oauth_state(
        self,
        state: str,
        provider: str,
        expected_nonce: str | None,
        request: Request,
    ) -> OAuthState:
        payload = self._verify(state, expected_type="oauth_state")
        if payload.get("provider") != provider:
            raise SessionError("OAuth state provider mismatch")

        nonce = payload.get("nonce")
        if not isinstance(nonce, str) or not expected_nonce or not hmac.compare_digest(
            nonce, expected_nonce
        ):
            raise SessionError("OAuth state nonce mismatch")

        session_user_id = self.require_session_user_id(request)
        subject = payload.get("sub")
        if not isinstance(subject, str) or not subject.strip():
            raise SessionError("OAuth state has no user")
        if not hmac.compare_digest(subject, session_user_id):
            raise SessionError("OAuth state user mismatch")

        return OAuthState(user_id=subject, nonce=nonce)

    def set_session_cookie(self, response: Any, user_id: str) -> None:
        response.set_cookie(
            key=SESSION_COOKIE_NAME,
            value=self.create_session(user_id),
            max_age=SESSION_TTL_SECONDS,
            httponly=True,
            secure=self._is_secure,
            samesite="lax",
            path="/",
        )

    def set_oauth_state_cookie(self, response: Any, nonce: str) -> None:
        response.set_cookie(
            key=OAUTH_STATE_COOKIE_NAME,
            value=nonce,
            max_age=OAUTH_STATE_TTL_SECONDS,
            httponly=True,
            secure=self._is_secure,
            samesite="lax",
            path="/",
        )

    @staticmethod
    def clear_oauth_state_cookie(response: Any) -> None:
        response.delete_cookie(key=OAUTH_STATE_COOKIE_NAME, path="/")

    @property
    def _is_secure(self) -> bool:
        return self.settings.app_env == "production"

    def _sign(self, payload: dict[str, Any]) -> str:
        encoded_payload = self._encode(json.dumps(payload, separators=(",", ":")))
        signature = hmac.new(
            self._secret,
            encoded_payload.encode("ascii"),
            hashlib.sha256,
        ).digest()
        return f"{encoded_payload}.{self._encode(signature)}"

    def _verify(self, token: str, *, expected_type: str) -> dict[str, Any]:
        encoded_payload, separator, encoded_signature = token.partition(".")
        if not separator or not encoded_payload or not encoded_signature:
            raise SessionError("Malformed signed token")

        expected_signature = hmac.new(
            self._secret,
            encoded_payload.encode("ascii"),
            hashlib.sha256,
        ).digest()
        try:
            received_signature = self._decode(encoded_signature)
        except ValueError as error:
            raise SessionError("Malformed token signature") from error
        if not hmac.compare_digest(expected_signature, received_signature):
            raise SessionError("Invalid token signature")

        try:
            raw_payload = json.loads(self._decode(encoded_payload).decode("utf-8"))
        except (ValueError, UnicodeDecodeError, json.JSONDecodeError) as error:
            raise SessionError("Malformed token payload") from error
        if not isinstance(raw_payload, dict):
            raise SessionError("Malformed token payload")
        payload = cast(dict[str, Any], raw_payload)
        if payload.get("typ") != expected_type:
            raise SessionError("Invalid token type")
        expiration = payload.get("exp")
        if not isinstance(expiration, int) or expiration <= int(time.time()):
            raise SessionError("Expired token")
        return payload

    @property
    def _secret(self) -> bytes:
        raw_secret = self.settings.session_secret or self.settings.token_encryption_key
        if not raw_secret:
            raise SessionError("SESSION_SECRET or TOKEN_ENCRYPTION_KEY is required")
        return hashlib.sha256(raw_secret.encode("utf-8")).digest()

    @staticmethod
    def _encode(value: str | bytes) -> str:
        raw = value.encode("utf-8") if isinstance(value, str) else value
        return base64.urlsafe_b64encode(raw).decode("ascii").rstrip("=")

    @staticmethod
    def _decode(value: str) -> bytes:
        return base64.urlsafe_b64decode(value + ("=" * (-len(value) % 4)))
