# tests/retrieval_eval.py — Retrieval regression harness for Zeus (Themis).
#
# Ground-truth (query, expected_keywords, expected_layer) rows live in
# tests/retrieval_eval_queries/*.yaml, split by the layer that should answer
# them (profile_questions.yaml, knowledge_questions.yaml). The pending/ subdir
# holds proposed-but-unaccepted queries and is excluded from scoring.
#
# Each live run runs every query against BOTH the Knowledge layer and the
# Profile/Memories layer, then scores:
#   - overall hit@1 / hit@5 / hit@10 / MRR@10 (rank within the expected layer),
#   - the same metrics broken out per expected_layer, and
#   - a `layer_miss` category: the keyword was found, but in a layer other than
#     the expected one. This is a distinct failure from "not found at all" and
#     is the signal that sub-budgets or routing need attention.
# A query that errors is recorded as `error` and excluded from the denominator
# (fail-open per query, never silently counted as a miss).
#
# Gate with ZEUS_RUN_RETRIEVAL_EVAL=1 (requires Qdrant + Ollama up). Optional
# ZEUS_RETRIEVAL_MIN_HIT5=<float> fails the test if overall hit@5 drops below
# the threshold — set this to the current baseline before changing config.

from __future__ import annotations

import json
import os
import re
from pathlib import Path
from typing import Any

import pytest
import yaml

QUERIES_DIR = Path(__file__).parent / "retrieval_eval_queries"
PENDING_DIRNAME = "pending"
VALID_LAYERS = {"knowledge", "profile"}


def load_suite(*, include_pending: bool = False) -> list[dict[str, Any]]:
    """Load the accepted query suite from tests/retrieval_eval_queries/*.yaml.

    Files under pending/ are excluded unless include_pending is set. Each row
    carries query, expected_keywords, expected_layer, and the source file stem.
    """
    if not QUERIES_DIR.is_dir():
        return []

    rows: list[dict[str, Any]] = []
    for path in sorted(QUERIES_DIR.rglob("*.yaml")):
        if not include_pending and PENDING_DIRNAME in path.relative_to(QUERIES_DIR).parts:
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


def _keywords_hit(text: str, keywords: list[str]) -> bool:
    low = text.lower()
    # Use plain substring for multi-word phrases; word-boundary for single tokens.
    for k in keywords:
        kl = k.lower()
        if " " in kl:
            if kl in low:
                return True
        elif re.search(rf"\b{re.escape(kl)}\b", low):
            return True
    return False


def _first_rank(hits: list[dict], keywords: list[str]) -> int:
    """1-indexed rank of the first hit whose text matches; 0 if none."""
    for i, h in enumerate(hits):
        if _keywords_hit(str(h.get("memory", "")), keywords):
            return i + 1
    return 0


def test_ground_truth_minimum_size():
    knowledge = [r for r in load_suite() if r["expected_layer"] == "knowledge"]
    assert len(knowledge) >= 30


def test_ground_truth_shape():
    rows = load_suite()
    assert rows, "no query files found under tests/retrieval_eval_queries/"
    for row in rows:
        assert isinstance(row["query"], str) and row["query"].strip()
        kws = row["expected_keywords"]
        assert isinstance(kws, list) and len(kws) >= 1
        assert all(isinstance(k, str) and k.strip() for k in kws)
        assert row["expected_layer"] in VALID_LAYERS


def _layer_results(query: str) -> dict[str, list[dict]]:
    """Run every retrieval layer once and return its results as mem0-shaped dicts."""
    from zeus.memory.search import get_profile_facts, search_knowledge, search_memories

    top_k = 10
    knowledge = search_knowledge(query=query, user_id="user", top_k=top_k)
    memory = search_memories(query=query, user_id="user", top_k=top_k)
    profile = [{"memory": f} for f in get_profile_facts("user", top_k=top_k)]
    return {"knowledge": knowledge, "memory": memory, "profile": profile}


def _expected_and_other(layers: dict[str, list[dict]], expected_layer: str) -> tuple[list[dict], list[dict]]:
    """Split layer results into the expected-layer stream (ordered) and the rest.

    Profile expectations are answered from Profile *or* Memories (profile facts
    ranked first); knowledge expectations from the Knowledge block.
    """
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


@pytest.mark.skipif(
    os.getenv("ZEUS_RUN_RETRIEVAL_EVAL") != "1",
    reason="Set ZEUS_RUN_RETRIEVAL_EVAL=1 to run live retrieval eval (needs Qdrant + Ollama).",
)
def test_live_retrieval_metrics(capsys):
    """Score the accepted suite with overall + per-layer metrics and layer_miss."""
    suite = load_suite()
    assert suite, "no accepted queries to score"

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

        # Fail-open per query: a retrieval error is recorded, not counted as a miss.
        try:
            layers = _layer_results(q)
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

        expected_hits, other_hits = _expected_and_other(layers, exp_layer)
        rank = _first_rank(expected_hits, kws)
        other_rank = _first_rank(other_hits, kws)

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
        "per_layer": {layer: _finalize(m) for layer, m in sorted(by_layer.items())},
        "config": {
            "ZEUS_KNOWLEDGE_HYBRID": os.getenv("ZEUS_KNOWLEDGE_HYBRID", "1"),
            "ZEUS_KNOWLEDGE_RERANK": os.getenv("ZEUS_KNOWLEDGE_RERANK", "0"),
            "ZEUS_EMBED_MODEL": os.getenv("ZEUS_EMBED_MODEL", "nomic-embed-text"),
        },
    }

    # Per-query report — makes failing queries immediately actionable.
    print("\n=== retrieval_eval: per-query ===")
    tag = {"hit": "OK   ", "layer_miss": "LAYER", "miss": "MISS ", "error": "ERR  "}
    for row in per_query:
        print(
            f"  {tag.get(row['outcome'], '?')} [{row['expected_layer'][:4]:4}] "
            f"rank={row.get('first_rank', 0):>2}  {row['query'][:58]:58}"
        )
    print("=== retrieval_eval: summary ===")
    print(json.dumps(summary, indent=2))

    # Optional write to disk for tracking across runs.
    out_path = os.getenv("ZEUS_RETRIEVAL_EVAL_OUT")
    if out_path:
        with open(out_path, "w") as f:
            json.dump({"summary": summary, "per_query": per_query}, f, indent=2)

    # Optional regression gate on overall hit@5.
    min_hit5 = os.getenv("ZEUS_RETRIEVAL_MIN_HIT5")
    if min_hit5:
        threshold = float(min_hit5)
        assert summary["overall"]["hit@5"] >= threshold, (
            f"overall hit@5 {summary['overall']['hit@5']} below threshold {threshold}"
        )
