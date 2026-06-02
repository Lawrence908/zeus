// src/lib/api/tools.ts — chat-path tool registry + invocation feed.
import { jsonFetch } from './base';

export interface ToolDirEntry {
  name: string;
  description: string;
  parameters?: Record<string, unknown>;
  aegis_policy?: string;
  result_aegis_policy?: string;
  cacheable?: boolean;
  timeout_seconds?: number;
}

export interface ToolInvocation {
  ts: string;
  tool: string;
  args?: Record<string, unknown>;
  content?: string;
  is_error?: boolean;
  cache_hit?: boolean;
  duration_ms?: number;
  aegis_flags?: string[];
  aegis_rejected?: boolean;
  source?: string;
}

export function listTools(): Promise<{ tools: ToolDirEntry[]; count: number; tools_enabled?: boolean }> {
  return jsonFetch('/admin/tools');
}

export function listInvocations(opts: { limit?: number; tool?: string } = {}): Promise<{
  invocations: ToolInvocation[];
  count: number;
}> {
  const params = new URLSearchParams();
  if (opts.limit) params.set('limit', String(opts.limit));
  if (opts.tool) params.set('tool', opts.tool);
  const q = params.toString();
  return jsonFetch(`/admin/tools/invocations${q ? '?' + q : ''}`);
}
