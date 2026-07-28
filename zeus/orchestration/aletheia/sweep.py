# zeus/orchestration/aletheia/sweep.py
"""The sweep: analyse documentation across observe roots, fail-open per document.

A sweep is a DAG with one node per document and no edges (docs are independent),
so a document that errors or times out marks itself ``incomplete`` and the sweep
continues; eleven of thirteen docs is worth eleven docs of value.

Per document the sweep runs two layers:
  1. Mechanical (always): extract backticked references, resolve each with the
     verifier. High precision, zero spend.
  2. Worker (optional, ``ZEUS_ALETHEIA_WORKER_ENABLED``): a read-only Claude Code
     process proposes further candidates, each re-checked by the same verifier.

Every reportable finding is screened through Aegis before it is persisted or
delivered - the observe scope is server-wide, so a finding must never carry a
secret from a config file into Telegram or the Knowledge layer.

Budget kill-switch is enforced at document boundaries (worker cost is only known
after a node completes), so a single runaway doc can overrun its slice but the
next doc will not start once the ceiling is hit.
"""

from __future__ import annotations

import logging
import os
import uuid

from pydantic import BaseModel

from zeus.orchestration.aletheia import config, verifier
from zeus.orchestration.aletheia.extract import extract_references
from zeus.orchestration.aletheia.models import (
    AletheiaRun,
    DocResult,
    DocStatus,
    Finding,
    RunMode,
    RunStatus,
    iso_week,
)
from zeus.orchestration.aletheia.store import AletheiaStore

logger = logging.getLogger("zeus.aletheia.sweep")

_SKIP_DIRS = {".git", "node_modules", "__pycache__", ".venv", "venv", "dist", "build", "_app"}


class SweepReport(BaseModel):
    run: AletheiaRun
    reportable: list[Finding] = []


def worker_enabled() -> bool:
    return os.getenv("ZEUS_ALETHEIA_WORKER_ENABLED", "0").strip().lower() in ("1", "true", "yes", "on")


def _aegis_ok(finding: Finding) -> bool:
    """Screen a finding's text through Aegis; reject drops it (never delivered)."""
    try:
        from zeus.safety.policy_engine import aegis_enabled, evaluate_text
        if not aegis_enabled():
            return True
        policy = os.getenv("ZEUS_ALETHEIA_AEGIS_POLICY", "standard").strip() or "standard"
        blob = f"{finding.claim}\n{finding.reference.target}\n{finding.evidence}"
        outcome = evaluate_text(blob, policy_name=policy)
        if outcome.status == "rejected":
            logger.warning(
                "aletheia: Aegis dropped finding doc=%s ref=%s flags=%s",
                finding.doc_path, finding.reference.target, outcome.flags,
            )
            return False
    except Exception as exc:  # screening failure must not leak an unscreened finding
        logger.warning("aletheia: Aegis screen error (%s); dropping finding", exc)
        return False
    return True


def discover_docs(
    mode: RunMode, changed_paths: list[str] | None = None
) -> list[tuple[str, str, str]]:
    """Return (abs_path, rel_path, root) for every doc in scope.

    Full sweep: every doc under every observe root. Incremental: docs that are
    themselves changed, plus docs that mention a changed path (cheap intersection
    proxy - a full reference-graph intersection is a later refinement).
    """
    changed_bases = {os.path.basename(p.rstrip("/")) for p in (changed_paths or [])}
    changed_norm = {p.lstrip("/") for p in (changed_paths or [])}
    out: list[tuple[str, str, str]] = []
    for root in config.observe_roots():
        for dirpath, dirnames, filenames in os.walk(root):
            dirnames[:] = [d for d in dirnames if d not in _SKIP_DIRS]
            for fn in filenames:
                ap = os.path.join(dirpath, fn)
                rel = os.path.relpath(ap, root)
                if not config.is_doc(rel) or config.path_excluded(rel):
                    continue
                if mode == RunMode.INCREMENTAL:
                    if not _doc_in_incremental_scope(ap, rel, changed_norm, changed_bases):
                        continue
                out.append((ap, rel, root))
    return out


