# Zeus Swarm (Argo): system brief

Status as of 2026-09-18. This is the **carry-out doc**: enough to reason about the
swarm without reading the code. Design rationale lives in
[`swarm-orchestration-plan.md`](swarm-orchestration-plan.md); eval philosophy in
[`themis-spec.md`](themis-spec.md).

One-line summary: **Argo is a merged, tested, fully-dark multi-agent coding swarm
with a working acceptance gate and nothing valid to measure improvement against.**

---

## 1. What it is

Argo takes a goal, plans it into a DAG of coding tasks, runs those tasks as
headless Claude Code processes in isolated git worktrees, verifies each one,
merges the successful ones onto a per-run integration branch, and stops at a human
gate before anything reaches `main`.

It is **not** a gateway and does not route across GPUs. The coding work is Claude
API; there is no local inference to arbitrate. Local models are used only for
nodes explicitly tagged cheap (`RoutingWorker` → Ollama).

Everything runs on the host that runs `zeus-core` (daedalus). There is no
per-host dispatch and no "send this node to apollo".

## 2. Naming, and two names that mislead

| Name | What it actually is |
|---|---|
| **Argo** | the swarm. `zeus/orchestration/swarm/`, ~2,700 LOC, 20 files |
| **argonaut** | one worker: a `claude -p` process in a worktree |
| **Metis** | the planner (goal → DAG) |
| **Olympus** | **not a service.** A hostname label for a future prod box. Zero code. The always-on host is daedalus |
| **Ruflo** | **not installed.** A YAML dialect parsed by ~90 lines of hand-written `runtime.py`. Superseded by Argo |

`AgentRuntime`/`TaskRunner`/`bus.py` are the pre-Argo layer: a config registry, a
sequential step runner, and an HTTP loopback to `localhost:8000`. Treat them as
legacy; Argo does not use them.

## 3. Execution model

```
goal
 └─ Metis plans a DAG ─────────── PLAN GATE (human)
     └─ per node, up to max_parallel (default 3, bounded 1-16):
         1. worktree cut from the integration tip, tracked files only
         2. argonaut edits (claude -p --output-format stream-json)
         3. verify: node.check in a sandboxed container
         4. Aegis screen on the output
         5. denylist check on the DIFF
         6. commit, merge into swarm/run-<id>
     └─ project check on the assembled branch ── FINAL GATE (human)
         └─ optional PR to main (ZEUS_SWARM_AUTO_PR, off by default)
```

Load-bearing properties:

- **Worktrees check out tracked files only.** `zeus/data/` is gitignored, so it
  never reaches a worker. A privacy boundary for free.
- **The container owns no git.** Only the worktree is mounted; the host
  coordinator does every commit and merge. Workers run as the host uid so files
  they write are host-owned and committable.
- **The denylist is enforced on the diff**, not just on tool arguments. An agent
  that can weaken its own policy has no policy.
- **Fail-open.** A node that exhausts retries marks its dependents unreachable and
  the run settles `COMPLETED_PARTIAL`: you get the passing subgraph, not nothing.
- **Durable.** SQLite store (`zeus/data/swarm.db`); `recover()` resets interrupted
  nodes and re-attaches worktrees across `zeus-core` restarts.

## 4. Worker protocol

The single extension seam (`zeus/orchestration/swarm/worker.py`):

```python
class Worker(Protocol):
    async def run(self, node, run, workspace, feedback=None) -> WorkerResult: ...
```

| Implementation | Mechanism | Auth |
|---|---|---|
| `StubWorker` | no-op | none (default) |
| `ClaudeCodeWorker` | host subprocess | inherits env; **silently falls back to your `~/.claude` subscription if `ANTHROPIC_API_KEY` is unset** |
| `SandboxedClaudeWorker` | `docker run --cap-drop ALL` | **hard-fails without the key**; passed by name only, never in argv |
| `LocalWorker` / `RoutingWorker` | HTTP to Ollama | none |

Selected by `ZEUS_SWARM_WORKER=stub|claude|sandbox|local`. **Use `sandbox` for
unattended work**, because the host path's silent subscription fallback means
unattributable spend across many iterations.

