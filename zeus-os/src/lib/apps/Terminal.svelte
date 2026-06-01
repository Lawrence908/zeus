<script lang="ts">
  import type { AppInstance } from '$lib/wm/tree';
  import TerminalPane from './TerminalPane.svelte';

  export let app: AppInstance;
  void app;

  interface Tab {
    id: number;
    label: string;
  }

  let tabs: Tab[] = [{ id: 1, label: 'shell' }];
  let activeId = 1;
  let nextId = 2;

  function addTab() {
    const t: Tab = { id: nextId, label: 'shell' };
    nextId += 1;
    tabs = [...tabs, t];
    activeId = t.id;
  }

  function closeTab(id: number) {
    const idx = tabs.findIndex((t) => t.id === id);
    if (idx < 0) return;
    tabs = tabs.filter((t) => t.id !== id);
    if (activeId === id) {
      activeId = tabs[Math.min(idx, tabs.length - 1)]?.id ?? 0;
    }
    if (tabs.length === 0) {
      // Don't auto-close the window; let the user explicitly close it via the
      // window chrome's close button. Add a fresh tab so the pane isn't blank.
      addTab();
    }
  }

  function onPaneExit(id: number) {
    return () => closeTab(id);
  }

  function onKey(ev: KeyboardEvent) {
    // Cmd/Ctrl + Shift + T: new tab. Cmd/Ctrl + Shift + W: close current.
    const mod = ev.metaKey || ev.ctrlKey;
    if (!mod || !ev.shiftKey) return;
    if (ev.key.toLowerCase() === 't') {
      ev.preventDefault();
      addTab();
    } else if (ev.key.toLowerCase() === 'w') {
      ev.preventDefault();
      closeTab(activeId);
    }
  }
</script>

<svelte:window on:keydown={onKey} />

<div class="h-full w-full flex flex-col">
  {#if tabs.length > 1}
    <div class="flex items-center px-1 py-0.5 text-xs font-mono select-none border-b border-border/30" style="background: rgb(var(--surface-2) / 0.5);">
      {#each tabs as t (t.id)}
        <button
          class="px-2 py-1 rounded-t-md mr-1 flex items-center gap-1 transition-colors"
          class:bg-surface={t.id === activeId}
          class:text-fg={t.id === activeId}
          class:text-muted={t.id !== activeId}
          on:click={() => (activeId = t.id)}
        >
          <span>{t.label} {t.id}</span>
          <span
            class="opacity-50 hover:opacity-100 hover:text-err"
            role="button"
            tabindex="0"
            on:click|stopPropagation={() => closeTab(t.id)}
            on:keydown={(ev) => ev.key === 'Enter' && closeTab(t.id)}
          >
            ×
          </span>
        </button>
      {/each}
      <button
        class="px-2 py-1 text-muted hover:text-fg"
        on:click={addTab}
        title="New tab (Ctrl+Shift+T)"
      >
        +
      </button>
    </div>
  {/if}
  <div class="flex-1 min-h-0 relative">
    {#each tabs as t (t.id)}
      <div class="absolute inset-0">
        <TerminalPane visible={t.id === activeId} onExit={onPaneExit(t.id)} />
      </div>
    {/each}
  </div>
  {#if tabs.length === 1}
    <button
      class="absolute top-1 right-1 z-10 text-muted hover:text-fg text-xs font-mono px-1 opacity-50 hover:opacity-100"
      on:click={addTab}
      title="New tab (Ctrl+Shift+T)"
    >
      +
    </button>
  {/if}
</div>
