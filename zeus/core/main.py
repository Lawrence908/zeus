# zeus/core/main.py — Zeus Core API bus and health endpoint
import asyncio
import os
import time
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Any

import httpx
from fastapi import FastAPI, Request
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from zeus.api.main import router as oracle_router
from zeus.bench.runner import BenchmarkRunner, load_results, save_results
from zeus.core.admin import init_query_log
from zeus.core.admin import router as admin_router
from zeus.core.chat import router as chat_router
from zeus.core.middleware import QueryLoggingMiddleware
from zeus.core.newsletter import router as newsletter_router
from zeus.core.query import QueryEngine, _run_llm, _active_model_name, _chat_use_claude, _ollama_model, set_ollama_model
from zeus.core.actions import router as actions_router
from zeus.core.calendar import router as calendar_router
from zeus.core.epstein_router import router as epstein_router  # private branch only; never merge to main
from zeus.core.inbox import router as inbox_router
from zeus.core.mesh import router as mesh_router
from zeus.core.vault import router as vault_router
from zeus.core.runtime_settings import RuntimeSettings
from zeus.core.session_storage import SQLiteSessionStorage
from zeus.core.sessions import InMemoryStorage, SessionManager
from zeus.core.voice_ws import router as voice_state_router
from zeus.core.zeus_os import router as zeus_os_router
from zeus.integrations.telegram import build_telegram_bot
from zeus.memory.store import get_memory_store
from zeus.kronos.api import router as kronos_router
from zeus.orchestration.bus import router as orchestration_router
from zeus.orchestration.hooks import build_default_registry, bus_metrics
from zeus.orchestration.runtime import AgentRuntime
from zeus.safety.integration import register_aegis_bus_pre_hook, register_aegis_bus_post_hook
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
    app.state.memory_store = get_memory_store()
    # Legacy alias: a few old call sites still reference app.state.memory.
    # Pointing it at the MemoryStore keeps those working until they're updated;
    # real mem0 semantics (.search/.add/.update/.delete) are provided by the
    # MemoryStore class directly.
    app.state.memory = app.state.memory_store
    app.state.voice_hub = VoiceStateHub()
    session_backend = os.getenv("ZEUS_SESSION_BACKEND", "memory").lower()
    if session_backend == "sqlite":
        db_path = os.getenv("ZEUS_SESSION_DB_PATH", "zeus/data/sessions.db")
        os.makedirs(os.path.dirname(db_path) or ".", exist_ok=True)
        storage = SQLiteSessionStorage(db_path)
    else:
        storage = InMemoryStorage()
    session_manager = SessionManager(storage, llm_fn=_run_llm)
    app.state.session_manager = session_manager
    app.state.query_engine = QueryEngine(session_manager=session_manager)

    # Agent runtime — load YAML definitions, start auto_start agents
    app.state.zeus_bus_url = ZEUS_BUS_URL
    runtime = AgentRuntime(_RUFLO_CONFIG)
    runtime.load()
    await runtime.start_all_auto()
    app.state.agent_runtime = runtime

    orch_hooks = build_default_registry()
    register_aegis_bus_pre_hook(orch_hooks)
    register_aegis_bus_post_hook(orch_hooks)
    app.state.orchestration_hooks = orch_hooks
    app.state.bus_metrics = bus_metrics

    # Chat-path tool loop (Zeus 10). Tools register into a process-local
    # registry; QueryEngine.query() consults it when ZEUS_TOOLS_ENABLED=1.
    from zeus.core.tools import registry as tool_registry
    from zeus.core.tools.current_time import register as _register_current_time
    from zeus.core.tools.file_read import register as _register_file_read
    from zeus.core.tools.file_search import register as _register_file_search
    from zeus.core.tools.action_run import register as _register_action_pack
    from zeus.core.tools.calendar_today import register as _register_calendar_today
    from zeus.core.tools.inbox_append import register as _register_inbox_append
    from zeus.core.tools.newsletter_latest import register as _register_newsletter_latest
    from zeus.core.tools.server_health import register as _register_server_health
    from zeus.core.tools.status_read import register as _register_status_read
    from zeus.core.tools.web_search import register_if_configured as _register_web_search
    from zeus.core.tools.deep_research import register as _register_deep_research
    from zeus.core.tools.news_search import register as _register_news_search
    from zeus.core.tools.epstein import register as _register_epstein

    _register_current_time()
    _register_web_search()
    _register_status_read()
    _register_server_health()
    _register_file_read()
    _register_file_search()
    _register_inbox_append()
    _register_action_pack()
    _register_calendar_today()
    _register_newsletter_latest()
    _register_deep_research()
    _register_news_search()
    _register_epstein()
    app.state.tools_registered = [spec.name for spec in tool_registry.list_specs()]

    # Observability — query log ring buffer
    init_query_log(app)

    # Runtime settings (LAB-322) — JSON-backed overrides for env config.
    app.state.runtime_settings = RuntimeSettings()

    # Telegram bridge (LAB-291) — optional, enabled via runtime settings or env.
    app.state.telegram_bot = None
    try:
        tg_bot = build_telegram_bot(
            app.state.query_engine,
            overrides=app.state.runtime_settings.get_section("telegram"),
        )
        if tg_bot is not None:
            await tg_bot.start()
            app.state.telegram_bot = tg_bot
    except Exception as exc:
        import logging
        logging.getLogger("zeus").warning("telegram bot failed to start: %s", exc)

    # KAIROS background agent daemon (LAB-330). Default OFF.
    app.state.kairos_daemon = None
    app.state.kairos_state = None
    app.state.kairos_task = None
    if os.getenv("ZEUS_KAIROS_ENABLED", "0").strip() in ("1", "true", "yes", "on"):
        try:
            from zeus.orchestration.daemon import build_default_kairos_daemon

            kairos_daemon, kairos_state = build_default_kairos_daemon(llm_fn=_run_llm)
            app.state.kairos_daemon = kairos_daemon
            app.state.kairos_state = kairos_state
            app.state.kairos_task = asyncio.create_task(kairos_daemon.run_forever())
        except Exception as exc:
            import logging
            logging.getLogger("zeus").warning("kairos daemon failed to start: %s", exc)

    # Kronos scheduler (cron-driven job runner). Default OFF; flip
    # ZEUS_KRONOS_ENABLED=1 per-environment once seed jobs are reviewed.
    app.state.kronos_registry = None
    app.state.kronos_executor = None
    app.state.kronos_scheduler = None
    app.state.kronos_task = None
    app.state.kronos_recent_runs = None
    if os.getenv("ZEUS_KRONOS_ENABLED", "0").strip().lower() in ("1", "true", "yes", "on"):
        try:
            from collections import deque as _deque
            from pathlib import Path as _Path

            from zeus.kronos.executor import KronosExecutor
            from zeus.kronos.registry import KronosRegistry
            from zeus.kronos.scheduler import KronosScheduler
            from zeus.kronos.storage import SQLiteJobStorage

            k_db_path = os.getenv("ZEUS_KRONOS_DB_PATH", "zeus/data/kronos.db")
            os.makedirs(os.path.dirname(k_db_path) or ".", exist_ok=True)
            k_storage = SQLiteJobStorage(k_db_path)
            k_registry = KronosRegistry(k_storage)

            seed_path = _Path("zeus/data/kronos.yaml")
            inserted = await k_registry.seed_from_yaml(seed_path)
            if inserted:
                import logging as _logging
                _logging.getLogger("zeus.kronos").info(
                    "seeded %d new job(s): %s", len(inserted), ", ".join(inserted)
                )

            k_tick = float(os.getenv("ZEUS_KRONOS_TICK_SECONDS", "30"))
            k_max = int(os.getenv("ZEUS_KRONOS_MAX_CONCURRENT", "3"))
            k_recent: _deque = _deque(maxlen=100)

            k_executor = KronosExecutor(
                k_storage,
                http_client=app.state.http_client,
                bus_url=ZEUS_BUS_URL,
            )
            k_scheduler = KronosScheduler(
                k_registry,
                k_executor,
                tick_seconds=k_tick,
                max_concurrent=k_max,
                recent_runs_buffer=k_recent,
            )
            app.state.kronos_registry = k_registry
            app.state.kronos_executor = k_executor
            app.state.kronos_scheduler = k_scheduler
            app.state.kronos_recent_runs = k_recent
            app.state.kronos_task = asyncio.create_task(k_scheduler.run_forever())
        except Exception as exc:
            import logging
            logging.getLogger("zeus").warning("kronos scheduler failed to start: %s", exc)

    # Scheduled ingest (APScheduler). Consolidator removed with mem0 — idempotent
    # re-ingest is now handled by MemoryStore.delete_by_source() / KnowledgeStore.
    app.state.ingest_scheduler = None
    try:
        from zeus.ingest.pipeline import IngestPipeline
        from zeus.ingest.scheduler import build_scheduler

        ingest_pipeline = IngestPipeline(sources=[])
        scheduler = build_scheduler(ingest_pipeline)
        scheduler.start()
        app.state.ingest_scheduler = scheduler
    except Exception as exc:
        import logging
        logging.getLogger("zeus").warning("scheduler not started: %s", exc)

    yield

    kairos_task = getattr(app.state, "kairos_task", None)
    kairos_daemon = getattr(app.state, "kairos_daemon", None)
    if kairos_task is not None and kairos_daemon is not None:
        try:
            kairos_daemon.stop_event.set()
            await asyncio.wait_for(kairos_task, timeout=5.0)
        except (asyncio.TimeoutError, asyncio.CancelledError):
            kairos_task.cancel()
        except Exception:
            pass

    kronos_task = getattr(app.state, "kronos_task", None)
    kronos_scheduler = getattr(app.state, "kronos_scheduler", None)
    if kronos_task is not None and kronos_scheduler is not None:
        try:
            kronos_scheduler.stop_event.set()
            await asyncio.wait_for(kronos_task, timeout=10.0)
        except (asyncio.TimeoutError, asyncio.CancelledError):
            kronos_task.cancel()
        except Exception:
            pass

    ingest_scheduler = getattr(app.state, "ingest_scheduler", None)
    if ingest_scheduler is not None:
        ingest_scheduler.shutdown(wait=False)

    tg_bot = getattr(app.state, "telegram_bot", None)
    if tg_bot is not None:
        try:
            await tg_bot.stop()
        except Exception:
            pass

    await app.state.http_client.aclose()


