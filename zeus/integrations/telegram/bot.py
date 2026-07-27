# zeus/integrations/telegram/bot.py — Iris Telegram bridge (LAB-291)
from __future__ import annotations

import logging
import os
import re
from typing import Iterable

from telegram import Update
from telegram.constants import ChatAction
from telegram.ext import (
    Application,
    ApplicationBuilder,
    CallbackQueryHandler,
    ContextTypes,
    MessageHandler,
    filters,
)

from zeus.core.query import QueryEngine
from zeus.safety.policy_engine import aegis_enabled, evaluate_text

logger = logging.getLogger("zeus.telegram")
# Ensure our INFO logs are visible even when uvicorn's root level is WARNING.
if logger.level == logging.NOTSET:
    logger.setLevel(logging.INFO)

_TELEGRAM_MAX_LEN = 4096


_MD_CODE_FENCE = re.compile(r"```[\w+-]*\n?([\s\S]*?)```")
_MD_INLINE_CODE = re.compile(r"`([^`]+)`")
_MD_IMAGE = re.compile(r"!\[([^\]]*)\]\([^)]+\)")
_MD_LINK = re.compile(r"\[([^\]]+)\]\(([^)]+)\)")
_MD_BOLD = re.compile(r"\*\*([^*]+)\*\*|__([^_]+)__")
_MD_ITALIC = re.compile(r"(?<!\*)\*([^*\n]+)\*(?!\*)|(?<!_)_([^_\n]+)_(?!_)")
_MD_HEADER = re.compile(r"^\s{0,3}#{1,6}\s+", re.MULTILINE)
_MD_HR = re.compile(r"^\s*[-*_]{3,}\s*$", re.MULTILINE)
_MD_BLOCKQUOTE = re.compile(r"^\s{0,3}>\s?", re.MULTILINE)
_MD_LIST_MARKER = re.compile(r"^(\s*)[-*+]\s+", re.MULTILINE)
_TRAILING_WS = re.compile(r"[ \t]+$", re.MULTILINE)
_MULTI_BLANKS = re.compile(r"\n{3,}")


