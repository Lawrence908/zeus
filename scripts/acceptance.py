#!/usr/bin/env python3
# scripts/acceptance.py
"""Acceptance gate for the Argo self-improvement loop.

Wired as the swarm's run-level project check (`ZEUS_SWARM_PROJECT_CHECK`), so it
runs once on the assembled integration branch and decides whether an iteration is
accepted. Exit 0 = accept, non-zero = reject.

Two kinds of signal, and the distinction is the whole design:

- GUARDS prove the change broke nothing. They can only ever return "no worse", so
  a loop built from guards alone accepts neutral churn forever: the agent rewrites
  things sideways, every gate passes, nothing improves.
- RATCHETS must actually move up for the change to be accepted. Zeus has exactly
  two today (retrieval eval, tool-use eval), so the loop is deliberately confined
  to the subsystems those measure. A diff touching nothing measurable is rejected
  as out of scope rather than waved through on guards.

Anti-gaming rules, both load-bearing:

1. The frozen suite is extracted from the baseline ref, NOT read from the
   worktree. An agent that edits an existing test cannot change its own score,
   because the score never reads its copy. New test files it adds still run in
   the ordinary suite; they just can't loosen an existing assertion.
2. This file, the eval harness, the query suites, and the baseline artifacts are
   all on the swarm path denylist. The loop may PROPOSE a new baseline; promoting
   one is a separate human commit. A process that can write the number it is
   compared against is not measuring anything.

The baseline shape is checked, not coerced: an old flat-shape baseline is a hard
failure with an explicit message, because silently comparing against the wrong
record is worse than refusing to run.
"""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any

REPO = Path(__file__).resolve().parent.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

# Diffs must touch at least one of these to be in scope: they are the paths whose
# quality a ratchet can actually measure. Widening this without adding a matching
# ratchet re-opens the neutral-churn hole.
RATCHET_PATHS = {
    "retrieval": ("zeus/memory/", "zeus/core/query.py"),
    "tool_use": ("zeus/core/tools/",),
}

# Rates below this delta are noise, not signal. Themis learned the hard way that
# 5pp on a 30-query suite is ~1.5 queries, under run-to-run variance.
DEFAULT_TOLERANCE = 0.05
DEFAULT_MIN_SUITE = 30


class Reject(Exception):
    """A gate refused the change. The message is fed back to the worker."""


def _run(
    cmd: list[str], *, cwd: Path, timeout: int = 900, env: dict[str, str] | None = None
) -> tuple[int, str]:
    proc = subprocess.run(
        cmd, cwd=str(cwd), capture_output=True, text=True, timeout=timeout,
        env={**os.environ, **(env or {})},
    )
    return proc.returncode, (proc.stdout + proc.stderr)[-4000:]


def _env(name: str, default: str) -> str:
    return os.getenv(name, default).strip() or default


def baseline_ref() -> str:
    return _env("ZEUS_ACCEPTANCE_BASELINE_REF", "origin/main")


def tolerance() -> float:
    return float(_env("ZEUS_ACCEPTANCE_TOLERANCE", str(DEFAULT_TOLERANCE)))


def changed_paths(repo: Path, ref: str) -> list[str]:
    rc, out = _run(["git", "diff", "--name-only", f"{ref}...HEAD"], cwd=repo)
    if rc != 0:
        raise Reject(f"cannot diff against baseline ref {ref!r}: {out}")
    return [p for p in out.splitlines() if p.strip()]


def in_scope(paths: list[str]) -> dict[str, bool]:
    """Which ratchets this diff is required to satisfy."""
    return {
        name: any(p.startswith(prefixes) for p in paths)
        for name, prefixes in RATCHET_PATHS.items()
    }


# --------------------------------------------------------------------------
# Guards
# --------------------------------------------------------------------------


def guard_diff_hygiene(repo: Path, paths: list[str]) -> str:
    """Re-check the denylist here as well as in the coordinator.

    The coordinator enforces it per node; this catches anything that reached the
    integration branch by another route (a merge, a rebase redo). Cheap, and the
    failure it prevents is the loop editing its own instrument.
    """
    from zeus.orchestration.swarm import config as swcfg

    denied = swcfg.denied_paths(paths)
    if denied:
        raise Reject(f"diff touches denied paths: {', '.join(sorted(denied))}")

    cap = int(_env("ZEUS_ACCEPTANCE_MAX_FILES", "60"))
    if len(paths) > cap:
        raise Reject(f"diff touches {len(paths)} files, over the {cap}-file cap")
    return f"{len(paths)} files, none denied"


