<script lang="ts">
  import { onDestroy, onMount } from 'svelte';
  import type { AppInstance } from '$lib/wm/tree';
  import {
    knowledgeFacets,
    listKnowledge,
    searchKnowledge,
    type KnowledgeEntry,
    type KnowledgeFacetValue
  } from '$lib/api/knowledge';

  export let app: AppInstance;
  void app;

  let entries: KnowledgeEntry[] = [];
  // Facets come in as a flat object: { total: <n>, source: [...], doc_type: [...] }.
  // Strip `total` here so the rest of the object is purely facet name → values.
  let facets: Record<string, KnowledgeFacetValue[]> = {};
  let totalPoints = 0;
  let searchQ = '';
  let sourceFilter = '';
  let docTypeFilter = '';
  let loading = false;
  let error = '';
  let lastFetched = '';
  let selected: KnowledgeEntry | null = null;
  let timer: ReturnType<typeof setInterval> | null = null;

  async function refreshFacets() {
    try {
      const r = await knowledgeFacets();
      const next: Record<string, KnowledgeFacetValue[]> = {};
      let total = 0;
      for (const [k, v] of Object.entries(r)) {
        if (k === 'total' && typeof v === 'number') {
          total = v;
        } else if (Array.isArray(v)) {
          next[k] = v as KnowledgeFacetValue[];
        }
      }
      facets = next;
      totalPoints = total;
    } catch {
      facets = {};
    }
  }

  async function refresh() {
    loading = true;
    try {
      if (searchQ.trim()) {
        const r = await searchKnowledge(searchQ.trim(), 50);
        entries = r.entries ?? r.results ?? [];
      } else {
        const r = await listKnowledge({
          source: sourceFilter || undefined,
          doc_type: docTypeFilter || undefined,
          limit: 100
        });
        entries = r.entries ?? r.items ?? [];
      }
      error = '';
      lastFetched = new Date().toLocaleTimeString();
    } catch (e) {
      error = String(e);
    } finally {
      loading = false;
    }
  }

  function fmtTs(ts?: string | null): string {
    if (!ts) return '';
    try {
      return new Date(ts).toLocaleString([], { dateStyle: 'short', timeStyle: 'short' });
    } catch {
      return ts;
    }
  }

  onMount(() => {
    refresh();
    refreshFacets();
    timer = setInterval(() => {
      refresh();
      refreshFacets();
    }, 30_000);
  });

  onDestroy(() => {
    if (timer) clearInterval(timer);
  });
</script>

<div class="h-full w-full flex flex-col font-mono text-xs">
  {#if error}
    <div class="bg-err/20 border-b border-err/40 px-3 py-2 text-err">
      <strong>Knowledge error:</strong> {error}
    </div>
  {/if}

  <header class="px-3 py-2 border-b border-border/40 flex items-center gap-2 flex-wrap">
    <input
      bind:value={searchQ}
      placeholder="Hybrid search (Enter)…"
      class="flex-1 min-w-[140px] bg-transparent border-b border-border/40 text-fg outline-none"
      on:keydown={(ev) => ev.key === 'Enter' && refresh()}
    />
    <select bind:value={sourceFilter} class="bg-surface text-fg p-1 rounded border border-border/40 text-[11px]" on:change={refresh}>
      <option value="">all sources</option>
      {#each facets.source ?? [] as f (f.value)}
        <option value={f.value}>{f.value} ({f.count})</option>
      {/each}
    </select>
    <select bind:value={docTypeFilter} class="bg-surface text-fg p-1 rounded border border-border/40 text-[11px]" on:change={refresh}>
      <option value="">all types</option>
      {#each facets.doc_type ?? [] as f (f.value)}
        <option value={f.value}>{f.value} ({f.count})</option>
      {/each}
    </select>
    <button class="text-[10px] px-2 py-0.5 border border-border/60 rounded" on:click={refresh}>refresh</button>
    <span class="text-[10px] text-muted">{entries.length} / {totalPoints} total {loading ? 'loading…' : ''} {lastFetched}</span>
  </header>

  <div class="flex-1 flex min-h-0">
    <ul class="w-1/2 overflow-y-auto border-r border-border/40">
      {#each entries as e (e.id)}
        <li class="border-b border-border/20" class:bg-surface2={selected?.id === e.id}>
          <button class="w-full text-left px-3 py-2 hover:bg-surface2/60" on:click={() => (selected = e)}>
            <p class="text-fg leading-snug truncate">{e.title || e.text.slice(0, 80)}</p>
            <p class="text-muted text-[10px] mt-1">
              {e.source}{e.doc_type ? ` · ${e.doc_type}` : ''}{e.created_at ? ` · ${fmtTs(e.created_at)}` : ''}
            </p>
          </button>
        </li>
      {:else}
        <li class="px-3 py-6 text-muted text-center">{loading ? 'loading…' : 'no knowledge matched.'}</li>
      {/each}
    </ul>

    <section class="w-1/2 overflow-y-auto p-3">
      {#if selected}
        <header class="mb-2">
          <h3 class="text-accent text-sm">{selected.title || '(untitled)'}</h3>
          <p class="text-muted text-[10px] mt-1">{selected.source}{selected.doc_type ? ` · ${selected.doc_type}` : ''}</p>
          {#if selected.url}
            <a href={selected.url} target="_blank" rel="noopener" class="text-accent text-[10px] underline">{selected.url}</a>
          {/if}
        </header>
        <pre class="text-fg whitespace-pre-wrap leading-relaxed">{selected.text}</pre>
        {#if selected.tags && selected.tags.length}
          <p class="text-muted text-[10px] mt-3">
            tags: {selected.tags.join(', ')}
          </p>
        {/if}
        <p class="text-muted text-[10px] mt-2">id {selected.id}</p>
      {:else}
        <p class="text-muted text-center mt-12">Select a knowledge entry to inspect.</p>
      {/if}
    </section>
  </div>
</div>
