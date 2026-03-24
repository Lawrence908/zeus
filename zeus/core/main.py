"""Zeus Core — FastAPI bus, main router connecting all services."""

from fastapi import FastAPI

from zeus.core.config import settings
from zeus.core.routes import health, services

app = FastAPI(
    title=settings.app_name,
    version=settings.version,
    description="Zeus personal AI — core API bus",
)

app.include_router(health.router, tags=["health"])
app.include_router(services.router, prefix="/services", tags=["services"])
