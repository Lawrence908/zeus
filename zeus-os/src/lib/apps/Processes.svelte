<script lang="ts">
  import { onDestroy, onMount } from 'svelte';
  import type { AppInstance } from '$lib/wm/tree';
  import { hostProcesses, type HostProcess } from '$lib/api/host';

  export let app: AppInstance;
  void app;

  let procs: HostProcess[] = [];
  let error = '';
  let lastFetched = '';
  let loading = true;
  let timer: ReturnType<typeof setInterval> | null = null;
  let filter = '';
  let sortBy: 'pcpu' | 'pmem' | 'rss_mb' | 'pid' = 'pcpu';

  async function refresh() {
    try {
      const r = await hostProcesses(60);
      procs = r.processes ?? [];
      error = r.ok ? '' : r.error ?? '';
      lastFetched = new Date().toLocaleTimeString();
    } catch (e) {
      error = String(e);
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

  $: filtered = procs
    .filter((p) => {
      const q = filter.toLowerCase().trim();
      if (!q) return true;
      return p.comm.toLowerCase().includes(q) || p.cmd.toLowerCase().includes(q) || p.user.toLowerCase().includes(q);
    })
    .slice()
    .sort((a, b) => {
      const av = a[sortBy];
      const bv = b[sortBy];
      if (sortBy === 'pid') return av - bv;
      return bv - av;
    });

  function setSort(k: typeof sortBy) {
    sortBy = k;
  }
</script>

<div class="h-full w-full flex flex-col font-mono text-xs">
  {#if error}
    <div class="bg-err/20 border-b border-err/40 px-3 py-2 text-err">{error}</div>
  {/if}

  <header class="px-3 py-1.5 border-b border-border/40 flex items-center gap-2 flex-wrap">
    <h3 class="text-accent text-sm">Processes</h3>
    <input
      bind:value={filter}
      placeholder="filter…"
      class="flex-1 min-w-[120px] bg-transparent border-b border-border/40 outline-none text-fg"
    />
    <span class="text-muted text-[10px]">
      {filtered.length} / {procs.length}{loading ? ' · loading…' : ''} {lastFetched}
    </span>
  </header>

  <div class="flex-1 overflow-y-auto">
    <table class="w-full">
      <thead class="text-muted text-[10px] uppercase sticky top-0 bg-bg/90 backdrop-blur">
        <tr>
          <th class="text-right pr-2 py-1 cursor-pointer" on:click={() => setSort('pid')} class:text-accent={sortBy === 'pid'}>PID</th>
          <th class="text-left pr-2">user</th>
          <th class="text-right pr-2 cursor-pointer" on:click={() => setSort('pcpu')} class:text-accent={sortBy === 'pcpu'}>CPU%</th>
          <th class="text-right pr-2 cursor-pointer" on:click={() => setSort('pmem')} class:text-accent={sortBy === 'pmem'}>MEM%</th>
          <th class="text-right pr-2 cursor-pointer" on:click={() => setSort('rss_mb')} class:text-accent={sortBy === 'rss_mb'}>RSS</th>
          <th class="text-left">command</th>
        </tr>
      </thead>
      <tbody>
        {#each filtered as p (p.pid)}
          <tr class="border-t border-border/10 hover:bg-surface2/30">
            <td class="text-right pr-2 text-muted">{p.pid}</td>
            <td class="pr-2 text-fg">{p.user}</td>
            <td class="text-right pr-2 text-fg">{p.pcpu.toFixed(1)}</td>
            <td class="text-right pr-2 text-muted">{p.pmem.toFixed(1)}</td>
            <td class="text-right pr-2 text-muted">{p.rss_mb.toFixed(0)} MB</td>
            <td class="text-fg/90 truncate max-w-[400px]" title={p.cmd}>{p.comm}</td>
          </tr>
        {:else}
          <tr><td colspan="6" class="text-muted text-center py-6">
            {loading ? 'loading…' : 'no processes match. Host SSH may not be configured (ZEUS_OS_PTY_HOST_SSH=0).'}
          </td></tr>
        {/each}
      </tbody>
    </table>
  </div>
</div>
