# tests/retrieval_eval.py — Ground-truth pairs for retrieval regression (LAB-127)
#
# Tune chunking / ZEUS_MEMORY_SEARCH_TOP_K against real data; this file stays
# repo-local expectations. Expand with strings that appear in your ingested corpus.

from __future__ import annotations

import os
import re
from typing import Any

import pytest

# 15 benchmark-style pairs: query → keywords that should appear in top hits (any match).
GROUND_TRUTH: list[dict[str, Any]] = [
    {"query": "What is the Zeus project?", "expected_keywords": ["zeus", "assistant", "homelab"]},
    {"query": "Zeus stack and components", "expected_keywords": ["fastapi", "mem0", "qdrant"]},
    {"query": "How does Zeus handle voice?", "expected_keywords": ["orpheus", "tts", "stt"]},
    {"query": "Mnemosyne memory layer", "expected_keywords": ["memory", "vector", "embed"]},
    {"query": "Iris ingest pipeline", "expected_keywords": ["ingest", "chunk", "markdown"]},
    {"query": "Aegis safety policies", "expected_keywords": ["safety", "policy", "aegis"]},
    {"query": "Oracle context API", "expected_keywords": ["context", "profile", "query"]},
    {"query": "Homelab server GPU", "expected_keywords": ["ollama", "rtx", "vram"]},
    {"query": "Chat session continuity", "expected_keywords": ["session", "summary", "turn"]},
    {"query": "MCP server integration", "expected_keywords": ["mcp", "tool", "stdio"]},
    {"query": "Ruflo orchestration agents", "expected_keywords": ["agent", "ruflo", "yaml"]},
    {"query": "Qdrant collection configuration", "expected_keywords": ["qdrant", "collection", "vector"]},
    {"query": "Personal preferences and facts", "expected_keywords": ["preference", "fact", "profile"]},
    {"query": "Docker compose Zeus services", "expected_keywords": ["docker", "compose", "core"]},
    {"query": "Embedding model name", "expected_keywords": ["nomic", "embed", "ollama"]},
]


def _keywords_hit(text: str, keywords: list[str]) -> bool:
    low = text.lower()
    return any(re.search(rf"\b{re.escape(k.lower())}\b", low) for k in keywords)


def test_ground_truth_minimum_size():
    assert len(GROUND_TRUTH) >= 10


def test_ground_truth_shape():
    for row in GROUND_TRUTH:
        assert isinstance(row.get("query"), str) and row["query"].strip()
        kws = row.get("expected_keywords")
        assert isinstance(kws, list) and len(kws) >= 1
        assert all(isinstance(k, str) and k.strip() for k in kws)


@pytest.mark.skipif(
    os.getenv("ZEUS_RUN_RETRIEVAL_EVAL") != "1",
    reason="Set ZEUS_RUN_RETRIEVAL_EVAL=1 to run live mem0 checks (needs Qdrant + embedder).",
)
def test_live_retrieval_keywords():
    from zeus.memory.config import get_memory_client
    from zeus.memory.search import search_memories

    memory = get_memory_client()
    failures: list[str] = []
    for row in GROUND_TRUTH:
        q = str(row["query"])
        kws = list(row["expected_keywords"])
        hits = search_memories(memory=memory, query=q, user_id="chris", top_k=5, namespaces=[])
        if not hits:
            failures.append(f"{q!r}: no hits")
            continue
        top = str(hits[0].get("memory", ""))
        if not _keywords_hit(top, kws):
            failures.append(f"{q!r}: top-1 missing keywords {kws!r} — {top[:120]!r}")

    if failures:
        pytest.fail("\n".join(failures))
