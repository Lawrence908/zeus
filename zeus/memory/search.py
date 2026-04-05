"""zeus/memory/search.py — Mnemosyne search helpers."""

import os
from collections.abc import Iterable

# Tunable via env (LAB-126); clamped to mem0 practical range.
MEMORY_SEARCH_TOP_K = max(1, min(20, int(os.getenv("ZEUS_MEMORY_SEARCH_TOP_K", "8"))))


def _matches_namespaces(memory_item: dict, namespaces: list[str]) -> bool:
    if not namespaces:
        return True

    metadata = memory_item.get("metadata", {}) or {}
    source = str(metadata.get("source", ""))
    namespace = str(metadata.get("namespace", ""))

    for candidate in namespaces:
        if namespace == candidate:
            return True
        if source.startswith(f"{candidate}:"):
            return True
    return False


def search_memories(
    memory,
    query: str,
    user_id: str,
    top_k: int | None = None,
    namespaces: list[str] | None = None,
) -> list[dict]:
    """Search mem0 and apply lightweight namespace filtering."""
    k = MEMORY_SEARCH_TOP_K if top_k is None else top_k
    results = memory.search(query=query, user_id=user_id, limit=k)
    if not isinstance(results, list):
        return []

    namespace_filters = namespaces or []
    filtered = [item for item in results if _matches_namespaces(item, namespace_filters)]
    return filtered[:k]


def format_context_block(memories: Iterable[dict], max_tokens: int = 2048) -> tuple[str, int]:
    """Format memories as a compact, source-labeled block for prompt injection."""

    def _label(mem: dict) -> str:
        md = mem.get("metadata", {}) or {}
        source = str(md.get("source", "")).strip() or "unknown"
        kind = str(md.get("type", "")).strip()
        file = str(md.get("file", "")).strip()
        title = str(md.get("title", "")).strip()
        score = mem.get("score", None)

        parts: list[str] = []
        if kind:
            parts.append(kind)
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

        return f"[{ ' | '.join(parts) }{score_part}]"

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


def get_profile_facts(memory, user_id: str, top_k: int = 8) -> list[str]:
    """Retrieve stable user profile facts with priority for context_pack memories.

    One vector search + in-process split avoids a duplicate Ollama embed of the same
    query (mem0 embeds per search; Zeus alternates embed/chat models on the GPU).
    """
    q = "stable profile facts identity goals preferences current projects"
    fetch_n = max(top_k * 2, 8)
    raw = memory.search(query=q, user_id=user_id, limit=fetch_n)
    if not isinstance(raw, list):
        raw = []
    preferred = [m for m in raw if _matches_namespaces(m, ["context_pack"])]
    fallback = [m for m in raw if not _matches_namespaces(m, ["context_pack"])]

    # Keep order stable while de-duplicating by text.
    seen: set[str] = set()
    facts: list[str] = []
    for mem in [*preferred, *fallback]:
        text = str(mem.get("memory", "")).strip()
        if not text or text in seen:
            continue
        seen.add(text)
        facts.append(text)
        if len(facts) >= top_k:
            break

    return facts
