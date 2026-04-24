# zeus/orchestration/ — Agent runtime, bus, hooks, Kairos

Agent lifecycle, multi-step tasks, bus routing, and the Kairos background daemon. Root brief: [`../../CLAUDE.md`](../../CLAUDE.md). Full spec: [`../docs/agent-runtime-spec.md`](../docs/agent-runtime-spec.md).

Kronos (the cron-driven scheduler) is the deterministic sibling to Kairos; runs as a parallel lifespan task. See [`../kronos/CLAUDE.md`](../kronos/CLAUDE.md).

## Layout

| File | Role |
|------|------|
| `runtime.py` | `AgentRuntime`, `AgentDefinition`, `AgentStep`, `StepResult`, `TaskRecord`, `TaskRunner` |
| `bus.py` | `/orchestration/*` FastAPI router (status, agent actions, call, tasks, kairos) |
| `hooks.py` | `HookRegistry`, `BusMetrics`, built-in hooks (`validate_context`, `log`, `retry_backoff`, `bus_metrics`) |
| `daemon.py` | `KairosAgent`, `KairosDaemon`, `MemoryDriftObserver`, `KairosState` |
| `ruflo.yaml` | Ruflo v3.5 swarm config |
| `agents/*.yaml` | Individual agent manifests: iris, mnemosyne, athena, oracle, orpheus |

## FastAPI surface (port 8203)

| Method | Path | Purpose |
|--------|------|---------|
| GET | `/orchestration/status` | Runtime + per-agent state |
| GET | `/orchestration/agents` | List manifests |
| POST | `/orchestration/agents/{name}/action` | `action: "start"` or `"stop"` |
| POST | `/orchestration/call` | `BusCallRequest`: target_agent, endpoint, method, payload, correlation_id, idempotent |
| POST | `/orchestration/tasks` | Multi-step task creation |
| GET | `/orchestration/tasks` | Recent `TaskRecord`s (ring buffer) |
| GET | `/orchestration/tasks/{task_id}` | Poll one task |
| GET | `/orchestration/kairos/status` | Daemon snapshot |

## Invariants

- **Every bus call passes through Aegis.** `aegis_bus_pre_hook` validates tool arguments via `evaluate_payload()`; `aegis_bus_post_hook` filters output via `evaluate_text()`. Registered from `zeus/core/main.py` lifespan.
- **Correlation IDs are mandatory.** If a caller omits one, `bus.py` generates a UUID4 and echoes it in the response; every log line carries it.
- **Retry on 502/503/504 only.** `retry_backoff` post-hook flags transient failures; `bus_call()` retries up to 3 times with exponential backoff (0.5s, 1s).
- **Task steps collect `StepResult` in a ring buffer.** `app.state.task_records` keeps the last N; `GET /orchestration/tasks` pages them. No database.
- **`on_failure` per step is `skip | retry | abort`.** Default is `abort`. Don't change the default without reading the caller.
- **Kairos default tool allowlist is read-only.** `ZEUS_KAIROS_TOOL_ALLOWLIST=zeus_memory_search`. Widening it requires an Aegis policy review.

## Env flags

| Env | Default | Effect |
|-----|---------|--------|
| `ZEUS_AEGIS_ENABLED` | `1` | Enforce Aegis on bus + chat paths |
| `ZEUS_AEGIS_POLICY` | `standard` | YAML policy name under `zeus/safety/policies/` |
| `ZEUS_KAIROS_ENABLED` | `0` | Start the background daemon in the FastAPI lifespan |
| `KAIROS_INTERVAL_MINUTES` | `60` | Cycle cadence |
| `KAIROS_MAX_ACTIONS_PER_CYCLE` | `5` | Hard cap on tool calls per cycle |
| `ZEUS_KAIROS_TOOL_ALLOWLIST` | `zeus_memory_search` | Comma-separated tool names Kairos can call |
| `ZEUS_ACTIONS_ENABLED` | `0` | Master switch for the `/actions/*` runner. Even with `ZEUS_MCP_ALLOW_WRITE=1` and `olympian_action_run` in the Kairos allowlist, executions are 403-rejected unless this is also `1`. |
| `ZEUS_ACTIONS_DIR` | `~/.zeus/actions` | Directory whose `.sh` files form the action allowlist. |
| `ZEUS_FILE_READ_ROOTS` | `~/.zeus,~/notes` | Allowlist roots for `/vault/file` and `/vault/search`. |
| `ZEUS_INBOX_PATH` | `~/.zeus/inbox.md` | Append target for `/inbox/append`. |
| `ZEUS_STATUS_PATH` | `~/.zeus/status.md` | File backing `/admin/status_file` and `olympian_status_read`. |

