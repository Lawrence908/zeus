<script lang="ts">
  import { onDestroy, onMount } from 'svelte';
  import type { AppInstance } from '$lib/wm/tree';
  import { jsonFetch } from '$lib/api/base';

  export let app: AppInstance;
  void app;

  interface Event {
    summary?: string;
    start?: string;
    end?: string;
    location?: string;
    description?: string;
    source?: string;
  }

  interface TodayResponse {
    date: string;
    events: Event[];
    error?: string;
  }

  let data: TodayResponse | null = null;
  let error = '';
  let loading = true;
  let lastFetched = '';
  let timer: ReturnType<typeof setInterval> | null = null;

  async function refresh() {
    loading = true;
    try {
      data = await jsonFetch<TodayResponse>('/calendar/today');
      error = data.error ?? '';
      lastFetched = new Date().toLocaleTimeString();
    } catch (e) {
      error = String(e);
    } finally {
      loading = false;
    }
  }

  function fmtTime(s?: string): string {
    if (!s) return '';
    try {
      const d = new Date(s);
      if (Number.isNaN(d.getTime())) return s;
      return d.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    } catch {
      return s;
    }
  }

  onMount(() => {
    refresh();
    timer = setInterval(refresh, 5 * 60_000);
  });

  onDestroy(() => {
    if (timer) clearInterval(timer);
  });

  $: events = data?.events ?? [];
</script>

<div class="h-full w-full flex flex-col font-mono text-xs">
  <header class="px-3 py-2 border-b border-border/40 flex items-center gap-2">
    <h3 class="text-accent text-sm">Today</h3>
    <span class="text-muted text-[10px]">{data?.date ?? ''}</span>
    <span class="ml-auto text-muted text-[10px]">{events.length} events{loading ? ' · loading…' : ''} {lastFetched}</span>
  </header>

  {#if error}
    <div class="bg-warn/15 border-b border-warn/30 px-3 py-2 text-warn text-[11px]">
      {error}
      <p class="mt-1 text-[10px] text-muted">Calendar reads from ingested gcal facts — ensure ZEUS_GCAL_ENABLED is on and the gcal source has run via Iris.</p>
    </div>
  {/if}

  <div class="flex-1 overflow-y-auto">
    {#if events.length}
      <ul>
        {#each events as e, i}
          <li class="border-b border-border/20 px-3 py-2">
            <div class="flex items-baseline justify-between gap-2">
              <span class="text-fg">{e.summary ?? '(untitled)'}</span>
              <span class="text-muted text-[10px] whitespace-nowrap">{fmtTime(e.start)}{e.end ? ` – ${fmtTime(e.end)}` : ''}</span>
            </div>
            {#if e.location}
              <p class="text-muted text-[10px] mt-0.5">📍 {e.location}</p>
            {/if}
            {#if e.description}
              <p class="text-fg/80 text-[11px] mt-1 line-clamp-2 whitespace-pre-wrap">{e.description.slice(0, 240)}{e.description.length > 240 ? '…' : ''}</p>
            {/if}
            {#if e.source}
              <p class="text-muted text-[10px] mt-1 italic">{e.source}</p>
            {/if}
          </li>
        {/each}
      </ul>
    {:else if !loading}
      <p class="text-muted text-center mt-12 px-6">
        Nothing on the calendar for today, or gcal hasn't been ingested. Trigger via the Ingest app → Google Calendar.
      </p>
    {/if}
  </div>
</div>
