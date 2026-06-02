// src/lib/api/kronos.ts — Kronos job scheduler client.
import { jsonFetch } from './base';

export interface JobDefinition {
  id: string;
  name?: string;
  description?: string;
  cron?: string | null;
  run_at?: string | null;
  executor: string;
  args?: Record<string, unknown>;
  enabled: boolean;
  category?: string;
  last_fired_at?: string | null;
  created_at?: string;
  updated_at?: string;
}

export interface JobRun {
  run_id: string;
  job_id: string;
  status: 'queued' | 'running' | 'success' | 'failed' | string;
  started_at?: string | null;
  finished_at?: string | null;
  error?: string | null;
  output?: string | null;
  duration_ms?: number | null;
}

export interface JobWithRuns extends JobDefinition {
  runs: JobRun[];
}

export interface ExecutorInfo {
  dotted_path: string;
  description?: string;
  category?: string;
}

export interface UpcomingFire {
  job_id: string;
  job_name?: string;
  fires_at: string;
}

export function listJobs(): Promise<{ jobs: JobDefinition[] }> {
  return jsonFetch('/kronos/jobs');
}

export function getJob(jobId: string): Promise<JobWithRuns> {
  return jsonFetch(`/kronos/jobs/${encodeURIComponent(jobId)}`);
}

export function listRuns(limit = 25): Promise<{ runs: JobRun[] }> {
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
