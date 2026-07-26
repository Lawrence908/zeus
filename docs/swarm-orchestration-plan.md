# docs/swarm-orchestration-plan.md - Swarm Orchestration Plan (Argo)

**Goal:** give the swarm a software project goal + a target repo, and have it **scope** the work, **decompose** it into a task graph, **dispatch** sandboxed Claude Code workers to do the work, **verify** against acceptance criteria, and drive to completion - under **checkpoint approvals**.

Working name: **Argo** (the quest engine); workers are **argonauts**; the scoper is **metis**. Names are tentative - swap to taste (Greek convention per root `CLAUDE.md`).

## Locked decisions (this phase)

| Decision | Choice |
|---|---|
| Target domain | Software / dev tasks (this repo + other local projects) |
| Autonomy (v1) | Checkpoint approvals - plan approval + approval on risky/write actions |
| Worker substrate | Hybrid - Zeus orchestrator + Claude Code / Agent SDK workers |
| Isolation | Container / OS sandbox (OpenShell gateway / NemoClaw), git worktree per task |
| Repo scope | **Allowlist config of absolute repo paths**, ships with just `~/zeus` (`ZEUS_SWARM_REPO_ALLOWLIST`). Adding canary/AstrID later is a config edit. |
| Worker invocation | **Claude Code CLI, headless** (`claude -p --output-format stream-json`) in the sandbox container |
| Merge strategy | **Per-run integration branch** `swarm/run-<id>` (commit-per-node); one PR out at the end |

## What we build on (existing substrate)

- `AgentRuntime` / `AgentDefinition` (`zeus/orchestration/runtime.py`) - YAML agents, lifecycle.
- `TaskRunner` - **sequential** step executor; `StepResult`; `on_failure: skip|retry|abort`. → extend to a DAG.
- Bus (`bus.py`) with Aegis pre/post hooks on every call; in-memory task ring buffer → **replace with durable store**.
- Kairos daemon - observe/decide/act loop (single-purpose today).
- Sandbox: `docs/nemoclaw-ops.md` (OpenShell gateway :8080, NemoClaw containers); Aegis `code_execution.yaml`, `file_access.yaml`, `tool_arguments.yaml`.

## Architecture

```
 goal + repo
     │
     ▼
 [Metis: Scoper/Planner]  → spec + task DAG (nodes: title, deps, acceptance, tool_scope)
     │   ── APPROVAL GATE 1 (approve plan) ──
     ▼
 [Argo Coordinator]  ── schedules ready DAG nodes (deps met), ≤ max_parallel
     │        │
     │        ├─▶ [Argonaut worker]  (Claude Code / SDK subagent)
     │        │      • ephemeral sandbox container + git worktree of target repo
     │        │      • scoped tools: edit / shell / test / git
     │        │      • write/risky action ── APPROVAL GATE 2 (or auto per policy)
     │        │      • every tool call ── Aegis
     │        │
     │        ▼
     │   [Verifier]  runs acceptance checks (tests/lint/build) per node
     │        │  fail → bounded retry / re-plan   pass → merge worktree
     ▼        ▼
 all nodes done + project gate ── APPROVAL GATE 3 (final review/merge) ── DONE
```

**Components (new, under `zeus/orchestration/swarm/`):**
- `planner.py` (Metis) - goal → scoped spec → DAG. Uses oracle context + Library repo knowledge; `small_llm_call` for structure, chat LLM for reasoning.
- `dag.py` - task-graph model + scheduler (ready-set, topological, parallel).
- `coordinator.py` (Argo) - run lifecycle, approval gates, budgets, retries, merge.
- `worker_client.py` - spawns/monitors an argonaut (Claude Code headless / Agent SDK) inside a sandbox container; streams StepResults over the bus.
- `verifier.py` - acceptance-check runner (per-node + project-level).
- `approvals.py` - approval-gate primitive + `PENDING_APPROVAL` state.
- `store.py` - durable run/task/approval store (SQLite first; Postgres if it graduates).

