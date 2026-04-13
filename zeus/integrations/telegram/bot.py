# zeus/integrations/telegram/bot.py — Iris Telegram bridge (LAB-291)
from __future__ import annotations

import logging
import os
from typing import Iterable

from telegram import Update
from telegram.constants import ChatAction
from telegram.ext import (
    Application,
    ApplicationBuilder,
    ContextTypes,
    MessageHandler,
    filters,
)

from zeus.core.query import QueryEngine
from zeus.safety.policy_engine import aegis_enabled, evaluate_text

logger = logging.getLogger("zeus.telegram")

_TELEGRAM_MAX_LEN = 4096


def _parse_chat_ids(raw: str | None) -> set[int]:
    if not raw:
        return set()
    out: set[int] = set()
    for part in raw.replace("\n", ",").split(","):
        cleaned = part.strip()
        if not cleaned:
            continue
        try:
            out.add(int(cleaned))
        except ValueError:
            logger.warning("ignoring invalid telegram chat id: %s", cleaned)
    return out


class TelegramBot:
    """Long-polling Telegram bridge that routes messages into a Zeus session."""

    def __init__(
        self,
        token: str,
        query_engine: QueryEngine,
        *,
        allowed_chat_ids: Iterable[int] = (),
        policy_name: str | None = None,
    ) -> None:
        self._token = token
        self._qe = query_engine
        self._allowed: set[int] = set(allowed_chat_ids)
        self._policy = policy_name
        self._application: Application | None = None
        self._bot_username: str | None = None

    @property
    def bot_username(self) -> str | None:
        return self._bot_username

    @property
    def chat_count(self) -> int:
        return len(self._allowed)

    @property
    def running(self) -> bool:
        app = self._application
        return app is not None and bool(getattr(app, "running", False))

    async def start(self) -> None:
        application = ApplicationBuilder().token(self._token).build()
        application.add_handler(
            MessageHandler(filters.TEXT & ~filters.COMMAND, self._on_message)
        )
        await application.initialize()
        await application.start()
        if application.updater is None:
            raise RuntimeError("telegram Application has no Updater")
        await application.updater.start_polling(drop_pending_updates=True)
        me = await application.bot.get_me()
        self._bot_username = me.username
        self._application = application
        logger.info(
            "telegram bot started as @%s (%d allowed chats)",
            me.username,
            len(self._allowed),
        )

    async def stop(self) -> None:
        app = self._application
        if app is None:
            return
        try:
            if app.updater is not None and app.updater.running:
                await app.updater.stop()
            if app.running:
                await app.stop()
            await app.shutdown()
        finally:
            self._application = None

    async def _on_message(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ) -> None:
        msg = update.effective_message
        chat = update.effective_chat
        if msg is None or chat is None or not msg.text:
            return
        if self._allowed and chat.id not in self._allowed:
            logger.info("dropping telegram message from disallowed chat %s", chat.id)
            return

        session_id = f"telegram:{chat.id}"
        await self._qe.sessions.get_or_create(
            session_id,
            metadata={"source": "telegram", "telegram_chat_id": chat.id},
        )

        try:
            await context.bot.send_chat_action(chat_id=chat.id, action=ChatAction.TYPING)
        except Exception:
            pass

        try:
            result = await self._qe.query(
                msg.text,
                session_id=session_id,
                use_context=True,
                max_tokens=512,
                source="telegram",
            )
            reply = result.assistant_message or ""
        except Exception as exc:
            logger.exception("telegram query failed: %s", exc)
            await msg.reply_text("Sorry, something went wrong handling that message.")
            return

        if aegis_enabled():
            outcome = evaluate_text(reply, self._policy)
            if outcome.status != "ok":
                logger.warning(
                    "aegis blocked telegram reply for chat %s (flags=%s)",
                    chat.id,
                    outcome.flags,
                )
                reply = "My response was filtered by Aegis safety policy."

        if not reply:
            reply = "(no response)"

        try:
            await msg.reply_text(reply[:_TELEGRAM_MAX_LEN])
        except Exception as exc:
            logger.exception("failed sending telegram reply: %s", exc)


def build_telegram_bot(query_engine: QueryEngine) -> TelegramBot | None:
    """Construct a TelegramBot from env if enabled, else return None."""
    enabled = os.getenv("TELEGRAM_ENABLED", "0").strip().lower() in ("1", "true", "yes")
    if not enabled:
        return None
    token = os.getenv("TELEGRAM_BOT_TOKEN", "").strip()
    if not token:
        logger.warning("TELEGRAM_ENABLED set but TELEGRAM_BOT_TOKEN is empty")
        return None
    allowed = _parse_chat_ids(os.getenv("TELEGRAM_ALLOWED_CHAT_IDS"))
    policy = (
        os.getenv("TELEGRAM_AEGIS_POLICY")
        or os.getenv("ZEUS_AEGIS_POLICY")
        or None
    )
    return TelegramBot(
        token,
        query_engine,
        allowed_chat_ids=allowed,
        policy_name=policy,
    )
