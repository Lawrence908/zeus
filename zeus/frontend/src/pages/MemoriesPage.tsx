// zeus/frontend/src/pages/MemoriesPage.tsx — browse, search, edit, delete ingested memories
import { useCallback, useEffect, useMemo, useRef, useState } from 'react'
import { TopNav } from '../components/layout/TopNav'

interface MemoryEntry {
  id: string
  text: string
  source: string
  metadata: Record<string, unknown>
  created_at?: string | null
  updated_at?: string | null
  score?: number
}

interface ListResponse {
  entries: MemoryEntry[]
  next_offset: string | null
  total_estimate: number | null
}

interface SearchHit {
  id: string
  score: number
  text: string
  source: string
  metadata: Record<string, unknown>
}

interface SearchResponse {
  results: SearchHit[]
}

const PAGE_SIZE = 50

function shortDate(s?: string | null): string {
  if (!s) return ''
  const d = new Date(s)
  if (Number.isNaN(d.getTime())) return ''
  return d.toLocaleDateString()
}

function MemoryCard({
  entry,
  selected,
  onToggleSelect,
  onUpdate,
  onDelete,
}: {
  entry: MemoryEntry
  selected: boolean
  onToggleSelect: (id: string, shift: boolean) => void
  onUpdate: (id: string, text: string) => Promise<void>
  onDelete: (id: string) => Promise<void>
}) {
  const [expanded, setExpanded] = useState(false)
  const [editing, setEditing] = useState(false)
  const [draft, setDraft] = useState(entry.text)
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState('')

  useEffect(() => {
    setDraft(entry.text)
  }, [entry.text])

  const handleSave = async () => {
    setBusy(true)
    setError('')
    try {
      await onUpdate(entry.id, draft)
      setEditing(false)
    } catch (e) {
      setError(e instanceof Error ? e.message : String(e))
    } finally {
      setBusy(false)
    }
  }

  const handleDelete = async () => {
    if (!confirm('Delete this memory? This cannot be undone.')) return
    setBusy(true)
    setError('')
    try {
      await onDelete(entry.id)
    } catch (e) {
      setError(e instanceof Error ? e.message : String(e))
      setBusy(false)
    }
  }

  return (
    <div
      className={[
        'border rounded bg-surface-container-lowest/50 p-3',
        selected
          ? 'border-primary-container/60 bg-primary-container/5'
          : 'border-outline-variant/20',
      ].join(' ')}
    >
      <div className="flex items-start gap-3">
        <label className="shrink-0 mt-0.5 cursor-pointer">
          <input
            type="checkbox"
            checked={selected}
            onChange={() => { /* handled on click to access shiftKey */ }}
            onClick={(e) => {
              e.stopPropagation()
              onToggleSelect(entry.id, (e as React.MouseEvent).shiftKey)
            }}
            className="accent-primary-container"
          />
        </label>
        <button
          type="button"
          onClick={() => setExpanded((v) => !v)}
          className="flex-1 text-left flex items-start gap-3 min-w-0"
        >
          <span className="text-[10px] font-label uppercase tracking-widest text-on-surface-variant/60 shrink-0 mt-0.5">
            {entry.source}
          </span>
          {entry.score !== undefined && (
            <span className="text-[10px] font-label text-primary-container shrink-0 mt-0.5">
              {entry.score.toFixed(3)}
            </span>
          )}
          <span className={`text-sm font-body text-on-surface flex-1 min-w-0 ${expanded ? '' : 'line-clamp-2'}`}>
            {entry.text || '(empty)'}
          </span>
        </button>
      </div>

      {expanded && (
        <div className="mt-3 border-t border-outline-variant/15 pt-3">
          {editing ? (
            <div className="space-y-2">
              <textarea
                value={draft}
                onChange={(e) => setDraft(e.target.value)}
                rows={5}
                className="w-full bg-surface-container-high border border-outline-variant/30 rounded px-2 py-1.5 text-sm font-body text-on-surface outline-none focus:border-primary-container/50"
              />
              <div className="flex gap-2">
                <button
                  type="button"
                  onClick={handleSave}
                  disabled={busy || !draft.trim()}
                  className="px-3 py-1 rounded text-xs font-label bg-primary-container text-on-primary-container disabled:opacity-40"
                >
                  {busy ? 'Saving…' : 'Save'}
                </button>
                <button
                  type="button"
                  onClick={() => { setEditing(false); setDraft(entry.text) }}
                  className="px-3 py-1 rounded text-xs font-label text-on-surface-variant hover:text-on-surface"
                >
                  Cancel
                </button>
              </div>
            </div>
          ) : (
            <pre className="whitespace-pre-wrap text-sm font-body text-on-surface">{entry.text}</pre>
          )}

          <div className="mt-3 grid grid-cols-2 gap-x-4 gap-y-1 text-[11px] font-body text-on-surface-variant/70">
            <div><span className="opacity-60">id:</span> {entry.id}</div>
            {entry.created_at && <div><span className="opacity-60">created:</span> {shortDate(entry.created_at)}</div>}
            {entry.updated_at && <div><span className="opacity-60">updated:</span> {shortDate(entry.updated_at)}</div>}
            {Object.entries(entry.metadata)
              .filter(([k]) => !['source', 'created_at', 'updated_at'].includes(k))
              .map(([k, v]) => (
                <div key={k}><span className="opacity-60">{k}:</span> {String(v)}</div>
              ))}
          </div>

          {!editing && (
            <div className="mt-3 flex gap-2">
              <button
                type="button"
                onClick={() => setEditing(true)}
                disabled={busy}
                className="px-3 py-1 rounded text-xs font-label bg-surface-container-high text-on-surface hover:bg-surface-container-highest disabled:opacity-40"
              >
                Edit
              </button>
              <button
                type="button"
                onClick={handleDelete}
                disabled={busy}
                className="px-3 py-1 rounded text-xs font-label text-error hover:bg-error/10 disabled:opacity-40"
              >
                Delete
              </button>
            </div>
          )}

          {error && (
            <p className="mt-2 text-xs font-body text-error">{error}</p>
          )}
        </div>
      )}
    </div>
  )
}

