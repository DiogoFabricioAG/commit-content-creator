import logging
import secrets

from fastapi import APIRouter, HTTPException, Request, status
from fastapi.responses import JSONResponse

from app.auth.session import (
    SESSION_COOKIE_NAME,
    SessionError,
    SessionManager,
)
from app.config import get_settings
from app.integrations.convex_client import ConvexGateway
from app.schemas.auth import SessionLoginRequest, SessionVerificationRequest
from app.whatsapp.kapso.client import KapsoClient

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/auth/session", tags=["session"])


@router.post("/login")
async def session_login(payload: SessionLoginRequest) -> JSONResponse:
    settings = get_settings()
    convex = ConvexGateway(settings)
    if not convex.is_configured:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="CONVEX_URL is required to create a session",
        )

    phone = payload.phone.strip()
    if not phone:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="A WhatsApp phone number is required",
        )

    try:
        user_id = convex.get_or_create_default_user(
            whatsapp_phone=phone,
            display_name=payload.display_name.strip() if payload.display_name else None,
        )
        if not convex.is_whatsapp_window_open(phone):
            return JSONResponse(
                {
                    "verificationRequired": False,
                    "code": "whatsapp_window_closed",
                    "detail": (
                        "Primero envía un mensaje al bot de WhatsApp y luego vuelve a solicitar el código."
                    ),
                },
                status_code=status.HTTP_409_CONFLICT,
            )

        verification_code = f"{secrets.randbelow(1_000_000):06d}"
        sessions = SessionManager(settings)
        challenge_token = sessions.create_phone_challenge(
            user_id=user_id,
            phone=phone,
            code=verification_code,
        )
        KapsoClient(settings).send_message(
            phone,
            (
                "🔐 LaborIN: tu código de verificación es "
                f"{verification_code}. Vence en 10 minutos."
            ),
        )
        response = JSONResponse(
            {
                "verificationRequired": True,
                "message": "Te enviamos un código por WhatsApp.",
                "expiresIn": 600,
            },
            status_code=status.HTTP_202_ACCEPTED,
        )
        sessions.set_phone_challenge_cookie(response, challenge_token)
        return response
    except SessionError as error:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Session signing is not configured",
        ) from error
    except Exception as error:
        logger.exception("Could not send phone verification code")
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="No se pudo enviar el código por WhatsApp. Intenta nuevamente.",
        ) from error


@router.post("/verify")
async def session_verify(
    payload: SessionVerificationRequest,
    request: Request,
) -> JSONResponse:
    settings = get_settings()
    sessions = SessionManager(settings)
    try:
        challenge = sessions.verify_phone_challenge(request, payload.code)
    except SessionError as error:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="El código de WhatsApp es inválido o ya expiró",
        ) from error

    convex = ConvexGateway(settings)
    if not convex.is_configured:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="CONVEX_URL is required to create a session",
        )
    if not convex.get_user_by_id(challenge.user_id):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="The session user no longer exists",
        )

    response = JSONResponse({"userId": challenge.user_id})
    sessions.set_session_cookie(response, challenge.user_id)
    sessions.clear_phone_challenge_cookie(response)
    return response


@router.get("/me")
async def session_me(request: Request) -> JSONResponse:
    settings = get_settings()
    sessions = SessionManager(settings)
    user_id = sessions.get_session_user_id(request)
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="A valid LaborIN session is required",
        )

    convex = ConvexGateway(settings)
    if not convex.is_configured:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="CONVEX_URL is required to resolve a session",
        )
    user = convex.get_user_by_id(user_id)
    if not user:
        response = JSONResponse(
            {"detail": "The session user no longer exists"},
            status_code=status.HTTP_401_UNAUTHORIZED,
        )
        response.delete_cookie(key=SESSION_COOKIE_NAME, path="/")
        return response
    return JSONResponse({"userId": user_id, "user": user})


@router.post("/logout")
async def session_logout() -> JSONResponse:
    response = JSONResponse({"status": "signed_out"})
    response.delete_cookie(key=SESSION_COOKIE_NAME, path="/")
    return response