_STATIC_DIR = Path(__file__).resolve().parent / "static"
_SPA_DIR = _STATIC_DIR / "app"
_SPA_INDEX = _SPA_DIR / "index.html"
_OS_DIR = _STATIC_DIR / "zeus-os"
_OS_INDEX = _OS_DIR / "index.html"

app = FastAPI(title="Zeus Core", version=ZEUS_VERSION, lifespan=lifespan)
app.add_middleware(QueryLoggingMiddleware)

app.include_router(oracle_router)
app.include_router(admin_router)
app.include_router(chat_router)
app.include_router(voice_state_router)
app.include_router(orchestration_router)
app.include_router(kronos_router)
app.include_router(newsletter_router)
app.include_router(vault_router)
app.include_router(inbox_router)
app.include_router(mesh_router)
app.include_router(actions_router)
app.include_router(calendar_router)
app.include_router(epstein_router)  # private branch only; never merge to main
app.include_router(zeus_os_router)

app.mount(
    "/static",
    StaticFiles(directory=str(_STATIC_DIR)),
    name="static",
)

# Serve React SPA assets (built by zeus/frontend via `npm run build`)
if (_SPA_DIR / "assets").is_dir():
    app.mount(
        "/assets",
        StaticFiles(directory=str(_SPA_DIR / "assets")),
        name="spa-assets",
    )