## 5. Isolation

Worker container: `--rm --init --cap-drop ALL --security-opt no-new-privileges`,
memory 2g, cpus 2, pids 512, HOME on tmpfs, worktree bind-mounted at `/work`.

**Egress defaults to `proxy`** (changed 2026-09-18): the worker joins an
`--internal` docker network with no route out, and reaches Anthropic only through
an allowlist tinyproxy. Verified: `api.anthropic.com` → 404 (reached),
`example.com` → `CONNECT tunnel failed, 403`, no-proxy → DNS failure.
`open` is now an explicit opt-out.

**Verify host-fallback defaults off** (changed 2026-09-18): a check that cannot be
sandboxed fails the node rather than running LLM-authored shell on the host.

Verify network is `none` for node checks. The run-level project check may use a
wider network (`ZEUS_SWARM_VERIFY_PROJECT_NETWORK`) **only when it came from the
env default**, a per-run `project_check` arrives from the API or planner, so it
is treated as untrusted and stays locked down.

## 6. The acceptance gate

`scripts/acceptance.py`, wired as `ZEUS_SWARM_PROJECT_CHECK`. Decides whether an
iteration is an improvement. Exit 0 accept, non-zero reject.

**Guards vs ratchets.** Guards prove nothing broke and can only return "no worse";
a loop of guards alone accepts neutral churn forever. Ratchets must move up.

| Gate | Kind | Trigger |
|---|---|---|
| diff hygiene (denylist, file cap) | guard | always |
| ruff | guard | always |
| import check | guard | always |
| frozen test suite | guard | always |
| tool-use eval | guard | diff touches `zeus/core/tools/` |
| retrieval eval | **ratchet** | diff touches `zeus/memory/`, `zeus/core/query.py` |

A diff touching no ratchet path is rejected as out of confined scope.

**Anti-gaming, both load-bearing:**

1. **The frozen suite is extracted from the baseline ref**, not read from the
   worktree (`git archive <ref> tests/`). An agent editing an existing test cannot
   move its own score; new test files it adds still run.
2. **The harness, query suites and baselines are on the denylist.** The loop may
   propose a baseline; a human promotes one.

**Consequence worth understanding:** the frozen suite cannot distinguish "agent
weakened a test" from "change intentionally redefines a contract". Both look the
same, so a deliberate behaviour change always fails the gate. This is the
intended constraint: **the loop improves implementations; humans redefine
contracts.**

**Refusals that prevent false signals** (each found by running it live, not by
reasoning):

- **Config mismatch is a hard refusal.** A metric is only comparable to a baseline
  captured the same way. Observed: running without the deployed env scored
  `hit@5 0.03` against a `0.61` baseline **on a no-op comment**, a plausible,
  catastrophic, entirely fictional regression.
- **Errored queries are a reject, not a score.** `score_suite` is fail-open per
  query, so a total outage returns N errored rows rather than raising.
- **Stale/flat-shape baseline is a hard failure**, never a fallback.
- **Cross-provider tool-use comparison is refused**: selection accuracy is a
  property of the model as much as of the code.
- **Noise floor**: deltas under `ZEUS_ACCEPTANCE_TOLERANCE` (default 5pp) are
  neither regression nor improvement. Suite must meet a minimum size.

## 7. Current state

**Built, merged, tested.** PR #44 merged 2026-07-25. P0–P11 plus hardening. 143
swarm tests, 171 including the gate. Deferred by design: adaptive re-planning
(P9c), Telegram inline buttons, cross-repo single run.

**Dark.** No `ZEUS_SWARM_*` in `.env` or `compose.yaml`; no `swarm.db`; no
`swarm/run-*` branches; `ZEUS_SWARM_WORKER` defaults to `stub`. It has never run.

**Images built** (2026-09-18): `zeus-swarm-argonaut` (808 MB),
`zeus-swarm-verify` (1.08 GB), `zeus-swarm-egress-proxy` (12.4 MB). Networks
`zeus-swarm-egress` (internal) and `zeus-swarm-egress-out` exist; proxy running.

