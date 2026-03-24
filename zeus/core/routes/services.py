"""Service registry and status endpoints."""

from fastapi import APIRouter

router = APIRouter()

SERVICE_REGISTRY: dict[str, dict] = {
    "mnemosyne": {"name": "Memory Layer", "status": "planned"},
    "hermes": {"name": "Ingest Pipeline", "status": "planned"},
    "apollo": {"name": "Voice Interface", "status": "planned"},
    "aegis": {"name": "Safety Layer", "status": "planned"},
    "oracle": {"name": "Zeus Context API", "status": "planned"},
    "olympians": {"name": "Agent Swarm", "status": "planned"},
}


@router.get("/")
async def list_services() -> dict:
    return {"services": SERVICE_REGISTRY}


@router.get("/{service_name}")
async def get_service(service_name: str) -> dict:
    if service_name in SERVICE_REGISTRY:
        return {"name": service_name, **SERVICE_REGISTRY[service_name]}
    return {"error": f"Unknown service: {service_name}"}
