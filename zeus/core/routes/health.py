"""Health check endpoints."""

from fastapi import APIRouter

from zeus.core.config import settings

router = APIRouter()


@router.get("/health")
async def health_check() -> dict:
    return {
        "status": "healthy",
        "service": settings.app_name,
        "version": settings.version,
    }


@router.get("/")
async def root() -> dict:
    return {
        "message": f"Welcome to {settings.app_name}",
        "version": settings.version,
        "docs": "/docs",
    }
