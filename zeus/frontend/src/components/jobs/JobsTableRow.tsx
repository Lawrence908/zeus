// zeus/frontend/src/components/jobs/JobsTableRow.tsx
import { useKronosStore } from '../../store/kronosStore'
import type { JobDefinition, JobRun } from '../../types/kronos'
import { JobCategoryBadge } from './JobCategoryBadge'
import { JobStatusBadge } from './JobStatusBadge'
import { describeCron, formatDuration, formatRelative } from './timeUtils'

interface Props {
  job: JobDefinition
  lastRun: JobRun | undefined
  nextFire: Date | undefined
  onSelect: (id: string) => void
}

export function JobsTableRow({ job, lastRun, nextFire, onSelect }: Props) {
  const toggling = useKronosStore((s) => s.toggling[job.id] ?? false)
  const running = useKronosStore((s) => s.runningNow[job.id] ?? false)
  const toggleEnabled = useKronosStore((s) => s.toggleEnabled)
  const runJobNow = useKronosStore((s) => s.runJobNow)

  const failed = lastRun?.status === 'failed' || lastRun?.status === 'timeout' || lastRun?.status === 'lost'
  const overdue = nextFire !== undefined && nextFire.getTime() < Date.now()

  const scheduleText = job.schedule.cron
    ? describeCron(job.schedule.cron, job.schedule.timezone)
    : job.schedule.run_at
      ? `Once at ${formatRelative(job.schedule.run_at)}`
      : '—'

  return (
    <tr
      onClick={() => onSelect(job.id)}
      className={[
        'border-b border-outline-variant/10 cursor-pointer transition-colors',
        'hover:bg-surface-container/40',
        !job.enabled ? 'opacity-50' : '',
        failed ? 'border-l-2 border-l-error/60' : '',
      ].join(' ')}
    >
      <td className="py-2 px-3">
        <div className="font-body text-sm text-on-surface font-semibold">{job.name}</div>
        <div className="font-mono text-[10px] text-on-surface-variant/50">{job.id}</div>
      </td>
      <td className="py-2 px-3">
        <JobCategoryBadge category={job.category} />
      </td>
      <td className="py-2 px-3">
        <span
          className="text-xs font-body text-on-surface-variant"
          title={`${job.schedule.cron ?? job.schedule.run_at ?? ''} (${job.schedule.timezone})`}
        >
          {scheduleText}
        </span>
      </td>
      <td className="py-2 px-3">
        {nextFire ? (
          <span
            className={[
              'text-xs font-body',
              overdue ? 'text-orange-400' : 'text-on-surface-variant',
            ].join(' ')}
            title={nextFire.toLocaleString()}
          >
            {overdue ? `overdue · ${formatRelative(nextFire.toISOString())}` : formatRelative(nextFire.toISOString())}
          </span>
        ) : (
          <span className="text-xs font-body text-on-surface-variant/40">—</span>
        )}
      </td>
      <td className="py-2 px-3">
        {lastRun ? (
          <div className="flex items-center gap-2">
            <JobStatusBadge status={lastRun.status} />
            <span className="text-[10px] font-mono text-on-surface-variant/60">
              {formatRelative(lastRun.started_at)}
            </span>
            {lastRun.duration_ms !== null && (
              <span className="text-[10px] font-mono text-on-surface-variant/40">
                ({formatDuration(lastRun.duration_ms)})
              </span>
            )}
          </div>
        ) : (
          <span className="text-xs font-body text-on-surface-variant/40">never run</span>
        )}
      </td>
      <td className="py-2 px-3">
        <button
          onClick={(e) => {
            e.stopPropagation()
            void toggleEnabled(job.id)
          }}
          disabled={toggling}
          title={job.enabled ? 'Disable' : 'Enable'}
          className={[
            'inline-flex h-5 w-9 items-center rounded-full transition-colors disabled:opacity-50',
            job.enabled ? 'bg-primary' : 'bg-outline-variant/40',
          ].join(' ')}
        >
          <span
            className={[
              'inline-block h-4 w-4 rounded-full bg-on-primary transition-transform',
              job.enabled ? 'translate-x-4' : 'translate-x-1',
            ].join(' ')}
          />
        </button>
      </td>
      <td className="py-2 px-3 text-right">
        <button
          onClick={(e) => {
            e.stopPropagation()
            void runJobNow(job.id)
          }}
          disabled={running}
          className="px-2 py-1 text-[10px] font-label font-semibold uppercase tracking-widest rounded border border-primary/30 text-primary hover:bg-primary-container/20 transition-colors disabled:opacity-40"
        >
          {running ? 'Running...' : 'Run Now'}
        </button>
      </td>
    </tr>
  )
}
