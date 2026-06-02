// src/lib/api/knowledge.ts — KnowledgeStore browser over /knowledge/*.
import { jsonFetch } from './base';

export interface KnowledgeEntry {
  id: string;
  text: string;
  source: string;
  source_id?: string;
  source_path?: string;
  chunk_index?: number;
  title?: string | null;
  url?: string | null;
  doc_type?: string | null;
  tags?: string[];
  created_at?: string;
  metadata?: Record<string, unknown>;
}

export interface KnowledgeListResponse {
  // Backend returns `entries`; accept the legacy `items` too.
  entries?: KnowledgeEntry[];
  items?: KnowledgeEntry[];
  count?: number;
  total?: number;
  next_offset?: number | null;
}

export interface KnowledgeFacetValue {
  value: string;
  count: number;
}

export interface KnowledgeFacetsResponse {
  // Backend returns facets flat at the top level keyed by facet name, plus a
  // `total` count. e.g. {total: 275326, source: [{value, count}, ...], doc_type: [...]}
  total: number;
  [facetName: string]: number | KnowledgeFacetValue[];
}

export function listKnowledge(opts: {
  source?: string;
  doc_type?: string;
  limit?: number;
  offset?: number;
} = {}): Promise<KnowledgeListResponse> {
  const p = new URLSearchParams();
  if (opts.source) p.set('source', opts.source);
  if (opts.doc_type) p.set('doc_type', opts.doc_type);
  if (opts.limit) p.set('limit', String(opts.limit));
  if (opts.offset) p.set('offset', String(opts.offset));
  const q = p.toString();
  return jsonFetch(`/knowledge/list${q ? '?' + q : ''}`);
}

export function knowledgeFacets(): Promise<KnowledgeFacetsResponse> {
  return jsonFetch('/knowledge/facets');
}

export function searchKnowledge(
  query: string,
  limit = 25
): Promise<{ query: string; results?: KnowledgeEntry[]; entries?: KnowledgeEntry[]; count?: number }> {
  return jsonFetch('/knowledge/search', {
    method: 'POST',
    body: JSON.stringify({ query, limit })
  });
}
