<script lang="ts">
  import type { VaultNode } from '$lib/api/obsidian';

  export let node: VaultNode;
  export let openFolders: Record<string, boolean>;
  export let currentPath: string | null;
  export let toggle: (path: string) => void;
  export let pick: (path: string) => void;
  export let depth: number = 0;

  $: indent = depth * 12;
</script>

{#if node.kind === 'dir'}
  <div>
    <button
      class="w-full text-left px-2 py-0.5 hover:bg-surface2/60 text-fg flex items-center"
      style:padding-left="{indent + 8}px"
      on:click={() => toggle(node.path)}
    >
      <span class="inline-block w-3 text-muted">{openFolders[node.path] ? '▾' : '▸'}</span>
      <span class="ml-1 truncate">{node.name}</span>
    </button>
    {#if openFolders[node.path]}
      {#each node.children ?? [] as child (child.path)}
        <svelte:self
          node={child}
          {openFolders}
          {currentPath}
          {toggle}
          {pick}
          depth={depth + 1}
        />
      {/each}
    {/if}
  </div>
{:else}
  <button
    class="w-full text-left px-2 py-0.5 hover:bg-surface2/60 truncate flex items-center"
    class:text-accent={currentPath === node.path}
    class:text-fg={currentPath !== node.path}
    style:padding-left="{indent + 8}px"
    on:click={() => node.kind === 'doc' && pick(node.path)}
  >
    <span class="inline-block w-3 text-muted text-[10px]">{node.kind === 'doc' ? '·' : node.kind === 'image' ? '🖼' : '·'}</span>
    <span class="ml-1 truncate">{node.name}</span>
  </button>
{/if}
