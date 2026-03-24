# zeus/core/main.py — Zeus Core API bus and health endpoint
import os
import time
from contextlib import asynccontextmanager

import httpx
from fastapi import FastAPI
from pydantic import BaseModel

ZEUS_VERSION = "0.1.0"
BOOT_TIME = time.time()

ZEUS_ENV = os.getenv("ZEUS_ENV", "dev")
QDRANT_URL = os.getenv("QDRANT_URL", "http://localhost:6333")
OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434")


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
    yield
    await app.state.http_client.aclose()


app = FastAPI(
    title="Zeus Core",
    version=ZEUS_VERSION,
    lifespan=lifespan,
)


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
    return {"name": "zeus", "version": ZEUS_VERSION, "env": ZEUS_ENV}
