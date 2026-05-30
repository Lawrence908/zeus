// src/lib/wm/tree.ts — BSP tiling tree.
//
// A workspace is rooted at a Node. Splits carry a direction + ratio; leaves
// own a single window. Operations return a NEW tree (immutable update) so
// Svelte stores can subscribe cheaply.

export type SplitDir = 'h' | 'v'; // h = side-by-side (vertical split line)
                                  // v = stacked (horizontal split line)
export type FocusDir = 'left' | 'right' | 'up' | 'down';

export interface AppInstance {
  appId: string; // launcher id (e.g. "terminal")
  kind: string; // Svelte component key
  title: string;
  props?: Record<string, unknown>;
}

export type LeafNode = {
  kind: 'leaf';
  id: string;
  app: AppInstance;
};

export type SplitNode = {
  kind: 'split';
  dir: SplitDir;
  ratio: number; // 0..1, fraction taken by `a`
  a: Node;
  b: Node;
};

export type Node = LeafNode | SplitNode;

export interface Rect {
  x: number;
  y: number;
  w: number;
  h: number;
}

let _idCounter = 0;
export function newId(prefix = 'w'): string {
  _idCounter += 1;
  return `${prefix}-${_idCounter}-${Math.random().toString(36).slice(2, 6)}`;
}

export function makeLeaf(app: AppInstance): LeafNode {
  return { kind: 'leaf', id: newId(), app };
}

// ─── traversal helpers ───────────────────────────────────────────────────────
export function findLeaf(root: Node | null, id: string): LeafNode | null {
  if (!root) return null;
  if (root.kind === 'leaf') return root.id === id ? root : null;
  return findLeaf(root.a, id) ?? findLeaf(root.b, id);
}

export function allLeaves(root: Node | null): LeafNode[] {
  if (!root) return [];
  if (root.kind === 'leaf') return [root];
  return [...allLeaves(root.a), ...allLeaves(root.b)];
}

export function firstLeaf(root: Node | null): LeafNode | null {
  if (!root) return null;
  if (root.kind === 'leaf') return root;
  return firstLeaf(root.a) ?? firstLeaf(root.b);
}

// ─── geometry ────────────────────────────────────────────────────────────────
export function computeRects(root: Node | null, viewport: Rect, gap: number): Record<string, Rect> {
  const out: Record<string, Rect> = {};
  if (!root) return out;
  walk(root, viewport, gap, out);
  return out;
}

function walk(node: Node, rect: Rect, gap: number, out: Record<string, Rect>) {
  if (node.kind === 'leaf') {
    out[node.id] = rect;
    return;
  }
  if (node.dir === 'h') {
    const total = rect.w - gap;
    const wa = Math.max(40, Math.round(total * node.ratio));
    const wb = Math.max(40, total - wa);
    walk(node.a, { x: rect.x, y: rect.y, w: wa, h: rect.h }, gap, out);
    walk(node.b, { x: rect.x + wa + gap, y: rect.y, w: wb, h: rect.h }, gap, out);
  } else {
    const total = rect.h - gap;
    const ha = Math.max(40, Math.round(total * node.ratio));
    const hb = Math.max(40, total - ha);
    walk(node.a, { x: rect.x, y: rect.y, w: rect.w, h: ha }, gap, out);
    walk(node.b, { x: rect.x, y: rect.y + ha + gap, w: rect.w, h: hb }, gap, out);
  }
}

// ─── mutations ──────────────────────────────────────────────────────────────
// All operations are pure: they return a new (possibly partially shared) tree.

export function splitLeaf(
  root: Node | null,
  focusId: string | null,
  dir: SplitDir,
  newApp: AppInstance
): { root: Node; focusId: string } {
  const newLeaf = makeLeaf(newApp);
  if (!root) return { root: newLeaf, focusId: newLeaf.id };
  if (!focusId) {
    const first = firstLeaf(root);
    if (first) focusId = first.id;
  }
  if (!focusId) {
    const split: SplitNode = { kind: 'split', dir, ratio: 0.5, a: root, b: newLeaf };
    return { root: split, focusId: newLeaf.id };
  }
  const next = replaceLeaf(root, focusId, (leaf) => ({
    kind: 'split',
    dir,
    ratio: 0.5,
    a: leaf,
    b: newLeaf
  }));
  return { root: next ?? root, focusId: newLeaf.id };
}

