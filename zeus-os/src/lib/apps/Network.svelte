<script lang="ts">
  import { onDestroy, onMount } from 'svelte';
  import type { AppInstance } from '$lib/wm/tree';
  import { hostNetwork, type HostNetworkResponse } from '$lib/api/host';

  export let app: AppInstance;
  void app;

  let data: HostNetworkResponse | null = null;
  let error = '';
  let lastFetched = '';
  let timer: ReturnType<typeof setInterval> | null = null;

  async function refresh() {
    try {
      data = await hostNetwork();
      error = data.tailscale.ok ? '' : data.tailscale.error ?? '';
      lastFetched = new Date().toLocaleTimeString();
    } catch (e) {
      error = String(e);
    }
  }

  function fmtBytes(n?: number): string {
    if (!n) return '0';
    if (n < 1024) return `${n} B`;
    if (n < 1_048_576) return `${(n / 1024).toFixed(0)} KB`;
    if (n < 1_073_741_824) return `${(n / 1_048_576).toFixed(1)} MB`;
    return `${(n / 1_073_741_824).toFixed(2)} GB`;
  }

  function fmtAgo(ts?: string): string {
    if (!ts) return '';
    try {
      const ms = Date.now() - new Date(ts).getTime();
      const s = Math.floor(ms / 1000);
      if (s < 60) return `${s}s ago`;
      if (s < 3600) return `${Math.floor(s / 60)}m ago`;
      if (s < 86400) return `${Math.floor(s / 3600)}h ago`;
      return `${Math.floor(s / 86400)}d ago`;
    } catch {
      return ts;
    }
  }

  onMount(() => {
    refresh();
    timer = setInterval(refresh, 10_000);
  });

  onDestroy(() => {
    if (timer) clearInterval(timer);
  });

  $: peers = data?.tailscale.peers ?? [];
  $: onlinePeers = peers.filter((p) => p.online).length;
</script>

<div class="h-full w-full overflow-y-auto p-4 font-mono text-xs space-y-5">
  {#if error}
    <div class="bg-warn/15 border border-warn/30 rounded px-3 py-2 text-warn">{error}</div>
  {/if}

  <header>
    <h3 class="text-accent text-sm">Network</h3>
    <p class="text-muted text-[10px]">{lastFetched ? `refreshed ${lastFetched}` : 'loading…'}</p>
  </header>

  {#if data}
    <!-- Tailscale self -->
    <section>
      <h4 class="text-accent text-[11px] uppercase mb-1">This host</h4>
      {#if data.tailscale.self?.ip}
        <p class="text-fg">{data.tailscale.self.hostname} <span class="text-muted">·</span> {data.tailscale.self.ip}</p>
        <p class="text-muted text-[10px]">{data.tailscale.self.dns_name} · {data.tailscale.self.os}</p>
      {:else}
        <p class="text-muted text-[11px]">Tailscale: not connected (or `tailscale status --json` unavailable).</p>
      {/if}
    </section>

    <!-- Peers -->
    <section>
      <h4 class="text-accent text-[11px] uppercase mb-1">
        Tailscale peers <span class="text-muted">({onlinePeers} online / {peers.length})</span>
      </h4>
      {#if peers.length}
        <table class="w-full">
          <thead class="text-muted text-[10px] text-left">
            <tr><th>Host</th><th>IP</th><th>OS</th><th class="text-right">RX</th><th class="text-right">TX</th><th class="text-right">seen</th></tr>
          </thead>
          <tbody>
            {#each peers as p (p.dns_name ?? p.ip ?? p.hostname)}
              <tr class="border-t border-border/20">
                <td class="py-1">
                  <span class:text-ok={p.online} class:text-muted={!p.online}>●</span>
                  <span class="text-fg ml-1">{p.hostname ?? '?'}</span>
                </td>
                <td class="py-1 text-fg/80">{p.ip ?? '–'}</td>
                <td class="py-1 text-muted">{p.os ?? ''}</td>
                <td class="py-1 text-right text-muted">{fmtBytes(p.rx_bytes)}</td>
                <td class="py-1 text-right text-muted">{fmtBytes(p.tx_bytes)}</td>
                <td class="py-1 text-right text-muted">{p.online ? 'now' : fmtAgo(p.last_seen)}</td>
              </tr>
            {/each}
          </tbody>
        </table>
      {:else if data.tailscale.raw}
        <pre class="text-[10px] text-fg/80 whitespace-pre-wrap">{data.tailscale.raw.slice(0, 1200)}</pre>
      {:else}
        <p class="text-muted text-[11px]">No peers reported.</p>
      {/if}
    </section>

    <!-- Local interfaces -->
    <section>
      <h4 class="text-accent text-[11px] uppercase mb-1">Local interfaces</h4>
      {#if data.interfaces.length}
        <table class="w-full">
          <thead class="text-muted text-[10px] text-left">
            <tr><th>Interface</th><th>State</th><th>Addrs</th><th>MAC</th><th class="text-right">MTU</th></tr>
          </thead>
          <tbody>
            {#each data.interfaces as i (i.name)}
              <tr class="border-t border-border/20">
                <td class="py-1 text-fg">{i.name}</td>
                <td class="py-1" class:text-ok={i.state === 'UP'} class:text-muted={i.state !== 'UP'}>{i.state ?? ''}</td>
                <td class="py-1 text-fg/80">{i.addrs.join(', ')}</td>
                <td class="py-1 text-muted text-[10px]">{i.mac ?? ''}</td>
                <td class="py-1 text-right text-muted">{i.mtu ?? ''}</td>
              </tr>
            {/each}
          </tbody>
        </table>
      {:else}
        <p class="text-muted text-[11px]">No interface data.</p>
      {/if}
    </section>
  {/if}
</div>
