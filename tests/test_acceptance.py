# tests/test_acceptance.py — Acceptance gate (Argo self-improvement loop).
"""The gate decides whether an iteration is accepted, so its refusals are the
safety property. These tests pin the refusals, not the happy path."""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from scripts import acceptance  # noqa: E402
from zeus.orchestration.swarm import config as swcfg  # noqa: E402


# ---- the loop cannot edit its own instrument ------------------------------


@pytest.mark.parametrize(
    "path",
    [
        "scripts/acceptance.py",
        "zeus/memory/eval_suite.py",
        "tests/retrieval_eval_queries/knowledge_questions.yaml",
        "tests/retrieval_eval_baseline.json",
        "pytest.ini",
        "zeus/safety/policies/swarm.yaml",
        "zeus/orchestration/swarm/coordinator.py",
    ],
)
def test_instrument_paths_are_denied(path):
    assert swcfg.path_denied(path), f"{path} must stay off-limits to a worker diff"


@pytest.mark.parametrize(
    "path",
    ["zeus/memory/library.py", "zeus/core/query.py", "tests/test_library.py"],
)
def test_subject_paths_remain_editable(path):
    """The agent must still be able to change the code it is being scored on, and
    to add tests. Edits to existing tests are neutralised by the frozen suite, not
    by the denylist."""
    assert not swcfg.path_denied(path)


# ---- scope confinement ----------------------------------------------------


def test_diff_outside_ratchet_paths_is_out_of_scope():
    assert not any(acceptance.in_scope(["README.md", "docs/thing.md"]).values())


def test_diff_touching_memory_is_in_retrieval_scope():
    assert acceptance.in_scope(["zeus/memory/library.py"])["retrieval"]


def test_tool_use_is_a_guard_not_a_ratchet():
    """Its baseline is saturated (1.0 / 0.0), so as a ratchet it could never fire.
    Promoting it needs headroom AND a suite big enough for the noise floor."""
    assert "tool_use" not in acceptance.RATCHET_PATHS
    assert "tool_use" in acceptance.GUARD_PATHS
    guards = acceptance.in_scope(["zeus/core/tools/loop.py"], acceptance.GUARD_PATHS)
    assert guards["tool_use"]
    assert not any(acceptance.in_scope(["zeus/core/tools/loop.py"]).values())


def test_false_positive_rate_direction_is_inverted(monkeypatch):
    """Down is better. Treating it like accuracy would read every improvement as a
    regression and every regression as an improvement."""
    monkeypatch.setenv("ZEUS_ACCEPTANCE_TOLERANCE", "0.05")
    regs, imps = acceptance._compare(
        {"false_positive_rate": 0.30}, {"false_positive_rate": 0.10},
        ["false_positive_rate"], label="tool_use",
    )
    assert regs and not imps
    regs2, imps2 = acceptance._compare(
        {"false_positive_rate": 0.02}, {"false_positive_rate": 0.20},
        ["false_positive_rate"], label="tool_use",
    )
    assert imps2 and not regs2


# ---- noise floor ----------------------------------------------------------


def test_delta_inside_tolerance_is_neither_regression_nor_improvement(monkeypatch):
    monkeypatch.setenv("ZEUS_ACCEPTANCE_TOLERANCE", "0.05")
    regs, imps = acceptance._compare(
        {"hit@5": 0.69}, {"hit@5": 0.667}, ["hit@5"], label="retrieval"
    )
    assert not regs and not imps, "a 2.3pp move on a 30-query suite is noise"


def test_real_regression_and_improvement_are_detected(monkeypatch):
    monkeypatch.setenv("ZEUS_ACCEPTANCE_TOLERANCE", "0.05")
    regs, _ = acceptance._compare({"hit@5": 0.50}, {"hit@5": 0.667}, ["hit@5"], label="r")
    assert regs
    _, imps = acceptance._compare({"hit@5": 0.80}, {"hit@5": 0.667}, ["hit@5"], label="r")
    assert imps


# ---- baseline integrity ---------------------------------------------------


