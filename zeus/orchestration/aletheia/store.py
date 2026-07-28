# zeus/orchestration/aletheia/store.py
"""Durable store for Aletheia runs and findings (stdlib sqlite3).

Mirrors zeus/orchestration/swarm/store.py: synchronous sqlite3 wrapped in
asyncio.to_thread, one connection per op, autocommit.

Findings are keyed by (run_id, identity) where identity is stable across runs
(hash of doc_path + reference target). That stability is what lets the weekly
digest distinguish *new* drift from drift *carried over* for weeks, and drift
that *disappeared* (a fix, reflected back). Only non-OK findings are stored;
OK references are counted transiently and never persisted.
"""

from __future__ import annotations

import asyncio
import sqlite3
from datetime import datetime, timedelta, timezone

from zeus.orchestration.aletheia.models import (
    AletheiaRun,
    Finding,
    FindingStatus,
    Reference,
    ReferenceKind,
    RunMode,
    RunStatus,
)


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


class AletheiaStore:
    def __init__(self, db_path: str) -> None:
        self._db_path = db_path
        with self._connect() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS aletheia_runs (
                    id                  TEXT PRIMARY KEY,
                    mode                TEXT NOT NULL,
                    status              TEXT NOT NULL,
                    iso_week            TEXT NOT NULL DEFAULT '',
                    budget_usd          REAL NOT NULL DEFAULT 0,
                    cost_usd            REAL NOT NULL DEFAULT 0,
                    docs_total          INTEGER NOT NULL DEFAULT 0,
                    docs_complete       INTEGER NOT NULL DEFAULT 0,
                    docs_incomplete     INTEGER NOT NULL DEFAULT 0,
                    findings_reportable INTEGER NOT NULL DEFAULT 0,
                    created_at          TEXT NOT NULL,
                    updated_at          TEXT NOT NULL
                )
                """
            )
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS aletheia_findings (
                    run_id          TEXT NOT NULL,
                    identity        TEXT NOT NULL,
                    iso_week        TEXT NOT NULL DEFAULT '',
                    doc_path        TEXT NOT NULL,
                    doc_line        INTEGER NOT NULL DEFAULT 0,
                    claim           TEXT NOT NULL DEFAULT '',
                    ref_kind        TEXT NOT NULL,
                    ref_target      TEXT NOT NULL,
                    status          TEXT NOT NULL,
                    evidence        TEXT NOT NULL DEFAULT '',
                    confidence      REAL NOT NULL DEFAULT 0,
                    verified        INTEGER NOT NULL DEFAULT 0,
                    verifier_status TEXT,
                    created_at      TEXT NOT NULL,
                    PRIMARY KEY (run_id, identity)
                )
                """
            )
            conn.execute(
                "CREATE INDEX IF NOT EXISTS idx_aletheia_findings_week "
                "ON aletheia_findings (iso_week, verified, status)"
            )

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self._db_path, isolation_level=None, timeout=30)
        conn.row_factory = sqlite3.Row
        return conn

    # -- runs -----------------------------------------------------------------

    async def create_run(self, run: AletheiaRun) -> None:
        await asyncio.to_thread(self._create_run, run)

    def _create_run(self, run: AletheiaRun) -> None:
        with self._connect() as conn:
            conn.execute(
                """INSERT INTO aletheia_runs
                   (id, mode, status, iso_week, budget_usd, cost_usd, docs_total,
                    docs_complete, docs_incomplete, findings_reportable, created_at, updated_at)
                   VALUES (?,?,?,?,?,?,?,?,?,?,?,?)""",
                (run.id, run.mode.value, run.status.value, run.iso_week, run.budget_usd,
                 run.cost_usd, run.docs_total, run.docs_complete, run.docs_incomplete,
                 run.findings_reportable, run.created_at, run.updated_at),
            )

    async def update_run(self, run: AletheiaRun) -> None:
        run.updated_at = _now_iso()
        await asyncio.to_thread(self._update_run, run)

    def _update_run(self, run: AletheiaRun) -> None:
        with self._connect() as conn:
            conn.execute(
                """UPDATE aletheia_runs SET status=?, iso_week=?, cost_usd=?, docs_total=?,
                   docs_complete=?, docs_incomplete=?, findings_reportable=?, updated_at=?
                   WHERE id=?""",
                (run.status.value, run.iso_week, run.cost_usd, run.docs_total,
                 run.docs_complete, run.docs_incomplete, run.findings_reportable,
                 run.updated_at, run.id),
            )

    async def get_run(self, run_id: str) -> AletheiaRun | None:
        return await asyncio.to_thread(self._get_run, run_id)

    def _get_run(self, run_id: str) -> AletheiaRun | None:
        with self._connect() as conn:
            row = conn.execute("SELECT * FROM aletheia_runs WHERE id=?", (run_id,)).fetchone()
        return _run_from_row(row) if row else None

    async def list_runs(self, *, limit: int = 50) -> list[AletheiaRun]:
        return await asyncio.to_thread(self._list_runs, limit)

    def _list_runs(self, limit: int) -> list[AletheiaRun]:
        with self._connect() as conn:
            rows = conn.execute(
                "SELECT * FROM aletheia_runs ORDER BY created_at DESC LIMIT ?", (limit,)
            ).fetchall()
        return [_run_from_row(r) for r in rows]

    # -- findings -------------------------------------------------------------

    async def add_finding(self, run_id: str, iso_week: str, finding: Finding) -> None:
        await asyncio.to_thread(self._add_finding, run_id, iso_week, finding)

    def _add_finding(self, run_id: str, iso_week: str, finding: Finding) -> None:
        with self._connect() as conn:
            conn.execute(
                """INSERT OR REPLACE INTO aletheia_findings
                   (run_id, identity, iso_week, doc_path, doc_line, claim, ref_kind,
                    ref_target, status, evidence, confidence, verified, verifier_status, created_at)
                   VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
                (run_id, finding.identity(), iso_week, finding.doc_path, finding.doc_line,
                 finding.claim, finding.reference.kind.value, finding.reference.target,
                 finding.status.value, finding.evidence, finding.confidence,
                 1 if finding.verified else 0,
                 finding.verifier_status.value if finding.verifier_status else None,
                 _now_iso()),
            )

    async def findings_for_week(
        self, iso_week: str, *, reportable_only: bool = True
    ) -> list[Finding]:
        """Latest finding per identity for a week (dedup across nightly re-runs)."""
        return await asyncio.to_thread(self._findings_for_week, iso_week, reportable_only)

    def _findings_for_week(self, iso_week: str, reportable_only: bool) -> list[Finding]:
        clause = "AND verified=1 AND status IN ('missing','moved','changed')" if reportable_only else ""
        with self._connect() as conn:
            rows = conn.execute(
                f"""SELECT * FROM aletheia_findings f
                    WHERE iso_week=? {clause}
                    AND created_at = (
                        SELECT MAX(created_at) FROM aletheia_findings
                        WHERE identity=f.identity AND iso_week=f.iso_week
                    )
                    GROUP BY identity
                    ORDER BY doc_path, doc_line""",
                (iso_week,),
            ).fetchall()
        return [_finding_from_row(r) for r in rows]

    async def identities_for_week(self, iso_week: str) -> set[str]:
        return await asyncio.to_thread(self._identities_for_week, iso_week)

    def _identities_for_week(self, iso_week: str) -> set[str]:
        with self._connect() as conn:
            rows = conn.execute(
                "SELECT DISTINCT identity FROM aletheia_findings "
                "WHERE iso_week=? AND verified=1 AND status IN ('missing','moved','changed')",
                (iso_week,),
            ).fetchall()
        return {r["identity"] for r in rows}

    async def prune(self, *, retention_days: int) -> int:
        return await asyncio.to_thread(self._prune, retention_days)

    def _prune(self, retention_days: int) -> int:
        cutoff = (datetime.now(timezone.utc) - timedelta(days=retention_days)).isoformat()
        with self._connect() as conn:
            cur = conn.execute("DELETE FROM aletheia_findings WHERE created_at < ?", (cutoff,))
            conn.execute("DELETE FROM aletheia_runs WHERE created_at < ?", (cutoff,))
            return cur.rowcount or 0


def _run_from_row(row: sqlite3.Row) -> AletheiaRun:
    return AletheiaRun(
        id=row["id"], mode=RunMode(row["mode"]), status=RunStatus(row["status"]),
        iso_week=row["iso_week"], budget_usd=row["budget_usd"], cost_usd=row["cost_usd"],
        docs_total=row["docs_total"], docs_complete=row["docs_complete"],
        docs_incomplete=row["docs_incomplete"], findings_reportable=row["findings_reportable"],
        created_at=row["created_at"], updated_at=row["updated_at"],
    )


def _finding_from_row(row: sqlite3.Row) -> Finding:
    vs = row["verifier_status"]
    return Finding(
        doc_path=row["doc_path"], doc_line=row["doc_line"], claim=row["claim"],
        reference=Reference(kind=ReferenceKind(row["ref_kind"]), target=row["ref_target"]),
        status=FindingStatus(row["status"]), evidence=row["evidence"],
        confidence=row["confidence"], verified=bool(row["verified"]),
        verifier_status=FindingStatus(vs) if vs else None,
    )
