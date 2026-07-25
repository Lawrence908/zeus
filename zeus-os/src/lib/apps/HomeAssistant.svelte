<script lang="ts">
  import { onDestroy, onMount, tick } from 'svelte';
  import type { AppInstance } from '$lib/wm/tree';
  import { haConfig } from '$lib/api/integrations';
  import { mountIframe, unmountIframe } from './iframe-sessions';

  export let app: AppInstance;

  let url = '';
  let mode: 'direct' | 'proxy' = 'direct';
  let upstream = '';
  let error = '';
  let loading = true;
  let editing = false;
  let urlInput = '';
  let host: HTMLDivElement;
  // Collapsed by default once a URL is configured: the header is setup
  // chrome, not something you need while actually driving HA.
  let headerOpen = false;

  async function load() {
    loading = true;
    try {
      const c = await haConfig();
      url = c.url;
      mode = c.mode ?? 'direct';
      upstream = c.upstream ?? c.url;
      urlInput = upstream;
      error = '';
    } catch (e) {
      error = String(e);
    } finally {
      loading = false;
    }
  }

  onMount(async () => {
    await load();
    await tick();
    if (host && url) mountIframe(app.instanceId, host, url, 'Home Assistant');
  });

  // If url changes (e.g. user picks "change url"), rebind the iframe to the new src.
  $: if (host && url) {
    mountIframe(app.instanceId, host, url, 'Home Assistant');
  }

  onDestroy(() => {
    // Detach (not dispose) — registry keeps the iframe alive across remount.
    unmountIframe(app.instanceId, host);
  });

  $: sameOrigin = (() => {
    if (!url || typeof window === 'undefined') return false;
    try {
      const u = new URL(url, window.location.href);
      return u.origin === window.location.origin;
    } catch {
      return false;
    }
  })();
  void sameOrigin; // surfaced through openInNewTab below

  function openInNewTab() {
    // Open the *upstream* URL (the real HA) in a new tab so the user gets
    // the canonical login flow rather than the proxied origin.
    const target = mode === 'proxy' ? upstream : url;
    if (target) window.open(target, '_blank', 'noopener');
  }
</script>

<div class="h-full w-full flex flex-col font-mono text-xs relative">
  {#if headerOpen || !url || error}
    <header class="px-3 py-1.5 border-b border-border/40 flex items-center gap-2">
      <h3 class="text-accent text-sm">Home Assistant</h3>
      {#if mode === 'proxy'}
        <span class="text-[10px] px-1.5 py-0.5 rounded bg-ok/20 text-ok" title="Routed through Zeus reverse proxy with CF Access service-token headers">
          proxy · CF token
        </span>
        <span class="text-muted text-[10px] truncate">→ {upstream}</span>
      {:else}
        <span class="text-muted text-[10px] truncate">{url || '(no url configured)'}</span>
      {/if}
      <div class="ml-auto flex gap-1">
        <button class="text-[10px] px-2 py-0.5 border border-border/60 rounded" on:click={() => (editing = !editing)}>
          {editing ? 'cancel' : 'change url'}
        </button>
        {#if url}
          <button class="text-[10px] px-2 py-0.5 border border-accent text-accent rounded" on:click={openInNewTab}>
            open ↗
          </button>
          <button
            class="text-[10px] px-2 py-0.5 border border-border/60 rounded text-muted hover:text-fg"
            on:click={() => (headerOpen = false)}
            title="Hide header"
          >hide ▴</button>
        {/if}
      </div>
    </header>
  {:else}
    <button
      class="absolute top-1 right-1 z-10 text-[10px] px-1.5 py-0.5 rounded text-muted/60 hover:text-fg surface-blur"
      style="background: rgb(var(--surface) / 0.7);"
      on:click={() => (headerOpen = true)}
      title="Show Home Assistant panel controls"
    >⚙</button>
  {/if}

  {#if editing}
    <div class="px-3 py-2 border-b border-border/40 flex items-center gap-2 bg-surface2/30">
      <input
        bind:value={urlInput}
        placeholder="https://homeassistant.…"
        class="flex-1 bg-transparent border-b border-border/40 outline-none text-fg"
      />
      <button
        class="text-[10px] px-2 py-0.5 border border-accent text-accent rounded"
        on:click={() => {
          url = urlInput;
          editing = false;
        }}
      >
        set
      </button>
      <span class="text-muted text-[10px]">runtime-only · persistent change requires ZEUS_OS_HA_URL in .env</span>
    </div>
  {/if}

  {#if error}
    <div class="bg-err/20 border-b border-err/40 px-3 py-2 text-err">{error}</div>
  {/if}

  {#if loading}
    <p class="text-muted px-3 py-2">loading…</p>
  {:else if url}
    <div bind:this={host} class="flex-1 min-h-0 w-full"></div>
  {:else}
    <div class="flex-1 grid place-items-center text-muted text-center px-6">
      <div>
        <p>No Home Assistant URL configured.</p>
        <p class="text-[10px] mt-2">Set <code class="text-fg">ZEUS_OS_HA_URL</code> in <code class="text-fg">zeus/.env</code> and restart zeus-core, or use "change url" above for a one-session override.</p>
      </div>
    </div>
  {/if}
</div>
