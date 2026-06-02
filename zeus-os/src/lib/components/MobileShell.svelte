<script lang="ts">
  import Panel from './Panel.svelte';
  import type { ModifierMode } from '$lib/wm/keybinds';

  export let modifier: ModifierMode = 'Meta';
  import Terminal from '$lib/apps/Terminal.svelte';
  import Chat from '$lib/apps/Chat.svelte';
  import SystemMonitor from '$lib/apps/SystemMonitor.svelte';
  import FileManager from '$lib/apps/FileManager.svelte';
  import Tools from '$lib/apps/Tools.svelte';
  import Jobs from '$lib/apps/Jobs.svelte';
  import TokenUsage from '$lib/apps/TokenUsage.svelte';
  import Settings from '$lib/apps/Settings.svelte';
  import Memories from '$lib/apps/Memories.svelte';
  import Knowledge from '$lib/apps/Knowledge.svelte';
  import Agents from '$lib/apps/Agents.svelte';
  import Ingest from '$lib/apps/Ingest.svelte';
  import Placeholder from '$lib/apps/Placeholder.svelte';

  import { activeWorkspace, leaves, wm, switchWorkspace, closeFocused, focusLeaf } from '$lib/wm/store';

  const components: Record<string, typeof Terminal> = {
    Terminal,
    Chat,
    SystemMonitor,
    FileManager,
    Tools,
    Jobs,
    TokenUsage,
    Settings,
    Memories,
    Knowledge,
    Agents,
    Ingest,
    Placeholder
  };

  $: idx = $leaves.findIndex((l) => l.id === $activeWorkspace.focusId);
  $: visible = idx >= 0 ? $leaves[idx] : $leaves[0];
  $: Comp = visible ? components[visible.app.kind] ?? Placeholder : null;

  function step(d: number) {
    if (!$leaves.length) return;
    const next = ($leaves.length + (idx < 0 ? 0 : idx) + d) % $leaves.length;
    focusLeaf($leaves[next].id);
  }
</script>

<div class="relative h-full w-full flex flex-col">
  <Panel {modifier} />
  <div class="flex-1 overflow-hidden mt-[30px]">
    {#if visible && Comp}
      <div class="absolute inset-0" style="top: 30px; bottom: 56px;">
        <div class="window-shell focused absolute inset-2 overflow-hidden">
          <header
            class="flex items-center justify-between px-3 py-1.5 text-xs"
            style="background: rgb(var(--surface-2) / 0.75); border-bottom: 1px solid rgb(var(--border-color) / 0.7);"
          >
            <span class="font-mono truncate">{visible.app.title}</span>
            <button class="text-muted hover:text-err" on:click={closeFocused}>×</button>
          </header>
          <div class="absolute inset-0" style="top: 28px;">
            <svelte:component this={Comp} app={visible.app} />
          </div>
        </div>
      </div>
    {:else}
      <div class="absolute inset-0 grid place-items-center text-muted text-sm">
        Tap the + button to open an app.
      </div>
    {/if}
  </div>

  <!-- bottom dock: workspace dots + nav -->
  <nav
    class="surface-blur absolute bottom-0 left-0 right-0 flex items-center justify-between px-3"
    style="height: 56px;"
  >
    <button
      class="text-fg/80 text-xl px-3"
      on:click={() => step(-1)}
      aria-label="Previous window"
    >
      ‹
    </button>
    <div class="flex gap-1.5">
      {#each $wm.workspaces as w (w.id)}
        <button
          class="w-2.5 h-2.5 rounded-full"
          class:bg-accent={w.id === $wm.activeWs}
          class:bg-muted={w.id !== $wm.activeWs}
          on:click={() => switchWorkspace(w.id)}
          aria-label="Workspace {w.id}"
        ></button>
      {/each}
    </div>
    <button
      class="text-fg/80 text-xl px-3"
      on:click={() => step(1)}
      aria-label="Next window"
    >
      ›
    </button>
  </nav>
</div>
