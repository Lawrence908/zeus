// zeus/frontend/src/components/jobs/JobDetailDrawer.tsx
//
// Slide-in drawer from the right with four tabs: Overview, History, Output,
// Edit. Phase 1 shipped Overview + History; Phase 2 adds Output (full text of
// the latest run with copy) and Edit (JobForm + delete danger zone).
import { useEffect, useMemo, useState } from 'react'

import { kronosApi } from '../../api/kronos'
import { nextFireByJob, useKronosStore } from '../../store/kronosStore'
import type { JobDefinition, JobRun } from '../../types/kronos'
import { JobCategoryBadge } from './JobCategoryBadge'
import { JobForm } from './JobForm'
import { JobStatusBadge } from './JobStatusBadge'
import {
  describeCron,
  formatAbsolute,
  formatDuration,
  formatRelative,
} from './timeUtils'

type Tab = 'overview' | 'history' | 'output' | 'edit'

interface Props {
  jobId: string
  onClose: () => void
}

export function JobDetailDrawer({ jobId, onClose }: Props) {
  const [tab, setTab] = useState<Tab>('overview')
  const [job, setJob] = useState<JobDefinition | null>(null)
  const [runs, setRuns] = useState<JobRun[]>([])
  const [error, setError] = useState<string | null>(null)
  const [loading, setLoading] = useState(false)
  const [refreshKey, setRefreshKey] = useState(0)

  const upcoming = useKronosStore((s) => s.upcoming)
  const toggleEnabled = useKronosStore((s) => s.toggleEnabled)
  const runJobNow = useKronosStore((s) => s.runJobNow)
  const deleteJob = useKronosStore((s) => s.deleteJob)
  const toggling = useKronosStore((s) => s.toggling[jobId] ?? false)
  const running = useKronosStore((s) => s.runningNow[jobId] ?? false)
  const refreshAll = useKronosStore((s) => s.refreshAll)

  const latestRun = useMemo(() => runs[0] ?? null, [runs])

  useEffect(() => {
    let cancelled = false
    setLoading(true)
    setError(null)
    void kronosApi
      .getJob(jobId)
      .then((data) => {
        if (cancelled) return
        setJob(data.job)
        setRuns(data.runs)
      })
      .catch((err: unknown) => {
        if (!cancelled) setError(err instanceof Error ? err.message : String(err))
      })
      .finally(() => {
        if (!cancelled) setLoading(false)
      })
    return () => {
      cancelled = true
    }
  }, [jobId, refreshKey])

  // ESC closes
  useEffect(() => {
    const onKey = (e: KeyboardEvent) => {
      if (e.key === 'Escape') onClose()
    }
    window.addEventListener('keydown', onKey)
    return () => window.removeEventListener('keydown', onKey)
  }, [onClose])

  const nextFire = nextFireByJob(upcoming).get(jobId)

  return (
    <>
      {/* Backdrop */}
      <div
        onClick={onClose}
        className="fixed inset-0 bg-black/40 z-40 transition-opacity"
      />

      {/* Drawer */}
      <aside className="fixed right-0 top-0 bottom-0 w-full sm:w-[560px] bg-surface-container-low border-l border-outline-variant/20 z-50 flex flex-col shadow-2xl">
        {/* Header */}
        <header className="flex items-center justify-between gap-3 px-5 py-4 border-b border-outline-variant/15">
          <div className="min-w-0">
            <h2 className="font-headline font-bold text-base text-on-surface truncate">
              {job?.name ?? jobId}
            </h2>
            {job && (
              <div className="flex items-center gap-2 mt-1">
                <JobCategoryBadge category={job.category} />
                <span className="text-[10px] font-mono text-on-surface-variant/50">{job.id}</span>
              </div>
            )}
          </div>
          <button
            onClick={onClose}
            className="w-8 h-8 flex items-center justify-center text-on-surface-variant hover:text-on-surface"
            title="Close (Esc)"
          >
            <span className="material-symbols-outlined text-[20px]">close</span>
          </button>
        </header>

        {/* Tabs */}
        <nav className="flex border-b border-outline-variant/15 px-5">
          {(['overview', 'history', 'output', 'edit'] as Tab[]).map((t) => (
            <button
              key={t}
              onClick={() => setTab(t)}
              className={[
                'px-3 py-2 text-xs font-label uppercase tracking-widest transition-colors',
                tab === t
                  ? 'text-primary border-b-2 border-primary -mb-px'
                  : 'text-on-surface-variant hover:text-on-surface',
              ].join(' ')}
            >
              {t}
              {t === 'history' && ` (${runs.length})`}
            </button>
          ))}
          <div className="flex-1" />
          <button
            onClick={() => {
              setRefreshKey((k) => k + 1)
              void refreshAll()
            }}
            className="text-xs font-label text-on-surface-variant hover:text-on-surface px-2"
            title="Refresh"
          >
            <span className="material-symbols-outlined text-[16px]">refresh</span>
          </button>
        </nav>

        {/* Body */}
        <div className="flex-1 overflow-y-auto custom-scrollbar p-5">
          {error && (
            <div className="mb-4 rounded border border-error/40 bg-error-container/20 text-error px-3 py-2 text-xs">
              {error}
            </div>
          )}
          {loading && !job && (
            <p className="text-xs text-on-surface-variant/60 italic">Loading...</p>
          )}
          {job && tab === 'overview' && (
            <OverviewTab
              job={job}
              nextFire={nextFire}
              toggling={toggling}
              running={running}
              onToggle={() => void toggleEnabled(job.id)}
              onRunNow={() => {
                void runJobNow(job.id)
                // Bump local refreshKey shortly after so History reflects the new run.
                setTimeout(() => setRefreshKey((k) => k + 1), 1000)
              }}
            />
          )}
          {job && tab === 'history' && <HistoryTab runs={runs} />}
          {job && tab === 'output' && <OutputTab run={latestRun} />}
          {job && tab === 'edit' && (
            <JobForm
              mode="edit"
              initial={job}
              onSaved={(updated) => {
                setJob(updated)
                setTab('overview')
                void refreshAll()
              }}
              onCancel={() => setTab('overview')}
              onDelete={async () => {
                await deleteJob(job.id)
                onClose()
              }}
            />
          )}
        </div>
      </aside>
    </>
  )
}

