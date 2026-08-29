from fastapi import APIRouter, Depends

from app.config import Settings, get_settings
from app.schemas.health import HealthResponse

router = APIRouter(tags=["health"])


@router.get("/health", response_model=HealthResponse)
def health(settings: Settings = Depends(get_settings)) -> HealthResponse:  # noqa: B008
    return HealthResponse(
        service=settings.app_name,
        environment=settings.app_env,
        convex_configured=bool(settings.convex_url),
    )
