// zeus/frontend/src/api/kronos.ts
// Thin fetch wrappers over /kronos/*. All routes relative; the Vite dev proxy
// (or production same-origin mount) routes them to FastAPI on 8203.
import type {
  ExecutorInfo,
  JobCategory,
  JobDefinition,
  JobRun,
  JobStatus,
  JobWithRuns,
  KronosHealth,
  ManualRunResponse,
  UpcomingFire,
} from '../types/kronos'

async function jsonOrThrow<T>(res: Response): Promise<T> {
  if (!res.ok) {
    const body = (await res.json().catch(() => ({}))) as { detail?: string }
    throw new Error(body.detail ?? `HTTP ${res.status}`)
  }
  return (await res.json()) as T
}

function qs(params: Record<string, unknown>): string {
  const sp = new URLSearchParams()
  for (const [k, v] of Object.entries(params)) {
    if (v === undefined || v === null || v === '') continue
    sp.set(k, String(v))
  }
  const s = sp.toString()
  return s ? `?${s}` : ''
}

export const kronosApi = {
  health: async (): Promise<KronosHealth> =>
    jsonOrThrow(await fetch('/kronos/health')),

  listCategories: async (): Promise<JobCategory[]> =>
    jsonOrThrow(await fetch('/kronos/categories')),

  listExecutors: async (): Promise<ExecutorInfo[]> =>
    jsonOrThrow(await fetch('/kronos/executors')),

  listJobs: async (
    filters: { category?: JobCategory; enabled?: boolean } = {},
  ): Promise<JobDefinition[]> =>
    jsonOrThrow(await fetch(`/kronos/jobs${qs(filters)}`)),

  getJob: async (id: string): Promise<JobWithRuns> =>
    jsonOrThrow(await fetch(`/kronos/jobs/${encodeURIComponent(id)}`)),

  createJob: async (def: Partial<JobDefinition>): Promise<JobDefinition> =>
    jsonOrThrow(
      await fetch('/kronos/jobs', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(def),
      }),
    ),

  updateJob: async (
    id: string,
    patch: Partial<JobDefinition>,
  ): Promise<JobDefinition> =>
    jsonOrThrow(
      await fetch(`/kronos/jobs/${encodeURIComponent(id)}`, {
        method: 'PATCH',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(patch),
      }),
    ),

  deleteJob: async (id: string): Promise<{ deleted: boolean }> =>
    jsonOrThrow(
      await fetch(`/kronos/jobs/${encodeURIComponent(id)}`, { method: 'DELETE' }),
    ),

  runNow: async (id: string): Promise<ManualRunResponse> =>
    jsonOrThrow(
      await fetch(`/kronos/jobs/${encodeURIComponent(id)}/run`, { method: 'POST' }),
    ),

  enable: async (id: string): Promise<JobDefinition> =>
    jsonOrThrow(
      await fetch(`/kronos/jobs/${encodeURIComponent(id)}/enable`, { method: 'POST' }),
    ),

  disable: async (id: string): Promise<JobDefinition> =>
    jsonOrThrow(
      await fetch(`/kronos/jobs/${encodeURIComponent(id)}/disable`, { method: 'POST' }),
    ),

  listRuns: async (
    params: {
      job_id?: string
      status?: JobStatus
      since?: string
      limit?: number
    } = {},
  ): Promise<JobRun[]> =>
    jsonOrThrow(await fetch(`/kronos/runs${qs(params)}`)),

  getRun: async (id: string): Promise<JobRun> =>
    jsonOrThrow(await fetch(`/kronos/runs/${encodeURIComponent(id)}`)),

  upcoming: async (limit = 20): Promise<UpcomingFire[]> =>
    jsonOrThrow(await fetch(`/kronos/schedule/upcoming${qs({ limit })}`)),
}
