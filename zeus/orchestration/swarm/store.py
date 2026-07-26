# zeus/orchestration/swarm/store.py
"""Durable run/task/approval store on stdlib sqlite3.

Mirrors zeus/kronos/storage.py: synchronous sqlite3 wrapped in
asyncio.to_thread, one connection per op, autocommit. Replaces the in-memory
task ring buffer for long-running swarm runs.
"""

from __future__ import annotations

import asyncio
import json
import sqlite3
import uuid
from datetime import datetime, timezone

from zeus.orchestration.swarm.models import (
    Approval,
    ApprovalKind,
    ApprovalState,
    NodeStatus,
    Run,
    RunSpec,
    RunStatus,
    RunView,
    TaskNode,
)


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


class SwarmStore:
    """SQLite-backed store for swarm runs, task nodes, and approval gates."""

    def __init__(self, db_path: str) -> None:
        self._db_path = db_path
        with self._connect() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS swarm_runs (
                    id           TEXT PRIMARY KEY,
                    goal         TEXT NOT NULL,
                    repo         TEXT NOT NULL,
                    status       TEXT NOT NULL,
                    budget_usd   REAL NOT NULL,
                    max_parallel INTEGER NOT NULL,
                    created_at   TEXT NOT NULL,
                    updated_at   TEXT NOT NULL
                )
                """
            )
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS swarm_nodes (
                    run_id            TEXT NOT NULL,
                    id                TEXT NOT NULL,
                    title             TEXT NOT NULL,
                    deps              TEXT NOT NULL,
                    acceptance        TEXT NOT NULL,
                    tool_scope        TEXT NOT NULL,
                    check_cmd         TEXT NOT NULL DEFAULT '',
                    requires_approval INTEGER NOT NULL,
                    max_attempts      INTEGER NOT NULL DEFAULT 1,
                    status            TEXT NOT NULL,
                    attempts          INTEGER NOT NULL,
                    worker_id         TEXT,
                    output            TEXT,
                    error             TEXT,
                    cost_usd          REAL NOT NULL DEFAULT 0,
                    session_id        TEXT,
                    updated_at        TEXT NOT NULL,
                    PRIMARY KEY (run_id, id)
                )
                """
            )
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS swarm_approvals (
                    id          TEXT PRIMARY KEY,
                    run_id      TEXT NOT NULL,
                    kind        TEXT NOT NULL,
                    node_id     TEXT,
                    state       TEXT NOT NULL,
                    created_at  TEXT NOT NULL,
                    resolved_at TEXT
                )
                """
            )

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self._db_path, isolation_level=None)
        conn.row_factory = sqlite3.Row
        return conn

    # ---- row <-> model ---------------------------------------------------

    @staticmethod
    def _run_from_row(r: sqlite3.Row) -> Run:
        return Run(
            id=r["id"],
            goal=r["goal"],
            repo=r["repo"],
            status=RunStatus(r["status"]),
            budget_usd=r["budget_usd"],
            max_parallel=r["max_parallel"],
            created_at=r["created_at"],
            updated_at=r["updated_at"],
        )

    @staticmethod
    def _node_from_row(r: sqlite3.Row) -> TaskNode:
        return TaskNode(
            run_id=r["run_id"],
            id=r["id"],
            title=r["title"],
            deps=json.loads(r["deps"]),
            acceptance=r["acceptance"],
            check=r["check_cmd"],
            tool_scope=json.loads(r["tool_scope"]),
            requires_approval=bool(r["requires_approval"]),
            max_attempts=r["max_attempts"],
            status=NodeStatus(r["status"]),
            attempts=r["attempts"],
            worker_id=r["worker_id"],
            output=r["output"],
            error=r["error"],
            cost_usd=r["cost_usd"],
            session_id=r["session_id"],
            updated_at=r["updated_at"],
        )

    @staticmethod
    def _approval_from_row(r: sqlite3.Row) -> Approval:
        return Approval(
            id=r["id"],
            run_id=r["run_id"],
            kind=ApprovalKind(r["kind"]),
            node_id=r["node_id"],
            state=ApprovalState(r["state"]),
            created_at=r["created_at"],
            resolved_at=r["resolved_at"],
        )

    # ---- create ----------------------------------------------------------

    async def create_run(self, spec: RunSpec) -> RunView:
        return await asyncio.to_thread(self._create_run_sync, spec)

    def _create_run_sync(self, spec: RunSpec) -> RunView:
        now = _now_iso()
        run = Run(
            id=uuid.uuid4().hex[:12],
            goal=spec.goal,
            repo=spec.repo,
            status=RunStatus.PENDING_PLAN_APPROVAL,
            budget_usd=spec.budget_usd,
            max_parallel=spec.max_parallel,
            created_at=now,
            updated_at=now,
        )
        with self._connect() as conn:
            conn.execute(
                "INSERT INTO swarm_runs (id, goal, repo, status, budget_usd, max_parallel, created_at, updated_at)"
                " VALUES (?,?,?,?,?,?,?,?)",
                (run.id, run.goal, run.repo, run.status.value, run.budget_usd, run.max_parallel, now, now),
            )
            for n in spec.nodes:
                # No deps -> ready immediately once the plan is approved; else blocked.
                status = NodeStatus.READY if not n.deps else NodeStatus.BLOCKED
                conn.execute(
                    "INSERT INTO swarm_nodes (run_id, id, title, deps, acceptance, tool_scope,"
                    " check_cmd, requires_approval, max_attempts, status, attempts, worker_id,"
                    " output, error, cost_usd, session_id, updated_at)"
                    " VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
                    (
                        run.id, n.id, n.title, json.dumps(n.deps), n.acceptance,
                        json.dumps(n.tool_scope), n.check, int(n.requires_approval), n.max_attempts,
                        status.value, 0, None, None, None, 0.0, None, now,
                    ),
                )
            # Gate 1: the plan itself must be approved before anything runs.
            conn.execute(
                "INSERT INTO swarm_approvals (id, run_id, kind, node_id, state, created_at, resolved_at)"
                " VALUES (?,?,?,?,?,?,?)",
                (uuid.uuid4().hex[:12], run.id, ApprovalKind.PLAN.value, None,
                 ApprovalState.PENDING.value, now, None),
            )
        return self._get_view_sync(run.id)  # type: ignore[return-value]

    # ---- read ------------------------------------------------------------

    async def get_view(self, run_id: str) -> RunView | None:
        return await asyncio.to_thread(self._get_view_sync, run_id)

    def _get_view_sync(self, run_id: str) -> RunView | None:
        with self._connect() as conn:
            rr = conn.execute("SELECT * FROM swarm_runs WHERE id = ?", (run_id,)).fetchone()
            if rr is None:
                return None
            nodes = [
                self._node_from_row(r)
                for r in conn.execute(
                    "SELECT * FROM swarm_nodes WHERE run_id = ? ORDER BY rowid", (run_id,)
                ).fetchall()
            ]
            approvals = [
                self._approval_from_row(r)
                for r in conn.execute(
                    "SELECT * FROM swarm_approvals WHERE run_id = ? ORDER BY rowid", (run_id,)
                ).fetchall()
            ]
        return RunView(run=self._run_from_row(rr), nodes=nodes, approvals=approvals)

    async def list_runs(self, *, limit: int = 50) -> list[Run]:
        return await asyncio.to_thread(self._list_runs_sync, limit)

    def _list_runs_sync(self, limit: int) -> list[Run]:
        with self._connect() as conn:
            rows = conn.execute(
                "SELECT * FROM swarm_runs ORDER BY created_at DESC LIMIT ?", (limit,)
            ).fetchall()
        return [self._run_from_row(r) for r in rows]

    # ---- mutate ----------------------------------------------------------

    async def set_run_status(self, run_id: str, status: RunStatus) -> None:
        await asyncio.to_thread(self._set_run_status_sync, run_id, status)

    def _set_run_status_sync(self, run_id: str, status: RunStatus) -> None:
        with self._connect() as conn:
            conn.execute(
                "UPDATE swarm_runs SET status = ?, updated_at = ? WHERE id = ?",
                (status.value, _now_iso(), run_id),
            )

    async def set_run_budget(self, run_id: str, budget_usd: float) -> None:
        await asyncio.to_thread(self._set_run_budget_sync, run_id, budget_usd)

    def _set_run_budget_sync(self, run_id: str, budget_usd: float) -> None:
        with self._connect() as conn:
            conn.execute(
                "UPDATE swarm_runs SET budget_usd = ?, updated_at = ? WHERE id = ?",
                (budget_usd, _now_iso(), run_id),
            )

    async def update_node(self, node: TaskNode) -> None:
        await asyncio.to_thread(self._update_node_sync, node)

    def _update_node_sync(self, node: TaskNode) -> None:
        with self._connect() as conn:
            conn.execute(
                "UPDATE swarm_nodes SET status = ?, attempts = ?, worker_id = ?, output = ?,"
                " error = ?, requires_approval = ?, cost_usd = ?, session_id = ?, updated_at = ?"
                " WHERE run_id = ? AND id = ?",
                (node.status.value, node.attempts, node.worker_id, node.output,
                 node.error, int(node.requires_approval), node.cost_usd, node.session_id,
                 _now_iso(), node.run_id, node.id),
            )

    async def create_approval(
        self, run_id: str, kind: ApprovalKind, node_id: str | None = None
    ) -> Approval:
        return await asyncio.to_thread(self._create_approval_sync, run_id, kind, node_id)

    def _create_approval_sync(
        self, run_id: str, kind: ApprovalKind, node_id: str | None
    ) -> Approval:
        ap = Approval(
            id=uuid.uuid4().hex[:12], run_id=run_id, kind=kind, node_id=node_id,
            state=ApprovalState.PENDING, created_at=_now_iso(), resolved_at=None,
        )
        with self._connect() as conn:
            conn.execute(
                "INSERT INTO swarm_approvals (id, run_id, kind, node_id, state, created_at, resolved_at)"
                " VALUES (?,?,?,?,?,?,?)",
                (ap.id, ap.run_id, ap.kind.value, ap.node_id, ap.state.value, ap.created_at, None),
            )
        return ap

    async def resolve_approval(self, approval_id: str, state: ApprovalState) -> Approval | None:
        return await asyncio.to_thread(self._resolve_approval_sync, approval_id, state)

    def _resolve_approval_sync(self, approval_id: str, state: ApprovalState) -> Approval | None:
        now = _now_iso()
        with self._connect() as conn:
            cur = conn.execute(
                "UPDATE swarm_approvals SET state = ?, resolved_at = ?"
                " WHERE id = ? AND state = ?",
                (state.value, now, approval_id, ApprovalState.PENDING.value),
            )
            if cur.rowcount == 0:
                return None
            row = conn.execute("SELECT * FROM swarm_approvals WHERE id = ?", (approval_id,)).fetchone()
        return self._approval_from_row(row) if row else None
