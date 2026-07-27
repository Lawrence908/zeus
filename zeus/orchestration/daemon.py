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


def _truthy_env(name: str) -> bool:
    return os.getenv(name, "").strip().lower() in ("1", "true", "yes", "y", "on")


def _envf(name: str, default: float) -> float:
    try:
        return float(os.getenv(name, str(default)))
    except (TypeError, ValueError):
        return default


class ServerHealthObserver:
    """Poll /admin/system and flag threshold breaches as alertable observations.

    Emits an Observation carrying ``raw["alert"]`` (text/priority/dedupe_key)
    only when something is wrong; idle otherwise. The alert is templated here
    (deterministic) rather than composed by the decide-LLM, because health
    alerts must be reliable and never hallucinated. Degrades gracefully when a
    data source is absent (no GPU / no docker in-container -> those checks skip).
    """

    def __init__(self) -> None:
        self._gpu_temp_c = _envf("ZEUS_MESH_ALERT_GPU_TEMP_C", 85.0)
        self._disk_pct = _envf("ZEUS_MESH_ALERT_DISK_PCT", 90.0)
        self._expected = [
            c.strip()
            for c in os.getenv("ZEUS_MESH_ALERT_EXPECTED_CONTAINERS", "").split(",")
            if c.strip()
        ]

    async def observe(self) -> Observation | None:
        try:
            data = await _http_get_json("/admin/system")
        except Exception as exc:
            logger.warning("kairos health observer poll failed: %s", exc)
            return None

        breaches: list[str] = []
        for d in data.get("disks") or []:
            pct = d.get("percent_used")
            if pct is not None and pct >= self._disk_pct:
                breaches.append(f"disk {d.get('path')} {pct:.0f}%")
        for g in data.get("gpus") or []:
            t = g.get("temperature_c")
            if t is not None and t >= self._gpu_temp_c:
                breaches.append(f"GPU{g.get('index')} {t:.0f}C")
        docker = data.get("docker") or {}
        names = set(docker.get("names") or [])
        # Only alert on down containers when we both expect some AND can see the
        # running set; an empty `names` means docker is unavailable, not "all down".
        if self._expected and names:
            down = [c for c in self._expected if c not in names]
            if down:
                breaches.append("down: " + ",".join(down))

        if not breaches:
            return None

        text = "zeus alert: " + "; ".join(breaches)
        return Observation(
            source="server_health",
            summary=text,
            raw={
                "alert": {
                    "text": text,
                    # Any breach is operationally critical -> bypasses quiet hours.
                    "priority": "critical",
                    # Stable key + the choke point's payload-signature check means a
                    # standing condition fires once per dedupe window, but a CHANGED
                    # breach set re-alerts immediately (text differs -> new signature).
                    "dedupe_key": "health:server_health",
                }
            },
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
        mesh_enabled: bool = False,
    ) -> None:
        self._llm = llm_fn
        self._observers = observers
        self._state = state
        self._allowlist = [t.strip() for t in allowlist if t.strip()]
        self._max_actions = max_actions
        self._user_id = user_id
        # mesh_notify is deliberately NOT in the LLM allowlist: the decide-LLM
        # must never compose radio traffic. It fires only from emit_alerts on
        # deterministic observer alerts, gated by this flag.
        self._mesh_enabled = mesh_enabled

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

    async def _run_tool_call(
        self, step: ToolCall, *, enforce_allowlist: bool = True
    ) -> StepExecution:
        """Guard + dispatch one tool call. Shared by act() and emit_alerts().

        Guard order: allowlist membership (LLM-plan path only) -> Aegis
        pre-hook on the args -> dispatch. emit_alerts skips the allowlist
        (mesh_notify is intentionally absent from it) but keeps the Aegis hook.
        """
        if enforce_allowlist and step.tool not in self._allowlist:
            logger.warning(
                "kairos rejected tool %r not in allowlist %s",
                step.tool, self._allowlist,
            )
            return StepExecution(tool=step.tool, status="rejected", error="not_in_allowlist")

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
            logger.warning("kairos aegis rejected %s args: %s", step.tool, exc)
            return StepExecution(tool=step.tool, status="rejected", error=str(exc))

        try:
            data = await self._dispatch(step.tool, step.args)
            return StepExecution(tool=step.tool, status="ok", data=data)
        except Exception as exc:
            logger.warning("kairos tool %s raised: %s", step.tool, exc)
            return StepExecution(tool=step.tool, status="error", error=str(exc))

    async def act(self, plan: CognitivePlan) -> list[StepExecution]:
        return [await self._run_tool_call(step) for step in plan.steps]

    async def emit_alerts(self, observations: list[Observation]) -> list[StepExecution]:
        """Deterministically push observer alerts to the mesh via mesh_notify.

        Runs outside the LLM decide/act path. Each observation carrying an
        ``raw["alert"]`` becomes a mesh_notify call. No-op unless mesh is
        enabled, so a stray alert can never transmit when the gate is off.
        """
        if not self._mesh_enabled:
            return []
        results: list[StepExecution] = []
        for obs in observations:
            alert = (obs.raw or {}).get("alert")
            if not isinstance(alert, dict) or not alert.get("text"):
                continue
            step = ToolCall(
                tool="mesh_notify",
                args={
                    "text": alert["text"],
                    "priority": alert.get("priority", "normal"),
                    "dedupe_key": alert.get("dedupe_key"),
                },
                rationale=f"auto-alert from {obs.source}",
            )
            results.append(await self._run_tool_call(step, enforce_allowlist=False))
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

        if tool == "mesh_notify":
            if not self._mesh_enabled:
                return {"ok": False, "reason": "mesh_notify_disabled"}
            # In-process call into the choke point: same gate/Aegis/quiet-hours/
            # dedupe/rate-limit/audit pipeline as any other caller, no HTTP hop.
            from zeus.core.mesh import MeshNotifyRequest, mesh_notify

            text = str(args.get("text") or "").strip()
            if not text:
                return {"ok": False, "reason": "empty_text"}
            req = MeshNotifyRequest(
                text=text,
                priority=str(args.get("priority") or "normal"),
                dedupe_key=args.get("dedupe_key"),
                source="kairos",
            )
            return await mesh_notify(req)

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
            alerts = await self._agent.emit_alerts(observations)
            executions = executions + alerts
            await self._agent.update_memory(observations, plan, executions)
            logger.info(
                "kairos cycle %d: obs=%d steps=%d alerts=%d",
                self._state.cycle_count, len(observations), len(executions), len(alerts),
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

    # mesh_notify is gated by its own knob (plus the choke point's own master
    # gate ZEUS_MESH_OUTBOUND_ENABLED downstream). Flipping this on both adds the
    # health observer and permits emit_alerts to fire; it never enters the LLM
    # allowlist, so the decide-LLM cannot author mesh traffic.
    mesh_enabled = _truthy_env("ZEUS_KAIROS_MESH_NOTIFY")

    observers: list[ObservationSource] = [MemoryDriftObserver()]
    if mesh_enabled:
        observers.append(ServerHealthObserver())

    # Pheme breaking-news observer: acts inside observe() (delivery passes
    # Aegis in zeus/pheme/delivery.py) and reports what it sent. Gated by
    # PHEME_BREAKING_ENABLED; never enters the LLM tool allowlist.
    if _truthy_env("PHEME_BREAKING_ENABLED"):
        from zeus.pheme.observer import PhemeBreakingObserver

        observers.append(PhemeBreakingObserver())

    agent = KairosAgent(
        llm_fn=llm_fn,
        observers=observers,
        state=state,
        allowlist=allowlist,
        max_actions=max_actions,
        mesh_enabled=mesh_enabled,
    )
    daemon = KairosDaemon(
        agent=agent, state=state, interval_seconds=interval_min * 60.0
    )
    return daemon, state
