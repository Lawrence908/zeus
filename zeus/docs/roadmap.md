# Zeus Roadmap

Current-state snapshot and near-term work. Authoritative ticket-level tracking lives in [docs/ZEUS_LINEAR_TICKET_PLAN.md](../../docs/ZEUS_LINEAR_TICKET_PLAN.md). The original sprint plan is archived at [legacy/roadmap_legacy.md](legacy/roadmap_legacy.md).

## Where Zeus is today (April 2026)

| Area | State |
|------|-------|
| Scaffold, compose stack, infra | Shipped. `compose.yaml` + `compose.override.yaml` bind-mount pattern in use on daedalus. |
| Memory layer | Shipped. mem0 removed; `MemoryStore` (`zeus/memory/store.py`) owns writes with bi-temporal payloads, LLM fact extraction via `small_llm_call`. |
| Knowledge layer | Shipped. `KnowledgeStore` (`zeus/memory/library.py`) with dense + BM25 hybrid (RRF) via Qdrant, optional BGE-reranker. Baseline 30-query eval: hit@1 0.60, hit@5 0.867, hit@10 0.933, MRR@10 0.71. |
| Reference layer | Shipped (Phase 1). `zeus/memory/reference.py` proxies kiwix (Wikipedia ZIM) and optional NOMAD Qdrant at retrieval time. |
| Retrieval fan-out | Shipped. `QueryEngine._collect_retrieval_context()` parallel-fetches four labelled blocks (Profile, Memories, Knowledge, Reference) with sub-budgets inside `ZEUS_CONTEXT_MAX_TOKENS`. |
| Small-LLM router | Shipped. `small_llm_call()` with privacy-tier gate, daily USD cap, SQLite usage ledger. Default chain: `gemini_paid,groq,openrouter,anthropic_haiku,ollama`. |
| Chat / Telegram / MCP | Shipped. Text chat with SSE streaming, sessions, Telegram plain-text bot with allow-list + Aegis filter, MCP tools `zeus_query / zeus_profile / zeus_remember / zeus_memory_search / zeus_ingest_trigger`. |
| Voice pipeline | Host-native scaffold in place (`zeus/voice/`). Wake, STT, TTS, Phaos state emission all wired; needs end-to-end latency validation. |
| Phaos orb | React + `@react-three/fiber` component in `zeus/frontend/`. Subscribes to `WS /ws/voice-state`. |
| Agent runtime + bus | Shipped. `runtime.py`, `bus.py`, `hooks.py`, Aegis pre + post hooks, `TaskRunner`, correlation IDs. |
| Kairos background daemon | Shipped in `zeus/orchestration/daemon.py`. Read-only tool allowlist by default (`ZEUS_KAIROS_TOOL_ALLOWLIST=zeus_memory_search`). Off by default (`ZEUS_KAIROS_ENABLED=0`). |
| Aegis | Shipped. `AegisPolicyEngine` with `evaluate_text` + `evaluate_payload`; policies in `zeus/safety/policies/*.yaml`; pre- and post-hooks registered on the bus. NemoClaw + OpenShell runbook: [docs/nemoclaw-ops.md](../../docs/nemoclaw-ops.md). |
| Admin + metrics | Shipped. `/admin`, `/admin/metrics`, `/admin/ingest/stats`, `/admin/settings` (runtime model switch, Telegram restart). React Settings page wraps these. |
| Benchmarks | Shipped. `zeus/bench/` module + `POST /models/benchmarks/run` + Settings UI badge. Persisted to `zeus/data/benchmarks.json`. |
| Olympus deployment | Not yet. Daedalus is the current always-on host. Deployment runbook is ready: [deployment.md](deployment.md). |

## Near-term (next sprint)

Source of truth is [ZEUS_LINEAR_TICKET_PLAN.md](../../docs/ZEUS_LINEAR_TICKET_PLAN.md). Themes currently open:

- **Retrieval tuning.** Extend `tests/retrieval_eval.py` with labelled Profile vs Knowledge ground-truth queries (LAB-NEW-D). Retune sub-budget percentages after data lands.
- **Olympus migration.** Move the always-on instance from daedalus to Olympus. Smoke + systemd units are documented; the only real work is redoing ingest and re-recording voice.
- **Kairos observability.** Surface `last_action_summary` and cycle count on `/admin` once the daemon runs full-time.
- **Static chat sunset.** `zeus/core/static/chat.html` and `viz/` are still served for fallback; can be removed once the React SPA covers every route.

## Future / backlog

Items that do not block the always-on deploy but extend the surface. Full list in the ticket plan; highlights:

- **Phaos TTS level sync.** Per-frame `audio_level` during `speaking` so the orb tracks TTS loudness.
- **Browser voice turn.** Push-to-talk in the React app, hitting the same Core / LLM / TTS path as Orpheus.
- **WebXR AR.** `ARButton` + immersive-ar on the orb scene.
- **Retrieval quality eval by layer.** Gate sub-budget changes on per-layer recall@5.
- **Rate-limit or auth on `POST /voice-state/publish`** when Core is exposed beyond localhost.

## Related

- [architecture.md](architecture.md): subsystem map
- [deployment.md](deployment.md): Olympus deployment runbook
- [model-comparison.md](model-comparison.md): measured tok/s + VRAM fit per model
- [docs/ZEUS_LINEAR_TICKET_PLAN.md](../../docs/ZEUS_LINEAR_TICKET_PLAN.md): ticket-level roadmap
- [docs/memory-architecture-plan.md](../../docs/memory-architecture-plan.md): three-layer memory plan + migration runbook
- [legacy/roadmap_legacy.md](legacy/roadmap_legacy.md): original sprint tracker
