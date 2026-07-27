# Chat-path tool-use spec

Lives under the chat path (`zeus/core/query.py` + `zeus/core/tools/`), distinct from:

- The **MCP server** (`zeus/mcp/server.py`) which exposes the same tools, plus the Olympian pack, to *external* assistant clients (Claude Desktop, Cursor).
- The **Olympian tool pack** (LAB-328) which adds file-read / search / status / health / inbox / action / calendar / newsletter tools. The pack is dual-exposed - every Olympian tool is registered both as a chat-path `ToolSpec` (this doc) AND as an MCP wrapper (`zeus/mcp/`), and both surfaces wrap the same Core HTTP endpoints, so behaviour is identical regardless of which surface fires.

Chat-path tool-use is what lets the chat LLM itself call tools during a `POST /chat/message` round-trip and fold the results back into its reply.

## Quick start

```bash
export ZEUS_TOOLS_ENABLED=1
export BRAVE_API_KEY=<your-brave-search-key>
# optional: lower or raise the per-query cap (default 5)
export ZEUS_TOOLS_MAX_CALLS_PER_QUERY=5
# optional: restrict which tools the model may use (unset = all registered).
# Use a read-only set in prod while dev runs the full pack.
export ZEUS_TOOLS_ALLOWLIST=current_time,web_search,zeus_calendar_today,zeus_news_search
docker compose up zeus-core
```

At startup `main.py` calls `register_if_configured()` from `zeus/core/tools/web_search.py`, which registers the `web_search` tool iff `BRAVE_API_KEY` is set. When `ZEUS_TOOLS_ENABLED=0` (default), chat behaviour is byte-identical to pre-tool-use - the registry is never consulted.

## Module layout

```
zeus/core/tools/
  __init__.py       # tools_enabled(), tools_max_calls(), public re-exports
  base.py           # ToolSpec, ToolCall, ToolResult, ToolHandler
  registry.py       # register / unregister / get / list_specs / available / clear
  adapters.py       # Pure wire-format adapters for Anthropic + Ollama
  loop.py           # run_tool_loop() — provider-agnostic driver
  cache.py          # In-memory TTL+LRU cache; opt-in per tool via ToolSpec.cacheable
  web_search.py     # Brave Search reference tool (cacheable=True)
  current_time.py   # Wall-clock tool (cacheable=False)
zeus/safety/policies/
  tool_arguments.yaml  # Aegis policy applied to tool args + results
tests/
  conftest.py       # autouse registry + cache reset
  test_tool_loop.py # registry / adapters / loop / cache / current_time
  test_chat_async.py  # /chat/async job lifecycle + callback
  test_classify.py    # /classify happy path + fallback
```

## Control flow

`QueryEngine.query()` - after the existing retrieval fan-out (`_collect_retrieval_context`) and system-prompt build - branches:

1. **Flag off or registry empty** → call `_run_llm()` once, keep the existing 3-attempt reflection loop. No behaviour change from today.
2. **Flag on and tools available** → call `run_tool_loop(system, user_prompt, tools, max_tokens, max_calls, use_claude=...)`. The loop drives the model through N tool-call rounds until it stops emitting tool calls or hits the cap.

If any tool fired during the loop, **reflection is skipped** - a tool-informed reply is treated as authoritative. If the model chose not to call tools (empty reply / refusal), the existing reflection path runs as before.

### Inside `run_tool_loop`

Per iteration:

1. Call `_run_llm_with_tools(system, messages, tools, max_tokens, turn_idx)`.
2. No tool calls → return the text.
3. Otherwise, for each emitted `ToolCall`:
   - **Aegis pre** on `call.arguments` via `AegisPolicyEngine(spec.aegis_policy).evaluate_payload(...)` (skipped if Aegis is disabled).
   - **Registry lookup** - unknown tool returns an error `ToolResult`.
   - **Execute** `handler(args)` under `asyncio.wait_for(spec.timeout_seconds)`; exceptions and timeouts become error results.
   - **Aegis post** on `result.content` via `evaluate_text(..., policy_name=spec.aegis_policy)`.
   - Count against `max_calls`. When hit, remaining calls are synthesised as error results; the next iteration gets a chance to compose a final answer.
4. Echo the assistant turn into `messages` in the right shape for the active provider, then append the tool-result follow-up message(s).
5. Loop.

The loop returns a `ToolLoopResult` with `reply`, `tool_calls`, `tool_results`, `iterations`, `stop_reason`, and `truncated`.

## Per-provider wire-format differences

Source: `zeus/core/tools/adapters.py`. All four adapter functions are pure (no I/O, no env reads) so they are trivially unit-testable.

| Concern | Anthropic Messages | Ollama `/api/chat` |
|---|---|---|
| Spec field for parameters | `input_schema` | `function.parameters` |
| Call ID | `toolu_...` (native) | none; synthesised as `f"{name}-{turn}-{i}"` |
| Result message | user-role content block `{type:tool_result, tool_use_id, content}`, and it MUST be the first block in that user message, and the user message MUST immediately follow the assistant turn that emitted the tool_use | `{role:"tool", content, tool_name}`, associated positionally |
| Stop signal | `stop_reason: "tool_use"` | `tool_calls` present on the message |
| Parallel calls | multiple `tool_use` blocks in one assistant message | array under `message.tool_calls` |

