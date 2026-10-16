# zeus/memory/_embed.py — Shared Ollama embedding helper for MemoryStore + KnowledgeStore.
from __future__ import annotations

import logging
import os

import httpx

logger = logging.getLogger(__name__)


def _int_env(name: str, default: int) -> int:
    raw = os.getenv(name)
    if raw is None:
        return default
    try:
        value = int(raw.strip())
    except ValueError:
        logger.warning("Invalid %s=%r; falling back to default %d", name, raw, default)
        return default
    if value <= 0:
        logger.warning("%s must be positive, got %d; using default %d", name, value, default)
        return default
    return value


# Dense vector width. This MUST match the Qdrant collection's configured size.
# Swapping embedding models therefore means a full re-embed into a NEW collection
# followed by an atomic cutover (scripts/reembed_retrieval.py), never an in-place
# model change: vectors from two models are not comparable, and mixing them
# degrades recall silently rather than erroring.
#   nomic-embed-text:v1.5  ->  768
#   qwen3-embedding:0.6b   -> 1024
#   qwen3-embedding:4b     -> 2560
DEFAULT_EMBED_DIMS = _int_env("ZEUS_EMBED_DIMS", 768)

# Longest chunk measured across zeus_knowledge / zeus_memories / zeus_news was
# 5906 chars (~1700 tokens), so 4096 covers the whole corpus with headroom.
# Raising it costs KV-cache VRAM on a card shared with ComfyUI; don't inflate it
# without a measurement. (nomic-embed-text:v1.5 was trained at n_ctx=2048 and
# warns above that; qwen3-embedding handles 32k.)
DEFAULT_EMBED_NUM_CTX = 4096

# Ollama's /api/embed takes an "input" array and is ~4x faster than one request
# per text (measured 51 vs 12 texts/s for nomic on the 3080). The older
# /api/embeddings endpoint is single-item only.
DEFAULT_EMBED_BATCH = 64

# Asymmetric embedding models want an instruction marking query vs document, and
# the convention differs by family. Ollama does not add one, so we do it here.
# Changing the style changes the vector space: the corpus must be re-embedded and
# queries prefixed identically, which is why this is tied to a re-embed migration.
#
#   nomic : BOTH sides prefixed -- "search_document: " / "search_query: "
#   qwen3 : documents bare; queries get "Instruct: {task}\nQuery: ".
#           Qwen reports 1-5% retrieval gain from the query instruction, so
#           omitting it gives away part of the upgrade.
EMBED_PREFIXES = os.getenv("ZEUS_EMBED_PREFIXES", "0").strip().lower() not in (
    "0",
    "false",
    "no",
    "",
)
_NOMIC_PREFIX = {"query": "search_query: ", "document": "search_document: "}
_DEFAULT_INSTRUCT = "Given a search query, retrieve relevant passages that answer it"


def _model_name(model: str | None = None) -> str:
    return model or os.getenv("ZEUS_EMBED_MODEL", "nomic-embed-text:v1.5")


def prefix_style(model: str | None = None) -> str:
    """Resolve the instruction convention: "nomic", "qwen3", or "none".

    ZEUS_EMBED_PREFIX_STYLE pins it explicitly; the default "auto" infers from
    the model name so the style can never drift out of sync with the model.
    """
    style = os.getenv("ZEUS_EMBED_PREFIX_STYLE", "auto").strip().lower()
    if style in ("nomic", "qwen3", "none"):
        return style
    name = _model_name(model).lower()
    if "qwen3" in name:
        return "qwen3"
    return "nomic" if EMBED_PREFIXES else "none"


def _apply_prefix(text: str, task: str, style: str) -> str:
    if style == "nomic":
        return f"{_NOMIC_PREFIX.get(task, '')}{text}"
    if style == "qwen3" and task == "query":
        instruct = os.getenv("ZEUS_EMBED_INSTRUCT", _DEFAULT_INSTRUCT).strip()
        return f"Instruct: {instruct}\nQuery: {text}"
    return text


def _timeout() -> httpx.Timeout:
    read = float(os.getenv("OLLAMA_EMBED_TIMEOUT_SEC", "120"))
    return httpx.Timeout(connect=10.0, read=read, write=10.0, pool=10.0)


def embed_texts(
    texts: list[str],
    *,
    ollama_url: str | None = None,
    model: str | None = None,
    task: str = "document",
    batch_size: int | None = None,
) -> list[list[float]]:
    """Embed texts via Ollama's batched /api/embed, preserving input order.

    ``task`` selects the instruction prefix ("query" or "document"); see
    ``prefix_style``. Callers embedding a search query MUST pass ``task="query"``
    so the asymmetric model sees the same framing it was trained on;
    document/chunk writes use the default.

    Raises if the model returns a vector width other than DEFAULT_EMBED_DIMS,
    since writing a mismatched width is the failure mode that corrupts a
    collection quietly.
    """
    if not texts:
        return []

    url = (ollama_url or os.getenv("OLLAMA_URL", "http://localhost:11435")).rstrip("/")
    embed_model = _model_name(model)
    keep_alive = os.getenv("ZEUS_EMBED_KEEP_ALIVE", "24h")
    num_ctx = _int_env("ZEUS_EMBED_NUM_CTX", DEFAULT_EMBED_NUM_CTX)
    size = batch_size or _int_env("ZEUS_EMBED_BATCH", DEFAULT_EMBED_BATCH)
    style = prefix_style(embed_model)
    prepared = [_apply_prefix(t, task, style) for t in texts]

    vectors: list[list[float]] = []
    with httpx.Client(timeout=_timeout()) as client:
        for start in range(0, len(prepared), size):
            chunk = prepared[start : start + size]
            resp = client.post(
                f"{url}/api/embed",
                json={
                    "model": embed_model,
                    "input": chunk,
                    "keep_alive": keep_alive,
                    "options": {"num_ctx": num_ctx},
                },
            )
            resp.raise_for_status()
            embeddings = (resp.json() or {}).get("embeddings")
            if not isinstance(embeddings, list) or len(embeddings) != len(chunk):
                raise RuntimeError(
                    f"ollama returned {len(embeddings) if isinstance(embeddings, list) else 'no'} "
                    f"embeddings for a batch of {len(chunk)} (model={embed_model})"
                )
            for emb in embeddings:
                if not isinstance(emb, list) or not emb:
                    raise RuntimeError(f"ollama returned an empty embedding (model={embed_model})")
                if len(emb) != DEFAULT_EMBED_DIMS:
                    raise RuntimeError(
                        f"{embed_model} returned {len(emb)}-dim vectors but "
                        f"ZEUS_EMBED_DIMS is {DEFAULT_EMBED_DIMS}; refusing to write "
                        "mismatched vectors (set ZEUS_EMBED_DIMS and re-embed)"
                    )
            vectors.extend(embeddings)
    return vectors