def _doc_in_incremental_scope(
    ap: str, rel: str, changed_norm: set[str], changed_bases: set[str]
) -> bool:
    if rel in changed_norm:  # the doc itself changed
        return True
    if not changed_bases:
        return False
    try:
        with open(ap, encoding="utf-8", errors="replace") as f:
            text = f.read()
    except OSError:
        return False
    return any(base in text for base in changed_bases)


async def _analyse_doc(
    ap: str, rel: str, root: str, mode: RunMode, store: AletheiaStore, run: AletheiaRun
) -> tuple[DocResult, list[Finding]]:
    try:
        with open(ap, encoding="utf-8", errors="replace") as f:
            text = f.read()
    except OSError as exc:
        return DocResult(doc_path=rel, status=DocStatus.INCOMPLETE, error=str(exc)), []

    by_id: dict[str, Finding] = {}
    cost = 0.0

    # 1. mechanical path
    for ex in extract_references(text):
        f = verifier.finding_from_reference(ex, rel)
        if f.reportable:
            by_id[f.identity()] = f

    # 2. worker path (recall extension)
    if worker_enabled():
        try:
            from zeus.orchestration.aletheia.worker import AletheiaWorker
            wres = await AletheiaWorker(mode=mode.value).run(rel, root)
            cost += wres.cost_usd
            if wres.success:
                for cand in wres.findings:
                    vf = verifier.verify_finding(cand)
                    if vf.reportable and vf.identity() not in by_id:
                        by_id[vf.identity()] = vf
            else:
                logger.info("aletheia worker failed on %s: %s", rel, wres.error)
        except Exception as exc:
            logger.warning("aletheia worker error on %s: %s", rel, exc)

    # 3. screen + persist
    reportable: list[Finding] = []
    for f in by_id.values():
        if not _aegis_ok(f):
            continue
        await store.add_finding(run.id, run.iso_week, f)
        reportable.append(f)

    return DocResult(doc_path=rel, status=DocStatus.OK, findings=len(reportable), cost_usd=cost), reportable


async def run_sweep(
    store: AletheiaStore,
    *,
    mode: RunMode = RunMode.FULL,
    changed_paths: list[str] | None = None,
) -> SweepReport:
    run = AletheiaRun(
        id=uuid.uuid4().hex,
        mode=mode,
        iso_week=iso_week(),
        budget_usd=config.max_usd_per_run(mode.value),
    )
    await store.create_run(run)

    docs = discover_docs(mode, changed_paths)
    run.docs_total = len(docs)
    all_reportable: list[Finding] = []

    for ap, rel, root in docs:
        if run.cost_usd >= run.budget_usd:  # kill-switch at the doc boundary
            run.status = RunStatus.PAUSED_BUDGET
            logger.warning("aletheia: run %s paused, budget $%.2f reached", run.id, run.budget_usd)
            break
        result, reportable = await _analyse_doc(ap, rel, root, mode, store, run)
        run.cost_usd += result.cost_usd
        if result.status == DocStatus.OK:
            run.docs_complete += 1
        else:
            run.docs_incomplete += 1
        all_reportable.extend(reportable)
        run.findings_reportable = len(all_reportable)
        await store.update_run(run)

    if run.status != RunStatus.PAUSED_BUDGET:
        if run.docs_total == 0 or run.docs_complete == 0 and run.docs_incomplete > 0:
            run.status = RunStatus.FAILED if run.docs_incomplete else RunStatus.COMPLETED
        elif run.docs_incomplete > 0:
            run.status = RunStatus.COMPLETED_PARTIAL
        else:
            run.status = RunStatus.COMPLETED
    await store.update_run(run)

    logger.info(
        "aletheia sweep %s: mode=%s docs=%d/%d findings=%d cost=$%.3f status=%s",
        run.id, mode.value, run.docs_complete, run.docs_total,
        run.findings_reportable, run.cost_usd, run.status.value,
    )
    return SweepReport(run=run, reportable=all_reportable)
