<!-- src/lib/apps/Swarm.svelte — Argo swarm: scope a goal into a DAG, watch it
     run, and tap the approval gates. -->
<script lang="ts">
  import { onDestroy, onMount } from 'svelte';
  import type { AppInstance } from '$lib/wm/tree';
  import { notify } from '$lib/notify/store';
  import {
    answerQuestion,
    approve,
    getRun,
    killRun,
    listRuns,
    nodeTranscript,
    openEventStream,
    planRun,
    runCi,
    runEvents,
    swarmHealth,
    swarmMetrics,
    swarmRepos,
    type ApprovalKind,
    type NodeStatus,
    type CiStatus,
    type Run,
    type RunView,
    type SwarmEvent,
    type SwarmMetrics,
    type TranscriptEvent
  } from '$lib/api/swarm';

  export let app: AppInstance;
  void app;

  let enabled: boolean | null = null;
  let runs: Run[] = [];
  let selected: RunView | null = null;
  let selectedId = '';
  let error = '';
  let busy = false;
  let timer: ReturnType<typeof setInterval> | null = null;
  let stream: EventSource | null = null;
  let metrics: SwarmMetrics | null = null;
  let events: SwarmEvent[] = [];
  let ci: CiStatus | null = null;
  let openNode = '';
  let transcript: { exists: boolean; events: TranscriptEvent[] } | null = null;

  async function loadCi() {
    if (!selected?.run.pr_url) {
      ci = null;
      return;
    }
    try {
      ci = await runCi(selected.run.id);
    } catch {
      ci = null;
    }
  }

  async function toggleTranscript(nodeId: string) {
    if (openNode === nodeId) {
      openNode = '';
      transcript = null;
      return;
    }
    openNode = nodeId;
    transcript = null;
    if (!selected) return;
    try {
      transcript = await nodeTranscript(selected.run.id, nodeId);
    } catch {
      transcript = null;
    }
  }

  let goal = '';
  let repo = '';
  let repos: string[] = [];
  let dryRun = false;

  const NODE_COLOR: Record<NodeStatus, string> = {
    succeeded: 'text-ok',
    failed: 'text-err',
    unreachable: 'text-err',
    skipped: 'text-muted',
    running: 'text-warn',
    ready: 'text-accent',
    pending_approval: 'text-accent2',
    blocked: 'text-muted'
  };

  const GATE_LABEL: Record<ApprovalKind, string> = {
    plan: 'Approve plan',
    node_write: 'Approve write',
    budget: 'Over budget — continue',
    final: 'Approve merge (final)',
    question: 'Clarification needed'
  };

  let answers: Record<string, string> = {}; // approval_id -> draft answer

  async function refresh() {
    try {
      runs = await listRuns();
      if (selectedId) selected = await getRun(selectedId);
      metrics = await swarmMetrics();
      error = '';
    } catch (e) {
      error = String(e);
    }
  }

  async function pick(id: string) {
    selectedId = id;
    openNode = '';
    transcript = null;
    try {
      selected = await getRun(id);
      events = await runEvents(id);
      await loadCi();
    } catch (e) {
      notify({ title: 'Load failed', body: String(e).slice(0, 140), kind: 'err' });
    }
  }

  // SSE push (P8): refresh the list, and the open run + its events, on change.
  async function onStreamUpdate(runId: string) {
    try {
      runs = await listRuns();
      if (runId === selectedId) {
        selected = await getRun(runId);
        events = await runEvents(runId);
        await loadCi();
      }
      metrics = await swarmMetrics();
    } catch {
      /* transient; the fallback poll will catch up */
    }
  }

  async function submitPlan() {
    if (!goal.trim() || busy) return;
    busy = true;
    try {
      const view = await planRun(goal.trim(), repo.trim(), dryRun);
      goal = '';
      const est = view.estimate ? ` · est $${view.estimate.total_usd.toFixed(2)}` : '';
      notify({ title: dryRun ? 'Planned (dry-run)' : 'Planned', body: `${view.nodes.length} nodes${est} — approve to run`, kind: 'ok' });
      await refresh();
      await pick(view.run.id);
    } catch (e) {
      notify({ title: 'Plan failed', body: String(e).slice(0, 180), kind: 'err' });
    } finally {
      busy = false;
    }
  }

  async function resolve(approvalId: string, ok: boolean) {
    if (!selected) return;
    busy = true;
    try {
      selected = await approve(selected.run.id, approvalId, ok);
      await refresh();
    } catch (e) {
      notify({ title: 'Approve failed', body: String(e).slice(0, 160), kind: 'err' });
    } finally {
      busy = false;
    }
  }

  async function sendAnswer(approvalId: string) {
    if (!selected) return;
    const text = (answers[approvalId] || '').trim();
    if (!text) return;
    busy = true;
    try {
      selected = await answerQuestion(selected.run.id, text, approvalId);
      answers[approvalId] = '';
      await refresh();
    } catch (e) {
      notify({ title: 'Answer failed', body: String(e).slice(0, 160), kind: 'err' });
    } finally {
      busy = false;
    }
  }

  async function kill() {
    if (!selected) return;
    busy = true;
    try {
      selected = await killRun(selected.run.id);
      await refresh();
    } finally {
      busy = false;
    }
  }

  $: pending = selected ? selected.approvals.filter((a) => a.state === 'pending') : [];
  $: nodeSpent = selected ? selected.nodes.reduce((s, n) => s + (n.cost_usd || 0), 0) : 0;
  $: planSpent = selected ? selected.run.planner_cost_usd || 0 : 0;
  $: spent = nodeSpent + planSpent;

  onMount(async () => {
    try {
      enabled = (await swarmHealth()).enabled;
    } catch {
      enabled = false;
    }
    try {
      repos = (await swarmRepos()).repos;
      if (repos.length && !repo) repo = repos[0];
    } catch {
      /* repos endpoint unavailable; leave the picker empty */
    }
    await refresh();
    // Live updates via SSE; keep a slow poll as a fallback if the stream drops.
    stream = openEventStream(onStreamUpdate);
    timer = setInterval(refresh, stream ? 20000 : 4000);
  });
  onDestroy(() => {
    if (timer) clearInterval(timer);
    stream?.close();
  });
