# zeus/pheme/delivery.py - Pheme outbound delivery: Telegram push + Twitter gate.
#
# The Telegram push is proactive (the bot is otherwise reactive): it sends the
# digest straight to PHEME_TELEGRAM_CHAT_ID via the Bot API, independent of the
# long-polling Application. The Approve / Skip inline keyboard is answered by
# the running TelegramBot (callback handler registered in bot.py), which calls
# approve_pending_tweet() here.
#
# Every outbound path passes Aegis:
#   - Telegram text: evaluate_text under the "pheme" policy before send
#   - Twitter: post_news_thread() runs its own evaluate_payload pre-hook
from __future__ import annotations

import json
import logging
import os
import re
from datetime import datetime, timezone
from pathlib import Path

from zeus.pheme.models import PhemeDigest

logger = logging.getLogger("zeus.pheme.delivery")

_TELEGRAM_MAX_LEN = 4096


def _data_dir() -> Path:
    return Path(os.getenv("PHEME_DATA_DIR", "zeus/data/pheme"))


def _autopost_enabled() -> bool:
    return os.getenv("PHEME_TWITTER_AUTOPOST", "0").strip() in ("1", "true", "yes", "on")


def pheme_chat_id() -> int | None:
    raw = os.getenv("PHEME_TELEGRAM_CHAT_ID", "").strip()
    try:
        return int(raw) if raw else None
    except ValueError:
        logger.warning("invalid PHEME_TELEGRAM_CHAT_ID: %r", raw)
        return None


# ---------------------------------------------------------------------------
# Pending-tweet store (the one-tap approval gate)
# ---------------------------------------------------------------------------

def _pending_path() -> Path:
    return _data_dir() / "pending_tweets.json"


def _load_pending() -> dict:
    p = _pending_path()
    if not p.is_file():
        return {}
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        logger.warning("corrupt pending tweets store, resetting")
        return {}


def _save_pending(data: dict) -> None:
    p = _pending_path()
    p.parent.mkdir(parents=True, exist_ok=True)
    tmp = p.with_suffix(".tmp")
    tmp.write_text(json.dumps(data, indent=2), encoding="utf-8")
    tmp.replace(p)


