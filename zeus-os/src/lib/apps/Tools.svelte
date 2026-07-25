<script lang="ts">
  import { onDestroy, onMount } from 'svelte';
  import type { AppInstance } from '$lib/wm/tree';
  import {
    invokeTool,
    listInvocations,
    listTools,
    type ToolDirEntry,
    type ToolInvocation,
    type ToolInvokeResult
  } from '$lib/api/tools';

  export let app: AppInstance;
  void app;

  let tools: ToolDirEntry[] = [];
  let toolsEnabled: boolean | undefined;
  let invocations: ToolInvocation[] = [];
  let filter = '';
  let toolFilter = '';
  let error = '';
  let loading = true;
  let lastFetched = '';
  let timer: ReturnType<typeof setInterval> | null = null;
  let selected: ToolDirEntry | null = null;

  async function refresh() {
    try {
      loading = true;
      const [t, inv] = await Promise.all([
        listTools(),
        listInvocations({ limit: 100, tool: toolFilter || undefined })
      ]);
      const anyT = t as { tools?: unknown };
      const raw: ToolDirEntry[] = Array.isArray(anyT.tools)
        ? (anyT.tools as ToolDirEntry[])
        : Array.isArray(t)
          ? (t as unknown as ToolDirEntry[])
          : [];
      // Backend returns one row per (name, source). Olympian tools are
      // registered in both the chat-path AND the MCP server, so 9 of them
      // appear twice. Dedupe by name; merge sources into a list so the row
      // can show a "chat + mcp" badge.
      const merged = new Map<string, ToolDirEntry>();
      for (const r of raw) {
        const k = r.name;
        const existing = merged.get(k);
        if (!existing) {
          merged.set(k, { ...r, sources: r.source ? [r.source] : [] });
        } else {
          if (r.source && !(existing.sources ?? []).includes(r.source)) {
            existing.sources = [...(existing.sources ?? []), r.source];
          }
        }
      }
      tools = [...merged.values()];
      // Loop state lives under `chat.enabled` (gates POST /admin/tools/invoke).
      toolsEnabled = t.chat?.enabled;
      invocations = inv.invocations ?? [];
      error = '';
      lastFetched = new Date().toLocaleTimeString();
      // Debug breadcrumb so we can see what the SPA actually received.
      // Open devtools Console; this should print "[Zeus OS Tools] got 26 tools …"
      // each refresh. If you see it but no list renders, the bug is in the
      // template, not the fetch.
      // eslint-disable-next-line no-console
      console.log('[Zeus OS Tools] got', tools.length, 'tools, first 3:',
        tools.slice(0, 3).map((x) => x?.name));
    } catch (e) {
      error = String(e);
      // eslint-disable-next-line no-console
      console.error('[Zeus OS Tools] refresh error', e);
    } finally {
      loading = false;
    }
  }

  onMount(() => {
    refresh();
    timer = setInterval(refresh, 4000);
  });

  onDestroy(() => {
    if (timer) clearInterval(timer);
  });

  function applyFilter(arr: ToolDirEntry[], q: string): ToolDirEntry[] {
    const needle = q.toLowerCase().trim();
    if (!needle) return arr;
    return arr.filter(
      (t) =>
        (t.name ?? '').toLowerCase().includes(needle) ||
        (t.description ?? '').toLowerCase().includes(needle)
    );
  }

  $: filteredTools = applyFilter(tools, filter);

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

  // ── try-tool form ──
  let tryOpen = false;
  let tryArgs = '{}';
  let tryBusy = false;
  let tryResult: ToolInvokeResult | null = null;
  let tryError = '';

  // Skeleton args from the JSON schema so the operator doesn't start from {}.
  function schemaSkeleton(t: ToolDirEntry): string {
    const props = (t.parameters as { properties?: Record<string, { type?: string; default?: unknown }> } | undefined)
      ?.properties;
    if (!props) return '{}';
    const out: Record<string, unknown> = {};
    for (const [k, v] of Object.entries(props)) {
      if (v.default !== undefined) out[k] = v.default;
      else if (v.type === 'number' || v.type === 'integer') out[k] = 0;
      else if (v.type === 'boolean') out[k] = false;
      else if (v.type === 'array') out[k] = [];
      else if (v.type === 'object') out[k] = {};
      else out[k] = '';
    }
    return JSON.stringify(out, null, 2);
  }

  function openTry() {
    if (!selected) return;
    tryOpen = !tryOpen;
    tryResult = null;
    tryError = '';
    if (tryOpen) tryArgs = schemaSkeleton(selected);
  }

  async function runTry() {
    if (!selected || tryBusy) return;
    tryError = '';
    tryResult = null;
    let parsed: Record<string, unknown>;
    try {
      parsed = JSON.parse(tryArgs || '{}');
    } catch (e) {
      tryError = `invalid JSON: ${e instanceof Error ? e.message : e}`;
      return;
    }
    tryBusy = true;
    try {
      tryResult = await invokeTool(selected.name, parsed);
      await refresh();
    } catch (e) {
      tryError = String(e).slice(0, 300);
    } finally {
      tryBusy = false;
    }
  }

  // Reset the try form when a different tool is selected.
  $: if (selected) {
    tryOpen = false;
    tryResult = null;
    tryError = '';
  }
