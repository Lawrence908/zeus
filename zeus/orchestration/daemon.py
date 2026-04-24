# zeus/orchestration/daemon.py — KAIROS background agent daemon (LAB-330)
#
# Observe → decide → act → update-memory loop. Runs inside the zeus-core
# FastAPI lifespan, gated by ZEUS_KAIROS_ENABLED. Every cycle is bounded,
# every tool arg is validated by Aegis, and nothing autonomous leaves the
# read-only tool allowlist unless operator flips both ZEUS_SHELL_ENABLED
# and the allowlist knob.
from __future__ import annotations

import asyncio
import datetime as dt
import json
import logging
import os
import re
from dataclasses import dataclass, field
from typing import Any, Protocol

import httpx
from pydantic import BaseModel, Field, ValidationError

from zeus.memory.search import search_memories
from zeus.safety.integration import aegis_bus_pre_hook

logger = logging.getLogger("zeus.kairos")

_DEFAULT_ALLOWLIST = "zeus_memory_search"
_DEFAULT_INTERVAL_MIN = 60
_DEFAULT_MAX_ACTIONS = 5
_EXEC_LOG_NAMESPACE = "execution_log"


# ------------------------------------------------------------------
# Data models
# ------------------------------------------------------------------


@dataclass
class Observation:
    source: str
    summary: str
    raw: dict[str, Any] = field(default_factory=dict)
    timestamp: dt.datetime = field(default_factory=lambda: dt.datetime.now(dt.timezone.utc))


class ToolCall(BaseModel):
    tool: str
    args: dict[str, Any] = Field(default_factory=dict)
    rationale: str = ""


class CognitivePlan(BaseModel):
    steps: list[ToolCall] = Field(default_factory=list)
    summary: str = ""


@dataclass
class StepExecution:
    tool: str
    status: str  # "ok" | "rejected" | "error"
    data: Any = None
    error: str | None = None


@dataclass
class KairosState:
    enabled: bool = False
    cycle_count: int = 0
    errors: int = 0
    last_cycle_at: dt.datetime | None = None
    last_action_summary: str = ""
    last_observations: list[str] = field(default_factory=list)

    def snapshot(self) -> dict[str, Any]:
        return {
            "enabled": self.enabled,
            "cycle_count": self.cycle_count,
            "errors": self.errors,
            "last_cycle_at": self.last_cycle_at.isoformat() if self.last_cycle_at else None,
            "last_action_summary": self.last_action_summary,
            "last_observations": list(self.last_observations),
        }


# ------------------------------------------------------------------
# Olympian read-side dispatch helpers
# ------------------------------------------------------------------


def _core_url() -> str:
    return os.getenv("ZEUS_CORE_URL", "http://127.0.0.1:8203").rstrip("/")


async def _http_get_json(path: str, params: dict[str, Any] | None = None, timeout: float = 10.0) -> Any:
    async with httpx.AsyncClient(timeout=timeout) as client:
        r = await client.get(f"{_core_url()}{path}", params=params)
        r.raise_for_status()
        return r.json() or {}


async def _http_post_json(path: str, payload: dict[str, Any], timeout: float = 15.0) -> Any:
    async with httpx.AsyncClient(timeout=timeout) as client:
        r = await client.post(f"{_core_url()}{path}", json=payload)
        r.raise_for_status()
        return r.json() or {}


async def _dispatch_status_read(args: dict[str, Any]) -> Any:
    return await _http_get_json("/admin/status_file")


async def _dispatch_server_health(args: dict[str, Any]) -> Any:
    return await _http_get_json("/admin/system")


async def _dispatch_file_read(args: dict[str, Any]) -> Any:
    path = str(args.get("path") or "").strip()
    if not path:
        raise ValueError("olympian_file_read requires 'path'")
    return await _http_get_json("/vault/file", params={"path": path})


