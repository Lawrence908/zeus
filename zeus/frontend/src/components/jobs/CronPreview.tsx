// zeus/frontend/src/components/jobs/CronPreview.tsx
//
// Renders the next N fire times for a cron expression / timezone pair.
// Updates whenever the user edits the cron field upstream.
import { useMemo } from 'react'

import { CronExpressionParser } from 'cron-parser'

import { formatRelative } from './timeUtils'

interface Props {
  cron: string
  timezone: string
  count?: number
}

export function CronPreview({ cron, timezone, count = 5 }: Props) {
  const result = useMemo(() => computeNext(cron, timezone, count), [cron, timezone, count])

  if (!cron.trim()) return null

  if ('error' in result) {
    return (
      <p className="text-[10px] font-mono text-on-surface-variant/40">
        Preview unavailable: {result.error}
      </p>
    )
  }

  return (
    <div className="space-y-1">
      <h4 className="text-[10px] font-label uppercase tracking-widest text-on-surface-variant/60">
        Next {count} fires
      </h4>
      <ul className="text-xs font-mono text-on-surface-variant space-y-0.5">
        {result.times.map((t, i) => (
          <li key={i} className="flex items-center justify-between gap-3">
            <span className="text-on-surface">{t.toLocaleString()}</span>
            <span className="text-on-surface-variant/50 text-[10px]">
              {formatRelative(t.toISOString())}
            </span>
          </li>
        ))}
      </ul>
    </div>
  )
}

function computeNext(
  cron: string,
  timezone: string,
  count: number,
): { times: Date[] } | { error: string } {
  try {
    const expr = CronExpressionParser.parse(cron.trim(), { tz: timezone })
    const out: Date[] = []
    for (let i = 0; i < count; i++) {
      out.push(expr.next().toDate())
    }
    return { times: out }
  } catch (err) {
    return { error: err instanceof Error ? err.message : String(err) }
  }
}