export function MemoriesPage() {
  const [entries, setEntries] = useState<MemoryEntry[]>([])
  const [sources, setSources] = useState<string[]>([])
  const [sourceFilter, setSourceFilter] = useState<string>('')
  const [search, setSearch] = useState('')
  const [searchActive, setSearchActive] = useState('')
  const [nextOffset, setNextOffset] = useState<string | null>(null)
  const [total, setTotal] = useState<number | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [selected, setSelected] = useState<Set<string>>(new Set())
  const [bulkBusy, setBulkBusy] = useState(false)
  const lastClickedId = useRef<string | null>(null)

  const loadSources = useCallback(async () => {
    try {
      const res = await fetch('/memory/sources')
      if (res.ok) {
        const data = await res.json() as { sources: string[] }
        setSources(data.sources)
      }
    } catch {
      // ignore
    }
  }, [])

  const loadList = useCallback(async (reset: boolean) => {
    setLoading(true)
    setError('')
    try {
      const params = new URLSearchParams({ limit: String(PAGE_SIZE) })
      if (sourceFilter) params.set('source', sourceFilter)
      if (!reset && nextOffset) params.set('offset', nextOffset)
      const res = await fetch(`/memory/list?${params.toString()}`)
      if (!res.ok) throw new Error(`List failed (${res.status})`)
      const data = await res.json() as ListResponse
      setEntries((prev) => reset ? data.entries : [...prev, ...data.entries])
      setNextOffset(data.next_offset)
      if (data.total_estimate != null) setTotal(data.total_estimate)
    } catch (e) {
      setError(e instanceof Error ? e.message : String(e))
    } finally {
      setLoading(false)
    }
  }, [sourceFilter, nextOffset])

  const runSearch = useCallback(async (query: string) => {
    setLoading(true)
    setError('')
    setSearchActive(query)
    try {
      const res = await fetch('/memory/search', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query, top_k: 20 }),
      })
      if (!res.ok) throw new Error(`Search failed (${res.status})`)
      const data = await res.json() as SearchResponse
      const mapped: MemoryEntry[] = data.results.map((h) => ({
        id: h.id,
        text: h.text,
        source: h.source,
        metadata: h.metadata,
        score: h.score,
      }))
      setEntries(mapped)
      setNextOffset(null)
    } catch (e) {
      setError(e instanceof Error ? e.message : String(e))
    } finally {
      setLoading(false)
    }
  }, [])

  const clearSearch = () => {
    setSearch('')
    setSearchActive('')
    setNextOffset(null)
    void loadList(true)
  }

  useEffect(() => {
    void loadSources()
  }, [loadSources])

  useEffect(() => {
    if (searchActive) return
    setNextOffset(null)
    void loadList(true)
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [sourceFilter])

  const handleUpdate = useCallback(async (id: string, text: string) => {
    const res = await fetch(`/memory/${id}`, {
      method: 'PATCH',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ text }),
    })
    if (!res.ok) {
      const detail = await res.text().catch(() => '')
      throw new Error(`Update failed (${res.status}) ${detail}`.trim())
    }
    const updated = await res.json() as MemoryEntry
    setEntries((prev) => prev.map((e) => e.id === id ? { ...e, ...updated } : e))
  }, [])

  const handleDelete = useCallback(async (id: string) => {
    const res = await fetch(`/memory/${id}`, { method: 'DELETE' })
    if (!res.ok) {
      const detail = await res.text().catch(() => '')
      throw new Error(`Delete failed (${res.status}) ${detail}`.trim())
    }
    setEntries((prev) => prev.filter((e) => e.id !== id))
    setSelected((prev) => {
      if (!prev.has(id)) return prev
      const next = new Set(prev)
      next.delete(id)
      return next
    })
  }, [])

  const toggleSelect = useCallback((id: string, shift: boolean) => {
    setSelected((prev) => {
      const next = new Set(prev)
      if (shift && lastClickedId.current) {
        const ids = entries.map((e) => e.id)
        const start = ids.indexOf(lastClickedId.current)
        const end = ids.indexOf(id)
        if (start >= 0 && end >= 0) {
          const [lo, hi] = start < end ? [start, end] : [end, start]
          const add = !prev.has(id)
          for (let i = lo; i <= hi; i++) {
            if (add) next.add(ids[i])
            else next.delete(ids[i])
          }
          lastClickedId.current = id
          return next
        }
      }
      if (next.has(id)) next.delete(id)
      else next.add(id)
      lastClickedId.current = id
      return next
    })
  }, [entries])

  const selectAllVisible = () => setSelected(new Set(entries.map((e) => e.id)))
  const clearSelection = () => {
    setSelected(new Set())
    lastClickedId.current = null
  }

  const handleBulkDelete = async () => {
    if (selected.size === 0) return
    if (!confirm(`Delete ${selected.size} selected memor${selected.size === 1 ? 'y' : 'ies'}? Cannot be undone.`)) return
    setBulkBusy(true)
    setError('')
    try {
      const ids = Array.from(selected)
      const res = await fetch('/memory/delete_batch', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ ids }),
      })
      if (!res.ok) {
        const detail = await res.text().catch(() => '')
        throw new Error(`Bulk delete failed (${res.status}) ${detail}`.trim())
      }
      const deleted = new Set(ids)
      setEntries((prev) => prev.filter((e) => !deleted.has(e.id)))
      clearSelection()
    } catch (e) {
      setError(e instanceof Error ? e.message : String(e))
    } finally {
      setBulkBusy(false)
    }
  }

  const headerLine = useMemo(() => {
    if (searchActive) return `${entries.length} hits for "${searchActive}"`
    const shown = entries.length
    if (total != null) return `${shown} of ~${total} memories`
    return `${shown} memories`
  }, [entries.length, total, searchActive])

  return (
    <div className="flex flex-col h-screen bg-background">
      <TopNav />
      <div className="flex-1 overflow-y-auto pt-[52px]">
        <div className="max-w-3xl mx-auto p-6">
          <h1 className="font-headline font-semibold text-lg text-on-surface mb-4">Memories</h1>

          <div className="flex flex-col sm:flex-row gap-2 mb-3">
            <form
              className="flex-1 flex gap-2"
              onSubmit={(e) => {
                e.preventDefault()
                if (search.trim()) void runSearch(search.trim())
              }}
            >
              <input
                value={search}
                onChange={(e) => setSearch(e.target.value)}
                placeholder="Search memories…"
                className="flex-1 bg-surface-container-high border border-outline-variant/30 rounded px-3 py-2 text-sm font-body text-on-surface placeholder:text-on-surface-variant/40 outline-none focus:border-primary-container/50"
              />
              <button
                type="submit"
                disabled={loading || !search.trim()}
                className="px-3 py-2 rounded text-sm font-label bg-primary-container text-on-primary-container disabled:opacity-40"
              >
                Search
              </button>
              {searchActive && (
                <button
                  type="button"
                  onClick={clearSearch}
                  className="px-3 py-2 rounded text-sm font-label text-on-surface-variant hover:text-on-surface"
                >
                  Clear
                </button>
              )}
            </form>

            <select
              value={sourceFilter}
              onChange={(e) => setSourceFilter(e.target.value)}
              disabled={!!searchActive}
              className="bg-surface-container-high border border-outline-variant/30 rounded px-2 py-2 text-sm font-body text-on-surface outline-none focus:border-primary-container/50 disabled:opacity-40"
            >
              <option value="">All sources</option>
              {sources.map((s) => (
                <option key={s} value={s}>{s}</option>
              ))}
            </select>
          </div>

          <div className="flex items-center justify-between mb-3 text-xs font-body text-on-surface-variant/70">
            <span>{headerLine}</span>
            {loading && <span className="text-primary-container">Loading…</span>}
          </div>

          {selected.size > 0 && (
            <div className="mb-3 flex items-center gap-2 px-3 py-2 rounded border border-primary-container/40 bg-primary-container/10 text-xs font-label">
              <span className="text-primary-container">{selected.size} selected</span>
              <button
                type="button"
                onClick={selectAllVisible}
                className="px-2 py-1 rounded text-on-surface-variant hover:text-on-surface hover:bg-surface-container-high"
              >
                Select all visible ({entries.length})
              </button>
              <button
                type="button"
                onClick={clearSelection}
                className="px-2 py-1 rounded text-on-surface-variant hover:text-on-surface hover:bg-surface-container-high"
              >
                Clear
              </button>
              <span className="flex-1" />
              <button
                type="button"
                onClick={handleBulkDelete}
                disabled={bulkBusy}
                className="px-3 py-1 rounded bg-error/15 text-error hover:bg-error/25 disabled:opacity-40"
              >
                {bulkBusy ? 'Deleting…' : `Delete ${selected.size}`}
              </button>
            </div>
          )}

          {error && (
            <p className="mb-3 text-sm font-body text-error">{error}</p>
          )}

          <div className="space-y-2">
            {entries.map((entry) => (
              <MemoryCard
                key={entry.id}
                entry={entry}
                selected={selected.has(entry.id)}
                onToggleSelect={toggleSelect}
                onUpdate={handleUpdate}
                onDelete={handleDelete}
              />
            ))}
            {!loading && entries.length === 0 && (
              <p className="text-sm font-body text-on-surface-variant/60">
                No memories match. Try clearing filters or run an Iris ingest.
              </p>
            )}
          </div>

          {!searchActive && nextOffset && (
            <div className="mt-4 flex justify-center">
              <button
                type="button"
                onClick={() => void loadList(false)}
                disabled={loading}
                className="px-4 py-2 rounded text-sm font-label bg-surface-container-high text-on-surface hover:bg-surface-container-highest disabled:opacity-40"
              >
                Load more
              </button>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