async def _dispatch_file_search(args: dict[str, Any]) -> Any:
    pattern = str(args.get("pattern") or "").strip()
    if not pattern:
        raise ValueError("olympian_file_search requires 'pattern'")
    payload: dict[str, Any] = {
        "pattern": pattern,
        "max_results": max(1, min(500, int(args.get("max_results") or 50))),
        "case_sensitive": bool(args.get("case_sensitive") or False),
        "fixed_strings": bool(args.get("fixed_strings") or False),
    }
    if args.get("root"):
        payload["root"] = str(args["root"])
    return await _http_post_json("/vault/search", payload)


async def _dispatch_calendar_today(args: dict[str, Any]) -> Any:
    return await _http_get_json("/calendar/today")


async def _dispatch_newsletter_latest(args: dict[str, Any]) -> Any:
    data = await _http_get_json("/api/newsletter/digests", params={"limit": 1})
    digests = (data or {}).get("digests") or []
    return {"digest": digests[0] if digests else None, "exists": bool(digests)}


_OLYMPIAN_READONLY_DISPATCH: dict[str, Any] = {
    "olympian_status_read": _dispatch_status_read,
    "olympian_server_health": _dispatch_server_health,
    "olympian_file_read": _dispatch_file_read,
    "olympian_file_search": _dispatch_file_search,
    "zeus_calendar_today": _dispatch_calendar_today,
    "zeus_newsletter_latest": _dispatch_newsletter_latest,
}


# ------------------------------------------------------------------
# Observation sources
# ------------------------------------------------------------------


class ObservationSource(Protocol):
    async def observe(self) -> Observation | None: ...


class MemoryDriftObserver:
    """Flag new curated-memory writes since the last cycle.

    Uses ``search_memories`` on a broad query and tracks the newest
    ``created_at``/``updated_at`` timestamp seen. Returns None on idle
    cycles (no new writes).
    """

    def __init__(self, user_id: str = "user") -> None:
        self._user_id = user_id
        self._watermark: str = ""  # ISO-8601 string from MemoryStore payload

    async def observe(self) -> Observation | None:
        try:
            results = await asyncio.to_thread(
                search_memories,
                query="recent changes updates new entries",
                user_id=self._user_id,
                top_k=5,
                namespaces=None,
            )
        except Exception as exc:
            logger.warning("kairos memory drift observer failed: %s", exc)
            return None

        newest = ""
        latest_text = ""
        for mem in results:
            md = mem.get("metadata") or {}
            ts = str(md.get("updated_at") or md.get("created_at") or "")
            if ts > newest:  # ISO-8601 compares lexicographically
                newest = ts
                latest_text = str(mem.get("memory", ""))[:200]

        if not newest or newest <= self._watermark:
            return None

        self._watermark = newest
        return Observation(
            source="memory_drift",
            summary=f"New memory since last cycle: {latest_text}",
            raw={"watermark": newest, "count": len(results)},
        )


# ------------------------------------------------------------------
# Agent
# ------------------------------------------------------------------


_JSON_BLOCK_RE = re.compile(r"\{.*\}", re.DOTALL)


