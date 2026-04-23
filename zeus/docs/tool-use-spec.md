# Chat-path tool-use spec

Lives under the chat path (`zeus/core/query.py` + `zeus/core/tools/`), distinct from:

- The **MCP server** (`zeus/mcp/server.py`) which exposes `zeus_query`, `zeus_profile`, `zeus_remember`, `zeus_memory_search`, `zeus_ingest_trigger` to *external* assistant clients (Claude Desktop, Cursor).
- The **olympian tool pack** (future, LAB-328) which gives *agents / KAIROS* file-read / search / shell tools.

Chat-path tool-use is what lets the chat LLM itself call tools during a `POST /chat/message` round-trip and fold the results back into its reply.

## Quick start

```bash
export ZEUS_TOOLS_ENABLED=1
export BRAVE_API_KEY=<your-brave-search-key>
# optional: lower or raise the per-query cap (default 5)
export ZEUS_TOOLS_MAX_CALLS_PER_QUERY=5
docker compose up zeus-core
```

At startup `main.py` calls `register_if_configured()` from `zeus/core/tools/web_search.py`, which registers the `web_search` tool iff `BRAVE_API_KEY` is set. When `ZEUS_TOOLS_ENABLED=0` (default), chat behaviour is byte-identical to pre-tool-use — the registry is never consulted.

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

`QueryEngine.query()` — after the existing retrieval fan-out (`_collect_retrieval_context`) and system-prompt build — branches:

1. **Flag off or registry empty** → call `_run_llm()` once, keep the existing 3-attempt reflection loop. No behaviour change from today.
2. **Flag on and tools available** → call `run_tool_loop(system, user_prompt, tools, max_tokens, max_calls, use_claude=...)`. The loop drives the model through N tool-call rounds until it stops emitting tool calls or hits the cap.

If any tool fired during the loop, **reflection is skipped** — a tool-informed reply is treated as authoritative. If the model chose not to call tools (empty reply / refusal), the existing reflection path runs as before.

### Inside `run_tool_loop`

Per iteration:

1. Call `_run_llm_with_tools(system, messages, tools, max_tokens, turn_idx)`.
2. No tool calls → return the text.
3. Otherwise, for each emitted `ToolCall`:
   - **Aegis pre** on `call.arguments` via `AegisPolicyEngine(spec.aegis_policy).evaluate_payload(...)` (skipped if Aegis is disabled).
   - **Registry lookup** — unknown tool returns an error `ToolResult`.
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

## Aegis policy — `tool_arguments.yaml`

Applied to every tool-call arguments dict (via `evaluate_payload`) and every tool-result text (via `evaluate_text`). Rules: prompt injection (reject), shell metacharacters (reject), secret extraction patterns (flag), filesystem traversal (reject). Add tool-specific rules by setting `ToolSpec.aegis_policy = "<name>"` and dropping a matching YAML under `zeus/safety/policies/`.

Aegis respects the global `ZEUS_AEGIS_ENABLED` gate. When disabled, tool args and results are not evaluated.

## Reference tool — `web_search`

`zeus/core/tools/web_search.py`:

- Calls `GET https://api.search.brave.com/res/v1/web/search` with `X-Subscription-Token: $BRAVE_API_KEY`, `count={1..10}`.
- Rate-limited to 1 qps via a module-level `asyncio.Semaphore(1)` + paced `sleep`. Brave free tier is 1 qps / 2,000 q/month.
- Schema is flat (`query`, optional `count`) so Qwen2.5-7B Q4_K_M handles it reliably (Qwen degrades on nested/enum schemas).
- Timeout 10 s.
- `cacheable=True`.
- Formatted output: `"- <title>\n  <url>\n  <description>"` per hit, concatenated with newlines.

## Reference tool — `current_time`

`zeus/core/tools/current_time.py`:

