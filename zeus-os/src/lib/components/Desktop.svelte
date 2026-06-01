<script lang="ts">
  import { onMount } from 'svelte';
  import { fade } from 'svelte/transition';
  import { cubicOut } from 'svelte/easing';

  import Window from './Window.svelte';
  import Panel from './Panel.svelte';
  import FloatingWindow from './FloatingWindow.svelte';
  import { activeWorkspace, floating, leaves, rects, viewport, gap } from '$lib/wm/store';
  import type { ModifierMode } from '$lib/wm/keybinds';

  export let modifier: ModifierMode = 'Meta';

  // Lay out windows inside the area below the top panel, with the configured
  // gap on all sides. Recompute on resize.
  let outer: HTMLDivElement;

  function updateViewport() {
    if (!outer) return;
    const r = outer.getBoundingClientRect();
    const PANEL_H = 30;
    const G = $gap;
    viewport.set({
      x: G,
      y: PANEL_H + G,
      w: Math.max(0, r.width - G * 2),
      h: Math.max(0, r.height - PANEL_H - G * 2)
    });
  }

  onMount(() => {
    updateViewport();
    const ro = new ResizeObserver(updateViewport);
    if (outer) ro.observe(outer);
    return () => ro.disconnect();
  });
</script>

<div bind:this={outer} class="relative h-full w-full overflow-hidden">
  <Panel {modifier} />
  {#key $activeWorkspace.id}
    <div
      class="absolute inset-0"
      in:fade={{ duration: 200, easing: cubicOut }}
    >
      {#each $leaves as leaf (leaf.id)}
        {#if $rects[leaf.id]}
          <Window
            {leaf}
            rect={$rects[leaf.id]}
            focused={leaf.id === $activeWorkspace.focusId}
          />
        {/if}
      {/each}
      {#each $floating as win (win.id)}
        <FloatingWindow {win} focused={win.id === $activeWorkspace.focusId} />
      {/each}
      {#if $leaves.length === 0 && $floating.length === 0}
        <div class="absolute inset-0 flex items-center justify-center pointer-events-none">
          <div class="text-center select-none">
            <p class="text-fg/30 text-2xl font-mono">Workspace {$activeWorkspace.id}</p>
            <p class="text-muted/60 text-sm mt-2">
              <kbd class="font-mono">Super</kbd> +
              <kbd class="font-mono">Return</kbd> &nbsp;Terminal &nbsp;·&nbsp;
              <kbd class="font-mono">Super</kbd> +
              <kbd class="font-mono">D</kbd> &nbsp;Launcher
            </p>
          </div>
        </div>
      {/if}
    </div>
  {/key}
</div>
