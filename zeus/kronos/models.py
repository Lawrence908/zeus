# zeus/kronos/models.py — Pydantic shapes for the Kronos scheduler.
from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field, field_validator, model_validator


class JobStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"
    TIMEOUT = "timeout"
    CANCELLED = "cancelled"
    LOST = "lost"  # scheduler crashed mid-run; row reaped on next boot


class JobCategory(str, Enum):
    BRIEFING = "briefing"
    INGEST = "ingest"
    MEMORY_REVIEW = "memory_review"
    MAINTENANCE = "maintenance"
    RESEARCH = "research"
    JOB_SEARCH = "job_search"
    HEALTH = "health"
    CUSTOM = "custom"


class JobSchedule(BaseModel):
    """Either a cron expression or a one-off datetime. Exactly one must be set."""

    cron: str | None = None
    timezone: str = "UTC"
    run_at: datetime | None = None  # one-off; auto-disables after firing

    @model_validator(mode="after")
    def _exactly_one(self) -> "JobSchedule":
        if (self.cron is None) == (self.run_at is None):
            raise ValueError("JobSchedule requires exactly one of 'cron' or 'run_at'")
        return self

    @field_validator("cron")
    @classmethod
    def _validate_cron(cls, v: str | None) -> str | None:
        if v is None:
            return v
        # Defer full parsing to croniter at scheduler time; reject obvious junk here.
        parts = v.split()
        if len(parts) not in (5, 6):
            raise ValueError(f"cron must be 5 or 6 fields, got: {v!r}")
        return v


class JobDefinition(BaseModel):
    id: str
    name: str
    description: str = ""
    category: JobCategory = JobCategory.CUSTOM
    schedule: JobSchedule
    executor: str | None = None  # "zeus.kronos.jobs.x.y" for built-in; "shell:..." for shell mode
    agent: str | None = None     # bus target name; if set, executor field is ignored
    endpoint: str = "/run"       # agent endpoint; only used when agent is set
    params: dict[str, Any] = Field(default_factory=dict)
    safety_policy: str = "standard"
    timeout_seconds: int = 300
    max_retries: int = 1
    tags: list[str] = Field(default_factory=list)
    enabled: bool = True

    @model_validator(mode="after")
    def _executor_or_agent(self) -> "JobDefinition":
        if not self.executor and not self.agent:
            raise ValueError("JobDefinition requires either 'executor' or 'agent'")
        if self.executor and self.agent:
            raise ValueError("JobDefinition: set one of 'executor' or 'agent', not both")
        return self


class JobRun(BaseModel):
    id: str                          # uuid4
    job_id: str
    correlation_id: str
    status: JobStatus
    started_at: datetime
    finished_at: datetime | None = None
    duration_ms: float | None = None
    output_summary: str | None = None
    error: str | None = None
    attempts: int = 1                # 1 on first try; incremented on retries

    def mark_finished(self, status: JobStatus, *, output: str | None, error: str | None) -> None:
        now = datetime.now(timezone.utc)
        self.finished_at = now
        self.duration_ms = (now - self.started_at).total_seconds() * 1000.0
        self.status = status
        self.output_summary = output
        self.error = error