// ---------------------------------------------------------------------------
// Output tab — full text of the latest run + copy button
// ---------------------------------------------------------------------------

function OutputTab({ run }: { run: JobRun | null }) {
  const [copied, setCopied] = useState(false)

  if (!run) {
    return (
      <p className="text-xs text-on-surface-variant/60 italic text-center py-8">
        No runs to inspect yet.
      </p>
    )
  }

  const body = run.output_summary ?? run.error ?? ''
  const handleCopy = async () => {
    try {
      await navigator.clipboard.writeText(body)
      setCopied(true)
      setTimeout(() => setCopied(false), 1500)
    } catch {
      // ignore — older browsers / no clipboard permission
    }
  }

  return (
    <div className="space-y-3">
      <div className="flex items-center justify-between gap-3">
        <div className="flex items-center gap-2">
          <JobStatusBadge status={run.status} size="sm" />
          <span className="text-[10px] font-mono text-on-surface-variant/60">
            {formatAbsolute(run.started_at)}
          </span>
          <span className="text-[10px] font-mono text-on-surface-variant/40">
            ({formatDuration(run.duration_ms)})
          </span>
        </div>
        <button
          onClick={() => void handleCopy()}
          disabled={!body}
          className="px-2 py-1 text-[10px] font-label font-semibold uppercase tracking-widest rounded border border-outline-variant/40 hover:border-primary/30 hover:text-primary transition-colors disabled:opacity-40"
        >
          {copied ? 'Copied' : 'Copy'}
        </button>
      </div>
      <div className="text-[10px] font-mono text-on-surface-variant/50">
        correlation: {run.correlation_id} · attempts: {run.attempts}
      </div>
      {run.error && (
        <pre className="text-xs font-mono text-error whitespace-pre-wrap bg-surface-container-lowest/60 border border-error/30 rounded px-3 py-2">
          {run.error}
        </pre>
      )}
      {run.output_summary && (
        <pre className="text-xs font-mono text-on-surface-variant whitespace-pre-wrap break-all bg-surface-container-lowest/60 border border-outline-variant/15 rounded px-3 py-2">
          {run.output_summary}
        </pre>
      )}
      {!run.error && !run.output_summary && (
        <p className="text-xs text-on-surface-variant/40 italic">No output recorded.</p>
      )}
    </div>
  )
}

// ---------------------------------------------------------------------------
// Overview tab
// ---------------------------------------------------------------------------

interface OverviewProps {
  job: JobDefinition
  nextFire: Date | undefined
  toggling: boolean
  running: boolean
  onToggle: () => void
  onRunNow: () => void
}