## Common patterns

**Calling an agent from another (internal service-to-service):**

```python
from zeus.orchestration.bus import BusCallRequest
# POST /orchestration/call with:
BusCallRequest(
    target_agent="oracle",
    endpoint="/context/query",
    method="POST",
    payload={"query": "...", "top_k": 5},
    correlation_id="user-req-abc",
    idempotent=True,
)
```

**Registering a post-hook:**

```python
from zeus.orchestration.hooks import HookRegistry

async def my_post_hook(context):
    # context has: request_id, target_agent, endpoint, response_data, safety_policy, ...
    ...

registry.register_post("my_metric", my_post_hook)
```

Hook ordering matches registration order. Keep post-hooks idempotent; they may run twice if retry fires.

**Adding an agent:**

1. Write `agents/<name>.yaml` with `name`, `description`, `model`, `tools`, `context`, `safety.policy`.
2. `safety.policy` must match an existing file in `zeus/safety/policies/`.
3. Reload the runtime (`docker compose restart zeus-core`) or hit `/orchestration/agents/<name>/action` to start.

## Kairos loop

```python
# daemon.py
async def cycle(self):
    observation = await self.observer.observe()      # MemoryDriftObserver, extensible
    plan = await self.decide(observation)            # LLM -> CognitivePlan(steps: list[ToolCall])
    for step in plan.steps[:KAIROS_MAX_ACTIONS_PER_CYCLE]:
        if step.name not in self.tool_allowlist:
            continue
        await aegis_bus_pre_hook({"payload": step.args, "safety_policy": "standard"})
        result = await dispatch(step)
    await self.update_memory(summary, namespace="execution_log")
```

Only `zeus_memory_search` is allowed by default. Any write-capable tool widens the blast radius and needs a safety review.

### Recommended additions to the Kairos allowlist (Olympian read-side)

The Olympian tool pack adds several read-only tools that are safe to widen the Kairos allowlist with. All have in-process `_dispatch` arms in `daemon.py` that route through the Core HTTP loopback, so server-side allowlists and Aegis policies apply identically to MCP, chat-path, and Kairos invocations.

Safe to add (read-only, no side effects):

```
ZEUS_KAIROS_TOOL_ALLOWLIST=zeus_memory_search,olympian_status_read,olympian_server_health,olympian_file_read,olympian_file_search,zeus_calendar_today,zeus_newsletter_latest
```

Conditionally safe (one write, low blast radius):

- `olympian_inbox_append` — append a one-line note to `~/.zeus/inbox.md`. Add only when there is a clear "Kairos leaves itself a note" use case, and only with `ZEUS_MCP_ALLOW_WRITE=1`.

Never add to the default allowlist:

- `olympian_action_run` — arbitrary script execution. The risk is unbounded by allowlist alone; gate behind a dedicated `ZEUS_KAIROS_ALLOW_ACTIONS=1` check before adding.
- `zeus_remember`, `zeus_ingest_trigger` — both write to memory or trigger ingest, which is observable but expensive on misuse.

## What not to do

- Don't bypass Aegis. Calls that skip pre/post hooks are silently lethal for a self-improving agent.
- Don't call the bus from inside a hook. Infinite recursion.
- Don't store task records in a real database. In-memory ring buffer is intentional.
- Don't give Kairos write tools without a dedicated policy and an env flag that defaults off.
- Don't widen `ZEUS_KAIROS_TOOL_ALLOWLIST` in a PR without a note explaining the blast radius.