def markdown_to_plaintext(text: str) -> str:
    """Best-effort strip of common Markdown so a reply reads cleanly in Telegram.

    Telegram supports MarkdownV2 but it is strict and unescaped characters in
    LLM output frequently break the parser. Sending plain text is more robust.
    """
    if not text:
        return text
    text = _MD_CODE_FENCE.sub(lambda m: m.group(1), text)
    text = _MD_IMAGE.sub(r"\1", text)
    text = _MD_LINK.sub(r"\1 (\2)", text)
    text = _MD_INLINE_CODE.sub(r"\1", text)
    text = _MD_BOLD.sub(lambda m: m.group(1) or m.group(2) or "", text)
    text = _MD_ITALIC.sub(lambda m: m.group(1) or m.group(2) or "", text)
    text = _MD_HEADER.sub("", text)
    text = _MD_HR.sub("", text)
    text = _MD_BLOCKQUOTE.sub("", text)
    text = _MD_LIST_MARKER.sub(lambda m: f"{m.group(1)}• ", text)
    text = _TRAILING_WS.sub("", text)
    text = _MULTI_BLANKS.sub("\n\n", text)
    return text.strip()


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
        application.add_handler(
            CallbackQueryHandler(self._on_pheme_callback, pattern=r"^pheme:")
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

    async def _on_pheme_callback(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ) -> None:
        """Handle Pheme digest Approve / Skip inline buttons.

        Approve fires the gated Twitter tool (Aegis pre-hook runs inside
        post_news_thread); Skip just drops the pending entry. Both edit the
        keyboard away so a digest cannot be approved twice.
        """
        query = update.callback_query
        if query is None or not query.data:
            return
        chat = update.effective_chat
        pheme_chat = None
        try:
            from zeus.pheme.delivery import pheme_chat_id

            pheme_chat = pheme_chat_id()
        except Exception:
            pass
        allowed = set(self._allowed)
        if pheme_chat is not None:
            allowed.add(pheme_chat)
        if allowed and (chat is None or chat.id not in allowed):
            logger.warning(
                "dropping pheme callback from disallowed chat_id=%s",
                getattr(chat, "id", None),
            )
            await query.answer()
            return

        parts = query.data.split(":")
        action = parts[1] if len(parts) > 1 else ""

        if action == "fb":
            # pheme:fb:<digest_id>:<story_idx>:<up|down> - ranking feedback.
            # Answered with a toast only; the digest message stays untouched.
            digest_id = parts[2] if len(parts) > 2 else ""
            try:
                idx = int(parts[3])
            except (IndexError, ValueError):
                await query.answer()
                return
            reaction = 1 if (len(parts) > 4 and parts[4] == "up") else -1
            import asyncio as _asyncio

            from zeus.pheme.feedback import record_reaction

            story = await _asyncio.to_thread(record_reaction, digest_id, idx, reaction)
            if story is None:
                await query.answer("Feedback window for this digest has expired.")
            else:
                verb = "More" if reaction > 0 else "Less"
                await query.answer(
                    f"{verb} like: {str(story.get('name', ''))[:50]}"
                )
            return

        digest_id = parts[2] if len(parts) > 2 else ""
        await query.answer()

        if action == "skip":
            from zeus.pheme.delivery import pop_pending_tweet

            pop_pending_tweet(digest_id)
            await query.edit_message_reply_markup(reply_markup=None)
            await context.bot.send_message(
                chat_id=chat.id, text="Skipped - nothing posted to Twitter."
            )
            return

        if action == "approve":
            from zeus.integrations.twitter.poster import TwitterPostError
            from zeus.pheme.delivery import approve_pending_tweet

            try:
                ids = await approve_pending_tweet(digest_id)
            except TwitterPostError as exc:
                logger.warning("pheme tweet approval failed: %s", exc)
                await context.bot.send_message(
                    chat_id=chat.id, text=f"Tweet failed: {exc}"
                )
                return
            await query.edit_message_reply_markup(reply_markup=None)
            await context.bot.send_message(
                chat_id=chat.id,
                text=f"Posted {len(ids)} tweet(s): https://x.com/i/web/status/{ids[0]}",
                disable_web_page_preview=True,
            )

    async def _on_message(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ) -> None:
        msg = update.effective_message
        chat = update.effective_chat
        if msg is None or chat is None or not msg.text:
            logger.info("telegram update ignored (no text/chat): %s", update)
            return
        logger.info(
            "telegram message received: chat_id=%s user=%s text=%r",
            chat.id,
            getattr(update.effective_user, "username", None),
            msg.text[:80],
        )
        if self._allowed and chat.id not in self._allowed:
            logger.warning(
                "dropping telegram message from disallowed chat_id=%s (allowlist=%s)",
                chat.id,
                sorted(self._allowed),
            )
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

        reply = markdown_to_plaintext(reply)

        try:
            await msg.reply_text(
                reply[:_TELEGRAM_MAX_LEN],
                disable_web_page_preview=True,
            )
        except Exception as exc:
            logger.exception("failed sending telegram reply: %s", exc)


def _coerce_bool(value: object, default: bool = False) -> bool:
    if value is None:
        return default
    if isinstance(value, bool):
        return value
    return str(value).strip().lower() in ("1", "true", "yes", "on")


def _coerce_chat_ids(value: object) -> set[int]:
    if value is None:
        return set()
    if isinstance(value, (list, tuple, set)):
        out: set[int] = set()
        for item in value:
            try:
                out.add(int(item))
            except (TypeError, ValueError):
                logger.warning("ignoring invalid telegram chat id: %r", item)
        return out
    return _parse_chat_ids(str(value))


def build_telegram_bot(
    query_engine: QueryEngine,
    overrides: dict | None = None,
) -> TelegramBot | None:
    """Construct a TelegramBot from runtime overrides + env, or return None.

    ``overrides`` (from ``RuntimeSettings.get_section('telegram')``) wins over
    env vars. Missing keys fall back to the matching ``TELEGRAM_*`` env.
    """
    overrides = overrides or {}

    enabled = _coerce_bool(
        overrides.get("enabled")
        if "enabled" in overrides
        else os.getenv("TELEGRAM_ENABLED", "0")
    )
    if not enabled:
        return None

    token = str(
        overrides.get("bot_token") or os.getenv("TELEGRAM_BOT_TOKEN", "")
    ).strip()
    if not token:
        logger.warning("telegram enabled but bot_token is empty")
        return None

    allowed = _coerce_chat_ids(
        overrides.get("allowed_chat_ids")
        if "allowed_chat_ids" in overrides
        else os.getenv("TELEGRAM_ALLOWED_CHAT_IDS")
    )
    policy = (
        overrides.get("aegis_policy")
        or os.getenv("TELEGRAM_AEGIS_POLICY")
        or os.getenv("ZEUS_AEGIS_POLICY")
        or None
    )
    return TelegramBot(
        token,
        query_engine,
        allowed_chat_ids=allowed,
        policy_name=policy,
    )