## Aegis policy - `tool_arguments.yaml`

Applied to every tool-call arguments dict (via `evaluate_payload`) and every tool-result text (via `evaluate_text`). Rules: prompt injection (reject), shell metacharacters (reject), secret extraction patterns (flag), filesystem traversal (reject). Add tool-specific rules by setting `ToolSpec.aegis_policy = "<name>"` and dropping a matching YAML under `zeus/safety/policies/`.

Aegis respects the global `ZEUS_AEGIS_ENABLED` gate. When disabled, tool args and results are not evaluated.

## Reference tool - `web_search`

`zeus/core/tools/web_search.py`:

- Calls `GET https://api.search.brave.com/res/v1/web/search` with `X-Subscription-Token: $BRAVE_API_KEY`, `count={1..10}`.
- Rate-limited to 1 qps via a module-level `asyncio.Semaphore(1)` + paced `sleep`. Brave free tier is 1 qps / 2,000 q/month.
- Schema is flat (`query`, optional `count`) so Qwen2.5-7B Q4_K_M handles it reliably (Qwen degrades on nested/enum schemas).
- Timeout 10 s.
- `cacheable=True`.
- Formatted output: `"- <title>\n  <url>\n  <description>"` per hit, concatenated with newlines.

## Reference tool - `current_time`

`zeus/core/tools/current_time.py`:

- No network, no external key. Registered unconditionally at startup.
- Schema: optional `timezone` (IANA name, default from `ZEUS_DEFAULT_TIMEZONE` or `UTC`) and `format` (`iso` | `human` | `unix`, default `iso`).
- `cacheable=False` (non-negotiable - the result changes every second).
- Timeout 1 s.

## Tool-result cache

`zeus/core/tools/cache.py` exposes a process-local `ToolCache` - an LRU with a per-entry TTL - that sits inside `_execute_one`:

1. **Before execute**: if `spec.cacheable` and an unexpired entry exists for `(name, canonical_args)`, return it. The returned `ToolResult` is rebound to the current call's `call_id` / `name` so provider adapters work.
2. **After execute**: if `spec.cacheable` and the result is not an error, store it.

Errors are never cached - transient failures would poison every subsequent identical call. `current_time` and any future time-sensitive, write-side, or side-effecting tool must stay `cacheable=False`.

Environment knobs:

| Var | Default | Meaning |
|-----|---------|---------|
| `ZEUS_TOOL_CACHE_TTL_SECONDS` | `300` | Entry lifetime in seconds. `0` disables the cache entirely (get/set become no-ops). |
| `ZEUS_TOOL_CACHE_MAX_ENTRIES` | `256` | Hard cap on stored entries. Oldest are evicted first. |

The cache is not persisted across restarts - stale cached results leaking across deploys is worse than a cold miss, so we start fresh on every boot.

## Async chat - `/chat/async` + `/classify`

The chat-path tool loop lets web_search queries run for 10–30 seconds. Synchronous HTTP endpoints that long are unusable for LoRa-bridged clients (Meshtastic), so the chat surface grows two endpoints documented in detail in [`chat-interface-spec.md`](chat-interface-spec.md):

- `POST /chat/async` → `{job_id, status, session_id, created_at}` immediately. A background `asyncio.Task` runs `engine.query()`; on completion the full `ChatMessageResponse` is POSTed to the caller-supplied `callback_url` (if any) and is available via `GET /chat/async/{job_id}`. Ring buffer is capped at 100 jobs.
- `POST /classify` → one-shot intent classifier via `small_llm_call(response_format=ChatClassification, min_privacy_tier=1)`. Returns `{intent, estimated_ms, tool_hint, reasoning}` - used by bridges to pick specific ack strings ("🔍 searching..." vs "💭 thinking...") before firing the real query. Falls back to `intent="chat"` when all providers are down.

## Environment flags

| Var | Default | Meaning |
|-----|---------|---------|
| `ZEUS_TOOLS_ENABLED` | `0` | Opt-in feature flag for the chat-path tool loop. |
| `ZEUS_TOOLS_MAX_CALLS_PER_QUERY` | `5` | Cap on total tool calls emitted per single `/chat/message` request. |
| `ZEUS_TOOLS_ALLOWLIST` | unset (all) | Comma-separated tool names the model may see and call this turn. Unset = every registered tool. Per-env rollout control: prod runs a read-only subset while dev runs the full pack. Resolved by `allowed_tool_specs()` and used both to build the system-prompt tool list and to hand tools to the loop, so the model is never told about a tool it can't call. Write tools stay additionally gated by `ZEUS_MCP_ALLOW_WRITE` / `ZEUS_ACTIONS_ENABLED`. |
| `BRAVE_API_KEY` | unset | Required to register the `web_search` tool. Without it, the registry is empty even when the flag is on. |