</script>

<div class="h-full w-full flex flex-col font-mono text-xs">
  {#if error}
    <div class="bg-err/20 border-b border-err/40 px-3 py-2 text-err">
      <strong>Error fetching tools:</strong> {error}
    </div>
  {/if}

  <div class="flex-1 flex min-h-0">
  <!-- Tools list -->
  <aside class="w-72 border-r border-border/40 flex flex-col">
    <header class="px-3 py-2 border-b border-border/40 flex items-center justify-between">
      <div>
        <h3 class="text-accent text-sm">Tools</h3>
        <p class="text-muted text-[10px]">
          {loading && tools.length === 0 ? 'loading…' : `${tools.length} registered`}{toolsEnabled === false ? ' · loop disabled' : ''}
          {#if lastFetched} · {lastFetched}{/if}
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
            <div class="flex gap-1 mt-1 text-[10px] text-muted flex-wrap">
              {#if t.sources && t.sources.length}
                <span class="text-accent2" title="Registration surfaces">{t.sources.join('+')}</span>
              {/if}
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
          <div class="flex gap-2">
            {#if (selected.sources ?? []).includes('chat')}
              <button
                class="text-[10px] px-2 py-0.5 border rounded"
                class:border-accent={tryOpen}
                class:text-accent={tryOpen}
                class:border-border={!tryOpen}
                class:text-muted={!tryOpen}
                on:click={openTry}
              >try</button>
            {/if}
            <button
              class="text-muted hover:text-fg text-[10px]"
              on:click={() => {
                toolFilter = toolFilter === selected!.name ? '' : selected!.name;
                refresh();
              }}
            >
              {toolFilter === selected.name ? 'Show all' : 'Filter feed'}
            </button>
          </div>
        </header>
        <p class="text-muted leading-relaxed">{selected.description}</p>
        {#if selected.parameters}
          <details class="mt-2">
            <summary class="text-muted cursor-pointer">parameters schema</summary>
            <pre class="mt-1 text-[10px] text-fg whitespace-pre-wrap overflow-x-auto">{JSON.stringify(selected.parameters, null, 2)}</pre>
          </details>
        {/if}
        {#if tryOpen}
          <div class="mt-2 border border-border/40 rounded p-2 space-y-2">
            <textarea
              bind:value={tryArgs}
              rows="4"
              spellcheck="false"
              class="w-full bg-surface rounded border border-border/40 p-2 text-[11px] text-fg outline-none resize-y font-mono"
            ></textarea>
            <div class="flex items-center gap-2">
              <button
                class="text-[10px] px-3 py-1 rounded bg-accent text-bg disabled:opacity-40"
                disabled={tryBusy || toolsEnabled === false}
                title={toolsEnabled === false ? 'Chat-path tools are disabled (ZEUS_TOOLS_ENABLED=0)' : 'Run this tool'}
                on:click={runTry}
              >{tryBusy ? 'running…' : 'run'}</button>
              {#if toolsEnabled === false}
                <span class="text-warn text-[10px]">loop disabled · set ZEUS_TOOLS_ENABLED=1</span>
              {/if}
              {#if tryError}<span class="text-err text-[10px]">{tryError}</span>{/if}
              {#if tryResult}
                <span class="text-[10px]" class:text-ok={!tryResult.is_error} class:text-err={tryResult.is_error}>
                  {tryResult.is_error ? 'error' : 'ok'} · {tryResult.duration_ms}ms
                </span>
              {/if}
            </div>
            {#if tryResult}
              <pre class="text-[10px] whitespace-pre-wrap break-words max-h-48 overflow-y-auto p-2 rounded"
                class:text-fg={!tryResult.is_error}
                class:text-err={tryResult.is_error}
                style="background: rgb(var(--surface-2) / 0.4);">{tryResult.content}</pre>
            {/if}
          </div>
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
</div>
