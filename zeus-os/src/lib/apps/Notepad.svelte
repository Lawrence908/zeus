<script lang="ts">
  import { onDestroy, onMount } from 'svelte';
  import type { AppInstance } from '$lib/wm/tree';
  import { notify } from '$lib/notify/store';
  import { renderMarkdown, readCodeClip } from '$lib/markdown';
  import { jsonFetch } from '$lib/api/base';

  export let app: AppInstance;

  // Each window keeps its own scratchpad. Persisted to localStorage keyed
  // by instanceId so it survives reloads (but not window close).
  const STORAGE_KEY = `zeus-os.notepad.${app.instanceId}`;
  const SAVE_DEBOUNCE_MS = 600;

  let text = '';
  let mode: 'edit' | 'preview' | 'split' = 'edit';
  let savedAt = '';
  let saveTimer: ReturnType<typeof setTimeout> | null = null;

  function restore() {
    if (typeof localStorage === 'undefined') return;
    text = localStorage.getItem(STORAGE_KEY) ?? '';
  }

  function persistLocal() {
    if (typeof localStorage === 'undefined') return;
    try {
      localStorage.setItem(STORAGE_KEY, text);
      savedAt = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' });
    } catch {
      /* quota / private-mode */
    }
  }

  function scheduleSave() {
    if (saveTimer) clearTimeout(saveTimer);
    saveTimer = setTimeout(persistLocal, SAVE_DEBOUNCE_MS);
  }

  async function exportToFile() {
    const ts = new Date().toISOString().replace(/[:.]/g, '-').slice(0, 19);
    const path = `/root/.zeus/notepad-${ts}.md`;
    try {
      await jsonFetch('/zeus-os/fs/write', {
        method: 'POST',
        body: JSON.stringify({ path, content: text })
      });
      notify({ title: 'Exported', body: path, kind: 'ok', ttlMs: 2200 });
    } catch (e) {
      notify({ title: 'Export failed', body: String(e).slice(0, 160), kind: 'err' });
    }
  }

  function clearAll() {
    if (!text || confirm('Clear notepad contents?')) {
      text = '';
      persistLocal();
    }
  }

  function onPreviewClick(ev: MouseEvent) {
    const t = ev.target as HTMLElement | null;
    if (!t) return;
    const btn = t.closest('.code-copy-btn') as HTMLElement | null;
    if (!btn) return;
    const raw = readCodeClip(btn);
    if (raw === null) return;
    navigator.clipboard?.writeText(raw).then(
      () => {
        btn.textContent = 'Copied';
        btn.classList.add('copied');
        setTimeout(() => {
          btn.textContent = 'Copy';
          btn.classList.remove('copied');
        }, 1200);
      },
      () => notify({ title: 'Copy failed', kind: 'warn', ttlMs: 1500 })
    );
  }

  onMount(() => {
    restore();
  });

  onDestroy(() => {
    if (saveTimer) clearTimeout(saveTimer);
    persistLocal();
  });

  $: if (text !== undefined) {
    scheduleSave();
  }
</script>

<div class="h-full w-full flex flex-col font-mono text-xs">
  <header class="px-3 py-1.5 border-b border-border/40 flex items-center gap-2">
    <h3 class="text-accent text-sm">Notepad</h3>
    <span class="text-muted text-[10px]">{text.length} chars{savedAt ? ` · saved ${savedAt}` : ''}</span>
    <div class="ml-auto flex gap-1 text-[10px]">
      <button
        class="px-2 py-0.5 rounded border"
        class:border-accent={mode === 'edit'}
        class:text-accent={mode === 'edit'}
        class:border-border={mode !== 'edit'}
        class:text-muted={mode !== 'edit'}
        on:click={() => (mode = 'edit')}
      >edit</button>
      <button
        class="px-2 py-0.5 rounded border"
        class:border-accent={mode === 'split'}
        class:text-accent={mode === 'split'}
        class:border-border={mode !== 'split'}
        class:text-muted={mode !== 'split'}
        on:click={() => (mode = 'split')}
      >split</button>
      <button
        class="px-2 py-0.5 rounded border"
        class:border-accent={mode === 'preview'}
        class:text-accent={mode === 'preview'}
        class:border-border={mode !== 'preview'}
        class:text-muted={mode !== 'preview'}
        on:click={() => (mode = 'preview')}
      >preview</button>
      <button class="px-2 py-0.5 border border-border/60 rounded text-muted hover:text-fg" on:click={exportToFile}>export .md</button>
      <button class="px-2 py-0.5 border border-err/60 rounded text-err hover:bg-err hover:text-bg" on:click={clearAll}>clear</button>
    </div>
  </header>

  <div class="flex-1 flex min-h-0">
    {#if mode === 'edit' || mode === 'split'}
      <textarea
        bind:value={text}
        spellcheck="false"
        placeholder="Quick scratchpad. Markdown-aware preview. Persists per-window in localStorage; export to ~/.zeus/notepad-*.md when you want it on disk."
        class="flex-1 bg-transparent p-4 outline-none text-fg leading-relaxed resize-none {mode === 'split' ? 'border-r border-border/40 w-1/2' : ''}"
      ></textarea>
    {/if}
    {#if mode === 'preview' || mode === 'split'}
      <div
        class="flex-1 overflow-y-auto p-4 prose-chat leading-relaxed {mode === 'split' ? 'w-1/2' : ''}"
        on:click={onPreviewClick}
        role="presentation"
      >
        {#if text.trim()}
          {@html renderMarkdown(text)}
        {:else}
          <p class="text-muted">(empty)</p>
        {/if}
      </div>
    {/if}
  </div>
</div>