class KairosAgent:
    def __init__(
        self,
        *,
        llm_fn,
        observers: list[ObservationSource],
        state: KairosState,
        allowlist: list[str],
        max_actions: int,
        user_id: str = "user",
    ) -> None:
        self._llm = llm_fn
        self._observers = observers
        self._state = state
        self._allowlist = [t.strip() for t in allowlist if t.strip()]
        self._max_actions = max_actions
        self._user_id = user_id

    async def observe(self) -> list[Observation]:
        out: list[Observation] = []
        for src in self._observers:
            try:
                obs = await src.observe()
            except Exception as exc:
                logger.warning("kairos observer %s raised: %s", src, exc)
                continue
            if obs is not None:
                out.append(obs)
        self._state.last_observations = [o.summary[:120] for o in out]
        return out

    async def decide(self, observations: list[Observation]) -> CognitivePlan:
        if not observations:
            return CognitivePlan(steps=[], summary="idle")

        obs_block = "\n".join(f"- [{o.source}] {o.summary}" for o in observations)
        allowed = ", ".join(self._allowlist) or "(none)"
        system = (
            "You are KAIROS, a cautious background agent for this Zeus assistant instance. "
            "You run read-only introspection cycles. Given observations, propose at most "
            f"{self._max_actions} tool calls, each using ONLY these tools: {allowed}. "
            "Never propose shell or write operations. Respond with a single JSON object "
            'of shape {"summary": "...", "steps": [{"tool": "...", "args": {...}, '
            '"rationale": "..."}]}. If no action is useful, return an empty steps list.'
        )
        user_prompt = f"Observations:\n{obs_block}\n\nPlan:"
        try:
            raw = await self._llm(system=system, user_prompt=user_prompt, max_tokens=512)
        except Exception as exc:
            logger.warning("kairos decide LLM call failed: %s", exc)
            return CognitivePlan(steps=[], summary=f"llm_error: {exc}")

        match = _JSON_BLOCK_RE.search(raw or "")
        if not match:
            logger.info("kairos decide returned no JSON, raw=%r", (raw or "")[:200])
            return CognitivePlan(steps=[], summary="parse_empty")

        try:
            data = json.loads(match.group(0))
            plan = CognitivePlan.model_validate(data)
        except (json.JSONDecodeError, ValidationError) as exc:
            logger.warning("kairos plan parse failed: %s", exc)
            return CognitivePlan(steps=[], summary=f"parse_error: {exc}")

        if len(plan.steps) > self._max_actions:
            logger.info(
                "kairos truncating plan from %d to %d steps",
                len(plan.steps), self._max_actions,
            )
            plan.steps = plan.steps[: self._max_actions]
        return plan

    async def act(self, plan: CognitivePlan) -> list[StepExecution]:
        results: list[StepExecution] = []
        for step in plan.steps:
            if step.tool not in self._allowlist:
                logger.warning(
                    "kairos rejected tool %r not in allowlist %s",
                    step.tool, self._allowlist,
                )
                results.append(
                    StepExecution(
                        tool=step.tool,
                        status="rejected",
                        error="not_in_allowlist",
                    )
                )
                continue

            # Aegis pre-hook on every tool call.
            try:
                await aegis_bus_pre_hook(
                    {
                        "target_agent": "kairos",
                        "endpoint": step.tool,
                        "safety_policy": "standard",
                        "payload": step.args,
                    }
                )
            except Exception as exc:
                logger.warning(
                    "kairos aegis rejected %s args: %s", step.tool, exc
                )
                results.append(
                    StepExecution(
                        tool=step.tool, status="rejected", error=str(exc)
                    )
                )
                continue

            try:
                data = await self._dispatch(step.tool, step.args)
                results.append(StepExecution(tool=step.tool, status="ok", data=data))
            except Exception as exc:
                logger.warning("kairos tool %s raised: %s", step.tool, exc)
                results.append(
                    StepExecution(tool=step.tool, status="error", error=str(exc))
                )
        return results

    async def _dispatch(self, tool: str, args: dict[str, Any]) -> Any:
        """Tool dispatch. Read-only only; extend as olympian_* pack lands.

        Olympian read-side tools route through the Core HTTP loopback so the
        endpoint's internal allowlist enforcement and Aegis policies apply
        identically whether the call comes from MCP, the chat path, or here.
        """
        if tool == "zeus_memory_search":
            query = str(args.get("query", "")).strip()
            if not query:
                return {"results": []}
            limit = int(args.get("limit", 5))
            hits = await asyncio.to_thread(
                search_memories,
                query=query,
                user_id=self._user_id,
                top_k=max(1, min(20, limit)),
            )
            return {"count": len(hits)}

        if tool in _OLYMPIAN_READONLY_DISPATCH:
            handler = _OLYMPIAN_READONLY_DISPATCH[tool]
            return await handler(args)

        raise RuntimeError(f"tool dispatch not implemented: {tool}")

    async def update_memory(
        self,
        observations: list[Observation],
        plan: CognitivePlan,
        executions: list[StepExecution],
    ) -> None:
        summary = plan.summary or "idle"
        self._state.last_action_summary = summary[:200]

        # Write a compact audit line via MemoryStore as a raw chunk (no extraction).
        from zeus.memory.store import get_memory_store

        line = (
            f"kairos cycle: obs={len(observations)} steps={len(executions)} "
            f"summary={summary[:120]}"
        )
        try:
            store = get_memory_store()
            await store.add_text(
                line,
                source="kairos",
                source_id=f"kairos:cycle:{self._state.cycle_count}",
                user_id=self._user_id,
                extract_facts=False,
                metadata={"namespace": _EXEC_LOG_NAMESPACE, "cycle": self._state.cycle_count},
            )
        except Exception as exc:
            logger.warning("kairos memory write failed: %s", exc)


