# tests/test_session_storage.py — SQLiteSessionStorage tests (LAB-351)
from __future__ import annotations

import asyncio
import os
import tempfile
import time

import pytest

from zeus.core.session_storage import SQLiteSessionStorage
from zeus.core.sessions import Session, Turn


def _make_session(sid: str = "s1", updated_at: float | None = None) -> Session:
    now = updated_at or time.time()
    return Session(
        id=sid,
        created_at=now,
        updated_at=now,
        turns=[
            Turn(user="hello", assistant="hi there", timestamp=now, latency_ms=42),
        ],
        summary="test summary",
        topic="greeting",
    )


@pytest.fixture
def db_path(tmp_path):
    return str(tmp_path / "test_sessions.db")


@pytest.fixture
def storage(db_path):
    s = SQLiteSessionStorage(db_path)
    yield s
    s.close()


class TestSaveLoadRoundTrip:
    def test_save_and_load(self, storage):
        session = _make_session("rt1")

        async def _run():
            await storage.save(session)
            loaded = await storage.load("rt1")
            assert loaded is not None
            assert loaded.id == session.id
            assert loaded.topic == session.topic
            assert loaded.summary == session.summary
            assert len(loaded.turns) == 1
            assert loaded.turns[0].user == "hello"
            assert loaded.turns[0].assistant == "hi there"
            assert loaded.turns[0].latency_ms == 42
            assert loaded.created_at == session.created_at
            assert loaded.updated_at == session.updated_at

        asyncio.run(_run())

    def test_load_missing_returns_none(self, storage):
        async def _run():
            assert await storage.load("nonexistent") is None

        asyncio.run(_run())

    def test_save_overwrites(self, storage):
        s1 = _make_session("ow1")

        async def _run():
            await storage.save(s1)
            s1.topic = "updated topic"
            s1.updated_at = time.time() + 1
            await storage.save(s1)
            loaded = await storage.load("ow1")
            assert loaded is not None
            assert loaded.topic == "updated topic"

        asyncio.run(_run())


class TestListRecent:
    def test_ordering_and_limit(self, storage):
        now = time.time()
        s_old = _make_session("old", updated_at=now - 100)
        s_mid = _make_session("mid", updated_at=now - 50)
        s_new = _make_session("new", updated_at=now)

        async def _run():
            # Save in non-chronological order
            await storage.save(s_mid)
            await storage.save(s_old)
            await storage.save(s_new)

            recent = await storage.list_recent(2)
            assert len(recent) == 2
            assert recent[0].id == "new"
            assert recent[1].id == "mid"

            all_sessions = await storage.list_recent(10)
            assert len(all_sessions) == 3
            assert [s.id for s in all_sessions] == ["new", "mid", "old"]

        asyncio.run(_run())


class TestDelete:
    def test_delete_existing(self, storage):
        session = _make_session("del1")

        async def _run():
            await storage.save(session)
            result = await storage.delete("del1")
            assert result is True
            assert await storage.load("del1") is None

        asyncio.run(_run())

    def test_delete_nonexistent(self, storage):
        async def _run():
            result = await storage.delete("nope")
            assert result is False

        asyncio.run(_run())


class TestPersistenceAcrossInstances:
    def test_data_survives_reinstantiation(self, db_path):
        session = _make_session("persist1")

        async def _run():
            # First instance: save
            storage1 = SQLiteSessionStorage(db_path)
            await storage1.save(session)
            storage1.close()

            # Second instance: load from same file
            storage2 = SQLiteSessionStorage(db_path)
            loaded = await storage2.load("persist1")
            storage2.close()

            assert loaded is not None
            assert loaded.id == "persist1"
            assert loaded.topic == "greeting"
            assert len(loaded.turns) == 1

        asyncio.run(_run())
