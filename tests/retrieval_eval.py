# tests/retrieval_eval.py — Retrieval regression harness for Zeus (Themis).
#
# Thin pytest wrapper over the shared scoring core in zeus/memory/eval_suite.py
# (which the nightly Kronos job also uses, so both score identically). Ground
# truth lives in tests/retrieval_eval_queries/*.yaml, split by expected layer;
# pending/ is excluded. See zeus/memory/eval_suite.py for the scoring model
# (per-layer hit@1/5/10/MRR@10 + layer_miss + fail-open-per-query).
#
# Gate with ZEUS_RUN_RETRIEVAL_EVAL=1 (requires Qdrant + Ollama up). Optional
# ZEUS_RETRIEVAL_MIN_HIT5=<float> fails the test if overall hit@5 drops below
# the threshold. Optional ZEUS_RETRIEVAL_EVAL_OUT writes the full report to disk.

from __future__ import annotations

import json
import os

import pytest

from zeus.memory.eval_suite import VALID_LAYERS, load_suite, score_suite


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


@pytest.mark.skipif(
    os.getenv("ZEUS_RUN_RETRIEVAL_EVAL") != "1",
    reason="Set ZEUS_RUN_RETRIEVAL_EVAL=1 to run live retrieval eval (needs Qdrant + Ollama).",
)
def test_live_retrieval_metrics(capsys):
    """Score the accepted suite with overall + per-layer metrics and layer_miss."""
    suite = load_suite()
    assert suite, "no accepted queries to score"

    summary, per_query = score_suite(suite)

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

    out_path = os.getenv("ZEUS_RETRIEVAL_EVAL_OUT")
    if out_path:
        with open(out_path, "w") as f:
            json.dump({"summary": summary, "per_query": per_query}, f, indent=2)

    min_hit5 = os.getenv("ZEUS_RETRIEVAL_MIN_HIT5")
    if min_hit5:
        threshold = float(min_hit5)
        assert summary["overall"]["hit@5"] >= threshold, (
            f"overall hit@5 {summary['overall']['hit@5']} below threshold {threshold}"
        )
