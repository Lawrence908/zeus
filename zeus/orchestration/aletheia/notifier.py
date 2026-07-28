# zeus/orchestration/aletheia/notifier.py
"""Telegram delivery for Aletheia.

Two shapes, matching the design's delivery split:
  - ``notify_incremental``: immediate terse push for a push-triggered run (doc
    count, top few findings) - quick value while the change is fresh.
  - ``notify_digest``: weekly headline + a pointer to the full report.

Best-effort: a delivery failure never affects a run. Reuses the existing bot
credentials (``TELEGRAM_BOT_TOKEN`` + allowlisted chat id), same as the swarm
notifier.
"""

from __future__ import annotations

import logging
import os

import httpx

from zeus.orchestration.aletheia.digest import DigestResult
from zeus.orchestration.aletheia.models import Finding
from zeus.orchestration.aletheia.sweep import SweepReport

logger = logging.getLogger("zeus.aletheia.notifier")

_TOP_N = 3


def _chat_id() -> str:
    chat = os.getenv("ZEUS_ALETHEIA_TELEGRAM_CHAT_ID", "").strip()
    if not chat:
        chat = os.getenv("ZEUS_SWARM_TELEGRAM_CHAT_ID", "").strip()
    if not chat:
        chat = os.getenv("TELEGRAM_ALLOWED_CHAT_IDS", "").split(",")[0].strip()
    return chat


async def _send(text: str) -> bool:
    token = os.getenv("TELEGRAM_BOT_TOKEN", "").strip()
    chat = _chat_id()
    if not token or not chat:
        logger.info("aletheia notifier: no telegram creds, skipping push")
        return False
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            await client.post(
                f"https://api.telegram.org/bot{token}/sendMessage",
                json={"chat_id": chat, "text": text, "disable_web_page_preview": True},
            )
        return True
    except Exception as exc:  # best-effort
        logger.warning("aletheia notifier failed: %s", exc)
        return False


def _top_line(f: Finding) -> str:
    return f"  - [{f.status.value}] {f.doc_path}: {f.reference.target}"


def build_incremental_message(report: SweepReport) -> str:
    r = report.run
    docs = sorted({f.doc_path for f in report.reportable})
    head = (
        f"\U0001f50d Aletheia (incremental): {r.findings_reportable} drift finding(s) "
        f"across {len(docs)} doc(s)."
    )
    if not report.reportable:
        return head + "\nDocs touched resolve clean."
    tops = "\n".join(_top_line(f) for f in report.reportable[:_TOP_N])
    more = f"\n  (+{r.findings_reportable - _TOP_N} more)" if r.findings_reportable > _TOP_N else ""
    return f"{head}\n{tops}{more}\nrun: {r.id}"


def build_digest_message(result: DigestResult) -> str:
    return (
        f"\U0001f4dc Aletheia weekly digest {result.iso_week}: "
        f"{result.total} open drift finding(s), {result.new} new, "
        f"{result.resolved} resolved.\nreport: {result.path}"
    )


async def notify_incremental(report: SweepReport) -> bool:
    return await _send(build_incremental_message(report))


async def notify_digest(result: DigestResult) -> bool:
    return await _send(build_digest_message(result))