- No network, no external key. Registered unconditionally at startup.
- Schema: optional `timezone` (IANA name, default from `ZEUS_DEFAULT_TIMEZONE` or `UTC`) and `format` (`iso` | `human` | `unix`, default `iso`).
- `cacheable=False` (non-negotiable — the result changes every second).
- Timeout 1 s.

## Tool-result cache

`zeus/core/tools/cache.py` exposes a process-local `ToolCache` — an LRU with a per-entry TTL — that sits inside `_execute_one`:

1. **Before execute**: if `spec.cacheable` and an unexpired entry exists for `(name, canonical_args)`, return it. The returned `ToolResult` is rebound to the current call's `call_id` / `name` so provider adapters work.
2. **After execute**: if `spec.cacheable` and the result is not an error, store it.

Errors are never cached — transient failures would poison every subsequent identical call. `current_time` and any future time-sensitive, write-side, or side-effecting tool must stay `cacheable=False`.

Environment knobs:

| Var | Default | Meaning |
|-----|---------|---------|
| `ZEUS_TOOL_CACHE_TTL_SECONDS` | `300` | Entry lifetime in seconds. `0` disables the cache entirely (get/set become no-ops). |
| `ZEUS_TOOL_CACHE_MAX_ENTRIES` | `256` | Hard cap on stored entries. Oldest are evicted first. |

The cache is not persisted across restarts — stale cached results leaking across deploys is worse than a cold miss, so we start fresh on every boot.

## Async chat — `/chat/async` + `/classify`

The chat-path tool loop lets web_search queries run for 10–30 seconds. Synchronous HTTP endpoints that long are unusable for LoRa-bridged clients (Meshtastic), so the chat surface grows two endpoints documented in detail in [`chat-interface-spec.md`](chat-interface-spec.md):

- `POST /chat/async` → `{job_id, status, session_id, created_at}` immediately. A background `asyncio.Task` runs `engine.query()`; on completion the full `ChatMessageResponse` is POSTed to the caller-supplied `callback_url` (if any) and is available via `GET /chat/async/{job_id}`. Ring buffer is capped at 100 jobs.
- `POST /classify` → one-shot intent classifier via `small_llm_call(response_format=ChatClassification, min_privacy_tier=1)`. Returns `{intent, estimated_ms, tool_hint, reasoning}` — used by bridges to pick specific ack strings ("🔍 searching..." vs "💭 thinking...") before firing the real query. Falls back to `intent="chat"` when all providers are down.

## Environment flags

| Var | Default | Meaning |
|-----|---------|---------|
| `ZEUS_TOOLS_ENABLED` | `0` | Opt-in feature flag for the chat-path tool loop. |
| `ZEUS_TOOLS_MAX_CALLS_PER_QUERY` | `5` | Cap on total tool calls emitted per single `/chat/message` request. |
| `BRAVE_API_KEY` | unset | Required to register the `web_search` tool. Without it, the registry is empty even when the flag is on. |

## Deferred (not in scope)

- **Streaming + tools (`query_stream`).** Anthropic's `input_json_delta` accumulation and Ollama's NDJSON tool-call chunks both need per-provider handling; React SSE UI works fine on tool-free chat today, so this is deferred until a concrete UX demands it.
- **Meshtastic bridge switching to `/chat/async`.** Node-RED flow change, not a chat-engine change. The endpoint is ready; the bridge migration is a separate ticket.

## Invariants (do not regress)

1. With `ZEUS_TOOLS_ENABLED=0`, `QueryEngine.query()` makes exactly one `_run_llm()` call plus any reflection retries — identical to pre-tool-use.
2. With the flag on and no registered tools, the code path routes around `run_tool_loop` and behaves as if the flag were off.
3. Every tool invocation passes through Aegis on both args and result text when `ZEUS_AEGIS_ENABLED=1`.
4. Reflection never runs when any tool fired during the query.
5. `QueryResult.tool_calls` is empty unless the tool loop was taken and at least one call fired.
