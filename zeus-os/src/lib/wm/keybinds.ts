// src/lib/wm/keybinds.ts — keymap parser + dispatcher.
//
// Binding format: "Super+H", "Super+Shift+1", "Super+Return", "Ctrl+Space".
// Tokens are case-insensitive. Modifiers: Super (Meta), Ctrl, Alt, Shift.
// The user picks what physically stands in for "Super" via config:
//   - Meta:    the Win/Cmd key. Default, native on Linux.
//   - Alt:     the Alt key. Fallback when Linux host WM captures Meta.
//   - CtrlAlt: Ctrl+Alt chord. Required on Windows clients because Win+letter
//              is reserved by the OS before the browser sees it.

import type { ThemeId } from '$lib/themes';

export type ModifierName = 'Meta' | 'Alt' | 'Ctrl' | 'Shift';
export type ModifierMode = 'Meta' | 'Alt' | 'CtrlAlt';

export interface KeybindContext {
  modifier: ModifierMode;
}

export const MODIFIER_LABEL: Record<ModifierMode, string> = {
  Meta: 'Super',
  Alt: 'Alt',
  CtrlAlt: 'Ctrl+Alt'
};

export const MODIFIER_DESCRIPTION: Record<ModifierMode, string> = {
  Meta: 'Use the Win / ⌘ / Super key as the WM modifier. Native Linux feel.',
  Alt: 'Use Alt as the WM modifier. Use when your host WM steals Super.',
  CtrlAlt: 'Use Ctrl+Alt as the WM modifier. Required on Windows clients where Win+letter is captured by the OS.'
};

export type Action =
  | { kind: 'open'; appId: string; dir?: 'h' | 'v' }
  | { kind: 'close' }
  | { kind: 'focus'; dir: 'left' | 'down' | 'up' | 'right' }
  | { kind: 'move'; dir: 'left' | 'down' | 'up' | 'right' }
  | { kind: 'split'; dir: 'h' | 'v' }
  | { kind: 'workspace'; id: number }
  | { kind: 'moveToWorkspace'; id: number }
  | { kind: 'toggleLauncher' }
  | { kind: 'toggleFloating' }
  | { kind: 'cycleTheme' }
  | { kind: 'setTheme'; theme: ThemeId }
  | { kind: 'setModifier'; mode: ModifierMode }
  | { kind: 'cheatsheet' }
  | { kind: 'reload' };

export interface ParsedBind {
  super: boolean;
  ctrl: boolean;
  alt: boolean;
  shift: boolean;
  key: string; // normalized: lowercased, e.g. "h", "1", "return", "/"
}

export function parseBind(spec: string): ParsedBind | null {
  const parts = spec
    .split('+')
    .map((s) => s.trim())
    .filter(Boolean);
  if (!parts.length) return null;
  const out: ParsedBind = {
    super: false,
    ctrl: false,
    alt: false,
    shift: false,
    key: ''
  };
  for (const p of parts) {
    const lc = p.toLowerCase();
    if (lc === 'super' || lc === 'mod' || lc === 'meta' || lc === 'cmd') {
      out.super = true;
    } else if (lc === 'ctrl' || lc === 'control') {
      out.ctrl = true;
    } else if (lc === 'alt' || lc === 'option') {
      out.alt = true;
    } else if (lc === 'shift') {
      out.shift = true;
    } else {
      out.key = normalizeKey(p);
    }
  }
  if (!out.key) return null;
  return out;
}

function normalizeKey(k: string): string {
  const lc = k.toLowerCase();
  const aliases: Record<string, string> = {
    return: 'enter',
    esc: 'escape',
    spc: ' ',
    space: ' ',
    slash: '/'
  };
  return aliases[lc] ?? lc;
}

