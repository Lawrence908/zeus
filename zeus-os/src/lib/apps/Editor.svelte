<script lang="ts">
  import { onDestroy, onMount } from 'svelte';
  import type { AppInstance } from '$lib/wm/tree';
  import { notify } from '$lib/notify/store';
  import { confirmDialog } from '$lib/components/confirm';
  import { fsList, fsRead, fsRoots, fsWrite, type FsEntry } from '$lib/api/fs';

  export let app: AppInstance;

  let container: HTMLDivElement;
  let mounted = false;
  let loading = false;
  let saving = false;
  let error = '';

  // Track the lazy-imported pieces so unmount can dispose them.
  type MonacoNs = typeof import('monaco-editor');
  type MonacoModel = ReturnType<MonacoNs['editor']['createModel']>;
  let monaco: MonacoNs | null = null;
  let editor: ReturnType<MonacoNs['editor']['create']> | null = null;

  // ── multi-file state ──
  // Each open file is a Monaco model; switching tabs is editor.setModel(),
  // which preserves per-file undo history and cursor position for free.
  interface OpenFile {
    path: string;
    model: MonacoModel;
    saved: string;
  }
  let openFiles: OpenFile[] = [];
  let activePath = '';
  let dirtyTick = 0; // bumped on any model edit so the dirty markers recompute

  $: activeFile = openFiles.find((f) => f.path === activePath) ?? null;
  $: language = activeFile ? detectLang(activeFile.path) : 'plaintext';
  $: dirty = dirtyTick >= 0 && !!activeFile && activeFile.model.getValue() !== activeFile.saved;

  function isDirty(f: OpenFile): boolean {
    return dirtyTick >= 0 && f.model.getValue() !== f.saved;
  }

  const EXT_LANG: Record<string, string> = {
    ts: 'typescript',
    tsx: 'typescript',
    js: 'javascript',
    jsx: 'javascript',
    svelte: 'html',
    html: 'html',
    xml: 'xml',
    json: 'json',
    yaml: 'yaml',
    yml: 'yaml',
    sh: 'shell',
    bash: 'shell',
    zsh: 'shell',
    css: 'css',
    scss: 'scss',
    py: 'python',
    rb: 'ruby',
    rs: 'rust',
    go: 'go',
    java: 'java',
    cpp: 'cpp',
    c: 'c',
    sql: 'sql',
    md: 'markdown',
    markdown: 'markdown',
    ini: 'ini',
    toml: 'ini',
    dockerfile: 'dockerfile'
  };

  function detectLang(p: string): string {
    if (!p) return 'plaintext';
    const base = p.split('/').pop()!;
    if (/^Dockerfile/i.test(base)) return 'dockerfile';
    const ext = base.split('.').pop()?.toLowerCase() ?? '';
    return EXT_LANG[ext] ?? 'plaintext';
  }

  function defineCatppuccinTheme(m: MonacoNs) {
    // Hand-tuned to match Zeus OS's Catppuccin Mocha palette so the embedded
    // editor doesn't clash with the surrounding theme.
    m.editor.defineTheme('catppuccin-mocha', {
      base: 'vs-dark',
      inherit: true,
      rules: [
        { token: 'comment', foreground: '6c7086', fontStyle: 'italic' },
        { token: 'keyword', foreground: 'cba6f7' },
        { token: 'string', foreground: 'a6e3a1' },
        { token: 'number', foreground: 'fab387' },
        { token: 'type', foreground: 'f9e2af' },
        { token: 'function', foreground: '89b4fa' },
        { token: 'variable', foreground: 'cdd6f4' }
      ],
      colors: {
        'editor.background': '#1e1e2e',
        'editor.foreground': '#cdd6f4',
        'editorLineNumber.foreground': '#6c7086',
        'editorLineNumber.activeForeground': '#cba6f7',
        'editorCursor.foreground': '#89b4fa',
        'editor.selectionBackground': '#45475a',
        'editorWhitespace.foreground': '#313244',
        'editor.lineHighlightBackground': '#313244',
        'editorIndentGuide.background': '#313244',
        'editorIndentGuide.activeBackground': '#45475a'
      }
    });
  }

  async function init() {
    if (!container) return;
    // Worker plumbing: SvelteKit + Vite bundles workers via ?worker imports.
    // Define the URL factory before importing monaco so it doesn't fall back
    // to "main thread only" mode.
    const w = window as unknown as { MonacoEnvironment?: { getWorker: (workerId: string, label: string) => Worker } };
    if (!w.MonacoEnvironment) {
      // Rollup needs each `new URL(static_string, import.meta.url)` so it
      // can emit a worker chunk per language. Hard-code one per kind; pick
      // by label at runtime.
      const jsonUrl = new URL('monaco-editor/esm/vs/language/json/json.worker.js', import.meta.url);
      const cssUrl = new URL('monaco-editor/esm/vs/language/css/css.worker.js', import.meta.url);
      const htmlUrl = new URL('monaco-editor/esm/vs/language/html/html.worker.js', import.meta.url);
      const tsUrl = new URL('monaco-editor/esm/vs/language/typescript/ts.worker.js', import.meta.url);
      const editorUrl = new URL('monaco-editor/esm/vs/editor/editor.worker.js', import.meta.url);
      w.MonacoEnvironment = {
        getWorker(_workerId: string, label: string): Worker {
          switch (label) {
            case 'json':
              return new Worker(jsonUrl, { type: 'module' });
            case 'css':
            case 'scss':
            case 'less':
              return new Worker(cssUrl, { type: 'module' });
            case 'html':
            case 'handlebars':
            case 'razor':
              return new Worker(htmlUrl, { type: 'module' });
            case 'typescript':
            case 'javascript':
              return new Worker(tsUrl, { type: 'module' });
            default:
              return new Worker(editorUrl, { type: 'module' });
          }
        }
      };
    }

    monaco = await import('monaco-editor');
    defineCatppuccinTheme(monaco);

    editor = monaco.editor.create(container, {
      value: '',
      language: 'plaintext',
      theme: 'catppuccin-mocha',
      automaticLayout: true,
      minimap: { enabled: false },
      scrollBeyondLastLine: false,
      fontFamily: 'JetBrains Mono, ui-monospace, monospace',
      fontSize: 13,
      lineNumbers: 'on',
      tabSize: 2
    });

    // Ctrl/Cmd+S to save.
    editor.addCommand(monaco.KeyMod.CtrlCmd | monaco.KeyCode.KeyS, () => {
      save();
    });

    mounted = true;
    void loadTreeRoots();

    // If a path came in as a prop, load it now that the editor exists.
    const propPath = (app.props as Record<string, unknown>)?.path as string | undefined;
    if (propPath) {
      lastPropPath = propPath;
      await open(propPath);
    }
  }

  async function open(p: string) {
    if (!p || !monaco || !editor) return;
    const existing = openFiles.find((f) => f.path === p);
    if (existing) {
      activate(p);
      return;
    }
    loading = true;
    error = '';
    try {
      const r = await fsRead(p);
      const model = monaco.editor.createModel(r.content, detectLang(p));
      model.onDidChangeContent(() => (dirtyTick += 1));
      openFiles = [...openFiles, { path: p, model, saved: r.content }];
      activate(p);
    } catch (e) {
      error = String(e);
      notify({ title: 'Load failed', body: error.slice(0, 160), kind: 'err' });
    } finally {
      loading = false;
    }
  }

  function activate(p: string) {
    const f = openFiles.find((x) => x.path === p);
    if (!f || !editor) return;
    editor.setModel(f.model);
    activePath = p;
  }

  async function closeTab(p: string) {
    const f = openFiles.find((x) => x.path === p);
    if (!f) return;
    if (isDirty(f)) {
      const ok = await confirmDialog(`Discard unsaved changes in ${p.split('/').pop()}?`, {
        confirmLabel: 'Discard'
      });
      if (!ok) return;
    }
    const idx = openFiles.indexOf(f);
    openFiles = openFiles.filter((x) => x.path !== p);
    f.model.dispose();
    if (activePath === p) {
      const next = openFiles[idx] ?? openFiles[idx - 1];
      if (next) activate(next.path);
      else {
        activePath = '';
        editor?.setModel(null);
      }
    }
  }

  async function save() {
    const f = openFiles.find((x) => x.path === activePath);
    if (!f) {
      notify({ title: 'No file — open one first', kind: 'warn', ttlMs: 1600 });
      return;
    }
    if (!activeWritable) {
      notify({
        title: 'Read-only',
        body: writeEnabled ? 'File is not under a write root' : 'File writes are disabled (ZEUS_OS_FS_WRITE_ENABLED)',
        kind: 'warn',
        ttlMs: 2200
      });
      return;
    }
    saving = true;
    try {
      const value = f.model.getValue();
      await fsWrite(f.path, value);
      f.saved = value;
      dirtyTick += 1;
      notify({ title: 'Saved', body: f.path.split('/').pop(), kind: 'ok', ttlMs: 1500 });
    } catch (e) {
      notify({ title: 'Save failed', body: String(e).slice(0, 200), kind: 'err' });
    } finally {
      saving = false;
    }
  }

  function revert() {
    const f = openFiles.find((x) => x.path === activePath);
    if (!f) return;
    f.model.setValue(f.saved);
  }

  async function promptOpen() {
    const next = window.prompt('Path to open:', activePath || '/app/zeus/CLAUDE.md');
    if (!next) return;
    await open(next);
  }

  // ── file tree sidebar ──
  // Lazy: directories fetch their children on first expand. The tree renders
  // as a flat list with indentation so no recursive component is needed.
  let treeOpen = false;
  let roots: string[] = [];
  // Reads are allowed across read_roots, but writes only under write_roots — so
  // a file can be openable yet not saveable. Track both to surface read-only.
  let writeRoots: string[] = [];
  let writeEnabled = false;
  const childrenCache = new Map<string, FsEntry[]>();
  const expanded = new Set<string>();
  let treeTick = 0;

  $: activeWritable =
    writeEnabled &&
    !!activePath &&
    writeRoots.some((r) => {
      const root = r.replace(/\/+$/, '');
      return activePath === root || activePath.startsWith(root + '/');
    });

  interface TreeRow {
    path: string;
    name: string;
    kind: FsEntry['kind'];
    depth: number;
  }

  async function loadTreeRoots() {
    try {
      const r = await fsRoots();
      roots = r.read_roots ?? [];
      writeRoots = r.write_roots ?? [];
      writeEnabled = r.write_enabled ?? false;
    } catch {
      roots = [];
    }
  }

  async function toggleDir(path: string) {
    if (expanded.has(path)) {
      expanded.delete(path);
    } else {
      expanded.add(path);
      if (!childrenCache.has(path)) {
        try {
          const list = await fsList(path);
          childrenCache.set(
            path,
            list.entries
              .filter((e) => !e.name.startsWith('.'))
              .sort((a, b) => {
                const d = (a.kind === 'dir' ? 0 : 1) - (b.kind === 'dir' ? 0 : 1);
                return d !== 0 ? d : a.name.localeCompare(b.name);
              })
          );
        } catch (e) {
          notify({ title: 'List failed', body: String(e).slice(0, 120), kind: 'warn', ttlMs: 2000 });
          expanded.delete(path);
        }
      }
    }
    treeTick += 1;
  }

  function buildRows(): TreeRow[] {
    const rows: TreeRow[] = [];
    // Roots can overlap (e.g. /app/zeus and /app/zeus/data), so the same path
    // can surface both as a nested child and as a top-level root. Dedupe by
    // path — the {#each} key must be unique.
    const seen = new Set<string>();
    const push = (row: TreeRow) => {
      if (seen.has(row.path)) return;
      seen.add(row.path);
      rows.push(row);
    };
    const walk = (dir: string, depth: number) => {
      const kids = childrenCache.get(dir);
      if (!kids || !expanded.has(dir)) return;
      for (const e of kids) {
        const p = dir.replace(/\/+$/, '') + '/' + e.name;
        push({ path: p, name: e.name, kind: e.kind, depth });
        if (e.kind === 'dir') walk(p, depth + 1);
      }
    };
    for (const r of roots) {
      push({ path: r, name: r, kind: 'dir', depth: 0 });
      walk(r, 1);
    }
    return rows;
  }

  $: treeRows = treeTick >= 0 && treeOpen ? buildRows() : [];

  // External callers (FileManager "Open in Editor" button, Obsidian "Edit")
  // mutate app.props.path to retarget this editor. Fire only when the prop
  // itself changes — keying on activePath instead would re-open the prop file
  // every time the user switched to a different tab.
  let lastPropPath = '';
  $: {
    const propPath = (app?.props as Record<string, unknown> | undefined)?.path as string | undefined;
    if (mounted && propPath && propPath !== lastPropPath) {
      lastPropPath = propPath;
      void open(propPath);
    }
  }

  $: title = activePath ? activePath.split('/').pop() : '(no file)';

  onMount(() => {
    init();
  });

  onDestroy(() => {
    try {
      for (const f of openFiles) f.model.dispose();
      editor?.dispose();
    } catch {
      /* ignore */
    }
  });