def save_pending_tweet(digest: PhemeDigest) -> None:
    data = _load_pending()
    data[digest.id] = {
        "lead": digest.public_lead,
        "thread": digest.public_thread,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    # Keep only the 10 most recent pending entries.
    for stale in sorted(data, key=lambda k: data[k].get("created_at", ""))[:-10]:
        data.pop(stale, None)
    _save_pending(data)


def pop_pending_tweet(digest_id: str) -> dict | None:
    data = _load_pending()
    entry = data.pop(digest_id, None)
    if entry is not None:
        _save_pending(data)
    return entry


async def approve_pending_tweet(digest_id: str) -> list[str]:
    """Fire the Twitter tool for an approved digest. Raises TwitterPostError."""
    from zeus.integrations.twitter.poster import TwitterPostError, post_news_thread

    entry = pop_pending_tweet(digest_id)
    if entry is None:
        raise TwitterPostError(f"no pending tweet for digest {digest_id}")
    return await post_news_thread(entry.get("lead", ""), entry.get("thread") or [])


# ---------------------------------------------------------------------------
# Breaking-alert budget
# ---------------------------------------------------------------------------

def _alert_log_path() -> Path:
    return _data_dir() / "alerts.json"


def max_alerts_per_day() -> int:
    try:
        return max(0, int(os.getenv("PHEME_MAX_ALERTS_PER_DAY", "3")))
    except ValueError:
        return 3


def alerts_sent_today() -> int:
    p = _alert_log_path()
    if not p.is_file():
        return 0
    try:
        data = json.loads(p.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return 0
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    return int(data.get(today, 0))


def record_alert() -> None:
    p = _alert_log_path()
    data: dict = {}
    if p.is_file():
        try:
            data = json.loads(p.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            data = {}
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    data = {today: int(data.get(today, 0)) + 1}  # keep only today's counter
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(data), encoding="utf-8")


# ---------------------------------------------------------------------------
# Telegram push
# ---------------------------------------------------------------------------

def _esc(text: str) -> str:
    """Escape for Telegram HTML parse mode."""
    return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def _domain(url: str) -> str:
    try:
        host = url.split("//", 1)[-1].split("/", 1)[0]
        return host.removeprefix("www.")
    except Exception:
        return "link"


def format_digest_html(digest: PhemeDigest, *, breaking: bool = False) -> str:
    """Render the digest as Telegram HTML: bold headers, one titled link per
    story, and compact meta lines instead of bracket noise."""
    try:
        day = datetime.fromisoformat(digest.generated_at).strftime("%a %b %-d")
    except ValueError:
        day = ""
    header = "🚨 <b>Pheme Breaking Alert</b>" if breaking else "🗞️ <b>Pheme Daily Digest</b>"
    if day:
        header += f" · {day}"

    lines: list[str] = [header, "", _esc(digest.lead.strip())]

    if digest.insights:
        lines += ["", "💡 <b>Insights</b>"]
        for ins in digest.insights:
            lines.append(f"•  {_esc(ins)}")

    if digest.connections:
        lines += ["", "🔗 <b>Connections</b> <i>(congressional signal x news)</i>"]
        for c in digest.connections[:5]:
            lines.append(f"•  {_esc(c.claim)} ({c.confidence:.0%})")

    lines += ["", "📰 <b>Top stories</b>"]
    from zeus.pheme.pipeline import _coverage_label, _one_line_take

    for i, cluster in enumerate(digest.clusters, 1):
        if cluster.thread_status == "development":
            marker = f"📈 day {cluster.thread_days}" if cluster.thread_days > 1 else "📈 developing"
        else:
            marker = "🆕 new"
        lines.append(
            f"{i}. <b>{_esc(cluster.name)}</b>  ·  {_esc(_coverage_label(cluster))}  ·  {marker}"
        )
        take = _one_line_take(cluster)
        if take:
            lines.append(f"     {_esc(take)}.")
        if cluster.urls:
            extra = len(cluster.urls) - 1
            link = f'     <a href="{_esc(cluster.urls[0])}">{_esc(_domain(cluster.urls[0]))}</a>'
            if extra > 0:
                link += f" <i>+{extra} more</i>"
            lines.append(link)
        lines.append("")
    return "\n".join(lines).strip()


_URL_RE_FOR_SAFETY = re.compile(r"https?://\S+")


async def send_digest_telegram(digest: PhemeDigest, *, breaking: bool = False) -> bool:
    """Push a digest to the dedicated news chat. Returns True when sent."""
    from telegram import Bot, InlineKeyboardButton, InlineKeyboardMarkup

    from zeus.integrations.telegram.bot import markdown_to_plaintext
    from zeus.safety.policy_engine import aegis_enabled, evaluate_text

    token = os.getenv("TELEGRAM_BOT_TOKEN", "").strip()
    chat_id = pheme_chat_id()
    if not token or chat_id is None:
        logger.info("pheme telegram push skipped (token or PHEME_TELEGRAM_CHAT_ID unset)")
        return False

    # Aegis runs on the user-visible text with URLs stripped: article URLs are
    # data, and long query tokens would otherwise trip the credential rule.
    safety_view = _URL_RE_FOR_SAFETY.sub("", digest.body)
    if aegis_enabled():
        outcome = evaluate_text(safety_view, "pheme")
        if outcome.status != "ok":
            logger.warning("aegis blocked pheme telegram push (flags=%s)", outcome.flags)
            header = "🚨 Pheme breaking alert" if breaking else "🗞️ Pheme daily digest"
            fallback = f"{header}\n\nDigest was filtered by Aegis safety policy."
            html = plain = fallback
        else:
            html = format_digest_html(digest, breaking=breaking)
            plain = markdown_to_plaintext(digest.body)
    else:
        html = format_digest_html(digest, breaking=breaking)
        plain = markdown_to_plaintext(digest.body)

    from zeus.integrations.twitter.poster import twitter_enabled
    from zeus.pheme.feedback import save_digest_context

    rows: list[list[InlineKeyboardButton]] = []
    if digest.clusters:
        # Per-story thumbs: one 👍 row and one 👎 row, numbered to match the
        # digest's story list. Presses feed the ranking preference store.
        save_digest_context(
            digest.id,
            [
                {
                    "key": c.key,
                    "name": c.name,
                    "entities": c.entities,
                    "topics": c.topics,
                    "sources": c.sources,
                }
                for c in digest.clusters
            ],
        )
        rows.append(
            [
                InlineKeyboardButton(f"👍{i + 1}", callback_data=f"pheme:fb:{digest.id}:{i}:up")
                for i in range(len(digest.clusters))
            ]
        )
        rows.append(
            [
                InlineKeyboardButton(f"👎{i + 1}", callback_data=f"pheme:fb:{digest.id}:{i}:down")
                for i in range(len(digest.clusters))
            ]
        )
    if twitter_enabled() and digest.public_lead and not _autopost_enabled():
        rows.append(
            [
                InlineKeyboardButton("✅ Tweet it", callback_data=f"pheme:approve:{digest.id}"),
                InlineKeyboardButton("⏭️ Skip", callback_data=f"pheme:skip:{digest.id}"),
            ]
        )
    keyboard = InlineKeyboardMarkup(rows) if rows else None

    bot = Bot(token=token)

    async def _send(text: str, parse_mode: str | None) -> None:
        # Chunk on line boundaries so HTML tags never split across messages.
        chunks: list[str] = []
        current = ""
        for line in text.split("\n"):
            if len(current) + len(line) + 1 > _TELEGRAM_MAX_LEN:
                chunks.append(current)
                current = line
            else:
                current = f"{current}\n{line}" if current else line
        if current:
            chunks.append(current)
        for i, chunk in enumerate(chunks):
            await bot.send_message(
                chat_id=chat_id,
                text=chunk,
                parse_mode=parse_mode,
                disable_web_page_preview=True,
                reply_markup=keyboard if i == len(chunks) - 1 else None,
            )

    try:
        await _send(html, "HTML")
    except Exception as exc:
        logger.warning("html digest send failed (%s), falling back to plain text", exc)
        try:
            await _send(plain, None)
        except Exception as exc2:
            logger.error("pheme telegram push failed: %s", exc2)
            return False

    # Morning-listen track (best-effort; text digest already delivered).
    if digest.audio_file:
        audio_path = Path(os.getenv("NEWSLETTER_AUDIO_DIR", "zeus/data/audio")) / digest.audio_file
        if audio_path.is_file():
            try:
                day = digest.generated_at[:10]
                with open(audio_path, "rb") as fh:
                    await bot.send_audio(
                        chat_id=chat_id,
                        audio=fh,
                        title=f"Pheme Daily Digest {day}",
                        performer="Zeus",
                    )
            except Exception as exc:
                logger.warning("digest audio send failed: %s", exc)

    logger.info("pheme digest %s pushed to telegram chat %s", digest.id, chat_id)
    return True


# ---------------------------------------------------------------------------
# Top-level delivery
# ---------------------------------------------------------------------------

async def deliver_digest(digest: PhemeDigest, *, breaking: bool = False) -> dict:
    """Telegram push, then Twitter: autopost when flipped on, else queue for approval."""
    result: dict = {"telegram": False, "twitter": "disabled"}
    if not digest.clusters:
        result["telegram"] = "skipped-empty"
        return result

    result["telegram"] = await send_digest_telegram(digest, breaking=breaking)

    from zeus.integrations.twitter.poster import TwitterPostError, post_news_thread, twitter_enabled

    if twitter_enabled() and digest.public_lead:
        if _autopost_enabled():
            try:
                ids = await post_news_thread(digest.public_lead, digest.public_thread)
                result["twitter"] = {"posted": ids}
            except TwitterPostError as exc:
                logger.error("pheme autopost failed: %s", exc)
                result["twitter"] = {"error": str(exc)}
        else:
            save_pending_tweet(digest)
            result["twitter"] = "pending-approval"
    return result
