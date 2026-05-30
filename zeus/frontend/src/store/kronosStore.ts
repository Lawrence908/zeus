// zeus/frontend/src/store/kronosStore.ts — Kronos page state.
//
// Three streams:
//   - jobs (refetched on mount, after every mutation, and every 30s)
//   - runs (polled every 5s while page is visible; pause on hidden tab)
//   - upcoming + health (polled every 30s with jobs)
//
// Filters and sort preference are persisted to localStorage under
// `kronos.table.prefs` so they survive reloads. Selected job lives in the
// store but is also reflected in the URL via ?job=<id> by the page.
import { create } from 'zustand'

import { kronosApi } from '../api/kronos'
import type {
  JobCategory,
  JobDefinition,
  JobRun,
  KronosFilters,
  KronosHealth,
  SortPref,
  UpcomingFire,
} from '../types/kronos'

const PREFS_KEY = 'kronos.table.prefs'

interface PersistedPrefs {
  filters?: KronosFilters
  sort?: SortPref
}

const DEFAULT_FILTERS: KronosFilters = {
  category: 'all',
  status: 'all',
  search: '',
}

const DEFAULT_SORT: SortPref = { key: 'name', dir: 'asc' }

function loadPrefs(): PersistedPrefs {
  try {
    const raw = localStorage.getItem(PREFS_KEY)
    return raw ? (JSON.parse(raw) as PersistedPrefs) : {}
  } catch {
    return {}
  }
}

function savePrefs(prefs: PersistedPrefs) {
  try {
    localStorage.setItem(PREFS_KEY, JSON.stringify(prefs))
  } catch {
    // localStorage unavailable; ignore
  }
}

interface KronosState {
  jobs: JobDefinition[]
  runs: JobRun[]
  upcoming: UpcomingFire[]
  health: KronosHealth | null

  filters: KronosFilters
  sort: SortPref

  loading: boolean
  error: string | null
  toggling: Record<string, boolean>
  runningNow: Record<string, boolean>

  // selectors / setters
  setFilter: <K extends keyof KronosFilters>(key: K, value: KronosFilters[K]) => void
  setSort: (sort: SortPref) => void

  // fetchers
  refreshJobs: () => Promise<void>
  refreshRuns: () => Promise<void>
  refreshUpcoming: () => Promise<void>
  refreshHealth: () => Promise<void>
  refreshAll: () => Promise<void>

  // mutations
  toggleEnabled: (id: string) => Promise<void>
  runJobNow: (id: string) => Promise<void>
  deleteJob: (id: string) => Promise<void>
  createJob: (def: Partial<JobDefinition>) => Promise<JobDefinition>
  updateJob: (id: string, patch: Partial<JobDefinition>) => Promise<JobDefinition>
}

export const useKronosStore = create<KronosState>((set, get) => {
  const prefs = loadPrefs()
  return {
    jobs: [],
    runs: [],
    upcoming: [],
    health: null,
    filters: { ...DEFAULT_FILTERS, ...(prefs.filters ?? {}) },
    sort: prefs.sort ?? DEFAULT_SORT,
    loading: false,
    error: null,
    toggling: {},
    runningNow: {},

    setFilter: (key, value) => {
      const filters = { ...get().filters, [key]: value }
      set({ filters })
      savePrefs({ filters, sort: get().sort })
    },

    setSort: (sort) => {
      set({ sort })
      savePrefs({ filters: get().filters, sort })
    },

    refreshJobs: async () => {
      set({ loading: true, error: null })
      try {
        const jobs = await kronosApi.listJobs()
        set({ jobs, loading: false })
      } catch (err) {
        set({ error: err instanceof Error ? err.message : String(err), loading: false })
      }
    },

    refreshRuns: async () => {
      try {
        const runs = await kronosApi.listRuns({ limit: 50 })
        set({ runs })
      } catch {
        // transient; next tick will retry
      }
    },

    refreshUpcoming: async () => {
      try {
        const upcoming = await kronosApi.upcoming(50)
        set({ upcoming })
      } catch {
        // transient
      }
    },

    refreshHealth: async () => {
      try {
        const health = await kronosApi.health()
        set({ health })
      } catch {
        set({ health: { enabled: false, reason: 'unreachable' } })
      }
    },

    refreshAll: async () => {
      await Promise.all([
        get().refreshJobs(),
        get().refreshRuns(),
        get().refreshUpcoming(),
        get().refreshHealth(),
      ])
    },

    toggleEnabled: async (id) => {
      const job = get().jobs.find((j) => j.id === id)
      if (!job) return
      // Optimistic update with rollback on failure.
      const prevJobs = get().jobs
      set({
        toggling: { ...get().toggling, [id]: true },
        jobs: prevJobs.map((j) => (j.id === id ? { ...j, enabled: !j.enabled } : j)),
      })
      try {
        const updated = job.enabled
          ? await kronosApi.disable(id)
          : await kronosApi.enable(id)
        set({
          jobs: get().jobs.map((j) => (j.id === id ? updated : j)),
        })
        void get().refreshUpcoming()
      } catch (err) {
        set({
          jobs: prevJobs,
          error: err instanceof Error ? err.message : String(err),
        })
      } finally {
        const t = { ...get().toggling }
        delete t[id]
        set({ toggling: t })
      }
    },

    runJobNow: async (id) => {
      set({ runningNow: { ...get().runningNow, [id]: true } })
      try {
        await kronosApi.runNow(id)
        // Give the executor a beat to write the row, then refresh runs.
        setTimeout(() => void get().refreshRuns(), 750)
      } catch (err) {
        set({ error: err instanceof Error ? err.message : String(err) })
      } finally {
        const r = { ...get().runningNow }
        delete r[id]
        set({ runningNow: r })
      }
    },

    deleteJob: async (id) => {
      try {
        await kronosApi.deleteJob(id)
        set({ jobs: get().jobs.filter((j) => j.id !== id) })
      } catch (err) {
        set({ error: err instanceof Error ? err.message : String(err) })
        throw err
      }
    },

    createJob: async (def) => {
      try {
        const created = await kronosApi.createJob(def)
        set({ jobs: [...get().jobs, created] })
        void get().refreshUpcoming()
        return created
      } catch (err) {
        set({ error: err instanceof Error ? err.message : String(err) })
        throw err
      }
    },

    updateJob: async (id, patch) => {
      try {
        const updated = await kronosApi.updateJob(id, patch)
        set({
          jobs: get().jobs.map((j) => (j.id === id ? updated : j)),
        })
        void get().refreshUpcoming()
        return updated
      } catch (err) {
        set({ error: err instanceof Error ? err.message : String(err) })
        throw err
      }
    },
  }
})

