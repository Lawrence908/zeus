// src/lib/apps/terminal-sessions.ts — long-lived terminal state.
//
// Each Terminal window's xterm + PTY + buffer lives in module-scope so that
// float ↔ tile toggles (which unmount the component) don't drop the shell.
// xterm is sensitive to its DOM container: rather than re-opening, we keep
// a detached container alive in this module and re-parent it to the new
// mount point on each remount. The Terminal instance never sees the swap.

import { openPty, type PtyClient } from '$lib/api/pty';
import { onAppDestroyed } from '$lib/wm/store';

export interface TerminalTab {
  id: string; // stable across remounts
  label: string;
}

export interface TerminalWindowState {
  tabs: TerminalTab[];
  activeTabId: string | null;
}

interface PaneSession {
  container: HTMLDivElement;
  term: import('@xterm/xterm').Terminal;
  fit: import('@xterm/addon-fit').FitAddon;
  pty: PtyClient;
  initialized: boolean;
}

let _windowSeq = 0;
let _tabSeq = 0;

const _windows = new Map<string, TerminalWindowState>();
const _panes = new Map<string, PaneSession>();

function paneKey(instanceId: string, tabId: string): string {
  return `${instanceId}::${tabId}`;
}

export function getWindowState(instanceId: string): TerminalWindowState {
  let state = _windows.get(instanceId);
  if (!state) {
    _tabSeq += 1;
    const tabId = `t-${_tabSeq}`;
    state = { tabs: [{ id: tabId, label: 'shell' }], activeTabId: tabId };
    _windows.set(instanceId, state);
  }
  return state;
}

export function newTab(instanceId: string): TerminalTab {
  const state = getWindowState(instanceId);
  _tabSeq += 1;
  const tab: TerminalTab = { id: `t-${_tabSeq}`, label: 'shell' };
  state.tabs = [...state.tabs, tab];
  state.activeTabId = tab.id;
  return tab;
}

export function setActiveTab(instanceId: string, tabId: string) {
  const state = getWindowState(instanceId);
  state.activeTabId = tabId;
}

export function renameTab(instanceId: string, tabId: string, label: string) {
  const state = getWindowState(instanceId);
  const trimmed = label.trim();
  state.tabs = state.tabs.map((t) =>
    t.id === tabId ? { ...t, label: trimmed || 'shell' } : t
  );
}

export function closeTab(instanceId: string, tabId: string): TerminalTab[] {
  const state = getWindowState(instanceId);
  state.tabs = state.tabs.filter((t) => t.id !== tabId);
  if (state.activeTabId === tabId) {
    state.activeTabId = state.tabs[state.tabs.length - 1]?.id ?? null;
  }
  // Tear down the pane backing this tab.
  _disposePane(paneKey(instanceId, tabId));
  // If we removed the last tab, also drop the window record so the next
  // remount of Terminal.svelte gets a fresh first tab.
  if (state.tabs.length === 0) {
    _windows.delete(instanceId);
  }
  return state.tabs;
}

function _disposePane(key: string) {
  const p = _panes.get(key);
  if (!p) return;
  try {
    p.pty.close();
  } catch {
    /* ignore */
  }
  try {
    p.term.dispose();
  } catch {
    /* ignore */
  }
  try {
    p.container.remove();
  } catch {
    /* ignore */
  }
  _panes.delete(key);
}

export interface MountResult {
  fit: () => void;
}

/**
 * Mount the pane backing (instanceId, tabId) into `host`. Creates the
 * xterm + PTY on first call; subsequent calls just re-attach the existing
 * container to the new host (the buffer + PTY connection survive).
 */
export async function mountPane(
  instanceId: string,
  tabId: string,
  host: HTMLElement,
  opts: { onExit?: (code: number) => void } = {}
): Promise<MountResult> {
  const key = paneKey(instanceId, tabId);
  const existing = _panes.get(key);
  if (existing) {
    host.appendChild(existing.container);
    queueMicrotask(() => {
      try {
        existing.fit.fit();
      } catch {
        /* ignore */
      }
    });
    return { fit: () => safeFit(existing.fit) };
  }

  // Fresh pane: dynamically import xterm so the chunk only loads when the
  // Terminal app is actually opened.
  const { Terminal } = await import('@xterm/xterm');
  const { FitAddon } = await import('@xterm/addon-fit');
  const { WebLinksAddon } = await import('@xterm/addon-web-links');
  await import('@xterm/xterm/css/xterm.css');

  const container = document.createElement('div');
  container.className = 'h-full w-full p-1 font-mono';

  const term = new Terminal({
    fontFamily: 'JetBrains Mono, ui-monospace, monospace',
    fontSize: 13,
    cursorBlink: true,
    allowProposedApi: true,
    scrollback: 5000,
    theme: themeFromCss()
  });
  const fit = new FitAddon();
  term.loadAddon(fit);
  term.loadAddon(new WebLinksAddon());

  host.appendChild(container);
  term.open(container);
  try {
    fit.fit();
  } catch {
    /* container may be 0-sized momentarily */
  }

  const pty = openPty({
    cols: term.cols,
    rows: term.rows,
    onOutput: (chunk) => term.write(chunk),
    onExit: (code) => {
      try {
        term.writeln('');
        term.writeln(`\x1b[2m[process exited (${code})]\x1b[0m`);
      } catch {
        /* ignore */
      }
      opts.onExit?.(code);
    }
  });

  term.onData((data) => pty.send(data));
  term.onResize(({ cols, rows }) => pty.resize(cols, rows));

  _panes.set(key, { container, term, fit, pty, initialized: true });
  return { fit: () => safeFit(fit) };
}

/**
 * Detach the pane container from `host` (call on component unmount). The
 * container and the underlying Terminal/PTY stay alive in the registry,
 * ready for the next mountPane().
 */
export function unmountPane(instanceId: string, tabId: string, host: HTMLElement | null) {
  const key = paneKey(instanceId, tabId);
  const pane = _panes.get(key);
  if (!pane) return;
  if (host && pane.container.parentElement === host) {
    host.removeChild(pane.container);
  }
}

function safeFit(fit: import('@xterm/addon-fit').FitAddon) {
  try {
    fit.fit();
  } catch {
    /* ignore */
  }
}

function themeFromCss() {
  const css = getComputedStyle(document.documentElement);
  const rgb = (name: string) => {
    const v = css.getPropertyValue(name).trim();
    if (!v) return undefined;
    const [r, g, b] = v.split(/\s+/).map(Number);
    return `#${[r, g, b].map((n) => n.toString(16).padStart(2, '0')).join('')}`;
  };
  return {
    background: rgb('--surface') ?? '#1e1e2e',
    foreground: rgb('--fg') ?? '#cdd6f4',
    cursor: rgb('--accent') ?? '#89b4fa'
  };
}

// Clean up everything for an instance when the WM tells us the window is
// closed for real (not just unmounted during a toggle).
onAppDestroyed((instanceId) => {
  const state = _windows.get(instanceId);
  if (state) {
    for (const tab of state.tabs) {
      _disposePane(paneKey(instanceId, tab.id));
    }
    _windows.delete(instanceId);
  }
});

// Reset the windowSeq side-effect-free reference so dead-code stays out of
// the bundle for tests that import this module bare.
void _windowSeq;
