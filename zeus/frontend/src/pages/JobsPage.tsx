// zeus/frontend/src/pages/JobsPage.tsx — Kronos `/jobs` dashboard.
//
// Phase 1: sortable filterable table, scheduler health indicator,
// detail drawer (Overview + History), enable/disable toggle, Run Now,
// polling execution feed. Create/Edit form + cron builder land in Phase 2.
//
// Selection is held in the URL (?job=<id>) — single source of truth — so the
// drawer is deep-linkable and we avoid ping-ponging effects between the URL
// and a duplicate store field.
import { useCallback, useEffect, useState } from 'react'
import { useSearchParams } from 'react-router-dom'

import { JobCreateModal } from '../components/jobs/JobCreateModal'
import { JobDetailDrawer } from '../components/jobs/JobDetailDrawer'
import { JobExecutionFeed } from '../components/jobs/JobExecutionFeed'
import { JobFilters } from '../components/jobs/JobFilters'
import { JobsTable } from '../components/jobs/JobsTable'
import { formatRelative } from '../components/jobs/timeUtils'
import { UpcomingTimeline } from '../components/jobs/UpcomingTimeline'
import { TopNav } from '../components/layout/TopNav'
import { useKronosStore } from '../store/kronosStore'

type ViewMode = 'table' | 'timeline'
const VIEW_MODE_KEY = 'kronos.view'

function loadViewMode(): ViewMode {
  try {
    const v = localStorage.getItem(VIEW_MODE_KEY)
    return v === 'timeline' ? 'timeline' : 'table'
  } catch {
    return 'table'
  }
}

export function JobsPage() {
  const [searchParams, setSearchParams] = useSearchParams()
  const selectedJobId = searchParams.get('job')
  const [showCreate, setShowCreate] = useState(false)
  const [view, setView] = useState<ViewMode>(loadViewMode)

  const setViewPersistent = (v: ViewMode) => {
    setView(v)
    try {
      localStorage.setItem(VIEW_MODE_KEY, v)
    } catch {
      // ignore
    }
  }

  const refreshAll = useKronosStore((s) => s.refreshAll)
  const error = useKronosStore((s) => s.error)
  const jobs = useKronosStore((s) => s.jobs)

  // Initial load + 30s refresh for jobs/upcoming/health.
  useEffect(() => {
    void refreshAll()
    const id = setInterval(() => void refreshAll(), 30_000)
    return () => clearInterval(id)
  }, [refreshAll])

  const onSelect = useCallback(
    (id: string) => {
      setSearchParams(
        (prev) => {
          const next = new URLSearchParams(prev)
          next.set('job', id)
          return next
        },
        { replace: true },
      )
    },
    [setSearchParams],
  )

  const onClose = useCallback(() => {
    setSearchParams(
      (prev) => {
        const next = new URLSearchParams(prev)
        next.delete('job')
        return next
      },
      { replace: true },
    )
  }, [setSearchParams])

  return (
    <div className="flex flex-col h-screen bg-background">
      <TopNav />

      <div className="flex-1 overflow-y-auto custom-scrollbar pt-[52px]">
        <div className="max-w-7xl mx-auto px-4 md:px-6 py-6 md:py-8">
          {/* Header */}
          <div className="mb-6 flex flex-col sm:flex-row sm:items-start sm:justify-between gap-3 sm:gap-4">
            <div>
              <div className="flex items-center gap-3 mb-1">
                <h1 className="font-headline font-bold text-2xl text-on-surface">Jobs</h1>
                <SchedulerHealthBadge />
              </div>
              <p className="font-body text-sm text-on-surface-variant">
                Kronos cron-driven scheduler. {jobs.length} job{jobs.length === 1 ? '' : 's'}{' '}
                registered.
              </p>
            </div>
            <button
              onClick={() => setShowCreate(true)}
              className="px-3 py-1.5 text-[10px] font-label font-semibold uppercase tracking-widest rounded transition-all"
              style={{ backgroundColor: '#00d4ff', color: '#003642' }}
            >
              + New Job
            </button>
          </div>

          {error && (
            <div className="mb-4 rounded border border-error/40 bg-error-container/20 text-error px-3 py-2 text-sm">
              {error}
            </div>
          )}

          <div className="mb-4 flex items-center gap-3">
            <div className="flex-1">
              <JobFilters />
            </div>
            <div className="flex items-center gap-1 rounded border border-outline-variant/30 bg-surface-container-high p-0.5 shrink-0">
              {(['table', 'timeline'] as ViewMode[]).map((v) => (
                <button
                  key={v}
                  onClick={() => setViewPersistent(v)}
                  className={[
                    'px-2 py-1 text-[10px] font-label uppercase tracking-widest rounded transition-colors',
                    view === v
                      ? 'bg-primary text-on-primary'
                      : 'text-on-surface-variant hover:text-on-surface',
                  ].join(' ')}
                >
                  {v}
                </button>
              ))}
            </div>
          </div>

          <div className="mb-6">
            {view === 'table' ? (
              <JobsTable onSelect={onSelect} />
            ) : (
              <UpcomingTimeline onSelect={onSelect} />
            )}
          </div>

          <JobExecutionFeed onSelectJob={onSelect} />
        </div>
      </div>

      {selectedJobId && <JobDetailDrawer jobId={selectedJobId} onClose={onClose} />}

      {showCreate && (
        <JobCreateModal
          onClose={() => setShowCreate(false)}
          onCreated={(job) => {
            setShowCreate(false)
            void refreshAll()
            onSelect(job.id)
          }}
        />
      )}
    </div>
  )
}

function SchedulerHealthBadge() {
  const health = useKronosStore((s) => s.health)
  if (!health) {
    return (
      <span className="inline-flex items-center gap-2 text-[10px] font-label uppercase tracking-widest text-on-surface-variant/50">
        <span className="w-1.5 h-1.5 rounded-full bg-outline" />
        unknown
      </span>
    )
  }
  if (!health.enabled) {
    return (
      <span
        className="inline-flex items-center gap-2 text-[10px] font-label uppercase tracking-widest text-error"
        title={health.reason ?? 'Kronos scheduler is not running'}
      >
        <span className="w-1.5 h-1.5 rounded-full bg-error" />
        scheduler off
      </span>
    )
  }
  const ageOk =
    !!health.last_tick_at &&
    Date.now() - new Date(health.last_tick_at).getTime() < 120_000
  const tooltip = [
    `tick_count: ${health.tick_count ?? 0}`,
    `errors: ${health.error_count ?? 0}`,
    health.last_tick_at ? `last tick: ${formatRelative(health.last_tick_at)}` : 'no ticks yet',
  ].join(' · ')
  return (
    <span
      className={[
        'inline-flex items-center gap-2 text-[10px] font-label uppercase tracking-widest',
        ageOk ? 'text-primary' : 'text-orange-400',
      ].join(' ')}
      title={tooltip}
    >
      <span
        className={[
          'w-1.5 h-1.5 rounded-full',
          ageOk ? 'bg-primary' : 'bg-orange-400',
          ageOk ? 'animate-pulse' : '',
        ].join(' ')}
      />
      scheduler {ageOk ? 'ok' : 'stale'}
    </span>
  )
}
