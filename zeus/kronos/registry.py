# zeus/kronos/registry.py — CRUD wrapper over JobStorage + idempotent YAML seed.
from __future__ import annotations

import logging
import os
import re
from datetime import datetime
from pathlib import Path
from typing import Any

import yaml

from zeus.kronos.models import JobDefinition, JobRun, JobSchedule, JobStatus
from zeus.kronos.storage import JobStorage

logger = logging.getLogger("zeus.kronos")

# ${VAR} / ${VAR:-default} interpolation for seed YAML values (same spirit as
# zeus/ingest/config.py). Lets e.g. PHEME_DIGEST_HOUR shape a seed cron without
# templating the file. Only applies at first insert - live jobs are never touched.
_SEED_ENV_RE = re.compile(r"\$\{([A-Za-z_][A-Za-z0-9_]*)(?::-([^}]*))?\}")


def _expand_seed_env(value: Any) -> Any:
    if isinstance(value, str):
        return _SEED_ENV_RE.sub(
            lambda m: os.environ.get(m.group(1)) or (m.group(2) or ""), value
        )
    if isinstance(value, list):
        return [_expand_seed_env(v) for v in value]
    if isinstance(value, dict):
        return {k: _expand_seed_env(v) for k, v in value.items()}
    return value


class KronosRegistry:
    """Facade over a JobStorage with YAML-seed loading."""

    def __init__(self, storage: JobStorage) -> None:
        self._storage = storage

    @property
    def storage(self) -> JobStorage:
        return self._storage

    # -- CRUD passthroughs ----------------------------------------------------

    async def add(self, job: JobDefinition) -> None:
        await self._storage.upsert_job(job)

    async def get(self, job_id: str) -> JobDefinition | None:
        return await self._storage.get_job(job_id)

    async def list(self, *, enabled: bool | None = None) -> list[JobDefinition]:
        return await self._storage.list_jobs(enabled=enabled)

    async def set_enabled(self, job_id: str, enabled: bool) -> bool:
        return await self._storage.set_enabled(job_id, enabled)

    async def delete(self, job_id: str) -> bool:
        return await self._storage.delete_job(job_id)

    async def last_fired_at(self, job_id: str) -> datetime | None:
        return await self._storage.get_last_fired_at(job_id)

    async def list_runs(self, **kwargs: Any) -> list[JobRun]:
        return await self._storage.list_runs(**kwargs)

    async def get_run(self, run_id: str) -> JobRun | None:
        return await self._storage.get_run(run_id)

    # -- YAML seed ------------------------------------------------------------

    async def seed_from_yaml(self, path: Path | str) -> list[str]:
        """
        Insert any jobs from the YAML file whose ids are not already in storage.

        Idempotent: re-running never clobbers user edits. Returns the list of
        ids that were newly inserted.
        """
        p = Path(path)
        if not p.is_file():
            logger.info("kronos seed YAML not found at %s, skipping", p)
            return []

        with open(p, encoding="utf-8") as f:
            doc = _expand_seed_env(yaml.safe_load(f) or {})
        raw_jobs = doc.get("jobs") or []
        if not isinstance(raw_jobs, list):
            logger.warning("kronos seed YAML has no 'jobs' list, skipping")
            return []

        inserted: list[str] = []
        for entry in raw_jobs:
            try:
                job = _parse_seed_entry(entry)
            except Exception as exc:
                logger.error("kronos seed: bad entry %r: %s", entry.get("id"), exc)
                continue
            if await self._storage.insert_if_absent(job):
                inserted.append(job.id)
                logger.info("kronos seed: inserted %s", job.id)
        return inserted

    async def reap_orphans(self, *, max_age_seconds: float) -> int:
        count = await self._storage.reap_orphans(max_age_seconds=max_age_seconds)
        if count:
            logger.warning("kronos: marked %d orphan run(s) as LOST on boot", count)
        return count


def _parse_seed_entry(entry: dict) -> JobDefinition:
    """Translate the YAML shape into a JobDefinition, normalising nested schedule."""
    sched_raw = entry.get("schedule") or {}
    schedule = JobSchedule(
        cron=sched_raw.get("cron"),
        timezone=sched_raw.get("timezone", "UTC"),
        run_at=sched_raw.get("run_at"),
    )
    data = {**entry, "schedule": schedule}
    return JobDefinition.model_validate(data)
