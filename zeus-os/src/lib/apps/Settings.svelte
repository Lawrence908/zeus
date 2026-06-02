<script lang="ts">
  import { onMount } from 'svelte';
  import type { AppInstance } from '$lib/wm/tree';
  import {
    getActiveModel,
    getTelegramStatus,
    listBenchmarks,
    listModels,
    setActiveModel,
    type ActiveModel,
    type ModelInfo
  } from '$lib/api/models';
  import { notify } from '$lib/notify/store';

  export let app: AppInstance;
  void app;

  let active: ActiveModel | null = null;
  let models: ModelInfo[] = [];
  let provider = '';
  let benchmarks: Record<string, unknown> | null = null;
  let telegram: Record<string, unknown> | null = null;
  let switching = false;
  let error = '';

  async function refresh() {
    try {
      const [a, m] = await Promise.all([getActiveModel(), listModels()]);
      active = a;
      provider = m.provider;
      models = m.models;
      error = '';
    } catch (e) {
      error = String(e);
    }
    try { benchmarks = await listBenchmarks(); } catch { benchmarks = null; }
    try { telegram = await getTelegramStatus(); } catch { telegram = null; }
  }

  async function pickModel(name: string) {
    if (!active || active.model === name || switching) return;
    switching = true;
    try {
      active = await setActiveModel(name);
      notify({ title: 'Model active', body: name, kind: 'ok', ttlMs: 2200 });
    } catch (e) {
      notify({ title: 'Switch failed', body: String(e).slice(0, 160), kind: 'err' });
    } finally {
      switching = false;
    }
  }

  function fmtSize(b?: number | null): string {
    if (!b) return '';
    const gb = b / (1024 ** 3);
    if (gb >= 1) return gb.toFixed(2) + ' GB';
    return (b / (1024 ** 2)).toFixed(0) + ' MB';
  }

  onMount(refresh);
</script>

<div class="h-full w-full overflow-y-auto p-4 font-mono text-xs space-y-5">
  {#if error}<p class="text-err">{error}</p>{/if}

  <!-- Active model + model list -->
  <section>
    <h3 class="text-accent text-sm mb-2">Active model</h3>
    {#if active}
      <p class="text-fg">
        <span class="text-muted">{active.provider}</span> · {active.model}
        {#if active.gpu_available !== undefined}
          <span class="text-[10px] {active.gpu_available ? 'text-ok' : 'text-warn'} ml-2">
            GPU {active.gpu_available ? 'available' : 'cpu only'}
          </span>
        {/if}
      </p>
    {:else}
      <p class="text-muted">loading…</p>
    {/if}

    <div class="mt-3">
      <p class="text-muted text-[10px] uppercase mb-1">Available ({provider})</p>
      <ul class="space-y-1">
        {#each models as m (m.name)}
          <li>
            <button
              class="w-full text-left flex items-center justify-between px-2 py-1 rounded hover:bg-surface2/60"
              class:bg-surface2={active?.model === m.name}
              disabled={switching}
              on:click={() => pickModel(m.name)}
            >
              <div>
                <p class="text-fg">{m.name}</p>
                <p class="text-muted text-[10px]">
                  {m.parameter_size || ''} {m.quantization_level || ''} {m.family || ''}
                </p>
              </div>
              <span class="text-muted text-[10px]">{fmtSize(m.size)}</span>
            </button>
          </li>
        {:else}
          <li class="text-muted text-[11px]">No models found. If you're in dev mode (ZEUS_LLM=claude) this lists Claude options instead of Ollama.</li>
        {/each}
      </ul>
    </div>
  </section>

  <!-- Benchmarks -->
  <section>
    <h3 class="text-accent text-sm mb-2">Benchmarks</h3>
    {#if benchmarks && Object.keys(benchmarks).length}
      <details>
        <summary class="text-muted cursor-pointer text-[11px]">raw results</summary>
        <pre class="mt-2 text-[10px] text-fg whitespace-pre-wrap overflow-x-auto">{JSON.stringify(benchmarks, null, 2).slice(0, 1500)}</pre>
      </details>
    {:else}
      <p class="text-muted text-[11px]">
        No benchmark data yet. Run <code class="text-fg">python -m zeus.bench</code> on the host or
        <code class="text-fg">POST /models/benchmarks/run</code> to populate.
      </p>
    {/if}
  </section>

  <!-- Telegram bridge -->
  <section>
    <h3 class="text-accent text-sm mb-2">Telegram bridge</h3>
    {#if telegram}
      <pre class="text-[10px] text-fg whitespace-pre-wrap">{JSON.stringify(telegram, null, 2)}</pre>
    {:else}
      <p class="text-muted text-[11px]">Bridge status unavailable.</p>
    {/if}
  </section>

  <!-- WM-level prefs note -->
  <section>
    <h3 class="text-accent text-sm mb-2">Window manager</h3>
    <p class="text-muted text-[11px] leading-relaxed">
      Theme and modifier-key (Super / Alt / Ctrl+Alt) live in the launcher (Ctrl+Space → search "theme" / "modifier"). Persisted to
      <code class="text-fg">~/.zeus/zeus-os/config.json</code>.
    </p>
  </section>
</div>
