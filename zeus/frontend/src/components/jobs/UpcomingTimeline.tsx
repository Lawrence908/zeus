// zeus/frontend/src/components/jobs/UpcomingTimeline.tsx
//
// Horizontal upcoming-fires timeline. Rows by category; each block is one
// scheduled fire of a job. Computes fires client-side from job.schedule.cron
// (or job.schedule.run_at) using cron-parser, since /kronos/schedule/upcoming
// only returns the soonest fire per job.
//
// Click a block -> opens that job's detail drawer via onSelect.
import { useMemo, useState } from 'react'

import { CronExpressionParser } from 'cron-parser'
import { useShallow } from 'zustand/react/shallow'

import { selectFilteredJobs, useKronosStore } from '../../store/kronosStore'
import type { JobCategory, JobDefinition } from '../../types/kronos'
import { formatRelative } from './timeUtils'

interface Props {
  onSelect: (id: string) => void
}

type WindowKey = '24h' | '7d'

const WINDOW_HOURS: Record<WindowKey, number> = {
  '24h': 24,
  '7d': 24 * 7,
}

// Cap per job to keep DOM size reasonable for dense crons (e.g. * * * * *).
const MAX_FIRES_PER_JOB = 200

const CATEGORY_BLOCK_CLASS: Record<JobCategory, string> = {
  briefing: 'bg-blue-500/70 hover:bg-blue-400 border-blue-300',
  ingest: 'bg-emerald-500/70 hover:bg-emerald-400 border-emerald-300',
  memory_review: 'bg-purple-500/70 hover:bg-purple-400 border-purple-300',
  maintenance: 'bg-zinc-500/70 hover:bg-zinc-400 border-zinc-300',
  research: 'bg-orange-500/70 hover:bg-orange-400 border-orange-300',
  job_search: 'bg-pink-500/70 hover:bg-pink-400 border-pink-300',
  health: 'bg-cyan-500/70 hover:bg-cyan-400 border-cyan-300',
  custom: 'bg-on-surface-variant/70 hover:bg-on-surface-variant border-outline-variant',
}

