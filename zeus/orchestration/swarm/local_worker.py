# zeus/orchestration/swarm/local_worker.py
"""Local worker tier (C4): trivial nodes on the homelab Ollama GPU, $0.

A local 7B model has no Claude Code tool loop, so this worker does NOT try to be
agentic. It runs one structured completion that emits the full file(s) the node
should write, then writes them into the git worktree. That is reliable for the
kind of node the planner tags "local": a doc, a config, a small single file, a
rename. Anything needing exploration or multi-file logic stays on the paid tier.

`RoutingWorker` lets a paid run stay hybrid: nodes the planner tags model:"local"
(or "ollama", or a concrete Ollama tag) run here for free; everything else goes
to the claude/sandbox worker. Cost is always 0.0 - it is your own GPU.
"""

from __future__ import annotations

import json
import logging
import os
import re

import httpx

from zeus.orchestration.swarm import config
from zeus.orchestration.swarm.models import Run, TaskNode
from zeus.orchestration.swarm.worker import Worker, WorkerResult

logger = logging.getLogger("zeus.swarm.local")

_SYSTEM = (
    "You are a coding worker completing ONE small task in a repository. You cannot "
    "run tools or explore. Respond with ONLY a JSON object of the form "
    '{"files": [{"path": "repo/relative/path", "content": "FULL new file contents"}], '
    '"summary": "one line"}. Each file you list is written verbatim, replacing any '
    "existing file at that path. Use repo-relative paths, never absolute, never '..'. "
    "Keep the change minimal and focused on the task. No prose outside the JSON."
)


def build_local_prompt(node: TaskNode, run: Run, feedback: str | None = None) -> str:
    lines = [
        f"Project goal: {run.goal}",
        "",
        f"Task: {node.title}",
    ]
    if node.acceptance:
        lines += [f"Acceptance: {node.acceptance}"]
    if node.answer:  # P10: human clarification
        lines += [f"Clarification - Q: {node.question}  A: {node.answer}"]
    if node.check:
        lines += [f"It will be verified by running: {node.check}"]
    if feedback:
        lines += ["", "A previous attempt did not pass. Fix it:", feedback]
    return "\n".join(lines)


def _extract_files(text: str) -> tuple[list[dict], str]:
    """Pull {files, summary} out of the model answer (raw / fenced / prose-wrapped)."""
    text = text.strip()
    obj: dict | None = None
    for candidate in _json_candidates(text):
        try:
            parsed = json.loads(candidate)
        except json.JSONDecodeError:
            continue
        if isinstance(parsed, dict) and "files" in parsed:
            obj = parsed
            break
    if obj is None:
        raise ValueError("local worker: no JSON object with a 'files' key in output")
    files = obj.get("files")
    if not isinstance(files, list) or not files:
        raise ValueError("local worker: 'files' was empty")
    return files, str(obj.get("summary", ""))


def _json_candidates(text: str) -> list[str]:
    out = [text]
    fence = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", text, re.DOTALL)
    if fence:
        out.append(fence.group(1))
    start, end = text.find("{"), text.rfind("}")
    if start != -1 and end > start:
        out.append(text[start : end + 1])
    return out


def _safe_join(workspace: str, rel: str) -> str:
    """Resolve a repo-relative path inside the worktree, rejecting escapes."""
    rel = (rel or "").strip().lstrip("/")
    if not rel:
        raise ValueError("empty file path")
    root = os.path.realpath(workspace)
    dest = os.path.realpath(os.path.join(root, rel))
    if dest != root and not dest.startswith(root + os.sep):
        raise ValueError(f"path escapes worktree: {rel!r}")
    return dest


class LocalWorker:
    """One-shot Ollama file-writer. Free; for trivial, single-shot nodes."""

    def __init__(self, *, model: str | None = None, timeout_s: float = 300) -> None:
        self._model = model
        self._timeout_s = timeout_s

    async def run(self, node: TaskNode, run: Run, workspace: str | None,
                  feedback: str | None = None) -> WorkerResult:
        if workspace is None:
            return WorkerResult(success=False, error="local worker requires a worktree")
        model = config.resolve_local_model(self._model or node.model)
        body = {
            "model": model,
            "messages": [
                {"role": "system", "content": _SYSTEM},
                {"role": "user", "content": build_local_prompt(node, run, feedback)},
            ],
            "stream": False,
            "format": "json",
            "options": {"temperature": 0.1},
        }
        timeout = httpx.Timeout(connect=10.0, read=self._timeout_s, write=10.0, pool=10.0)
        try:
            async with httpx.AsyncClient(timeout=timeout) as client:
                resp = await client.post(f"{config.ollama_url()}/api/chat", json=body)
                resp.raise_for_status()
                data = resp.json()
        except (httpx.HTTPError, OSError) as exc:
            return WorkerResult(success=False, error=f"ollama call failed: {exc}")

        content = str((data.get("message") or {}).get("content", ""))
        try:
            files, summary = _extract_files(content)
        except ValueError as exc:
            return WorkerResult(success=False, error=str(exc))

        written: list[str] = []
        try:
            for f in files:
                if not isinstance(f, dict):
                    raise ValueError("local worker: each 'files' entry must be an object")
                rel = f.get("path", "")
                dest = _safe_join(workspace, rel)
                os.makedirs(os.path.dirname(dest) or workspace, exist_ok=True)
                with open(dest, "w", encoding="utf-8") as fh:
                    fh.write(str(f.get("content", "")))
                written.append(rel.strip().lstrip("/"))
        except (ValueError, OSError) as exc:
            return WorkerResult(success=False, error=f"local worker write failed: {exc}")

        note = summary or f"wrote {', '.join(written)}"
        return WorkerResult(success=True, output=f"[local:{model}] {note}", cost_usd=0.0)


class RoutingWorker:
    """Dispatch each node to the free local tier or the paid worker by its model hint."""

    def __init__(self, paid: Worker, local: Worker | None = None) -> None:
        self._paid = paid
        self._local = local or LocalWorker()

    async def run(self, node: TaskNode, run: Run, workspace: str | None,
                  feedback: str | None = None) -> WorkerResult:
        if config.is_local_model(node.model):
            return await self._local.run(node, run, workspace, feedback)
        return await self._paid.run(node, run, workspace, feedback)
