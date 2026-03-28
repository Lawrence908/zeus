# zeus/core/main.py — Zeus Core API bus and health endpoint
import asyncio
import os
import time
from contextlib import asynccontextmanager
from pathlib import Path

import httpx
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from zeus.api.main import router as oracle_router
from zeus.core.admin import init_query_log
from zeus.core.admin import router as admin_router
from zeus.core.chat import router as chat_router
from zeus.core.middleware import QueryLoggingMiddleware
from zeus.core.query import QueryEngine, _run_llm
from zeus.core.sessions import InMemoryStorage, SessionManager
from zeus.core.voice_ws import router as voice_state_router
from zeus.memory.config import get_memory_client
from zeus.orchestration.bus import router as orchestration_router
from zeus.orchestration.hooks import build_default_registry
from zeus.orchestration.runtime import AgentRuntime
from zeus.safety.integration import register_aegis_bus_post_hook
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
    app.state.boot_time = BOOT_TIME
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

    orch_hooks = build_default_registry()
    register_aegis_bus_post_hook(orch_hooks)
    app.state.orchestration_hooks = orch_hooks

    # Observability — query log ring buffer
    init_query_log(app)

    # Scheduled ingest (APScheduler)
    # Sources are empty by default; populate via INGEST_* env vars or CLI.
    # The scheduler still runs on schedule — it just skips if no sources are wired.
    app.state.ingest_scheduler = None
    try:
        from zeus.ingest.pipeline import IngestPipeline
        from zeus.ingest.scheduler import build_scheduler
        from zeus.memory.consolidate import MemoryConsolidator

        ingest_pipeline = IngestPipeline(sources=[])
        consolidator = MemoryConsolidator(app.state.memory)
        scheduler = build_scheduler(ingest_pipeline, consolidator)
        scheduler.start()
        app.state.ingest_scheduler = scheduler
    except Exception as exc:
        import logging
        logging.getLogger("zeus").warning("scheduler not started: %s", exc)

    yield

    ingest_scheduler = getattr(app.state, "ingest_scheduler", None)
    if ingest_scheduler is not None:
        ingest_scheduler.shutdown()

    await app.state.http_client.aclose()


_STATIC_DIR = Path(__file__).resolve().parent / "static"

app = FastAPI(title="Zeus Core", version=ZEUS_VERSION, lifespan=lifespan)
app.add_middleware(QueryLoggingMiddleware)

app.include_router(oracle_router)
app.include_router(admin_router)
app.include_router(chat_router)
app.include_router(voice_state_router)
app.include_router(orchestration_router)

app.mount(
    "/static",
    StaticFiles(directory=str(_STATIC_DIR)),
    name="static",
)


@app.get("/health", include_in_schema=False)
async def health() -> dict[str, str]:
    """Liveness only — for Docker/orchestrator probes. Does not call Qdrant or Ollama."""
    return {"status": "ok"}


@app.get("/status", response_model=StatusResponse)
async def status(request: Request) -> StatusResponse:
    client: httpx.AsyncClient = request.app.state.http_client
    qdrant_url = f"{QDRANT_URL.rstrip('/')}/readyz"
    ollama_url = f"{OLLAMA_URL.rstrip('/')}/api/tags"
    qdrant, ollama = await asyncio.gather(
        check_service(client, "qdrant", qdrant_url),
        check_service(client, "ollama", ollama_url),
    )
    boot = getattr(request.app.state, "boot_time", BOOT_TIME)
    return StatusResponse(
        version=ZEUS_VERSION,
        environment=ZEUS_ENV,
        uptime_seconds=round(time.time() - boot, 1),
        services=[qdrant, ollama],
    )