# Serve Zeus OS bundle (built by zeus-os/ via `npm run build`) at /os/.
# adapter-static emits everything under one directory with index.html at root.
if _OS_DIR.is_dir():
    app.mount(
        "/os",
        StaticFiles(directory=str(_OS_DIR), html=True),
        name="zeus-os",
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


# ------------------------------------------------------------------
# Model management endpoints
# ------------------------------------------------------------------


class ModelInfo(BaseModel):
    name: str
    size: int | None = None
    parameter_size: str | None = None
    quantization_level: str | None = None
    modified_at: str | None = None
    family: str | None = None


class ModelsListResponse(BaseModel):
    provider: str  # "ollama" | "claude"
    models: list[ModelInfo]


class ActiveModelResponse(BaseModel):
    provider: str
    model: str
    gpu_available: bool | None = None


class SetModelRequest(BaseModel):
    model: str


@app.get("/models", response_model=ModelsListResponse)
async def list_models(request: Request) -> ModelsListResponse:
    """List models available in Ollama (pulled to the container)."""
    client: httpx.AsyncClient = request.app.state.http_client
    ollama_url = f"{OLLAMA_URL.rstrip('/')}/api/tags"
    try:
        resp = await client.get(ollama_url, timeout=5.0)
        resp.raise_for_status()
        data = resp.json()
    except Exception:
        return ModelsListResponse(provider="ollama", models=[])

    models: list[ModelInfo] = []
    for m in data.get("models", []):
        details = m.get("details", {})
        models.append(ModelInfo(
            name=m.get("name", ""),
            size=m.get("size"),
            parameter_size=details.get("parameter_size"),
            quantization_level=details.get("quantization_level"),
            modified_at=m.get("modified_at"),
            family=details.get("family"),
        ))
    return ModelsListResponse(provider="ollama", models=models)


@app.get("/models/active", response_model=ActiveModelResponse)
async def get_active_model(request: Request) -> ActiveModelResponse:
    """Return the currently active model and provider."""
    provider = "claude" if _chat_use_claude() else "ollama"
    model = _active_model_name()

    # Check GPU status from Ollama
    gpu_available: bool | None = None
    if provider == "ollama":
        client: httpx.AsyncClient = request.app.state.http_client
        try:
            resp = await client.get(f"{OLLAMA_URL.rstrip('/')}/api/ps", timeout=3.0)
            if resp.status_code == 200:
                ps_data = resp.json()
                running = ps_data.get("models", [])
                for rm in running:
                    # If any model is using a GPU layer, GPU is available
                    details = rm.get("details", {})
                    size_vram = rm.get("size_vram", 0)
                    gpu_available = size_vram > 0
                    break
                if not running:
                    gpu_available = None  # no models loaded yet, unknown
        except Exception:
            pass

    return ActiveModelResponse(provider=provider, model=model, gpu_available=gpu_available)


class BenchmarkRunRequest(BaseModel):
    models: list[str] | None = None  # None = all chat models


_bench_lock = asyncio.Lock()
_bench_state: dict[str, Any] = {"running": False, "models": [], "current": None, "completed": []}


async def _bench_worker(models: list[str] | None) -> None:
    runner = BenchmarkRunner(ollama_url=OLLAMA_URL)
    try:
        async with httpx.AsyncClient() as client:
            target = models or await runner.list_models(client)
        _bench_state["models"] = list(target)
        _bench_state["completed"] = []

        def on_progress(evt: dict[str, Any]) -> None:
            if evt["event"] == "start":
                _bench_state["current"] = evt["model"]
            else:
                _bench_state["current"] = None
                _bench_state["completed"].append(evt["model"])
                save_results([
                    r for r in _scratch_results if r.model == evt["model"]
                ])

        _scratch_results = []
        async with httpx.AsyncClient() as client:
            for model in target:
                on_progress({"event": "start", "model": model})
                res = await runner.run_model(model, client=client)
                _scratch_results.append(res)
                save_results([res])
                on_progress({"event": "done", "model": model, "result": res.to_dict()})
    finally:
        _bench_state["running"] = False
        _bench_state["current"] = None


@app.get("/models/benchmarks")
async def get_benchmarks() -> dict[str, Any]:
    payload = load_results()
    payload["status"] = {
        "running": _bench_state["running"],
        "current": _bench_state["current"],
        "queued": _bench_state["models"],
        "completed": _bench_state["completed"],
    }
    return payload


@app.post("/models/benchmarks/run")
async def run_benchmarks(body: BenchmarkRunRequest) -> dict[str, Any]:
    if _bench_lock.locked() or _bench_state["running"]:
        raise HTTPException(status_code=409, detail="Benchmark already running")

    async def _runner() -> None:
        async with _bench_lock:
            _bench_state["running"] = True
            try:
                await _bench_worker(body.models)
            except Exception as exc:
                import logging
                logging.getLogger("zeus").exception("benchmark run failed: %s", exc)

    asyncio.create_task(_runner())
    return {"ok": True, "started": True}


@app.post("/models/active", response_model=ActiveModelResponse)
async def set_active_model(body: SetModelRequest) -> ActiveModelResponse:
    """Switch the active Ollama model at runtime (no restart needed)."""
    set_ollama_model(body.model)
    provider = "claude" if _chat_use_claude() else "ollama"
    return ActiveModelResponse(provider=provider, model=_active_model_name())


async def _restart_telegram_bot(app: FastAPI) -> None:
    """Tear down the existing telegram bot (if any) and rebuild from runtime settings."""
    existing = getattr(app.state, "telegram_bot", None)
    if existing is not None:
        try:
            await existing.stop()
        except Exception as exc:
            import logging
            logging.getLogger("zeus").warning("telegram bot stop failed: %s", exc)
        app.state.telegram_bot = None

    overrides = app.state.runtime_settings.get_section("telegram")
    tg_bot = build_telegram_bot(app.state.query_engine, overrides=overrides)
    if tg_bot is None:
        return
    try:
        await tg_bot.start()
        app.state.telegram_bot = tg_bot
    except Exception as exc:
        import logging
        logging.getLogger("zeus").warning("telegram bot start failed: %s", exc)


class TelegramSettingsPatch(BaseModel):
    enabled: bool | None = None
    bot_token: str | None = None
    allowed_chat_ids: list[int] | None = None
    aegis_policy: str | None = None


class SettingsPatch(BaseModel):
    telegram: TelegramSettingsPatch | None = None


def _mask_token(token: str | None) -> str | None:
    if not token:
        return None
    if len(token) <= 8:
        return "***"
    return f"{token[:4]}…{token[-4:]}"


@app.get("/admin/settings")
async def get_settings(request: Request) -> dict:
    rs: RuntimeSettings = request.app.state.runtime_settings
    snap = rs.snapshot()
    tg = dict(snap.get("telegram", {}))
    if "bot_token" in tg:
        tg["bot_token_masked"] = _mask_token(tg.pop("bot_token"))
    return {"telegram": tg}


@app.patch("/admin/settings")
async def patch_settings(body: SettingsPatch, request: Request) -> dict:
    rs: RuntimeSettings = request.app.state.runtime_settings
    changed: list[str] = []

    if body.telegram is not None:
        updates = body.telegram.model_dump(exclude_none=True)
        if updates:
            rs.update_section("telegram", updates)
            changed.append("telegram")
            await _restart_telegram_bot(request.app)

    return {"ok": True, "changed": changed}


class TelegramStatusResponse(BaseModel):
    enabled: bool
    connected: bool
    bot_username: str | None = None
    chat_count: int = 0


@app.get("/integrations/telegram/status", response_model=TelegramStatusResponse)
async def telegram_status(request: Request) -> TelegramStatusResponse:
    bot = getattr(request.app.state, "telegram_bot", None)
    env_enabled = os.getenv("TELEGRAM_ENABLED", "0").strip().lower() in ("1", "true", "yes")
    runtime_settings = getattr(request.app.state, "runtime_settings", None)
    if runtime_settings is not None:
        telegram_section = runtime_settings.get_section("telegram") or {}
        enabled = bool(telegram_section.get("enabled", env_enabled))
    else:
        enabled = env_enabled
    # A live, running bot is the ground truth — reflect it even if the flag
    # above disagrees (e.g. runtime override applied but file not reloaded).
    if bot is not None and getattr(bot, "running", False):
        enabled = True
    if bot is None:
        return TelegramStatusResponse(enabled=enabled, connected=False)
    return TelegramStatusResponse(
        enabled=enabled,
        connected=bot.running,
        bot_username=bot.bot_username,
        chat_count=bot.chat_count,
    )


@app.get("/{path:path}", include_in_schema=False)
async def spa_fallback(path: str) -> FileResponse:
    """Serve React SPA for all non-API routes. Registered last so it never shadows API routes."""
    if _SPA_INDEX.is_file():
        return FileResponse(str(_SPA_INDEX), media_type="text/html")
    from fastapi import HTTPException
    raise HTTPException(status_code=503, detail="Frontend not built. Run `npm run build` in zeus/frontend/.")