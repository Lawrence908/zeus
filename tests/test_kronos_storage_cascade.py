# tests/test_kronos_storage_cascade.py
"""Deleting a job must take its run history with it.

job_runs declares ON DELETE CASCADE, but sqlite's foreign_keys pragma is
per-connection and defaults OFF, so the constraint is inert unless every
connection opts in.
"""

from __future__ import annotations

import asyncio
import sqlite3

from zeus.kronos.storage import SQLiteJobStorage


def _seed_run(db_path: str, run_id: str, job_id: str) -> None:
    conn = sqlite3.connect(db_path, isolation_level=None)
    try:
        conn.execute(
            "INSERT INTO job_runs (id, job_id, correlation_id, status, started_at, attempts)"
            " VALUES (?, ?, ?, ?, ?, 1)",
            (run_id, job_id, "corr123", "SUCCESS", "2026-09-30T00:00:00+00:00"),
        )
    finally:
        conn.close()


def _count(db_path: str, sql: str) -> int:
    conn = sqlite3.connect(db_path)
    try:
        return conn.execute(sql).fetchone()[0]
    finally:
        conn.close()


def test_foreign_keys_enabled_on_every_connection(tmp_path) -> None:
    db = str(tmp_path / "kronos.db")
    store = SQLiteJobStorage(db)
    conn = store._connect()
    try:
        assert conn.execute("PRAGMA foreign_keys").fetchone()[0] == 1
    finally:
        conn.close()


def test_deleting_a_job_cascades_its_runs(tmp_path) -> None:
    db = str(tmp_path / "kronos.db")
    store = SQLiteJobStorage(db)

    conn = store._connect()
    try:
        conn.execute(
            "INSERT INTO jobs (id, definition, enabled, created_at, updated_at)"
            " VALUES ('doomed', '{}', 0, '2026-09-30', '2026-09-30')"
        )
        conn.execute(
            "INSERT INTO jobs (id, definition, enabled, created_at, updated_at)"
            " VALUES ('keeper', '{}', 1, '2026-09-30', '2026-09-30')"
        )
    finally:
        conn.close()

    _seed_run(db, "run-a", "doomed")
    _seed_run(db, "run-b", "doomed")
    _seed_run(db, "run-c", "keeper")

    assert asyncio.run(store.delete_job("doomed")) is True

    assert _count(db, "SELECT COUNT(*) FROM job_runs WHERE job_id='doomed'") == 0
    # An unrelated job's history must survive.
    assert _count(db, "SELECT COUNT(*) FROM job_runs WHERE job_id='keeper'") == 1
    assert (
        _count(db, "SELECT COUNT(*) FROM job_runs WHERE job_id NOT IN (SELECT id FROM jobs)")
        == 0
    )
