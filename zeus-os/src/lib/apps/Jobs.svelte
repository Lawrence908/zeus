<script lang="ts">
  import { onDestroy, onMount } from 'svelte';
  import type { AppInstance } from '$lib/wm/tree';
  import { notify } from '$lib/notify/store';
  import {
    createJob,
    deleteJob,
    getJob,
    listExecutors,
    listJobs,
    listUpcoming,
    runJobNow,
    setJobEnabled,
    type ExecutorInfo,
    type JobDefinition,
    type JobRun,
    type UpcomingFire
  } from '$lib/api/kronos';

  export let app: AppInstance;
  void app;

  let jobs: JobDefinition[] = [];
  let upcoming: UpcomingFire[] = [];
  let executors: ExecutorInfo[] = [];
  let runs: JobRun[] = [];
  let selectedJobId: string | null = null;
  let error = '';
  let timer: ReturnType<typeof setInterval> | null = null;

  // Create form state.
  let creating = false;
  let newJob = {
    id: '',
    name: '',
    cron: '',
    run_at: '',
    executor: '',
    args_json: '{}'
  };

  async function refreshList() {
    try {
      const [j, u] = await Promise.all([listJobs(), listUpcoming()]);
      jobs = Array.isArray(j) ? j : [];
      upcoming = Array.isArray(u) ? u : [];
      error = '';
    } catch (e) {
      error = String(e);
    }
  }

  async function refreshSelected() {
    if (!selectedJobId) return;
    try {
      const detail = await getJob(selectedJobId);
      runs = detail.runs ?? [];
    } catch (e) {
      error = String(e);
    }
  }

  async function loadExecutors() {
    try {
      executors = await listExecutors();
    } catch {
      executors = [];
    }
  }

  function pickJob(id: string) {
    selectedJobId = id;
    refreshSelected();
  }

  async function submitNew(ev: SubmitEvent) {
    ev.preventDefault();
    let params: Record<string, unknown> = {};
    try {
      params = JSON.parse(newJob.args_json || '{}');
    } catch {
      notify({ title: 'Params JSON invalid', kind: 'err' });
      return;
    }
    if (!newJob.id || !newJob.executor) {
      notify({ title: 'Need at least id + executor', kind: 'warn' });
      return;
    }
    if (!newJob.cron && !newJob.run_at) {
      notify({ title: 'Need cron OR run_at', kind: 'warn' });
      return;
    }
    try {
      const def = await createJob({
        id: newJob.id,
        name: newJob.name || newJob.id,
        schedule: {
          cron: newJob.cron || null,
          timezone: 'UTC',
          run_at: newJob.run_at || null
        },
        executor: newJob.executor,
        params,
        enabled: true
      });
      notify({ title: 'Job created', body: def.id, kind: 'ok' });
      creating = false;
      newJob = { id: '', name: '', cron: '', run_at: '', executor: '', args_json: '{}' };
      await refreshList();
      selectedJobId = def.id;
      await refreshSelected();
    } catch (e) {
      notify({ title: 'Create failed', body: String(e).slice(0, 200), kind: 'err' });
    }
  }

  async function runNow(id: string) {
    try {
      await runJobNow(id);
      notify({ title: 'Triggered', body: id, kind: 'ok', ttlMs: 1800 });
      await refreshSelected();
    } catch (e) {
      notify({ title: 'Run failed', body: String(e).slice(0, 160), kind: 'err' });
    }
  }

  async function toggleEnabled(j: JobDefinition) {
    try {
      await setJobEnabled(j.id, !j.enabled);
      await refreshList();
    } catch (e) {
      notify({ title: 'Toggle failed', body: String(e).slice(0, 160), kind: 'err' });
    }
  }

  async function dropJob(j: JobDefinition) {
    if (!confirm(`Delete job '${j.id}'?`)) return;
    try {
      await deleteJob(j.id);
      if (selectedJobId === j.id) selectedJobId = null;
      await refreshList();
    } catch (e) {
      notify({ title: 'Delete failed', body: String(e).slice(0, 160), kind: 'err' });
    }
  }

  function fmtTs(ts?: string | null): string {
    if (!ts) return '–';
    try {
      return new Date(ts).toLocaleString([], { dateStyle: 'short', timeStyle: 'short' });
    } catch {
      return ts;
    }
  }

  onMount(() => {
    refreshList();
    loadExecutors();
    timer = setInterval(() => {
      refreshList();
      if (selectedJobId) refreshSelected();
    }, 6000);
  });

  onDestroy(() => {
    if (timer) clearInterval(timer);
  });

  $: selected = jobs.find((j) => j.id === selectedJobId) ?? null;
</script>