function OverviewTab({ job, nextFire, toggling, running, onToggle, onRunNow }: OverviewProps) {
  const scheduleText = job.schedule.cron
    ? describeCron(job.schedule.cron, job.schedule.timezone)
    : job.schedule.run_at
      ? `Once at ${formatAbsolute(job.schedule.run_at)}`
      : '—'

  return (
    <div className="space-y-5">
      {/* Description */}
      {job.description && (
        <p className="font-body text-sm text-on-surface-variant leading-relaxed">
          {job.description}
        </p>
      )}

      {/* Action row */}
      <div className="flex flex-wrap items-center gap-3">
        <button
          onClick={onRunNow}
          disabled={running}
          className="px-3 py-1.5 text-[10px] font-label font-semibold uppercase tracking-widest rounded border border-primary/30 text-primary hover:bg-primary-container/20 transition-colors disabled:opacity-40"
        >
          {running ? 'Running...' : 'Run Now'}
        </button>
        <button
          onClick={onToggle}
          disabled={toggling}
          className={[
            'px-3 py-1.5 text-[10px] font-label font-semibold uppercase tracking-widest rounded border transition-colors disabled:opacity-40',
            job.enabled
              ? 'border-error/30 text-error hover:bg-error-container/20'
              : 'border-primary/30 text-primary hover:bg-primary-container/20',
          ].join(' ')}
        >
          {toggling ? '...' : job.enabled ? 'Disable' : 'Enable'}
        </button>
        <span className="text-[10px] font-label text-on-surface-variant/50 ml-auto">
          {job.enabled ? 'enabled' : 'disabled'}
        </span>
      </div>

      {/* Definition grid */}
      <DefinitionGrid
        rows={[
          ['Schedule', scheduleText],
          [
            'Raw cron',
            job.schedule.cron ?? job.schedule.run_at ?? '—',
            job.schedule.timezone,
          ],
          ['Next fire', nextFire ? `${nextFire.toLocaleString()} (${formatRelative(nextFire.toISOString())})` : '—'],
          ['Executor', job.executor ?? `agent: ${job.agent ?? '—'}`],
          job.agent ? ['Endpoint', job.endpoint] : null,
          ['Safety policy', job.safety_policy],
          ['Timeout', `${job.timeout_seconds}s`],
          ['Max retries', String(job.max_retries)],
          job.tags.length > 0 ? ['Tags', job.tags.join(', ')] : null,
        ].filter(Boolean) as Array<[string, string, string?]>}
      />

      {/* Params */}
      <div>
        <h3 className="text-[10px] font-label uppercase tracking-widest text-on-surface-variant/60 mb-2">
          Params
        </h3>
        <pre className="text-xs font-mono bg-surface-container-lowest/60 border border-outline-variant/15 rounded px-3 py-2 text-on-surface-variant whitespace-pre-wrap break-all">
          {JSON.stringify(job.params, null, 2)}
        </pre>
      </div>
    </div>
  )
}

function DefinitionGrid({ rows }: { rows: Array<[string, string, string?]> }) {
  return (
    <dl className="grid grid-cols-[120px_1fr] gap-y-2 gap-x-4 text-xs">
      {rows.map(([label, value, suffix], i) => (
        <div key={i} className="contents">
          <dt className="text-[10px] font-label uppercase tracking-widest text-on-surface-variant/60 self-start pt-0.5">
            {label}
          </dt>
          <dd className="font-body text-on-surface break-words">
            {value}
            {suffix && (
              <span className="text-on-surface-variant/50 text-[10px] ml-2">({suffix})</span>
            )}
          </dd>
        </div>
      ))}
    </dl>
  )
}

// ---------------------------------------------------------------------------
// History tab
// ---------------------------------------------------------------------------

function HistoryTab({ runs }: { runs: JobRun[] }) {
  const [expanded, setExpanded] = useState<Record<string, boolean>>({})

  if (runs.length === 0) {
    return (
      <p className="text-xs text-on-surface-variant/60 italic text-center py-8">
        No runs recorded yet.
      </p>
    )
  }

  return (
    <div className="space-y-1">
      {runs.map((r) => {
        const open = expanded[r.id] ?? false
        return (
          <div
            key={r.id}
            className="border border-outline-variant/15 rounded bg-surface-container-lowest/40"
          >
            <button
              onClick={() =>
                setExpanded((prev) => ({ ...prev, [r.id]: !prev[r.id] }))
              }
              className="w-full flex items-center justify-between gap-3 px-3 py-2 text-left"
            >
              <div className="flex items-center gap-2 min-w-0">
                <JobStatusBadge status={r.status} />
                <span className="text-[10px] font-mono text-on-surface-variant/60 truncate">
                  {formatAbsolute(r.started_at)}
                </span>
              </div>
              <div className="flex items-center gap-2 shrink-0">
                <span className="text-[10px] font-mono text-on-surface-variant/50">
                  {formatDuration(r.duration_ms)}
                </span>
                <span
                  className="material-symbols-outlined text-on-surface-variant/40 transition-transform"
                  style={{ fontSize: 16, transform: open ? 'rotate(180deg)' : undefined }}
                >
                  expand_more
                </span>
              </div>
            </button>
            {open && (
              <div className="px-3 pb-3 text-xs">
                <div className="mb-2 text-[10px] font-mono text-on-surface-variant/50">
                  correlation: {r.correlation_id} · attempts: {r.attempts}
                </div>
                {r.error && (
                  <pre className="text-error whitespace-pre-wrap font-mono mb-2">{r.error}</pre>
                )}
                {r.output_summary && (
                  <pre className="text-on-surface-variant whitespace-pre-wrap font-mono break-all">
                    {r.output_summary}
                  </pre>
                )}
                {!r.error && !r.output_summary && (
                  <span className="text-on-surface-variant/40 italic">No output recorded.</span>
                )}
              </div>
            )}
          </div>
        )
      })}
    </div>
  )
}
