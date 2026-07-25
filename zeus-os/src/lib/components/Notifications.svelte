<script lang="ts">
  import { fly } from 'svelte/transition';
  import { cubicOut } from 'svelte/easing';

  import { toasts, dismiss, type ToastKind } from '$lib/notify/store';

  const kindAccent: Record<ToastKind, string> = {
    info: 'border-l-accent',
    ok: 'border-l-ok',
    warn: 'border-l-warn',
    err: 'border-l-err'
  };
</script>

<div
  class="absolute top-12 right-3 z-50 flex flex-col gap-2 pointer-events-none w-72"
  aria-live="polite"
  aria-atomic="false"
>
  {#each $toasts as t (t.id)}
    <button
      type="button"
      class="surface-blur text-left text-sm rounded-wm shadow-lg p-3 pointer-events-auto border border-border/40 border-l-4 {kindAccent[t.kind]}"
      style="background: rgb(var(--surface) / 0.92);"
      on:click={() => dismiss(t.id)}
      transition:fly={{ x: 280, duration: 200, easing: cubicOut }}
    >
      <p class="font-mono text-fg leading-tight">{t.title}</p>
      {#if t.body}
        <p class="text-xs text-muted mt-1 leading-snug">{t.body}</p>
      {/if}
    </button>
  {/each}
</div>
