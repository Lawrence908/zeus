<script lang="ts">
  import { onMount } from 'svelte';
  import type { AppInstance } from '$lib/wm/tree';
  import { notify } from '$lib/notify/store';
  import { readCodeClip, renderMarkdown } from '$lib/markdown';
  import {
    resolveWikilink,
    vaultFile,
    vaultIndex,
    vaultTree,
    type VaultIndexResponse,
    type VaultNode
  } from '$lib/api/obsidian';
  import ObsidianTreeNode from './ObsidianTreeNode.svelte';

  export let app: AppInstance;
  void app;

  let tree: VaultNode | null = null;
  let index: VaultIndexResponse | null = null;
  // Plain object so reassignment (toggleFolder below) triggers Svelte
  // reactivity reliably. The empty string key represents the vault root.
  let openFolders: Record<string, boolean> = { '': true };
  let currentPath: string | null = null;
  let currentTitle = '';
  let body = '';
  let rawMode = false;
  let rawBody = '';
  let error = '';
  let filter = '';
  let history: string[] = [];
  let backstack: string[] = [];

  async function loadTree() {
    try {
      const t = await vaultTree();
      tree = t.tree;
    } catch (e) {
      error = `tree: ${String(e)}`;
    }
  }

  async function loadIndex() {
    try {
      index = await vaultIndex();
    } catch (e) {
      error = `index: ${String(e)}`;
    }
  }

  async function open(path: string, pushHistory = true) {
    try {
      const r = await vaultFile(path);
      if (pushHistory && currentPath) backstack.push(currentPath);
      currentPath = path;
      currentTitle = path.split('/').pop()!.replace(/\.(md|markdown)$/i, '');
      rawBody = r.content;
      body = r.rewritten;
      if (!history.includes(path)) history = [path, ...history].slice(0, 20);
      error = '';
      ensureAncestorsOpen(path);
    } catch (e) {
      notify({ title: 'Open failed', body: String(e).slice(0, 160), kind: 'err' });
    }
  }

  function ensureAncestorsOpen(path: string) {
    const segments = path.split('/');
    const next = { ...openFolders };
    let cur = '';
    for (let i = 0; i < segments.length - 1; i += 1) {
      cur = cur ? `${cur}/${segments[i]}` : segments[i];
      next[cur] = true;
    }
    openFolders = next;
  }

  function toggleFolder(path: string) {
    openFolders = { ...openFolders, [path]: !openFolders[path] };
  }

  function back() {
    const prev = backstack.pop();
    if (prev) open(prev, false);
  }

  // Click-delegate: rewrite obsidian:// and obsidian-asset:// hrefs so the
  // rendered markdown can intercept wikilinks without per-component bindings.
  function onContentClick(ev: MouseEvent) {
    const t = ev.target as HTMLElement | null;
    if (!t) return;
    const a = t.closest('a') as HTMLAnchorElement | null;
    if (a) {
      const href = a.getAttribute('href') ?? '';
      if (href.startsWith('obsidian://')) {
        ev.preventDefault();
        const target = decodeURIComponent(href.slice('obsidian://'.length));
        const resolved = resolveWikilink(target, index, currentPath);
        if (resolved) {
          open(resolved);
        } else {
          notify({ title: 'Wikilink not found', body: target, kind: 'warn', ttlMs: 2200 });
        }
        return;
      }
    }
    // Code-block copy buttons share the same delegated approach as Chat.
    const btn = t.closest('.code-copy-btn') as HTMLElement | null;
    if (btn) {
      const raw = readCodeClip(btn);
      if (raw === null) return;
      navigator.clipboard?.writeText(raw).then(
        () => {
          const orig = btn.textContent;
          btn.textContent = 'Copied';
          btn.classList.add('copied');
          setTimeout(() => {
            btn.textContent = orig ?? 'Copy';
            btn.classList.remove('copied');
          }, 1200);
        },
        () => notify({ title: 'Copy failed', kind: 'warn', ttlMs: 1500 })
      );
    }
  }

  // Image embeds (![[name.png]]) are rewritten to real /zeus-os/vault/asset
  // URLs server-side, so no DOM post-processing here. Styling lives in the
  // .obsidian-body CSS below.

  $: filteredTree = (() => {
    if (!tree) return null;
    const q = filter.trim().toLowerCase();
    if (!q) return tree;
    function rec(node: VaultNode): VaultNode | null {
      if (node.kind !== 'dir') {
        return node.name.toLowerCase().includes(q) ? node : null;
      }
      const children = (node.children ?? [])
        .map(rec)
        .filter((c): c is VaultNode => c !== null);
      if (children.length === 0) return null;
      return { ...node, children };
    }
    return rec(tree);
  })();

  onMount(() => {
    loadTree();
    loadIndex();
  });
</script>

<div class="h-full w-full flex font-mono text-xs">
  <!-- Tree sidebar -->
  <aside class="w-72 border-r border-border/40 flex flex-col">
    <header class="px-3 py-2 border-b border-border/40">
      <h3 class="text-accent text-sm">Obsidian vault</h3>
      <input
        bind:value={filter}
        placeholder="filter…"
        class="w-full mt-1 bg-transparent border-b border-border/40 outline-none text-[11px]"
      />
    </header>
    {#if error}<p class="text-err px-3 py-2 text-[11px]">{error}</p>{/if}
    <div class="flex-1 overflow-y-auto py-1">
      {#if filteredTree}
        {#each filteredTree.children ?? [] as node (node.path)}
          <ObsidianTreeNode
            {node}
            {openFolders}
            {currentPath}
            toggle={toggleFolder}
            pick={open}
            depth={0}
          />
        {/each}
      {:else}
        <p class="text-muted text-center mt-6 text-[11px]">loading…</p>
      {/if}
    </div>
  </aside>

  <!-- Document pane -->
  <section class="flex-1 flex flex-col min-w-0">
    {#if currentPath}
      <header class="px-3 py-1.5 border-b border-border/40 flex items-center justify-between">
        <div class="min-w-0">
          <h3 class="text-accent text-sm truncate">{currentTitle}</h3>
          <p class="text-muted text-[10px] truncate">{currentPath}</p>
        </div>
        <div class="flex gap-1">
          {#if backstack.length > 0}
            <button class="text-[10px] px-2 py-0.5 border border-border/60 rounded" on:click={back}>← back</button>
          {/if}
          <button
            class="text-[10px] px-2 py-0.5 border border-border/60 rounded"
            class:bg-accent={rawMode}
            class:text-bg={rawMode}
            on:click={() => (rawMode = !rawMode)}
          >
            {rawMode ? 'rendered' : 'raw'}
          </button>
        </div>
      </header>

      <div class="flex-1 overflow-y-auto p-4">
        {#if rawMode}
          <pre class="text-fg/90 whitespace-pre-wrap text-[11px] leading-relaxed">{rawBody}</pre>
        {:else}
          <div class="prose-chat obsidian-body" on:click={onContentClick} role="presentation">
            {@html renderMarkdown(body)}
          </div>
        {/if}
      </div>
    {:else}
      <div class="flex-1 grid place-items-center text-muted text-center px-6">
        <div>
          <p>Select a markdown file from the tree.</p>
          <p class="mt-1 text-[10px]">Wikilinks <code class="text-fg">[[Note]]</code> and embeds <code class="text-fg">![[image.png]]</code> resolve against the vault index.</p>
        </div>
      </div>
    {/if}
  </section>
</div>
