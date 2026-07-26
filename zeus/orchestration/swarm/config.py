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


def planner_model() -> str:
    """Model Metis uses to scope a goal into a DAG (set cheaper to save)."""
    return os.getenv("ZEUS_SWARM_PLANNER_MODEL", model_default())


def planner_max_turns() -> int:
    return int(os.getenv("ZEUS_SWARM_PLANNER_MAX_TURNS", "20"))


# ---------------------------------------------------------------------------
# Local worker tier (C4) - trivial nodes on the homelab Ollama GPU, $0.
# ---------------------------------------------------------------------------

_LOCAL_ALIASES = ("local", "ollama")


def ollama_url() -> str:
    """Base URL for the local Ollama the LocalWorker calls (reuses OLLAMA_URL)."""
    raw = os.getenv("ZEUS_SWARM_OLLAMA_URL") or os.getenv("OLLAMA_URL", "http://localhost:11435")
    return raw.rstrip("/")


def local_model() -> str:
    """Ollama tag the LocalWorker runs (must be pulled on the host)."""
    return os.getenv("ZEUS_SWARM_LOCAL_MODEL", "qwen2.5:7b-instruct")


def is_local_model(model: str) -> bool:
    """True if a node's model hint routes to the free local tier.

    Matches the aliases "local"/"ollama" and any concrete Ollama tag (which carry
    a ":" size suffix, e.g. "qwen2.5:7b-instruct"), so the planner can name either.
    """
    m = (model or "").strip().lower()
    if not m:
        return False
    return m in _LOCAL_ALIASES or ":" in m


def resolve_local_model(model: str) -> str:
    """Concrete Ollama tag for a node routed local (aliases -> configured default)."""
    m = (model or "").strip().lower()
    return local_model() if m in _LOCAL_ALIASES or not m else model.strip()


def hybrid_local() -> bool:
    """Whether a paid run also routes local-tagged nodes to the free tier."""
    return os.getenv("ZEUS_SWARM_HYBRID_LOCAL", "1").strip().lower() in ("1", "true", "yes", "on")


def sandbox_limits() -> dict[str, str]:
    return {
        "memory": os.getenv("ZEUS_SWARM_SANDBOX_MEMORY", "2g"),
        "cpus": os.getenv("ZEUS_SWARM_SANDBOX_CPUS", "2"),
        "pids": os.getenv("ZEUS_SWARM_SANDBOX_PIDS", "512"),
    }


# ---------------------------------------------------------------------------
# Verify sandbox (P5) - the node's `check` is LLM-authored shell, so it must run
# isolated, not on the host. Own image (needs the repo's test toolchain) and its
# own, tighter network default (checks should not need egress).
# ---------------------------------------------------------------------------


def verify_sandbox() -> bool:
    """Whether `node.check` runs in a container (P5). Off = legacy host exec."""
    return os.getenv("ZEUS_SWARM_VERIFY_SANDBOX", "1").strip().lower() in ("1", "true", "yes", "on")


def verify_host_fallback() -> bool:
    """If the verify sandbox can't run (no docker/image), fall back to host exec.

    On by default so dev doesn't hard-break; the coordinator logs a loud WARNING
    when it happens. Set to 0 to fail closed (a check that can't be sandboxed
    fails) on hosts where running LLM-authored shell on the host is unacceptable.
    """
    return os.getenv("ZEUS_SWARM_VERIFY_HOST_FALLBACK", "1").strip().lower() in ("1", "true", "yes", "on")


def verify_image() -> str:
    """Image the check runs in - must carry the repo's test toolchain + deps."""
    return os.getenv("ZEUS_SWARM_VERIFY_IMAGE", "zeus-swarm-verify:latest")


def verify_network() -> str:
    """Checks should not need egress; default `none`. Widen per-stack if a check
    must fetch (e.g. `pip install`)."""
    return os.getenv("ZEUS_SWARM_VERIFY_NETWORK", "none")


def verify_limits() -> dict[str, str]:
    return {
        "memory": os.getenv("ZEUS_SWARM_VERIFY_MEMORY", "2g"),
        "cpus": os.getenv("ZEUS_SWARM_VERIFY_CPUS", "2"),
        "pids": os.getenv("ZEUS_SWARM_VERIFY_PIDS", "512"),
    }
