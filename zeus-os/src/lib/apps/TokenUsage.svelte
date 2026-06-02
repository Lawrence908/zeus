<script lang="ts">
  import { onDestroy, onMount } from 'svelte';
  import type { AppInstance } from '$lib/wm/tree';
  import { importHistoric, loadUsage, type UsageResponse } from '$lib/api/usage';
  import { notify } from '$lib/notify/store';

  export let app: AppInstance;
  void app;

  let data: UsageResponse | null = null;
  let error = '';
  let sinceDays = 30;
  let providerFilter = '';
  let importInfo: { import_dir: string; found_files: string[] } | null = null;
  let timer: ReturnType<typeof setInterval> | null = null;

  // Catppuccin-ish palette so chart colors look intentional regardless of theme.
  const PROVIDER_COLORS: Record<string, string> = {
    anthropic: '#cba6f7',
    anthropic_haiku: '#b4befe',
    gemini_paid: '#f9e2af',
    groq: '#f38ba8',
    openrouter: '#fab387',
    ollama: '#a6e3a1',
    cursor: '#94e2d5',
    unknown: '#6c7086'
  };
  const colorFor = (p: string) => PROVIDER_COLORS[p] ?? PROVIDER_COLORS.unknown;

  async function refresh() {
    try {
      data = await loadUsage({
        bucket: 'day',
        since_days: sinceDays,
        provider: providerFilter || undefined
      });
      error = '';
    } catch (e) {
      error = String(e);
    }
  }

  onMount(async () => {
    await refresh();
    try {
      const i = await importHistoric();
      importInfo = { import_dir: i.import_dir, found_files: i.found_files };
    } catch {
      /* ignore */
    }
    timer = setInterval(refresh, 30_000);
  });

  onDestroy(() => {
    if (timer) clearInterval(timer);
  });

  function fmtTokens(n: number): string {
    if (n < 1000) return n.toString();
    if (n < 1_000_000) return (n / 1000).toFixed(1) + 'K';
    return (n / 1_000_000).toFixed(2) + 'M';
  }

  function fmtCost(c: number): string {
    if (c === 0) return '$0';
    if (c < 0.01) return '<$0.01';
    if (c < 1) return '$' + c.toFixed(2);
    return '$' + c.toFixed(2);
  }

  interface StackPoint {
    bucket: string;
    total: number;
    parts: { provider: string; tokens: number; from: number; to: number }[];
  }

  $: stacked = (() => {
    if (!data) return { points: [] as StackPoint[], providers: [] as string[], max: 0 };
    const byBucket = new Map<string, Map<string, number>>();
    const providers = new Set<string>();
    for (const p of data.series) {
      providers.add(p.provider);
      const tokens = p.tokens_in + p.tokens_out;
      const b = byBucket.get(p.bucket) ?? new Map<string, number>();
      b.set(p.provider, (b.get(p.provider) ?? 0) + tokens);
      byBucket.set(p.bucket, b);
    }
    const providerList = [...providers].sort();
    const buckets = [...byBucket.keys()].sort();
    let max = 0;
    const points: StackPoint[] = buckets.map((bucket) => {
      const b = byBucket.get(bucket)!;
      let cursor = 0;
      const parts: StackPoint['parts'] = [];
      for (const p of providerList) {
        const v = b.get(p) ?? 0;
        parts.push({ provider: p, tokens: v, from: cursor, to: cursor + v });
        cursor += v;
      }
      if (cursor > max) max = cursor;
      return { bucket, total: cursor, parts };
    });
    return { points, providers: providerList, max };
  })();

  // Render the chart as flexbox bars (one column per bucket, segments stacked).
  $: chartWidth = Math.max(280, stacked.points.length * 18);
</script>

