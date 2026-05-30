<script lang="ts">
  import { onMount } from 'svelte';
  import type { AppInstance } from '$lib/wm/tree';
  import { fsList, fsRead, fsRoots, type FsEntry } from '$lib/api/fs';

  export let app: AppInstance;
  void app;

  let roots: string[] = [];
  let path = '';
  let entries: FsEntry[] = [];
  let preview: { name: string; content: string; truncated: boolean } | null = null;
  let error = '';

  async function loadRoots() {
    try {
      const r = await fsRoots();
      roots = r.read_roots;
      if (roots.length && !path) {
        path = roots[0];
        await loadDir(path);
      }
    } catch (e) {
      error = String(e);
    }
  }

  async function loadDir(p: string) {
    error = '';
    preview = null;
    try {
      const list = await fsList(p);
      path = list.path;
      entries = list.entries;
    } catch (e) {
      error = String(e);
      entries = [];
    }
  }

  async function clickEntry(e: FsEntry) {
    const next = path.endsWith('/') ? path + e.name : path + '/' + e.name;
    if (e.kind === 'dir') {
      await loadDir(next);
    } else if (e.kind === 'file') {
      try {
        const r = await fsRead(next);
        preview = { name: e.name, content: r.content, truncated: r.truncated };
      } catch (err) {
        error = String(err);
      }
    }
  }

  function up() {
    const parts = path.replace(/\/+$/, '').split('/');
    if (parts.length <= 1) return;
    parts.pop();
    const next = parts.join('/') || '/';
    loadDir(next);
  }

  function fmt(n: number): string {
    if (n < 1024) return `${n} B`;
    const units = ['KB', 'MB', 'GB'];
    let i = -1;
    let v = n;
    while (v >= 1024 && i < units.length - 1) {
      v /= 1024;
      i += 1;
    }
    return `${v.toFixed(1)} ${units[i]}`;
  }

  onMount(loadRoots);
</script>

<div class="h-full w-full flex font-mono text-sm">
  <aside class="w-44 border-r border-border/40 overflow-y-auto p-2 space-y-1">
    <p class="text-xs text-muted px-2 pt-1 pb-2 uppercase">Roots</p>
    {#each roots as r (r)}
      <button
        class="w-full text-left px-2 py-1 rounded hover:bg-surface2/60 truncate"
        class:bg-surface2={r === path}
        on:click={() => loadDir(r)}
        title={r}
      >
        {r}
      </button>
    {/each}
  </aside>

  <div class="flex-1 flex flex-col min-w-0">
    <header class="flex items-center gap-2 px-3 py-1.5 border-b border-border/40 text-xs">
      <button class="text-muted hover:text-fg" on:click={up}>↑</button>
      <span class="truncate">{path || '–'}</span>
    </header>

    {#if error}
      <div class="text-err px-3 py-2 text-xs">{error}</div>
    {/if}

    <div class="flex-1 flex min-h-0">
      <ul class="w-1/2 overflow-y-auto border-r border-border/40">
        {#each entries as e (e.name)}
          <li>
            <button
              class="w-full text-left flex items-center justify-between px-3 py-1 hover:bg-surface2/60"
              on:dblclick={() => clickEntry(e)}
              on:click={() => clickEntry(e)}
            >
              <span class="truncate">
                {e.kind === 'dir' ? '📁' : e.kind === 'link' ? '🔗' : '📄'}
                &nbsp;{e.name}
              </span>
              <span class="text-muted text-xs">{e.kind === 'dir' ? '' : fmt(e.size)}</span>
            </button>
          </li>
        {:else}
          <li class="px-3 py-2 text-muted text-xs">Empty directory.</li>
        {/each}
      </ul>
      <div class="w-1/2 overflow-y-auto p-3 text-xs">
        {#if preview}
          <header class="mb-2 text-accent">{preview.name}{preview.truncated ? ' (truncated)' : ''}</header>
          <pre class="whitespace-pre-wrap leading-relaxed">{preview.content}</pre>
        {:else}
          <p class="text-muted">Select a file to preview.</p>
        {/if}
      </div>
    </div>
  </div>
</div>
