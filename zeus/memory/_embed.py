# zeus/memory/_embed.py — Shared Ollama embedding helper for MemoryStore + KnowledgeStore.
from __future__ import annotations

import logging
import os

import httpx

DEFAULT_EMBED_DIMS = 768  # nomic-embed-text
# nomic-embed-text:v1.5 was trained with n_ctx=2048; asking for more triggers a
# llama.cpp "requested context size too large" warning and wastes KV-cache VRAM.
DEFAULT_EMBED_NUM_CTX = 2048
logger = logging.getLogger(__name__)


def _timeout() -> httpx.Timeout:
    read = float(os.getenv("OLLAMA_EMBED_TIMEOUT_SEC", "120"))
    return httpx.Timeout(connect=10.0, read=read, write=10.0, pool=10.0)


def embed_texts(
    texts: list[str],
    *,
    ollama_url: str | None = None,
    model: str | None = None,
) -> list[list[float]]:
    """Embed each text via Ollama's /api/embeddings. Ollama has no batch endpoint."""
    url = (ollama_url or os.getenv("OLLAMA_URL", "http://localhost:11435")).rstrip("/")
    embed_model = model or os.getenv("ZEUS_EMBED_MODEL", "nomic-embed-text:v1.5")
    keep_alive = os.getenv("ZEUS_EMBED_KEEP_ALIVE", "24h")
    raw_num_ctx = os.getenv("ZEUS_EMBED_NUM_CTX")
    num_ctx = DEFAULT_EMBED_NUM_CTX
    if raw_num_ctx is not None:
        try:
            parsed_num_ctx = int(raw_num_ctx.strip())
            if parsed_num_ctx <= 0:
                raise ValueError(
                    f"ZEUS_EMBED_NUM_CTX must be positive, got {parsed_num_ctx}"
                )
            num_ctx = parsed_num_ctx
        except ValueError:
            logger.warning(
                "Invalid ZEUS_EMBED_NUM_CTX=%r; falling back to default %d",
                raw_num_ctx,
                DEFAULT_EMBED_NUM_CTX,
            )

    vectors: list[list[float]] = []
    with httpx.Client(timeout=_timeout()) as client:
        for text in texts:
            resp = client.post(
                f"{url}/api/embeddings",
                json={
                    "model": embed_model,
                    "prompt": text,
                    "keep_alive": keep_alive,
                    "options": {"num_ctx": num_ctx},
                },
            )
            resp.raise_for_status()
            emb = resp.json().get("embedding")
            if not isinstance(emb, list) or not emb:
                raise RuntimeError(
                    f"ollama returned no embedding for chunk ({len(text)} chars)"
                )
            vectors.append(emb)
    return vectors
