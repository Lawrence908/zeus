<!-- src/lib/components/ConfirmHost.svelte — singleton renderer for confirmDialog().
     Mounted once in +page.svelte. Esc cancels, Enter confirms. -->
<script lang="ts">
  import { fade, scale } from 'svelte/transition';
  import { cubicOut } from 'svelte/easing';
  import { pendingConfirm } from './confirm';

  function onKey(ev: KeyboardEvent) {
    if (!$pendingConfirm) return;
    if (ev.key === 'Escape') {
      ev.preventDefault();
      ev.stopPropagation();
      $pendingConfirm.resolve(false);
    } else if (ev.key === 'Enter') {
      ev.preventDefault();
      ev.stopPropagation();
      $pendingConfirm.resolve(true);
    }
  }
</script>

<svelte:window on:keydown|capture={onKey} />

{#if $pendingConfirm}
  <div
    class="fixed inset-0 z-[200] grid place-items-center"
    style="background: rgb(0 0 0 / 0.45); backdrop-filter: blur(3px);"
    transition:fade={{ duration: 120 }}
    on:mousedown={() => $pendingConfirm?.resolve(false)}
    role="presentation"
  >
    <div
      class="window-shell focused w-80 p-4 font-mono"
      transition:scale={{ duration: 160, start: 0.94, easing: cubicOut }}
      on:mousedown|stopPropagation
      role="alertdialog"
      aria-label={$pendingConfirm.title}
    >
      <h3 class="text-sm text-fg mb-1">{$pendingConfirm.title}</h3>
      <p class="text-xs text-muted mb-4 whitespace-pre-wrap">{$pendingConfirm.message}</p>
      <div class="flex justify-end gap-2 text-xs">
        <button
          class="px-3 py-1 rounded border border-border/60 text-muted hover:text-fg"
          on:click={() => $pendingConfirm?.resolve(false)}
        >Cancel</button>
        <button
          class="px-3 py-1 rounded {$pendingConfirm.danger
            ? 'bg-err text-bg hover:opacity-90'
            : 'bg-accent text-bg hover:opacity-90'}"
          on:click={() => $pendingConfirm?.resolve(true)}
        >{$pendingConfirm.confirmLabel}</button>
      </div>
    </div>
  </div>
{/if}
