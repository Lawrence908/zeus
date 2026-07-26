# zeus/orchestration/swarm/transcript.py
"""Locate and summarise an argonaut's Claude Code transcript for a node (P8b).

Claude Code writes a per-session JSONL transcript under
`~/.claude/projects/<escaped-cwd>/<session_id>.jsonl`. We don't try to
reconstruct the escaped-cwd - we glob for `<session_id>.jsonl` under the projects
root, which is robust to how the worktree path was escaped.

Best-effort: the *sandboxed* worker writes its transcript inside the ephemeral
container (HOME is a tmpfs), so only the host `claude` worker leaves one on disk.
A missing transcript returns an empty list, never an error.
"""

from __future__ import annotations

import glob
import json
import logging
import os

logger = logging.getLogger("zeus.swarm.transcript")


def projects_dir() -> str:
    override = os.getenv("ZEUS_SWARM_TRANSCRIPT_DIR")
    if override:
        return os.path.expanduser(override)
    cfg = os.getenv("CLAUDE_CONFIG_DIR")
    base = os.path.expanduser(cfg) if cfg else os.path.expanduser("~/.claude")
    return os.path.join(base, "projects")


def find_transcript(session_id: str) -> str | None:
    """Path to `<session_id>.jsonl` under any project dir, or None."""
    if not session_id:
        return None
    matches = glob.glob(os.path.join(projects_dir(), "*", f"{session_id}.jsonl"))
    return matches[0] if matches else None


def _text_of(content: object) -> str:
    """Flatten a message `content` (string or list of blocks) to short text."""
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        parts: list[str] = []
        for block in content:
            if not isinstance(block, dict):
                continue
            t = block.get("type")
            if t == "text":
                parts.append(str(block.get("text", "")))
            elif t == "tool_use":
                parts.append(f"[tool_use {block.get('name', '')}]")
            elif t == "tool_result":
                parts.append("[tool_result]")
        return " ".join(p for p in parts if p)
    return ""


def _summarize(event: dict) -> dict | None:
    etype = event.get("type")
    if etype in ("user", "assistant"):
        msg = event.get("message") or {}
        role = msg.get("role", etype)
        text = _text_of(msg.get("content"))
        if not text:
            return None
        return {"type": etype, "role": role, "text": text[:600]}
    if etype == "result":
        return {"type": "result", "role": "system",
                "text": str(event.get("result", ""))[:600]}
    return None


def read_transcript(session_id: str, *, limit: int = 200) -> dict:
    """Compact, bounded view of a node's transcript. `{exists, events}`."""
    path = find_transcript(session_id)
    if path is None:
        return {"exists": False, "events": []}
    events: list[dict] = []
    try:
        with open(path, encoding="utf-8") as fh:
            for line in fh:
                line = line.strip()
                if not line:
                    continue
                try:
                    evt = json.loads(line)
                except json.JSONDecodeError:
                    continue
                summary = _summarize(evt) if isinstance(evt, dict) else None
                if summary is not None:
                    events.append(summary)
    except OSError as exc:
        logger.warning("transcript read failed for %s: %s", session_id, exc)
        return {"exists": False, "events": []}
    return {"exists": True, "events": events[-limit:]}
