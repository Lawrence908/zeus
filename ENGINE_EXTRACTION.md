# Engine Extraction — Prompt

This file holds the briefing prompt for extracting Zeus into a generic engine that can be redeployed as multiple personae (e.g. Chris's "Zeus" + a goddess-themed deployment for someone else). Run it in a fresh Claude Code session started at `/home/chris/zeus`.

The sanitization pass (see `SANITIZATION_AUDIT.md`) parameterized personal content. This pass is the structural follow-up: persona layering, deployment isolation, plugin architecture for per-deployment ingest sources, and the engine/personal-overlay split.

---

## Prompt to paste

```
Mission: Plan and execute the extraction of this codebase into a generic AI-assistant engine
that can be deployed as multiple distinct personae on the same homelab (and later on
separate hosts) without leaking secrets, prompts, or data between deployments.

Context — read these first, in order:
- ./CLAUDE.md (root brief)
- ./docs/INDEX.md (doc map)
- ./SANITIZATION_AUDIT.md (what the previous pass already accomplished — do not redo it)
- ./zeus/docs/INDEX.md (product/subsystem docs)

Background you must internalize:
- Zeus is a self-hosted personal AI: voice + chat + Telegram + MCP + Meshtastic.
- The previous pass (April 2026) parameterized personal identifiers, introduced an
  override-dir loader for prompts and workspace templates, scrubbed sessions.db from git
  history via filter-repo, and verified the deployment still works. Build on that work; do
  not duplicate it.
- The first new deployment will be a goddess-themed persona for the operator's fiancée,
  focused (eventually) on stock-market / economy / news distillation. The persona name is
  not yet chosen — flag it as a decision.
- Both deployments will run on the same homelab initially (separate Docker projects,
  separate Qdrant collections, separate .env, separate data dirs). Eventually one may
  move to a separate host. Plan for isolation from day one.
- Do NOT reintroduce mem0 or LiteLLM (forbidden, see CLAUDE.md). Do NOT bypass Aegis. Do
  NOT collapse the two LLM layers (_run_llm + small_llm_call). Do NOT collapse the
  three-layer memory (Mnemosyne / Library / Reference). Do NOT commit or push.

Goal: a codebase where standing up a second deployment is a documented procedure
(clone repo → copy .env.example → fill in deployer identity, secrets, persona overrides →
docker compose up) and where each deployment's secrets, data, prompts, and per-deployment
plugins are physically isolated from every other deployment's.

The previous pass deferred the structural items below to this phase. They are the core of
this work:
- Greek subsystem-name strategy (engine vocab vs configurable vs renamed).
- Engine + overlay split (single repo with deployments/ dirs, vs engine repo + per-user
  overlay repos as submodules / pip package, vs fork-and-customize).
- MCP tool namespace (zeus_query → engine_query, configurable per deployment, or stay).
- Env var prefix (ZEUS_* → ENGINE_*, configurable, or stay).
- Qdrant collection naming (zeus_memories → per-deployment prefix, or stay).
- Eval queries + baselines (zeus/data/eval/queries.json, tests/retrieval_eval_*.json).
- Hardware narrative consolidation (root CLAUDE.md / README.md hardware references).
- Personal docs (docs/ZEUS_LINEAR_TICKET_PLAN.md, docs/memory-architecture-plan.md).
- .claude/settings.json — example file + gitignore strategy.
- Plugin architecture for per-deployment ingest sources (so finance/news ingest for the
  fiancée's persona doesn't require modifying the engine).
- Pre-existing bugs surfaced in Phase 3 verification (Qdrant client drift on
  /admin/ingest/stats, Ollama embed model-swap latency) — fix in this pass or defer.

Run in four phases. STOP and wait for explicit approval between Phase 1 and Phase 2, and
between Phase 2 and Phase 3.

=== Phase 1: Architecture audit + decision surface (READ-ONLY). ===

Produce ./ENGINE_EXTRACTION_PLAN.md. Structure:

1. **Inventory of what is "engine" vs "deployment-specific" today.** Walk the tree
   (zeus/core/, zeus/memory/, zeus/ingest/, zeus/orchestration/, zeus/safety/, zeus/voice/,
   zeus/api/, zeus/mcp/, zeus/integrations/, zeus/frontend/, zeus/bench/, scripts/,
   docs/, zeus/docs/, compose*.yaml, .env.example) and classify each subsystem / file
   group: ENGINE (generic, shared), OVERLAY (per-deployment customization), HYBRID
   (mostly engine but with deployment-specific knobs), or PERSONAL-DATA (lives in
   gitignored data dirs). For HYBRID items, name the specific knobs.

2. **Decisions to make (call out each, with options, recommendation, and rationale).**
   For each, list 2-3 options, the operator's likely answer if obvious, and the
   tradeoffs. The operator must explicitly answer each before Phase 3.
   - D1 — Repo structure: monorepo with `deployments/<name>/` overlay dirs vs
     engine repo + per-user overlay repos as git submodules vs fork-and-customize vs
     engine as a pip-installable package consumed by per-deployment repos.
   - D2 — Greek subsystem names (Mnemosyne / Library / Phaos / Orpheus / Kairos /
     Aegis / Iris / Oracle / Olympians): keep as engine vocab unchanged, rename to
     functional terms (memory / knowledge / voice-orb / voice / background-agent / safety
     / ingest / context-api / agent-swarm), or make configurable per deployment.
     Recommend keeping as engine vocab — the names are good and per-deployment renaming
     is huge churn for marginal benefit.
   - D3 — Top-level deployment identity: how does a deployment declare its name (e.g.
     "Zeus", "Athena")? New env var like `ENGINE_DEPLOYMENT_NAME`? How does that flow
     to: chat prompts, voice persona, Telegram bot username, MCP server name, /health
     responses, frontend title?
   - D4 — MCP tool prefix (zeus_query, zeus_profile, zeus_remember, zeus_ingest_trigger,
     zeus_memory_search, plus the Olympian tool pack): keep `zeus_` as engine namespace,
     rename to `engine_` / `assistant_`, or make the prefix configurable from
     `ENGINE_DEPLOYMENT_NAME` (so Athena's deployment exposes `athena_query`). Note
     the impact on existing MCP clients (Cursor, Claude Desktop) that have configs
     pointing at `zeus_*` tools.
   - D5 — Env var prefix (ZEUS_*): keep, rename to ENGINE_*, or support both with a
     deprecation period. Inventory how many ZEUS_* vars exist in `.env.example` and
     across the code so the cost is visible.
   - D6 — Qdrant collection naming (`zeus_memories`, `zeus_knowledge`): keep with a
     deployment-specific prefix prepended (e.g. `chris_zeus_memories`,
     `athena_zeus_memories`) so two deployments can share a single Qdrant instance, or
     require each deployment to run its own Qdrant. Recommend a configurable prefix
     for shared-Qdrant flexibility.
   - D7 — Service ports & docker-compose isolation: how do two deployments coexist on
     the same host? Compose project name + per-deployment port offsets in .env, or one
     compose stack per deployment in its own directory.
   - D8 — Plugin architecture for ingest sources. The fiancée's persona needs new
     ingest sources (RSS, financial APIs, news aggregators). Should new sources live
     in `zeus/ingest/sources/` in the engine (and benefit everyone), or be loadable
     from an overlay path? Propose a registration mechanism.
   - D9 — Eval fixtures (zeus/data/eval/queries.json,
     tests/retrieval_eval_*.json): genericize and ship as example, move to
     gitignored overlay, or keep as engine reference baseline noted as "reference
     deployment's corpus". Phase 2 of the previous pass deferred to (a) — revisit.
   - D10 — Personal docs in `docs/`: ZEUS_LINEAR_TICKET_PLAN.md (still references the
     operator's Linear workspace), memory-architecture-plan.md (decision narrative).
     Genericize, move to overlay, or split WHY/HOW.
   - D11 — Pre-existing bugs (Qdrant CollectionInfo client drift on
     /admin/ingest/stats, Ollama embed warmup latency on single-GPU prod): fix in
     this pass, defer to a separate ticket, or accept as known-not-fixed.
   - D12 — Goddess-themed deployment name. Not Claude's call. Flag the decision so
     the operator picks one (Athena and Hera are obvious; many other options).
   - D13 — `.claude/settings.json` strategy for the engine repo: relativized as it is
     today, or `.claude/settings.example.json` + gitignore the real one.
   - D14 — License. The repo currently has none. If there's any chance of going public,
     pick one before extraction; if staying private, flag for later.

3. **Proposed engine layout** (best guess, given recommended answers to D1-D14). Show
   the full directory tree of what the repo would look like post-extraction. Mark
   every file/dir as engine, overlay, gitignored, or unchanged.

4. **Migration plan** (stepwise, with verification gates between each step). For each
   step name: file moves/renames, code edits, config edits, docs edits, expected blast
   radius, how to verify the existing deployment still works after that step, and
   estimated edit volume (small / medium / large diff).

5. **Risk register.** Things that could break the existing deployment: prompt loader
   regressions, Qdrant collection rename data migration, MCP client config drift,
   docker-compose env-file resolution, frontend bundle staleness. Mitigation per item.

6. **Out of scope (for this pass).** Explicitly exclude: actually standing up the
   second deployment (separate effort once engine is ready), building finance/news
   ingest sources (separate effort), going public on GitHub (deferred per operator),
   Greek subsystem renames if D2 stays as recommended.

7. **Open questions for the operator.** Anything in the audit you couldn't answer
   yourself.

STOP. Do not edit anything. Wait for the operator to review and answer D1-D14.

=== Phase 2: Apply operator decisions and refine the plan. ===

Once decisions are in: rewrite the migration plan section of ENGINE_EXTRACTION_PLAN.md
with the chosen options baked in. List every file that will be created / moved /
renamed / deleted / modified. Estimate total diff size. Identify any decisions that
created new sub-decisions and surface them. STOP. Wait for the operator to approve the
refined plan before any edits.

=== Phase 3: Execute the migration. ===

Execute step by step from the approved migration plan. After each step:
- Run pytest (must stay green; if a test breaks, stop and report).
- Confirm `docker compose up -d zeus-core` boots cleanly and `/health` returns 200.
- Confirm the operator's existing deployment still resolves the override prompts and
  the existing Qdrant collections (use a configurable prefix that defaults to today's
  collection names if D6 chose configurable-prefix).
- Commit nothing. The operator commits per logical chunk after reviewing.

Constraints during execution:
- Build on the override-dir mechanism from the previous pass; do not replace it.
- Do not break Aegis pre/post hooks.
- Do not collapse _run_llm and small_llm_call.
- Do not collapse Mnemosyne / Library / Reference.
- mem0 stays out. LiteLLM stays out.
- Greek subsystem names stay unless D2 chose otherwise.
- Compose isolation: two deployments must be able to run on this host without
  port / collection / volume / network collisions.

=== Phase 4: Verify generic-deployer dry-run. ===

Without actually deploying a second instance, dry-run a fresh-deployer flow on paper:
1. Walk through what a hypothetical second deployer does after `git clone`. Document
   it as `docs/SECOND_DEPLOYMENT_RUNBOOK.md` (or update an existing deployment doc).
2. List every env var they must set, every overlay file they must create, every
   external service they must provision (Qdrant, Ollama, kiwix, optional Telegram
   bot, optional Brave key, optional voice stack), and the order of operations.
3. Identify any step that requires editing engine code rather than overlay/config —
   flag those as engine debt.
4. Verify the operator's existing deployment one more time end-to-end:
   - pytest green
   - `docker compose up -d` clean
   - smoke test: chat reply, memory search, /admin endpoints, voice WS handshake if
     enabled in .env, MCP tool list.
5. Append a HANDOFF section to ENGINE_EXTRACTION_PLAN.md listing what's deferred to
   the next phases (build second deployment, build finance/news ingest plugin, public
   release prep).

Report back when each phase completes. Do not commit, do not push, do not delete the
git backups in /tmp.
```

---

## What this prompt produces

- `ENGINE_EXTRACTION_PLAN.md` — the audit + decisions + migration plan + risk register, populated through Phases 1-2 and updated through Phases 3-4.
- `docs/SECOND_DEPLOYMENT_RUNBOOK.md` (or equivalent) — the documented procedure for standing up a second persona on the same homelab.
- A series of small, reviewable diffs (uncommitted) that you commit per logical chunk.
- No edits to existing prompt overrides, real `.env`, or git history.

## When to run it

Run Phase 1 in a quiet hour — it's read-only and won't conflict with Kronos work. Pause on the decisions for as long as you need (especially D12 — goddess-name choice — and D8 — plugin architecture, which is the most consequential structural call). Run Phases 2-4 after Kronos merges so you're not stacking two structural changes.
