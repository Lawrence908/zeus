<script lang="ts">
  import { onDestroy, onMount, tick } from 'svelte';
  import type { AppInstance } from '$lib/wm/tree';
  import { notify } from '$lib/notify/store';
  import { fsRead, type FsReadResult } from '$lib/api/fs';
  import { jsonFetch } from '$lib/api/base';

  export let app: AppInstance;

  let container: HTMLDivElement;
  let mounted = false;
  let path: string = ((app.props as Record<string, unknown>)?.path as string) ?? '';
  let original = '';
  let buffer = '';
  let loading = false;
  let saving = false;
  let error = '';
  let language = 'plaintext';

  // Track the lazy-imported pieces so unmount can dispose them.
  type MonacoNs = typeof import('monaco-editor');
  let monaco: MonacoNs | null = null;
  let editor: ReturnType<MonacoNs['editor']['create']> | null = null;

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
      value: buffer,
      language,
      theme: 'catppuccin-mocha',
      automaticLayout: true,
      minimap: { enabled: false },
      scrollBeyondLastLine: false,
      fontFamily: 'JetBrains Mono, ui-monospace, monospace',
      fontSize: 13,
      lineNumbers: 'on',
      tabSize: 2
    });

    editor.onDidChangeModelContent(() => {
      if (editor) buffer = editor.getValue();
    });

    // Ctrl/Cmd+S to save.
    editor.addCommand(monaco.KeyMod.CtrlCmd | monaco.KeyCode.KeyS, () => {
      save();
    });

    mounted = true;

    // If a path came in as a prop, load it now that the editor exists.
    if (path) await load(path);
  }

  async function load(p: string) {
    if (!p) return;
    loading = true;
    error = '';
    try {
      const r: FsReadResult = await fsRead(p);
      original = r.content;
      buffer = r.content;
      path = p;
      language = detectLang(p);
      if (monaco && editor) {
        const model = editor.getModel();
        if (model) {
          monaco.editor.setModelLanguage(model, language);
        }
        editor.setValue(buffer);
      }
    } catch (e) {
      error = String(e);
      notify({ title: 'Load failed', body: error.slice(0, 160), kind: 'err' });
    } finally {
      loading = false;
    }
  }

  async function save() {
    if (!path) {
      notify({ title: 'No path — open a file first', kind: 'warn', ttlMs: 1600 });
      return;
    }
    saving = true;
    try {
      await jsonFetch('/zeus-os/fs/write', {
        method: 'POST',
        body: JSON.stringify({ path, content: buffer })
      });
      original = buffer;
      notify({ title: 'Saved', body: path.split('/').pop(), kind: 'ok', ttlMs: 1500 });
    } catch (e) {
      notify({ title: 'Save failed', body: String(e).slice(0, 200), kind: 'err' });
    } finally {
      saving = false;
    }
  }

  function revert() {
    buffer = original;
    if (editor) editor.setValue(original);
  }

  async function promptOpen() {
    const next = window.prompt('Path to open:', path || '/app/zeus/CLAUDE.md');
    if (!next) return;
    await tick();
    await load(next);
  }

  // External callers (FileManager "Open in Editor" button, Obsidian "Edit")
  // mutate app.props.path to retarget this editor. Watch for that.
  $: if (mounted && app && (app.props as Record<string, unknown>)?.path && (app.props as Record<string, unknown>).path !== path) {
    const next = (app.props as Record<string, unknown>).path as string;
    load(next);
  }

  $: dirty = buffer !== original;
  $: title = path ? path.split('/').pop() : '(unsaved)';

  onMount(() => {
    init();
  });

  onDestroy(() => {
    try {
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
    <button class="text-[10px] px-2 py-0.5 border border-border/60 rounded" on:click={promptOpen}>Open…</button>
    <span class="text-fg truncate" title={path}>{title}{dirty ? ' •' : ''}</span>
    <span class="text-muted text-[10px]">{language}</span>
    <div class="ml-auto flex gap-1">
      {#if dirty}
        <button class="text-[10px] px-2 py-0.5 border border-border/60 text-muted rounded" on:click={revert}>Revert</button>
      {/if}
      <button
        class="text-[10px] px-2 py-0.5 rounded border {dirty ? 'border-accent text-accent' : 'border-border/60 text-muted'}"
        disabled={saving || !path || !dirty}
        on:click={save}
        title="Ctrl+S"
      >
        {saving ? 'saving…' : 'Save'}
      </button>
    </div>
  </header>

  {#if loading}
    <p class="text-muted px-3 py-1">loading {path}…</p>
  {/if}

  <div bind:this={container} class="flex-1 min-h-0"></div>
</div>