function replaceLeaf(
  node: Node,
  id: string,
  replace: (leaf: LeafNode) => Node
): Node | null {
  if (node.kind === 'leaf') return node.id === id ? replace(node) : null;
  const ra = replaceLeaf(node.a, id, replace);
  if (ra) return { ...node, a: ra };
  const rb = replaceLeaf(node.b, id, replace);
  if (rb) return { ...node, b: rb };
  return null;
}

export function closeLeaf(root: Node | null, id: string): { root: Node | null; focusId: string | null } {
  if (!root) return { root: null, focusId: null };
  if (root.kind === 'leaf') {
    if (root.id === id) return { root: null, focusId: null };
    return { root, focusId: id };
  }
  const closed = removeIn(root, id);
  if (closed === null) return { root: null, focusId: null };
  if (closed === root) return { root, focusId: id };
  const nextFocus = firstLeaf(closed)?.id ?? null;
  return { root: closed, focusId: nextFocus };
}

function removeIn(node: Node, id: string): Node | null {
  if (node.kind === 'leaf') return node.id === id ? null : node;
  const a = removeIn(node.a, id);
  if (a === null) return node.b;
  if (a !== node.a) return { ...node, a };
  const b = removeIn(node.b, id);
  if (b === null) return node.a;
  if (b !== node.b) return { ...node, b };
  return node;
}

export function swapLeaves(root: Node, idA: string, idB: string): Node {
  if (idA === idB) return root;
  const a = findLeaf(root, idA);
  const b = findLeaf(root, idB);
  if (!a || !b) return root;
  let next = replaceLeaf(root, idA, () => b) ?? root;
  next = replaceLeaf(next, idB, () => a) ?? next;
  return next;
}

export function resizeSplit(root: Node, focusId: string, delta: number): Node {
  // Walk up the path to focusId; resize the nearest split whose dir matches
  // the direction the user is asking about. For Phase 1 we resize whatever
  // the nearest ancestor is.
  return resizeOnPath(root, focusId, delta) ?? root;
}

function resizeOnPath(node: Node, id: string, delta: number): Node | null {
  if (node.kind === 'leaf') return node.id === id ? node : null;
  const a = resizeOnPath(node.a, id, delta);
  if (a) {
    if (a !== node.a) return { ...node, a };
    return { ...node, ratio: clampRatio(node.ratio + delta) };
  }
  const b = resizeOnPath(node.b, id, delta);
  if (b) {
    if (b !== node.b) return { ...node, b };
    return { ...node, ratio: clampRatio(node.ratio - delta) };
  }
  return null;
}

function clampRatio(r: number): number {
  return Math.max(0.1, Math.min(0.9, r));
}

// ─── directional focus ───────────────────────────────────────────────────────
// We use the geometry pass and a simple "closest centroid in direction" search.
export function focusInDirection(
  root: Node | null,
  viewport: Rect,
  gap: number,
  focusId: string | null,
  dir: FocusDir
): string | null {
  if (!root) return null;
  const rects = computeRects(root, viewport, gap);
  if (!focusId || !rects[focusId]) {
    const first = firstLeaf(root);
    return first?.id ?? null;
  }
  const src = rects[focusId];
  const sx = src.x + src.w / 2;
  const sy = src.y + src.h / 2;
  let best: { id: string; d: number } | null = null;
  for (const [id, r] of Object.entries(rects)) {
    if (id === focusId) continue;
    const cx = r.x + r.w / 2;
    const cy = r.y + r.h / 2;
    if (dir === 'left' && cx >= sx - 1) continue;
    if (dir === 'right' && cx <= sx + 1) continue;
    if (dir === 'up' && cy >= sy - 1) continue;
    if (dir === 'down' && cy <= sy + 1) continue;
    const axis = dir === 'left' || dir === 'right' ? Math.abs(cx - sx) : Math.abs(cy - sy);
    const ortho = dir === 'left' || dir === 'right' ? Math.abs(cy - sy) : Math.abs(cx - sx);
    const d = axis + ortho * 0.5;
    if (!best || d < best.d) best = { id, d };
  }
  return best?.id ?? focusId;
}

export function moveInDirection(
  root: Node | null,
  viewport: Rect,
  gap: number,
  focusId: string | null,
  dir: FocusDir
): Node | null {
  if (!root || !focusId) return root;
  const targetId = focusInDirection(root, viewport, gap, focusId, dir);
  if (!targetId || targetId === focusId) return root;
  return swapLeaves(root, focusId, targetId);
}
