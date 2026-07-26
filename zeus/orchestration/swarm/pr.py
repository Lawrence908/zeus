# zeus/orchestration/swarm/pr.py
"""Open a GitHub PR from a run's integration branch at the final gate (P7).

Best-effort and OPT-IN (config.auto_pr()): pushes `swarm/run-<id>` to origin and
runs `gh pr create`. Any failure (no gh, no remote, no auth) returns a PrResult
with an error and never crashes the gate - the branch is still there to PR by
hand. The final human approval is the authorization for this outward action.
"""

from __future__ import annotations

import asyncio
import logging
import os
import shutil

from pydantic import BaseModel

from zeus.orchestration.swarm import config
from zeus.orchestration.swarm.models import Run

logger = logging.getLogger("zeus.swarm.pr")


class PrResult(BaseModel):
    url: str | None = None
    error: str | None = None


async def _run(cmd: list[str], cwd: str, timeout_s: float = 120) -> tuple[int, str, str]:
    proc = await asyncio.create_subprocess_exec(
        *cmd, cwd=cwd,
        stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE,
        env=os.environ.copy(),
    )
    out, err = await asyncio.wait_for(proc.communicate(), timeout=timeout_s)
    return proc.returncode or 0, out.decode("utf-8", "replace"), err.decode("utf-8", "replace")


async def _default_base(repo: str) -> str:
    """origin's default branch (origin/HEAD -> main/master); fall back to 'main'."""
    if config.pr_base():
        return config.pr_base()
    rc, out, _ = await _run(["git", "symbolic-ref", "--short", "refs/remotes/origin/HEAD"], repo)
    if rc == 0 and out.strip().startswith("origin/"):
        return out.strip()[len("origin/"):]
    return "main"


def build_pr_body(run: Run, nodes_summary: str) -> str:
    lines = [
        f"Autonomous swarm run `{run.id}` completed the goal:",
        "",
        f"> {run.goal}",
        "",
        "## Nodes",
        nodes_summary or "(none)",
    ]
    if run.project_check:
        state = "passed" if run.project_check_passed else "not verified"
        lines += ["", f"Project check `{run.project_check}`: **{state}**."]
    lines += [
        "",
        "Generated with [Claude Code](https://claude.com/claude-code) via the Argo swarm.",
    ]
    return "\n".join(lines)


class PullRequestOpener:
    """Push the integration branch and open a PR via `gh`."""

    def __init__(self, *, timeout_s: float = 120) -> None:
        self._timeout_s = timeout_s

    async def open(self, run: Run, branch: str, nodes_summary: str = "") -> PrResult:
        repo = os.path.realpath(os.path.expanduser(run.repo))
        if shutil.which("git") is None:
            return PrResult(error="git not found on PATH")
        if shutil.which("gh") is None:
            return PrResult(error="gh CLI not found on PATH (cannot open PR)")
        try:
            rc, _, err = await _run(["git", "push", "-u", "origin", branch], repo, self._timeout_s)
            if rc != 0:
                return PrResult(error=f"git push failed: {err.strip()[:300]}")
            base = await _default_base(repo)
            title = f"swarm: {run.goal}"[:120]
            body = build_pr_body(run, nodes_summary)
            rc, out, err = await _run(
                ["gh", "pr", "create", "--head", branch, "--base", base,
                 "--title", title, "--body", body],
                repo, self._timeout_s,
            )
            if rc != 0:
                return PrResult(error=f"gh pr create failed: {err.strip()[:300]}")
            url = next((ln.strip() for ln in out.splitlines() if ln.strip().startswith("http")), out.strip())
            logger.info("swarm %s: opened PR %s", run.id, url)
            return PrResult(url=url)
        except (asyncio.TimeoutError, OSError) as exc:
            return PrResult(error=f"PR open errored: {exc}")
