<script lang="ts">
  import { onMount } from 'svelte';
  import type { AppInstance } from '$lib/wm/tree';
  import { linearQuery, linearStatus } from '$lib/api/integrations';
  import { notify } from '$lib/notify/store';
  import { readCodeClip, renderMarkdown } from '$lib/markdown';

  export let app: AppInstance;
  void app;

  interface State {
    id: string;
    name: string;
    color: string;
    type: string;
  }

  interface Project {
    id: string;
    name: string;
  }

  interface Issue {
    id: string;
    identifier: string;
    title: string;
    description?: string | null;
    url: string;
    priority: number;
    state: State;
    assignee?: { displayName: string } | null;
    project?: { id: string; name: string } | null;
    labels?: { nodes: { name: string; color: string }[] };
    createdAt: string;
    updatedAt: string;
  }

  let configured = false;
  let teamKey = 'LAB';
  let states: State[] = [];
  let projects: Project[] = [];
  let issues: Issue[] = [];
  let stateFilter = '';
  let projectFilter = '';
  let searchQ = '';
  let loading = false;
  let error = '';
  let lastFetched = '';
  let selected: Issue | null = null;

  const ISSUES_QUERY = `query Issues($filter: IssueFilter!) {
    issues(filter: $filter, first: 50, orderBy: updatedAt) {
      nodes {
        id identifier title description url priority createdAt updatedAt
        state { id name color type }
        assignee { displayName }
        project { id name }
        labels { nodes { name color } }
      }
    }
  }`;

  const META_QUERY = `query Meta($teamKey: String!) {
    teams(filter: { key: { eq: $teamKey } }) {
      nodes {
        id name key
        states { nodes { id name color type } }
      }
    }
    projects(first: 50) { nodes { id name } }
  }`;

  async function checkStatus() {
    try {
      const s = await linearStatus();
      configured = s.configured;
      teamKey = s.team_key;
    } catch (e) {
      error = String(e);
    }
  }

  async function loadMeta() {
    if (!configured) return;
    try {
      const r = await linearQuery<{
        teams: { nodes: { states: { nodes: State[] } }[] };
        projects: { nodes: Project[] };
      }>(META_QUERY, { teamKey });
      if (r.errors?.length) {
        error = r.errors.map((e) => e.message).join('; ');
        return;
      }
      states = r.data?.teams.nodes[0]?.states.nodes ?? [];
      projects = r.data?.projects.nodes ?? [];
      error = '';
    } catch (e) {
      error = String(e);
    }
  }

  async function loadIssues() {
    if (!configured) return;
    loading = true;
    try {
      const filter: Record<string, unknown> = {
        team: { key: { eq: teamKey } }
      };
      if (stateFilter) filter.state = { id: { eq: stateFilter } };
      if (projectFilter) filter.project = { id: { eq: projectFilter } };
      if (searchQ.trim()) {
        // Linear search is via the `title.containsIgnoreCase` filter; for
        // broader text search use the dedicated `searchIssues` query.
        filter.title = { containsIgnoreCase: searchQ.trim() };
      }
      const r = await linearQuery<{ issues: { nodes: Issue[] } }>(ISSUES_QUERY, { filter });
      if (r.errors?.length) {
        error = r.errors.map((e) => e.message).join('; ');
        return;
      }
      issues = r.data?.issues.nodes ?? [];
      error = '';
      lastFetched = new Date().toLocaleTimeString();
    } catch (e) {
      error = String(e);
    } finally {
      loading = false;
    }
  }

  function fmtDate(s?: string) {
    if (!s) return '';
    try {
      return new Date(s).toLocaleDateString([], { month: 'short', day: 'numeric' });
    } catch {
      return s;
    }
  }

  function priorityLabel(p: number): string {
    return ['no priority', 'urgent', 'high', 'medium', 'low'][p] ?? '?';
  }

  function onPreviewClick(ev: MouseEvent) {
    const t = ev.target as HTMLElement | null;
    if (!t) return;
    const btn = t.closest('.code-copy-btn') as HTMLElement | null;
    if (!btn) return;
    const raw = readCodeClip(btn);
    if (raw === null) return;
    navigator.clipboard?.writeText(raw).then(
      () => {
        btn.textContent = 'Copied';
        btn.classList.add('copied');
        setTimeout(() => {
          btn.textContent = 'Copy';
          btn.classList.remove('copied');
        }, 1200);
      },
      () => notify({ title: 'Copy failed', kind: 'warn', ttlMs: 1500 })
    );
  }

  onMount(async () => {
    await checkStatus();
    if (configured) {
      await loadMeta();
      await loadIssues();
    }
  });
</script>

