<script lang="ts">
  import { createEventDispatcher, tick } from 'svelte';
  import { fade, scale } from 'svelte/transition';
  import { cubicOut } from 'svelte/easing';

  import { listApps, type AppEntry } from '$lib/api/apps';
  import { openApp } from '$lib/wm/store';
  import { THEMES, applyTheme, type ThemeId } from '$lib/themes';
  import { MODIFIER_LABEL, type ModifierMode } from '$lib/wm/keybinds';

  export let open = false;
  export let modifier: ModifierMode = 'Meta';

  const dispatch = createEventDispatcher<{ setModifier: ModifierMode }>();

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

  const MOD_MODES: ModifierMode[] = ['Meta', 'Alt', 'CtrlAlt'];
  $: modifierEntries = MOD_MODES.filter((m) => m !== modifier).map((m) => ({
    id: 'modifier:' + m,
    label: `Modifier: ${MODIFIER_LABEL[m]}${m === 'CtrlAlt' ? ' (Windows-friendly)' : m === 'Meta' ? ' (Linux default)' : ''}`,
    hint: 'modifier',
    onPick: () => dispatch('setModifier', m)
  } satisfies Entry));

  $: actionEntries = [
    {
      id: 'action:reload',
      label: 'Reload Zeus OS',
      hint: 'action',
      onPick: () => window.location.reload()
    } satisfies Entry
  ];

  $: entries = [...appEntries, ...themeEntries, ...modifierEntries, ...actionEntries];

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
    // Only steal focus (and pop the on-screen keyboard) on desktop. On mobile
    // the launcher is a bottom sheet you tap through, so leave the input unfocused.
    tick().then(() => {
      if (typeof window !== 'undefined' && window.matchMedia('(min-width: 768px)').matches) {
        inputEl?.focus();
      }
    });
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
    class="absolute inset-0 z-40 flex items-end justify-center md:items-start md:pt-[15vh]"
    style="background: rgb(0 0 0 / 0.35); backdrop-filter: blur(6px);"
    role="presentation"
    on:click|self={() => (open = false)}
    transition:fade={{ duration: 120 }}
  >
    <div
      class="surface-blur shadow-2xl overflow-hidden border border-border/40 flex flex-col
             w-full rounded-t-2xl max-h-[80vh]
             md:w-[min(640px,92vw)] md:rounded-2xl md:max-h-[70vh]"
      transition:scale={{ duration: 220, start: 0.96, easing: cubicOut }}
    >
      <!-- mobile grab handle -->
      <div class="md:hidden mx-auto mt-2 mb-1 h-1 w-10 rounded-full bg-muted/40 shrink-0"></div>
      <div class="p-3 border-b border-border/40 shrink-0">
        <input
          bind:this={inputEl}
          bind:value={query}
          on:input={() => (selected = 0)}
          placeholder="Search apps, themes, actions…"
          class="w-full bg-transparent text-fg placeholder:text-muted/70 outline-none text-base font-mono"
        />
      </div>
      <ul class="flex-1 min-h-0 overflow-y-auto">
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
      <footer class="px-4 py-2 text-[10px] text-muted border-t border-border/40 justify-between shrink-0 hidden md:flex">
        <span><kbd>↑</kbd>/<kbd>↓</kbd> select &nbsp; <kbd>↵</kbd> open &nbsp; <kbd>Esc</kbd> close &nbsp;·&nbsp; modifier: <span class="text-fg">{MODIFIER_LABEL[modifier]}</span></span>
        <span>{filtered.length} / {entries.length}</span>
      </footer>
    </div>
  </div>
{/if}
