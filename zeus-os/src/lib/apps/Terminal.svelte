<script lang="ts">
  import type { AppInstance } from '$lib/wm/tree';
  import TerminalPane from './TerminalPane.svelte';
  import {
    closeTab as registryCloseTab,
    getWindowState,
    newTab as registryNewTab,
    setActiveTab,
    type TerminalTab
  } from './terminal-sessions';

  export let app: AppInstance;

  // Rehydrate tab list + active tab from the module-scoped registry so a
  // float ↔ tile toggle keeps the shells (and their buffers) intact.
  let state = getWindowState(app.instanceId);
  let tabs: TerminalTab[] = state.tabs;
  let activeId: string = state.activeTabId ?? tabs[0]?.id ?? '';

  function refresh() {
    state = getWindowState(app.instanceId);
    tabs = state.tabs;
    activeId = state.activeTabId ?? tabs[0]?.id ?? '';
  }

  function addTab() {
    registryNewTab(app.instanceId);
    refresh();
  }

  function closeTab(id: string) {
    const remaining = registryCloseTab(app.instanceId, id);
    if (remaining.length === 0) {
      // Keep the window populated rather than going blank — the WM's window
      // close button is the explicit teardown path.
      registryNewTab(app.instanceId);
    }
    refresh();
  }

  function pickTab(id: string) {
    setActiveTab(app.instanceId, id);
    activeId = id;
  }

  function onPaneExit(id: string) {
    return () => closeTab(id);
  }

  function onKey(ev: KeyboardEvent) {
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
      {#each tabs as t, idx (t.id)}
        <button
          class="px-2 py-1 rounded-t-md mr-1 flex items-center gap-1 transition-colors"
          class:bg-surface={t.id === activeId}
          class:text-fg={t.id === activeId}
          class:text-muted={t.id !== activeId}
          on:click={() => pickTab(t.id)}
        >
          <span>{t.label} {idx + 1}</span>
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
        <TerminalPane
          instanceId={app.instanceId}
          tabId={t.id}
          visible={t.id === activeId}
          onExit={onPaneExit(t.id)}
        />
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
