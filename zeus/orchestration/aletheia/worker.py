# zeus/orchestration/aletheia/worker.py
"""Read-only Claude Code investigator for one document.

This is the *recall extension* on top of the mechanical extractor+verifier path.
The mechanical path catches backticked references with high precision and zero
spend; this worker reads the doc and the code and proposes further candidate
findings (including from prose the extractor can't parse). Every candidate it
emits is still re-checked by the independent verifier before it can be reported,
so the worker widening recall never lowers precision.

Read-only is enforced three ways, from the design:
  1. allowlist: only Read/Grep/Glob + two read-only git subcommands.
  2. denylist: exclusion globs compile into `--disallowedTools` so the
     personal-data layer is unreadable even though Read is allowed.
  3. no worktree: it reads the live tree; there is nothing to commit.
"""

from __future__ import annotations

import json
import logging
import re

from pydantic import BaseModel

from zeus.orchestration.aletheia import config
from zeus.orchestration.aletheia.models import (
    Finding,
    FindingStatus,
    Reference,
    ReferenceKind,
)
# Reuse the swarm's battle-tested claude subprocess plumbing.
from zeus.orchestration.swarm.claude_worker import (
    build_command,
    claude_available,
    parse_stream_json,
)

logger = logging.getLogger("zeus.aletheia.worker")

_JSON_ARRAY_RE = re.compile(r"\[.*\]", re.DOTALL)


class WorkerResult(BaseModel):
    success: bool
    findings: list[Finding] = []
    cost_usd: float = 0.0
    session_id: str | None = None
    error: str | None = None


def build_prompt(doc_rel: str) -> str:
    kinds = ", ".join(k.value for k in ReferenceKind)
    statuses = "missing, moved, changed"
    return (
        "You are Aletheia, a read-only documentation-drift investigator. Analyse "
        f"exactly one document: `{doc_rel}`.\n\n"
        "Read the document, then resolve every concrete claim it makes about this "
        "codebase (file paths, symbols/functions/classes, environment variables, "
        "HTTP endpoints, config keys, shell commands) against the actual code using "
        "Read/Grep/Glob. Report only claims that NO LONGER HOLD.\n\n"
        "Output ONLY a JSON array (no prose, no code fence). Each element:\n"
        '  {"doc_line": <int>, "claim": "<short quote of the doc claim>", '
        '"reference": {"kind": "<one of: ' + kinds + '>", "target": "<the referenced thing>"}, '
        '"status": "<one of: ' + statuses + '>", '
        '"evidence": "<where you looked and what you found>", "confidence": <0..1>}\n\n'
        "Rules: status `missing` = the referenced thing does not exist; `moved` = it "
        "exists elsewhere than documented (put the real location in evidence); `changed` "
        "= it exists in place but its signature/default/behaviour contradicts the doc. "
        "Do NOT report things that resolve correctly. Do NOT invent references. If the "
        "document is fully accurate, output []. Never read .env files or anything under "
        "a data directory."
    )


def parse_findings(result_text: str, doc_rel: str) -> list[Finding]:
    """Coerce the worker's JSON array into unverified Finding objects.

    Robust to the model wrapping the array in prose: the first ``[...]`` span is
    taken. Malformed elements are skipped, never crash the sweep.
    """
    m = _JSON_ARRAY_RE.search(result_text or "")
    if not m:
        return []
    try:
        raw = json.loads(m.group(0))
    except json.JSONDecodeError:
        return []
    if not isinstance(raw, list):
        return []

    out: list[Finding] = []
    for item in raw:
        if not isinstance(item, dict):
            continue
        try:
            ref = item.get("reference") or {}
            kind = ReferenceKind(str(ref.get("kind", "")).strip())
            target = str(ref.get("target", "")).strip()
            status = FindingStatus(str(item.get("status", "")).strip())
            if not target or status not in (
                FindingStatus.MISSING, FindingStatus.MOVED, FindingStatus.CHANGED
            ):
                continue
            out.append(
                Finding(
                    doc_path=doc_rel,
                    doc_line=int(item.get("doc_line") or 0),
                    claim=str(item.get("claim", ""))[:280],
                    reference=Reference(kind=kind, target=target),
                    status=status,
                    evidence=str(item.get("evidence", ""))[:400],
                    confidence=float(item.get("confidence") or 0.5),
                    verified=False,  # the verifier confirms before this is reported
                )
            )
        except (ValueError, TypeError):
            continue
    return out


class AletheiaWorker:
    """Spawn a headless `claude -p` scoped read-only to investigate one doc."""

    def __init__(self, *, mode: str = "full", model: str | None = None) -> None:
        self._mode = mode
        self._model = model or config.worker_model()

    async def run(self, doc_rel: str, workspace: str) -> WorkerResult:
        if not claude_available():
            return WorkerResult(success=False, error="`claude` CLI not found on PATH")

        cmd = build_command(
            build_prompt(doc_rel),
            allowed_tools=config.allowed_tools(),
            permission_mode="acceptEdits",  # no edit tools are allowed; avoids prompts
            max_turns=config.max_turns(self._mode),
            model=self._model,
        )
        # Enforce the exclusion denylist at the tool boundary.
        for spec in config.disallowed_tool_specs():
            cmd += ["--disallowedTools", spec]

        import asyncio
        import os
        try:
            proc = await asyncio.create_subprocess_exec(
                *cmd, cwd=workspace,
                stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE,
                env=os.environ.copy(),
            )
            out, err = await asyncio.wait_for(
                proc.communicate(), timeout=config.worker_timeout_s()
            )
        except asyncio.TimeoutError:
            return WorkerResult(success=False, error="worker timed out")
        except OSError as exc:
            return WorkerResult(success=False, error=f"spawn failed: {exc}")

        parsed = parse_stream_json(out.decode("utf-8", "replace"))
        if parsed["is_error"]:
            detail = parsed["result"] or err.decode("utf-8", "replace")[:300] or "claude error"
            return WorkerResult(
                success=False, error=detail,
                cost_usd=parsed["total_cost_usd"], session_id=parsed["session_id"],
            )
        return WorkerResult(
            success=True,
            findings=parse_findings(parsed["result"], doc_rel),
            cost_usd=parsed["total_cost_usd"],
            session_id=parsed["session_id"],
        )
