<script lang="ts">
  import { onDestroy, onMount } from 'svelte';
  import { openSysStream, type SysSample } from '$lib/api/sys';
  import type { AppInstance } from '$lib/wm/tree';

  export let app: AppInstance;
  void app;

  let sample: SysSample | null = null;
  let cpuHistory: number[] = [];
  let memHistory: number[] = [];
  let stream: ReturnType<typeof openSysStream> | null = null;

  const MAX = 60;

  function push(arr: number[], v: number | null): number[] {
    const next = arr.slice(arr.length >= MAX ? 1 : 0);
    next.push(v ?? 0);
    return next;
  }

  function spark(values: number[], w = 220, h = 40, max = 100): string {
    if (values.length === 0) return '';
    const dx = w / Math.max(1, MAX - 1);
    return values
      .map((v, i) => {
        const x = i * dx;
        const y = h - (v / max) * h;
        return `${i === 0 ? 'M' : 'L'} ${x.toFixed(1)} ${y.toFixed(1)}`;
      })
      .join(' ');
  }

  function fmtBytes(n: number): string {
    if (n < 1024) return `${n} B`;
    const units = ['KB', 'MB', 'GB', 'TB'];
    let i = -1;
    let v = n;
    while (v >= 1024 && i < units.length - 1) {
      v /= 1024;
      i += 1;
    }
    return `${v.toFixed(1)} ${units[i]}`;
  }

  onMount(() => {
    stream = openSysStream((s) => {
      sample = s;
      cpuHistory = push(cpuHistory, s.cpu_pct);
      const memPct =
        s.mem && s.mem.total > 0
          ? ((s.mem.total - s.mem.available) / s.mem.total) * 100
          : 0;
      memHistory = push(memHistory, memPct);
    });
  });

  onDestroy(() => stream?.close());

  $: cpuPath = spark(cpuHistory);
  $: memPath = spark(memHistory);
</script>

<div class="h-full w-full p-4 overflow-y-auto text-sm font-mono">
  <section class="mb-4">
    <header class="flex items-center justify-between mb-2">
      <h3 class="text-accent">CPU</h3>
      <span class="text-fg">{sample?.cpu_pct?.toFixed(1) ?? '–'}%</span>
    </header>
    <svg width="100%" height="42" viewBox="0 0 220 40" preserveAspectRatio="none" class="text-accent">
      <path d={cpuPath} fill="none" stroke="currentColor" stroke-width="1.5" />
    </svg>
  </section>

  <section class="mb-4">
    <header class="flex items-center justify-between mb-2">
      <h3 class="text-accent2">Memory</h3>
      {#if sample?.mem}
        <span class="text-fg">
          {fmtBytes(sample.mem.total - sample.mem.available)} / {fmtBytes(sample.mem.total)}
        </span>
      {:else}
        <span class="text-muted">–</span>
      {/if}
    </header>
    <svg width="100%" height="42" viewBox="0 0 220 40" preserveAspectRatio="none" class="text-accent2">
      <path d={memPath} fill="none" stroke="currentColor" stroke-width="1.5" />
    </svg>
  </section>

  {#if sample?.gpu}
    <section class="mb-4">
      <header class="flex items-center justify-between mb-2">
        <h3 class="text-ok">GPU</h3>
        <span class="text-fg">{sample.gpu.util.toFixed(0)}% · {sample.gpu.temp_c.toFixed(0)}°C</span>
      </header>
      <div class="text-muted text-xs">
        VRAM {fmtBytes(sample.gpu.mem_used)} / {fmtBytes(sample.gpu.mem_total)}
      </div>
    </section>
  {:else}
    <section class="text-muted text-xs">
      GPU stats land in Phase 1.5 (nvidia-smi via host SSH). Until then, only container CPU + memory are sampled.
    </section>
  {/if}

  {#if sample?.load}
    <section class="mt-4 text-muted text-xs">
      Load average: {sample.load.map((n) => n.toFixed(2)).join(' · ')}
    </section>
  {/if}
</div>
