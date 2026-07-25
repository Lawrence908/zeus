// src/lib/api/orchestration.ts — agent runtime + tasks over /orchestration/*.
import { jsonFetch } from './base';

export interface AgentInfo {
  name: string;
  description?: string;
  status?: string;
  model?: string;
  // Backend may serialise models as either {dev, prod} or list of names.
  models?: string[] | Record<string, string>;
  tools?: string[];
  auto_start?: boolean;
  safety_policy?: string;
  error?: string | null;
  uptime_seconds?: number;
  last_seen?: string | null;
}

export interface OrchestrationStatusRaw {
  // Backend returns agents as a dict {name: AgentInfo}. Keep the raw shape
  // around in case callers want the surrounding metadata.
  agents: Record<string, Omit<AgentInfo, 'name'>>;
  environment?: string;
  ruflo_version?: string;
  active_model?: string;
  metrics?: Record<string, unknown>;
}

export interface OrchestrationStatus {
  agents: AgentInfo[];
  environment?: string;
  ruflo_version?: string;
  active_model?: string;
  metrics?: Record<string, unknown>;
}

export interface AgentTask {
  task_id: string;
  agent: string;
  description?: string;
  status: 'pending' | 'running' | 'done' | 'failed' | string;
  elapsed_ms?: number | null;
  step_count?: number;
  results_count?: number;
  // Legacy field names kept for older backends.
  action?: string;
  error?: string | null;
}

// Mirrors the backend TaskRecord (zeus/orchestration/runtime.py). Each result is
// a StepResult: { step_name, status, data, error, duration_ms }. Note the output
// payload is `data`, not `output`.
export interface AgentStepResult {
  step_name?: string;
  status?: string;
  data?: unknown;
  error?: string | null;
  duration_ms?: number;
  [k: string]: unknown;
}

export interface AgentTaskDetail {
  id: string;
  agent_name: string;
  description?: string;
  status: string;
  elapsed_ms?: number | null;
  steps?: { name?: string; endpoint?: string; [k: string]: unknown }[];
  results?: AgentStepResult[];
  [k: string]: unknown;
}

export async function getStatus(): Promise<OrchestrationStatus> {
  const raw = await jsonFetch<OrchestrationStatusRaw>('/orchestration/status');
  // Normalise: agents come as a dict; flatten into an array with name on the row.
  const agents: AgentInfo[] = [];
  const rawAgents = raw.agents ?? {};
  if (Array.isArray(rawAgents)) {
    // Forward-compat: if backend ever switches to array form, accept it.
    for (const a of rawAgents as unknown as AgentInfo[]) agents.push(a);
  } else {
    for (const [name, info] of Object.entries(rawAgents)) {
      agents.push({ name, ...(info as Omit<AgentInfo, 'name'>) });
    }
  }
  return {
    agents,
    environment: raw.environment,
    ruflo_version: raw.ruflo_version,
    active_model: raw.active_model,
    metrics: raw.metrics
  };
}

export function listTasks(): Promise<AgentTask[] | { tasks: AgentTask[] }> {
  return jsonFetch('/orchestration/tasks');
}

export function getTask(taskId: string): Promise<AgentTaskDetail> {
  return jsonFetch(`/orchestration/tasks/${encodeURIComponent(taskId)}`);
}

export function createTask(req: {
  agent: string;
  action: string;
  args?: Record<string, unknown>;
}): Promise<AgentTask> {
  return jsonFetch('/orchestration/tasks', {
    method: 'POST',
    body: JSON.stringify(req)
  });
}
