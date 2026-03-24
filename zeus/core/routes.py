from fastapi import APIRouter

from zeus import __version__
from zeus.core.config import settings

router = APIRouter()


@router.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok", "version": __version__}


@router.get("/")
async def root() -> dict[str, str]:
    return {
        "name": settings.app_name,
        "version": __version__,
        "description": "Personal AI for RAG and agent orchestration",
    }


@router.get("/services")
async def services() -> dict[str, list[dict[str, str]]]:
    """List all registered Zeus subsystems and their status."""
    subsystems = [
        {"name": "mnemosyne", "description": "Memory layer (mem0 + Qdrant)", "status": "planned"},
        {"name": "hermes", "description": "Ingest pipeline", "status": "planned"},
        {"name": "apollo", "description": "Voice interface (STT + TTS)", "status": "planned"},
        {"name": "aegis", "description": "Safety layer (NemoClaw + OpenShell)", "status": "planned"},
        {"name": "olympians", "description": "Agent swarm orchestration", "status": "planned"},
        {"name": "oracle", "description": "Zeus Context API", "status": "planned"},
    ]
    return {"services": subsystems}
