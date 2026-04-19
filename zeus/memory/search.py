"""zeus/memory/search.py — Mnemosyne search helpers (MemoryStore-backed)."""

from __future__ import annotations

import asyncio
import logging
import os
from collections.abc import Iterable

logger = logging.getLogger("zeus.memory.search")

try:
    KNOWLEDGE_SEARCH_TOP_K = max(
        1, min(20, int(os.getenv("ZEUS_KNOWLEDGE_SEARCH_TOP_K", "5")))
    )
except (TypeError, ValueError):
    KNOWLEDGE_SEARCH_TOP_K = 5

try:
    REFERENCE_SEARCH_TOP_K = max(
        1, min(20, int(os.getenv("ZEUS_REFERENCE_SEARCH_TOP_K", "5")))
    )
except (TypeError, ValueError):
    REFERENCE_SEARCH_TOP_K = 5

try:
    MEMORY_SEARCH_TOP_K = max(1, min(20, int(os.getenv("ZEUS_MEMORY_SEARCH_TOP_K", "8"))))
except (TypeError, ValueError):
    MEMORY_SEARCH_TOP_K = 8


def _hit_to_mem0_shape(hit) -> dict:
    """Reshape MemoryStore.MemoryHit -> mem0-shaped dict that format_context_block expects.

    Keeps the renderer and existing API response shapes unchanged during the
    mem0 → MemoryStore migration.
    """
    md = dict(hit.payload)
    md.setdefault("source", hit.source)
    md.setdefault("file", md.get("source_id") or "")
    md.setdefault("type", "memory")
    return {
        "id": hit.id,
        "memory": hit.text,
        "score": hit.score,
        "metadata": md,
    }


def search_memories(
    query: str,
    user_id: str,
    top_k: int | None = None,
    namespaces: list[str] | None = None,
) -> list[dict]:
    """Search the MemoryStore and return mem0-shaped dicts."""
    from zeus.memory.store import get_memory_store

    k = MEMORY_SEARCH_TOP_K if top_k is None else max(1, min(20, top_k))
    try:
        store = get_memory_store()
        hits = store.search(query, user_id=user_id, top_k=k, sources=namespaces or None)
    except Exception as exc:
        logger.warning("memory search failed: %s", exc)
        return []
    return [_hit_to_mem0_shape(h) for h in hits]


def format_context_block(memories: Iterable[dict], max_tokens: int = 2048) -> tuple[str, int]:
    """Format memories as a compact, source-labeled block for prompt injection."""

    def _label(mem: dict) -> str:
        md = mem.get("metadata", {}) or {}
        source = str(md.get("source", "")).strip() or "unknown"
        category = str(md.get("category", "")).strip()
        subject = str(md.get("subject", "")).strip()
        predicate = str(md.get("predicate", "")).strip()
        kind = str(md.get("type", "")).strip()
        file = str(md.get("file", "")).strip()
        title = str(md.get("title", "")).strip()
        score = mem.get("score", None)

        parts: list[str] = []
        if category:
            parts.append(category)
        elif kind:
            parts.append(kind)
        if subject and predicate:
            parts.append(f"{subject}.{predicate}")
        if file:
            parts.append(file)
        elif title:
            parts.append(title)
        if not parts:
            parts.append(source)

        score_part = ""
        try:
            if score is not None:
                score_part = f" score={float(score):.3f}"
        except (TypeError, ValueError):
            score_part = ""

        return f"[{' | '.join(parts)}{score_part}]"

    blocks: list[str] = []
    for mem in memories:
        text = str(mem.get("memory", "")).strip()
        if not text:
            continue
        blocks.append(f"{_label(mem)}\n{text}")

    context = "\n---\n".join(blocks)
    token_estimate = len(context) // 4
    if token_estimate > max_tokens:
        max_chars = max_tokens * 4
        context = context[:max_chars].rstrip() + "\n[truncated]"
        token_estimate = max_tokens

    return context, token_estimate


def search_knowledge(
    query: str,
    user_id: str,
    top_k: int | None = None,
    sources: list[str] | None = None,
) -> list[dict]:
    """Vector search over the raw-chunk Knowledge layer (separate from MemoryStore)."""
    from zeus.memory.library import get_knowledge_store

    k = KNOWLEDGE_SEARCH_TOP_K if top_k is None else max(1, min(20, top_k))
    try:
        store = get_knowledge_store()
        hits = store.search(query, top_k=k, user_id=user_id, sources=sources)
    except Exception as exc:
        logger.warning("knowledge search failed: %s", exc)
        return []

    results: list[dict] = []
    for hit in hits:
        md = dict(hit.payload)
        md.setdefault("source", hit.source)
        md.setdefault("file", hit.source_path)
        md.setdefault("type", "knowledge")
        results.append(
            {
                "memory": hit.text,
                "score": hit.score,
                "metadata": md,
            }
        )
    return results


async def search_reference(query: str, top_k: int | None = None) -> list[dict]:
    """Live HTTP proxy to kiwix + NOMAD. Returns mem0-shaped dicts."""
    from zeus.memory.reference import ReferenceHit, get_reference_clients

    k = REFERENCE_SEARCH_TOP_K if top_k is None else max(1, min(20, top_k))
    kiwix, nomad = get_reference_clients()
    if kiwix is None and nomad is None:
        return []

    tasks = []
    if kiwix is not None:
        tasks.append(kiwix.search(query, top_k=k))
    if nomad is not None:
        tasks.append(nomad.search(query, top_k=k))

    try:
        results = await asyncio.gather(*tasks, return_exceptions=True)
    except Exception as exc:
        logger.warning("reference gather failed: %s", exc)
        return []

    hits: list[ReferenceHit] = []
    for r in results:
        if isinstance(r, Exception):
            logger.warning("reference backend raised: %s", r)
            continue
        hits.extend(r)

    hits.sort(key=lambda h: h.score, reverse=True)
    hits = hits[:k]

    out: list[dict] = []
    for hit in hits:
        out.append(
            {
                "memory": hit.text,
                "score": hit.score,
                "metadata": {
                    "source": hit.source,
                    "file": hit.source_path or hit.url,
                    "title": hit.source_path,
                    "type": "reference",
                    "url": hit.url,
                },
            }
        )
    return out


def get_profile_facts(user_id: str, top_k: int = 8) -> list[str]:
    """Retrieve stable profile facts; prefer context_pack + identity/preference categories."""
    from zeus.memory.store import get_memory_store

    store = get_memory_store()
    try:
        preferred_hits = store.search(
            "stable profile facts identity preferences",
            user_id=user_id,
            top_k=top_k * 2,
            sources=["context_pack"],
        )
        fallback_hits = store.search(
            "identity preferences current projects",
            user_id=user_id,
            top_k=top_k * 2,
            category=["identity", "preference", "skill", "relationship"],
        )
    except Exception as exc:
        logger.warning("profile fact search failed: %s", exc)
        return []

    seen: set[str] = set()
    facts: list[str] = []
    for hit in [*preferred_hits, *fallback_hits]:
        text = hit.text.strip()
        if not text or text in seen:
            continue
        seen.add(text)
        facts.append(text)
        if len(facts) >= top_k:
            break
    return facts
