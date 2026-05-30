// src/lib/api/config.ts — user config persistence.
import { jsonFetch } from './base';
import type { ThemeId } from '$lib/themes';

export interface ZeusOsConfig {
  theme: ThemeId;
  modifier: 'Meta' | 'Alt';
  gap_px: number;
  pinned: Record<string, string>; // workspaceId → appId
  keybinds: Record<string, string>; // spec → action serialized
}

export function loadConfig(): Promise<ZeusOsConfig> {
  return jsonFetch<ZeusOsConfig>('/zeus-os/config');
}

export function saveConfig(cfg: ZeusOsConfig): Promise<{ ok: boolean; path: string }> {
  return jsonFetch<{ ok: boolean; path: string }>('/zeus-os/config', {
    method: 'PUT',
    body: JSON.stringify(cfg)
  });
}
