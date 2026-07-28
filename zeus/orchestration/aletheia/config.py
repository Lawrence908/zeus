# zeus/orchestration/aletheia/config.py
"""Aletheia guardrails: what it may read, what it must never read, its budget.

Deliberate divergence from the coding swarm:

- OBSERVE ROOTS are *wide* and *read-only*. The swarm's write allowlist
  (``ZEUS_SWARM_REPO_ALLOWLIST``) is narrow. These are two separate lists and
  must never be conflated - Aletheia may observe a repo it can never edit.
- EXCLUSION GLOBS protect the personal-data layer (``.env``, ``zeus/data/**``,
  ``*.db``). Crucially these are *enforced*, not just documented: they compile
  into ``--disallowedTools`` deny specs passed to every worker (see
  ``disallowed_tool_specs``). Listing a glob a worker's Read tool ignores would
  be security theatre; the worker reads the live tree, so enforcement is at the
  tool boundary from day one, before any container sandbox lands.
"""

from __future__ import annotations

import fnmatch
import os

# Default observe root: just the zeus repo. Widen via env as other repos are
# vetted. An allowlist, never "~/" or "/" - those hold non-repos, .ssh, .env.
_DEFAULT_OBSERVE_ROOTS = "~/zeus"

# Personal-data layer. Never read, never quoted into a finding. zeus/data/**
# holds context_pack.md, the Obsidian mirror, sessions.db, the usage ledger.
_DEFAULT_EXCLUDE = (
    "**/.env,**/.env.*,**/.ssh/**,zeus/data/**,**/*.db,**/*.sqlite,**/*.sqlite3"
)

# Files that count as "documentation" for the sweep. Prose docs only.
_DEFAULT_DOC_GLOBS = "**/*.md,**/*.mdx,**/*.rst"

_TRUTHY = ("1", "true", "yes", "on")


def _realpath(p: str) -> str:
    return os.path.realpath(os.path.expanduser(p.strip()))


def _split(raw: str) -> list[str]:
    """Split on newlines or commas (env vars survive both forms)."""
    parts: list[str] = []
    for chunk in raw.replace("\n", ",").split(","):
        s = chunk.strip()
        if s:
            parts.append(s)
    return parts


# ---------------------------------------------------------------------------
# Observe roots (read scope)
# ---------------------------------------------------------------------------


def _unsafe_root(real: str) -> bool:
    """Reject roots that would expose the whole home dir or filesystem."""
    home = os.path.realpath(os.path.expanduser("~"))
    return real in ("", "/", home) or real == os.path.dirname(home)


def observe_roots() -> list[str]:
    """Absolute, de-duped, existing roots Aletheia may read.

    Unsafe roots (``/``, ``~``) are dropped, not honoured: a config typo must
    never widen the read scope to the whole home directory.
    """
    raw = os.getenv("ZEUS_ALETHEIA_OBSERVE_ROOTS", _DEFAULT_OBSERVE_ROOTS)
    out: list[str] = []
    for p in _split(raw):
        real = _realpath(p)
        if _unsafe_root(real) or not os.path.isdir(real):
            continue
        if real not in out:
            out.append(real)
    return out


def observe_allowed(path: str) -> bool:
    """True iff ``path`` resolves to a location under some observe root."""
    real = _realpath(path)
    for root in observe_roots():
        if real == root or real.startswith(root + os.sep):
            return True
    return False


# ---------------------------------------------------------------------------
# Exclusions (enforced, not decorative)
# ---------------------------------------------------------------------------


def exclusion_globs() -> list[str]:
    raw = os.getenv("ZEUS_ALETHEIA_EXCLUDE", _DEFAULT_EXCLUDE)
    return _split(raw)


def path_excluded(path: str) -> bool:
    """True iff a path (abs or repo-relative) matches any exclusion glob.

    Matches the full relative path, and - crucially - the basename against each
    glob's trailing segment. ``fnmatch`` does not treat ``/`` specially, so a
    pattern like ``**/.env`` would *not* match a bare ``.env`` at a root; the
    trailing-segment check closes that hole. Getting this wrong means reading
    the personal-data layer, so it is exercised directly in the tests.
    """
    rel = path.lstrip("/")
    base = os.path.basename(rel)
    for pat in exclusion_globs():
        # A `**/`-anchored glob must also match at the root: `**/.ssh/**` should
        # catch `.ssh/id_rsa` and `**/.env` should catch a bare `.env`. fnmatch
        # gives `/` no special meaning, so the `**/` prefix otherwise *requires*
        # a leading segment. Test the stripped form too. This is the exclusion
        # of the personal-data layer; a miss here is a real leak, so it is tested.
        candidates = [pat]
        if pat.startswith("**/"):
            candidates.append(pat[3:])
        if any(fnmatch.fnmatch(rel, c) for c in candidates):
            return True
        tail = pat.rsplit("/", 1)[-1]  # specific filename glob (not "*"/"**")
        if tail and tail not in ("*", "**") and fnmatch.fnmatch(base, tail):
            return True
    return False