<div class="h-full w-full flex flex-col font-mono text-xs overflow-y-auto">
  <!-- Headline cards -->
  <div class="px-4 py-3 grid grid-cols-2 lg:grid-cols-4 gap-3 border-b border-border/40">
    {#if data}
      <div class="bg-surface2/40 rounded p-3">
        <p class="text-muted text-[10px] uppercase">Tokens · {data.window.since_days}d</p>
        <p class="text-fg text-xl">{fmtTokens(data.totals.tokens)}</p>
        <p class="text-muted text-[10px]">{fmtTokens(data.totals.tokens_in)} in · {fmtTokens(data.totals.tokens_out)} out</p>
      </div>
      <div class="bg-surface2/40 rounded p-3">
        <p class="text-muted text-[10px] uppercase">Cost · {data.window.since_days}d</p>
        <p class="text-fg text-xl">{fmtCost(data.totals.cost_usd)}</p>
        <p class="text-muted text-[10px]">{data.totals.calls} calls</p>
      </div>
      <div class="bg-surface2/40 rounded p-3">
        <p class="text-muted text-[10px] uppercase">Top provider</p>
        <p class="text-fg text-sm truncate">{data.by_provider[0]?.provider ?? '–'}</p>
        <p class="text-muted text-[10px]">{fmtTokens(data.by_provider[0]?.tokens ?? 0)} tokens</p>
      </div>
      <div class="bg-surface2/40 rounded p-3">
        <p class="text-muted text-[10px] uppercase">Top model</p>
        <p class="text-fg text-sm truncate">{data.by_model[0]?.model ?? '–'}</p>
        <p class="text-muted text-[10px]">{fmtCost(data.by_model[0]?.cost_usd ?? 0)}</p>
      </div>
    {/if}
  </div>

  <!-- Filters -->
  <div class="px-4 py-2 border-b border-border/40 flex items-center gap-3 text-[10px] text-muted">
    <label>
      Window:
      <select class="bg-surface text-fg ml-1 rounded p-0.5 border border-border/40" bind:value={sinceDays} on:change={refresh}>
        <option value={1}>1 day</option>
        <option value={7}>7 days</option>
        <option value={30}>30 days</option>
        <option value={90}>90 days</option>
        <option value={365}>1 year</option>
        <option value={3650}>all time</option>
      </select>
    </label>
    <label>
      Provider:
      <select class="bg-surface text-fg ml-1 rounded p-0.5 border border-border/40" bind:value={providerFilter} on:change={refresh}>
        <option value="">all</option>
        {#each data?.by_provider ?? [] as p}
          <option value={p.provider}>{p.provider}</option>
        {/each}
      </select>
    </label>
    <button class="ml-auto text-muted hover:text-fg" on:click={refresh}>refresh</button>
  </div>

  {#if error}<p class="text-err px-4 py-2">{error}</p>{/if}

  <!-- Stacked chart -->
  <section class="px-4 py-3 border-b border-border/40">
    <h3 class="text-accent text-sm mb-2">Daily token volume by provider</h3>
    {#if stacked.points.length > 0}
      <div class="flex items-end gap-1 h-40 overflow-x-auto" style="min-width: {chartWidth}px;">
        {#each stacked.points as pt (pt.bucket)}
          <div class="flex flex-col items-center flex-shrink-0" style="width: 16px;">
            <div class="relative w-full" style="height: 130px;">
              {#each pt.parts as seg (seg.provider)}
                {#if seg.tokens > 0}
                  <div
                    class="absolute left-0 right-0"
                    style="background: {colorFor(seg.provider)}; bottom: {(seg.from / stacked.max) * 100}%; height: {((seg.to - seg.from) / stacked.max) * 100}%;"
                    title="{seg.provider}: {fmtTokens(seg.tokens)} on {pt.bucket}"
                  ></div>
                {/if}
              {/each}
            </div>
            <span class="text-[8px] text-muted mt-0.5 rotate-45 origin-top-left whitespace-nowrap" style="height: 24px;">
              {pt.bucket.slice(5)}
            </span>
          </div>
        {/each}
      </div>
      <div class="flex flex-wrap gap-3 mt-3 text-[10px] text-muted">
        {#each stacked.providers as p}
          <span class="flex items-center gap-1">
            <span class="inline-block w-2.5 h-2.5 rounded-sm" style="background: {colorFor(p)};"></span>
            {p}
          </span>
        {/each}
      </div>
    {:else}
      <p class="text-muted">No usage rows in window. Try asking Zeus something or extend the window.</p>
    {/if}
  </section>

  <!-- Per-provider + per-caller tables -->
  <div class="grid lg:grid-cols-2 gap-4 px-4 py-3 border-b border-border/40">
    <div>
      <h4 class="text-accent text-[11px] uppercase mb-1">By provider</h4>
      <table class="w-full">
        <thead class="text-muted text-[10px] text-left">
          <tr><th>Provider</th><th class="text-right">Tokens</th><th class="text-right">Cost</th><th class="text-right">Calls</th></tr>
        </thead>
        <tbody>
          {#each data?.by_provider ?? [] as r}
            <tr class="border-t border-border/20">
              <td class="py-1 text-fg">
                <span class="inline-block w-2 h-2 rounded-sm mr-1" style="background: {colorFor(r.provider!)};"></span>
                {r.provider}
              </td>
              <td class="py-1 text-right text-fg">{fmtTokens(r.tokens)}</td>
              <td class="py-1 text-right text-fg">{fmtCost(r.cost_usd)}</td>
              <td class="py-1 text-right text-muted">{r.calls}</td>
            </tr>
          {/each}
        </tbody>
      </table>
    </div>
    <div>
      <h4 class="text-accent text-[11px] uppercase mb-1">Top callers</h4>
      <table class="w-full">
        <thead class="text-muted text-[10px] text-left">
          <tr><th>Caller</th><th class="text-right">Tokens</th><th class="text-right">Cost</th></tr>
        </thead>
        <tbody>
          {#each (data?.by_caller ?? []).slice(0, 10) as r}
            <tr class="border-t border-border/20">
              <td class="py-1 text-fg truncate" style="max-width: 200px;">{r.caller}</td>
              <td class="py-1 text-right text-fg">{fmtTokens(r.tokens)}</td>
              <td class="py-1 text-right text-fg">{fmtCost(r.cost_usd)}</td>
            </tr>
          {/each}
        </tbody>
      </table>
    </div>
  </div>

  <!-- Historical import scaffold -->
  <section class="px-4 py-3">
    <h3 class="text-accent text-sm mb-1">Historical import</h3>
    <p class="text-muted leading-relaxed">
      This view tracks usage going forward. To backfill past Claude and Cursor spend,
      drop CSV exports into <code class="text-fg">{importInfo?.import_dir ?? '~/.zeus/usage-imports/'}</code>
      and an importer (zeus/core/usage_import.py) will fold them in. The parser is stubbed today —
      see <code>zeus/docs/token-usage.md</code> for the expected schema.
    </p>
    {#if importInfo && importInfo.found_files.length > 0}
      <p class="text-fg text-[11px] mt-2">Pending imports: {importInfo.found_files.join(', ')}</p>
    {:else}
      <p class="text-muted text-[10px] mt-2">No files dropped yet.</p>
    {/if}
    <button
      class="mt-2 text-[10px] px-2 py-1 border border-accent text-accent rounded hover:bg-accent hover:text-bg"
      on:click={async () => {
        try {
          const r = await importHistoric();
          notify({ title: 'Importer', body: r.note, kind: 'info', ttlMs: 4000 });
          importInfo = { import_dir: r.import_dir, found_files: r.found_files };
        } catch (e) {
          notify({ title: 'Import failed', body: String(e).slice(0, 160), kind: 'err' });
        }
      }}
    >
      Check import dir
    </button>
  </section>
</div>
