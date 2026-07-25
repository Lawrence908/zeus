// src/lib/api/memory.ts — MemoryStore CRUD over /memory/*.
import { jsonFetch } from './base';

// Backend returns `text` at the top level and a `metadata` blob with the
// extracted fact fields (category, confidence, valid_from, …). We expose a
// normalised view to the app via toEntry() — keep both names usable so older
// callers don't break.
export interface MemoryEntry {
  id: string;
  text?: string;
  memory?: string; // legacy synonym for text
  source?: string;
  source_id?: string;
  created_at?: string;
  updated_at?: string;
  metadata?: {
    category?: string | null;
    contains_pii?: boolean;
    confidence?: number;
    valid_from?: string | null;
    valid_until?: string | null;
    [k: string]: unknown;
  };
}

export interface MemoryListResponse {
  // Backend returns `entries`. Older mem0-era code used `memories`; accept both.
  entries?: MemoryEntry[];
  memories?: MemoryEntry[];
  count?: number;
  total?: number;
  next_offset?: number | null;
}

export interface MemorySourcesResponse {
  // /memory/sources returns a bare list of source names. The legacy shape
  // included per-source counts; we accept both for forward-compatibility.
  sources: (string | { source: string; count: number })[];
  total?: number;
}

export interface MemorySearchResponse {
  query: string;
  // Backend may use either `results` or `entries` depending on route version.
  results?: MemoryEntry[];
  entries?: MemoryEntry[];
  count?: number;
}

/** Extract the displayable body of a memory regardless of field name. */
export function memoryText(m: MemoryEntry): string {
  return m.text ?? m.memory ?? '';
}

/** Pull metadata fields up; returns a flat view for the UI. */
export function memoryView(m: MemoryEntry): {
  body: string;
  category: string | null;
  confidence: number | null;
  containsPii: boolean;
  validFrom: string | null;
  validUntil: string | null;
  source: string | null;
  sourceId: string | null;
} {
  const md = m.metadata ?? {};
  return {
    body: memoryText(m),
    category: (md.category as string | null) ?? null,
    confidence: typeof md.confidence === 'number' ? (md.confidence as number) : null,
    containsPii: !!md.contains_pii,
    validFrom: (md.valid_from as string | null) ?? null,
    validUntil: (md.valid_until as string | null) ?? null,
    source: m.source ?? (md.source as string | undefined) ?? null,
    sourceId: m.source_id ?? (md.source_id as string | undefined) ?? null
  };
}

export function listMemories(opts: {
  source?: string;
  limit?: number;
  offset?: number;
} = {}): Promise<MemoryListResponse> {
  const p = new URLSearchParams();
  if (opts.source) p.set('source', opts.source);
  if (opts.limit) p.set('limit', String(opts.limit));
  if (opts.offset) p.set('offset', String(opts.offset));
  const q = p.toString();
  return jsonFetch(`/memory/list${q ? '?' + q : ''}`);
}

export function listSources(): Promise<MemorySourcesResponse> {
  return jsonFetch('/memory/sources');
}

export function searchMemories(query: string, limit = 25): Promise<MemorySearchResponse> {
  return jsonFetch('/memory/search', {
    method: 'POST',
    body: JSON.stringify({ query, limit })
  });
}

export function getMemory(id: string): Promise<MemoryEntry> {
  return jsonFetch(`/memory/${encodeURIComponent(id)}`);
}

export function patchMemory(id: string, patch: Partial<MemoryEntry>): Promise<MemoryEntry> {
  return jsonFetch(`/memory/${encodeURIComponent(id)}`, {
    method: 'PATCH',
    body: JSON.stringify(patch)
  });
}

export function deleteMemory(id: string): Promise<{ ok: boolean }> {
  return jsonFetch(`/memory/${encodeURIComponent(id)}`, { method: 'DELETE' });
}

export interface MemoryAddResult {
  status: string;
  added: number;
  skipped: number;
  errors: string[];
}

export function addMemory(
  text: string,
  opts: { source?: string; extract_facts?: boolean } = {}
): Promise<MemoryAddResult> {
  return jsonFetch('/memory/add', {
    method: 'POST',
    body: JSON.stringify({
      text,
      source: opts.source ?? 'manual',
      extract_facts: opts.extract_facts ?? false
    })
  });
}

export function bulkDeleteMemories(ids: string[]): Promise<{ deleted: number }> {
  return jsonFetch('/memory/delete_batch', {
    method: 'POST',
    body: JSON.stringify({ ids })
  });
}
