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
    scope = acceptance.in_scope(["zeus/memory/library.py"])
    assert scope["retrieval"] and not scope["tool_use"]


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
