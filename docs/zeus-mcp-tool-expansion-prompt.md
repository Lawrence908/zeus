# Zeus MCP Tool Expansion: Triage Prompt for Claude Code

## Context

I'm expanding the MCP tool surface for Zeus, my self-hosted personal AI assistant. The goal is to make Zeus genuinely useful from constrained interfaces (Telegram, Meshtastic radio, voice) by exposing the right mix of **read**, **search**, **decision**, **action**, and **integration** tools.

Current state:
- MCP server lives in `zeus/mcp/server.py` (FastMCP over Zeus Core HTTP)
- Existing tools: `zeus_query`, `zeus_profile`, `zeus_remember`, `zeus_memory_search`, `zeus_ingest_trigger`
- Write tools gated by `ZEUS_MCP_ALLOW_WRITE`
- LAB-107 (MCP Tool Definitions) is in progress with more to add
- LAB-328 (Olympian Tool Pack Expansion) proposes `olympian_file_read`, `olympian_search`, `olympian_shell`, `olympian_memory_search`
- Every tool call passes through Aegis pre/post hooks (LAB-326)
- Kairos daemon (LAB-330) uses a separate read-only allowlist

## What I want from this session

Go through the tool list below with me. For each tool:

1. **Decide whether it's worth building** given my actual usage patterns (primary interfaces: Telegram + Meshtastic + voice + MCP clients like Cursor/Claude Desktop)
2. **Flag dependencies** - does it need a new subsystem, a new API, or just wiring?
3. **Flag safety concerns** - what's the Aegis policy, what's the env gate, what's the allowlist?
4. **Sketch the signature** - `@mcp.tool()` name, params, return shape
5. **Rank priority** - High / Medium / Low based on leverage vs effort

Then we weed out the ones that aren't reasonable, and I'll create Linear tickets for the keepers.

---

## Candidate tool list

### Memory and context (foundation, mostly exists)

- **`zeus_query`** ✅ exists - grounded context retrieval
- **`zeus_profile`** ✅ exists - profile facts only
- **`zeus_remember`** ✅ exists - write to memory
- **`zeus_memory_search`** ✅ exists - targeted memory lookup
- **`zeus_knowledge_search`** - explicit bulk-RAG search against `zeus_knowledge` (currently bundled into `zeus_query`; worth splitting for tool-first agents that want raw chunks without the chat LLM wrapping)
- **`zeus_reference_lookup`** - query the Reference layer directly (kiwix Wikipedia, NOMAD) without going through QueryEngine. Useful when you know you want an encyclopedic answer, not a personal one.

### File and search (the `olympian_` pack)

- **`olympian_file_read`** - read from an allowlisted root (`ZEUS_FILE_READ_ROOTS`). Status files, pinned checklists, Obsidian notes by path.
- **`olympian_search`** - ripgrep-backed content search across vault / logs without re-ingesting. Much faster than RAG for "did I write about X?".
- **`olympian_file_write`** - append-only writes to a narrow allowlist (e.g. `~/.zeus/inbox.md`, `~/.zeus/scratch.md`). Separate env gate from read.
- **`olympian_status_read`** - convenience wrapper: reads `~/.zeus/status.md` specifically. One tool call, no path arg needed. For Telegram / Meshtastic "what's on my plate?" shortcuts.

### Calendar and time

- **`zeus_calendar_today`** - gcal pull for today only, formatted compactly (title, time, location). Low-latency, radio-friendly.
- **`zeus_calendar_upcoming`** - next N events across a configurable window
- **`zeus_calendar_add`** - write an event (gated). Useful for "add a reminder for Thursday at 3pm".
- **`zeus_time_query`** - "what time is it in Tokyo", "how long until my next meeting", "is it past 5pm?". Pure function, no external deps.

### Task and inbox

- **`olympian_task_add`** - write a task to a JSON file / Obsidian inbox / whatever your task system is. Key decision: single canonical task store or federated across systems.
- **`olympian_task_list`** - read current open tasks
- **`olympian_task_complete`** - mark done by id
- **`olympian_inbox_append`** - lower-friction variant: append a line to `~/.zeus/inbox.md` without structure. "Remember this for later" use case.

### System operations (the high-risk, high-value set)

- **`olympian_shell`** - gated by `ZEUS_SHELL_ENABLED=1` + regex allowlist. Candidates to allowlist:
  - `ufw allow <port>/tcp` / `ufw status`
  - `systemctl restart <service>` for a defined service list
  - `docker restart <container>` / `podman restart <container>` for a defined container list
  - `tailscale status` / `tailscale ip`
  - Custom scripts: `~/.zeus/actions/*.sh` (the allowlist is the directory, not the command)
