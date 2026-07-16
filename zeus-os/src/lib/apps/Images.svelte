<script lang="ts">
  import { onMount } from 'svelte';
  import type { AppInstance } from '$lib/wm/tree';
  import { fsList, fsRoots, type FsEntry } from '$lib/api/fs';

  export let app: AppInstance;
  void app;

  const IMAGE_EXT = new Set(['png', 'jpg', 'jpeg', 'gif', 'webp', 'svg', 'avif']);

  let roots: string[] = [];
  let path = '';
  let entries: FsEntry[] = [];
  let error = '';
  let loading = true;
  let selected: { name: string; abs: string } | null = null;
  let pathInput = '';

  function extOf(name: string): string {
    const i = name.lastIndexOf('.');
    return i < 0 ? '' : name.slice(i + 1).toLowerCase();
  }

  async function loadRoots() {
    try {
      const r = await fsRoots();
      roots = r.read_roots ?? [];
      if (roots.length && !path) {
        path = roots[0];
        pathInput = path;
        await loadDir(path);
      }
    } catch (e) {
      error = String(e);
    } finally {
      loading = false;
    }
  }

  async function loadDir(p: string) {
    error = '';
    loading = true;
    try {
      const list = await fsList(p);
      path = list.path;
      pathInput = list.path;
      entries = list.entries;
    } catch (e) {
      error = String(e);
      entries = [];
    } finally {
      loading = false;
    }
  }

  function navigate(e: FsEntry) {
    const next = path.endsWith('/') ? path + e.name : path + '/' + e.name;
    if (e.kind === 'dir') loadDir(next);
  }

  function up() {
    const parts = path.replace(/\/+$/, '').split('/');
    if (parts.length <= 1) return;
    parts.pop();
    loadDir(parts.join('/') || '/');
  }

  function rawUrl(name: string): string {
    const abs = path.endsWith('/') ? path + name : path + '/' + name;
    return `/zeus-os/fs/raw?path=${encodeURIComponent(abs)}`;
  }

  function pick(e: FsEntry) {
    const abs = path.endsWith('/') ? path + e.name : path + '/' + e.name;
    selected = { name: e.name, abs };
  }

  function fmt(n: number): string {
    if (n < 1024) return `${n} B`;
    if (n < 1_048_576) return `${(n / 1024).toFixed(1)} KB`;
    return `${(n / 1_048_576).toFixed(1)} MB`;
  }

  onMount(loadRoots);

  $: images = entries.filter((e) => e.kind === 'file' && IMAGE_EXT.has(extOf(e.name)));
  $: subdirs = entries.filter((e) => e.kind === 'dir');
</script>

<div class="h-full w-full flex flex-col font-mono text-xs">
  {#if error}
    <div class="bg-err/20 border-b border-err/40 px-3 py-2 text-err">{error}</div>
  {/if}

  <header class="px-3 py-1.5 border-b border-border/40 flex items-center gap-2">
    <button class="text-muted hover:text-fg" on:click={up} title="up">↑</button>
    <input
      bind:value={pathInput}
      on:keydown={(ev) => ev.key === 'Enter' && loadDir(pathInput)}
      class="flex-1 bg-transparent border-b border-border/40 outline-none text-fg"
    />
    <select bind:value={path} on:change={() => loadDir(path)} class="bg-surface text-fg p-1 rounded border border-border/40 text-[11px]">
      {#each roots as r (r)}<option value={r}>{r}</option>{/each}
    </select>
    <span class="text-muted text-[10px]">{images.length} images{loading ? ' · loading…' : ''}</span>
  </header>

  <div class="flex-1 flex min-h-0">
    <!-- Gallery -->
    <div class="flex-1 overflow-y-auto p-2">
      {#if subdirs.length}
        <div class="flex flex-wrap gap-1 mb-3">
          {#each subdirs as d (d.name)}
            <button class="text-[10px] px-2 py-0.5 rounded border border-border/40 text-muted hover:text-fg hover:border-accent" on:click={() => navigate(d)}>
              📁 {d.name}
            </button>
          {/each}
        </div>
      {/if}
      {#if images.length}
        <div class="grid gap-2" style="grid-template-columns: repeat(auto-fill, minmax(140px, 1fr));">
          {#each images as img (img.name)}
            <button
              class="aspect-square rounded border border-border/40 hover:border-accent overflow-hidden flex flex-col"
              class:border-accent={selected?.name === img.name}
              on:click={() => pick(img)}
              title="{img.name} · {fmt(img.size)}"
            >
              <div class="flex-1 grid place-items-center bg-surface2/30">
                <img src={rawUrl(img.name)} alt={img.name} class="max-h-full max-w-full object-contain" loading="lazy" />
              </div>
              <p class="text-[9px] text-muted truncate px-1 py-0.5 border-t border-border/30 bg-surface/60">{img.name}</p>
            </button>
          {/each}
        </div>
      {:else if !loading}
        <p class="text-muted text-center mt-12">No images in this directory.</p>
      {/if}
    </div>

    <!-- Preview pane -->
    {#if selected}
      <aside class="w-1/3 min-w-[260px] border-l border-border/40 flex flex-col">
        <header class="px-3 py-2 border-b border-border/40 text-[11px] text-accent truncate" title={selected.abs}>{selected.name}</header>
        <div class="flex-1 grid place-items-center p-3 bg-surface2/30">
          <img src={`/zeus-os/fs/raw?path=${encodeURIComponent(selected.abs)}`} alt={selected.name} class="max-h-full max-w-full object-contain" />
        </div>
        <footer class="px-3 py-1.5 border-t border-border/40 text-[10px] text-muted truncate">{selected.abs}</footer>
      </aside>
    {/if}
  </div>
</div>
