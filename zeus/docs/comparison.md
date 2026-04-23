# Where Zeus borrows from other agent frameworks

Quick reference for the patterns Zeus explicitly lifted from other open-source agent frameworks, and what it keeps unique. This doc is historical context, not a feature matrix: the current source of truth for shipped behavior is [architecture.md](architecture.md) and the [Linear ticket plan](../../docs/ZEUS_LINEAR_TICKET_PLAN.md).

## Borrowed patterns

| From | Pattern | Where it lives in Zeus |
|------|---------|------------------------|
| Ruflo v3.5 | MCP-first tool integration | `zeus/mcp/` (FastMCP over Zeus Core HTTP) |
| Ruflo v3.5 | YAML-defined agent manifests | `zeus/orchestration/agents/*.yaml` loaded by `runtime.py` |
| Squad | Pre/post hook pipeline around tool calls | `zeus/orchestration/hooks.py` + `zeus/safety/integration.py` |
| Squad | Session persistence and resumable interactions | `zeus/core/sessions.py` (in-memory or SQLite) |
| Claude Code | Tool-first loops over chat-first reasoning | `zeus_*` MCP tools; Kairos observe/decide/act |
| Claude Code | Reflection on empty or failed replies | 3-attempt retry in `QueryEngine.query()` |

## Intentional differences

- **Voice-first orchestration.** Orpheus pipeline (wake, STT, chat, TTS) is a first-class path, not a bolt-on.
- **Personal-memory-first design.** Three labelled blocks in the system prompt (Profile, Memories, Knowledge, Reference) with sub-budgeted retrieval. Bulk docs never go through LLM fact extraction.
- **Hand-rolled data plane.** `MemoryStore`, `KnowledgeStore`, `small_llm_call` router all own their Qdrant and provider boundaries directly; no mem0, no LiteLLM, no LangChain.
- **Local-first prod.** Olympus (RTX 3080, 10 GB) runs Qwen2.5-7B via Ollama for chat; small-LLM router has Ollama as the local-fallback last hop.
- **Privacy-tier gate.** Every `small_llm_call` declares `min_privacy_tier`; Gemini free tier is excluded from the chain because it trains on input.

## Prioritized work pointer

The authoritative sprint and ticket plan is [docs/ZEUS_LINEAR_TICKET_PLAN.md](../../docs/ZEUS_LINEAR_TICKET_PLAN.md). Current-sprint goals live in [roadmap.md](roadmap.md).
