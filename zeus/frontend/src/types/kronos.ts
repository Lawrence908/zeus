// zeus/frontend/src/types/kronos.ts
// Mirrors zeus/kronos/models.py. Keep in sync when backend models change.
// (No codegen yet — hand-written is fine while the surface is small.)

export type JobStatus =
  | 'pending'
  | 'running'
  | 'success'
  | 'failed'
  | 'timeout'
  | 'cancelled'
  | 'lost'

export type JobCategory =
  | 'briefing'
  | 'ingest'
  | 'memory_review'
  | 'maintenance'
  | 'research'
  | 'job_search'
  | 'health'
  | 'custom'

export interface JobSchedule {
  cron: string | null
  timezone: string
  run_at: string | null // ISO datetime for one-offs
}

export interface JobDefinition {
  id: string
  name: string
  description: string
  category: JobCategory
  schedule: JobSchedule
  executor: string | null
  agent: string | null
  endpoint: string
  params: Record<string, unknown>
  safety_policy: string
  timeout_seconds: number
  max_retries: number
  tags: string[]
  enabled: boolean
}

export interface JobRun {
  id: string
  job_id: string
  correlation_id: string
  status: JobStatus
  started_at: string
  finished_at: string | null
  duration_ms: number | null
  output_summary: string | null
  error: string | null
  attempts: number
}

export interface JobWithRuns {
  job: JobDefinition
  runs: JobRun[]
}

export interface UpcomingFire {
  job_id: string
  name: string
  next_fire: string // ISO
  timezone: string
}

export interface ExecutorInfo {
  dotted_path: string
  module: string
  function: string
  docstring: string | null
}

export interface KronosHealth {
  enabled: boolean
  reason?: string
  tick_count?: number
  last_tick_at?: string | null
  error_count?: number
  queue_depth?: number
  enabled_jobs?: number
}

export interface ManualRunResponse {
  job_id: string
  run_id: string
  correlation_id: string
}

export type StatusFilter = 'all' | 'enabled' | 'disabled' | 'failed' | 'overdue'

export interface KronosFilters {
  category: JobCategory | 'all'
  status: StatusFilter
  search: string
}

export type SortKey = 'name' | 'category' | 'next_fire' | 'last_run' | 'enabled'
export type SortDir = 'asc' | 'desc'

export interface SortPref {
  key: SortKey
  dir: SortDir
}
