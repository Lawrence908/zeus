<script lang="ts">
  import { onDestroy, onMount } from 'svelte';

  import { wm, activeWorkspace, switchWorkspace } from '$lib/wm/store';
  import { isEmpty } from '$lib/wm/workspace';
  import { openSysStream, type SysSample } from '$lib/api/sys';
  import { findLeaf } from '$lib/wm/tree';
  import { MODIFIER_LABEL, type ModifierMode } from '$lib/wm/keybinds';

  export let modifier: ModifierMode = 'Meta';

  let now = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' });
  let clock: ReturnType<typeof setInterval> | null = null;

  let sample: SysSample | null = null;
  let stream: ReturnType<typeof openSysStream> | null = null;

  onMount(() => {
    clock = setInterval(() => {
      now = new Date().toLocaleTimeString([], {
        hour: '2-digit',
        minute: '2-digit',
        second: '2-digit'
      });
    }, 1000);
    stream = openSysStream((s) => (sample = s));
  });

  onDestroy(() => {
    if (clock) clearInterval(clock);
    stream?.close();
  });

  $: ws = $activeWorkspace;
  $: focusedTitle = ws?.focusId
    ? findLeaf(ws.root, ws.focusId)?.app.title ?? ''
    : '';
  $: cpu = sample?.cpu_pct ?? null;
  $: memPct =
    sample?.mem && sample.mem.total > 0
      ? Math.round(((sample.mem.total - sample.mem.available) / sample.mem.total) * 100)
      : null;
  $: gpu = sample?.gpu?.util ?? null;
  $: vramPct =
    sample?.gpu && sample.gpu.mem_total > 0
      ? Math.round((sample.gpu.mem_used / sample.gpu.mem_total) * 100)
      : null;
</script>

<header
  class="surface-blur absolute top-0 left-0 right-0 z-30 flex items-center px-3 select-none"
  style="height: var(--panel-height);"
>
  <!-- workspaces (hidden on mobile — the mobile dock provides workspace dots) -->
  <div class="hidden md:flex gap-1.5 items-center">
    {#each $wm.workspaces as w (w.id)}
      <button
        class="text-xs font-mono w-6 h-5 rounded-md grid place-items-center transition-colors"
        class:bg-accent={w.id === $wm.activeWs}
        class:text-bg={w.id === $wm.activeWs}
        class:text-muted={w.id !== $wm.activeWs}
        on:click={() => switchWorkspace(w.id)}
        title="Workspace {w.id}"
      >
        {w.id === 10 ? '0' : w.id}
        {#if !isEmpty(w) && w.id !== $wm.activeWs}
          <span class="absolute -mb-3 w-1 h-1 rounded-full bg-accent2"></span>
        {/if}
      </button>
    {/each}
  </div>

  <!-- focused window title -->
  <div class="flex-1 text-center text-xs text-muted truncate px-4">
    {focusedTitle}
  </div>

  <!-- system stats + clock -->
  <div class="flex items-center gap-3 text-xs font-mono text-muted">
    <!-- detailed stats hidden on mobile to avoid overflow -->
    {#if cpu !== null}
      <span class="hidden md:inline" title="CPU"><span class="text-accent">CPU</span> {cpu.toFixed(0)}%</span>
    {/if}
    {#if memPct !== null}
      <span class="hidden md:inline" title="Memory"><span class="text-accent">MEM</span> {memPct}%</span>
    {/if}
    {#if gpu !== null}
      <span class="hidden md:inline" title="GPU utilization"><span class="text-accent">GPU</span> {gpu.toFixed(0)}%</span>
    {/if}
    {#if vramPct !== null}
      <span class="hidden md:inline" title="VRAM used / total"><span class="text-accent">VRAM</span> {vramPct}%</span>
    {/if}
    <span
      class="hidden md:inline-block px-1.5 py-0.5 rounded-md text-[10px] uppercase tracking-wide text-bg bg-accent2/80"
      title="WM modifier — open the launcher (Ctrl+Space) and search 'modifier' to change"
    >
      {MODIFIER_LABEL[modifier]}
    </span>
    <span class="text-fg">{now}</span>
  </div>
</header>
