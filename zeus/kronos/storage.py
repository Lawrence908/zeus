# zeus/kronos/storage.py — SQLite-backed job + run persistence for Kronos.
# Mirrors zeus/core/session_storage.py: stdlib sqlite3 inside asyncio.to_thread,
# one short-lived connection per call so no Connection object is shared across
# threads.
from __future__ import annotations

import asyncio
import sqlite3
import uuid
from datetime import datetime, timezone
from typing import Protocol

from zeus.kronos.models import JobDefinition, JobRun, JobStatus


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _iso_to_dt(s: str | None) -> datetime | None:
    if s is None:
        return None
    return datetime.fromisoformat(s)


class JobStorage(Protocol):
    async def upsert_job(self, job: JobDefinition) -> None: ...
    async def insert_if_absent(self, job: JobDefinition) -> bool: ...
    async def get_job(self, job_id: str) -> JobDefinition | None: ...
    async def list_jobs(self, *, enabled: bool | None = None) -> list[JobDefinition]: ...
    async def set_enabled(self, job_id: str, enabled: bool) -> bool: ...
    async def delete_job(self, job_id: str) -> bool: ...
    async def get_last_fired_at(self, job_id: str) -> datetime | None: ...

    async def claim_fire(
        self, job_id: str, now: datetime, correlation_id: str
    ) -> JobRun: ...
    async def finish_run(self, run: JobRun) -> None: ...
    async def reap_orphans(self, *, max_age_seconds: float) -> int: ...

    async def list_runs(
        self, *, job_id: str | None = None, status: JobStatus | None = None,
        since: datetime | None = None, limit: int = 50,
    ) -> list[JobRun]: ...
    async def get_run(self, run_id: str) -> JobRun | None: ...


