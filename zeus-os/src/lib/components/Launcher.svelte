<script lang="ts">
  import { tick } from 'svelte';
  import { fade, scale } from 'svelte/transition';
  import { cubicOut } from 'svelte/easing';

  import { listApps, type AppEntry } from '$lib/api/apps';
  import { openApp } from '$lib/wm/store';
  import { THEMES, applyTheme, type ThemeId } from '$lib/themes';

  export let open = false;

  let query = '';
  let inputEl: HTMLInputElement;
  let apps: AppEntry[] = [];
  let selected = 0;

  interface Entry {
    id: string;
    label: string;
    hint: string;
    onPick: () => void;
  }

  $: appEntries = apps.map((a) => ({
    id: 'app:' + a.id,
    label: a.title,
    hint: 'app',
    onPick: () => {
      openApp({ appId: a.id, kind: a.kind, title: a.title });
    }
  } satisfies Entry));

  $: themeEntries = THEMES.map((t) => ({
    id: 'theme:' + t.id,
    label: 'Theme: ' + t.label,
    hint: 'theme',
    onPick: () => applyTheme(t.id as ThemeId)
  } satisfies Entry));

  $: actionEntries = [
    {
      id: 'action:reload',
      label: 'Reload Zeus OS',
      hint: 'action',
      onPick: () => window.location.reload()
    } satisfies Entry
  ];

  $: entries = [...appEntries, ...themeEntries, ...actionEntries];

  $: filtered = filterEntries(entries, query);

  function filterEntries(items: Entry[], q: string): Entry[] {
    const s = q.trim().toLowerCase();
    if (!s) return items;
    const score = (label: string) => {
      const lc = label.toLowerCase();
      if (lc.startsWith(s)) return 0;
      if (lc.includes(s)) return 1;
      let i = 0;
      for (const ch of lc) {
        if (i < s.length && ch === s[i]) i += 1;
      }
      return i === s.length ? 2 : 3;
    };
    return items
      .map((it) => ({ it, s: score(it.label) }))
      .filter((x) => x.s < 3)
      .sort((a, b) => a.s - b.s)
      .map((x) => x.it);
  }

  async function refreshApps() {
    try {
      const { apps: list } = await listApps();
      apps = list;
    } catch {
      apps = [];
    }
  }

  $: if (open) {
    refreshApps();
    query = '';
    selected = 0;
    tick().then(() => inputEl?.focus());
  }

  function pick(i: number) {
    const e = filtered[i];
    if (!e) return;
    e.onPick();
    open = false;
  }

  function onKey(ev: KeyboardEvent) {
    if (!open) return;
    if (ev.key === 'Escape') {
      open = false;
    } else if (ev.key === 'ArrowDown') {
      ev.preventDefault();
      selected = (selected + 1) % Math.max(1, filtered.length);
    } else if (ev.key === 'ArrowUp') {
      ev.preventDefault();
      selected = (selected - 1 + filtered.length) % Math.max(1, filtered.length);
    } else if (ev.key === 'Enter') {
      ev.preventDefault();
      pick(selected);
    }
  }
</script>

<svelte:window on:keydown={onKey} />

{#if open}
  <div
    class="absolute inset-0 z-40 flex items-start justify-center pt-[15vh]"
    style="background: rgb(0 0 0 / 0.35); backdrop-filter: blur(6px);"
    role="presentation"
    on:click|self={() => (open = false)}
    transition:fade={{ duration: 120 }}
  >
    <div
      class="surface-blur rounded-2xl shadow-2xl w-[min(640px,92vw)] overflow-hidden border border-border/40"
      transition:scale={{ duration: 220, start: 0.96, easing: cubicOut }}
    >
      <div class="p-3 border-b border-border/40">
        <input
          bind:this={inputEl}
          bind:value={query}
          on:input={() => (selected = 0)}
          placeholder="Search apps, themes, actions…"
          class="w-full bg-transparent text-fg placeholder:text-muted/70 outline-none text-base font-mono"
        />
      </div>
      <ul class="max-h-[50vh] overflow-y-auto">
        {#each filtered as e, i (e.id)}
          <li>
            <button
              class="w-full text-left px-4 py-2 flex items-center justify-between text-sm font-mono"
              class:bg-accent={i === selected}
              class:text-bg={i === selected}
              class:text-fg={i !== selected}
              on:mouseenter={() => (selected = i)}
              on:click={() => pick(i)}
            >
              <span>{e.label}</span>
              <span class="text-xs opacity-60">{e.hint}</span>
            </button>
          </li>
        {:else}
          <li class="px-4 py-6 text-center text-muted text-sm">No matches.</li>
        {/each}
      </ul>
      <footer class="px-4 py-2 text-[10px] text-muted border-t border-border/40 flex justify-between">
        <span><kbd>↑</kbd>/<kbd>↓</kbd> select &nbsp; <kbd>↵</kbd> open &nbsp; <kbd>Esc</kbd> close</span>
        <span>{filtered.length} / {entries.length}</span>
      </footer>
    </div>
  </div>
{/if}
