<!-- src/lib/apps/Epstein.svelte — Epstein corpus workbench (PRIVATE BRANCH ONLY).

  Read-only workbench over zeus-core's /epstein/* proxy: cited search, one-entity
  dossiers, and connection maps. Co-occurrence is a signal about where to read,
  NEVER an accusation. This app lives only on the `epstein` branch. -->
<script lang="ts">
  import { onMount } from 'svelte';
  import type { AppInstance } from '$lib/wm/tree';
  import {
    epsteinStatus,
    epsteinSearch,
    epsteinDossier,
    epsteinConnections,
    type StatusResponse,
    type SearchResponse,
    type DossierResponse,
    type ConnectionsResponse,
    type EpsteinHit
  } from '$lib/api/epstein';

  export let app: AppInstance;
  void app;

  type Tab = 'search' | 'dossier' | 'connections';
  let tab: Tab = 'search';

  let status: StatusResponse | null = null;
  let statusLoading = true;

  // Search
  let searchQ = '';
  let searchDocType = '';
  let searchRes: SearchResponse | null = null;
  let searchLoading = false;

  // Dossier
  let dossierName = '';
  let dossierDepth = 1;
  let dossierRes: DossierResponse | null = null;
  let dossierLoading = false;

  // Connections
  let connNames = '';
  let connDepth = 2;
  let connRes: ConnectionsResponse | null = null;
  let connLoading = false;

  let error = '';

  onMount(async () => {
    try {
      status = await epsteinStatus();
    } catch (e) {
      status = { enabled: false, reachable: false, error: String(e) };
    } finally {
      statusLoading = false;
    }
  });

  async function runSearch() {
    if (!searchQ.trim()) return;
    searchLoading = true;
    error = '';
    try {
      searchRes = await epsteinSearch(searchQ.trim(), {
        doc_type: searchDocType.trim() || undefined,
        n_results: 15
      });
    } catch (e) {
      error = String(e);
    } finally {
      searchLoading = false;
    }
  }

  async function runDossier() {
    if (!dossierName.trim()) return;
    dossierLoading = true;
    error = '';
    try {
      dossierRes = await epsteinDossier(dossierName.trim(), { depth: dossierDepth });
    } catch (e) {
      error = String(e);
    } finally {
      dossierLoading = false;
    }
  }

  async function runConnections() {
    const names = connNames
      .split(',')
      .map((s) => s.trim())
      .filter(Boolean);
    if (names.length < 2) {
      error = 'Enter at least two comma-separated names.';
      return;
    }
    connLoading = true;
    error = '';
    try {
      connRes = await epsteinConnections(names, { depth: connDepth });
    } catch (e) {
      error = String(e);
    } finally {
      connLoading = false;
    }
  }

  const TABS: { id: Tab; label: string }[] = [
    { id: 'search', label: 'Search' },
    { id: 'dossier', label: 'Dossier' },
    { id: 'connections', label: 'Connections' }
  ];
</script>

