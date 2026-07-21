<script lang="ts">
  import { onDestroy, onMount } from 'svelte';

  import Desktop from '$lib/components/Desktop.svelte';
  import MobileShell from '$lib/components/MobileShell.svelte';
  import Launcher from '$lib/components/Launcher.svelte';
  import Cheatsheet from '$lib/components/Cheatsheet.svelte';
  import Notifications from '$lib/components/Notifications.svelte';
  import { notify } from '$lib/notify/store';

  import { get } from 'svelte/store';
  import {
    bootstrap,
    closeFocused,
    focusDir,
    moveDir,
    moveFocusedToWorkspace,
    openApp,
    switchWorkspace,
    toggleFloating,
    wm
  } from '$lib/wm/store';
  import { allLeaves } from '$lib/wm/tree';
  import {
    DEFAULT_KEYMAP,
    MODIFIER_LABEL,
    compile,
    matchEvent,
    type Action,
    type KeybindContext,
    type ModifierMode
  } from '$lib/wm/keybinds';
  import { applyTheme, nextTheme, THEMES, type ThemeId } from '$lib/themes';
  import { listApps, type AppEntry } from '$lib/api/apps';
  import { loadConfig, saveConfig, type ZeusOsConfig } from '$lib/api/config';
  import { triggerVoicePtt } from '$lib/voice/store';

  let launcherOpen = false;
  let cheatsheetOpen = false;
  let isMobile = false;
  let theme: ThemeId = 'catppuccin-mocha';
  let modifier: ModifierMode = detectDefaultModifier();
  $: ctx = { modifier } satisfies KeybindContext;
  let config: ZeusOsConfig | null = null;
  let apps: AppEntry[] = [];

  // Default to CtrlAlt on Windows so Win+letter doesn't fight the OS.
  function detectDefaultModifier(): ModifierMode {
    if (typeof navigator === 'undefined') return 'Meta';
    const ua = navigator.userAgent || '';
    if (/Windows/i.test(ua)) return 'CtrlAlt';
    return 'Meta';
  }

  const compiled = compile(DEFAULT_KEYMAP);

  function detectMobile() {
    isMobile = typeof window !== 'undefined' && window.innerWidth < 768;
  }

  function onResize() {
    detectMobile();
  }

  function onKey(ev: KeyboardEvent) {
    // Avoid intercepting typing in input/textarea/contenteditable.
    const target = ev.target as HTMLElement | null;
    if (target) {
      const tag = target.tagName;
      if (
        (tag === 'INPUT' || tag === 'TEXTAREA' || target.isContentEditable) &&
        !ev.metaKey &&
        !ev.altKey
      ) {
        return;
      }
    }
    for (const b of compiled) {
      if (matchEvent(ev, b.bind, ctx)) {
        ev.preventDefault();
        runAction(b.action);
        return;
      }
    }
  }

  function findApp(id: string): AppEntry | undefined {
    return apps.find((a) => a.id === id);
  }

  function runAction(action: Action) {
    switch (action.kind) {
      case 'open': {
        const a = findApp(action.appId);
        if (a) openApp({ appId: a.id, kind: a.kind, title: a.title }, action.dir ?? 'h');
        break;
      }
      case 'close':
        closeFocused();
        break;
      case 'focus':
        focusDir(action.dir);
        break;
      case 'move':
        moveDir(action.dir);
        break;
      case 'split': {
        // For Phase 1, "split" without a target opens the Terminal (a reasonable default).
        const a = findApp('terminal');
        if (a) openApp({ appId: a.id, kind: a.kind, title: a.title }, action.dir);
        break;
      }
      case 'workspace':
        switchWorkspace(action.id);
        break;
      case 'moveToWorkspace':
        moveFocusedToWorkspace(action.id);
        break;
      case 'toggleLauncher':
        cheatsheetOpen = false;
        launcherOpen = !launcherOpen;
        break;
      case 'cycleTheme': {
        theme = nextTheme(theme);
        applyTheme(theme);
        persistTheme();
        notify({ title: 'Theme', body: theme, kind: 'info', ttlMs: 1800 });
        break;
      }
      case 'setTheme':
        theme = action.theme;
        applyTheme(theme);
        persistTheme();
        notify({ title: 'Theme', body: theme, kind: 'info', ttlMs: 1800 });
        break;
      case 'setModifier':
        modifier = action.mode;
        persistConfig();
        notify({
          title: 'Modifier',
          body: `${MODIFIER_LABEL[modifier]} now stands in for Super`,
          kind: 'ok',
          ttlMs: 2400
        });
        break;
      case 'cheatsheet':
        launcherOpen = false;
        cheatsheetOpen = !cheatsheetOpen;
        break;
      case 'reload':
        window.location.reload();
        break;
      case 'toggleFloating':
        toggleFloating();
        break;
      case 'voicePtt': {
        // Make sure the Voice Orb is mounted (otherwise the PTT trigger has
        // no listener), then fire the toggle event on the shared store.
        const voice = findApp('voice');
        if (voice) {
          const already = new Set<string>();
          for (const w of get(wm).workspaces) {
            for (const l of allLeaves(w.root)) already.add(l.app.appId);
            for (const f of w.floating) already.add(f.app.appId);
          }
          if (!already.has(voice.id)) {
            openApp({ appId: voice.id, kind: voice.kind, title: voice.title }, 'h');
          }
        }
        triggerVoicePtt();
        break;
      }
    }
  }

  async function persistTheme() {
    if (!config) return;
    config = { ...config, theme };
    try {
      await saveConfig(config);
    } catch {
      /* non-fatal */
    }
  }

  async function persistConfig() {
    if (!config) return;
    config = { ...config, theme, modifier };
    try {
      await saveConfig(config);
    } catch {
      /* non-fatal */
    }
  }

  async function init() {
    detectMobile();
    window.addEventListener('resize', onResize);
    window.addEventListener('keydown', onKey);

    try {
      apps = (await listApps()).apps;
    } catch {
      apps = [];
    }
    try {
      config = await loadConfig();
      if (config?.theme && THEMES.some((t) => t.id === config!.theme)) {
        theme = config.theme as ThemeId;
        applyTheme(theme);
      }
      if (config?.modifier === 'Alt' || config?.modifier === 'CtrlAlt' || config?.modifier === 'Meta') {
        modifier = config.modifier;
      }
    } catch {
      /* fall back to defaults */
    }

    // Phase 1 starts with the Chat app pinned in workspace 1.
    const chat = findApp('chat');
    if (chat) {
      bootstrap([
        { app: { appId: chat.id, kind: chat.kind, title: chat.title }, workspace: 1 }
      ]);
    }
  }

  onMount(init);

  onDestroy(() => {
    window.removeEventListener('resize', onResize);
    window.removeEventListener('keydown', onKey);
  });
</script>

<div class="h-screen w-screen overflow-hidden">
  {#if isMobile}
    <MobileShell {modifier} />
  {:else}
    <Desktop {modifier} />
  {/if}
  <Launcher bind:open={launcherOpen} {modifier} on:setModifier={(e) => runAction({ kind: 'setModifier', mode: e.detail })} />
  <Cheatsheet bind:open={cheatsheetOpen} {modifier} />
  <Notifications />
</div>
