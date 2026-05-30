// zeus/frontend/src/components/jobs/CronBuilder.tsx
//
// Preset dropdown + raw cron text field + timezone select. v1: no visual
// "every N units" builder; users pick a preset or type cron directly.
import { useMemo } from 'react'

import { CronExpressionParser } from 'cron-parser'

interface Props {
  value: string
  timezone: string
  onChange: (cron: string) => void
  onTimezoneChange: (tz: string) => void
}

interface Preset {
  label: string
  expr: string
}

const PRESETS: Preset[] = [
  { label: 'Every minute', expr: '* * * * *' },
  { label: 'Every 5 minutes', expr: '*/5 * * * *' },
  { label: 'Every 15 minutes', expr: '*/15 * * * *' },
  { label: 'Every hour (on the hour)', expr: '0 * * * *' },
  { label: 'Every 6 hours', expr: '0 */6 * * *' },
  { label: 'Daily at 7:00', expr: '0 7 * * *' },
  { label: 'Daily at 9:00', expr: '0 9 * * *' },
  { label: 'Weekdays at 9:00', expr: '0 9 * * 1-5' },
  { label: 'Weekly Monday 9:00', expr: '0 9 * * 1' },
  { label: 'Weekly Sunday 18:00', expr: '0 18 * * 0' },
  { label: 'Monthly on the 1st at 0:00', expr: '0 0 1 * *' },
]

const COMMON_TZ = [
  'UTC',
  'America/Los_Angeles',
  'America/Denver',
  'America/Chicago',
  'America/New_York',
  'Europe/London',
  'Europe/Berlin',
  'Asia/Tokyo',
  'Australia/Sydney',
]

const baseInput =
  'bg-surface-container-high border border-outline-variant/30 rounded px-3 py-1.5 text-xs ' +
  'font-mono text-on-surface outline-none focus:border-primary-container/50 transition-colors'

const baseSelect =
  'bg-surface-container-high border border-outline-variant/30 rounded px-3 py-1.5 text-xs ' +
  'font-body text-on-surface outline-none focus:border-primary-container/50 transition-colors'

export function CronBuilder({ value, timezone, onChange, onTimezoneChange }: Props) {
  const validation = useMemo(() => validateCron(value), [value])

  // Browser's TZ as a default option if not already in the common list.
  const browserTz = useMemo(() => {
    try {
      return Intl.DateTimeFormat().resolvedOptions().timeZone
    } catch {
      return 'UTC'
    }
  }, [])
  const tzOptions = useMemo(() => {
    const set = new Set([browserTz, ...COMMON_TZ, timezone])
    return Array.from(set).filter(Boolean)
  }, [browserTz, timezone])

  return (
    <div className="space-y-2">
      <div className="flex flex-wrap items-center gap-2">
        <label className="text-[10px] font-label uppercase tracking-widest text-on-surface-variant/60">
          Preset
        </label>
        <select
          value=""
          onChange={(e) => {
            if (e.target.value) onChange(e.target.value)
          }}
          className={baseSelect}
        >
          <option value="">— Pick a preset —</option>
          {PRESETS.map((p) => (
            <option key={p.expr} value={p.expr}>
              {p.label} ({p.expr})
            </option>
          ))}
        </select>
      </div>

      <div className="flex items-center gap-2">
        <label className="text-[10px] font-label uppercase tracking-widest text-on-surface-variant/60 shrink-0">
          Cron
        </label>
        <input
          type="text"
          value={value}
          onChange={(e) => onChange(e.target.value)}
          placeholder="0 9 * * *"
          spellCheck={false}
          className={[baseInput, 'flex-1', validation.ok ? '' : 'border-error/60'].join(' ')}
        />
      </div>

      <div className="flex items-center gap-2">
        <label className="text-[10px] font-label uppercase tracking-widest text-on-surface-variant/60 shrink-0">
          TZ
        </label>
        <select
          value={timezone}
          onChange={(e) => onTimezoneChange(e.target.value)}
          className={baseSelect}
        >
          {tzOptions.map((tz) => (
            <option key={tz} value={tz}>
              {tz}
            </option>
          ))}
        </select>
      </div>

      {!validation.ok && (
        <p className="text-[10px] font-mono text-error">
          {validation.error ?? 'Invalid cron expression'}
        </p>
      )}
    </div>
  )
}

export function validateCron(cron: string): { ok: boolean; error?: string } {
  if (!cron || !cron.trim()) return { ok: false, error: 'cron required' }
  try {
    CronExpressionParser.parse(cron.trim())
    return { ok: true }
  } catch (err) {
    return { ok: false, error: err instanceof Error ? err.message : String(err) }
  }
}