def test_flat_shape_baseline_is_a_hard_failure(tmp_path):
    """Silently comparing against a pre-scorer baseline is worse than refusing."""
    p = tmp_path / "old.json"
    p.write_text(json.dumps({"summary": {"hit@5": 0.867, "n_queries": 30}}))
    with pytest.raises(acceptance.Reject, match="flat-shape"):
        acceptance._load_baseline(p, kind="retrieval")


def test_missing_baseline_is_a_hard_failure(tmp_path):
    with pytest.raises(acceptance.Reject, match="rebaseline"):
        acceptance._load_baseline(tmp_path / "nope.json", kind="retrieval")


def test_current_shape_baseline_loads(tmp_path):
    p = tmp_path / "new.json"
    p.write_text(json.dumps({"summary": {"overall": {"hit@5": 0.6}, "per_layer": {}}}))
    assert acceptance._load_baseline(p, kind="retrieval")["overall"]["hit@5"] == 0.6


# ---- ratchet plumbing -----------------------------------------------------
# score_suite returns a (summary, per_query) TUPLE and is fail-open per query:
# unreachable services come back as N errored rows, not an exception. Both of
# those were assumed wrong once and only surfaced against live services.


def _suite_rows(n=30):
    return [
        {"query": f"q{i}", "expected_keywords": ["k"], "expected_layer": "knowledge",
         "suite": "s"}
        for i in range(n)
    ]


def test_ratchet_consumes_the_tuple_return(monkeypatch, tmp_path):
    base = tmp_path / "b.json"
    base.write_text(json.dumps({"summary": {
        "overall": {"hit@1": 0.1, "hit@5": 0.1, "hit@10": 0.1, "mrr@10": 0.1},
        "per_layer": {}}}))
    monkeypatch.setenv("ZEUS_ACCEPTANCE_RETRIEVAL_BASELINE", str(base))
    monkeypatch.setenv("ZEUS_ACCEPTANCE_TOLERANCE", "0.05")

    summary = {"overall": {"n_queries": 30, "n_scored": 30, "n_error": 0,
                           "hit@1": 0.6, "hit@5": 0.8, "hit@10": 0.9, "mrr@10": 0.7}}
    monkeypatch.setattr(acceptance, "_load_suite_and_score",
                        lambda: (_suite_rows(), summary))

    regs, imps, note = acceptance.ratchet_retrieval(Path("."))
    assert not regs and imps and "n_scored=30" in note


def test_errored_queries_are_a_reject_not_a_score(monkeypatch, tmp_path):
    """A total connectivity outage scores every query as `error`; reading that as
    a quality result is the worst failure this gate can have."""
    base = tmp_path / "b.json"
    base.write_text(json.dumps({"summary": {"overall": {"hit@5": 0.1}, "per_layer": {}}}))
    monkeypatch.setenv("ZEUS_ACCEPTANCE_RETRIEVAL_BASELINE", str(base))

    summary = {"overall": {"n_queries": 30, "n_scored": 0, "n_error": 30,
                           "hit@1": 0.0, "hit@5": 0.0, "hit@10": 0.0, "mrr@10": 0.0}}
    monkeypatch.setattr(acceptance, "_load_suite_and_score",
                        lambda: (_suite_rows(), summary))

    with pytest.raises(acceptance.Reject, match="errored"):
        acceptance.ratchet_retrieval(Path("."))


def test_undersized_suite_is_rejected(monkeypatch):
    monkeypatch.setenv("ZEUS_ACCEPTANCE_MIN_SUITE", "30")
    monkeypatch.setattr(acceptance, "_load_suite_and_score",
                        lambda: (_suite_rows(5), {"overall": {}}))
    with pytest.raises(acceptance.Reject, match="noise floor"):
        acceptance.ratchet_retrieval(Path("."))


