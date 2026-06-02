<script lang="ts">
  import { onDestroy, onMount } from 'svelte';
  import type { AppInstance } from '$lib/wm/tree';
  import { listInvocations, listTools, type ToolDirEntry, type ToolInvocation } from '$lib/api/tools';

  export let app: AppInstance;
  void app;

  let tools: ToolDirEntry[] = [];
  let toolsEnabled: boolean | undefined;
  let invocations: ToolInvocation[] = [];
  let filter = '';
  let toolFilter = '';
  let error = '';
  let timer: ReturnType<typeof setInterval> | null = null;
  let selected: ToolDirEntry | null = null;

  async function refresh() {
    try {
      const [t, inv] = await Promise.all([
        listTools(),
        listInvocations({ limit: 100, tool: toolFilter || undefined })
      ]);
      tools = t.tools ?? [];
      toolsEnabled = (t as { tools_enabled?: boolean }).tools_enabled;
      invocations = inv.invocations ?? [];
      error = '';
    } catch (e) {
      error = String(e);
    }
  }

  onMount(() => {
    refresh();
    timer = setInterval(refresh, 4000);
  });

  onDestroy(() => {
    if (timer) clearInterval(timer);
  });

  $: filteredTools = tools.filter((t) => {
    const q = filter.toLowerCase();
    if (!q) return true;
    return t.name.toLowerCase().includes(q) || t.description.toLowerCase().includes(q);
  });

  function fmtTime(ts: string): string {
    try {
      return new Date(ts).toLocaleTimeString([], {
        hour: '2-digit',
        minute: '2-digit',
        second: '2-digit'
      });
    } catch {
      return ts;
    }
  }

  function fmtArgs(args?: Record<string, unknown>): string {
    if (!args || Object.keys(args).length === 0) return '';
    try {
      return JSON.stringify(args);
    } catch {
      return '';
    }
  }
</script>

<div class="h-full w-full flex font-mono text-xs">
  <!-- Tools list -->
  <aside class="w-72 border-r border-border/40 flex flex-col">
    <header class="px-3 py-2 border-b border-border/40 flex items-center justify-between">
      <div>
        <h3 class="text-accent text-sm">Tools</h3>
        <p class="text-muted text-[10px]">
          {tools.length} registered{toolsEnabled === false ? ' · loop disabled' : ''}
        </p>
      </div>
      <input
        bind:value={filter}
        placeholder="filter…"
        class="bg-transparent border-b border-border/40 text-fg outline-none text-[11px] w-24"
      />
    </header>
    <ul class="flex-1 overflow-y-auto">
      {#each filteredTools as t (t.name)}
        <li>
          <button
            class="w-full text-left px-3 py-2 hover:bg-surface2/60"
            class:bg-surface2={selected?.name === t.name}
            on:click={() => (selected = t)}
          >
            <div class="text-fg">{t.name}</div>
            <div class="text-muted text-[10px] truncate">{t.description.slice(0, 60)}…</div>
            <div class="flex gap-1 mt-1 text-[10px] text-muted">
              {#if t.cacheable}<span class="text-ok">cache</span>{/if}
              {#if t.aegis_policy}<span title="Aegis policy">{t.aegis_policy}</span>{/if}
              {#if t.timeout_seconds}<span>{t.timeout_seconds}s</span>{/if}
            </div>
          </button>
        </li>
      {/each}
    </ul>
  </aside>

  <!-- Right pane: tool detail + invocation feed -->
  <section class="flex-1 flex flex-col min-w-0">
    {#if selected}
      <div class="p-3 border-b border-border/40">
        <header class="flex items-center justify-between mb-1">
          <h3 class="text-accent text-sm">{selected.name}</h3>
          <button
            class="text-muted hover:text-fg text-[10px]"
            on:click={() => {
              toolFilter = toolFilter === selected!.name ? '' : selected!.name;
              refresh();
            }}
          >
            {toolFilter === selected.name ? 'Show all' : 'Filter feed'}
          </button>
        </header>
        <p class="text-muted leading-relaxed">{selected.description}</p>
        {#if selected.parameters}
          <details class="mt-2">
            <summary class="text-muted cursor-pointer">parameters schema</summary>
            <pre class="mt-1 text-[10px] text-fg whitespace-pre-wrap overflow-x-auto">{JSON.stringify(selected.parameters, null, 2)}</pre>
          </details>
        {/if}
      </div>
    {/if}

    <div class="px-3 py-2 border-b border-border/40 flex items-center justify-between">
      <h3 class="text-accent text-sm">Recent invocations</h3>
      <span class="text-muted text-[10px]">
        {invocations.length} shown
        {#if toolFilter} · filter: <span class="text-fg">{toolFilter}</span>{/if}
      </span>
    </div>

    {#if error}
      <p class="text-err px-3 py-2">{error}</p>
    {/if}

    <ul class="flex-1 overflow-y-auto">
      {#each invocations as inv}
        <li class="px-3 py-2 border-b border-border/20 hover:bg-surface2/40">
          <header class="flex items-center justify-between text-[10px] text-muted">
            <span>
              <span class="text-fg">{inv.tool}</span>
              {#if inv.cache_hit}<span class="text-ok ml-2">cache</span>{/if}
              {#if inv.aegis_rejected}<span class="text-err ml-2">aegis</span>{/if}
              {#if inv.is_error}<span class="text-err ml-2">err</span>{/if}
              {#if inv.source}<span class="ml-2">{inv.source}</span>{/if}
            </span>
            <span>{fmtTime(inv.ts)}{inv.duration_ms ? ` · ${inv.duration_ms}ms` : ''}</span>
          </header>
          {#if fmtArgs(inv.args)}
            <pre class="mt-1 text-[10px] text-muted whitespace-pre-wrap break-words">{fmtArgs(inv.args)}</pre>
          {/if}
          {#if inv.content}
            <pre class="mt-1 text-[10px] text-fg/80 whitespace-pre-wrap break-words">{inv.content.slice(0, 240)}{inv.content.length > 240 ? '…' : ''}</pre>
          {/if}
        </li>
      {:else}
        <li class="px-3 py-6 text-muted text-center">No invocations recorded yet. Ask Zeus a tool-worthy question to populate this feed.</li>
      {/each}
    </ul>
  </section>
</div>
