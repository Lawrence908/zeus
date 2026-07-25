// src/lib/api/obsidian.ts — Obsidian vault browser client.
import { jsonFetch } from './base';

export interface VaultNode {
  kind: 'dir' | 'doc' | 'image' | 'asset' | 'other';
  name: string;
  path: string;
  size?: number;
  mtime?: number;
  children?: VaultNode[];
}

export interface VaultTreeResponse {
  root: string;
  tree: VaultNode;
}

export interface VaultIndexResponse {
  root: string;
  by_title: Record<string, string[]>; // stem → [relative paths]
  paths: string[];
}

export interface VaultFileResponse {
  path: string;
  abs_path: string;
  content: string;
  rewritten: string;
  size_bytes: number;
}

export function vaultTree(): Promise<VaultTreeResponse> {
  return jsonFetch('/zeus-os/vault/tree');
}

export function vaultIndex(): Promise<VaultIndexResponse> {
  return jsonFetch('/zeus-os/vault/index');
}

export function vaultFile(path: string): Promise<VaultFileResponse> {
  return jsonFetch(`/zeus-os/vault/file?path=${encodeURIComponent(path)}`);
}

/**
 * Resolve an obsidian:// or obsidian-asset:// URI (emitted by the backend
 * markdown rewriter) against the vault index. Returns the relative path
 * inside the vault, or null when unresolved.
 */
export function resolveWikilink(
  target: string,
  index: VaultIndexResponse | null,
  currentPath: string | null
): string | null {
  if (!index) return null;
  const stem = target.replace(/\.(md|markdown)$/i, '');
  // Direct path match (e.g. "subfolder/Note") wins.
  if (index.paths.includes(stem + '.md')) return stem + '.md';
  if (index.paths.includes(stem)) return stem;
  // Stem-based: prefer the same-folder hit if any, else the first.
  const candidates = index.by_title[stem] ?? [];
  if (candidates.length === 0) return null;
  if (candidates.length === 1) return candidates[0];
  if (currentPath) {
    const folder = currentPath.split('/').slice(0, -1).join('/');
    const sibling = candidates.find((c) => c.startsWith(folder + '/'));
    if (sibling) return sibling;
  }
  return candidates[0];
}
