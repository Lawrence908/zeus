// zeus/frontend/src/pages/IngestPage.tsx — Iris ingest controls + container-scoped diagnostics
import { useCallback, useEffect, useState } from 'react'
import { TopNav } from '../components/layout/TopNav'

const SOURCES = [
  { value: 'all', label: 'All configured sources' },
  { value: 'markdown', label: 'Markdown' },
  { value: 'obsidian', label: 'Obsidian' },
  { value: 'chatgpt', label: 'ChatGPT export' },
  { value: 'context_pack', label: 'Context pack' },
  { value: 'email', label: 'Email' },
  { value: 'git', label: 'Git' },
  { value: 'gcal', label: 'Google Calendar' },
  { value: 'bookmarks', label: 'Bookmarks' },
] as const

type Diagnostics = {
  zeus_pid: number
  scope_note: string
  ollama_ps: Record<string, unknown> | null
  ollama_ps_error: string | null
  ollama_running_model_count: number | null
}

type IngestStats = {
  error?: string
  collections?: Record<
    string,
    { points_count?: number; vectors_count?: number; status?: string }
  >
}

type MetricsScheduler = {
  running?: boolean
  jobs?: { id: string; next_run: string | null }[]
}

export function IngestPage() {
  const [source, setSource] = useState<string>('all')
  const [userId, setUserId] = useState('user')
  const [busy, setBusy] = useState(false)
  const [lastResult, setLastResult] = useState<string | null>(null)
  const [error, setError] = useState<string | null>(null)

  const [diag, setDiag] = useState<Diagnostics | null>(null)
  const [stats, setStats] = useState<IngestStats | null>(null)
  const [scheduler, setScheduler] = useState<MetricsScheduler | null>(null)

  const refresh = useCallback(async () => {
    setError(null)
    try {
      const [d, s, m] = await Promise.all([
        fetch('/admin/diagnostics').then((r) => {
          if (!r.ok) throw new Error(`diagnostics ${r.status}`)
          return r.json() as Promise<Diagnostics>
        }),
        fetch('/admin/ingest/stats').then((r) => {
          if (!r.ok) throw new Error(`ingest stats ${r.status}`)
          return r.json() as Promise<IngestStats>
        }),
        fetch('/admin/metrics').then((r) => {
          if (!r.ok) throw new Error(`metrics ${r.status}`)
          return r.json() as Promise<{ scheduler?: MetricsScheduler }>
        }),
      ])
      setDiag(d)
      setStats(s)
      setScheduler(m.scheduler ?? null)
    } catch (e) {
      setError(e instanceof Error ? e.message : String(e))
    }
  }, [])

  useEffect(() => {
    void refresh()
  }, [refresh])

  const runIngest = async () => {
    setBusy(true)
    setLastResult(null)
    setError(null)
    try {
      const r = await fetch('/ingest/trigger', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ source, user_id: userId }),
      })
      const body = await r.json().catch(() => ({}))
      if (!r.ok) {
        throw new Error(
          typeof body.detail === 'string'
            ? body.detail
            : `ingest ${r.status}: ${JSON.stringify(body)}`,
        )
      }
      setLastResult(
        `Indexed ${body.chunks_indexed ?? 0} chunks from: ${(body.sources_run ?? []).join(', ') || '—'}`,
      )
      await refresh()
    } catch (e) {
      setError(e instanceof Error ? e.message : String(e))
    } finally {
      setBusy(false)
    }
  }

  const clearQueryLog = async () => {
    setError(null)
    try {
      const r = await fetch('/admin/query-log/clear', { method: 'POST' })
      if (!r.ok) throw new Error(`clear ${r.status}`)
      setLastResult('Admin query log cleared.')
    } catch (e) {
      setError(e instanceof Error ? e.message : String(e))
    }
  }

  return (
    <div className="min-h-screen bg-background text-on-surface pt-[52px]">
      <TopNav />
      <main className="max-w-3xl mx-auto px-4 py-8 font-body">
        <h1 className="font-headline text-xl font-semibold text-on-surface mb-1">Iris · Ingest</h1>
        <p className="text-sm text-on-surface-variant mb-8">
          Run ingestion against Mnemosyne, inspect Qdrant collections, and see Ollama load from this
          process&apos;s network view. Host-wide process lists still need{' '}
          <code className="text-xs bg-surface-container-high px-1 rounded">lsof</code> on the host.
        </p>

        {error && (
          <div className="mb-6 rounded border border-error/40 bg-error-container/20 text-error px-3 py-2 text-sm">
            {error}
          </div>
        )}
        {lastResult && (
          <div className="mb-6 rounded border border-primary-container/30 bg-surface-container-high px-3 py-2 text-sm text-on-surface">
            {lastResult}
          </div>
        )}

        <section className="mb-8 rounded border border-outline-variant/20 bg-surface-container-low p-5">
          <h2 className="font-headline text-sm font-semibold uppercase tracking-widest text-on-surface-variant/70 mb-4">
            Run ingest
          </h2>
          <div className="flex flex-col sm:flex-row gap-4 sm:items-end">
            <div className="flex-1">
              <label className="block text-[10px] font-label uppercase tracking-widest text-on-surface-variant/60 mb-1">
                Source
              </label>
              <select
                value={source}
                onChange={(e) => setSource(e.target.value)}
                className="w-full bg-surface-container-high border border-outline-variant/30 rounded px-3 py-2 text-sm outline-none focus:border-primary-container/50"
              >
                {SOURCES.map((s) => (
                  <option key={s.value} value={s.value}>
                    {s.label}
                  </option>
                ))}
              </select>
            </div>
            <div className="w-full sm:w-40">
              <label className="block text-[10px] font-label uppercase tracking-widest text-on-surface-variant/60 mb-1">
                User ID
              </label>
              <input
                value={userId}
                onChange={(e) => setUserId(e.target.value)}
                className="w-full bg-surface-container-high border border-outline-variant/30 rounded px-3 py-2 text-sm outline-none focus:border-primary-container/50"
              />
            </div>
            <button
              type="button"
              disabled={busy}
              onClick={() => void runIngest()}
              className="shrink-0 px-4 py-2 rounded text-sm font-label font-medium bg-primary-container text-on-primary-container disabled:opacity-50"
            >
              {busy ? 'Running…' : 'Run now'}
            </button>
          </div>
        </section>

        <section className="mb-8 rounded border border-outline-variant/20 bg-surface-container-low p-5">
          <div className="flex flex-wrap items-center justify-between gap-3 mb-4">
            <h2 className="font-headline text-sm font-semibold uppercase tracking-widest text-on-surface-variant/70">
              Diagnostics
            </h2>
            <div className="flex gap-2">
              <button
                type="button"
                onClick={() => void refresh()}
                className="px-3 py-1.5 rounded text-xs font-label border border-outline-variant/40 hover:border-primary-container/40"
              >
                Refresh
              </button>
              <button
                type="button"
                onClick={() => void clearQueryLog()}
                className="px-3 py-1.5 rounded text-xs font-label border border-outline-variant/40 hover:border-outline-variant/60"
                title="Clears the in-memory admin query log only"
              >
                Reset query log
              </button>
            </div>
          </div>
          {diag ? (
            <dl className="grid gap-2 text-sm">
              <div className="flex justify-between gap-4 border-b border-outline-variant/15 pb-2">
                <dt className="text-on-surface-variant">Zeus PID</dt>
                <dd className="font-mono">{diag.zeus_pid}</dd>
              </div>
              <div className="flex justify-between gap-4 border-b border-outline-variant/15 pb-2">
                <dt className="text-on-surface-variant">Ollama loaded models</dt>
                <dd className="font-mono">
                  {diag.ollama_running_model_count ?? '—'}
                  {diag.ollama_ps_error && (
                    <span className="block text-xs text-error mt-1">{diag.ollama_ps_error}</span>
                  )}
                </dd>
              </div>
              <p className="text-xs text-on-surface-variant/80 leading-relaxed pt-1">{diag.scope_note}</p>
            </dl>
          ) : (
            <p className="text-sm text-on-surface-variant">Loading…</p>
          )}
        </section>

        <section className="mb-8 rounded border border-outline-variant/20 bg-surface-container-low p-5">
          <h2 className="font-headline text-sm font-semibold uppercase tracking-widest text-on-surface-variant/70 mb-4">
            Scheduler
          </h2>
          {!scheduler?.running ? (
            <p className="text-sm text-on-surface-variant">Scheduler not running.</p>
          ) : !scheduler.jobs?.length ? (
            <p className="text-sm text-on-surface-variant">No scheduled jobs.</p>
          ) : (
            <ul className="text-sm space-y-2">
              {scheduler.jobs.map((j) => (
                <li key={j.id} className="flex justify-between gap-4 border-b border-outline-variant/10 pb-2 last:border-0">
                  <span className="font-mono text-on-surface-variant">{j.id}</span>
                  <span>{j.next_run ? new Date(j.next_run).toLocaleString() : '—'}</span>
                </li>
              ))}
            </ul>
          )}
        </section>

        <section className="rounded border border-outline-variant/20 bg-surface-container-low p-5">
          <h2 className="font-headline text-sm font-semibold uppercase tracking-widest text-on-surface-variant/70 mb-4">
            Qdrant collections
          </h2>
          {stats?.error ? (
            <p className="text-sm text-error">{stats.error}</p>
          ) : !stats?.collections || Object.keys(stats.collections).length === 0 ? (
            <p className="text-sm text-on-surface-variant">No collection data.</p>
          ) : (
            <table className="w-full text-sm">
              <thead>
                <tr className="text-left text-[10px] uppercase tracking-widest text-on-surface-variant/60">
                  <th className="pb-2">Collection</th>
                  <th className="pb-2">Points</th>
                  <th className="pb-2">Status</th>
                </tr>
              </thead>
              <tbody>
                {Object.entries(stats.collections).map(([name, c]) => (
                  <tr key={name} className="border-t border-outline-variant/15">
                    <td className="py-2 font-mono text-xs">{name}</td>
                    <td className="py-2">{c.points_count ?? c.vectors_count ?? '—'}</td>
                    <td className="py-2 text-on-surface-variant">{c.status ?? '—'}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </section>

        <p className="mt-8 text-xs text-on-surface-variant/60">
          Classic dashboard:{' '}
          <a href="/admin" className="text-primary-container hover:underline">
            /admin
          </a>
        </p>
      </main>
    </div>
  )
}
