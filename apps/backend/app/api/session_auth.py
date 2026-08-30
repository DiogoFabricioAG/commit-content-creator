from fastapi import APIRouter, HTTPException, Request, status
from fastapi.responses import JSONResponse

from app.auth.session import SESSION_COOKIE_NAME, SessionError, SessionManager
from app.config import get_settings
from app.integrations.convex_client import ConvexGateway
from app.schemas.auth import SessionLoginRequest

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
        response = JSONResponse({"userId": user_id})
        SessionManager(settings).set_session_cookie(response, user_id)
        return response
    except SessionError as error:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Session signing is not configured",
        ) from error


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