## Data model (durable - replaces the ring buffer)

- **Run** `{ id, goal, repo, spec, status, budget, created_at }`
- **TaskNode** `{ id, run_id, title, deps[], acceptance, tool_scope, status, worker_id, results[], attempts }`
- **Approval** `{ id, run_id, task_id, kind: plan|write|final, state: pending|approved|rejected }`
- Extend `TaskRecord`/`StepResult`; add DAG edges. Statuses gain `pending_approval`, `blocked`.

## API + UI surface

- `zeus/core/` → `/swarm/*`: `POST /swarm/runs` (submit), `GET /swarm/runs/{id}` (+ DAG), `POST /swarm/runs/{id}/approve`, `GET /swarm/runs/{id}/stream` (SSE/WS), `POST /swarm/runs/{id}/kill`.
- Zeus OS → new **Swarm** app: submit goal, live DAG view, approve gates, per-node logs.
- Approvals also reachable via Telegram (reuse `integrations/telegram`).

## Safety contract (extends the Agentic Safety Contract)

- **Every** argonaut tool call passes Aegis (`code_execution`, `file_access`, `tool_arguments`).
- **All writes are sandboxed**: worktrees + ephemeral containers; nothing touches homelab services / `compose.yaml` / running containers - this phase is **dev-scoped only** (ops automation is a separate, deferred scope with its own gate).
- **Per-run budgets**: USD (reuse the small-LLM ledger pattern), wall-clock, tool-call count, `max_parallel` workers. Exceed → pause for approval.
- **Kill-switch** + full audit trail in the run store; default-deny tool scope per node (planner grants the minimum).

## Phasing

- **Phase 0 - Foundations (done).** DAG task model + durable run store; `/swarm/*` API; approval-gate primitive; repo allowlist + self-edit denylist config; **fail-open** semantics; dispatch to a **stub** worker. State machine + gates verified end-to-end (15 tests).
- **Phase 1a - Worker seam (host, done).** Real Claude Code argonaut: `claude -p --output-format stream-json` on a **git worktree** of `~/zeus`, scoped `--allowedTools`, `session_id`/`total_cost_usd` captured, run on the **host** (denylist diff-check, no container). Commit-per-node onto `swarm/run-<id>`. Verified end-to-end with a live run (real edit committed, cost captured); integration commits use `--no-verify`, commit failures fail-open.
- **Phase 1b - Sandbox (worker built; container run pending real image).** `SandboxedClaudeWorker` (`sandbox.py`) wraps the same claude argv in `docker run --rm --init --user <host uid> --cap-drop ALL --security-opt no-new-privileges --memory/--cpus/--pids-limit`, bind-mounting the node's worktree at `/work`. Worker contract unchanged from 1a; the host still owns git. Image: `docker build -t zeus-swarm-argonaut:latest docker/argonaut` (node + `@anthropic-ai/claude-code` + git). Enable with `ZEUS_SWARM_WORKER=sandbox`. Budgeted costs, as predicted: **auth** - a fresh container has no `~/.claude` session, so `ANTHROPIC_API_KEY` is required and passed by name (`-e ANTHROPIC_API_KEY`); **egress** - the container needs `api.anthropic.com` (default network for now; lock down later). Knobs: `ZEUS_SWARM_SANDBOX_{IMAGE,NETWORK,MEMORY,CPUS,PIDS}`.
- **Phase 2 - Metis planner (done).** `planner.py`: `ClaudePlanner` runs `claude -p --permission-mode plan --output-format json` (read-only) in the repo, explores it, and emits a JSON node DAG; `parse_plan` extracts it defensively (raw / fenced / prose-wrapped). `POST /swarm/plan {goal, repo}` scopes the goal into a run awaiting plan approval - the Metis-proposed DAG IS Gate 1. `StubPlanner` for tests / no-LLM. The coordinator (P0) already runs the DAG respecting deps.
- **Phase 3 - Verify loop + budget (done); parallelism (P3b).** `verifier.py`: each node carries a `check` (shell command); `CommandVerifier` runs it in the worktree *before* commit, so only passing work lands. The coordinator retries up to `max_attempts`, feeding the check output back to the worker each attempt (`Worker.run(..., feedback=)`); exhaustion fails the node fail-open. Metis emits `check`/`max_attempts`. Budget kill-switch: node `cost_usd` accumulates; exceeding `budget_usd` pauses the run (`PAUSED_BUDGET`) behind a `BUDGET` approval that grants headroom on approve.
- **Phase 3b - Parallelism (done).** Per-node git worktrees on `swarm/run-<id>-n-<node>` branched from the current integration tip; the coordinator dispatches a ready batch of up to `max_parallel` nodes concurrently (`asyncio.gather`), each worker+verify running in its own worktree. Passing work is committed on the node branch and merged into the integration branch under a per-run lock (worktree creation + merge serialized; the slow worker/verify are not). A merge conflict aborts cleanly and fails the node fail-open. Tested: two independent nodes both land; two nodes editing the same file race to merge, one wins, the other fails-open (stable across orderings).
- **Phase 4 - UX (done); resilience later.** Zeus OS **Swarm app** (`zeus-os/src/lib/apps/Swarm.svelte` + `api/swarm.ts`, registered as kind `Swarm`): scope a goal (`POST /swarm/plan`), watch the live DAG (node status/cost/deps/errors, budget spent/cap), tap the approval gates, kill a run. **Telegram approvals**: the coordinator fires `approval_opened` on each in-run gate (node-write / budget / final); `TelegramNotifier.from_env()` pushes a prompt via the Bot API (`TELEGRAM_BOT_TOKEN` + chat id), best-effort so a notify failure never affects the run. Durable resume after restart is the remaining resilience item (integration branches already persist in git).

