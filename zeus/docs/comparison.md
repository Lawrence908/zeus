# Zeus vs Ruflo vs Squad

This document compares Zeus against Ruflo and Squad and highlights what Zeus should implement next.

## Feature Matrix

| Capability | Zeus (current) | Ruflo | Squad | Zeus Gap / Action |
|---|---|---|---|---|
| Agent orchestration runtime | YAML contracts only | Full coordinator + topologies + workflows | Coordinator + router + fan-out | Build Python runtime + coordinator + event bus |
| Inter-agent communication | Planned via FastAPI bus | Message bus + worker services | Event bus + typed tools | Implement bus adapter and routing primitives |
| Safety/policy layer | Designed (Aegis), not implemented | Security tooling and policy modules | HookPipeline with pre/post policy checks | Implement hook pipeline and `AegisFilter` |
| Voice interface | Detailed spec only | Not a focus | Not a focus | Implement Orpheus end-to-end (core differentiator) |
| Memory architecture | Strong: mem0 + Qdrant + ingest | Hybrid memory modules available | File-native memory in `.squad` | Add session memory, consolidation, scheduled ingest |
| Text chat UX | None | Chat UI in separate package | Interactive shell + remote bridge | Add minimal web chat for development and fallback |
| MCP support | None | First-class MCP server/client | MCP-aware templates/integration | Add Zeus MCP server tools |
| Observability | Smoke test script | Perf tooling + targets | Telemetry + monitoring modules | Add query logs, ingest metrics, admin dashboard |
| Session continuity | None | Partial conversation concepts | Session store + resume flow | Add session model and rolling summaries |
| Deployment maturity | Compose + runbook | Multiple deployment paths | CLI/runtime workflows | Keep current Compose path; add sidecars gradually |

## What Zeus Should Borrow

### From Ruflo

- Modular orchestration shape (runtime, bus, plugins, workers)
- MCP-first integration model for tool interoperability
- Workflow-driven execution with explicit dependencies

### From Squad

- Policy enforcement pattern (before/after hook pipeline)
- Session persistence and resumable interactions
- Practical operator UX for interactive use and status inspection

## What Zeus Should Keep Unique

- Voice-first architecture (wake word -> STT -> context -> LLM -> TTS)
- Personal memory-first design (ingest + mem0 + Qdrant tuned for one user)
- Local-first production path on Olympus hardware constraints

## Prioritized Implementation Order

1. Finish Sprints 1-4 already defined in `roadmap.md`
2. Build lightweight orchestration runtime (Sprint 5)
3. Add sessions and conversation continuity (Sprint 6)
4. Add text chat interface for dev and fallback UX (Sprint 7)
5. Add MCP server for external assistant interoperability (Sprint 8)
6. Add observability and continuous ingest automation (Sprint 9)
7. Expand ingest source adapters (Sprint 10)
