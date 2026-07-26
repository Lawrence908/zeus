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

- **C1 - Per-node model routing (done).** A doc edit costs the same as a hard refactor today. Add optional `model` to `TaskNodeSpec`/`TaskNode`; Metis picks it per node (cheap model - Haiku-class - for trivial nodes: docs, config, single-file, rename; strong model for logic/multi-file). The workers already thread `--model` through `build_command`, so this is mostly: wire `node.model -> build_command`, add `ZEUS_SWARM_MODEL_DEFAULT`/`ZEUS_SWARM_MODEL_CHEAP`, and extend the Metis prompt with model-selection guidance. ~10x on the trivial nodes.
- **C2 - Cost estimate + dry-run at the plan gate (done).** You currently approve blind, then spend. (a) Surface a per-node + run-total cost **estimate** (heuristic from model + tool_scope + title size, or a one-shot cheap-model estimator) on the RunView / Swarm app at Gate 1, shown against `budget_usd`. (b) A `dry_run` flag that runs the whole DAG against `StubWorker` (zero spend) to validate structure, gates, and merge order before committing to a real run.
- **C3 - Cheaper planning (done).** Metis runs a strong-model exploration pass per plan. Make the planner model configurable (`ZEUS_SWARM_PLANNER_MODEL`, cheaper default; strong as opt-in for hard projects) with bounded exploration turns, and **capture Metis's own `cost_usd`/`session` into the run** (currently unrecorded) so planning spend is visible.
- **C4 - Local-model worker tier (done).** Claude was the only worker; every node was paid. Added `LocalWorker` (`local_worker.py`) on the homelab Ollama behind the same `Worker` protocol. Ollama has no Claude-Code tool loop, so instead of an agentic loop it runs one structured `format:"json"` completion that emits `{files:[{path,content}]}` and writes them into the worktree (with worktree-escape rejection) - reliable for the node kind the planner tags `local`: a self-contained doc/config/template written from the task alone. `cost_usd` is always `0.0`. Routing is two-fold: `ZEUS_SWARM_WORKER=local` runs every node free, and `RoutingWorker` (default on via `ZEUS_SWARM_HYBRID_LOCAL`) wraps a paid `claude`/`sandbox` run so nodes tagged `model:"local"` (or a concrete Ollama tag) go free while hard nodes stay on claude. Metis prompt now offers `local` as the cheapest tier; the estimate scores local nodes at `$0`. Config: `ZEUS_SWARM_LOCAL_MODEL` (default `qwen2.5:7b-instruct`), `ZEUS_SWARM_OLLAMA_URL` (falls back to `OLLAMA_URL`). Live-smoked: `qwen2.5:7b` wrote a real README at `$0.0`. Limit: single-shot, no exploration - anything needing repo context stays on the paid tier.

**Cross-cutting:** wire swarm `cost_usd` into the existing `small_llm_usage.db` ledger + `/admin`; keep `max_attempts` default 1 so retries only cost where a `check` justifies them.

### Hardening + capability (after Phase C)


