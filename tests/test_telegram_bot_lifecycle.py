# tests/test_telegram_bot_lifecycle.py
"""Start/stop lifecycle guards for the Telegram bridge.

Both cases below leak a live getUpdates poller that stop() cannot reach, which
surfaces as 'Conflict: terminated by other getUpdates request' against a token
that only one deployment is supposedly using.
"""

from __future__ import annotations

import asyncio
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from zeus.integrations.telegram.bot import TelegramBot


def _fake_application() -> MagicMock:
    app = MagicMock()
    app.initialize = AsyncMock()
    app.start = AsyncMock()
    app.stop = AsyncMock()
    app.shutdown = AsyncMock()
    app.running = True
    app.updater = MagicMock()
    app.updater.running = True
    app.updater.start_polling = AsyncMock()
    app.updater.stop = AsyncMock()
    app.bot.get_me = AsyncMock(return_value=MagicMock(username="zeus_homelab_bot"))
    app.add_handler = MagicMock()
    return app


def _patch_builder(apps: list[MagicMock]):
    """Hand out a fresh Application per build() so leaks are countable."""
    builder = MagicMock()
    builder.token.return_value = builder
    builder.build.side_effect = apps
    return patch(
        "zeus.integrations.telegram.bot.ApplicationBuilder", return_value=builder
    )


def _bot() -> TelegramBot:
    return TelegramBot("123:ABC", MagicMock(), allowed_chat_ids=[42])


def test_double_start_does_not_open_a_second_poller() -> None:
    first, second = _fake_application(), _fake_application()
    bot = _bot()

    async def scenario() -> None:
        with _patch_builder([first, second]):
            await bot.start()
            await bot.start()  # e.g. two restart calls racing
        await bot.stop()

    asyncio.run(scenario())

    first.updater.start_polling.assert_awaited_once()
    second.updater.start_polling.assert_not_awaited()
    # stop() must reach the one poller that is actually running.
    first.updater.stop.assert_awaited_once()


def test_get_me_failure_tears_down_the_poller() -> None:
    app = _fake_application()
    app.bot.get_me = AsyncMock(side_effect=RuntimeError("network blip"))
    bot = _bot()

    async def scenario() -> None:
        with _patch_builder([app]):
            with pytest.raises(RuntimeError):
                await bot.start()

    asyncio.run(scenario())

    # Polling started, so it must be stopped rather than left orphaned.
    app.updater.start_polling.assert_awaited_once()
    app.updater.stop.assert_awaited_once()
    app.shutdown.assert_awaited_once()
    assert bot._application is None
