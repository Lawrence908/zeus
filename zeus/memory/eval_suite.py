# zeus/memory/eval_suite.py — Shared retrieval-eval scoring core (Themis).
#
# Single source of truth for the per-layer retrieval eval so the pytest harness
# (tests/retrieval_eval.py) and the nightly Kronos job
# (zeus/kronos/jobs/retrieval_eval.py) score identically.
#
# Ground-truth (query, expected_keywords, expected_layer) rows live in
# tests/retrieval_eval_queries/*.yaml, split by the layer that should answer
# them. The pending/ subdir holds proposed-but-unaccepted queries and is
# excluded from scoring.
#
# Scoring runs every query against BOTH the Knowledge layer and the
# Profile/Memories layer, then reports overall + per-layer hit@1/5/10/MRR@10
# plus a `layer_miss` category (keyword found, but in a layer other than the
# expected one). A query that errors is recorded as `error` and excluded from
# the denominator (fail-open per query, never a silent miss).

from __future__ import annotations

import os
import re
from pathlib import Path
from typing import Any

import yaml

# tests/retrieval_eval_queries/ relative to the repo root (this file lives at
# <root>/zeus/memory/eval_suite.py, so parents[2] is the root).
QUERIES_DIR = Path(__file__).resolve().parents[2] / "tests" / "retrieval_eval_queries"
PENDING_DIRNAME = "pending"
VALID_LAYERS = {"knowledge", "profile"}
DEFAULT_TOP_K = 10


def load_suite(*, include_pending: bool = False, queries_dir: Path | None = None) -> list[dict[str, Any]]:
    """Load the accepted query suite. Files under pending/ are excluded unless
    include_pending is set. Each row carries query, expected_keywords,
    expected_layer, and the source file stem."""
    root = queries_dir or QUERIES_DIR
    if not root.is_dir():
        return []

    rows: list[dict[str, Any]] = []
    for path in sorted(root.rglob("*.yaml")):
        if not include_pending and PENDING_DIRNAME in path.relative_to(root).parts:
            continue
        loaded = yaml.safe_load(path.read_text(encoding="utf-8")) or []
        if not isinstance(loaded, list):
            continue
        for item in loaded:
            if not isinstance(item, dict):
                continue
            query = str(item.get("query") or "").strip()
            kws = item.get("expected_keywords") or []
            if not query or not isinstance(kws, list) or not kws:
                continue
            layer = str(item.get("expected_layer") or "knowledge").strip().lower()
            rows.append(
                {
                    "query": query,
                    "expected_keywords": [str(k) for k in kws if str(k).strip()],
                    "expected_layer": layer,
                    "suite": path.stem,
                }
            )
    return rows


def keywords_hit(text: str, keywords: list[str]) -> bool:
    low = text.lower()
    # Substring for multi-word phrases; word-boundary for single tokens.
    for k in keywords:
        kl = k.lower()
        if " " in kl:
            if kl in low:
                return True
        elif re.search(rf"\b{re.escape(kl)}\b", low):
            return True
    return False


def first_rank(hits: list[dict], keywords: list[str]) -> int:
    """1-indexed rank of the first hit whose text matches; 0 if none."""
    for i, h in enumerate(hits):
        if keywords_hit(str(h.get("memory", "")), keywords):
            return i + 1
    return 0


def layer_results(query: str, *, top_k: int = DEFAULT_TOP_K) -> dict[str, list[dict]]:
    """Run every retrieval layer once, returning mem0-shaped dicts per layer."""
    from zeus.memory.search import get_profile_facts, search_knowledge, search_memories

    knowledge = search_knowledge(query=query, user_id="user", top_k=top_k)
    memory = search_memories(query=query, user_id="user", top_k=top_k)
    profile = [{"memory": f} for f in get_profile_facts("user", top_k=top_k)]
    return {"knowledge": knowledge, "memory": memory, "profile": profile}


