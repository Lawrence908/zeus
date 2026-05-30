// zeus/frontend/src/components/jobs/timeUtils.ts
// Small formatting helpers for the Kronos UI. No deps; pure functions.

export function formatRelative(iso: string | null | undefined, now = Date.now()): string {
  if (!iso) return '—'
  const t = new Date(iso).getTime()
  if (Number.isNaN(t)) return '—'
  const delta = t - now
  const past = delta < 0
  const abs = Math.abs(delta)
  const sec = Math.round(abs / 1000)
  if (sec < 45) return past ? `${sec}s ago` : `in ${sec}s`
  const min = Math.round(sec / 60)
  if (min < 60) return past ? `${min}m ago` : `in ${min}m`
  const hr = Math.round(min / 60)
  if (hr < 24) return past ? `${hr}h ago` : `in ${hr}h`
  const day = Math.round(hr / 24)
  if (day < 14) return past ? `${day}d ago` : `in ${day}d`
  return new Date(iso).toLocaleDateString()
}

export function formatAbsolute(iso: string | null | undefined): string {
  if (!iso) return ''
  const d = new Date(iso)
  if (Number.isNaN(d.getTime())) return ''
  return d.toLocaleString()
}

export function formatDuration(ms: number | null | undefined): string {
  if (ms === null || ms === undefined) return '—'
  if (ms < 1000) return `${Math.round(ms)}ms`
  const s = ms / 1000
  if (s < 60) return `${s.toFixed(1)}s`
  const m = s / 60
  return `${m.toFixed(1)}m`
}

// Best-effort human gloss for the most common cron forms; otherwise echo raw.
export function describeCron(cron: string | null | undefined, tz: string): string {
  if (!cron) return ''
  const parts = cron.trim().split(/\s+/)
  if (parts.length !== 5 && parts.length !== 6) return cron
  const [min, hr, dom, mon, dow] = parts.length === 6 ? parts.slice(1) : parts
  const tzSuffix = tz === 'UTC' ? ' UTC' : ` ${tz}`

  const isEvery = (v: string) => v === '*'
  const isHourly = isEvery(hr) && /^\d+$/.test(min)

  if (
    isEvery(mon) &&
    isEvery(dom) &&
    isEvery(dow) &&
    /^\d+$/.test(hr) &&
    /^\d+$/.test(min)
  ) {
    return `Daily at ${pad(hr)}:${pad(min)}${tzSuffix}`
  }
  if (isHourly && isEvery(dom) && isEvery(mon) && isEvery(dow)) {
    return `Hourly at :${pad(min)}${tzSuffix}`
  }
  if (
    isEvery(mon) &&
    isEvery(dom) &&
    /^\d+$/.test(hr) &&
    /^\d+$/.test(min) &&
    /^\d+$/.test(dow)
  ) {
    const days = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat']
    return `${days[Number(dow) % 7]} at ${pad(hr)}:${pad(min)}${tzSuffix}`
  }
  return cron
}

function pad(s: string): string {
  return s.padStart(2, '0')
}