**Naming:** `argo` collides with Argo Workflows / Argo CD (which may run on this homelab). `Argo` coordinator + `argonauts` workers is kept, but env/config are namespaced `ZEUS_SWARM_*` to avoid friction.

## Future phases (post-P4 roadmap)

P0-P4 make Argo functionally complete for sequential and parallel runs on `~/zeus`. These phases harden it for real, unattended, production use. Ordered by priority.

### Phase C - Cost & efficiency (chosen next; ahead of P5+)

Every node is a full paid `claude -p` invocation, one model is used for all nodes, and you approve the plan before seeing any cost - so the per-run spend is what limits real usage. This phase attacks that. Ordered by leverage-over-effort; **C1 + C2 deliver most of the savings with low effort.**

- **C1 - Per-node model routing (biggest lever, low effort).** A doc edit costs the same as a hard refactor today. Add optional `model` to `TaskNodeSpec`/`TaskNode`; Metis picks it per node (cheap model - Haiku-class - for trivial nodes: docs, config, single-file, rename; strong model for logic/multi-file). The workers already thread `--model` through `build_command`, so this is mostly: wire `node.model -> build_command`, add `ZEUS_SWARM_MODEL_DEFAULT`/`ZEUS_SWARM_MODEL_CHEAP`, and extend the Metis prompt with model-selection guidance. ~10x on the trivial nodes.
- **C2 - Cost estimate + dry-run at the plan gate.** You currently approve blind, then spend. (a) Surface a per-node + run-total cost **estimate** (heuristic from model + tool_scope + title size, or a one-shot cheap-model estimator) on the RunView / Swarm app at Gate 1, shown against `budget_usd`. (b) A `dry_run` flag that runs the whole DAG against `StubWorker` (zero spend) to validate structure, gates, and merge order before committing to a real run.
- **C3 - Cheaper planning.** Metis runs a strong-model exploration pass per plan. Make the planner model configurable (`ZEUS_SWARM_PLANNER_MODEL`, cheaper default; strong as opt-in for hard projects) with bounded exploration turns, and **capture Metis's own `cost_usd`/`session` into the run** (currently unrecorded) so planning spend is visible.
- **C4 - Local-model worker tier (stretch).** Claude is the only worker; every node is paid. Add a `local` worker on the homelab Ollama (e.g. `qwen2.5-coder`) behind the same `Worker` protocol - a minimal read/propose-diff/apply loop for trivial nodes, with claude reserved for hard nodes via C1 routing. Bigger build (Ollama has no Claude-Code tool loop), so it is a later stretch, but it turns doc/config/boilerplate nodes free.

