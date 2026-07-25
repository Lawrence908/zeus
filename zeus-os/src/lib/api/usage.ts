// src/lib/api/usage.ts — LLM token usage analytics.
import { jsonFetch } from './base';

export interface UsageSeriesPoint {
  bucket: string; // YYYY-MM-DD or YYYY-MM-DDTHH:00
  provider: string;
  tokens_in: number;
  tokens_out: number;
  cost_usd: number;
  calls: number;
}

export interface UsageRollup {
  provider?: string;
  model?: string;
  caller?: string;
  tokens: number;
  cost_usd: number;
  calls: number;
}

export interface UsageResponse {
  series: UsageSeriesPoint[];
  by_provider: UsageRollup[];
  by_model: UsageRollup[];
  by_caller: UsageRollup[];
  totals: {
    tokens: number;
    tokens_in: number;
    tokens_out: number;
    cost_usd: number;
    calls: number;
  };
  window: { since_days: number; bucket: string };
  note?: string;
}

export function loadUsage(opts: {
  bucket?: 'day' | 'hour';
  since_days?: number;
  provider?: string;
  caller?: string;
} = {}): Promise<UsageResponse> {
  const p = new URLSearchParams();
  if (opts.bucket) p.set('bucket', opts.bucket);
  if (opts.since_days) p.set('since_days', String(opts.since_days));
  if (opts.provider) p.set('provider', opts.provider);
  if (opts.caller) p.set('caller', opts.caller);
  const q = p.toString();
  return jsonFetch<UsageResponse>(`/admin/llm_usage${q ? '?' + q : ''}`);
}

export function importHistoric(): Promise<{
  status: string;
  note: string;
  import_dir: string;
  found_files: string[];
}> {
  return jsonFetch('/admin/llm_usage/import', { method: 'POST' });
}
