# zeus/core/main.py
"""Zeus Core — FastAPI bus and main router."""

import os
import time
from contextlib import asynccontextmanager
from datetime import datetime, timezone
import httpx
from fastapi import FastAPI
from pydantic import BaseModel

from zeus import __version__

# Track startup time for uptime calculation
_start_time: float = 0.0


class ServiceStatus(BaseModel):
    """Status of an individual service."""
    name: str
    status: str  # "healthy", "unhealthy", "unknown"
    latency_ms: float | None = None
    error: str | None = None


class StatusResponse(BaseModel):
    """Response model for /status endpoint."""
    service: str
    version: str
    environment: str
    uptime_seconds: float
    started_at: str
    services: dict[str, ServiceStatus]


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifespan — startup and shutdown."""
    global _start_time
    _start_time = time.time()
    yield


app = FastAPI(
    title="Zeus Core",
    description="Personal AI Assistant — FastAPI bus and main router",
    version=__version__,
    lifespan=lifespan,
)


def get_env() -> str:
    """Get current environment (dev/prod)."""
    return os.getenv("ZEUS_ENV", "dev")


async def check_qdrant() -> ServiceStatus:
    """Check Qdrant vector database health."""
    host = os.getenv("QDRANT_HOST", "localhost")
    port = os.getenv("QDRANT_PORT", "6333")
    url = f"http://{host}:{port}/readiness"
    
    try:
        start = time.time()
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get(url)
        latency = (time.time() - start) * 1000
        
        if response.status_code == 200:
            return ServiceStatus(name="qdrant", status="healthy", latency_ms=latency)
        return ServiceStatus(
            name="qdrant",
            status="unhealthy",
            latency_ms=latency,
            error=f"HTTP {response.status_code}"
        )
    except httpx.ConnectError:
        return ServiceStatus(name="qdrant", status="unhealthy", error="Connection refused")
    except httpx.TimeoutException:
        return ServiceStatus(name="qdrant", status="unhealthy", error="Timeout")
    except Exception as e:
        return ServiceStatus(name="qdrant", status="unknown", error=str(e))


async def check_ollama() -> ServiceStatus:
    """Check Ollama LLM server health."""
    host = os.getenv("OLLAMA_HOST", "http://localhost:11434")
    url = f"{host}/api/tags"
    
    try:
        start = time.time()
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get(url)
        latency = (time.time() - start) * 1000
        
        if response.status_code == 200:
            return ServiceStatus(name="ollama", status="healthy", latency_ms=latency)
        return ServiceStatus(
            name="ollama",
            status="unhealthy",
            latency_ms=latency,
            error=f"HTTP {response.status_code}"
        )
    except httpx.ConnectError:
        return ServiceStatus(name="ollama", status="unhealthy", error="Connection refused")
    except httpx.TimeoutException:
        return ServiceStatus(name="ollama", status="unhealthy", error="Timeout")
    except Exception as e:
        return ServiceStatus(name="ollama", status="unknown", error=str(e))


async def check_anthropic() -> ServiceStatus:
    """Check Anthropic API availability (dev mode only)."""
    api_key = os.getenv("ANTHROPIC_API_KEY")
    
    if not api_key:
        return ServiceStatus(name="anthropic", status="unknown", error="No API key configured")
    
    # Just verify key format, don't make actual API call to avoid rate limits
    if api_key.startswith("sk-ant-"):
        return ServiceStatus(name="anthropic", status="healthy")
    return ServiceStatus(name="anthropic", status="unhealthy", error="Invalid API key format")


@app.get("/")
async def root() -> dict[str, str]:
    """Root endpoint — basic info."""
    return {
        "service": "zeus-core",
        "version": __version__,
        "docs": "/docs",
    }


@app.get("/status", response_model=StatusResponse)
async def status() -> StatusResponse:
    """
    Service health status.
    
    Returns version, uptime, and reachability of dependent services:
    - Qdrant (vector database)
    - Ollama (LLM server, prod mode)
    - Anthropic (Claude API, dev mode)
    """
    env = get_env()
    uptime = time.time() - _start_time
    started = datetime.fromtimestamp(_start_time, tz=timezone.utc).isoformat()
    
    # Check all services in parallel
    qdrant_status = await check_qdrant()
    ollama_status = await check_ollama()
    anthropic_status = await check_anthropic()
    
    services = {
        "qdrant": qdrant_status,
        "ollama": ollama_status,
        "anthropic": anthropic_status,
    }
    
    return StatusResponse(
        service="zeus-core",
        version=__version__,
        environment=env,
        uptime_seconds=round(uptime, 2),
        started_at=started,
        services=services,
    )


@app.get("/health")
async def health() -> dict[str, str]:
    """Simple health check for load balancers / container orchestration."""
    return {"status": "ok"}