<div class="h-full w-full flex font-mono text-xs">
  <aside class="w-72 border-r border-border/40 flex flex-col">
    <header class="px-3 py-2 border-b border-border/40 flex items-center justify-between">
      <div>
        <h3 class="text-accent text-sm">Kronos jobs</h3>
        <p class="text-muted text-[10px]">{jobs.length} registered</p>
      </div>
      <button
        class="text-[10px] px-2 py-0.5 rounded border border-accent text-accent hover:bg-accent hover:text-bg"
        on:click={() => (creating = !creating)}
      >
        {creating ? 'Cancel' : '+ New'}
      </button>
    </header>

    {#if creating}
      <form class="px-3 py-3 border-b border-border/40 space-y-2 bg-surface2/30" on:submit={submitNew}>
        <input class="w-full bg-transparent border-b border-border/40 outline-none text-fg" bind:value={newJob.id} placeholder="job id (slug)" required />
        <input class="w-full bg-transparent border-b border-border/40 outline-none text-fg" bind:value={newJob.name} placeholder="display name" />
        <input class="w-full bg-transparent border-b border-border/40 outline-none text-fg" bind:value={newJob.cron} placeholder="cron (e.g. 0 7 * * *)" />
        <input class="w-full bg-transparent border-b border-border/40 outline-none text-fg" bind:value={newJob.run_at} placeholder="run_at (ISO; one-off)" />
        <select class="w-full bg-surface text-fg p-1 rounded outline-none border border-border/40" bind:value={newJob.executor} required>
          <option value="">executor…</option>
          {#each executors as ex (ex.dotted_path)}
            <option value={ex.dotted_path}>{ex.dotted_path}</option>
          {/each}
        </select>
        <textarea
          class="w-full bg-transparent border border-border/40 rounded p-1 text-fg outline-none"
          rows="3"
          bind:value={newJob.args_json}
          placeholder="args JSON, e.g. &#123;&quot;topic&quot;: &quot;...&quot;&#125;"
        ></textarea>
        <button type="submit" class="w-full bg-accent text-bg py-1 rounded text-[11px]">Create</button>
      </form>
    {/if}

    <ul class="flex-1 overflow-y-auto">
      {#each jobs as j (j.id)}
        <li>
          <button
            class="w-full text-left px-3 py-2 hover:bg-surface2/60"
            class:bg-surface2={selectedJobId === j.id}
            on:click={() => pickJob(j.id)}
          >
            <div class="flex items-center justify-between">
              <span class="text-fg truncate">{j.name || j.id}</span>
              <span class="text-[10px] {j.enabled ? 'text-ok' : 'text-muted'}">
                {j.enabled ? 'on' : 'off'}
              </span>
            </div>
            <div class="text-muted text-[10px] truncate">
              {j.schedule?.cron || j.schedule?.run_at || '–'}
            </div>
          </button>
        </li>
      {:else}
        <li class="px-3 py-4 text-muted text-center">No jobs.</li>
      {/each}
    </ul>

    {#if upcoming.length > 0}
      <div class="border-t border-border/40 px-3 py-2 max-h-32 overflow-y-auto">
        <p class="text-[10px] text-muted uppercase mb-1">Upcoming</p>
        {#each upcoming.slice(0, 5) as u}
          <p class="text-[11px] text-fg/80">
            <span class="text-muted">{fmtTs(u.next_fire)}</span> {u.name || u.job_id}
          </p>
        {/each}
      </div>
    {/if}
  </aside>

  <section class="flex-1 flex flex-col min-w-0">
    {#if error}
      <p class="text-err px-3 py-2 text-[11px]">{error}</p>
    {/if}

    {#if selected}
      <header class="px-3 py-2 border-b border-border/40">
        <div class="flex items-center justify-between">
          <h3 class="text-accent text-sm">{selected.name || selected.id}</h3>
          <div class="flex gap-1">
            <button class="text-[10px] px-2 py-0.5 border border-accent text-accent rounded" on:click={() => runNow(selected!.id)}>Run now</button>
            <button class="text-[10px] px-2 py-0.5 border border-border/60 text-fg rounded" on:click={() => toggleEnabled(selected!)}>
              {selected.enabled ? 'Disable' : 'Enable'}
            </button>
            <button class="text-[10px] px-2 py-0.5 border border-err/60 text-err rounded" on:click={() => dropJob(selected!)}>Delete</button>
          </div>
        </div>
        <p class="text-muted text-[10px] mt-1">{selected.id} · {selected.executor || selected.agent || '(no executor)'}</p>
        {#if selected.description}<p class="text-fg/80 text-[11px] mt-1">{selected.description}</p>{/if}
        <p class="text-muted text-[10px] mt-1">
          {selected.schedule?.cron ? `cron: ${selected.schedule.cron}` : ''}
          {selected.schedule?.run_at ? ` run_at: ${selected.schedule.run_at}` : ''}
          {selected.schedule?.timezone ? ` (${selected.schedule.timezone})` : ''}
          · last: {fmtTs(selected.last_fired_at)}
        </p>
        {#if selected.params && Object.keys(selected.params).length}
          <details class="mt-1">
            <summary class="text-muted text-[10px] cursor-pointer">params</summary>
            <pre class="mt-1 text-[10px] text-fg whitespace-pre-wrap overflow-x-auto">{JSON.stringify(selected.params, null, 2)}</pre>
          </details>
        {/if}
      </header>

      <div class="px-3 py-2 border-b border-border/40 text-[11px] text-accent">Runs</div>
      <ul class="flex-1 overflow-y-auto">
        {#each runs as r (r.id)}
          <li class="px-3 py-2 border-b border-border/20">
            <header class="flex items-center justify-between text-[10px] text-muted">
              <span>
                <span class="text-fg">{r.status}</span>
                {#if r.duration_ms} · {Math.round(r.duration_ms)}ms{/if}
                {#if r.attempts && r.attempts > 1} · attempt {r.attempts}{/if}
              </span>
              <span>{fmtTs(r.finished_at || r.started_at)}</span>
            </header>
            {#if r.error}<p class="text-err text-[11px] mt-1">{r.error}</p>{/if}
            {#if r.output_summary}<pre class="text-[10px] text-fg/80 whitespace-pre-wrap mt-1">{r.output_summary.slice(0, 300)}{r.output_summary.length > 300 ? '…' : ''}</pre>{/if}
          </li>
        {:else}
          <li class="px-3 py-4 text-muted text-center">No runs yet.</li>
        {/each}
      </ul>
    {:else}
      <div class="flex-1 grid place-items-center text-muted text-center px-6">
        <div>
          <p>Pick a job to see its run history,</p>
          <p>or hit <span class="text-accent">+ New</span> to create one.</p>
          <p class="mt-3 text-[10px]">Jobs created via Zeus chat appear here automatically.</p>
        </div>
      </div>
    {/if}
  </section>
</div>
