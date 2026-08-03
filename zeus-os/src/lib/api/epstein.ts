// src/lib/api/epstein.ts — browser client for the Epstein corpus workbench.
//
// PRIVATE BRANCH ONLY. Talks to zeus-core's /epstein/* router, which is a
// read-only proxy to the external corpus API. Co-occurrence is a signal about
// where to read, never an accusation.
import { jsonFetch } from './base';

export interface EpsteinHit {
  text: string;
  document_id: string;
  source_label: string;
  doc_type: string;
  chunk_index: string;
  score: number;
  citation: string;
}

export interface Citation {
  document_id: string;
  source_label: string;
}

export interface StatusResponse {
  enabled: boolean;
  reachable: boolean;
  error?: string;
  capabilities?: Record<string, unknown>;
  safety_rules?: string;
  graph_available?: boolean;
  doc_types?: Record<string, number>;
}

export interface SearchResponse {
  enabled: boolean;
  reachable: boolean;
  error?: string;
  query?: string;
  results?: EpsteinHit[];
  entities?: Record<string, unknown>;
}

export interface TimelineEvent {
  date: string;
  event_type: string;
  description: string;
}

export interface DossierResponse {
  enabled: boolean;
  reachable: boolean;
  error?: string;
  entity: string;
  graph_available?: boolean;
  confidence?: string;
  connections?: string[];
  timeline?: TimelineEvent[];
  doc_types?: string[];
  evidence?: EpsteinHit[];
  citations?: Citation[];
  gaps?: string[];
  safety_rules?: string;
  markdown?: string;
}

export interface ConnectionPair {
  a: string;
  b: string;
  connected: boolean;
  intermediaries: string[];
  events: { date?: string; description?: string }[];
  evidence: EpsteinHit[];
}

export interface GraphEdge {
  source: string;
  target: string;
  connected: boolean;
  relation: string;
  intermediaries: string[];
  evidence: Citation[];
}

export interface ConnectionsResponse {
  enabled: boolean;
  reachable: boolean;
  error?: string;
  entities: string[];
  graph_available?: boolean;
  confidence?: string;
  pairs?: ConnectionPair[];
  graph?: { nodes: { id: string; role: string }[]; edges: GraphEdge[] };
  citations?: Citation[];
  gaps?: string[];
  safety_rules?: string;
  markdown?: string;
}

export function epsteinStatus(): Promise<StatusResponse> {
  return jsonFetch<StatusResponse>('/epstein/status');
}

export function epsteinSearch(
  query: string,
  opts: { doc_type?: string; n_results?: number; expand_graph?: boolean } = {}
): Promise<SearchResponse> {
  return jsonFetch<SearchResponse>('/epstein/search', {
    method: 'POST',
    body: JSON.stringify({ query, ...opts })
  });
}

export function epsteinDossier(
  name: string,
  opts: { depth?: number; doc_type?: string } = {}
): Promise<DossierResponse> {
  return jsonFetch<DossierResponse>('/epstein/dossier', {
    method: 'POST',
    body: JSON.stringify({ name, ...opts })
  });
}

export function epsteinConnections(
  names: string[],
  opts: { depth?: number } = {}
): Promise<ConnectionsResponse> {
  return jsonFetch<ConnectionsResponse>('/epstein/connections', {
    method: 'POST',
    body: JSON.stringify({ names, ...opts })
  });
}
