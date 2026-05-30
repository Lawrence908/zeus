// src/lib/api/apps.ts — launcher app registry.
import { jsonFetch } from './base';

export interface AppEntry {
  id: string;
  title: string;
  icon: string;
  kind: string;
  default_workspace?: number;
}

export function listApps(): Promise<{ apps: AppEntry[] }> {
  return jsonFetch<{ apps: AppEntry[] }>('/zeus-os/apps');
}
