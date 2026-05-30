<script lang="ts">
  import { onDestroy, onMount } from 'svelte';

  import Desktop from '$lib/components/Desktop.svelte';
  import MobileShell from '$lib/components/MobileShell.svelte';
  import Launcher from '$lib/components/Launcher.svelte';
  import Cheatsheet from '$lib/components/Cheatsheet.svelte';

  import {
    bootstrap,
    closeFocused,
    focusDir,
    moveDir,
    moveFocusedToWorkspace,
    openApp,
    switchWorkspace
  } from '$lib/wm/store';
  import {
    DEFAULT_KEYMAP,
    compile,
    matchEvent,
    type Action,
    type KeybindContext
  } from '$lib/wm/keybinds';
  import { applyTheme, nextTheme, THEMES, type ThemeId } from '$lib/themes';
  import { listApps, type AppEntry } from '$lib/api/apps';
  import { loadConfig, saveConfig, type ZeusOsConfig } from '$lib/api/config';

  let launcherOpen = false;
  let cheatsheetOpen = false;
  let isMobile = false;
  let theme: ThemeId = 'catppuccin-mocha';
  let ctx: KeybindContext = { modifier: 'Meta' };
  let config: ZeusOsConfig | null = null;
  let apps: AppEntry[] = [];

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
        break;
      }
      case 'setTheme':
        theme = action.theme;
        applyTheme(theme);
        persistTheme();
        break;
      case 'cheatsheet':
        launcherOpen = false;
        cheatsheetOpen = !cheatsheetOpen;
        break;
      case 'reload':
        window.location.reload();
        break;
      case 'toggleFloating':
        // Phase 1 stub.
        break;
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
      if (config?.modifier === 'Alt') {
        ctx = { modifier: 'Alt' };
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
    <MobileShell />
  {:else}
    <Desktop />
  {/if}
  <Launcher bind:open={launcherOpen} />
  <Cheatsheet bind:open={cheatsheetOpen} />
</div>
