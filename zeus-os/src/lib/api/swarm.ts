// src/lib/api/swarm.ts — client for the Argo swarm (/swarm/*).
import { jsonFetch } from './base';

export type RunStatus =
  | 'pending_plan_approval'
  | 'running'
  | 'pending_final_approval'
  | 'completed'
  | 'completed_partial'
  | 'failed'
  | 'cancelled'
  | 'paused_budget';

export type NodeStatus =
  | 'blocked'
  | 'ready'
  | 'pending_approval'
  | 'running'
  | 'succeeded'
  | 'failed'
  | 'skipped'
  | 'unreachable';

export type ApprovalKind = 'plan' | 'node_write' | 'budget' | 'final';
export type ApprovalState = 'pending' | 'approved' | 'rejected';

export interface Run {
  id: string;
  goal: string;
  repo: string;
  status: RunStatus;
  budget_usd: number;
  max_parallel: number;
  dry_run: boolean;
  created_at: string;
  updated_at: string;
}

export interface TaskNode {
  run_id: string;
  id: string;
  title: string;
  deps: string[];
  status: NodeStatus;
  attempts: number;
  cost_usd: number;
  requires_approval: boolean;
  check: string;
  model: string;
  error?: string | null;
  output?: string | null;
}

export interface RunEstimate {
  total_usd: number;
  per_node: Record<string, number>;
}

export interface Approval {
  id: string;
  run_id: string;
  kind: ApprovalKind;
  node_id?: string | null;
  state: ApprovalState;
}

export interface RunView {
  run: Run;
  nodes: TaskNode[];
  approvals: Approval[];
  estimate?: RunEstimate | null;
}

export function swarmHealth(): Promise<{ enabled: boolean }> {
  return jsonFetch('/swarm/health');
}

export function listRuns(limit = 50): Promise<Run[]> {
  return jsonFetch(`/swarm/runs?limit=${limit}`);
}

export function getRun(id: string): Promise<RunView> {
  return jsonFetch(`/swarm/runs/${encodeURIComponent(id)}`);
}

export function planRun(goal: string, repo: string, dryRun = false): Promise<RunView> {
  return jsonFetch('/swarm/plan', {
    method: 'POST',
    body: JSON.stringify({ goal, repo, dry_run: dryRun })
  });
}

export function approve(runId: string, approvalId: string, approve: boolean): Promise<RunView> {
  return jsonFetch(`/swarm/runs/${encodeURIComponent(runId)}/approve`, {
    method: 'POST',
    body: JSON.stringify({ approval_id: approvalId, approve })
  });
}

export function killRun(runId: string): Promise<RunView> {
  return jsonFetch(`/swarm/runs/${encodeURIComponent(runId)}/kill`, { method: 'POST' });
}