</script>

<div class="h-full w-full flex flex-col font-mono text-xs">
  {#if enabled === false}
    <div class="bg-warn/20 border-b border-warn/40 px-3 py-2 text-warn">
      Swarm is disabled. Set <span class="text-fg">ZEUS_SWARM_ENABLED=1</span> (and
      <span class="text-fg">ZEUS_SWARM_WORKER=sandbox</span>) on zeus-core.
    </div>
  {/if}
  {#if error}
    <div class="bg-err/20 border-b border-err/40 px-3 py-2 text-err">{error}</div>
  {/if}

  <!-- submit -->
  <header class="px-3 py-2 border-b border-border/40 flex items-center gap-2">
    <input
      bind:value={goal}
      placeholder="Goal to scope + complete…"
      class="flex-1 bg-surface rounded border border-border/50 px-2 py-1 outline-none text-fg focus:border-accent/70"
      on:keydown={(e) => e.key === 'Enter' && submitPlan()}
    />
    {#if repos.length}
      <select
        bind:value={repo}
        class="w-44 bg-surface rounded border border-border/50 px-2 py-1 outline-none text-muted focus:border-accent/70"
        title="Target repo (from the swarm allowlist)"
      >
        {#each repos as r}
          <option value={r}>{r.split('/').slice(-1)[0]}</option>
        {/each}
      </select>
    {:else}
      <input
        bind:value={repo}
        class="w-44 bg-surface rounded border border-border/50 px-2 py-1 outline-none text-muted"
        title="Target repo (must be on the swarm allowlist)"
      />
    {/if}
    <label class="flex items-center gap-1 text-[10px] text-muted cursor-pointer" title="Run the DAG against a stub (zero spend) to validate its shape">
      <input type="checkbox" bind:checked={dryRun} />
      dry-run
    </label>
    <button
      class="px-3 py-1 rounded bg-accent text-bg disabled:opacity-40"
      disabled={busy || !goal.trim()}
      on:click={submitPlan}
    >{busy ? '…' : 'plan'}</button>
  </header>

  {#if metrics && metrics.runs_total > 0}
    <div class="px-3 py-1 border-b border-border/30 text-[10px] text-muted flex items-center gap-3 flex-wrap">
      <span>{metrics.runs_total} runs</span>
      <span class="text-ok">{metrics.runs_by_status.completed ?? 0} done</span>
      <span class="text-warn">{metrics.runs_by_status.completed_partial ?? 0} partial</span>
      <span class="text-err">{metrics.runs_by_status.failed ?? 0} failed</span>
      <span>retry {(metrics.retry_rate * 100).toFixed(0)}%</span>
      <span class="text-fg">${metrics.cost_total_usd.toFixed(2)} total</span>
      <span>~${metrics.avg_cost_per_run_usd.toFixed(2)}/run</span>
    </div>
  {/if}

  <div class="flex-1 flex min-h-0">
    <!-- runs -->
    <ul class="w-1/3 overflow-y-auto border-r border-border/40">
      {#each runs as r (r.id)}
        <li class="border-b border-border/20" class:bg-surface2={r.id === selectedId}>
          <button class="w-full text-left px-3 py-2 hover:bg-surface2/60" on:click={() => pick(r.id)}>
            <div class="text-fg truncate">{r.goal}</div>
            <div class="text-[10px] text-muted mt-0.5">{r.status} · {r.id.slice(0, 8)}</div>
          </button>
        </li>
      {:else}
        <li class="px-3 py-6 text-muted text-center">No runs. Scope a goal above.</li>
      {/each}
    </ul>

    <!-- detail -->
    <section class="flex-1 overflow-y-auto p-3">
      {#if selected}
        <header class="flex items-center justify-between mb-2 gap-2">
          <div class="min-w-0">
            <h3 class="text-accent text-sm truncate">{selected.run.goal}</h3>
            <p class="text-[10px] text-muted">
              {selected.run.status}{selected.run.dry_run ? ' · dry-run' : ''}
              · spent ${spent.toFixed(2)}{planSpent ? ` (plan $${planSpent.toFixed(2)})` : ''}{selected.estimate ? ` / est $${selected.estimate.total_usd.toFixed(2)}` : ''} of ${selected.run.budget_usd.toFixed(2)}
              · x{selected.run.max_parallel}
            </p>
          </div>
          <button class="text-[10px] px-2 py-0.5 border border-err/60 text-err rounded shrink-0" on:click={kill}>kill</button>
        </header>

        {#if selected.run.project_check}
          <div class="mb-2 text-[10px] flex items-center gap-2 flex-wrap">
            <span class="text-muted">project check <span class="text-fg">{selected.run.project_check}</span></span>
            {#if selected.run.project_check_passed === true}
              <span class="text-ok">passed</span>
            {:else if selected.run.project_check_passed === false}
              <span class="text-err">failed</span>
            {:else}
              <span class="text-muted/60">not run</span>
            {/if}
            {#if selected.run.pr_url}
              <a class="text-accent underline" href={selected.run.pr_url} target="_blank" rel="noopener">open PR ↗</a>
              {#if ci && ci.status !== 'no_pr'}
                <span
                  class:text-ok={ci.status === 'passing'}
                  class:text-err={ci.status === 'failing'}
                  class:text-warn={ci.status === 'pending'}
                  class:text-muted={!['passing', 'failing', 'pending'].includes(ci.status)}
                  title={ci.checks.map((c) => `${c.name}: ${c.state}`).join('\n')}
                >CI {ci.status}</span>
              {/if}
            {/if}
          </div>
        {/if}

        {#if pending.length}
          <div class="mb-3 space-y-1">
            {#each pending as a (a.id)}
              {#if a.kind === 'question'}
                <div class="border border-accent2/50 rounded px-2 py-1.5 bg-accent2/5">
                  <div class="text-accent2 mb-1">{GATE_LABEL[a.kind]}{a.node_id ? ` · ${a.node_id}` : ''}</div>
                  {#if a.detail}<p class="text-fg mb-1 whitespace-pre-wrap">{a.detail}</p>{/if}
                  <div class="flex items-center gap-1">
                    <input
                      bind:value={answers[a.id]}
                      placeholder="Your answer…"
                      class="flex-1 bg-surface rounded border border-border/50 px-2 py-1 outline-none text-fg focus:border-accent2/70"
                      on:keydown={(e) => e.key === 'Enter' && sendAnswer(a.id)}
                    />
                    <button class="text-[10px] px-2 py-0.5 rounded bg-accent2 text-bg" disabled={busy || !(answers[a.id] || '').trim()} on:click={() => sendAnswer(a.id)}>answer</button>
                    <button class="text-[10px] px-2 py-0.5 rounded border border-border/60 text-muted" disabled={busy} on:click={() => resolve(a.id, false)}>skip</button>
                  </div>
                </div>
              {:else}
                <div class="flex items-center justify-between gap-2 border border-accent/40 rounded px-2 py-1 bg-accent/5">
                  <span class="text-accent2">{GATE_LABEL[a.kind]}{a.node_id ? ` · ${a.node_id}` : ''}</span>
                  <span class="flex gap-1 shrink-0">
                    <button class="text-[10px] px-2 py-0.5 rounded bg-accent text-bg" disabled={busy} on:click={() => resolve(a.id, true)}>approve</button>
                    <button class="text-[10px] px-2 py-0.5 rounded border border-border/60 text-muted" disabled={busy} on:click={() => resolve(a.id, false)}>reject</button>
                  </span>
                </div>
              {/if}
            {/each}
          </div>
        {/if}

        <p class="text-[10px] text-muted uppercase tracking-widest mb-1">DAG</p>
        <ul class="space-y-1">
          {#each selected.nodes as n (n.id)}
            <li class="border-b border-border/20 py-1">
              <div class="flex items-center justify-between gap-2">
                <span class="truncate">
                  <span class="text-fg">{n.id}</span>
                  {#if n.deps.length}<span class="text-muted/60"> ← {n.deps.join(',')}</span>{/if}
                  <span class="text-muted"> · {n.title}</span>
                </span>
                <span class="shrink-0 flex items-center gap-1 {NODE_COLOR[n.status]}">
                  {n.model ? `${n.model} · ` : ''}{n.status}{n.cost_usd ? ` · $${n.cost_usd.toFixed(2)}` : (selected.estimate ? ` · ~$${(selected.estimate.per_node[n.id] ?? 0).toFixed(2)}` : '')}{n.attempts > 1 ? ` · ${n.attempts}x` : ''}
                  {#if n.session_id}
                    <button class="text-[9px] px-1 rounded border border-border/50 text-muted hover:text-fg" on:click={() => toggleTranscript(n.id)}>log</button>
                  {/if}
                </span>
              </div>
              {#if n.error}<p class="text-err text-[10px] whitespace-pre-wrap">{n.error}</p>{/if}
              {#if openNode === n.id}
                <div class="mt-1 ml-2 border-l border-border/40 pl-2 max-h-40 overflow-y-auto">
                  {#if transcript === null}
                    <p class="text-[10px] text-muted">loading…</p>
                  {:else if !transcript.exists}
                    <p class="text-[10px] text-muted">No transcript on disk (sandbox workers write theirs inside the container).</p>
                  {:else}
                    {#each transcript.events as ev}
                      <p class="text-[10px] whitespace-pre-wrap"><span class="text-muted/70">{ev.role}:</span> {ev.text}</p>
                    {/each}
                  {/if}
                </div>
              {/if}
            </li>
          {/each}
        </ul>

        {#if events.length}
          <p class="text-[10px] text-muted uppercase tracking-widest mt-3 mb-1">Activity</p>
          <ul class="space-y-0.5">
            {#each events.slice(0, 40) as ev (ev.id)}
              <li class="text-[10px] flex gap-2">
                <span class="text-muted/60 shrink-0">{ev.ts.slice(11, 19)}</span>
                <span class="text-muted/80 shrink-0">{ev.kind}</span>
                <span class="truncate">{ev.node_id ? `${ev.node_id}: ` : ''}{ev.detail}</span>
              </li>
            {/each}
          </ul>
        {/if}
      {:else}
        <p class="text-muted text-center mt-12">Select a run, or scope a goal to start one.</p>
      {/if}
    </section>
  </div>
</div>