export function matchEvent(ev: KeyboardEvent, bind: ParsedBind, ctx: KeybindContext): boolean {
  // The "Super" bit consumes whatever physical modifier(s) the user picked.
  // For modes that include Ctrl or Alt in the Super chord, we ignore those
  // flags when checking the bind's own ctrl/alt fields so that bindings like
  // "Super+Shift+Q" still match without false-mismatching on the consumed mods.
  let superDown: boolean;
  let ctrlConsumed: boolean;
  let altConsumed: boolean;
  switch (ctx.modifier) {
    case 'Meta':
      superDown = ev.metaKey;
      ctrlConsumed = false;
      altConsumed = false;
      break;
    case 'Alt':
      superDown = ev.altKey;
      ctrlConsumed = false;
      altConsumed = true;
      break;
    case 'CtrlAlt':
    default:
      superDown = ev.ctrlKey && ev.altKey;
      // Only treat Ctrl/Alt as consumed when the chord actually used them as
      // Super; this lets non-super bindings like raw `Ctrl+Space` still match.
      ctrlConsumed = superDown;
      altConsumed = superDown;
      break;
  }
  if (bind.super !== superDown) return false;
  if (!ctrlConsumed && bind.ctrl !== ev.ctrlKey) return false;
  if (!altConsumed && bind.alt !== ev.altKey) return false;
  if (bind.shift !== ev.shiftKey) return false;
  return normalizeKey(ev.key) === bind.key;
}

export interface BindMap {
  spec: string;
  bind: ParsedBind;
  action: Action;
}

export function compile(map: Record<string, Action>): BindMap[] {
  const out: BindMap[] = [];
  for (const [spec, action] of Object.entries(map)) {
    const bind = parseBind(spec);
    if (bind) out.push({ spec, bind, action });
  }
  return out;
}

export const DEFAULT_KEYMAP: Record<string, Action> = {
  'Super+Return': { kind: 'open', appId: 'terminal' },
  'Super+D': { kind: 'toggleLauncher' },
  'Ctrl+Space': { kind: 'toggleLauncher' },
  'Super+Shift+Q': { kind: 'close' },
  'Super+F': { kind: 'toggleFloating' },
  'Super+R': { kind: 'cycleTheme' },
  'Super+Slash': { kind: 'cheatsheet' },
  'Super+H': { kind: 'focus', dir: 'left' },
  'Super+J': { kind: 'focus', dir: 'down' },
  'Super+K': { kind: 'focus', dir: 'up' },
  'Super+L': { kind: 'focus', dir: 'right' },
  'Super+Shift+H': { kind: 'move', dir: 'left' },
  'Super+Shift+J': { kind: 'move', dir: 'down' },
  'Super+Shift+K': { kind: 'move', dir: 'up' },
  'Super+Shift+L': { kind: 'move', dir: 'right' },
  'Super+V': { kind: 'split', dir: 'h' },
  'Super+S': { kind: 'split', dir: 'v' },
  'Super+1': { kind: 'workspace', id: 1 },
  'Super+2': { kind: 'workspace', id: 2 },
  'Super+3': { kind: 'workspace', id: 3 },
  'Super+4': { kind: 'workspace', id: 4 },
  'Super+5': { kind: 'workspace', id: 5 },
  'Super+6': { kind: 'workspace', id: 6 },
  'Super+7': { kind: 'workspace', id: 7 },
  'Super+8': { kind: 'workspace', id: 8 },
  'Super+9': { kind: 'workspace', id: 9 },
  'Super+0': { kind: 'workspace', id: 10 },
  'Super+Shift+1': { kind: 'moveToWorkspace', id: 1 },
  'Super+Shift+2': { kind: 'moveToWorkspace', id: 2 },
  'Super+Shift+3': { kind: 'moveToWorkspace', id: 3 },
  'Super+Shift+4': { kind: 'moveToWorkspace', id: 4 },
  'Super+Shift+5': { kind: 'moveToWorkspace', id: 5 },
  'Super+Shift+6': { kind: 'moveToWorkspace', id: 6 },
  'Super+Shift+7': { kind: 'moveToWorkspace', id: 7 },
  'Super+Shift+8': { kind: 'moveToWorkspace', id: 8 },
  'Super+Shift+9': { kind: 'moveToWorkspace', id: 9 },
  'Super+Shift+0': { kind: 'moveToWorkspace', id: 10 }
};