</script>

<div class="h-full w-full flex flex-col font-mono text-xs">
  {#if error}
    <div class="bg-err/20 border-b border-err/40 px-3 py-2 text-err">
      <strong>Editor error:</strong> {error}
    </div>
  {/if}

  <header class="flex items-center gap-2 px-3 py-1.5 border-b border-border/40">
    <button
      class="text-[10px] px-2 py-0.5 border rounded"
      class:border-accent={treeOpen}
      class:text-accent={treeOpen}
      class:border-border={!treeOpen}
      class:text-muted={!treeOpen}
      on:click={() => (treeOpen = !treeOpen)}
      title="Toggle file tree"
    >tree</button>
    <button class="text-[10px] px-2 py-0.5 border border-border/60 rounded" on:click={promptOpen}>Open…</button>
    <span class="text-fg truncate" title={activePath}>{title}{dirty ? ' •' : ''}</span>
    <span class="text-muted text-[10px]">{language}</span>
    {#if activePath && !activeWritable}
      <span class="text-warn text-[10px]" title={writeEnabled ? 'Not under a write root — read-only' : 'File writes are disabled'}>read-only</span>
    {/if}
    <div class="ml-auto flex gap-1">
      {#if dirty}
        <button class="text-[10px] px-2 py-0.5 border border-border/60 text-muted rounded" on:click={revert}>Revert</button>
      {/if}
      <button
        class="text-[10px] px-2 py-0.5 rounded border {dirty && activeWritable ? 'border-accent text-accent' : 'border-border/60 text-muted'}"
        disabled={saving || !activePath || !dirty || !activeWritable}
        on:click={save}
        title={activePath && !activeWritable ? 'Read-only' : 'Ctrl+S'}
      >
        {saving ? 'saving…' : 'Save'}
      </button>
    </div>
  </header>

  {#if openFiles.length > 1}
    <div class="flex items-center px-1 py-0.5 border-b border-border/30 overflow-x-auto" style="background: rgb(var(--surface-2) / 0.5);">
      {#each openFiles as f (f.path)}
        <button
          class="px-2 py-1 rounded-t-md mr-1 flex items-center gap-1 whitespace-nowrap transition-colors"
          class:bg-surface={f.path === activePath}
          class:text-fg={f.path === activePath}
          class:text-muted={f.path !== activePath}
          on:click={() => activate(f.path)}
          title={f.path}
        >
          <span>{f.path.split('/').pop()}{isDirty(f) ? ' •' : ''}</span>
          <span
            class="opacity-50 hover:opacity-100 hover:text-err"
            role="button"
            tabindex="0"
            on:click={(ev) => {
              ev.stopPropagation();
              closeTab(f.path);
            }}
            on:keydown={(ev) => ev.key === 'Enter' && closeTab(f.path)}
          >×</span>
        </button>
      {/each}
    </div>
  {/if}

  {#if loading}
    <p class="text-muted px-3 py-1">loading…</p>
  {/if}

  <div class="flex-1 flex min-h-0">
    {#if treeOpen}
      <aside class="w-56 shrink-0 border-r border-border/40 overflow-y-auto py-1">
        {#each treeRows as row (row.path)}
          <button
            class="w-full text-left px-2 py-0.5 hover:bg-surface2/60 truncate flex items-center gap-1"
            class:text-accent={row.path === activePath}
            style="padding-left: {8 + row.depth * 12}px;"
            on:click={() => (row.kind === 'dir' ? toggleDir(row.path) : open(row.path))}
            title={row.path}
          >
            {#if row.kind === 'dir'}
              <span class="text-muted">{expanded.has(row.path) ? '▾' : '▸'}</span>
            {/if}
            <span class="truncate">{row.name}</span>
          </button>
        {:else}
          <p class="text-muted/60 px-3 py-2 text-[10px]">No readable roots.</p>
        {/each}
      </aside>
    {/if}
    <div bind:this={container} class="flex-1 min-w-0 min-h-0"></div>
  </div>
</div>