- **P5 - Sandbox the verifier (security; the code-execution hole - done).**
  Was: `CommandVerifier` ran `node.check` - an LLM-authored shell command - directly on the **host** in the worktree; P1b sandboxed the worker but not the check, so a planned `check` was an unsandboxed code-execution vector on zeus-core. Fixed: `SandboxedCommandVerifier` (`verifier.py`) runs the check in an ephemeral, resource-capped, `no-new-privileges`, `--cap-drop ALL` container with **only the worktree mounted** at `/work` and **`--network none` by default** (checks don't need egress). `main.py` selects it for all real workers when `ZEUS_SWARM_VERIFY_SANDBOX=1` (default) and docker is present; otherwise it falls back to host exec with a loud WARNING (`ZEUS_SWARM_VERIFY_HOST_FALLBACK=1`, default) or `FailClosedVerifier` when fallback is off. Image is `ZEUS_SWARM_VERIFY_IMAGE` (default `zeus-swarm-verify:latest`, `docker/verify/Dockerfile` - lean python+git+ruff+pytest; point it at a full runtime image for import-heavy checks). Live-smoked free: reads the worktree (pass), fails a bad check, `Network is unreachable` under `--network none`, and `/home/chris` absent (host FS isolated). 5 new tests.
  **Worker-sandbox egress policy (done).** `config.sandbox_egress()` selects how the worker container's network is constrained: `open` (default, back-compat bridge), `proxy` (join an `--internal` network with no route out and force all traffic through an allowlist HTTP(S) proxy via `HTTPS_PROXY`), or `none`. `docker/egress-proxy/` ships a tinyproxy image that default-denies every host except `*.anthropic.com`, with a README for the two-network setup. `build_docker_command` injects the proxy env; `SandboxedClaudeWorker` fails closed if `proxy` mode has no proxy URL. Live-verified: on the internal network a worker reaches `api.anthropic.com` through the proxy, `example.com` is denied, and direct egress can't even resolve DNS. 5 new tests.
  **Aegis `swarm` policy (done).** `zeus/safety/policies/swarm.yaml` screens the worker's reported output (diff summary + check output) for exfiltration to non-allowlisted hosts, leaked credentials/private keys, prompt-injection, and sensitive-file access. `Coordinator._aegis_screen()` runs it after verify and *before commit*, so unsafe output fails the node fail-open and never lands on the integration branch. Gated by `ZEUS_SWARM_AEGIS_ENABLED` (default on) on top of global `ZEUS_AEGIS_ENABLED`; policy name via `ZEUS_SWARM_AEGIS_POLICY`. It screens the summary, not the raw code diff, to avoid false positives on source. 7 new tests.
  Remaining (minor): guaranteeing `ANTHROPIC_API_KEY` is never logged (already passed by name into the container, never echoed).

- **P6 - Durable resume + reapers (resilience - done).**
  Was: the coordinator's `_workspaces` dict and in-flight `asyncio` tasks were in-memory; a zeus-core restart mid-run orphaned worktrees and left `running`/`pending_*` runs stuck, and a node interrupted mid-run stayed `running` forever. Fixed: `Coordinator.recover()` (`coordinator.py`) runs on startup (backgrounded from the lifespan, `ZEUS_SWARM_RESUME_ON_START=1` default) - it resets interrupted `running` nodes to `ready`, re-attaches the integration workspace via `CodeWorkspace.attach()` (re-uses the on-disk worktree, else re-checks-out the surviving branch, else clean `setup()` - never resets merged work), reaps orphan `swarm/run-*` worktrees+branches whose run is no longer live via `CodeWorkspace.reap_orphans()`, then re-drives `running` runs. `pending_final`/`paused_budget` runs get their workspace re-attached so a later approval still tears down cleanly. Live-smoked free: a crashed run's stuck node reset -> dispatched -> reached the final gate; dead-run debris reaped; live branch kept. 7 new tests.
  Not yet crash-safe *within* a node (a worker killed mid-`claude` still costs and re-runs from scratch on resume) - acceptable given the per-node worktree is atomic (nothing lands until merge). A periodic (not just startup) reaper is a later nicety.

- **P7 - Auto-PR + project gate (close the loop - done).**
  Was: verification was per-node only, and the final gate just left `swarm/run-<id>` for a manual PR. Now `Coordinator._finalize()` (runs on final-gate approval, before workspace teardown): (1) runs a run-level `project_check` on the assembled integration branch by reusing the **sandboxed** verifier (so the full suite/build runs isolated too); a failing check does not discard merged work - the run settles `completed_partial` with the check output, no PR, branch left to fix; a passing check (or none) with all nodes green settles `completed`; (2) opt-in `gh pr create` from the integration branch via `pr.py` (`git push -u origin` + `gh pr create`, best-effort, URL stored on the run). The `project_check` comes from the planner (new top-level `project_check` in the plan JSON), an API/`ZEUS_SWARM_PROJECT_CHECK` override, in that precedence. Store gained `project_check`/`project_check_passed`/`project_check_output`/`pr_url` (with an idempotent `ALTER TABLE` migration for existing dbs); the Swarm app shows the check badge + PR link. Metis cost was already captured in C3. 12 new tests.
  **Auto-PR is OFF by default (`ZEUS_SWARM_AUTO_PR=1` to enable):** pushing a branch and opening a PR on the real repo is an outward action, so it stays opt-in even though the final human approval authorizes it. CI polling on the opened PR is deferred to P8 (observability).

- **P8 - Observability + streaming (core done).**
  Was: the Swarm app polled every 4s with no metrics or audit surface. Now: (1) `GET /swarm/metrics` (`store.metrics()`) - run counts by status, node counts, retry rate, total + planner + per-model cost, avg cost/run; shown as a strip in the Swarm app. (2) A **durable audit log** (`swarm_events` table + `store.append_event`/`list_events`, `GET /swarm/runs/{id}/events`): every run-status change, approval open/resolve, and node succeeded/failed/skipped is recorded with a timestamp; shown as an Activity feed. (3) An **SSE stream** `GET /swarm/events` backed by an in-process `SwarmEventBus` the coordinator publishes to on every advance/resolve/kill; the Swarm app subscribes via `EventSource` and refreshes on push, dropping the poll to a 20s fallback. Store-layer logging is centralized (run-status/approval events fire from the store mutators). 12 new tests.
  **Deferred to P8b:** per-node argonaut transcript surfacing (`~/.claude/projects/<escaped-repo>/<session>.jsonl`) - genuinely limited because the sandbox worker writes its transcript inside an ephemeral container, not on the host, so only the host `claude` worker leaves one; and CI-status polling on the auto-opened PR.

- **P9 - Smarter execution (core done).**
  Was: a merge conflict failed the node outright; scheduling was FIFO; a stuck node had no escalation. Done: (P9a) **auto-rebase by redo** - on a merge conflict the coordinator re-cuts the node's worktree from the *new* integration tip and re-runs the worker with conflict feedback, up to `ZEUS_SWARM_MERGE_CONFLICT_RETRIES` (default 1) extra tries, before failing - so two nodes that raced on the same file both land instead of one dying fail-open. (P9b) **critical-path scheduling** - `dag.dispatchable` now returns ready nodes ordered by longest downstream chain first (`dag.critical_path_depth`), so the work that gates the most remaining nodes starts first (shorter makespan), deterministic on ties. Per-node model routing was already delivered in C1. 8 new tests.
  **Deferred to P9c - adaptive re-planning:** after repeated node failures, hand the failures back to Metis for a revised sub-DAG spliced into the running run. It is the biggest remaining execution feature (it mutates a live DAG: new nodes, new deps, store + workspace reconciliation mid-run) and wants its own phase.

- **P10 - Question gates + bidirectional Telegram (done).**
  Was: Telegram was notify-only, and a node that needed human clarification had nowhere to ask. Done: a **`QUESTION` gate** - a node carries an optional `question` (Metis emits it only for a genuine ambiguity); before that node runs the coordinator opens a `QUESTION` approval carrying the text, the run pauses, and the human replies with free text via `POST /swarm/runs/{id}/answer` (`Coordinator.answer()`, `approval_id` optional). The answer is stored on the node and injected into the worker prompt as a clarification; rejecting the gate skips the node. The Swarm app renders a question gate as a text box (answer / skip). **Bidirectional Telegram:** the notifier's question message shows the text and `/answer <run_id> <text>`; the bot now has an allowlisted `/answer` command wired via a late-bound callback to `Coordinator.answer()` (works even though the bot starts before the coordinator). 9 new tests.
  Not done: Telegram *inline buttons* for approve/reject (the `/answer` command + the app cover the interaction; inline callback buttons are a UX nicety for later).

- **P11 - Reach (core done).**
  Was: single-repo default, human-initiated runs only. Done: (P11a) **multi-repo allowlist surface** - `GET /swarm/repos` exposes `config.repo_allowlist()`; the Swarm app now offers a repo dropdown (no hardcoded path), so adding a repo to `ZEUS_SWARM_REPO_ALLOWLIST` makes it targetable. (P11b) **autonomous plan-gated proposal** - `POST /swarm/propose` (gated by `ZEUS_SWARM_PROPOSE_ENABLED`, default off) scopes a goal into a run that **always stops at the plan gate** with its budget **hard-capped at `ZEUS_SWARM_PROPOSE_BUDGET_USD`** (an initiator cannot exceed it), then pushes a notification so a human approves before any spend. Kairos gets a `swarm_propose` tool (`_OLYMPIAN_WRITE_DISPATCH`) that is double-gated: it must be added to `ZEUS_KAIROS_TOOL_ALLOWLIST` *and* the server flag must be on. So Kairos can *suggest* work but never spend without human approval. 6 new tests.
  **Deferred - cross-repo single run:** one run spanning multiple repos (per-repo worktrees, integration branches, and PRs) is a real architectural change and its own phase; the allowlist already lets a run target any one allowlisted repo.

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