def guard_lint(repo: Path) -> str:
    # `python -m`, never .venv/bin/*: a swarm worktree checks out tracked files
    # only, so .venv does not exist there. The interpreter running this script is
    # the one with the deps, whether that is the host venv or the verify image.
    rc, out = _run([sys.executable, "-m", "ruff", "check", "."], cwd=repo, timeout=300)
    if rc != 0:
        raise Reject(f"ruff failed:\n{out}")
    return "ruff clean"


def guard_frozen_suite(repo: Path, ref: str) -> str:
    """Run the baseline ref's test suite against the worktree's code.

    `git archive` the baseline `tests/` into a temp dir and point pytest at it.
    pythonpath=. in pytest.ini resolves relative to the rootdir (the worktree), so
    the tests are the baseline's but the `zeus` package under test is the agent's.
    """
    tmp = Path(tempfile.mkdtemp(prefix="acceptance-frozen-"))
    try:
        archive = subprocess.run(
            ["git", "archive", ref, "tests/"],
            cwd=str(repo), capture_output=True, timeout=120,
        )
        if archive.returncode != 0:
            raise Reject(
                f"cannot extract frozen suite from {ref!r}: "
                f"{archive.stderr.decode(errors='replace')[-800:]}"
            )
        subprocess.run(["tar", "-x", "-C", str(tmp)], input=archive.stdout, check=True)

        rc, out = _run(
            [
                sys.executable, "-m", "pytest", str(tmp / "tests"), "-q", "--no-header",
                "--no-cov", "-p", "no:cacheprovider",
            ],
            cwd=repo, timeout=1800,
        )
        if rc != 0:
            raise Reject(f"frozen suite from {ref} fails against this change:\n{out}")
        return out.strip().splitlines()[-1] if out.strip() else "passed"
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def guard_imports(repo: Path) -> str:
    """Importing zeus.core.main has filesystem side effects.

    `zeus/core/comfyui.py:images_dir()` mkdirs ZEUS_IMAGES_DIR at import time, and
    its default is the absolute `/app/zeus/data/images` - a path that exists in the
    zeus-core image but not in the verify sandbox. Left alone, this guard fails on
    the container's layout rather than on the change, which is the false signal the
    whole gate exists to avoid. Point it at a scratch dir so the guard measures
    importability and nothing else.
    """
    with tempfile.TemporaryDirectory(prefix="acceptance-images-") as scratch:
        rc, out = _run(
            [sys.executable, "-c", "import zeus.core.main"],
            cwd=repo, timeout=180, env={"ZEUS_IMAGES_DIR": scratch},
        )
    if rc != 0:
        raise Reject(f"zeus.core.main does not import:\n{out}")
    return "imports clean"


# --------------------------------------------------------------------------
# Ratchets
# --------------------------------------------------------------------------


def _load_baseline(path: Path, *, kind: str) -> dict[str, Any]:
    if not path.exists():
        raise Reject(f"{kind} baseline missing at {path}; rebaseline before running the loop")
    data = json.loads(path.read_text())
    summary = data.get("summary", data)
    if kind == "retrieval" and "per_layer" not in summary:
        raise Reject(
            f"{path} is the old flat-shape baseline (no per_layer). It predates the "
            "current scorer and cannot be compared against. Rebaseline first: this is "
            "a deliberate hard failure, not a fallback."
        )
    return summary


def _compare(
    current: dict[str, Any], base: dict[str, Any], metrics: list[str], *, label: str
) -> tuple[list[str], list[str]]:
    """Return (regressions, improvements) beyond the noise floor."""
    tol = tolerance()
    regressions: list[str] = []
    improvements: list[str] = []
    for m in metrics:
        if m not in current or m not in base:
            continue
        delta = float(current[m]) - float(base[m])
        if delta < -tol:
            regressions.append(f"{label}.{m} {base[m]:.4f} -> {current[m]:.4f} ({delta:+.4f})")
        elif delta > tol:
            improvements.append(f"{label}.{m} {base[m]:.4f} -> {current[m]:.4f} ({delta:+.4f})")
    return regressions, improvements