**Cross-cutting:** wire swarm `cost_usd` into the existing `small_llm_usage.db` ledger + `/admin`; keep `max_attempts` default 1 so retries only cost where a `check` justifies them.

### Hardening + capability (after Phase C)


- **P5 - Sandbox the verifier + egress lockdown + Aegis (security; do first).**
  Gap: `CommandVerifier` runs `node.check` - an LLM-authored shell command - directly on the **host** in the worktree. P1b sandboxes the worker but not the check, so a planned `check` is an unsandboxed code-execution vector on zeus-core. The sandbox also uses the default docker network (unrestricted egress), and the swarm's denylist is separate from the existing `AegisPolicyEngine`.
  Scope: run `check` inside the same container image as the worker (mount the worktree, restricted network); a dedicated egress policy (allow only `api.anthropic.com` + whatever package registries a run needs); route the worker's diff summary + check output through Aegis under a new `swarm` policy; guarantee `ANTHROPIC_API_KEY` is never logged.

- **P6 - Durable resume + reapers (resilience).**
  Gap: the coordinator's `_workspaces` dict and in-flight `asyncio` tasks are in-memory; a zeus-core restart mid-run orphans worktrees and leaves `running`/`pending_*` runs stuck. Node execution is not crash-safe (a node interrupted mid-run stays `running`).
  Scope: on startup, scan the store for non-terminal runs, reconcile against on-disk git worktrees/branches, re-attach integration worktrees, and resume `running` runs (reset interrupted `running` nodes to `ready`, re-dispatch); a periodic reaper for orphaned worktrees/branches from dead runs.

- **P7 - Auto-PR + project gate + CI (close the loop).**
  Gap: the final gate leaves `swarm/run-<id>` for a manual PR; verification is per-node only; Metis's own `cost_usd`/`session` is never recorded.
  Scope: at the final gate run a run-level `project_check` (full test suite / build) on the integration branch; on pass `gh pr create` from `swarm/run-<id>` and link the PR in the run/store/UI; optionally poll CI on the PR and reflect status; capture Metis cost into the run.

- **P8 - Observability + streaming.**
  Gap: the Swarm app polls every 4s; there is no metrics or audit surface.
  Scope: `/swarm/metrics` (run counts, success/partial/fail + retry rates, cost per run/model) into `/admin`; a durable audit log (approvals: who + when, node transitions); an SSE/WS event stream to the Swarm app to replace polling; surface each argonaut's transcript (`~/.claude/projects/<escaped-repo>/`) per node.