## Olympian tool pack (LAB-328)

Eight new tools land in `zeus/core/tools/` and are dual-exposed through MCP (`zeus/mcp/`):

| Tool | File | Side | Backing endpoint | Aegis policy |
|------|------|-----|------------------|--------------|
| `olympian_status_read` | `status_read.py` | read | `GET /admin/status_file` | `tool_arguments` |
| `olympian_server_health` | `server_health.py` | read | `GET /admin/system` | `tool_arguments` |
| `olympian_file_read` | `file_read.py` | read | `GET /vault/file` | `file_access` |
| `olympian_file_search` | `file_search.py` | read | `POST /vault/search` | `file_access` |
| `olympian_inbox_append` | `inbox_append.py` | write | `POST /inbox/append` | `file_access` |
| `olympian_action_list` | `action_run.py` | read | `GET /actions/list` | `tool_arguments` |
| `olympian_action_run` | `action_run.py` | write | `POST /actions/run` | `file_access` |
| `zeus_calendar_today` | `calendar_today.py` | read | `GET /calendar/today` | `tool_arguments` |
| `zeus_newsletter_latest` | `newsletter_latest.py` | read | `GET /api/newsletter/digests?limit=1` | `tool_arguments` |

Cacheability:

- `cacheable=True` on `status_read`, `server_health`, `calendar_today`, `newsletter_latest` (the underlying data changes on the order of minutes; the default short TTL keeps responses fresh).
- `cacheable=False` on `file_read`, `file_search`, `inbox_append`, `action_list`, `action_run` (file contents and side effects must always reflect current state).

Server-side gates compose:

- All write endpoints require `ZEUS_MCP_ALLOW_WRITE=1`.
- `/actions/list` and `/actions/run` additionally require `ZEUS_ACTIONS_ENABLED=1`.
- `/vault/file` and `/vault/search` resolve every path against `ZEUS_FILE_READ_ROOTS` after symlink dereferencing - escapes are 400-rejected.
- `/actions/run` validates `name` against `^[A-Za-z0-9][A-Za-z0-9_-]{0,63}$` and runs scripts via `asyncio.create_subprocess_exec` with no shell, capping output at 64 KB per stream.

Aegis policy `file_access.yaml` is new and rejects path traversal, shell metacharacters, and I/O redirection to sensitive paths in tool payloads. It flags (does not reject) credential-shaped strings in inbox captures so personal notes are not blocked by false positives.

## Observability

Every tool invocation (success, error, cache hit, Aegis reject) is recorded into an in-process ring buffer (`zeus/core/tools/recorder.py`) and exposed two ways:

- `GET /admin/tools/invocations`: the raw recent feed (newest first) for the Tools UIs.
- `GET /admin/metrics` `tools` block, via `recorder.metrics_summary()`, rolls the buffer into overall `total` / `error_rate` / `cache_hit_rate` / `aegis_reject_count` / `latency_ms_p50/p95` plus a per-tool breakdown (busiest first). Optional `window_seconds` restricts to recent calls. MCP-server invocations happen out-of-process and are not recorded here.

`GET /admin/tools` also reports `chat.allowlist` / `chat.allowed_count` and a per-tool `allowed` flag so the UI can grey out registered-but-blocked tools.

## Voice parity

`QueryEngine.query()` and `query_stream()` accept a `voice` flag. When set, the reply uses `_build_voice_system_prompt()` (the terse, no-markdown `voice_system.md` tone) while retrieval, the tool loop, Aegis, and sessions run identically. The four retrieval blocks fold into one `CONTEXT`; the tool list is appended only when tools are enabled. The host-native Orpheus pipeline streams from `/chat/stream` with `voice=True` and a persisted `session_id`, so spoken turns share history with text chat and inherit tools + Aegis for free (no separate LLM path).

## Deferred (not in scope)

- **Token-delta streaming during tool use.** `query_stream` runs the tool loop to completion (it needs multiple round trips) and yields the assembled reply as a single chunk; tool-free replies still stream token-by-token. Per-provider streaming of the model's final turn *after* tools (Anthropic `input_json_delta`, Ollama NDJSON) is deferred until a concrete UX demands it.
- **Meshtastic bridge switching to `/chat/async`.** Node-RED flow change, not a chat-engine change. The endpoint is ready; the bridge migration is a separate ticket.

## Invariants (do not regress)

1. With `ZEUS_TOOLS_ENABLED=0`, `QueryEngine.query()` makes exactly one `_run_llm()` call plus any reflection retries - identical to pre-tool-use.
2. With the flag on but no tools available after the allowlist filter (none registered, or `ZEUS_TOOLS_ALLOWLIST` excludes them all), the code path routes around `run_tool_loop` and behaves as if the flag were off.
3. Every tool invocation passes through Aegis on both args and result text when `ZEUS_AEGIS_ENABLED=1`.
4. Reflection never runs when any tool fired during the query.
5. `QueryResult.tool_calls` is empty unless the tool loop was taken and at least one call fired.