def ratchet_retrieval(repo: Path) -> tuple[list[str], list[str], str]:
    """Score the retrieval suite live and compare to the promoted baseline.

    Needs Qdrant + Ollama. Unreachable services are a hard failure, never a skip:
    a skipped ratchet silently degrades the loop back to guards-only.
    """
    from zeus.memory.eval_suite import load_suite, score_suite

    suite = load_suite()
    min_n = int(_env("ZEUS_ACCEPTANCE_MIN_SUITE", str(DEFAULT_MIN_SUITE)))
    if len(suite) < min_n:
        raise Reject(
            f"retrieval suite has {len(suite)} queries, under the {min_n} minimum; "
            "the noise floor would swamp the signal"
        )

    try:
        report = score_suite(suite)
    except Exception as exc:  # noqa: BLE001 - surfaced as a reject, not swallowed
        raise Reject(f"retrieval eval could not run (Qdrant/Ollama reachable?): {exc}") from exc

    summary = report["summary"]
    overall = summary["overall"]
    if overall.get("n_error", 0) > 0:
        raise Reject(
            f"retrieval eval had {overall['n_error']} errored queries; "
            "a scoring bug must not be read as a quality change"
        )

    base = _load_baseline(
        Path(_env("ZEUS_ACCEPTANCE_RETRIEVAL_BASELINE", "tests/retrieval_eval_baseline.json")),
        kind="retrieval",
    )
    regs, imps = _compare(
        overall, base["overall"], ["hit@1", "hit@5", "hit@10", "mrr@10"], label="retrieval"
    )
    note = f"n_scored={overall['n_scored']} hit@5={overall['hit@5']:.4f}"
    return regs, imps, note


def ratchet_tool_use(repo: Path) -> tuple[list[str], list[str], str]:
    """Tool-use eval is gated behind its own env flag and needs a live LLM path."""
    raise Reject(
        "tool_use ratchet not yet wired: tests/tool_use_eval.py needs a live provider "
        "and has no promoted baseline in this shape. Either wire it or remove "
        "zeus/core/tools/ from RATCHET_PATHS - do not leave it silently skipped."
    )


RATCHETS = {"retrieval": ratchet_retrieval, "tool_use": ratchet_tool_use}


# --------------------------------------------------------------------------


def main() -> int:
    repo = Path(os.getenv("ZEUS_ACCEPTANCE_REPO", str(REPO))).resolve()
    ref = baseline_ref()
    report: dict[str, Any] = {"baseline_ref": ref, "guards": {}, "ratchets": {}}

    try:
        paths = changed_paths(repo, ref)
        scope = in_scope(paths)
        report["changed_files"] = len(paths)
        report["scope"] = scope

        if not any(scope.values()):
            raise Reject(
                "diff touches no ratchet-measurable path "
                f"({', '.join(sorted(RATCHET_PATHS))}); out of confined scope. "
                "Accepting it would be neutral churn."
            )

        for name, gate in (
            ("diff_hygiene", lambda: guard_diff_hygiene(repo, paths)),
            ("lint", lambda: guard_lint(repo)),
            ("imports", lambda: guard_imports(repo)),
            ("frozen_suite", lambda: guard_frozen_suite(repo, ref)),
        ):
            report["guards"][name] = gate()

        all_regs: list[str] = []
        all_imps: list[str] = []
        for name, required in scope.items():
            if not required:
                continue
            regs, imps, note = RATCHETS[name](repo)
            report["ratchets"][name] = {"note": note, "regressions": regs, "improvements": imps}
            all_regs.extend(regs)
            all_imps.extend(imps)

        if all_regs:
            raise Reject("ratchet regression:\n  " + "\n  ".join(all_regs))
        if not all_imps:
            raise Reject(
                "no ratchet metric improved beyond the noise floor "
                f"(tolerance {tolerance():.3f}). Non-regressing is not the bar."
            )
        report["improvements"] = all_imps

    except Reject as exc:
        report["accepted"] = False
        report["reason"] = str(exc)
        print(json.dumps(report, indent=2))
        print(f"\nREJECTED: {exc}", file=sys.stderr)
        return 1

    report["accepted"] = True
    print(json.dumps(report, indent=2))
    print("\nACCEPTED: " + "; ".join(all_imps))
    return 0


if __name__ == "__main__":
    sys.exit(main())
