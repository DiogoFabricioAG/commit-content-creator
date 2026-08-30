import pytest
from app.auth.session import OAUTH_STATE_COOKIE_NAME, SessionError, SessionManager
from app.config import Settings
from starlette.requests import Request


def request_with_cookie(name: str, value: str) -> Request:
    return Request(
        {
            "type": "http",
            "headers": [(b"cookie", f"{name}={value}".encode("ascii"))],
        }
    )


def test_signed_session_round_trip_and_tamper_protection() -> None:
    manager = SessionManager(Settings(app_env="test", session_secret="test-session-secret"))
    token = manager.create_session("user_123")

    assert manager.get_session_user_id(request_with_cookie("laborin_session", token)) == "user_123"

    payload, signature = token.rsplit(".", 1)
    tampered = f"{payload[:-1]}x.{signature}"
    assert manager.get_session_user_id(request_with_cookie("laborin_session", tampered)) is None


def test_oauth_state_is_bound_to_session_and_nonce_cookie() -> None:
    manager = SessionManager(Settings(app_env="test", session_secret="test-session-secret"))
    session_token = manager.create_session("user_123")
    state, nonce = manager.create_oauth_state("user_123", "linkedin")
    request = request_with_cookie("laborin_session", session_token)

    verified = manager.verify_oauth_state(
        state,
        "linkedin",
        nonce,
        request,
    )

    assert verified.user_id == "user_123"
    assert verified.nonce == nonce

    with pytest.raises(SessionError):
        manager.verify_oauth_state(
            state,
            "linkedin",
            "wrong-nonce",
            request,
        )

    with pytest.raises(SessionError):
        manager.verify_oauth_state(
            state,
            "github",
            nonce,
            request,
        )


def test_oauth_state_requires_the_authenticated_session() -> None:
    manager = SessionManager(Settings(app_env="test", session_secret="test-session-secret"))
    state, nonce = manager.create_oauth_state("user_123", "github")
    request = request_with_cookie(OAUTH_STATE_COOKIE_NAME, nonce)

    with pytest.raises(SessionError):
        manager.verify_oauth_state(state, "github", nonce, request)
