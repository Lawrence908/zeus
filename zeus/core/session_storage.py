# zeus/core/session_storage.py — SQLite-backed session persistence (LAB-351)
from __future__ import annotations

import asyncio
import sqlite3
import time

from zeus.core.sessions import Session


class SQLiteSessionStorage:
    """Durable session storage using stdlib sqlite3.

    All blocking sqlite3 calls are dispatched via ``asyncio.to_thread`` so the
    event loop is never blocked.
    """

    def __init__(self, db_path: str) -> None:
        self._db_path = db_path
        self._conn = sqlite3.connect(db_path, check_same_thread=False)
        self._conn.execute("PRAGMA journal_mode=WAL")
        self._conn.execute(
            "CREATE TABLE IF NOT EXISTS sessions "
            "(id TEXT PRIMARY KEY, data TEXT NOT NULL, updated_at REAL NOT NULL)"
        )
        self._conn.commit()

    # -- SessionStorage Protocol ------------------------------------------------

    async def save(self, session: Session) -> None:
        data = session.model_dump_json()
        updated_at = session.updated_at
        await asyncio.to_thread(self._save_sync, session.id, data, updated_at)

    async def load(self, session_id: str) -> Session | None:
        return await asyncio.to_thread(self._load_sync, session_id)

    async def list_recent(self, limit: int) -> list[Session]:
        return await asyncio.to_thread(self._list_recent_sync, limit)

    async def delete(self, session_id: str) -> bool:
        return await asyncio.to_thread(self._delete_sync, session_id)

    # -- Synchronous helpers (run in thread) ------------------------------------

    def _save_sync(self, session_id: str, data: str, updated_at: float) -> None:
        self._conn.execute(
            "INSERT OR REPLACE INTO sessions (id, data, updated_at) VALUES (?, ?, ?)",
            (session_id, data, updated_at),
        )
        self._conn.commit()

    def _load_sync(self, session_id: str) -> Session | None:
        row = self._conn.execute(
            "SELECT data FROM sessions WHERE id = ?", (session_id,)
        ).fetchone()
        if row is None:
            return None
        return Session.model_validate_json(row[0])

    def _list_recent_sync(self, limit: int) -> list[Session]:
        rows = self._conn.execute(
            "SELECT data FROM sessions ORDER BY updated_at DESC LIMIT ?", (limit,)
        ).fetchall()
        return [Session.model_validate_json(r[0]) for r in rows]

    def _delete_sync(self, session_id: str) -> bool:
        cursor = self._conn.execute(
            "DELETE FROM sessions WHERE id = ?", (session_id,)
        )
        self._conn.commit()
        return cursor.rowcount > 0

    def close(self) -> None:
        self._conn.close()
