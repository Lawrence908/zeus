// src/lib/wm/store.ts — Svelte stores that wire the WM together.
import { derived, get, writable } from 'svelte/store';

import {
  type AppInstance,
  type FocusDir,
  type Node,
  type Rect,
  type SplitDir,
  allLeaves,
  closeLeaf,
  computeRects,
  findLeaf,
  firstLeaf,
  focusInDirection,
  makeLeaf,
  moveInDirection,
  newId,
  splitLeaf,
  swapLeaves
} from './tree';
import { type FloatingWindow, type Workspace, makeWorkspaces } from './workspace';

export interface WmState {
  workspaces: Workspace[];
  activeWs: number;
}

const initial: WmState = {
  workspaces: makeWorkspaces(10),
  activeWs: 1
};

export const wm = writable<WmState>(initial);

export const viewport = writable<Rect>({ x: 0, y: 0, w: 1280, h: 720 });
export const gap = writable<number>(8);

export const activeWorkspace = derived(wm, ($wm) => $wm.workspaces[$wm.activeWs - 1]);

export const focusedLeafId = derived(activeWorkspace, ($w) => $w?.focusId ?? null);

export const rects = derived([activeWorkspace, viewport, gap], ([$w, $v, $g]) =>
  $w ? computeRects($w.root, $v, $g) : {}
);

export const leaves = derived(activeWorkspace, ($w) => ($w ? allLeaves($w.root) : []));

export const floating = derived(activeWorkspace, ($w) => ($w?.floating ?? []));

// ─── helpers ────────────────────────────────────────────────────────────────
function updateActive(mut: (ws: Workspace) => Workspace) {
  wm.update(($wm) => {
    const wsList = $wm.workspaces.slice();
    wsList[$wm.activeWs - 1] = mut(wsList[$wm.activeWs - 1]);
    return { ...$wm, workspaces: wsList };
  });
}

// ─── workspace switching ────────────────────────────────────────────────────
export function switchWorkspace(id: number) {
  if (id < 1 || id > 10) return;
  wm.update(($wm) => ({ ...$wm, activeWs: id }));
}

export function moveFocusedToWorkspace(id: number) {
  if (id < 1 || id > 10) return;
  const $wm = get(wm);
  if ($wm.activeWs === id) return;
  const ws = $wm.workspaces[$wm.activeWs - 1];
  if (!ws.focusId) return;
  const leaf = findLeaf(ws.root, ws.focusId);
  if (!leaf) return;
  const { root: rootAfter, focusId } = closeLeaf(ws.root, ws.focusId);
  const target = $wm.workspaces[id - 1];
  const { root: targetRoot, focusId: targetFocus } = splitLeaf(
    target.root,
    target.focusId,
    'h',
    leaf.app
  );
  const wsList = $wm.workspaces.slice();
  wsList[$wm.activeWs - 1] = { ...ws, root: rootAfter, focusId };
  wsList[id - 1] = { ...target, root: targetRoot, focusId: targetFocus };
  wm.set({ ...$wm, workspaces: wsList });
}

// ─── window ops ─────────────────────────────────────────────────────────────
export function openApp(app: AppInstance, dir: SplitDir = 'h') {
  updateActive((ws) => {
    const { root, focusId } = splitLeaf(ws.root, ws.focusId, dir, app);
    return { ...ws, root, focusId };
  });
}

export function closeFocused() {
  updateActive((ws) => {
    if (!ws.focusId) return ws;
    // Floating window?
    if (ws.floating.some((f) => f.id === ws.focusId)) {
      const remaining = ws.floating.filter((f) => f.id !== ws.focusId);
      return {
        ...ws,
        floating: remaining,
        focusId: remaining[remaining.length - 1]?.id ?? firstLeaf(ws.root)?.id ?? null
      };
    }
    const { root, focusId } = closeLeaf(ws.root, ws.focusId);
    return { ...ws, root, focusId: focusId ?? firstLeaf(root)?.id ?? null };
  });
}

export function focusLeaf(id: string) {
  updateActive((ws) => ({ ...ws, focusId: id }));
}

export function focusDir(dir: FocusDir) {
  const $wm = get(wm);
  const $v = get(viewport);
  const $g = get(gap);
  const ws = $wm.workspaces[$wm.activeWs - 1];
  const next = focusInDirection(ws.root, $v, $g, ws.focusId, dir);
  if (next && next !== ws.focusId) {
    focusLeaf(next);
  }
}

