# zeus/memory/_embed.py — Shared Ollama embedding helper for MemoryStore + KnowledgeStore.
from __future__ import annotations

import os

import httpx

DEFAULT_EMBED_DIMS = 768  # nomic-embed-text


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
    embed_model = model or os.getenv("ZEUS_EMBED_MODEL", "nomic-embed-text")

    vectors: list[list[float]] = []
    with httpx.Client(timeout=_timeout()) as client:
        for text in texts:
            resp = client.post(
                f"{url}/api/embeddings",
                json={"model": embed_model, "prompt": text},
            )
            resp.raise_for_status()
            emb = resp.json().get("embedding")
            if not isinstance(emb, list) or not emb:
                raise RuntimeError(
                    f"ollama returned no embedding for chunk ({len(text)} chars)"
                )
            vectors.append(emb)
    return vectors
