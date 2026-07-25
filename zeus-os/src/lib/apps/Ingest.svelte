<script lang="ts">
  import { onDestroy, onMount } from 'svelte';
  import type { AppInstance } from '$lib/wm/tree';
  import { notify } from '$lib/notify/store';
  import { getIngestStats, triggerIngest, type IngestStats } from '$lib/api/ingest';

  export let app: AppInstance;
  void app;

  let stats: IngestStats | null = null;
  let error = '';
  let lastFetched = '';
  let triggering = false;
  let timer: ReturnType<typeof setInterval> | null = null;

  // Source names mirror zeus/ingest/config.yaml. Add to the table when new
  // sources land in ingest config.
  const SOURCES = [
    { id: 'context_pack', label: 'Context pack', kind: 'profile' },
    { id: 'gcal', label: 'Google Calendar', kind: 'profile' },
    { id: 'obsidian', label: 'Obsidian vault', kind: 'knowledge' },
    { id: 'chatgpt', label: 'ChatGPT export', kind: 'knowledge' },
    { id: 'newsletter', label: 'Newsletters', kind: 'knowledge' },
    { id: 'bookmarks', label: 'Bookmarks', kind: 'knowledge' },
    { id: 'email', label: 'Email (IMAP)', kind: 'knowledge' },
    { id: 'git', label: 'Git commits', kind: 'knowledge' },
    { id: 'kiwix', label: 'Kiwix ZIM', kind: 'reference' }
  ] as const;

  async function refresh() {
    try {
      stats = await getIngestStats();
      error = '';
      lastFetched = new Date().toLocaleTimeString();
    } catch (e) {
      error = String(e);
    }
  }

  async function trigger(src: string) {
    triggering = true;
    try {
      const r = await triggerIngest({ source: src });
      notify({ title: `Ingest queued: ${src}`, body: r.status, kind: 'ok', ttlMs: 2200 });
      await refresh();
    } catch (e) {
      notify({ title: 'Trigger failed', body: String(e).slice(0, 160), kind: 'err' });
    } finally {
      triggering = false;
    }
  }

  function fmt(n: number): string {
    if (n < 1000) return String(n);
    if (n < 1_000_000) return (n / 1000).toFixed(1) + 'K';
    return (n / 1_000_000).toFixed(2) + 'M';
  }

  onMount(() => {
    refresh();
    timer = setInterval(refresh, 20_000);
  });

  onDestroy(() => {
    if (timer) clearInterval(timer);
  });
</script>

<div class="h-full w-full overflow-y-auto p-4 font-mono text-xs space-y-4">
  {#if error}
    <div class="bg-err/20 border border-err/40 rounded px-3 py-2 text-err">
      <strong>Ingest error:</strong> {error}
    </div>
  {/if}

  <header>
    <h3 class="text-accent text-sm">Iris · ingest</h3>
    <p class="text-muted text-[10px]">{lastFetched ? `last refresh ${lastFetched}` : 'loading…'}</p>
  </header>

  <!-- Collection stats -->
  <section>
    <h4 class="text-accent text-[11px] uppercase mb-1">Collections</h4>
    {#if stats?.error}
      <p class="text-warn text-[11px]">backend: {stats.error}</p>
    {:else if stats?.collections && Object.keys(stats.collections).length}
      <table class="w-full">
        <thead class="text-muted text-[10px] text-left">
          <tr><th>Collection</th><th class="text-right">Points</th><th class="text-right">Vectors</th><th class="text-right">Indexed</th><th class="text-right">Status</th></tr>
        </thead>
        <tbody>
          {#each Object.entries(stats.collections) as [name, c] (name)}
            <tr class="border-t border-border/20">
              <td class="py-1 text-fg">{name}</td>
              <td class="py-1 text-right text-fg">{c.points_count !== null && c.points_count !== undefined ? fmt(c.points_count) : '–'}</td>
              <td class="py-1 text-right text-muted">{c.vectors_count !== null && c.vectors_count !== undefined ? fmt(c.vectors_count) : '–'}</td>
              <td class="py-1 text-right text-muted">{c.indexed_vectors_count !== null && c.indexed_vectors_count !== undefined ? fmt(c.indexed_vectors_count) : '–'}</td>
              <td class="py-1 text-right text-muted">{c.status ?? ''}</td>
            </tr>
          {/each}
        </tbody>
      </table>
    {:else}
      <p class="text-muted">No collection stats.</p>
    {/if}
    {#if stats?.last_ingest_at}
      <p class="text-muted text-[10px] mt-2">last ingest: {stats.last_ingest_at}</p>
    {/if}
  </section>

  <!-- Trigger sources -->
  <section>
    <h4 class="text-accent text-[11px] uppercase mb-1">Trigger</h4>
    <div class="grid grid-cols-2 gap-2">
      {#each SOURCES as s (s.id)}
        <button
          class="flex items-center justify-between px-3 py-2 rounded border border-border/40 hover:border-accent text-left"
          disabled={triggering}
          on:click={() => trigger(s.id)}
        >
          <div>
            <p class="text-fg">{s.label}</p>
            <p class="text-muted text-[10px]">→ {s.kind}</p>
          </div>
          <span class="text-accent text-[11px]">▶</span>
        </button>
      {/each}
    </div>
    <p class="text-muted text-[10px] mt-3 leading-relaxed">
      Triggers <code class="text-fg">POST /ingest/trigger</code>; routing follows
      zeus/ingest/config.yaml. Profile sources fan out into the memory store via
      LLM fact extraction; knowledge sources go raw into <code class="text-fg">zeus_knowledge</code>.
    </p>
  </section>
</div>
