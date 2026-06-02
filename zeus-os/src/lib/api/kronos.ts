// src/lib/api/kronos.ts — Kronos job scheduler client.
import { jsonFetch } from './base';

export interface JobSchedule {
  cron: string | null;
  timezone: string;
  run_at: string | null;
}

export interface JobDefinition {
  id: string;
  name: string;
  description: string;
  category: string;
  schedule: JobSchedule;
  executor: string | null;
  agent: string | null;
  endpoint: string;
  params: Record<string, unknown>;
  safety_policy: string;
  timeout_seconds: number;
  max_retries: number;
  tags: string[];
  enabled: boolean;
  last_fired_at?: string | null;
}

export interface JobRun {
  id: string;
  job_id: string;
  correlation_id?: string;
  status: 'pending' | 'running' | 'success' | 'failed' | 'timeout' | 'cancelled' | 'lost' | string;
  started_at: string;
  finished_at: string | null;
  duration_ms: number | null;
  output_summary?: string | null;
  error?: string | null;
  attempts?: number;
}

export interface JobWithRuns extends JobDefinition {
  runs: JobRun[];
}

export interface ExecutorInfo {
  dotted_path: string;
  module?: string;
  function?: string;
  docstring?: string | null;
}

export interface UpcomingFire {
  job_id: string;
  name?: string;
  next_fire: string;
  timezone?: string;
}

export function listJobs(): Promise<JobDefinition[]> {
  return jsonFetch('/kronos/jobs');
}

export function getJob(jobId: string): Promise<JobWithRuns> {
  return jsonFetch(`/kronos/jobs/${encodeURIComponent(jobId)}`);
}

export function listRuns(limit = 25): Promise<JobRun[]> {
  return jsonFetch(`/kronos/runs?limit=${limit}`);
}

export function listExecutors(): Promise<ExecutorInfo[]> {
  return jsonFetch('/kronos/executors');
}

export function listUpcoming(): Promise<UpcomingFire[]> {
  return jsonFetch('/kronos/schedule/upcoming');
}

export function createJob(def: Partial<JobDefinition>): Promise<JobDefinition> {
  return jsonFetch('/kronos/jobs', { method: 'POST', body: JSON.stringify(def) });
}

export function patchJob(jobId: string, patch: Partial<JobDefinition>): Promise<JobDefinition> {
  return jsonFetch(`/kronos/jobs/${encodeURIComponent(jobId)}`, {
    method: 'PATCH',
    body: JSON.stringify(patch)
  });
}

export function deleteJob(jobId: string): Promise<{ ok: boolean }> {
  return jsonFetch(`/kronos/jobs/${encodeURIComponent(jobId)}`, { method: 'DELETE' });
}

export function runJobNow(jobId: string): Promise<{ run_id: string }> {
  return jsonFetch(`/kronos/jobs/${encodeURIComponent(jobId)}/run`, { method: 'POST' });
}

export function setJobEnabled(jobId: string, enabled: boolean): Promise<JobDefinition> {
  const action = enabled ? 'enable' : 'disable';
  return jsonFetch(`/kronos/jobs/${encodeURIComponent(jobId)}/${action}`, { method: 'POST' });
}