<div class="h-full w-full flex flex-col font-mono text-xs">
  {#if error}
    <div class="bg-err/20 border-b border-err/40 px-3 py-2 text-err">{error}</div>
  {/if}

  {#if !configured}
    <div class="flex-1 grid place-items-center text-muted text-center px-6">
      <div>
        <p class="text-fg mb-2">Linear API key not configured.</p>
        <p class="text-[11px] leading-relaxed">
          Add <code class="text-accent">LINEAR_API_KEY</code> to <code class="text-fg">zeus/.env</code>
          (Linear → Settings → API → Personal API key), then restart zeus-core. The team key defaults
          to <code class="text-fg">LAB</code> — override with <code class="text-fg">ZEUS_LINEAR_TEAM_KEY</code>.
        </p>
      </div>
    </div>
  {:else}
    <header class="px-3 py-2 border-b border-border/40 flex items-center gap-2 flex-wrap">
      <h3 class="text-accent text-sm">Linear · {teamKey}</h3>
      <input
        bind:value={searchQ}
        placeholder="title contains…"
        class="flex-1 min-w-[140px] bg-transparent border-b border-border/40 outline-none text-fg"
        on:keydown={(ev) => ev.key === 'Enter' && loadIssues()}
      />
      <select bind:value={stateFilter} class="bg-surface text-fg p-1 rounded border border-border/40 text-[11px]" on:change={loadIssues}>
        <option value="">all states</option>
        {#each states as s (s.id)}
          <option value={s.id}>{s.name}</option>
        {/each}
      </select>
      <select bind:value={projectFilter} class="bg-surface text-fg p-1 rounded border border-border/40 text-[11px]" on:change={loadIssues}>
        <option value="">all projects</option>
        {#each projects as p (p.id)}
          <option value={p.id}>{p.name}</option>
        {/each}
      </select>
      <button class="text-[10px] px-2 py-0.5 border border-border/60 rounded" on:click={loadIssues}>refresh</button>
      <span class="text-[10px] text-muted">{issues.length} {loading ? 'loading…' : ''} {lastFetched}</span>
    </header>

    <div class="flex-1 flex min-h-0">
      <ul class="w-1/2 overflow-y-auto border-r border-border/40">
        {#each issues as i (i.id)}
          <li class="border-b border-border/20" class:bg-surface2={selected?.id === i.id}>
            <button class="w-full text-left px-3 py-2 hover:bg-surface2/60" on:click={() => (selected = i)}>
              <div class="flex items-center justify-between">
                <span class="text-muted text-[10px]">{i.identifier}</span>
                <span
                  class="text-[10px] px-1.5 rounded"
                  style="background: {i.state.color}33; color: {i.state.color};"
                >
                  {i.state.name}
                </span>
              </div>
              <p class="text-fg mt-0.5 leading-snug">{i.title}</p>
              <div class="flex items-center justify-between mt-1 text-[10px] text-muted">
                <span>{i.project?.name ?? '(no project)'}</span>
                <span>{priorityLabel(i.priority)} · {fmtDate(i.updatedAt)}</span>
              </div>
            </button>
          </li>
        {:else}
          <li class="px-3 py-6 text-muted text-center">{loading ? 'loading…' : 'no issues match.'}</li>
        {/each}
      </ul>

      <section class="w-1/2 overflow-y-auto p-3">
        {#if selected}
          <header class="mb-2">
            <a href={selected.url} target="_blank" rel="noopener" class="text-muted text-[10px]">{selected.identifier} ↗</a>
            <h3 class="text-accent text-sm mt-1">{selected.title}</h3>
            <div class="flex items-center gap-2 text-[10px] mt-1">
              <span style="color: {selected.state.color};">● {selected.state.name}</span>
              <span class="text-muted">{priorityLabel(selected.priority)}</span>
              {#if selected.project}<span class="text-muted">· {selected.project.name}</span>{/if}
              {#if selected.assignee}<span class="text-muted">· {selected.assignee.displayName}</span>{/if}
            </div>
            {#if selected.labels && selected.labels.nodes.length}
              <div class="flex gap-1 mt-2 flex-wrap">
                {#each selected.labels.nodes as l (l.name)}
                  <span class="text-[10px] px-1.5 rounded" style="background: {l.color}33; color: {l.color};">{l.name}</span>
                {/each}
              </div>
            {/if}
          </header>
          {#if selected.description}
            <div class="prose-chat leading-relaxed" on:click={onPreviewClick} role="presentation">
              {@html renderMarkdown(selected.description)}
            </div>
          {:else}
            <p class="text-muted text-[11px]">(no description)</p>
          {/if}
          <p class="text-muted text-[10px] mt-4">
            created {fmtDate(selected.createdAt)} · updated {fmtDate(selected.updatedAt)}
          </p>
        {:else}
          <p class="text-muted text-center mt-12">Pick an issue to read its description.</p>
        {/if}
      </section>
    </div>
  {/if}
</div>
