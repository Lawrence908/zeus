// src/lib/api/fs.ts — REST client for /zeus-os/fs/*.
import { jsonFetch } from './base';

export interface FsEntry {
  name: string;
  kind: 'dir' | 'file' | 'link' | 'other';
  size: number;
  mtime: number;
}

export interface FsListing {
  path: string;
  entries: FsEntry[];
}

export interface FsRoots {
  read_roots: string[];
  write_roots: string[];
  write_enabled: boolean;
}

export interface FsReadResult {
  path: string;
  content: string;
  size_bytes: number;
  bytes_returned: number;
  truncated: boolean;
  mtime: number;
}

export function fsRoots(): Promise<FsRoots> {
  return jsonFetch<FsRoots>('/zeus-os/fs/roots');
}

export function fsList(path: string): Promise<FsListing> {
  return jsonFetch<FsListing>(`/zeus-os/fs/list?path=${encodeURIComponent(path)}`);
}

export function fsRead(path: string): Promise<FsReadResult> {
  return jsonFetch<FsReadResult>(`/zeus-os/fs/file?path=${encodeURIComponent(path)}`);
}