export function UpcomingTimeline({ onSelect }: Props) {
  const jobs = useKronosStore(useShallow(selectFilteredJobs))
  const [windowKey, setWindowKey] = useState<WindowKey>('24h')

  // Recompute every time `jobs` or `windowKey` changes. Note: this does NOT
  // tick with the clock; the page-level 30s refresh re-triggers store updates,
  // which causes selectFilteredJobs to return a new array, which re-renders us.
  const { rows, ticks, start, end, totalFires, capped } = useMemo(
    () => buildTimeline(jobs, windowKey),
    [jobs, windowKey],
  )

  return (
    <div className="border border-outline-variant/20 rounded bg-surface-container/30">
      <header className="flex items-center justify-between gap-3 px-4 py-3 border-b border-outline-variant/15">
        <div className="flex items-center gap-3">
          <h2 className="font-headline font-semibold text-sm text-on-surface uppercase tracking-widest">
            Upcoming
          </h2>
          <span className="text-[10px] font-mono text-on-surface-variant/50">
            {totalFires} fire{totalFires === 1 ? '' : 's'} across {rows.length} categor
            {rows.length === 1 ? 'y' : 'ies'}
            {capped && ' · some jobs capped'}
          </span>
        </div>
        <div className="flex items-center gap-1 rounded border border-outline-variant/30 bg-surface-container-high p-0.5">
          {(['24h', '7d'] as WindowKey[]).map((k) => (
            <button
              key={k}
              onClick={() => setWindowKey(k)}
              className={[
                'px-2 py-0.5 text-[10px] font-label uppercase tracking-widest rounded transition-colors',
                windowKey === k
                  ? 'bg-primary text-on-primary'
                  : 'text-on-surface-variant hover:text-on-surface',
              ].join(' ')}
            >
              {k}
            </button>
          ))}
        </div>
      </header>

      {rows.length === 0 ? (
        <p className="text-xs text-on-surface-variant/60 italic px-4 py-8 text-center">
          No upcoming fires in the next {windowKey}. Enable a recurring job, or
          widen the filters.
        </p>
      ) : (
        <div className="p-4">
          <div className="space-y-2">
            {rows.map((row) => (
              <CategoryRow
                key={row.category}
                row={row}
                start={start}
                end={end}
                onSelect={onSelect}
              />
            ))}
          </div>

          {/* Scale */}
          <div className="relative mt-4 h-6 border-t border-outline-variant/30 ml-[120px]">
            {ticks.map((t, i) => (
              <div
                key={i}
                className="absolute top-0 h-2 border-l border-outline-variant/30"
                style={{ left: `${t.pct}%` }}
              >
                <span className="absolute top-2 -translate-x-1/2 text-[10px] font-mono text-on-surface-variant/60 whitespace-nowrap">
                  {t.label}
                </span>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}

// ---------------------------------------------------------------------------
// Row — one category band with all its blocks
// ---------------------------------------------------------------------------

interface RowFire {
  job: JobDefinition
  at: Date
}

interface CategoryRowData {
  category: JobCategory
  fires: RowFire[]
}

function CategoryRow({
  row,
  start,
  end,
  onSelect,
}: {
  row: CategoryRowData
  start: Date
  end: Date
  onSelect: (id: string) => void
}) {
  const span = end.getTime() - start.getTime()
  const blockClass = CATEGORY_BLOCK_CLASS[row.category] ?? CATEGORY_BLOCK_CLASS.custom

  return (
    <div className="flex items-center gap-3">
      <div className="w-[120px] shrink-0">
        <span className="text-[10px] font-label uppercase tracking-widest text-on-surface-variant/70">
          {row.category.replace('_', ' ')}
        </span>
      </div>
      <div className="relative flex-1 h-7 rounded bg-surface-container-lowest/50 border border-outline-variant/15">
        {/* "Now" tick at the start of the window */}
        <div className="absolute left-0 top-0 bottom-0 border-l border-primary/40" />
        {row.fires.map((fire, i) => {
          const pct = ((fire.at.getTime() - start.getTime()) / span) * 100
          if (pct < 0 || pct > 100) return null
          return (
            <button
              key={`${fire.job.id}-${i}`}
              onClick={() => onSelect(fire.job.id)}
              title={`${fire.job.name} — ${fire.at.toLocaleString()} (${formatRelative(
                fire.at.toISOString(),
              )})`}
              className={[
                'absolute top-0.5 bottom-0.5 w-2 rounded-sm border transition-all hover:scale-y-110',
                blockClass,
              ].join(' ')}
              style={{ left: `calc(${pct}% - 4px)` }}
            />
          )
        })}
      </div>
    </div>
  )
}

// ---------------------------------------------------------------------------
// Compute helpers
// ---------------------------------------------------------------------------

interface TimelineData {
  rows: CategoryRowData[]
  ticks: { pct: number; label: string }[]
  start: Date
  end: Date
  totalFires: number
  capped: boolean
}

function buildTimeline(jobs: JobDefinition[], windowKey: WindowKey): TimelineData {
  const start = new Date()
  const end = new Date(start.getTime() + WINDOW_HOURS[windowKey] * 3600 * 1000)

  const enabled = jobs.filter((j) => j.enabled)

  const byCategory = new Map<JobCategory, RowFire[]>()
  let totalFires = 0
  let capped = false

  for (const job of enabled) {
    const fires = computeFires(job, start, end)
    if (fires.length === MAX_FIRES_PER_JOB) capped = true
    if (fires.length === 0) continue
    totalFires += fires.length
    const list = byCategory.get(job.category) ?? []
    for (const at of fires) {
      list.push({ job, at })
    }
    byCategory.set(job.category, list)
  }

  const rows: CategoryRowData[] = []
  // Order categories by first-fire time so the busiest soonest sits on top.
  const ordered = Array.from(byCategory.entries()).sort((a, b) => {
    const at = Math.min(...a[1].map((f) => f.at.getTime()))
    const bt = Math.min(...b[1].map((f) => f.at.getTime()))
    return at - bt
  })
  for (const [category, fires] of ordered) {
    fires.sort((a, b) => a.at.getTime() - b.at.getTime())
    rows.push({ category, fires })
  }

  return {
    rows,
    ticks: buildTicks(start, end, windowKey),
    start,
    end,
    totalFires,
    capped,
  }
}

function computeFires(job: JobDefinition, start: Date, end: Date): Date[] {
  if (job.schedule.run_at) {
    const t = new Date(job.schedule.run_at)
    return t >= start && t <= end ? [t] : []
  }
  if (!job.schedule.cron) return []
  try {
    const expr = CronExpressionParser.parse(job.schedule.cron, {
      tz: job.schedule.timezone || 'UTC',
      currentDate: start,
    })
    const out: Date[] = []
    while (out.length < MAX_FIRES_PER_JOB) {
      const next = expr.next().toDate()
      if (next > end) break
      out.push(next)
    }
    return out
  } catch {
    return []
  }
}

function buildTicks(
  start: Date,
  end: Date,
  windowKey: WindowKey,
): { pct: number; label: string }[] {
  const span = end.getTime() - start.getTime()
  const tickCount = windowKey === '24h' ? 5 : 8 // every 6h, or every day
  const out: { pct: number; label: string }[] = []
  for (let i = 0; i <= tickCount; i++) {
    const pct = (i / tickCount) * 100
    if (pct > 100) break
    const t = new Date(start.getTime() + (span * i) / tickCount)
    const label =
      windowKey === '24h'
        ? t.toLocaleTimeString([], { hour: 'numeric', minute: '2-digit' })
        : t.toLocaleDateString([], { weekday: 'short', month: 'short', day: 'numeric' })
    out.push({ pct, label })
  }
  return out
}