def test_tool_use_refuses_cross_provider_comparison(monkeypatch, tmp_path):
    """selection_accuracy is a property of the model as much as the code; diffing a
    qwen number against a Claude number manufactures signal out of nothing."""
    base = tmp_path / "tu.json"
    base.write_text(json.dumps({"summary": {
        "selection_accuracy": 1.0, "false_positive_rate": 0.0, "answer_hit_rate": 1.0,
        "config": {"provider": "ollama", "model": "qwen2.5:7b-instruct-q4_K_M"}}}))
    monkeypatch.setenv("ZEUS_ACCEPTANCE_TOOL_USE_BASELINE", str(base))
    monkeypatch.setattr(acceptance, "_run_tool_eval", lambda: {
        "n_errors": 0, "n_cases": 17, "selection_accuracy": 1.0,
        "false_positive_rate": 0.0, "answer_hit_rate": 1.0,
        "config": {"provider": "claude", "model": "claude-sonnet-5"}})

    with pytest.raises(acceptance.Reject, match="not comparable"):
        acceptance.guard_tool_use(Path("."))


def test_tool_use_guard_passes_when_flat(monkeypatch, tmp_path):
    base = tmp_path / "tu.json"
    base.write_text(json.dumps({"summary": {
        "selection_accuracy": 1.0, "false_positive_rate": 0.0, "answer_hit_rate": 1.0,
        "config": {"provider": "ollama", "model": "m"}}}))
    monkeypatch.setenv("ZEUS_ACCEPTANCE_TOOL_USE_BASELINE", str(base))
    monkeypatch.setattr(acceptance, "_run_tool_eval", lambda: {
        "n_errors": 0, "n_cases": 17, "selection_accuracy": 1.0,
        "false_positive_rate": 0.0, "answer_hit_rate": 1.0,
        "config": {"provider": "ollama", "model": "m"}})
    assert "no regression" in acceptance.guard_tool_use(Path("."))


def test_tool_use_guard_rejects_a_real_regression(monkeypatch, tmp_path):
    base = tmp_path / "tu.json"
    base.write_text(json.dumps({"summary": {
        "selection_accuracy": 1.0, "false_positive_rate": 0.0, "answer_hit_rate": 1.0,
        "config": {"provider": "ollama", "model": "m"}}}))
    monkeypatch.setenv("ZEUS_ACCEPTANCE_TOOL_USE_BASELINE", str(base))
    monkeypatch.setattr(acceptance, "_run_tool_eval", lambda: {
        "n_errors": 0, "n_cases": 17, "selection_accuracy": 0.7,
        "false_positive_rate": 0.4, "answer_hit_rate": 1.0,
        "config": {"provider": "ollama", "model": "m"}})
    with pytest.raises(acceptance.Reject, match="tool-use regression"):
        acceptance.guard_tool_use(Path("."))


def test_retrieval_refuses_mismatched_config(monkeypatch, tmp_path):
    """Observed for real: with the deployed env missing, a no-op comment scored
    hit@5 0.03 against a 0.61 baseline. Comparing across config manufactures a
    catastrophic-looking regression that has nothing to do with the change."""
    base = tmp_path / "b.json"
    base.write_text(json.dumps({"summary": {
        "overall": {"hit@1": 0.5, "hit@5": 0.6, "hit@10": 0.7, "mrr@10": 0.55},
        "per_layer": {},
        "config": {"ZEUS_KNOWLEDGE_HYBRID": "1", "ZEUS_KNOWLEDGE_RERANK": "0",
                   "ZEUS_EMBED_MODEL": "nomic-embed-text:v1.5"}}}))
    monkeypatch.setenv("ZEUS_ACCEPTANCE_RETRIEVAL_BASELINE", str(base))

    summary = {
        "overall": {"n_queries": 33, "n_scored": 33, "n_error": 0,
                    "hit@1": 0.03, "hit@5": 0.03, "hit@10": 0.03, "mrr@10": 0.03},
        "config": {"ZEUS_KNOWLEDGE_HYBRID": "1", "ZEUS_KNOWLEDGE_RERANK": "1",
                   "ZEUS_EMBED_MODEL": "nomic-embed-text"},
    }
    monkeypatch.setattr(acceptance, "_load_suite_and_score",
                        lambda: (_suite_rows(33), summary))

    with pytest.raises(acceptance.Reject, match="not comparable"):
        acceptance.ratchet_retrieval(Path("."))
