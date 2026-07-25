// src/lib/api/models.ts — model selector + benchmark + admin settings.
import { jsonFetch } from './base';

export interface ModelInfo {
  name: string;
  size?: number | null;
  parameter_size?: string | null;
  quantization_level?: string | null;
  modified_at?: string | null;
  family?: string | null;
}

export interface ModelsList {
  provider: string;
  models: ModelInfo[];
}

export interface ActiveModel {
  provider: string;
  model: string;
  gpu_available?: boolean | null;
}

export function listModels(): Promise<ModelsList> {
  return jsonFetch('/models');
}

export function getActiveModel(): Promise<ActiveModel> {
  return jsonFetch('/models/active');
}

export function setActiveModel(model: string): Promise<ActiveModel> {
  return jsonFetch('/models/active', { method: 'POST', body: JSON.stringify({ model }) });
}

export function listBenchmarks(): Promise<Record<string, unknown>> {
  return jsonFetch('/models/benchmarks');
}

export function getAdminSettings(): Promise<Record<string, unknown>> {
  return jsonFetch('/admin/settings');
}

export function patchAdminSettings(patch: Record<string, unknown>): Promise<Record<string, unknown>> {
  return jsonFetch('/admin/settings', { method: 'PATCH', body: JSON.stringify(patch) });
}

export function getTelegramStatus(): Promise<Record<string, unknown>> {
  return jsonFetch('/integrations/telegram/status');
}