- **P9 - Smarter execution.**
  Gap: a merge conflict fails the node outright; scheduling is FIFO; one model for all nodes; a stuck node has no escalation to re-planning.
  Scope: on merge conflict, auto-rebase the node branch onto the new integration tip and re-run the worker once (recover both nodes' work) before failing; critical-path-aware scheduling; per-node model routing (cheap model for trivial nodes); adaptive re-planning - after repeated node failures, hand the failures back to Metis for a revised sub-DAG.

- **P10 - Bidirectional Telegram + question gates.**
  Gap: Telegram is notify-only, and a node that needs human clarification has nowhere to ask.
  Scope: Telegram inline buttons (approve/reject) -> callback -> `/swarm/approve`; a `QUESTION` approval kind + node state where an argonaut writes a question file and the run pauses for a typed answer, fed back as `feedback`; plan and final-PR links in the messages.

- **P11 - Reach.**
  Gap: single-repo (`~/zeus`), human-initiated runs only.
  Scope: multi-repo allowlist + cross-repo run coordination; Kairos-initiated swarm runs (the background daemon proposes and launches low-risk runs under tight budgets and mandatory gates, extending its read-only allowlist only with an Aegis review).

**Cross-cutting (not phase-gated):** grow the test suite alongside each phase; keep the plan doc and `zeus/orchestration/CLAUDE.md` in sync; align terminology with Ruflo/olympians so the swarm reads as one subsystem; a `swarm` seed policy under `zeus/safety/policies/`.

## Resolved

- **Repo scope:** an allowlist of absolute repo paths (`ZEUS_SWARM_REPO_ALLOWLIST`, `zeus/orchestration/swarm/config.py`), shipping with just `~/zeus`. "Anything under `~/`" is rejected: `~` holds non-repos, `.ssh`, and stray `.env` files, and a worktree needs a git repo anyway. Two things fall out of targeting the zeus repo:
  - Worktrees only check out **tracked** files. `zeus/data/` is gitignored, so a worker's workspace never contains the context pack, the Obsidian mirror, or the SQLite ledgers - a privacy boundary for free, and a second reason to use worktrees over pointing a container at the live tree.
  - A worker editing the zeus repo can edit the thing supervising it. A **path denylist** (`ZEUS_SWARM_PATH_DENYLIST`, default `zeus/safety/policies/**`, `zeus/orchestration/**`, `.env*`) is enforced by the coordinator on the worker's **diff** (P1b), not just via tool args. An agent that can weaken its own Aegis policy has no Aegis policy.
- **Worker invocation:** Claude Code CLI, headless: `claude -p --output-format stream-json`, with `--allowedTools`, `--permission-mode`, and `--max-turns` as the safety surface. The result JSON carries `session_id` and `total_cost_usd`, which drop into the usage ledger and give the kill-switch a real threshold (both already on the `WorkerResult` / `TaskNode` models). The `Worker` protocol is the seam - CLI now, SDK later without touching the coordinator. Set `ANTHROPIC_API_KEY` regardless (overrides subscription auth, makes spend attributable per run). Transcripts land as JSONL under `~/.claude/projects/<escaped-repo-path>/`; capture cost/session from the result object and, for question-asking, have the worker write its question set to a repo markdown file rather than blocking.
- **Merge strategy:** PR-per-task and a task DAG conflict (if B depends on A, B's worktree needs A's changes; gating that on review stalls the run at the first dependency edge). Instead: the coordinator merges each passing node's worktree into a per-run integration branch `swarm/run-<id>` (one commit per node); dependent nodes branch from the integration branch so the DAG flows; at the end, one PR from `swarm/run-<id>` to `main`. Artifact = batched PR per run; internal mechanism = auto-merge; diff is reviewable commit-by-commit. The two gates stay put: plan approval in, merge approval out.
- **Fail-open:** when a node exhausts its retries it does not fail the run. The coordinator marks the node `failed`, marks its transitive dependents `unreachable`, and keeps scheduling the rest; the run settles to `completed_partial` (delivering the passing subgraph) unless nothing succeeded. Built into the P0 model (`RunStatus.COMPLETED_PARTIAL`, `NodeStatus.UNREACHABLE`), not bolted on.

## Proposed defaults (adjust anytime)

- **Cost ceiling:** hard cap **$10 / run** (surfaced from the small-LLM + Claude Code usage ledger); pause for approval at 80%.
- **max_parallel:** **3** argonauts (bounded by host + sandbox capacity).
- **Worker image:** one base sandbox image (git, ripgrep, node, python, common build tools) + a per-run overlay hook for project-specific toolchains. Refine at Phase 1.
- **Retry budget:** 2 acceptance-fail retries per node before it escalates to an approval gate.

## Roadmap linkage

Fits root `CLAUDE.md`'s orchestration principles (tool-first, plan/execute/reflect, Aegis on every autonomous path) and extends Projects 7/10 in `docs/ZEUS_LINEAR_TICKET_PLAN.md`. Add a new project block there once Phase 0 scope is agreed.
