// src/lib/api/integrations.ts — HA + Linear bridges.
import { jsonFetch } from './base';

export interface HaConfig {
  url: string;
  mode?: 'direct' | 'proxy';
  upstream?: string;
}

export interface LinearStatus {
  configured: boolean;
  team_key: string;
}

export function haConfig(): Promise<HaConfig> {
  return jsonFetch('/zeus-os/ha/config');
}

export function linearStatus(): Promise<LinearStatus> {
  return jsonFetch('/zeus-os/linear/status');
}

export function linearQuery<T = Record<string, unknown>>(
  query: string,
  variables: Record<string, unknown> = {}
): Promise<{ data?: T; errors?: { message: string }[] }> {
  return jsonFetch('/zeus-os/linear/query', {
    method: 'POST',
    body: JSON.stringify({ query, variables })
  });
}
