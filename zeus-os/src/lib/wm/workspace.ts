// src/lib/wm/workspace.ts — workspace state model.
import type { Node } from './tree';

export interface FloatingWindow {
  id: string;
  app: import('./tree').AppInstance;
  x: number;
  y: number;
  w: number;
  h: number;
  z: number;
}

export interface Workspace {
  id: number; // 1..10
  root: Node | null;
  focusId: string | null;
  floating: FloatingWindow[];
}

export function makeWorkspaces(count = 10): Workspace[] {
  const out: Workspace[] = [];
  for (let i = 1; i <= count; i += 1) {
    out.push({ id: i, root: null, focusId: null, floating: [] });
  }
  return out;
}

export function isEmpty(ws: Workspace): boolean {
  return ws.root === null && ws.floating.length === 0;
}
