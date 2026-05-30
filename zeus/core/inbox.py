# zeus/core/inbox.py — Append-only capture endpoint for the Olympian tool pack
#
# POST /inbox/append   {text, tags?}   appends one bullet line to ZEUS_INBOX_PATH
#
# Atomic append uses fcntl.LOCK_EX to keep concurrent writers from interleaving
# bytes mid-line. Lines are kept under 8 KB so a runaway caller cannot fill the
# disk in one request. Aegis policy `file_access` flags but does NOT reject
# credential-shaped strings: this is personal capture; false positives would
# train the user away from using the tool.
from __future__ import annotations

import fcntl
import logging
import os
from datetime import datetime
from pathlib import Path
from typing import Any

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from zeus.safety.policy_engine import AegisPolicyEngine, aegis_enabled

logger = logging.getLogger("zeus.inbox")

router = APIRouter(tags=["inbox"])

_MAX_TEXT_LEN = 8 * 1024
_MAX_TAG_COUNT = 16
_MAX_TAG_LEN = 64


def _inbox_path() -> Path:
    raw = os.getenv("ZEUS_INBOX_PATH", "~/.zeus/inbox.md")
    return Path(os.path.expanduser(raw))


def _write_enabled() -> bool:
    # Mirrors the MCP write gate so curl-from-localhost cannot bypass it
    # when the operator deliberately turned writes off everywhere.
    return os.getenv("ZEUS_MCP_ALLOW_WRITE", "false").strip().lower() in (
        "1", "true", "yes", "y", "on",
    )


def _aegis_check(payload: dict[str, Any]) -> None:
    if not aegis_enabled() or not payload:
        return
    engine = AegisPolicyEngine(policy="file_access")
    outcome = engine.evaluate_payload(payload, policy_name="file_access")
    if outcome.status == "rejected":
        raise HTTPException(status_code=400, detail=outcome.message or "Aegis blocked payload.")


class InboxAppendRequest(BaseModel):
    text: str = Field(..., min_length=1, max_length=_MAX_TEXT_LEN)
    tags: list[str] | None = Field(default=None)


@router.post("/inbox/append")
async def inbox_append(req: InboxAppendRequest) -> dict[str, Any]:
    """Append a single bullet line to ZEUS_INBOX_PATH. Backs olympian_inbox_append.

    Format: `- [YYYY-MM-DD HH:MM] <text> #tag1 #tag2\n`

    Newlines and CRs in `text` are collapsed to spaces so each entry stays one
    line — the inbox file is meant to be readable as a flat list.
    """
    if not _write_enabled():
        raise HTTPException(
            status_code=403,
            detail="Inbox writes are disabled. Set ZEUS_MCP_ALLOW_WRITE=1 to enable.",
        )

    tags_raw = req.tags or []
    if len(tags_raw) > _MAX_TAG_COUNT:
        raise HTTPException(status_code=400, detail=f"too many tags (max {_MAX_TAG_COUNT})")
    tags: list[str] = []
    for t in tags_raw:
        s = str(t or "").strip().lstrip("#")
        if not s:
            continue
        if len(s) > _MAX_TAG_LEN:
            raise HTTPException(status_code=400, detail=f"tag too long (max {_MAX_TAG_LEN} chars)")
        if any(c.isspace() for c in s):
            raise HTTPException(status_code=400, detail="tags may not contain whitespace")
        tags.append(s)

    _aegis_check({"text": req.text, "tags": ",".join(tags)})

    text_clean = " ".join(req.text.replace("\r", " ").replace("\n", " ").split())
    if not text_clean:
        raise HTTPException(status_code=400, detail="text is empty after stripping")

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
    suffix = (" " + " ".join(f"#{t}" for t in tags)) if tags else ""
    line = f"- [{timestamp}] {text_clean}{suffix}\n"

    path = _inbox_path()
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
    except OSError as exc:
        raise HTTPException(status_code=500, detail=f"cannot create inbox directory: {exc}") from exc

    try:
        # Open append-mode + advisory lock keeps concurrent writers serialised.
        with open(path, "a", encoding="utf-8") as fh:
            try:
                fcntl.flock(fh.fileno(), fcntl.LOCK_EX)
                fh.write(line)
                fh.flush()
            finally:
                fcntl.flock(fh.fileno(), fcntl.LOCK_UN)
    except OSError as exc:
        raise HTTPException(status_code=500, detail=f"append failed: {exc}") from exc

    return {
        "path": str(path),
        "appended_line": line.rstrip("\n"),
        "bytes_written": len(line),
    }
