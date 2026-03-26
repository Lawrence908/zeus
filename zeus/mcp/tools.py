"""zeus/mcp/tools.py — MCP tool implementations calling Zeus Core HTTP APIs."""

from __future__ import annotations

import os
from typing import Any

import httpx


def _core_url() -> str:
    return os.getenv("ZEUS_CORE_URL", "http://127.0.0.1:8203").rstrip("/")


def _allow_write() -> bool:
    return os.getenv("ZEUS_MCP_ALLOW_WRITE", "false").strip().lower() in {"1", "true", "yes", "y"}


async def zeus_query(*, query: str, top_k: int = 5, max_tokens: int = 1024) -> dict[str, Any]:
    async with httpx.AsyncClient() as client:
        r = await client.post(
            f"{_core_url()}/context/query",
            json={"query": query, "top_k": top_k, "max_tokens": max_tokens},
            timeout=10,
        )
        r.raise_for_status()
        data = r.json() or {}
        sources = data.get("sources") or []
        source_strings = []
        for s in sources:
            src = (s or {}).get("source")
            if src:
                source_strings.append(str(src))
        return {
            "context": str(data.get("context") or ""),
            "sources": source_strings,
            "token_estimate": int(data.get("token_estimate") or 0),
        }


async def zeus_profile() -> dict[str, Any]:
    async with httpx.AsyncClient() as client:
        r = await client.get(f"{_core_url()}/context/profile", timeout=10)
        r.raise_for_status()
        data = r.json() or {}
        summary = str(data.get("summary") or "")
        facts = data.get("facts") or []
        profile = summary
        if facts:
            profile = summary + "\n" + "\n".join(f"- {str(f)}" for f in facts[:12])
        return {"profile": profile.strip(), "updated_at": ""}


async def zeus_remember(*, text: str, namespace: str = "general", tags: list[str] | None = None) -> dict[str, Any]:
    if not _allow_write():
        raise PermissionError("ZEUS_MCP_ALLOW_WRITE is false; zeus_remember disabled")

    payload = {"text": text, "namespace": namespace, "tags": tags or []}
    async with httpx.AsyncClient() as client:
        r = await client.post(f"{_core_url()}/memory/add", json=payload, timeout=10)
        r.raise_for_status()
        data = r.json() or {}
        return {"memory_id": str(data.get("memory_id") or ""), "status": str(data.get("status") or "ok")}