# ------------------------------------------------------------------
# Daemon wrapper
# ------------------------------------------------------------------


class KairosDaemon:
    def __init__(
        self,
        agent: KairosAgent,
        state: KairosState,
        interval_seconds: float,
    ) -> None:
        self._agent = agent
        self._state = state
        self._interval = interval_seconds
        self.stop_event = asyncio.Event()

    async def run_forever(self) -> None:
        self._state.enabled = True
        logger.info(
            "kairos daemon started (interval=%.0fs)", self._interval
        )
        try:
            while not self.stop_event.is_set():
                try:
                    await asyncio.wait_for(
                        self.stop_event.wait(), timeout=self._interval
                    )
                    break  # stop signalled during sleep
                except asyncio.TimeoutError:
                    pass
                await self._run_cycle()
        except asyncio.CancelledError:
            logger.info("kairos daemon cancelled")
            raise
        finally:
            self._state.enabled = False
            logger.info("kairos daemon stopped")

    async def _run_cycle(self) -> None:
        self._state.cycle_count += 1
        self._state.last_cycle_at = dt.datetime.now(dt.timezone.utc)
        try:
            observations = await self._agent.observe()
            plan = await self._agent.decide(observations)
            executions = await self._agent.act(plan)
            await self._agent.update_memory(observations, plan, executions)
            logger.info(
                "kairos cycle %d: obs=%d steps=%d",
                self._state.cycle_count, len(observations), len(executions),
            )
        except Exception as exc:
            self._state.errors += 1
            logger.exception("kairos cycle failed: %s", exc)


# ------------------------------------------------------------------
# Builder
# ------------------------------------------------------------------


def _parse_allowlist(raw: str | None) -> list[str]:
    if not raw:
        return [_DEFAULT_ALLOWLIST]
    return [t.strip() for t in raw.split(",") if t.strip()]


def build_default_kairos_daemon(
    *, llm_fn
) -> tuple[KairosDaemon, KairosState]:
    """Construct a daemon from env vars. MemoryStore is accessed as a singleton."""
    state = KairosState()
    allowlist = _parse_allowlist(os.getenv("ZEUS_KAIROS_TOOL_ALLOWLIST"))
    try:
        max_actions = max(
            1, int(os.getenv("KAIROS_MAX_ACTIONS_PER_CYCLE", str(_DEFAULT_MAX_ACTIONS)))
        )
    except ValueError:
        max_actions = _DEFAULT_MAX_ACTIONS
    try:
        interval_min = max(
            1, int(os.getenv("KAIROS_INTERVAL_MINUTES", str(_DEFAULT_INTERVAL_MIN)))
        )
    except ValueError:
        interval_min = _DEFAULT_INTERVAL_MIN

    observers: list[ObservationSource] = [MemoryDriftObserver()]
    agent = KairosAgent(
        llm_fn=llm_fn,
        observers=observers,
        state=state,
        allowlist=allowlist,
        max_actions=max_actions,
    )
    daemon = KairosDaemon(
        agent=agent, state=state, interval_seconds=interval_min * 60.0
    )
    return daemon, state
