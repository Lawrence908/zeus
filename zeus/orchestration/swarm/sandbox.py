# zeus/orchestration/swarm/sandbox.py
"""Sandboxed argonaut (P1b): the same `claude -p` run, inside a container.

Identical Worker contract to ClaudeCodeWorker - only the execution boundary
changes. The node's git worktree is bind-mounted at /work; claude runs inside
an ephemeral, resource-capped, no-new-privileges container as the host user (so
the files it writes are owned by the host and the coordinator can commit them);
the host still owns all git operations.

The cost of this phase is auth + egress, not the agent:
  - Auth: a fresh container has no ~/.claude session, so ANTHROPIC_API_KEY is
    required and passed through (`-e ANTHROPIC_API_KEY`). This also makes spend
    attributable per run, which is what we want anyway.
  - Egress: the container needs to reach api.anthropic.com. Default network has
    it; a locked-down egress policy is a later hardening step.
"""

from __future__ import annotations

import asyncio
import logging
import os
import shutil

from zeus.orchestration.swarm import config
from zeus.orchestration.swarm.claude_worker import (
    _DEFAULT_ALLOWED_TOOLS,
    build_command,
    build_prompt,
    parse_stream_json,
)
from zeus.orchestration.swarm.models import Run, TaskNode
from zeus.orchestration.swarm.worker import WorkerResult

logger = logging.getLogger("zeus.swarm.sandbox")

_API_KEY_ENV = "ANTHROPIC_API_KEY"


def docker_available() -> bool:
    return shutil.which("docker") is not None


def build_docker_command(
    claude_argv: list[str],
    *,
    workspace: str,
    image: str,
    network: str,
    limits: dict[str, str],
    api_key_env: str = _API_KEY_ENV,
    run_as_host_user: bool = True,
) -> list[str]:
    """Wrap a claude argv in an ephemeral, capped `docker run`."""
    cmd = [
        "docker", "run", "--rm", "--init",
        "--network", network,
        "-v", f"{workspace}:/work",
        "-w", "/work",
        "--security-opt", "no-new-privileges",
        "--cap-drop", "ALL",
        "--memory", limits["memory"],
        "--cpus", limits["cpus"],
        "--pids-limit", limits["pids"],
        # Pass the key through by name (value comes from the parent env).
        "-e", api_key_env,
        # Give the CLI a writable HOME (mode 1777 so the --user uid can write it),
        # kept out of the mounted worktree.
        "--tmpfs", "/home/agent:rw,mode=1777",
        "-e", "HOME=/home/agent",
    ]
    if run_as_host_user:
        cmd += ["--user", f"{os.getuid()}:{os.getgid()}"]
    cmd += [image, *claude_argv]
    return cmd


class SandboxedClaudeWorker:
    """Run `claude -p` inside a container against the node's mounted worktree."""

    def __init__(self, *, permission_mode: str = "acceptEdits", max_turns: int = 30,
                 model: str | None = None, timeout_s: float = 1800) -> None:
        self._permission_mode = permission_mode
        self._max_turns = max_turns
        self._model = model
        self._timeout_s = timeout_s

    async def run(self, node: TaskNode, run: Run, workspace: str | None,
                  feedback: str | None = None) -> WorkerResult:
        if workspace is None:
            return WorkerResult(success=False, error="sandbox worker requires a worktree")
        if not docker_available():
            return WorkerResult(success=False, error="`docker` not found on PATH")
        if not os.environ.get(_API_KEY_ENV):
            return WorkerResult(
                success=False,
                error=f"{_API_KEY_ENV} must be set for the sandboxed worker (no host auth in the container)",
            )

        claude_argv = build_command(
            build_prompt(node, run, feedback),
            allowed_tools=node.tool_scope or _DEFAULT_ALLOWED_TOOLS,
            permission_mode=self._permission_mode,
            max_turns=self._max_turns,
            model=node.model or self._model,  # per-node routing (C1)
        )
        cmd = build_docker_command(
            claude_argv,
            workspace=workspace,
            image=config.sandbox_image(),
            network=config.sandbox_network(),
            limits=config.sandbox_limits(),
        )
        try:
            proc = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                env=os.environ.copy(),
            )
            out, err = await asyncio.wait_for(proc.communicate(), timeout=self._timeout_s)
        except asyncio.TimeoutError:
            return WorkerResult(success=False, error=f"sandbox timed out after {self._timeout_s}s")
        except OSError as exc:
            return WorkerResult(success=False, error=f"docker spawn failed: {exc}")

        parsed = parse_stream_json(out.decode("utf-8", "replace"))
        if parsed["is_error"]:
            detail = parsed["result"] or err.decode("utf-8", "replace")[:400] or "sandbox claude error"
            return WorkerResult(success=False, error=detail,
                                cost_usd=parsed["total_cost_usd"], session_id=parsed["session_id"])
        return WorkerResult(success=True, output=parsed["result"],
                            cost_usd=parsed["total_cost_usd"], session_id=parsed["session_id"])
