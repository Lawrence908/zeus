<script lang="ts">
  import { onDestroy, onMount } from 'svelte';
  import type { AppInstance } from '$lib/wm/tree';
  import { notify } from '$lib/notify/store';
  import {
    bulkDeleteMemories,
    deleteMemory,
    listMemories,
    listSources,
    memoryView,
    patchMemory,
    searchMemories,
    type MemoryEntry
  } from '$lib/api/memory';

  export let app: AppInstance;
  void app;

  let entries: MemoryEntry[] = [];
  let sources: { source: string; count: number }[] = [];

  // /memory/sources returns either bare strings or {source,count}. Normalize.
  function normaliseSources(raw: (string | { source: string; count: number })[]): { source: string; count: number }[] {
    return raw.map((s) => (typeof s === 'string' ? { source: s, count: 0 } : s));
  }
  let sourceFilter = '';
  let searchQ = '';
  let loading = false;
  let error = '';
  let lastFetched = '';
  let selected: MemoryEntry | null = null;
  let editing = false;
  let editMemory = '';
  let editCategory = '';
  let timer: ReturnType<typeof setInterval> | null = null;
  const chosen = new Set<string>();
  $: chosenCount = chosen.size;
  let _: number = 0; // bump to force re-render of chosen-derived UI
  void _;

  async function refreshSources() {
    try {
      const r = await listSources();
      sources = normaliseSources(r.sources ?? []);
    } catch {
      sources = [];
    }
  }

  async function refresh() {
    loading = true;
    try {
      if (searchQ.trim()) {
        const r = await searchMemories(searchQ.trim(), 50);
        entries = r.entries ?? r.results ?? [];
      } else {
        const r = await listMemories({ source: sourceFilter || undefined, limit: 100 });
        entries = r.entries ?? r.memories ?? [];
      }
      error = '';
      lastFetched = new Date().toLocaleTimeString();
    } catch (e) {
      error = String(e);
    } finally {
      loading = false;
    }
  }

  function pick(e: MemoryEntry) {
    selected = e;
    editing = false;
    const v = memoryView(e);
    editMemory = v.body;
    editCategory = v.category ?? '';
  }

  function toggleChoose(id: string) {
    if (chosen.has(id)) chosen.delete(id);
    else chosen.add(id);
    _ += 1;
  }

  async function saveEdit() {
    if (!selected) return;
    try {
      // Backend mostly cares about `text`; we send both names to be safe with
      // older handlers. Category lives in metadata in the canonical model.
      const next = await patchMemory(selected.id, {
        text: editMemory,
        memory: editMemory,
        metadata: { ...(selected.metadata ?? {}), category: editCategory || null }
      });
      selected = next;
      editing = false;
      notify({ title: 'Memory saved', kind: 'ok', ttlMs: 1500 });
      await refresh();
    } catch (e) {
      notify({ title: 'Save failed', body: String(e).slice(0, 160), kind: 'err' });
    }
  }

  async function dropOne(id: string) {
    if (!confirm('Delete this memory?')) return;
    try {
      await deleteMemory(id);
      if (selected?.id === id) selected = null;
      await refresh();
    } catch (e) {
      notify({ title: 'Delete failed', body: String(e).slice(0, 160), kind: 'err' });
    }
  }

  async function bulkDelete() {
    if (chosen.size === 0) return;
    if (!confirm(`Delete ${chosen.size} memories?`)) return;
    try {
      const r = await bulkDeleteMemories([...chosen]);
      notify({ title: `Deleted ${r.deleted}`, kind: 'ok', ttlMs: 1800 });
      chosen.clear();
      _ += 1;
      await refresh();
    } catch (e) {
      notify({ title: 'Bulk delete failed', body: String(e).slice(0, 160), kind: 'err' });
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
    refreshSources();
    timer = setInterval(refresh, 15_000);
  });

  onDestroy(() => {
    if (timer) clearInterval(timer);
  });
</script>

