"""zeus/memory/search.py — Mnemosyne search helpers."""

from collections.abc import Iterable


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
    top_k: int = 5,
    namespaces: list[str] | None = None,
) -> list[dict]:
    """Search mem0 and apply lightweight namespace filtering."""
    results = memory.search(query=query, user_id=user_id, limit=top_k)
    if not isinstance(results, list):
        return []

    namespace_filters = namespaces or []
    filtered = [item for item in results if _matches_namespaces(item, namespace_filters)]
    return filtered[:top_k]


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
    """Retrieve stable user profile facts with priority for context_pack memories."""
    preferred = search_memories(
        memory=memory,
        query="stable profile facts identity goals preferences current projects",
        user_id=user_id,
        top_k=max(top_k * 2, 8),
        namespaces=["context_pack"],
    )
    fallback = search_memories(
        memory=memory,
        query="stable profile facts identity goals preferences current projects",
        user_id=user_id,
        top_k=max(top_k * 2, 8),
    )

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