// -- Selectors --------------------------------------------------------------

export function selectFilteredJobs(state: KronosState): JobDefinition[] {
  const { jobs, filters, sort, runs } = state
  let out = jobs
  if (filters.category !== 'all') {
    out = out.filter((j) => j.category === filters.category)
  }
  if (filters.search.trim()) {
    const q = filters.search.toLowerCase()
    out = out.filter(
      (j) =>
        j.name.toLowerCase().includes(q) ||
        j.id.toLowerCase().includes(q) ||
        j.description.toLowerCase().includes(q),
    )
  }
  if (filters.status === 'enabled') out = out.filter((j) => j.enabled)
  else if (filters.status === 'disabled') out = out.filter((j) => !j.enabled)
  else if (filters.status === 'failed') {
    const lastByJob = lastRunByJob(runs)
    out = out.filter((j) => lastByJob.get(j.id)?.status === 'failed')
  } else if (filters.status === 'overdue') {
    // Backend overdue computation lives in /admin/metrics; for the table, a
    // job is "overdue" when its computed next_fire (from upcoming list) is in
    // the past relative to now.
    const now = Date.now()
    const next = nextFireByJob(state.upcoming)
    out = out.filter((j) => {
      const t = next.get(j.id)
      return t !== undefined && t.getTime() < now
    })
  }

  const sorted = [...out].sort((a, b) => compareJobs(a, b, sort, state))
  return sorted
}

export function lastRunByJob(runs: JobRun[]): Map<string, JobRun> {
  const m = new Map<string, JobRun>()
  for (const r of runs) {
    const existing = m.get(r.job_id)
    if (!existing || r.started_at > existing.started_at) {
      m.set(r.job_id, r)
    }
  }
  return m
}

export function nextFireByJob(upcoming: UpcomingFire[]): Map<string, Date> {
  const m = new Map<string, Date>()
  for (const u of upcoming) {
    const existing = m.get(u.job_id)
    const t = new Date(u.next_fire)
    if (!existing || t < existing) m.set(u.job_id, t)
  }
  return m
}

function compareJobs(
  a: JobDefinition,
  b: JobDefinition,
  sort: SortPref,
  state: KronosState,
): number {
  const dir = sort.dir === 'asc' ? 1 : -1
  switch (sort.key) {
    case 'name':
      return a.name.localeCompare(b.name) * dir
    case 'category':
      return a.category.localeCompare(b.category) * dir
    case 'enabled':
      return (Number(a.enabled) - Number(b.enabled)) * dir
    case 'next_fire': {
      const next = nextFireByJob(state.upcoming)
      const at = next.get(a.id)?.getTime() ?? Number.POSITIVE_INFINITY
      const bt = next.get(b.id)?.getTime() ?? Number.POSITIVE_INFINITY
      return (at - bt) * dir
    }
    case 'last_run': {
      const last = lastRunByJob(state.runs)
      const at = last.get(a.id)?.started_at ?? ''
      const bt = last.get(b.id)?.started_at ?? ''
      return at.localeCompare(bt) * dir
    }
    default:
      return 0
  }
}

export const KRONOS_CATEGORIES: JobCategory[] = [
  'briefing',
  'ingest',
  'memory_review',
  'maintenance',
  'research',
  'job_search',
  'health',
  'custom',
]
