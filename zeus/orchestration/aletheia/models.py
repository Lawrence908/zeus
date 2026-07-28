# zeus/orchestration/aletheia/models.py
"""Pydantic shapes for Aletheia: References, Findings, Runs.

A Finding is the unit of output. It is deliberately *structured* (not prose) so
the verifier can re-resolve it mechanically and the digest can track its
identity across weeks. Identity is ``sha1(doc_path + reference.target)`` so the
same drift keeps a stable id run-to-run (new vs carried-over vs fixed).
"""

from __future__ import annotations

import hashlib
from datetime import datetime, timezone
from enum import Enum

from pydantic import BaseModel, Field


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


class ReferenceKind(str, Enum):
    PATH = "path"          # `zeus/memory/store.py`
    SYMBOL = "symbol"      # `MemoryStore.get_profile_facts` / file::symbol
    ENV_VAR = "env_var"    # `ZEUS_KNOWLEDGE_HYBRID`
    ENDPOINT = "endpoint"  # `POST /swarm/runs`, `/admin/metrics`
    CONFIG_KEY = "config_key"  # a yaml/toml key claimed to exist
    COMMAND = "command"    # `python -m zeus.bench`


class FindingStatus(str, Enum):
    OK = "ok"                    # resolves as documented (counted, not reported)
    MISSING = "missing"          # referenced thing does not exist anywhere
    MOVED = "moved"              # exists, but not where the doc says
    CHANGED = "changed"          # exists in place but signature/default contradicts doc
    UNVERIFIABLE = "unverifiable"  # could not be resolved either way (stored, not reported)


class RunMode(str, Enum):
    FULL = "full"                # nightly sweep of all observe roots
    INCREMENTAL = "incremental"  # push-triggered, scoped to changed paths


class RunStatus(str, Enum):
    RUNNING = "running"
    COMPLETED = "completed"
    COMPLETED_PARTIAL = "completed_partial"  # fail-open: some docs errored
    FAILED = "failed"                        # nothing analysed
    CANCELLED = "cancelled"
    PAUSED_BUDGET = "paused_budget"          # hit the per-run ceiling


class DocStatus(str, Enum):
    OK = "ok"              # analysed to completion
    INCOMPLETE = "incomplete"  # errored/timed out; fail-open kept the rest of the sweep


class Reference(BaseModel):
    """One concrete claim a doc makes about the codebase."""

    kind: ReferenceKind
    target: str = Field(..., min_length=1)  # normalised: path, file::symbol, VAR, METHOD /route

    def normalised_target(self) -> str:
        return self.target.strip()


class Finding(BaseModel):
    """A candidate drift item. Only CONFIRMED, reportable statuses reach a human."""

    doc_path: str            # repo-relative path of the doc
    doc_line: int = 0
    claim: str = ""          # what the doc asserts (short)
    reference: Reference
    status: FindingStatus
    evidence: str = ""       # where the verifier looked / what it found
    confidence: float = 0.5
    # verifier linkage (set by the independent verifier, not the worker)
    verified: bool = False
    verifier_status: FindingStatus | None = None

    def identity(self) -> str:
        """Stable id: same doc + same referenced target => same finding over time."""
        key = f"{self.doc_path}\x00{self.reference.kind.value}\x00{self.reference.normalised_target()}"
        return hashlib.sha1(key.encode("utf-8")).hexdigest()  # noqa: S324 - identity, not security

    @property
    def reportable(self) -> bool:
        """Confirmed drift, excluding OK and UNVERIFIABLE (stored, not surfaced)."""
        return (
            self.verified
            and self.status in (FindingStatus.MISSING, FindingStatus.MOVED, FindingStatus.CHANGED)
        )


class DocResult(BaseModel):
    """Per-document node result in the fail-open sweep DAG."""

    doc_path: str
    status: DocStatus = DocStatus.OK
    findings: int = 0        # reportable findings emitted for this doc
    cost_usd: float = 0.0
    error: str | None = None


class AletheiaRun(BaseModel):
    id: str
    mode: RunMode
    status: RunStatus = RunStatus.RUNNING
    iso_week: str = ""       # e.g. "2026-W31"; groups findings for the weekly digest
    budget_usd: float = 3.0
    cost_usd: float = 0.0
    docs_total: int = 0
    docs_complete: int = 0
    docs_incomplete: int = 0
    findings_reportable: int = 0
    created_at: str = Field(default_factory=_now_iso)
    updated_at: str = Field(default_factory=_now_iso)


def iso_week(dt: datetime | None = None) -> str:
    dt = dt or datetime.now(timezone.utc)
    y, w, _ = dt.isocalendar()
    return f"{y}-W{w:02d}"