def expected_and_other(
    layers: dict[str, list[dict]], expected_layer: str
) -> tuple[list[dict], list[dict]]:
    """Split layer results into the expected-layer stream (ordered) and the rest.

    Profile expectations are answered from Profile *or* Memories (profile facts
    ranked first); knowledge expectations from the Knowledge block."""
    if expected_layer == "profile":
        expected = [*layers["profile"], *layers["memory"]]
        other = layers["knowledge"]
    else:
        expected = layers["knowledge"]
        other = [*layers["memory"], *layers["profile"]]
    return expected, other


def _blank_metrics() -> dict[str, Any]:
    return {"n": 0, "hit@1": 0, "hit@5": 0, "hit@10": 0, "layer_miss": 0, "error": 0, "mrr_sum": 0.0}


def _finalize(m: dict[str, Any]) -> dict[str, Any]:
    """Turn raw counters into rates over the non-error denominator."""
    scored = m["n"] - m["error"]
    denom = max(scored, 1)
    return {
        "n_queries": m["n"],
        "n_scored": scored,
        "n_error": m["error"],
        "hit@1": round(m["hit@1"] / denom, 4),
        "hit@5": round(m["hit@5"] / denom, 4),
        "hit@10": round(m["hit@10"] / denom, 4),
        "mrr@10": round(m["mrr_sum"] / denom, 4),
        "layer_miss": round(m["layer_miss"] / denom, 4),
    }


def score_suite(
    suite: list[dict[str, Any]] | None = None, *, top_k: int = DEFAULT_TOP_K
) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    """Score the accepted suite against the live retrieval stack.

    Synchronous (the search helpers are sync); call under asyncio.to_thread from
    async contexts. Returns (summary, per_query). Never raises for a per-query
    retrieval error: that query is recorded as `error` and excluded from the
    denominator."""
    suite = load_suite() if suite is None else suite

    per_query: list[dict[str, Any]] = []
    overall = _blank_metrics()
    by_layer: dict[str, dict[str, Any]] = {}

    for row in suite:
        q = row["query"]
        kws = row["expected_keywords"]
        exp_layer = row["expected_layer"]
        m = by_layer.setdefault(exp_layer, _blank_metrics())
        overall["n"] += 1
        m["n"] += 1

        try:
            layers = layer_results(q, top_k=top_k)
        except Exception as exc:  # noqa: BLE001 - surfaced in the report, never fatal
            overall["error"] += 1
            m["error"] += 1
            per_query.append(
                {
                    "query": q,
                    "suite": row["suite"],
                    "expected_layer": exp_layer,
                    "outcome": "error",
                    "error": str(exc),
                }
            )
            continue

        expected_hits, other_hits = expected_and_other(layers, exp_layer)
        rank = first_rank(expected_hits, kws)
        other_rank = first_rank(other_hits, kws)

        if rank:
            outcome = "hit"
        elif other_rank:
            outcome = "layer_miss"
        else:
            outcome = "miss"

        rr = (1.0 / rank) if rank else 0.0
        for bucket in (overall, m):
            bucket["mrr_sum"] += rr
            if 1 <= rank <= 1:
                bucket["hit@1"] += 1
            if 1 <= rank <= 5:
                bucket["hit@5"] += 1
            if 1 <= rank <= 10:
                bucket["hit@10"] += 1
            if outcome == "layer_miss":
                bucket["layer_miss"] += 1

        per_query.append(
            {
                "query": q,
                "suite": row["suite"],
                "expected_layer": exp_layer,
                "outcome": outcome,
                "first_rank": rank,
                "wrong_layer_rank": other_rank,
                "rr": round(rr, 4),
            }
        )

    summary = {
        "overall": _finalize(overall),
        "per_layer": {layer: _finalize(mm) for layer, mm in sorted(by_layer.items())},
        "config": {
            "ZEUS_KNOWLEDGE_HYBRID": os.getenv("ZEUS_KNOWLEDGE_HYBRID", "1"),
            "ZEUS_KNOWLEDGE_RERANK": os.getenv("ZEUS_KNOWLEDGE_RERANK", "0"),
            "ZEUS_EMBED_MODEL": os.getenv("ZEUS_EMBED_MODEL", "nomic-embed-text"),
        },
    }
    return summary, per_query
