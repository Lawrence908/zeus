<script lang="ts">
  import { onMount } from 'svelte';
  import type { AppInstance } from '$lib/wm/tree';
  import { fsList, fsRead, fsRoots, type FsEntry } from '$lib/api/fs';
  import { readCodeClip, renderMarkdown } from '$lib/markdown';
  import { notify } from '$lib/notify/store';
  import { openApp } from '$lib/wm/store';

  export let app: AppInstance;
  void app;

  let roots: string[] = [];
  let path = '';
  let entries: FsEntry[] = [];
  let preview:
    | {
        name: string;
        absPath: string;
        kind: 'image' | 'markdown' | 'text';
        content: string;
        src?: string;
        truncated?: boolean;
      }
    | null = null;
  let error = '';
  let showHidden = false;
  let sortBy: 'name' | 'size' | 'mtime' = 'name';
  let sortDesc = false;

  const IMAGE_EXT = new Set(['png', 'jpg', 'jpeg', 'gif', 'webp', 'svg', 'avif', 'ico']);
  const MARKDOWN_EXT = new Set(['md', 'markdown']);

  async function loadRoots() {
    try {
      const r = await fsRoots();
      // eslint-disable-next-line no-console
      console.log('[Zeus OS FileManager] roots response:', r);
      roots = r.read_roots ?? [];
      if (roots.length && !path) {
        path = roots[0];
        await loadDir(path);
      }
    } catch (e) {
      error = String(e);
      // eslint-disable-next-line no-console
      console.error('[Zeus OS FileManager] loadRoots error', e);
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

  function extOf(name: string): string {
    const i = name.lastIndexOf('.');
    if (i < 0) return '';
    return name.slice(i + 1).toLowerCase();
  }

  async function clickEntry(e: FsEntry) {
    const next = path.endsWith('/') ? path + e.name : path + '/' + e.name;
    if (e.kind === 'dir') {
      await loadDir(next);
      return;
    }
    if (e.kind !== 'file') return;

    const ext = extOf(e.name);
    if (IMAGE_EXT.has(ext)) {
      // /zeus-os/fs/file returns text; for binary previews we use a fetch that
      // grabs the raw file via the same endpoint and reconstructs a blob URL.
      try {
        const res = await fetch(`/zeus-os/fs/raw?path=${encodeURIComponent(next)}`);
        if (res.ok) {
          const blob = await res.blob();
          const src = URL.createObjectURL(blob);
          preview = { name: e.name, absPath: next, kind: 'image', content: '', src };
          return;
        }
      } catch {
        /* fall through to text preview */
      }
    }

    try {
      const r = await fsRead(next);
      const kind: 'markdown' | 'text' = MARKDOWN_EXT.has(ext) ? 'markdown' : 'text';
      preview = { name: e.name, absPath: next, kind, content: r.content, truncated: r.truncated };
    } catch (err) {
      error = String(err);
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

  // Crude language detection for highlight.js fences.
  function fenceLang(name: string): string {
    const ext = extOf(name);
    const map: Record<string, string> = {
      py: 'python',
      ts: 'typescript',
      tsx: 'typescript',
      js: 'javascript',
      jsx: 'javascript',
      svelte: 'xml',
      html: 'xml',
      xml: 'xml',
      json: 'json',
      yaml: 'yaml',
      yml: 'yaml',
      sh: 'bash',
      bash: 'bash',
      zsh: 'bash',
      css: 'css',
      go: 'go',
      rs: 'rust',
      sql: 'sql',
      md: 'markdown',
      ini: 'ini',
      toml: 'ini',
      dockerfile: 'dockerfile'
    };
    return map[ext] ?? '';
  }

  // Fetch roots once on mount. Without this the sidebar is empty and the
  // right pane reports "Empty directory." — a regression introduced when
  // onMount got dropped during the markdown-preview refactor.
  onMount(loadRoots);

  function onPreviewClick(ev: MouseEvent) {
    const t = ev.target as HTMLElement | null;
    if (!t) return;
    const btn = t.closest('.code-copy-btn') as HTMLElement | null;
    if (!btn) return;
    const raw = readCodeClip(btn);
    if (raw === null) return;
    navigator.clipboard?.writeText(raw).then(
      () => {
        const orig = btn.textContent;
        btn.textContent = 'Copied';
        btn.classList.add('copied');
        setTimeout(() => {
          btn.textContent = orig ?? 'Copy';
          btn.classList.remove('copied');
        }, 1200);
      },
      () => notify({ title: 'Copy failed', kind: 'warn', ttlMs: 1500 })
    );
  }

  // Clickable breadcrumb segments; each jumps to that path prefix.
  $: crumbs = (() => {
    const parts = path.replace(/\/+$/, '').split('/').filter(Boolean);
    const out: { label: string; full: string }[] = [];
    let acc = '';
    for (const p of parts) {
      acc += '/' + p;
      out.push({ label: p, full: acc });
    }
    return out;
  })();

  // Dirs first, then the selected sort; dotfiles hidden unless toggled on.
  $: view = entries
    .filter((e) => showHidden || !e.name.startsWith('.'))
    .slice()
    .sort((a, b) => {
      const aDir = a.kind === 'dir' ? 0 : 1;
      const bDir = b.kind === 'dir' ? 0 : 1;
      if (aDir !== bDir) return aDir - bDir;
      let cmp = 0;
      if (sortBy === 'size') cmp = a.size - b.size;
      else if (sortBy === 'mtime') cmp = a.mtime - b.mtime;
      else cmp = a.name.localeCompare(b.name);
      return sortDesc ? -cmp : cmp;
    });

  $: previewHtml = (() => {
    if (!preview) return '';
    if (preview.kind === 'markdown') return renderMarkdown(preview.content);
    if (preview.kind === 'text') {
      const lang = fenceLang(preview.name);
      const body = '```' + lang + '\n' + preview.content + '\n```';
      return renderMarkdown(body);
    }
    return '';
  })();
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
      <button class="text-muted hover:text-fg" on:click={up} title="Up one level">↑</button>
      <nav class="flex items-center gap-0.5 truncate flex-1 min-w-0">
        {#each crumbs as c, i (c.full)}
          {#if i > 0}<span class="text-muted/50">/</span>{/if}
          <button
            class="hover:text-accent truncate"
            class:text-fg={i === crumbs.length - 1}
            class:text-muted={i !== crumbs.length - 1}
            on:click={() => loadDir(c.full)}
            title={c.full}
          >{c.label}</button>
        {:else}
          <span class="text-muted">–</span>
        {/each}
      </nav>
      <label class="flex items-center gap-1 text-muted shrink-0 cursor-pointer">
        <input type="checkbox" bind:checked={showHidden} class="accent-current" />
        <span>.dot</span>
      </label>
      <select
        class="bg-surface text-muted rounded border border-border/50 px-1 py-0.5 outline-none shrink-0"
        bind:value={sortBy}
        title="Sort by"
      >
        <option value="name">name</option>
        <option value="size">size</option>
        <option value="mtime">modified</option>
      </select>
      <button
        class="text-muted hover:text-fg shrink-0"
        on:click={() => (sortDesc = !sortDesc)}
        title="Toggle sort direction"
      >{sortDesc ? '↓' : '↑'}</button>
    </header>

    {#if error}
      <div class="text-err px-3 py-2 text-xs">{error}</div>
    {/if}

    <div class="flex-1 flex min-h-0">
      <ul class="w-1/2 overflow-y-auto border-r border-border/40">
        {#each view as e (e.name)}
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
          <header class="mb-2 text-accent flex items-center justify-between gap-2">
            <span class="truncate">{preview.name}</span>
            <div class="flex gap-1 items-center">
              {#if preview.truncated}
                <span class="text-warn text-[10px]">truncated</span>
              {/if}
              {#if preview.kind !== 'image'}
                <button
                  class="text-[10px] px-2 py-0.5 border border-accent text-accent rounded hover:bg-accent hover:text-bg"
                  on:click={() => openApp({ appId: 'editor', kind: 'Editor', title: preview!.name, props: { path: preview!.absPath } })}
                  title="Open in Editor"
                >
                  Edit
                </button>
              {/if}
            </div>
          </header>
          {#if preview.kind === 'image' && preview.src}
            <img src={preview.src} alt={preview.name} class="max-w-full max-h-full object-contain" />
          {:else}
            <div
              class="prose-chat text-xs leading-relaxed"
              on:click={onPreviewClick}
              role="presentation"
            >
              {@html previewHtml}
            </div>
          {/if}
        {:else}
          <p class="text-muted">Select a file to preview. Markdown renders, code highlights, images show as thumbnails.</p>
        {/if}
      </div>
    </div>
  </div>
</div>