<div class="h-full w-full flex flex-col font-mono text-xs bg-bg text-fg">
  <!-- Status banner -->
  {#if statusLoading}
    <div class="px-3 py-2 text-muted border-b border-border/40">Probing corpus API…</div>
  {:else if !status?.enabled}
    <div class="bg-warn/15 border-b border-warn/40 px-3 py-2 text-warn">
      Epstein capability disabled (set <code>ZEUS_EPSTEIN_ENABLED=1</code> and corpus creds).
    </div>
  {:else if !status?.reachable}
    <div class="bg-err/15 border-b border-err/40 px-3 py-2 text-err">
      Corpus API unreachable. {status?.error ?? ''}
    </div>
  {:else}
    <div class="bg-surface border-b border-border/40 px-3 py-1.5 flex items-center gap-3">
      <span class="text-ok">● online</span>
      <span class="text-muted">graph: {status?.graph_available ? 'available' : 'down'}</span>
      {#if status?.doc_types}
        <span class="text-muted truncate">doc_types: {Object.keys(status.doc_types).length}</span>
      {/if}
    </div>
  {/if}

  <!-- Sensitivity notice -->
  <div class="px-3 py-1.5 text-[10px] text-muted border-b border-border/20 leading-snug">
    Sensitive legal corpus (victims + unproven allegations). Co-occurrence is a signal about
    where to read, never an accusation. Every claim is cited by document_id.
  </div>

  <!-- Tabs -->
  <div class="flex border-b border-border/40 shrink-0">
    {#each TABS as t}
      <button
        class="px-4 py-2 border-r border-border/30 {tab === t.id
          ? 'bg-surface2 text-accent'
          : 'text-muted hover:bg-surface/60'}"
        on:click={() => (tab = t.id)}
      >
        {t.label}
      </button>
    {/each}
  </div>

  {#if error}
    <div class="bg-err/15 text-err px-3 py-1.5 text-[11px]">{error}</div>
  {/if}

  <div class="flex-1 min-h-0 overflow-y-auto">
    <!-- SEARCH -->
    {#if tab === 'search'}
      <div class="p-3 flex flex-col gap-2">
        <div class="flex gap-2">
          <input
            class="flex-1 bg-surface text-fg p-1.5 rounded border border-border/40"
            placeholder="Search the corpus…"
            bind:value={searchQ}
            on:keydown={(e) => e.key === 'Enter' && runSearch()}
          />
          <input
            class="w-32 bg-surface text-fg p-1.5 rounded border border-border/40"
            placeholder="doc_type (opt)"
            bind:value={searchDocType}
          />
          <button
            class="px-3 rounded border border-accent/50 text-accent hover:bg-accent/10"
            on:click={runSearch}
            disabled={searchLoading}
          >
            {searchLoading ? '…' : 'Search'}
          </button>
        </div>

        {#if searchRes && !searchRes.reachable}
          <div class="text-err text-[11px]">{searchRes.error}</div>
        {:else if searchRes?.results}
          <div class="text-muted text-[10px]">{searchRes.results.length} hits</div>
          {#each searchRes.results as h}
            <div class="border border-border/30 rounded p-2 bg-surface/40">
              <div class="flex justify-between text-[10px] text-muted mb-1">
                <span class="text-accent2 truncate">{h.citation}</span>
                <span>score {h.score.toFixed(3)}</span>
              </div>
              <div class="leading-snug whitespace-pre-wrap">{h.text}</div>
            </div>
          {/each}
        {/if}
      </div>
    {/if}

    <!-- DOSSIER -->
    {#if tab === 'dossier'}
      <div class="p-3 flex flex-col gap-2">
        <div class="flex gap-2">
          <input
            class="flex-1 bg-surface text-fg p-1.5 rounded border border-border/40"
            placeholder="Entity name (e.g. Jeffrey Epstein)"
            bind:value={dossierName}
            on:keydown={(e) => e.key === 'Enter' && runDossier()}
          />
          <select
            class="bg-surface text-fg p-1.5 rounded border border-border/40"
            bind:value={dossierDepth}
          >
            <option value={1}>depth 1</option>
            <option value={2}>depth 2</option>
            <option value={3}>depth 3</option>
          </select>
          <button
            class="px-3 rounded border border-accent/50 text-accent hover:bg-accent/10"
            on:click={runDossier}
            disabled={dossierLoading}
          >
            {dossierLoading ? '…' : 'Build'}
          </button>
        </div>

        {#if dossierRes && !dossierRes.reachable}
          <div class="text-err text-[11px]">{dossierRes.error}</div>
        {:else if dossierRes}
          <div class="flex gap-3 text-[10px] text-muted">
            <span>confidence: <span class="text-fg">{dossierRes.confidence}</span></span>
            <span>access: {dossierRes.graph_available ? 'graph + search' : 'search-only'}</span>
            <span>{dossierRes.evidence?.length ?? 0} excerpts</span>
          </div>

          {#if dossierRes.connections?.length}
            <div>
              <div class="text-muted text-[10px] mb-1">Connections (co-occurrence only)</div>
              <div class="flex flex-wrap gap-1">
                {#each dossierRes.connections as c}
                  <span class="px-1.5 py-0.5 rounded bg-surface2 border border-border/30">{c}</span>
                {/each}
              </div>
            </div>
          {/if}

          {#if dossierRes.timeline?.length}
            <div>
              <div class="text-muted text-[10px] mb-1">Timeline (graph-derived)</div>
              {#each dossierRes.timeline as e}
                <div class="border-l-2 border-accent2/40 pl-2 mb-1">
                  <span class="text-accent2">{e.date || 'undated'}</span>
                  <span class="text-fg">{e.description}</span>
                </div>
              {/each}
            </div>
          {/if}

          {#if dossierRes.evidence?.length}
            <div class="text-muted text-[10px] mb-1">Cited excerpts</div>
            {#each dossierRes.evidence as h}
              <div class="border border-border/30 rounded p-2 bg-surface/40">
                <div class="text-[10px] text-accent2 mb-1 truncate">{h.citation}</div>
                <div class="leading-snug whitespace-pre-wrap">{h.text}</div>
              </div>
            {/each}
          {/if}

          {#if dossierRes.gaps?.length}
            <div class="text-warn text-[10px]">
              {#each dossierRes.gaps as g}<div>⚠ {g}</div>{/each}
            </div>
          {/if}
        {/if}
      </div>
    {/if}

    <!-- CONNECTIONS -->
    {#if tab === 'connections'}
      <div class="p-3 flex flex-col gap-2">
        <div class="flex gap-2">
          <input
            class="flex-1 bg-surface text-fg p-1.5 rounded border border-border/40"
            placeholder="Comma-separated names (min 2)"
            bind:value={connNames}
            on:keydown={(e) => e.key === 'Enter' && runConnections()}
          />
          <select
            class="bg-surface text-fg p-1.5 rounded border border-border/40"
            bind:value={connDepth}
          >
            <option value={1}>depth 1</option>
            <option value={2}>depth 2</option>
            <option value={3}>depth 3</option>
          </select>
          <button
            class="px-3 rounded border border-accent/50 text-accent hover:bg-accent/10"
            on:click={runConnections}
            disabled={connLoading}
          >
            {connLoading ? '…' : 'Map'}
          </button>
        </div>

        {#if connRes && !connRes.reachable}
          <div class="text-err text-[11px]">{connRes.error}</div>
        {:else if connRes?.pairs}
          <div class="text-[10px] text-muted">
            confidence: {connRes.confidence} · {connRes.graph_available ? 'graph + search' : 'search-only'}
          </div>
          {#each connRes.pairs as p}
            <div class="border border-border/30 rounded p-2 bg-surface/40">
              <div class="flex justify-between items-center mb-1">
                <span class="text-fg">{p.a} ↔ {p.b}</span>
                <span class="text-[10px] {p.connected ? 'text-ok' : 'text-muted'}">
                  {p.connected ? 'connected' : 'no graph path'}
                </span>
              </div>
              {#if p.intermediaries?.length}
                <div class="text-[10px] text-muted mb-1">
                  via: {p.intermediaries.join(', ')}
                </div>
              {/if}
              {#each p.evidence.slice(0, 3) as h}
                <div class="text-[10px] border-l-2 border-border/40 pl-2 mb-1">
                  <span class="text-accent2">{h.citation}</span>
                  <span class="text-fg">{h.text.slice(0, 200)}</span>
                </div>
              {/each}
            </div>
          {/each}
        {/if}
      </div>
    {/if}
  </div>
</div>
