<script lang="ts">
  import { fade, scale } from 'svelte/transition';
  import { cubicOut } from 'svelte/easing';
  import { tweened } from 'svelte/motion';
  import { onDestroy } from 'svelte';

  import type { LeafNode, Rect } from '$lib/wm/tree';
  import { focusLeaf, closeFocused } from '$lib/wm/store';

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
  import Obsidian from '$lib/apps/Obsidian.svelte';
  import Editor from '$lib/apps/Editor.svelte';
  import HomeAssistant from '$lib/apps/HomeAssistant.svelte';
  import Linear from '$lib/apps/Linear.svelte';
  import Processes from '$lib/apps/Processes.svelte';
  import Network from '$lib/apps/Network.svelte';
  import Notepad from '$lib/apps/Notepad.svelte';
  import Calendar from '$lib/apps/Calendar.svelte';
  import Images from '$lib/apps/Images.svelte';
  import VoiceOrb from '$lib/apps/VoiceOrb.svelte';
  import Epstein from '$lib/apps/Epstein.svelte';
  import Placeholder from '$lib/apps/Placeholder.svelte';

  export let leaf: LeafNode;
  export let rect: Rect;
  export let focused: boolean;

  const x = tweened(rect.x, { duration: 180, easing: cubicOut });
  const y = tweened(rect.y, { duration: 180, easing: cubicOut });
  const w = tweened(rect.w, { duration: 180, easing: cubicOut });
  const h = tweened(rect.h, { duration: 180, easing: cubicOut });

  $: x.set(rect.x);
  $: y.set(rect.y);
  $: w.set(rect.w);
  $: h.set(rect.h);

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
    Obsidian,
    Editor,
    HomeAssistant,
    Linear,
    Processes,
    Network,
    Notepad,
    Calendar,
    Images,
    VoiceOrb,
    Epstein,
    Placeholder
  };
  $: Comp = components[leaf.app.kind] ?? Placeholder;

  onDestroy(() => {
    /* tweens are GC'd by Svelte */
  });
</script>

<div
  class="window-shell absolute overflow-hidden"
  class:focused
  style="left:{$x}px; top:{$y}px; width:{$w}px; height:{$h}px;"
  role="group"
  aria-label={leaf.app.title}
  on:mousedown={() => focusLeaf(leaf.id)}
  in:scale={{ duration: 200, start: 0.96, easing: cubicOut }}
  out:fade={{ duration: 120 }}
>
  <header
    class="flex items-center justify-between px-3 py-1.5 text-xs select-none"
    style="background: rgb(var(--surface-2) / 0.75); border-bottom: 1px solid rgb(var(--border-color) / 0.7);"
  >
    <span class="font-mono truncate text-muted">{leaf.app.title}</span>
    <button
      class="text-muted hover:text-err transition-colors px-1"
      title="Close"
      on:click={() => {
        focusLeaf(leaf.id);
        closeFocused();
      }}
      aria-label="Close window"
    >
      ×
    </button>
  </header>
  <div class="absolute inset-0" style="top: 28px;">
    <svelte:component this={Comp} app={leaf.app} />
  </div>
</div>
