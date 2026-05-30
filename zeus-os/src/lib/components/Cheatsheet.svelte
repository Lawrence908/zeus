<script lang="ts">
  import { fade, scale } from 'svelte/transition';
  import { cubicOut } from 'svelte/easing';

  export let open = false;

  const rows: [string, string][] = [
    ['Super + Return', 'Open Terminal'],
    ['Super + D / Ctrl + Space', 'Launcher'],
    ['Super + Shift + Q', 'Close window'],
    ['Super + F', 'Toggle floating'],
    ['Super + H / J / K / L', 'Focus left / down / up / right'],
    ['Super + Shift + H / J / K / L', 'Move window'],
    ['Super + V / S', 'Split vertical / horizontal'],
    ['Super + 1..0', 'Switch workspace'],
    ['Super + Shift + 1..0', 'Move window to workspace'],
    ['Super + R', 'Cycle theme'],
    ['Super + /', 'This cheatsheet']
  ];
</script>

{#if open}
  <div
    class="absolute inset-0 z-40 flex items-center justify-center"
    style="background: rgb(0 0 0 / 0.4); backdrop-filter: blur(6px);"
    role="presentation"
    on:click|self={() => (open = false)}
    transition:fade={{ duration: 120 }}
  >
    <div
      class="surface-blur rounded-2xl shadow-2xl w-[min(560px,92vw)] border border-border/40 p-6"
      transition:scale={{ duration: 220, start: 0.96, easing: cubicOut }}
    >
      <h2 class="text-lg font-mono mb-4 text-accent">Zeus OS — keybinds</h2>
      <table class="w-full text-sm font-mono">
        <tbody>
          {#each rows as [k, v]}
            <tr>
              <td class="py-1 pr-6 text-muted whitespace-nowrap">{k}</td>
              <td class="py-1 text-fg">{v}</td>
            </tr>
          {/each}
        </tbody>
      </table>
      <p class="mt-4 text-xs text-muted">
        Press <kbd>Esc</kbd> or click outside to dismiss.
      </p>
    </div>
  </div>
{/if}
