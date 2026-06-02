<script lang="ts">
  import { fade, scale } from 'svelte/transition';
  import { cubicOut } from 'svelte/easing';
  import { MODIFIER_LABEL, type ModifierMode } from '$lib/wm/keybinds';

  export let open = false;
  export let modifier: ModifierMode = 'Meta';

  $: mod = MODIFIER_LABEL[modifier];
  $: rows = [
    [`${mod} + Return`, 'Open Terminal'],
    [`${mod} + D  /  Ctrl + Space`, 'Launcher'],
    [`${mod} + Shift + Q`, 'Close window'],
    [`${mod} + F`, 'Toggle floating'],
    [`${mod} + H / J / K / L`, 'Focus left / down / up / right'],
    [`${mod} + Shift + H / J / K / L`, 'Move window'],
    [`${mod} + V / S`, 'Split vertical / horizontal'],
    [`${mod} + 1..0`, 'Switch workspace'],
    [`${mod} + Shift + 1..0`, 'Move window to workspace'],
    [`${mod} + R`, 'Cycle theme'],
    [`${mod} + /`, 'This cheatsheet']
  ] satisfies [string, string][];
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
      <h2 class="text-lg font-mono mb-1 text-accent">Zeus OS — keybinds</h2>
      <p class="text-xs text-muted mb-3 font-mono">
        Modifier: <span class="text-fg">{mod}</span> · change it from the launcher (search "modifier")
      </p>
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
