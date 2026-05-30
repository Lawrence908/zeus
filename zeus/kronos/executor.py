# zeus/kronos/executor.py — Dispatcher for Kronos jobs.
#
# Three modes:
#   - Built-in:  executor="zeus.kronos.jobs.x.y" — importlib + await callable(params).
#                Aegis pre (evaluate_payload) + post (evaluate_text) run here.
#   - Agent:     agent=<name>, endpoint=<path> — HTTP POST to /orchestration/call.
#                The bus already runs Aegis pre/post, so the executor does not
#                re-scan (would double-filter and mask bus responses).
#   - Shell:     executor="shell:..." — Phase 3; currently raises.
from __future__ import annotations

import asyncio
import importlib
import json
import logging
import time
import uuid
from datetime import datetime, timezone
from typing import Any

import httpx

from zeus.core.retry import with_retry
from zeus.kronos.models import JobDefinition, JobRun, JobStatus
from zeus.kronos.storage import JobStorage
from zeus.safety.policy_engine import AegisPolicyEngine, aegis_enabled, evaluate_text

logger = logging.getLogger("zeus.kronos")


def _new_correlation_id() -> str:
    return uuid.uuid4().hex[:12]


def _to_scanable_text(data: Any) -> str:
    if isinstance(data, str):
        return data
    try:
        return json.dumps(data, ensure_ascii=False, default=str)
    except (TypeError, ValueError):
        return str(data)


class AegisRejection(RuntimeError):
    """Raised when Aegis blocks a job's input payload or output."""


class KronosExecutor:
    """
    Runs a single JobDefinition to completion, writing results to JobStorage.

    The scheduler is responsible for calling ``storage.claim_fire`` first to
    record fire-intent atomically (so a crashed process leaves a recoverable
    PENDING row). The executor then takes the returned ``JobRun`` and drives
    it to a terminal status.
    """

    def __init__(
        self,
        storage: JobStorage,
        *,
        http_client: httpx.AsyncClient,
        bus_url: str,
    ) -> None:
        self._storage = storage
        self._http = http_client
        self._bus_url = bus_url.rstrip("/")

    async def run(self, job: JobDefinition, run: JobRun) -> JobRun:
        run.status = JobStatus.RUNNING
        run.started_at = datetime.now(timezone.utc)
        logger.info(
            "[kronos correlation_id=%s] start job=%s mode=%s",
            run.correlation_id,
            job.id,
            "agent" if job.agent else "shell" if _is_shell(job) else "builtin",
        )
        t0 = time.monotonic()
        try:
            if job.agent:
                output = await self._run_agent(job, run)
            elif _is_shell(job):
                raise NotImplementedError("Shell dispatch mode ships in Phase 3")
            else:
                output = await self._run_builtin(job, run)
            run.mark_finished(JobStatus.SUCCESS, output=output, error=None)
            logger.info(
                "[kronos correlation_id=%s] success job=%s duration=%.0fms",
                run.correlation_id, job.id, (time.monotonic() - t0) * 1000,
            )
        except asyncio.TimeoutError:
            run.mark_finished(
                JobStatus.TIMEOUT,
                output=None,
                error=f"timeout after {job.timeout_seconds}s",
            )
            logger.warning(
                "[kronos correlation_id=%s] timeout job=%s after %ds",
                run.correlation_id, job.id, job.timeout_seconds,
            )
        except AegisRejection as exc:
            run.mark_finished(JobStatus.FAILED, output=None, error=f"aegis: {exc}")
            logger.warning(
                "[kronos correlation_id=%s] aegis_blocked job=%s: %s",
                run.correlation_id, job.id, exc,
            )
        except Exception as exc:
            run.mark_finished(JobStatus.FAILED, output=None, error=str(exc))
            logger.exception(
                "[kronos correlation_id=%s] failed job=%s: %s",
                run.correlation_id, job.id, exc,
            )
        finally:
            await self._storage.finish_run(run)
        return run

    # -- Dispatch modes -------------------------------------------------------

    async def _run_builtin(self, job: JobDefinition, run: JobRun) -> str:
        assert job.executor, "builtin mode requires executor dotted path"

        # Aegis pre-hook on params.
        if aegis_enabled() and job.params:
            engine = AegisPolicyEngine(policy=job.safety_policy)
            outcome = engine.evaluate_payload(job.params, policy_name=job.safety_policy)
            if outcome.status == "rejected":
                raise AegisRejection(outcome.message or "input blocked")

        fn = _import_callable(job.executor)

        async def _call() -> Any:
            result = fn(job.params)
            if asyncio.iscoroutine(result):
                result = await result
            return result

        raw = await asyncio.wait_for(
            with_retry(
                _call,
                max_retries=job.max_retries,
                label=f"kronos:{job.id}",
            ),
            timeout=job.timeout_seconds,
        )
        summary = _summarise(raw)

        # Aegis post-hook on output.
        if aegis_enabled() and summary:
            outcome = evaluate_text(summary, policy_name=job.safety_policy)
            if outcome.status == "rejected":
                raise AegisRejection(outcome.message or "output blocked")

        return summary

    async def _run_agent(self, job: JobDefinition, run: JobRun) -> str:
        """Dispatch via the orchestration bus. Aegis hooks run on the bus side."""
        assert job.agent, "agent mode requires 'agent' field"
        payload = {
            "target_agent": job.agent,
            "endpoint": job.endpoint,
            "method": "POST",
            "payload": job.params,
            "correlation_id": run.correlation_id,
            "idempotent": False,
        }

        async def _call() -> Any:
            resp = await self._http.post(
                f"{self._bus_url}/orchestration/call",
                json=payload,
                timeout=job.timeout_seconds,
            )
            resp.raise_for_status()
            return resp.json()

        data = await asyncio.wait_for(
            with_retry(
                _call,
                max_retries=job.max_retries,
                label=f"kronos:{job.id}:agent",
            ),
            timeout=job.timeout_seconds,
        )
        # Surface bus-side errors as executor failures.
        if isinstance(data, dict) and data.get("status") == "error":
            raise RuntimeError(data.get("error") or "agent call failed")
        return _summarise(data)


def _is_shell(job: JobDefinition) -> bool:
    return bool(job.executor) and job.executor.startswith("shell:")


def _import_callable(dotted: str):
    module_path, _, attr = dotted.rpartition(".")
    if not module_path:
        raise ImportError(f"invalid executor path: {dotted!r}")
    module = importlib.import_module(module_path)
    try:
        return getattr(module, attr)
    except AttributeError as exc:
        raise ImportError(f"{dotted!r} not found in {module_path}") from exc


def _summarise(value: Any, *, max_len: int = 4000) -> str:
    text = _to_scanable_text(value)
    if len(text) > max_len:
        return text[:max_len] + "... [truncated]"
    return text
