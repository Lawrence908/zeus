# zeus/core/main.py — Zeus Core API bus and health endpoint
import os
import time
from contextlib import asynccontextmanager
from pathlib import Path

import httpx
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from zeus.api.main import router as oracle_router
from zeus.core.chat import router as chat_router
from zeus.core.query import QueryEngine, _run_llm
from zeus.core.sessions import InMemoryStorage, SessionManager
from zeus.core.voice_ws import router as voice_state_router
from zeus.memory.config import get_memory_client
from zeus.orchestration.bus import router as orchestration_router
from zeus.orchestration.hooks import build_default_registry
from zeus.orchestration.runtime import AgentRuntime
from zeus.voice.state import VoiceStateHub

ZEUS_VERSION = "0.1.0"
BOOT_TIME = time.time()

ZEUS_ENV = os.getenv("ZEUS_ENV", "dev")
QDRANT_URL = os.getenv("QDRANT_URL", "http://localhost:6333")
OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11435")
ZEUS_BUS_URL = os.getenv("ZEUS_CORE_URL", "http://localhost:8000")

_RUFLO_CONFIG = Path(__file__).resolve().parent.parent / "orchestration" / "ruflo.yaml"


class ServiceHealth(BaseModel):
    name: str
    status: str  # "up" | "down" | "unknown"
    latency_ms: float | None = None


class StatusResponse(BaseModel):
    version: str
    environment: str
    uptime_seconds: float
    services: list[ServiceHealth]


async def check_service(client: httpx.AsyncClient, name: str, url: str) -> ServiceHealth:
    try:
        start = time.monotonic()
        resp = await client.get(url, timeout=3.0)
        latency = (time.monotonic() - start) * 1000
        status = "up" if resp.status_code < 400 else "down"
        return ServiceHealth(name=name, status=status, latency_ms=round(latency, 1))
    except Exception:
        return ServiceHealth(name=name, status="down")


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.http_client = httpx.AsyncClient()
    app.state.memory = get_memory_client()
    app.state.voice_hub = VoiceStateHub()
    storage = InMemoryStorage()
    session_manager = SessionManager(storage, llm_fn=_run_llm)
    app.state.session_manager = session_manager
    app.state.query_engine = QueryEngine(
        memory=app.state.memory,
        session_manager=session_manager,
    )

    # Agent runtime — load YAML definitions, start auto_start agents
    app.state.zeus_bus_url = ZEUS_BUS_URL
    runtime = AgentRuntime(_RUFLO_CONFIG)
    runtime.load()
    await runtime.start_all_auto()
    app.state.agent_runtime = runtime
    app.state.hook_registry = build_default_registry()

    yield
    await app.state.http_client.aclose()


app = FastAPI(
    title="Zeus Core",
    version=ZEUS_VERSION,
    lifespan=lifespan,
)
app.include_router(oracle_router)
app.include_router(voice_state_router)
app.include_router(chat_router)
app.include_router(orchestration_router)

_static_dir = Path(__file__).resolve().parent / "static"
if _static_dir.is_dir():
    app.mount("/static", StaticFiles(directory=str(_static_dir)), name="static")


@app.get("/status", response_model=StatusResponse)
async def status():
    """Health check: reports version, uptime, and reachability of all services."""
    client = app.state.http_client

    services = await check_service(client, "qdrant", f"{QDRANT_URL}/healthz")
    ollama = await check_service(client, "ollama", f"{OLLAMA_URL}/api/tags")

    return StatusResponse(
        version=ZEUS_VERSION,
        environment=ZEUS_ENV,
        uptime_seconds=round(time.time() - BOOT_TIME, 1),
        services=[services, ollama],
    )


@app.get("/")
async def root():
    return {
        "name": "zeus",
        "version": ZEUS_VERSION,
        "env": ZEUS_ENV,
        "ui": {
            "chat": "/chat",
            "phaos_viz": "/viz",
            "voice_state_ws": "/ws/voice-state",
        },
    }
