# zeus/orchestration/swarm/ci.py
"""Poll CI status on a run's auto-opened PR (P8b), on demand via `gh`.

Stateless: the endpoint calls `gh pr checks <url>` when asked, so there's no
background poller or extra run column. Best-effort - no gh, no PR, or a gh error
all resolve to a benign status rather than raising.
"""

from __future__ import annotations

import asyncio
import json
import logging
import os
import shutil

from pydantic import BaseModel

logger = logging.getLogger("zeus.swarm.ci")


class CiCheck(BaseModel):
    name: str
    state: str  # pass | fail | pending | skipping | ...


class CiStatus(BaseModel):
    status: str  # no_pr | no_gh | unknown | passing | failing | pending | none
    checks: list[CiCheck] = []


def _rollup(checks: list[CiCheck]) -> str:
    if not checks:
        return "none"
    states = {c.state.lower() for c in checks}
    if states & {"fail", "failure", "error", "cancelled", "timed_out"}:
        return "failing"
    if states & {"pending", "in_progress", "queued", "waiting"}:
        return "pending"
    if states & {"pass", "success"}:
        return "passing"
    return "unknown"


async def pr_ci_status(pr_url: str | None, *, timeout_s: float = 30) -> CiStatus:
    if not pr_url:
        return CiStatus(status="no_pr")
    if shutil.which("gh") is None:
        return CiStatus(status="no_gh")
    try:
        proc = await asyncio.create_subprocess_exec(
            "gh", "pr", "checks", pr_url, "--json", "name,state",
            stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE,
            env=os.environ.copy(),
        )
        out, err = await asyncio.wait_for(proc.communicate(), timeout=timeout_s)
    except (asyncio.TimeoutError, OSError) as exc:
        logger.warning("gh pr checks failed: %s", exc)
        return CiStatus(status="unknown")
    # gh exits non-zero when checks are failing OR when there are none; parse anyway.
    try:
        rows = json.loads(out.decode("utf-8", "replace") or "[]")
    except json.JSONDecodeError:
        # "no checks reported" comes back as a message on stderr, not JSON.
        return CiStatus(status="none")
    checks = [CiCheck(name=str(r.get("name", "")), state=str(r.get("state", ""))) for r in rows]
    return CiStatus(status=_rollup(checks), checks=checks)
