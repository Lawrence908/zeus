# Aletheia: Documentation Drift Investigator

**Status:** Phase 1 implemented (`feat/aletheia`)
**Owner:** Chris
**Last updated:** 2026-07-28
**Depends on:** Argo swarm store/worker/notifier *patterns*; Kronos scheduler; Aegis policy engine
**Naming:** Aletheia, personification of truth and disclosure, the counterpart to Lethe (concealment). Role-domain fit: this agent's only job is to surface the gap between what the docs claim and what the code does.

---

## Changes from the first draft

The first draft had three design-level risks worth blocking on. They are fixed
in the sections below and called out here so the delta is legible:

1. **Exclusion enforcement was aspirational.** The draft listed personal-data
   globs but relied on a container `:ro` mount that "lands later," leaving v1
   with *no mechanism* stopping the worker's `Read` from touching `.env` or
   `zeus/data/**`. Now enforced at the tool boundary from day one (see
   [Read-only enforcement](#read-only-enforcement-three-layers)).
2. **"Depends on Argo P0/P1" undersold the new work.** The swarm coordinator is
   worktree/diff/merge/PR-centric and `RunSpec` hard-requires a single
   write-allowlisted repo. Aletheia has no worktree, no diff, no merge, and a
   multi-root read-only scope, so it gets its **own light runner**, not the
   swarm coordinator (see [Architecture](#architecture-what-is-reused-vs-new)).
3. **Server-wide reads could exfiltrate secrets.** The draft never screened
   findings, so a finding quoting a `compose.yaml` env line would ship a secret
   to Telegram and into the Knowledge layer. Findings are now **Aegis-screened**
   before any persistence or delivery (see [Delivery](#delivery)).

Two smaller corrections also baked in: the mechanical extractor+verifier path is
**primary** (the LLM worker only extends recall), and scheduling is via
**Kronos**, not Kairos (a nightly batch job is Kronos's shape).

---

## Purpose

Zeus has two documentation trees (`docs/` at repo root, `zeus/docs/`) plus
`CLAUDE.md`, `README.md`, and roughly a dozen subsystem specs. They drift from
the code continuously, and the drift is invisible until an AI collaborator is
bootstrapped from a stale `CLAUDE.md` and makes a wrong assumption.

Aletheia is a read-only investigator that walks documentation, resolves every
concrete reference it makes to the codebase, and reports what no longer holds. It
is the archetypal long-investigation task: tedious for a human, mechanically
verifiable, and valuable in proportion to how thorough it is.

This worker is **read-only in v1**. It reports drift; it does not fix it. See
[Phase 2](#phase-2-proposed-patches-not-built) for the write path.

---

## Architecture: what is reused vs new

Aletheia is a dedicated package, `zeus/orchestration/aletheia/`. It reuses the
Argo swarm's *patterns* (durable sqlite store, headless `claude -p` plumbing,
Telegram notifier) and the Kronos scheduler, but **not** the swarm coordinator.

Why not the swarm coordinator: it is built to take a single `RunSpec.repo`
(validated against the *write* allowlist), cut a git worktree, run an edit
worker, inspect the diff against a path denylist, merge into an integration
branch, and open a PR behind approval gates. Aletheia has none of those: no
single repo, no worktree, no diff, no merge, no PR, and no human plan/merge gate
(a read-only sweep should not stall on approval). Forcing it through the swarm
coordinator would be mostly conditionals bypassing that machinery. Instead:

| Concern | Aletheia | Reused from |
|---|---|---|
| Run/finding persistence | `store.py` (own schema) | *pattern* of `swarm/store.py` |
| Worker subprocess | `worker.py` | `swarm/claude_worker.py` helpers |
| Telegram | `notifier.py` | *pattern* of `swarm/notifier.py` |
| Scheduling | Kronos jobs + seed | `zeus/kronos/*` |
| Sweep control flow | `sweep.py` (own, fail-open, no worktree) | **new** |

Module map: `config` (guardrails), `models`, `extract`, `verifier`, `store`,
`worker`, `sweep`, `digest`, `notifier`, `api`. Push trigger:
`scripts/aletheia-post-receive.sh`. Tests: `tests/test_aletheia.py`.

---

## Scope

### Observe scope (read-only, server-wide)

Aletheia's *observe* scope is deliberately wide, because drift is assessed across
the whole server, not just the Zeus repo. This is the key divergence from the
coding swarm, whose *write* scope is deliberately narrow. Two separate config
lists that must never be conflated:

| Config | Purpose | Mode |
|---|---|---|
| `ZEUS_SWARM_REPO_ALLOWLIST` | Repos the coding swarm may worktree and commit to | read + write |
| `ZEUS_ALETHEIA_OBSERVE_ROOTS` | Paths Aletheia may read and analyse | read only |

`ZEUS_ALETHEIA_OBSERVE_ROOTS` is a newline/comma list of absolute paths. It is an
allowlist; `config.observe_roots()` **drops** unsafe roots (`/`, `~`, the home
dir itself) rather than honouring a typo that would widen the read scope to the
whole home directory.

### Read-only enforcement, three layers

The draft's layer 1 (tool allowlist) is porous on its own and layer 3 (`:ro`
mount) had not landed, which left the exclusion list unenforced. The corrected
model enforces exclusions *before* any sandbox:

1. **Tool allowlist** (`config.allowed_tools`): `Read,Grep,Glob` plus two
   read-only git subcommands. No `Edit`, `Write`, or unrestricted `Bash`.
2. **Exclusion denylist, enforced** (`config.disallowed_tool_specs`): every
   exclusion glob compiles into `--disallowedTools Read(<glob>)`, `Grep(<glob>)`,
   `Glob(<glob>)`. Deny beats allow in Claude Code's permission model, so the
   personal-data layer is unreadable even though `Read` is on the allowlist. The
   verifier's own filesystem scan independently honours `path_excluded()`, so the
   zero-LLM path can't read excluded files either. **This holds on the host tree
   today, before any container.**
3. **No worktree / future `:ro` mount**: it reads the live tree read-only; there
   is nothing to commit, and a bind-mount `:ro` (if/when containerised) is
   defence in depth on top, not the sole guarantee.

### Explicit exclusions (`ZEUS_ALETHEIA_EXCLUDE`)

```
**/.env, **/.env.*, **/.ssh/**, zeus/data/**, **/*.db, **/*.sqlite, **/*.sqlite3
```

`zeus/data/**` holds `context_pack.md`, the Obsidian mirror, the session DB, and
the small-LLM usage ledger. It is gitignored, but Aletheia reads the *live* tree,
so the exclusion is stated and enforced explicitly. Glob matching is `/`-aware in
`config.path_excluded()` (plain `fnmatch` would miss a root-level `.env` against
`**/.env`); this is exercised directly in the tests because a miss here is a real
leak, not a cosmetic bug.

---

## Triggers and cadence

### Scheduled (primary) - Kronos, not Kairos

A nightly full sweep is a batch job with a weekly digest, which is exactly
Kronos's shape; registering it as a "Kairos observation source" would force a
cron job into an observe/decide/act loop. It is a Kronos job
(`aletheia-nightly-sweep`) and inherits Kronos's enable gate, timeout, and runs
feed for free.

- `ZEUS_ALETHEIA_SCHEDULE`, default `0 3 * * *` (nightly off-peak).
- Additionally gated by `ZEUS_ALETHEIA_ENABLED`, so a seeded-but-off job never
  spends. Silent by design; findings persist for the weekly digest.

### Push-triggered (secondary)

`scripts/aletheia-post-receive.sh` computes the changed paths for a push and
POSTs them to `POST /aletheia/runs` with `mode: incremental`. Scope is docs that
are themselves changed, or that mention a changed path.

**Trust boundary (corrected).** `POST /aletheia/runs` can only ever trigger a
*read-only* investigation. There is no `worker`-type field to assert and no
write/merge gate to bypass, so a hook (or anything else) posting here cannot
escalate to a writing run, unlike the coding swarm's `POST /swarm/runs`. Read
scope stays bounded by `ZEUS_ALETHEIA_OBSERVE_ROOTS` and the enforced exclusions.

### Weekly digest

Kronos job `aletheia-weekly-digest` (`ZEUS_ALETHEIA_DIGEST_SCHEDULE`, default
`0 8 * * 1`).

---

## Finding schema and the verifier

Output is a list of structured findings, not prose, because a structured finding
is mechanically checkable.

`reference.kind` is one of `path`, `symbol`, `env_var`, `endpoint`, `config_key`,
`command`. `status` is one of:

| Status | Meaning | Source |
|---|---|---|
| `ok` | Resolves as documented | counted, never stored/reported |
| `missing` | Referenced thing does not exist | mechanical or worker |
| `moved` | Exists, but not where documented | mechanical or worker |
| `changed` | Signature/default/behaviour contradicts the doc | worker only (see below) |
| `unverifiable` | Not mechanically resolvable | stored, not reported |

Stable identity is `sha1(doc_path + reference.kind + reference.target)`, so the
same drift keeps its id across runs and the digest can compute new vs
carried-over vs resolved.

### Mechanical path is primary; the worker extends recall

The extractor (`extract.py`) pulls backticked references out of a doc and the
verifier (`verifier.py`) resolves each against the filesystem - high precision,
**zero LLM spend**. This is the primary path and catches the cheap, checkable
drift. The read-only Claude Code worker (`worker.py`, gated by
`ZEUS_ALETHEIA_WORKER_ENABLED`, default off) only *widens recall* into claims the
extractor can't parse; every candidate it emits is re-resolved by the same
verifier before it can be reported, so widening recall never lowers precision.

`changed` is deliberately **not inferred mechanically** - a grep can't decide
that a documented default contradicts the code. It can only arrive from the
worker and still needs human judgement (it is excluded from Phase-2 auto-patch).

### Acceptance check

The verifier runs independently of the worker, in Zeus:

1. Every finding carries a `reference` the verifier resolves on its own (paths and
   env vars directly; symbols/endpoints/commands by scanning the tree, honouring
   exclusions).
2. A worker finding whose independent resolution disagrees with its `status` is
   dropped and logged as a worker error (exact-match confirmation).
3. `unverifiable` findings are stored but not reported - signal for improving the
   extractor, not something to wake up to.

Known precision limit (tracked, not fixed in v1): `moved` on a very common symbol
name can mis-attribute; dotted `Class.method` references are confirmed only by
the final segment, so no `moved` is claimed for them.

---

## Delivery

| Trigger | Delivery |
|---|---|
| Push-triggered | Immediate terse Telegram: doc count, top findings, run id. |
| Scheduled nightly | No notification; findings persist silently. |
| Weekly digest | Markdown report (per doc; new vs carried vs resolved) + Telegram headline with a link. |

**Every reportable finding is Aegis-screened before it is persisted or
delivered** (`sweep._aegis_ok`, policy `ZEUS_ALETHEIA_AEGIS_POLICY`). The observe
scope is server-wide, so a finding could otherwise quote a secret from a
`compose.yaml`, Caddyfile, or `homelab-docs/network.md` and carry it into
Telegram *and* the Knowledge layer. A screen failure drops the finding closed
(fails safe), never leaks it.

The digest is written to `zeus/data/research/aletheia/weekly-<iso-week>.md` and
ingested into the Knowledge layer with `source="aletheia"`,
`source_id=<iso-week>`; `delete_by_source()` makes re-runs idempotent. Stable
identity lets the digest distinguish *new drift this week* from *drift sitting
there for weeks* and *drift that disappeared* (a fix, reflected back).

---

## Budget and failure behaviour

- `ZEUS_ALETHEIA_MAX_USD_FULL` / `_INCREMENTAL`, separate ceilings; `--max-turns`
  set per mode.
- Cost read from the worker result's `total_cost_usd` and accumulated on the run.
- Kill-switch is enforced **at document boundaries** - worker cost is only known
  after a node completes, so a single runaway doc can overrun its slice, but the
  next doc will not start once the ceiling is hit. `--max-turns` is the only
  within-document bound (turns are not dollars). The mechanical path is free, so
  a mechanical-only sweep never hits the ceiling.
- **Fail-open, per document.** The sweep is a DAG with one node per document and
  no edges. A node that errors or times out marks that document `incomplete` and
  the sweep continues; eleven of thirteen docs is worth eleven docs of value.

---

## Phase 2: proposed patches (not built)

A write mode that proposes doc edits. Constraints if/when it happens:

- Write scope collapses to `ZEUS_SWARM_REPO_ALLOWLIST` only; server-wide
  observation stays read-only forever. Aletheia may notice drift in a repo it
  cannot edit; it reports.
- Uses the standard Argo merge path: worktree, integration branch, one PR, merge
  approval gate. The swarm path denylist still applies (docs *describing*
  `zeus/safety/**` or `zeus/orchestration/**` are editable; those subsystems are
  not).
- Only `missing` and `moved` are auto-patch eligible; `changed` is a human call.

---

## Open questions

- [ ] Widen extraction from backticks to prose once the backtick baseline's catch
      rate is measured. v1 knowingly catches cheap drift and misses architectural
      prose ("QueryEngine fans out into four blocks") - be honest about that.
- [ ] Should push-triggered runs extend beyond the zeus repo (hook is per-repo)?
- [ ] Which non-zeus repos join `ZEUS_ALETHEIA_OBSERVE_ROOTS` initially?
- [ ] Doc-rename churn: identity keys on `doc_path`, so a rename reads as a wall
      of new+disappeared drift. `git`-follow or a claim slug later.
- [ ] Weekly digest day, and whether it should also land in Linear as a comment.

---

## Action items (Phase 1 - done)

1. [x] `ZEUS_ALETHEIA_OBSERVE_ROOTS` config + loader, distinct from the swarm
       write allowlist, with **enforced** exclusion globs
2. [x] Reference extractor over markdown (backticked paths, symbols, env vars,
       endpoints, commands)
3. [x] Finding schema as Pydantic, persisted with stable identity
4. [x] Independent verifier with disagreement logging + `unverifiable` handling
5. [x] Read-only worker invocation with allowlist + enforced denylist + per-mode
       budget
6. [x] Kronos nightly sweep job (replaces the Kairos-source idea)
7. [x] `post-receive` hook + `POST /aletheia/runs` incremental mode
8. [x] Telegram immediate notifier for incremental runs
9. [x] Weekly digest generator + Knowledge ingest (`source="aletheia"`)
10. [x] Per-document fail-open in the sweep + Aegis screening of every finding

---

## Linear tickets to file

Placeholder IDs only; replace after creation.

- `LAB-NEW-ALETHEIA-1` Aletheia parent: documentation drift investigator
- `LAB-NEW-ALETHEIA-2` Observe-root config and **enforced** exclusion
- `LAB-NEW-ALETHEIA-3` Reference extractor plus finding schema
- `LAB-NEW-ALETHEIA-4` Independent verifier
- `LAB-NEW-ALETHEIA-5` Kronos nightly job plus push-trigger hook
- `LAB-NEW-ALETHEIA-6` Telegram notifier plus weekly digest
