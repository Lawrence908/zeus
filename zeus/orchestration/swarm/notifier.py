# zeus/orchestration/swarm/notifier.py
"""Notify a human when an approval gate opens (so long runs don't stall silently).

The coordinator fires `approval_opened` whenever it creates an in-run gate
(node write / budget / final). NullNotifier is the default; TelegramNotifier
pushes a message via the Telegram Bot API using the existing bot credentials.
Notification is best-effort - a failure never affects the run.
"""

from __future__ import annotations

import logging
import os
from typing import Protocol

import httpx

from zeus.orchestration.swarm.models import Approval, ApprovalKind, Run

logger = logging.getLogger("zeus.swarm.notifier")

_GATE_TEXT: dict[ApprovalKind, str] = {
    ApprovalKind.PLAN: "plan ready to approve",
    ApprovalKind.NODE_WRITE: "node awaiting write approval",
    ApprovalKind.BUDGET: "run is over budget",
    ApprovalKind.FINAL: "run finished, awaiting final merge approval",
}


class ApprovalNotifier(Protocol):
    async def approval_opened(self, run: Run, approval: Approval) -> None: ...


class NullNotifier:
    async def approval_opened(self, run: Run, approval: Approval) -> None:
        return None


def build_message(run: Run, approval: Approval) -> str:
    what = _GATE_TEXT.get(approval.kind, approval.kind.value)
    node = f" ({approval.node_id})" if approval.node_id else ""
    return (
        f"\U0001f916 Argo swarm: {what}{node}\n"
        f"goal: {run.goal[:160]}\n"
        f"run: {run.id} · status {run.status.value}\n"
        f"approve in the Zeus OS Swarm app."
    )


class TelegramNotifier:
    """Push approval prompts to Telegram via the Bot API (sendMessage)."""

    def __init__(self, token: str, chat_id: str) -> None:
        self._url = f"https://api.telegram.org/bot{token}/sendMessage"
        self._chat_id = chat_id

    async def approval_opened(self, run: Run, approval: Approval) -> None:
        async with httpx.AsyncClient(timeout=10) as client:
            await client.post(self._url, json={"chat_id": self._chat_id, "text": build_message(run, approval)})

    @classmethod
    def from_env(cls) -> "TelegramNotifier | None":
        token = os.getenv("TELEGRAM_BOT_TOKEN", "").strip()
        chat = os.getenv("ZEUS_SWARM_TELEGRAM_CHAT_ID", "").strip()
        if not chat:
            # Fall back to the first allowlisted chat id.
            chat = os.getenv("TELEGRAM_ALLOWED_CHAT_IDS", "").split(",")[0].strip()
        if not token or not chat:
            return None
        return cls(token, chat)
