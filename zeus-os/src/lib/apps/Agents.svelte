<script lang="ts">
  import { onDestroy, onMount } from 'svelte';
  import type { AppInstance } from '$lib/wm/tree';
  import { getStatus, listTasks, type AgentInfo, type AgentTask } from '$lib/api/orchestration';

  export let app: AppInstance;
  void app;

  let agents: AgentInfo[] = [];
  let tasks: AgentTask[] = [];
  let busMetrics: Record<string, unknown> | undefined;
  let error = '';
  let lastFetched = '';
  let loading = false;
  let timer: ReturnType<typeof setInterval> | null = null;
  let selected: AgentInfo | null = null;

  async function refresh() {
    loading = true;
    try {
      const [s, t] = await Promise.all([getStatus(), listTasks()]);
      agents = s.agents ?? [];
      busMetrics = s.metrics;
      tasks = Array.isArray(t) ? t : (t.tasks ?? []);
      error = '';
      lastFetched = new Date().toLocaleTimeString();
    } catch (e) {
      error = String(e);
    } finally {
      loading = false;
    }
  }

  function fmtUptime(s?: number): string {
    if (!s || s <= 0) return '';
    if (s < 60) return `${Math.round(s)}s`;
    if (s < 3600) return `${(s / 60).toFixed(1)}m`;
    if (s < 86400) return `${(s / 3600).toFixed(1)}h`;
    return `${(s / 86400).toFixed(1)}d`;
  }

  function fmtModels(m: AgentInfo['models']): string {
    if (!m) return '';
    if (Array.isArray(m)) return m.join(', ');
    // dict shape: {dev: ..., prod: ...}
    return Object.entries(m)
      .map(([k, v]) => `${k}=${v}`)
      .join(' · ');
  }

  onMount(() => {
    refresh();
    timer = setInterval(refresh, 8_000);
  });

  onDestroy(() => {
    if (timer) clearInterval(timer);
  });
</script>

<div class="h-full w-full flex flex-col font-mono text-xs">
  {#if error}
    <div class="bg-err/20 border-b border-err/40 px-3 py-2 text-err">
      <strong>Agents error:</strong> {error}
    </div>
  {/if}

  <header class="px-3 py-2 border-b border-border/40 flex items-center justify-between">
    <div>
      <h3 class="text-accent text-sm">Agents</h3>
      <p class="text-muted text-[10px]">
        {agents.length} loaded · {tasks.length} tasks · {loading ? 'loading…' : ''} {lastFetched}
      </p>
    </div>
    <button class="text-[10px] px-2 py-0.5 border border-border/60 rounded" on:click={refresh}>refresh</button>
  </header>

  <div class="flex-1 flex min-h-0">
    <ul class="w-1/2 overflow-y-auto border-r border-border/40">
      {#each agents as a (a.name)}
        <li class="border-b border-border/20" class:bg-surface2={selected?.name === a.name}>
          <button class="w-full text-left px-3 py-2 hover:bg-surface2/60" on:click={() => (selected = a)}>
            <div class="flex items-center justify-between">
              <span class="text-fg">{a.name}</span>
              <span class="text-[10px] {a.status === 'running' || a.status === 'idle' ? 'text-ok' : 'text-muted'}">
                {a.status ?? '?'}
              </span>
            </div>
            {#if a.description}<p class="text-muted text-[10px] truncate">{a.description}</p>{/if}
            <p class="text-muted text-[10px] mt-0.5">
              {a.model ?? fmtModels(a.models)}{a.uptime_seconds ? ` · up ${fmtUptime(a.uptime_seconds)}` : ''}
            </p>
          </button>
        </li>
      {:else}
        <li class="px-3 py-6 text-muted text-center">No agents loaded.</li>
      {/each}
    </ul>

    <section class="w-1/2 overflow-y-auto p-3">
      {#if selected}
        <header class="mb-2">
          <h3 class="text-accent text-sm">{selected.name}</h3>
          <p class="text-muted text-[10px]">{selected.status ?? 'unknown'}</p>
        </header>
        {#if selected.description}<p class="text-fg/80 mb-2">{selected.description}</p>{/if}
        {#if selected.tools && selected.tools.length}
          <p class="text-[10px] text-muted">tools</p>
          <ul class="text-fg/80 text-[11px] mb-2">
            {#each selected.tools as t}<li>· {t}</li>{/each}
          </ul>
        {/if}
        {#if selected.model || selected.models}
          <p class="text-[10px] text-muted">models</p>
          <p class="text-fg/80 text-[11px] mb-2">{selected.model || fmtModels(selected.models)}</p>
        {/if}
        {#if selected.safety_policy}
          <p class="text-[10px] text-muted">safety policy</p>
          <p class="text-fg/80 text-[11px] mb-2">{selected.safety_policy}</p>
        {/if}
        {#if selected.error}
          <p class="text-err text-[11px] mb-2">error: {selected.error}</p>
        {/if}
      {:else}
        <p class="text-muted text-center mb-4">Select an agent to inspect its definition.</p>
      {/if}

      <header class="mt-4 mb-1">
        <h3 class="text-accent text-sm">Recent tasks</h3>
      </header>
      <ul class="space-y-1">
        {#each tasks.slice(0, 15) as t (t.task_id)}
          <li class="border-b border-border/20 py-1">
            <div class="flex items-center justify-between text-[10px] text-muted">
              <span>{t.agent} · {t.action}</span>
              <span class:text-ok={t.status === 'done'} class:text-err={t.status === 'error'} class="text-fg">{t.status}</span>
            </div>
            {#if t.error}<p class="text-err text-[10px]">{t.error}</p>{/if}
          </li>
        {:else}
          <li class="text-muted text-[10px]">No tasks in the bus.</li>
        {/each}
      </ul>

      {#if busMetrics}
        <details class="mt-4">
          <summary class="text-muted text-[10px] cursor-pointer">bus metrics</summary>
          <pre class="mt-1 text-[10px] text-fg/80 whitespace-pre-wrap">{JSON.stringify(busMetrics, null, 2)}</pre>
        </details>
      {/if}
    </section>
  </div>
</div>