<div class="h-full w-full flex flex-col font-mono text-xs">
  {#if error}
    <div class="bg-err/20 border-b border-err/40 px-3 py-2 text-err">
      <strong>Memory error:</strong> {error}
    </div>
  {/if}

  <header class="px-3 py-2 border-b border-border/40 flex items-center gap-2">
    <input
      bind:value={searchQ}
      placeholder="Semantic search…"
      class="flex-1 bg-transparent border-b border-border/40 text-fg outline-none"
      on:keydown={(ev) => ev.key === 'Enter' && refresh()}
    />
    <select bind:value={sourceFilter} class="bg-surface text-fg p-1 rounded border border-border/40 text-[11px]" on:change={refresh}>
      <option value="">all sources</option>
      {#each sources as s (s.source)}
        <option value={s.source}>{s.source}{s.count ? ` (${s.count})` : ''}</option>
      {/each}
    </select>
    <button class="text-[10px] px-2 py-0.5 border border-border/60 rounded" on:click={refresh}>refresh</button>
    {#if chosenCount > 0}
      <button class="text-[10px] px-2 py-0.5 border border-err/60 text-err rounded" on:click={bulkDelete}>
        delete {chosenCount}
      </button>
    {/if}
    <span class="text-[10px] text-muted">{entries.length} {loading ? 'loading…' : ''} {lastFetched}</span>
  </header>

  <div class="flex-1 flex min-h-0">
    <ul class="w-1/2 overflow-y-auto border-r border-border/40">
      {#each entries as m (m.id)}
        {@const view = memoryView(m)}
        <li class="border-b border-border/20" class:bg-surface2={selected?.id === m.id}>
          <div class="flex items-start gap-2 px-3 py-2">
            <input
              type="checkbox"
              checked={chosen.has(m.id)}
              on:change={() => toggleChoose(m.id)}
              class="mt-0.5"
            />
            <button class="flex-1 text-left" on:click={() => pick(m)}>
              <p class="text-fg whitespace-pre-wrap leading-snug">{view.body.slice(0, 240)}{view.body.length > 240 ? '…' : ''}</p>
              <p class="text-muted text-[10px] mt-1">
                {view.source ?? '(no source)'}{view.category ? ` · ${view.category}` : ''}
                {view.confidence !== null ? ` · ${(view.confidence * 100).toFixed(0)}%` : ''}
              </p>
            </button>
            <button class="text-err text-[10px] opacity-50 hover:opacity-100" on:click={() => dropOne(m.id)}>×</button>
          </div>
        </li>
      {:else}
        <li class="px-3 py-6 text-muted text-center">{loading ? 'loading…' : 'no memories matched.'}</li>
      {/each}
    </ul>

    <section class="w-1/2 overflow-y-auto p-3">
      {#if selected}
        {@const view = memoryView(selected)}
        <header class="flex items-center justify-between mb-2">
          <h3 class="text-accent text-sm">Memory · {view.source ?? 'unknown'}</h3>
          <div class="flex gap-1">
            <button class="text-[10px] px-2 py-0.5 border border-accent text-accent rounded" on:click={() => (editing = !editing)}>
              {editing ? 'Cancel' : 'Edit'}
            </button>
            <button class="text-[10px] px-2 py-0.5 border border-err/60 text-err rounded" on:click={() => dropOne(selected!.id)}>Delete</button>
          </div>
        </header>

        {#if editing}
          <label class="text-[10px] text-muted block mb-1">memory</label>
          <textarea bind:value={editMemory} rows="6" class="w-full bg-transparent border border-border/40 rounded p-2 text-fg outline-none"></textarea>
          <label class="text-[10px] text-muted block mt-2 mb-1">category</label>
          <input bind:value={editCategory} class="w-full bg-transparent border-b border-border/40 text-fg outline-none" />
          <button class="mt-3 px-3 py-1 rounded bg-accent text-bg text-[11px]" on:click={saveEdit}>Save</button>
        {:else}
          <p class="text-fg whitespace-pre-wrap leading-relaxed">{view.body}</p>
          <p class="text-muted text-[10px] mt-3">id {selected.id}</p>
          {#if view.category}<p class="text-muted text-[10px]">category {view.category}</p>{/if}
          {#if view.confidence !== null}
            <p class="text-muted text-[10px]">confidence {(view.confidence * 100).toFixed(1)}%{view.containsPii ? ' · PII' : ''}</p>
          {/if}
          {#if view.source}<p class="text-muted text-[10px]">source {view.source}{view.sourceId ? ` (${view.sourceId})` : ''}</p>{/if}
          {#if view.validFrom || view.validUntil}
            <p class="text-muted text-[10px]">valid {fmtTs(view.validFrom)} — {fmtTs(view.validUntil) || 'open'}</p>
          {/if}
        {/if}
      {:else}
        <p class="text-muted text-center mt-12">Select a memory to view + edit.</p>
      {/if}
    </section>
  </div>
</div>