- **`olympian_service_status`** - read-only wrapper: `systemctl status <service>` parsed to structured output. No write gate needed.
- **`olympian_docker_ps`** - read-only container state
- **`olympian_disk_usage`** - `df -h` parsed; flags when any mount is over threshold
- **`olympian_server_health`** - aggregate tool: CPU load, RAM, GPU VRAM (nvidia-smi), Zeus service health, Qdrant status. Single call returns a health summary.

### Integration edges

- **`olympian_mail_send`** - SMTP send from an allowlisted sender, to an allowlisted recipient list. "Email me a summary", "email this to mom".
- **`olympian_webhook_post`** - POST JSON to an allowlisted webhook URL. Zapier / n8n / GitHub Actions / Discord webhook dispatch.
- **`olympian_slack_post`** - if you run a personal Slack, post to a specific channel
- **`meshtastic_send`** - write a message back out the radio. Enables two-way conversation loop: Telegram triggers action, result broadcast on Meshtastic.
- **`homeassistant_call`** - call a Home Assistant service (turn off lights, set thermostat). Gated by allowlisted entities.

### Newsletter and feed

- **`zeus_newsletter_latest`** - pull the most recent digest without hitting the full web UI. For Meshtastic: "what's in today's newsletter?" returns the summary.
- **`zeus_newsletter_search`** - search across accumulated newsletter summaries by topic
- **`olympian_rss_fetch`** - fetch an allowlisted RSS feed and summarize. Useful when you want headlines but don't want Zeus re-ingesting the whole feed.

### Planning and meta

- **`olympian_plan`** - given a task description, return a structured `{steps: [...], estimated_minutes: N, risks: [...]}`. Not an action tool, it's a planning primitive that TaskRunner (LAB-332) can consume.
- **`olympian_reflect`** - given a recent conversation or task log, return a reflection: what went well, what to improve. Feeds back into memory as a namespaced fact.
- **`zeus_session_summary`** - summarize the current session on demand (rolling summary is automatic, this is explicit). "What have we discussed today?".

### Meshtastic-specific considerations

- **`olympian_precompute_summary`** - scheduled job, not a tool itself, but a pattern: pre-generate summaries at fixed intervals so Meshtastic reads are always instant. Tools read from the pre-computed file instead of triggering live LLM calls.
- **Batch-first design**: any Meshtastic-exposed tool should answer in under ~500 chars when possible. Prefer `zeus_profile` / `olympian_status_read` / `zeus_calendar_today` over `zeus_query`.

---

## Priority questions for triage

1. **Which integrations do I actually already run?** (Home Assistant yes/no, personal Slack yes/no, SMTP configured yes/no, Meshtastic node online yes/no.)
2. **What's the single canonical task store?** (Obsidian inbox, a JSON file, Things 3 export, Todoist API.)
3. **Which shell commands do I trust Zeus to run without my sign-off?** (Start small: `tailscale status`, `docker ps`, `df -h`. Add writes later.)
4. **Do I want two-way Meshtastic loop now or batch-read only?** (Two-way means writing a `meshtastic_send` service and a queue.)
5. **What's my appetite for `olympian_file_write`?** (Append-only to an inbox is low-risk; arbitrary writes are not.)

---

## What I want you to produce

For each tool above, a one-paragraph verdict:

```
### <tool_name>
**Verdict:** Build / Defer / Skip
**Priority:** High / Medium / Low
**Dependencies:** <new APIs, env vars, integrations>
**Safety:** <Aegis policy name, env gate, allowlist pattern>
**Signature sketch:**
@mcp.tool()
def <name>(<params>) -> <return>:
    """<docstring>"""
**Notes:** <one-line rationale>
```

Then a ranked shortlist of the 5-8 tools worth building first, and a proposed Linear ticket structure (parent + subs) for them.

---

## Constraints

- Python 3.11+, FastAPI, FastMCP
- File paths as comments at the top of each file
- No emdashes in any generated text or docs
- Every action tool gated by Aegis pre-hook (payload validation)
- Every shell-style tool gated by a dedicated env flag + regex allowlist
- Kairos allowlist stays read-only by default
- Prefer composition: each tool wraps a Core HTTP endpoint where possible, rather than reimplementing logic in `zeus/mcp/`

Go.
