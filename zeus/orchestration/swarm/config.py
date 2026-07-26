# zeus/orchestration/swarm/config.py
"""Swarm guardrail config: which repos are targetable, which paths are off-limits.

Two lists, both env-overridable:

- REPO ALLOWLIST - absolute repo paths a run may target. Ships with just the
  zeus repo; adding canary/AstrID later is a config edit, not a refactor.
  Rejecting "anything under ~/" is deliberate: ~ holds non-repos, .ssh, and
  stray .env files, and a worktree needs a git repo anyway.
- PATH DENYLIST - globs a worker's diff may never touch, enforced by the
  coordinator when it inspects the diff (P1), not just via tool args. Covers the
  swarm's own supervisory code and Aegis policies: an agent that can weaken its
  own policy has no policy.
"""

from __future__ import annotations

import fnmatch
import os

_DEFAULT_REPO_ALLOWLIST = "~/zeus"
_DEFAULT_PATH_DENYLIST = (
    "zeus/safety/policies/**,zeus/orchestration/**,.git/**,"
    ".env,.env.*,*/.env,*/.env.*"
)


def _realpath(p: str) -> str:
    return os.path.realpath(os.path.expanduser(p.strip()))


def repo_allowlist() -> list[str]:
    raw = os.getenv("ZEUS_SWARM_REPO_ALLOWLIST", _DEFAULT_REPO_ALLOWLIST)
    return [_realpath(p) for p in raw.split(",") if p.strip()]


def repo_allowed(path: str) -> bool:
    """True iff `path` resolves to a repo on the allowlist."""
    return _realpath(path) in repo_allowlist()


def path_denylist() -> list[str]:
    raw = os.getenv("ZEUS_SWARM_PATH_DENYLIST", _DEFAULT_PATH_DENYLIST)
    return [p.strip() for p in raw.split(",") if p.strip()]


def path_denied(rel_path: str) -> bool:
    """True iff a repo-relative path matches any denylist glob.

    Used by the coordinator on every changed path in a worker's diff before the
    node's worktree is merged into the run integration branch.
    """
    rel = rel_path.lstrip("/")
    return any(fnmatch.fnmatch(rel, pat) for pat in path_denylist())


def denied_paths(rel_paths: list[str]) -> list[str]:
    return [p for p in rel_paths if path_denied(p)]


# ---------------------------------------------------------------------------
# Sandbox (P1b) - container knobs for the sandboxed argonaut.
# ---------------------------------------------------------------------------


def sandbox_image() -> str:
    return os.getenv("ZEUS_SWARM_SANDBOX_IMAGE", "zeus-swarm-argonaut:latest")


def sandbox_network() -> str:
    # Needs egress to api.anthropic.com. Lock down to a dedicated network later.
    return os.getenv("ZEUS_SWARM_SANDBOX_NETWORK", "bridge")


def model_default() -> str:
    """Strong model for logic/multi-file nodes (claude CLI alias or full id)."""
    return os.getenv("ZEUS_SWARM_MODEL_DEFAULT", "sonnet")


def model_cheap() -> str:
    """Cheap model for trivial nodes (docs, config, single-file, rename)."""
    return os.getenv("ZEUS_SWARM_MODEL_CHEAP", "haiku")


def sandbox_limits() -> dict[str, str]:
    return {
        "memory": os.getenv("ZEUS_SWARM_SANDBOX_MEMORY", "2g"),
        "cpus": os.getenv("ZEUS_SWARM_SANDBOX_CPUS", "2"),
        "pids": os.getenv("ZEUS_SWARM_SANDBOX_PIDS", "512"),
    }