class SQLiteJobStorage:
    """Durable job + run storage on stdlib sqlite3."""

    def __init__(self, db_path: str) -> None:
        self._db_path = db_path
        with self._connect() as conn:
            conn.execute("PRAGMA journal_mode=WAL")
            conn.execute("PRAGMA foreign_keys=ON")
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS jobs (
                    id TEXT PRIMARY KEY,
                    definition TEXT NOT NULL,
                    enabled INTEGER NOT NULL,
                    last_fired_at TEXT,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                )
                """
            )
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS job_runs (
                    id TEXT PRIMARY KEY,
                    job_id TEXT NOT NULL,
                    correlation_id TEXT NOT NULL,
                    status TEXT NOT NULL,
                    started_at TEXT NOT NULL,
                    finished_at TEXT,
                    duration_ms REAL,
                    output_summary TEXT,
                    error TEXT,
                    attempts INTEGER NOT NULL DEFAULT 1,
                    FOREIGN KEY(job_id) REFERENCES jobs(id) ON DELETE CASCADE
                )
                """
            )
            conn.execute(
                "CREATE INDEX IF NOT EXISTS idx_job_runs_job_started "
                "ON job_runs(job_id, started_at DESC)"
            )
            conn.execute(
                "CREATE INDEX IF NOT EXISTS idx_job_runs_status "
                "ON job_runs(status)"
            )
            conn.commit()

    def _connect(self) -> sqlite3.Connection:
        return sqlite3.connect(self._db_path, isolation_level=None)

    # -- Jobs -----------------------------------------------------------------

    async def upsert_job(self, job: JobDefinition) -> None:
        await asyncio.to_thread(self._upsert_job_sync, job)

    def _upsert_job_sync(self, job: JobDefinition) -> None:
        now = _now_iso()
        defn = job.model_dump_json()
        with self._connect() as conn:
            conn.execute("BEGIN")
            row = conn.execute("SELECT created_at FROM jobs WHERE id=?", (job.id,)).fetchone()
            created = row[0] if row else now
            conn.execute(
                "INSERT OR REPLACE INTO jobs "
                "(id, definition, enabled, last_fired_at, created_at, updated_at) "
                "VALUES (?, ?, ?, (SELECT last_fired_at FROM jobs WHERE id=?), ?, ?)",
                (job.id, defn, 1 if job.enabled else 0, job.id, created, now),
            )
            conn.execute("COMMIT")

    async def insert_if_absent(self, job: JobDefinition) -> bool:
        return await asyncio.to_thread(self._insert_if_absent_sync, job)

    def _insert_if_absent_sync(self, job: JobDefinition) -> bool:
        now = _now_iso()
        defn = job.model_dump_json()
        with self._connect() as conn:
            cur = conn.execute(
                "INSERT OR IGNORE INTO jobs "
                "(id, definition, enabled, last_fired_at, created_at, updated_at) "
                "VALUES (?, ?, ?, NULL, ?, ?)",
                (job.id, defn, 1 if job.enabled else 0, now, now),
            )
            return cur.rowcount > 0

    async def get_job(self, job_id: str) -> JobDefinition | None:
        return await asyncio.to_thread(self._get_job_sync, job_id)

    def _get_job_sync(self, job_id: str) -> JobDefinition | None:
        with self._connect() as conn:
            row = conn.execute(
                "SELECT definition, enabled FROM jobs WHERE id=?", (job_id,)
            ).fetchone()
        if row is None:
            return None
        defn = JobDefinition.model_validate_json(row[0])
        # Storage-level enabled overrides any stale value in the JSON payload.
        defn.enabled = bool(row[1])
        return defn

    async def list_jobs(self, *, enabled: bool | None = None) -> list[JobDefinition]:
        return await asyncio.to_thread(self._list_jobs_sync, enabled)

    def _list_jobs_sync(self, enabled: bool | None) -> list[JobDefinition]:
        query = "SELECT definition, enabled FROM jobs"
        params: tuple = ()
        if enabled is not None:
            query += " WHERE enabled=?"
            params = (1 if enabled else 0,)
        query += " ORDER BY id"
        with self._connect() as conn:
            rows = conn.execute(query, params).fetchall()
        out: list[JobDefinition] = []
        for defn_text, en in rows:
            defn = JobDefinition.model_validate_json(defn_text)
            defn.enabled = bool(en)
            out.append(defn)
        return out

    async def set_enabled(self, job_id: str, enabled: bool) -> bool:
        return await asyncio.to_thread(self._set_enabled_sync, job_id, enabled)

    def _set_enabled_sync(self, job_id: str, enabled: bool) -> bool:
        with self._connect() as conn:
            cur = conn.execute(
                "UPDATE jobs SET enabled=?, updated_at=? WHERE id=?",
                (1 if enabled else 0, _now_iso(), job_id),
            )
            return cur.rowcount > 0

    async def delete_job(self, job_id: str) -> bool:
        return await asyncio.to_thread(self._delete_job_sync, job_id)

    def _delete_job_sync(self, job_id: str) -> bool:
        with self._connect() as conn:
            cur = conn.execute("DELETE FROM jobs WHERE id=?", (job_id,))
            return cur.rowcount > 0

    async def get_last_fired_at(self, job_id: str) -> datetime | None:
        return await asyncio.to_thread(self._get_last_fired_at_sync, job_id)

    def _get_last_fired_at_sync(self, job_id: str) -> datetime | None:
        with self._connect() as conn:
            row = conn.execute(
                "SELECT last_fired_at, created_at FROM jobs WHERE id=?", (job_id,)
            ).fetchone()
        if row is None:
            return None
        return _iso_to_dt(row[0]) or _iso_to_dt(row[1])

    # -- Runs -----------------------------------------------------------------

    async def claim_fire(
        self, job_id: str, now: datetime, correlation_id: str
    ) -> JobRun:
        """
        Atomically record fire-intent and bump last_fired_at.

        Writes a PENDING JobRun row and updates jobs.last_fired_at in a single
        transaction. If the scheduler crashes mid-execute, reap_orphans() will
        find the PENDING row on the next boot and mark it LOST. Returns the
        newly-created JobRun.
        """
        return await asyncio.to_thread(self._claim_fire_sync, job_id, now, correlation_id)

    def _claim_fire_sync(self, job_id: str, now: datetime, correlation_id: str) -> JobRun:
        run = JobRun(
            id=uuid.uuid4().hex,
            job_id=job_id,
            correlation_id=correlation_id,
            status=JobStatus.PENDING,
            started_at=now,
        )
        with self._connect() as conn:
            conn.execute("BEGIN IMMEDIATE")
            conn.execute(
                "INSERT INTO job_runs "
                "(id, job_id, correlation_id, status, started_at, attempts) "
                "VALUES (?, ?, ?, ?, ?, 1)",
                (run.id, run.job_id, run.correlation_id, run.status.value,
                 run.started_at.isoformat()),
            )
            conn.execute(
                "UPDATE jobs SET last_fired_at=?, updated_at=? WHERE id=?",
                (now.isoformat(), _now_iso(), job_id),
            )
            conn.execute("COMMIT")
        return run

    async def finish_run(self, run: JobRun) -> None:
        await asyncio.to_thread(self._finish_run_sync, run)

    def _finish_run_sync(self, run: JobRun) -> None:
        with self._connect() as conn:
            conn.execute(
                "UPDATE job_runs SET status=?, finished_at=?, duration_ms=?, "
                "output_summary=?, error=?, attempts=? WHERE id=?",
                (
                    run.status.value,
                    run.finished_at.isoformat() if run.finished_at else None,
                    run.duration_ms,
                    run.output_summary,
                    run.error,
                    run.attempts,
                    run.id,
                ),
            )

    async def reap_orphans(self, *, max_age_seconds: float) -> int:
        """Mark any PENDING/RUNNING run older than max_age_seconds as LOST. Run on boot."""
        return await asyncio.to_thread(self._reap_orphans_sync, max_age_seconds)

    def _reap_orphans_sync(self, max_age_seconds: float) -> int:
        now = datetime.now(timezone.utc)
        cutoff = now.timestamp() - max_age_seconds
        cutoff_iso = datetime.fromtimestamp(cutoff, tz=timezone.utc).isoformat()
        with self._connect() as conn:
            cur = conn.execute(
                "UPDATE job_runs SET status=?, finished_at=?, "
                "error='scheduler restart; run never completed' "
                "WHERE status IN (?, ?) AND started_at < ?",
                (
                    JobStatus.LOST.value,
                    now.isoformat(),
                    JobStatus.PENDING.value,
                    JobStatus.RUNNING.value,
                    cutoff_iso,
                ),
            )
            return cur.rowcount

    async def list_runs(
        self, *, job_id: str | None = None, status: JobStatus | None = None,
        since: datetime | None = None, limit: int = 50,
    ) -> list[JobRun]:
        return await asyncio.to_thread(
            self._list_runs_sync, job_id, status, since, limit
        )

    def _list_runs_sync(
        self, job_id: str | None, status: JobStatus | None,
        since: datetime | None, limit: int,
    ) -> list[JobRun]:
        clauses: list[str] = []
        params: list = []
        if job_id is not None:
            clauses.append("job_id=?")
            params.append(job_id)
        if status is not None:
            clauses.append("status=?")
            params.append(status.value)
        if since is not None:
            clauses.append("started_at>=?")
            params.append(since.isoformat())
        where = (" WHERE " + " AND ".join(clauses)) if clauses else ""
        params.append(max(1, min(limit, 500)))
        with self._connect() as conn:
            rows = conn.execute(
                f"SELECT id, job_id, correlation_id, status, started_at, "
                f"finished_at, duration_ms, output_summary, error, attempts "
                f"FROM job_runs{where} ORDER BY started_at DESC LIMIT ?",
                tuple(params),
            ).fetchall()
        return [self._row_to_run(r) for r in rows]

    async def get_run(self, run_id: str) -> JobRun | None:
        return await asyncio.to_thread(self._get_run_sync, run_id)

    def _get_run_sync(self, run_id: str) -> JobRun | None:
        with self._connect() as conn:
            row = conn.execute(
                "SELECT id, job_id, correlation_id, status, started_at, "
                "finished_at, duration_ms, output_summary, error, attempts "
                "FROM job_runs WHERE id=?",
                (run_id,),
            ).fetchone()
        return self._row_to_run(row) if row else None

    @staticmethod
    def _row_to_run(row: tuple) -> JobRun:
        return JobRun(
            id=row[0],
            job_id=row[1],
            correlation_id=row[2],
            status=JobStatus(row[3]),
            started_at=_iso_to_dt(row[4]),  # type: ignore[arg-type]
            finished_at=_iso_to_dt(row[5]),
            duration_ms=row[6],
            output_summary=row[7],
            error=row[8],
            attempts=row[9],
        )

    def close(self) -> None:
        return None