**The gate is proven end to end** in the verify sandbox: guards pass, frozen suite
runs 397 green on a clean diff, live scoring runs against Qdrant/Ollama,
regression detection fires, config guard refuses an incomparable baseline.

### The blocker: nothing valid to ratchet on

Measured 2026-09-18 under the deployed config:

| Layer | n | hit@1 | hit@5 | hit@10 |
|---|---|---|---|---|
| knowledge | 30 | **1.00** | 1.00 | 1.00 |
| profile | 3 | 0.00 | 0.00 | 0.33 |

- **Knowledge is saturated**, 30/30 at rank 1. No headroom; a ratchet rejects
  everything forever. The rerank work moved it from `hit@1 0.5667`.
- **Profile has headroom but is unmeasurable**, n=3, seeded unverified, one case
  is 33pp against a 5pp tolerance.
- **Tool-use is saturated too**, `selection_accuracy 1.0`, `false_positive_rate
  0.0` on 17 cases. Hence guard, not ratchet.

**No baseline has been promoted.** Promoting a saturated suite would lock in a
loop that can never accept anything while looking correctly configured.

### Known gaps

- `eval_suite`'s recorded config block omits the memory-layer flags
  (`ZEUS_MEMORY_HYBRID`, `ZEUS_MEMORY_RERANK`) and collection names, so the config
  guard has a blind spot, a silently-400ing profile layer passed it.
- The verify image resolves `>=` at build time and pulled `qdrant-client 1.19.1`
  against a 1.17.0 server. Pin it before running unattended.
- `.env.*` in the denylist also matches `.env.example`, so an agent cannot
  document a new env var.
- `FlagEmbedding` in `requirements.txt` appears dead (nothing imports it since the
  reranker became an httpx client) and pulls ~5.3 GB of torch + CUDA.
- `zeus/orchestration/CLAUDE.md` still documents only Ruflo.

## 8. Operating it

Enable (gated, sandboxed):

```bash
ZEUS_SWARM_ENABLED=1
ZEUS_SWARM_WORKER=sandbox
ZEUS_SWARM_SANDBOX_EGRESS=proxy            # now the default
ZEUS_SWARM_EGRESS_PROXY=http://zeus-swarm-egress-proxy:8888
ZEUS_SWARM_SANDBOX_NETWORK=zeus-swarm-egress
ZEUS_SWARM_PROJECT_CHECK="python scripts/acceptance.py"
ZEUS_SWARM_VERIFY_PROJECT_NETWORK=homelab-web   # where zeus-qdrant + zeus-ollama live
ZEUS_SWARM_VERIFY_IMAGE=zeus-swarm-verify:latest
ANTHROPIC_API_KEY=...                       # required by the sandbox worker
```

Leave off until deliberately chosen: `ZEUS_SWARM_AUTO_PR`,
`ZEUS_SWARM_PROPOSE_ENABLED` (lets Kairos suggest runs; always plan-gated, budget
capped at $1).

### Interaction surfaces (all already built, none exercised)

1. **HTTP + SSE**, `/swarm/propose|runs|plan|approve|answer|kill|events|metrics`,
   plus per-node transcripts and `gh pr checks` rollup.
2. **Zeus OS SPA**, `zeus-os/src/lib/apps/Swarm.svelte` (423 lines) + `api/swarm.ts`.
3. **Telegram**, approval prompts and bidirectional `/answer` for question gates.

The intended human loop is: approve the plan, answer questions as they arrive,
approve the final gate, review the PR. Approvals are latency-tolerant and
mobile-friendly (Telegram); monitoring is visual (SPA); the PR is where code
review actually happens.

## 9. What unblocks the project

Suite work, not harness work.

1. Grow the knowledge suite until it has headroom, harder queries, ideally minted
   from real query-log usage (highest signal per Themis; blocked on a persisted
   query log).
2. Verify and grow the 3 profile queries past the noise floor.
3. Widen `eval_suite`'s config block so the guard can see the memory layer.
4. Pin the verify image's deps to deployed versions.
5. **Then** baseline, under a committed tree.
