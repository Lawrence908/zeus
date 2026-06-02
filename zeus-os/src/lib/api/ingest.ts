// src/lib/api/ingest.ts — ingest trigger + stats over /ingest/* and /admin/ingest/stats.
import { jsonFetch } from './base';

export interface IngestCollectionInfo {
  points_count: number | null;
  vectors_count?: number | null;
  indexed_vectors_count?: number | null;
  status?: string;
}

export interface IngestStats {
  // Backend returns {collections: {name → CollectionInfo}}; we normalise to an
  // array in the app for table rendering.
  collections?: Record<string, IngestCollectionInfo>;
  total_points?: number;
  last_ingest_at?: string | null;
  error?: string;
}

export interface IngestTriggerRequest {
  source: string;
  args?: Record<string, unknown>;
}

export interface IngestTriggerResponse {
  source: string;
  status: 'queued' | 'started' | 'done' | string;
  job_id?: string;
  detail?: string;
}

export function getIngestStats(): Promise<IngestStats> {
  return jsonFetch('/admin/ingest/stats');
}

export function triggerIngest(req: IngestTriggerRequest): Promise<IngestTriggerResponse> {
  return jsonFetch('/ingest/trigger', {
    method: 'POST',
    body: JSON.stringify(req)
  });
}