export function moveDir(dir: FocusDir) {
  const $wm = get(wm);
  const $v = get(viewport);
  const $g = get(gap);
  const ws = $wm.workspaces[$wm.activeWs - 1];
  if (!ws.focusId) return;
  const root = moveInDirection(ws.root, $v, $g, ws.focusId, dir);
  if (root && root !== ws.root) {
    updateActive((cur) => ({ ...cur, root }));
  }
}

export function setSplitDir(_dir: SplitDir) {
  // Future: convert nearest split to dir. No-op for Phase 1 (use openApp).
}

export function resizeFocused(_dir: 'h' | 'v', _delta: number) {
  // Placeholder for Super+Ctrl+arrow resize, Phase 1.5.
}

// ─── floating windows ───────────────────────────────────────────────────────
let _floatZCounter = 0;

function defaultFloatRect(viewport: Rect, fromTile?: Rect): { x: number; y: number; w: number; h: number } {
  if (fromTile) {
    return {
      x: Math.max(viewport.x, fromTile.x + 16),
      y: Math.max(viewport.y, fromTile.y + 16),
      w: Math.min(900, Math.max(360, fromTile.w)),
      h: Math.min(600, Math.max(240, fromTile.h))
    };
  }
  const w = Math.min(820, Math.max(360, viewport.w * 0.5));
  const h = Math.min(560, Math.max(240, viewport.h * 0.6));
  return {
    x: viewport.x + (viewport.w - w) / 2,
    y: viewport.y + (viewport.h - h) / 2,
    w,
    h
  };
}

export function toggleFloating() {
  const $wm = get(wm);
  const $v = get(viewport);
  const $g = get(gap);
  const ws = $wm.workspaces[$wm.activeWs - 1];
  if (!ws.focusId) return;

  // If the current focus is a floating window, return it to a tile.
  const floatHit = ws.floating.find((f) => f.id === ws.focusId);
  if (floatHit) {
    const newApp: AppInstance = { ...floatHit.app };
    const { root, focusId } = splitLeaf(ws.root, firstLeaf(ws.root)?.id ?? null, 'h', newApp);
    updateActive((cur) => ({
      ...cur,
      root,
      focusId,
      floating: cur.floating.filter((f) => f.id !== floatHit.id)
    }));
    return;
  }

  // Otherwise pull the focused tile out into a floating window.
  const leaf = findLeaf(ws.root, ws.focusId);
  if (!leaf) return;
  const rects = computeRects(ws.root, $v, $g);
  const fromTile = rects[leaf.id];
  const { root: rootAfter } = closeLeaf(ws.root, leaf.id);
  _floatZCounter += 1;
  const rect = defaultFloatRect($v, fromTile);
  const floating: FloatingWindow = {
    id: newId('f'),
    app: { ...leaf.app },
    x: rect.x,
    y: rect.y,
    w: rect.w,
    h: rect.h,
    z: _floatZCounter
  };
  updateActive((cur) => ({
    ...cur,
    root: rootAfter,
    focusId: floating.id,
    floating: [...cur.floating, floating]
  }));
}

export function updateFloating(id: string, patch: Partial<Pick<FloatingWindow, 'x' | 'y' | 'w' | 'h'>>) {
  updateActive((ws) => ({
    ...ws,
    floating: ws.floating.map((f) => (f.id === id ? { ...f, ...patch } : f))
  }));
}

export function raiseFloating(id: string) {
  _floatZCounter += 1;
  const z = _floatZCounter;
  updateActive((ws) => ({
    ...ws,
    focusId: id,
    floating: ws.floating.map((f) => (f.id === id ? { ...f, z } : f))
  }));
}

export function closeFloating(id: string) {
  updateActive((ws) => ({
    ...ws,
    focusId: ws.focusId === id ? (firstLeaf(ws.root)?.id ?? null) : ws.focusId,
    floating: ws.floating.filter((f) => f.id !== id)
  }));
}

export interface InitialApp {
  app: AppInstance;
  dir?: SplitDir;
  workspace?: number;
}

export function bootstrap(apps: InitialApp[] = []) {
  wm.update(($wm) => {
    const wsList = $wm.workspaces.slice();
    for (const a of apps) {
      const wsId = a.workspace ?? $wm.activeWs;
      const target = wsList[wsId - 1];
      const { root, focusId } = splitLeaf(target.root, target.focusId, a.dir ?? 'h', a.app);
      wsList[wsId - 1] = { ...target, root, focusId };
    }
    return { ...$wm, workspaces: wsList };
  });
}
