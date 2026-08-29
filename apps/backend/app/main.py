from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.github_webhooks import router as github_webhook_router
from app.api.health import router as health_router
from app.api.kapso_webhooks import router as kapso_webhook_router
from app.api.linkedin_oauth import router as linkedin_oauth_router
from app.config import get_settings

settings = get_settings()

app = FastAPI(
    title=settings.app_name,
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)

app.include_router(health_router)
app.include_router(github_webhook_router)
app.include_router(kapso_webhook_router)
app.include_router(linkedin_oauth_router)
