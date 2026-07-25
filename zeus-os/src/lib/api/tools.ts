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
  source?: string; // 'chat' | 'mcp' on the wire — many tools are registered in both
  sources?: string[]; // populated client-side after dedupe (e.g. ['chat', 'mcp'])
  write_gated?: boolean;
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

export interface ToolsDirectory {
  tools: ToolDirEntry[];
  // Chat-path loop state (gates POST /admin/tools/invoke).
  chat?: { enabled: boolean; max_calls_per_query: number; count: number };
  mcp?: { write_enabled: boolean; count: number };
}

export function listTools(): Promise<ToolsDirectory> {
  return jsonFetch('/admin/tools');
}

export interface ToolInvokeResult {
  tool: string;
  content: string;
  is_error: boolean;
  duration_ms: number;
}

export function invokeTool(
  tool: string,
  args: Record<string, unknown>
): Promise<ToolInvokeResult> {
  return jsonFetch('/admin/tools/invoke', {
    method: 'POST',
    body: JSON.stringify({ tool, arguments: args })
  });
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