def disallowed_tool_specs() -> list[str]:
    """Compile exclusion globs into Claude Code ``--disallowedTools`` specs.

    This is the enforcement of the exclusion list: the worker is told, at spawn
    time, that Read/Grep/Glob on these globs are denied. Deny beats allow in
    Claude Code's permission model, so even though Read is on the allowlist the
    personal-data globs are unreadable. Applied on the host tree today; the
    container ``:ro`` mount (when the sandbox lands) is defence in depth on top.
    """
    specs: list[str] = []
    for glob in exclusion_globs():
        for tool in ("Read", "Grep", "Glob"):
            specs.append(f"{tool}({glob})")
    return specs


# ---------------------------------------------------------------------------
# Tool allowlist (read-only)
# ---------------------------------------------------------------------------


def allowed_tools() -> list[str]:
    """Read-only investigator toolset. No Edit, no Write, no unrestricted Bash.

    Bash is scoped to two read-only git subcommands. Note this is a porous
    boundary on its own (shell arg globs are prefix matches); the hard
    guarantees are the absence of a writable worktree and the ``:ro`` mount.
    """
    raw = os.getenv(
        "ZEUS_ALETHEIA_ALLOWED_TOOLS",
        "Read,Grep,Glob,Bash(git log:*),Bash(git diff:*),Bash(git show:*)",
    )
    return _split(raw)


# ---------------------------------------------------------------------------
# Document discovery
# ---------------------------------------------------------------------------


def doc_globs() -> list[str]:
    raw = os.getenv("ZEUS_ALETHEIA_DOC_GLOBS", _DEFAULT_DOC_GLOBS)
    return _split(raw)


def is_doc(rel_path: str) -> bool:
    rel = rel_path.lstrip("/")
    for pat in doc_globs():
        # `**/*.md` must match a root-level `README.md` too; fnmatch's `/` is not
        # special, so also test the `**/`-stripped form (see path_excluded).
        if fnmatch.fnmatch(rel, pat):
            return True
        if pat.startswith("**/") and fnmatch.fnmatch(rel, pat[3:]):
            return True
    return False


# ---------------------------------------------------------------------------
# Budget + turns (per-mode: full sweep vs incremental push)
# ---------------------------------------------------------------------------


def max_usd_per_run(mode: str) -> float:
    """Hard spend ceiling for a run. Kill-switch enforced at doc boundaries."""
    if mode == "incremental":
        return float(os.getenv("ZEUS_ALETHEIA_MAX_USD_INCREMENTAL", "0.50"))
    return float(os.getenv("ZEUS_ALETHEIA_MAX_USD_FULL", "3.00"))


def max_turns(mode: str) -> int:
    """Per-document turn cap (the only within-document bound; turns != dollars)."""
    if mode == "incremental":
        return int(os.getenv("ZEUS_ALETHEIA_MAX_TURNS_INCREMENTAL", "12"))
    return int(os.getenv("ZEUS_ALETHEIA_MAX_TURNS_FULL", "25"))


def worker_timeout_s() -> float:
    return float(os.getenv("ZEUS_ALETHEIA_WORKER_TIMEOUT_S", "600"))


# ---------------------------------------------------------------------------
# Model + enable gate + schedule
# ---------------------------------------------------------------------------


def worker_model() -> str:
    """Investigation is read-and-reason; a cheap fast model is the default."""
    return os.getenv("ZEUS_ALETHEIA_MODEL", "haiku").strip() or "haiku"


def enabled() -> bool:
    return os.getenv("ZEUS_ALETHEIA_ENABLED", "0").strip().lower() in _TRUTHY


def schedule_cron() -> str:
    """Nightly off-peak sweep. Kronos owns the actual firing."""
    return os.getenv("ZEUS_ALETHEIA_SCHEDULE", "0 3 * * *").strip()


def digest_cron() -> str:
    """Weekly digest. Default: Monday 08:00."""
    return os.getenv("ZEUS_ALETHEIA_DIGEST_SCHEDULE", "0 8 * * 1").strip()


def notify_incremental() -> bool:
    """Push an immediate Telegram message for incremental (push-triggered) runs."""
    return os.getenv("ZEUS_ALETHEIA_NOTIFY_INCREMENTAL", "1").strip().lower() in _TRUTHY


def db_path() -> str:
    return os.getenv("ZEUS_ALETHEIA_DB_PATH", "zeus/data/aletheia.db")


def digest_dir() -> str:
    return os.getenv("ZEUS_ALETHEIA_DIGEST_DIR", "zeus/data/research/aletheia")


def findings_retention_days() -> int:
    """Keep findings this long so the digest can compute new/carried/fixed trends."""
    return int(os.getenv("ZEUS_ALETHEIA_RETENTION_DAYS", "90"))
