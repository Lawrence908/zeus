// zeus/frontend/src/components/jobs/JobExecutionFeed.tsx
//
// Polls /kronos/runs every 5s while the tab is visible. Pauses on
// document.visibilitychange. Click a row -> opens parent job's drawer.
import { useEffect, useState } from 'react'

import { useKronosStore } from '../../store/kronosStore'
import { JobStatusBadge } from './JobStatusBadge'
import { formatDuration, formatRelative } from './timeUtils'

interface Props {
  onSelectJob: (id: string) => void
}

export function JobExecutionFeed({ onSelectJob }: Props) {
  const runs = useKronosStore((s) => s.runs)
  const jobs = useKronosStore((s) => s.jobs)
  const refreshRuns = useKronosStore((s) => s.refreshRuns)
  const [open, setOpen] = useState(true)

  // Poll runs every 5s while the page is visible.
  useEffect(() => {
    let interval: ReturnType<typeof setInterval> | null = null

    const start = () => {
      if (interval !== null) return
      void refreshRuns()
      interval = setInterval(() => void refreshRuns(), 5000)
    }
    const stop = () => {
      if (interval !== null) {
        clearInterval(interval)
        interval = null
      }
    }
    const onVis = () => {
      if (document.hidden) stop()
      else start()
    }

    if (!document.hidden) start()
    document.addEventListener('visibilitychange', onVis)
    return () => {
      stop()
      document.removeEventListener('visibilitychange', onVis)
    }
  }, [refreshRuns])

  const jobNameById = new Map(jobs.map((j) => [j.id, j.name]))
  const recent = runs.slice(0, 25)

  return (
    <div className="border border-outline-variant/20 rounded bg-surface-container/30">
      <button
        onClick={() => setOpen((v) => !v)}
        className="w-full flex items-center justify-between gap-3 px-4 py-3 text-left"
      >
        <div className="flex items-center gap-3">
          <h2 className="font-headline font-semibold text-sm text-on-surface uppercase tracking-widest">
            Recent Executions
          </h2>
          <span className="text-[10px] font-mono text-on-surface-variant/50">
            {runs.length} total · refresh every 5s
          </span>
        </div>
        <span
          className="material-symbols-outlined text-on-surface-variant/60 transition-transform"
          style={{ fontSize: 18, transform: open ? 'rotate(180deg)' : undefined }}
        >
          expand_more
        </span>
      </button>
      {open && (
        <div className="border-t border-outline-variant/15">
          {recent.length === 0 ? (
            <p className="text-xs text-on-surface-variant/60 italic px-4 py-6 text-center">
              No runs yet. Trigger one via Run Now or wait for the next scheduled tick.
            </p>
          ) : (
            <ul>
              {recent.map((r) => (
                <li
                  key={r.id}
                  onClick={() => onSelectJob(r.job_id)}
                  className="flex items-center gap-3 px-4 py-2 border-b border-outline-variant/10 last:border-b-0 cursor-pointer hover:bg-surface-container-low/40 transition-colors"
                >
                  <JobStatusBadge status={r.status} />
                  <span className="font-body text-xs text-on-surface flex-1 truncate">
                    {jobNameById.get(r.job_id) ?? r.job_id}
                  </span>
                  <span className="text-[10px] font-mono text-on-surface-variant/60 shrink-0">
                    {formatRelative(r.started_at)}
                  </span>
                  <span className="text-[10px] font-mono text-on-surface-variant/40 shrink-0 w-14 text-right">
                    {formatDuration(r.duration_ms)}
                  </span>
                </li>
              ))}
            </ul>
          )}
        </div>
      )}
    </div>
  )
}
