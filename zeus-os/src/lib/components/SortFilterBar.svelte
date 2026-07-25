<!-- src/lib/components/SortFilterBar.svelte — shared filter + sort strip.
     Used by the data-dense apps (Memories, Knowledge, Tools, Jobs) so they
     stop re-implementing the same input/select/direction cluster. All three
     control props are bindable; the `extra` slot hangs app-specific controls
     on the right edge. -->
<script lang="ts" context="module">
  export interface SortOption {
    value: string;
    label: string;
  }
</script>

<script lang="ts">
  import { createEventDispatcher } from 'svelte';

  export let query = '';
  export let placeholder = 'filter…';
  export let sortOptions: SortOption[] = [];
  export let sortBy = '';
  export let sortDesc = false;
  export let total: number | null = null;

  // Apps with server-side search (e.g. Knowledge) listen for Enter to fire it.
  const dispatch = createEventDispatcher<{ submit: string }>();
</script>

<div class="flex items-center gap-2 px-3 py-1.5 border-b border-border/40 text-xs font-mono">
  <input
    class="flex-1 min-w-0 bg-surface rounded border border-border/50 px-2 py-0.5 outline-none text-fg placeholder:text-muted/50 focus:border-accent/70"
    {placeholder}
    bind:value={query}
    on:keydown={(e) => e.key === 'Enter' && dispatch('submit', query)}
  />
  {#if sortOptions.length}
    <select
      class="bg-surface text-muted rounded border border-border/50 px-1 py-0.5 outline-none shrink-0"
      bind:value={sortBy}
      title="Sort by"
    >
      {#each sortOptions as o (o.value)}
        <option value={o.value}>{o.label}</option>
      {/each}
    </select>
    <button
      class="text-muted hover:text-fg shrink-0 px-1"
      on:click={() => (sortDesc = !sortDesc)}
      title="Toggle sort direction"
    >{sortDesc ? '↓' : '↑'}</button>
  {/if}
  {#if total !== null}
    <span class="text-muted/60 shrink-0">{total}</span>
  {/if}
  <slot name="extra" />
</div>
