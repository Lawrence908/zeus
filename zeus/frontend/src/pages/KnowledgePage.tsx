// zeus/frontend/src/pages/KnowledgePage.tsx — browse / search zeus_knowledge (bulk RAG chunks)
//
// Parallel to MemoriesPage but backed by the /knowledge/* API. Differences:
//   - Facet sidebar (source / type / book), each facet row has a hover × that
//     bulk-deletes every chunk tagged with that facet value.
//   - Multi-select via checkboxes — shift-click extends a range on the current
//     view, selection toolbar appears when >0 selected.
//   - Citation link from metadata.url for chunks that carry one (e.g. kiwix_zim).
//   - No per-point edit; bulk chunks aren't authored. Use delete-by-source or
//     multi-select + delete-batch instead.
import { useCallback, useEffect, useMemo, useRef, useState } from 'react'
import { TopNav } from '../components/layout/TopNav'

interface KnowledgeEntry {
  id: string
  text: string
  source: string
  source_id?: string | null
  source_path?: string | null
  chunk_index?: number | null
  metadata: Record<string, unknown>
  created_at?: string | null
  score?: number
}

interface ListResponse {
  entries: KnowledgeEntry[]
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

interface FacetBucket {
  value: string
  count: number
}

interface FacetsResponse {
  total: number
  source: FacetBucket[]
  type: FacetBucket[]
  book: FacetBucket[]
}

type FacetKey = 'source' | 'type' | 'book'

const PAGE_SIZE = 50

function shortDate(s?: string | null): string {
  if (!s) return ''
  const d = new Date(s)
  if (Number.isNaN(d.getTime())) return ''
  return d.toLocaleDateString()
}

function formatCount(n: number): string {
  if (n >= 1000) return `${(n / 1000).toFixed(n >= 10000 ? 0 : 1)}k`
  return String(n)
}

function citationHref(entry: KnowledgeEntry): string | null {
  const md = entry.metadata || {}
  const url = md['url']
  if (typeof url === 'string' && url.startsWith('http')) return url
  return null
}

function KnowledgeCard({
  entry,
  selected,
  onToggleSelect,
  onDeleteBySource,
}: {
  entry: KnowledgeEntry
  selected: boolean
  onToggleSelect: (id: string, shift: boolean) => void
  onDeleteBySource: (source: string, sourceId: string) => Promise<void>
}) {
  const [expanded, setExpanded] = useState(false)
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState('')
  const citation = citationHref(entry)
  const book = entry.metadata?.['book']
  const title = entry.metadata?.['title']
  const chunkIdx = entry.chunk_index ?? entry.metadata?.['chunk_index']

  const handleDeleteBySource = async () => {
    if (!entry.source_id) return
    const label = String(book || entry.source_id)
    if (!confirm(
      `Delete all chunks for "${label}"?\n\nThis removes every point tagged source="${entry.source}" source_id="${entry.source_id}". Cannot be undone.`,
    )) return
    setBusy(true)
    setError('')
    try {
      await onDeleteBySource(entry.source, entry.source_id)
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
            onChange={() => { /* click handler does work, this silences React warning */ }}
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
          <pre className="whitespace-pre-wrap text-sm font-body text-on-surface">{entry.text}</pre>

          <div className="mt-3 grid grid-cols-2 gap-x-4 gap-y-1 text-[11px] font-body text-on-surface-variant/70">
            <div><span className="opacity-60">id:</span> {entry.id}</div>
            {typeof title === 'string' && <div><span className="opacity-60">title:</span> {title}</div>}
            {typeof book === 'string' && <div><span className="opacity-60">book:</span> {book}</div>}
            {entry.source_id && <div><span className="opacity-60">source_id:</span> {entry.source_id}</div>}
            {entry.source_path && <div><span className="opacity-60">path:</span> {entry.source_path}</div>}
            {chunkIdx !== undefined && chunkIdx !== null && <div><span className="opacity-60">chunk_index:</span> {String(chunkIdx)}</div>}
            {entry.created_at && <div><span className="opacity-60">created:</span> {shortDate(entry.created_at)}</div>}
            {Object.entries(entry.metadata)
              .filter(([k]) => !['source', 'source_id', 'source_path', 'chunk_index', 'created_at', 'title', 'book', 'url', 'file', 'text', 'user_id'].includes(k))
              .map(([k, v]) => (
                <div key={k}><span className="opacity-60">{k}:</span> {String(v)}</div>
              ))}
          </div>

          <div className="mt-3 flex gap-2 items-center">
            {citation && (
              <a
                href={citation}
                target="_blank"
                rel="noreferrer noopener"
                className="px-3 py-1 rounded text-xs font-label bg-primary-container/20 text-primary-container hover:bg-primary-container/30"
              >
                Open source
              </a>
            )}
            {entry.source_id && (
              <button
                type="button"
                onClick={handleDeleteBySource}
                disabled={busy}
                className="px-3 py-1 rounded text-xs font-label text-error hover:bg-error/10 disabled:opacity-40"
              >
                {busy ? 'Deleting…' : 'Delete by source'}
              </button>
            )}
          </div>

          {error && (
            <p className="mt-2 text-xs font-body text-error">{error}</p>
          )}
        </div>
      )}
    </div>
  )
}

function FacetList({
  title,
  facetKey,
  items,
  active,
  onSelect,
  onDelete,
}: {
  title: string
  facetKey: FacetKey
  items: FacetBucket[]
  active: string
  onSelect: (value: string) => void
  onDelete: (facetKey: FacetKey, value: string, count: number) => void
}) {
  return (
    <div>
      <h2 className="text-[10px] font-label uppercase tracking-widest text-on-surface-variant/60 mb-1.5">
        {title}
      </h2>
      <ul className="space-y-0.5">
        <li>
          <button
            type="button"
            onClick={() => onSelect('')}
            className={[
              'w-full text-left px-2 py-1 rounded text-xs font-body flex items-center justify-between',
              active === ''
                ? 'bg-primary-container/20 text-primary-container'
                : 'text-on-surface-variant hover:bg-surface-container-high hover:text-on-surface',
            ].join(' ')}
          >
            <span>all</span>
          </button>
        </li>
        {items.map((b) => (
          <li key={b.value} className="group relative">
            <button
              type="button"
              onClick={() => onSelect(b.value)}
              className={[
                'w-full text-left px-2 py-1 pr-6 rounded text-xs font-body flex items-center justify-between gap-2',
                active === b.value
                  ? 'bg-primary-container/20 text-primary-container'
                  : 'text-on-surface-variant hover:bg-surface-container-high hover:text-on-surface',
              ].join(' ')}
              title={b.value}
            >
              <span className="truncate">{b.value}</span>
              <span className="text-[10px] font-label text-on-surface-variant/50 shrink-0">
                {formatCount(b.count)}
              </span>
            </button>
            <button
              type="button"
              onClick={(e) => { e.stopPropagation(); onDelete(facetKey, b.value, b.count) }}
              title={`Delete all ${b.count.toLocaleString()} chunks tagged ${facetKey}="${b.value}"`}
              className="absolute right-1 top-1/2 -translate-y-1/2 opacity-0 group-hover:opacity-100 w-4 h-4 flex items-center justify-center rounded text-error hover:bg-error/10 text-[12px] leading-none"
            >
              ×
            </button>
          </li>
        ))}
        {items.length === 0 && (
          <li className="px-2 py-1 text-[11px] font-body text-on-surface-variant/40">
            (none)
          </li>
        )}
      </ul>
    </div>
  )
}

export function KnowledgePage() {
  const [entries, setEntries] = useState<KnowledgeEntry[]>([])
  const [facets, setFacets] = useState<FacetsResponse | null>(null)
  const [sourceFilter, setSourceFilter] = useState<string>('')
  const [typeFilter, setTypeFilter] = useState<string>('')
  const [bookFilter, setBookFilter] = useState<string>('')
  const [search, setSearch] = useState('')
  const [searchActive, setSearchActive] = useState('')
  const [nextOffset, setNextOffset] = useState<string | null>(null)
  const [total, setTotal] = useState<number | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [selected, setSelected] = useState<Set<string>>(new Set())
  const [bulkBusy, setBulkBusy] = useState(false)
  const lastClickedId = useRef<string | null>(null)

  const loadFacets = useCallback(async () => {
    try {
      const params = new URLSearchParams()
      if (sourceFilter) params.set('source', sourceFilter)
      if (typeFilter) params.set('type', typeFilter)
      const res = await fetch(`/knowledge/facets?${params.toString()}`)
      if (res.ok) {
        const data = await res.json() as FacetsResponse
        setFacets(data)
      }
    } catch {
      // ignore
    }
  }, [sourceFilter, typeFilter])

  const loadList = useCallback(async (reset: boolean) => {
    setLoading(true)
    setError('')
    try {
      const params = new URLSearchParams({ limit: String(PAGE_SIZE) })
      if (sourceFilter) params.set('source', sourceFilter)
      if (typeFilter) params.set('type', typeFilter)
      if (bookFilter) params.set('book', bookFilter)
      if (!reset && nextOffset) params.set('offset', nextOffset)
      const res = await fetch(`/knowledge/list?${params.toString()}`)
      if (!res.ok) throw new Error(`List failed (${res.status})`)
      const data = await res.json() as ListResponse
      setEntries((prev) => reset ? data.entries : [...prev, ...data.entries])
      setNextOffset(data.next_offset)
      if (data.total_estimate != null) setTotal(data.total_estimate)
      else setTotal(null)
    } catch (e) {
      setError(e instanceof Error ? e.message : String(e))
    } finally {
      setLoading(false)
    }
  }, [sourceFilter, typeFilter, bookFilter, nextOffset])

  const runSearch = useCallback(async (query: string) => {
    setLoading(true)
    setError('')
    setSearchActive(query)
    try {
      const body: Record<string, unknown> = { query, top_k: 20 }
      if (sourceFilter) body.sources = [sourceFilter]
      const res = await fetch('/knowledge/search', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(body),
      })
      if (!res.ok) throw new Error(`Search failed (${res.status})`)
      const data = await res.json() as SearchResponse
      const mapped: KnowledgeEntry[] = data.results.map((h) => ({
        id: h.id,
        text: h.text,
        source: h.source,
        source_id: (h.metadata?.['source_id'] as string) ?? null,
        source_path: (h.metadata?.['source_path'] as string) ?? null,
        chunk_index: (h.metadata?.['chunk_index'] as number) ?? null,
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
  }, [sourceFilter])

  const clearSearch = () => {
    setSearch('')
    setSearchActive('')
    setNextOffset(null)
    void loadList(true)
  }

  useEffect(() => {
    void loadFacets()
  }, [loadFacets])

  useEffect(() => {
    if (searchActive) return
    setNextOffset(null)
    void loadList(true)
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [sourceFilter, typeFilter, bookFilter])

  const handleDeleteBySource = useCallback(async (source: string, sourceId: string) => {
    const params = new URLSearchParams({ source, source_id: sourceId })
    const res = await fetch(`/knowledge/by-source?${params.toString()}`, { method: 'DELETE' })
    if (!res.ok) {
      const detail = await res.text().catch(() => '')
      throw new Error(`Delete failed (${res.status}) ${detail}`.trim())
    }
    setEntries((prev) => prev.filter((e) => !(e.source === source && e.source_id === sourceId)))
    void loadFacets()
  }, [loadFacets])

  const handleDeleteByFacet = useCallback(async (key: FacetKey, value: string, count: number) => {
    if (!confirm(
      `Delete every chunk tagged ${key}="${value}"?\n\n~${count.toLocaleString()} points will be removed. Cannot be undone.`,
    )) return
    try {
      const params = new URLSearchParams({ key, value })
      const res = await fetch(`/knowledge/by-facet?${params.toString()}`, { method: 'DELETE' })
      if (!res.ok) {
        const detail = await res.text().catch(() => '')
        throw new Error(`Delete failed (${res.status}) ${detail}`.trim())
      }
      // Refresh everything — the active filter may have just emptied.
      void loadFacets()
      if (key === 'source' && sourceFilter === value) setSourceFilter('')
      else if (key === 'type' && typeFilter === value) setTypeFilter('')
      else if (key === 'book' && bookFilter === value) setBookFilter('')
      else void loadList(true)
    } catch (e) {
      setError(e instanceof Error ? e.message : String(e))
    }
  }, [loadFacets, loadList, sourceFilter, typeFilter, bookFilter])

  const toggleSelect = useCallback((id: string, shift: boolean) => {
    setSelected((prev) => {
      const next = new Set(prev)
      if (shift && lastClickedId.current) {
        // Range select on the current view.
        const ids = entries.map((e) => e.id)
        const start = ids.indexOf(lastClickedId.current)
        const end = ids.indexOf(id)
        if (start >= 0 && end >= 0) {
          const [lo, hi] = start < end ? [start, end] : [end, start]
          const addOrRemove = !prev.has(id)
          for (let i = lo; i <= hi; i++) {
            if (addOrRemove) next.add(ids[i])
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

  const selectAllVisible = () => {
    setSelected(new Set(entries.map((e) => e.id)))
  }

  const clearSelection = () => {
    setSelected(new Set())
    lastClickedId.current = null
  }

  const handleBulkDelete = async () => {
    if (selected.size === 0) return
    if (!confirm(`Delete ${selected.size} selected chunk${selected.size === 1 ? '' : 's'}? Cannot be undone.`)) return
    setBulkBusy(true)
    setError('')
    try {
      const ids = Array.from(selected)
      const res = await fetch('/knowledge/delete_batch', {
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
      void loadFacets()
    } catch (e) {
      setError(e instanceof Error ? e.message : String(e))
    } finally {
      setBulkBusy(false)
    }
  }

  const headerLine = useMemo(() => {
    if (searchActive) return `${entries.length} hits for "${searchActive}"`
    const shown = entries.length
    if (total != null) return `${shown} of ~${total.toLocaleString()} chunks`
    if (facets) {
      const scopeTotal = bookFilter
        ? facets.book.find((b) => b.value === bookFilter)?.count
        : facets.total
      if (scopeTotal != null) return `${shown} of ~${scopeTotal.toLocaleString()} chunks`
    }
    return `${shown} chunks`
  }, [entries.length, total, searchActive, facets, bookFilter])

  return (
    <div className="flex flex-col h-screen bg-background">
      <TopNav />
      <div className="flex-1 overflow-y-auto pt-[52px]">
        <div className="max-w-6xl mx-auto p-6">
          <h1 className="font-headline font-semibold text-lg text-on-surface mb-4">Knowledge</h1>

          <div className="grid grid-cols-1 md:grid-cols-[200px_1fr] gap-4">
            {/* Facet sidebar */}
            <aside className="space-y-4">
              <FacetList
                title={`Source${sourceFilter ? ` — ${sourceFilter}` : ''}`}
                facetKey="source"
                items={facets?.source ?? []}
                active={sourceFilter}
                onSelect={(v) => {
                  setSourceFilter(v)
                  setTypeFilter('')
                  setBookFilter('')
                }}
                onDelete={handleDeleteByFacet}
              />
              <FacetList
                title={`Type${typeFilter ? ` — ${typeFilter}` : ''}`}
                facetKey="type"
                items={facets?.type ?? []}
                active={typeFilter}
                onSelect={(v) => {
                  setTypeFilter(v)
                  setBookFilter('')
                }}
                onDelete={handleDeleteByFacet}
              />
              <FacetList
                title={`Book${bookFilter ? ` — ${bookFilter}` : ''}`}
                facetKey="book"
                items={facets?.book ?? []}
                active={bookFilter}
                onSelect={setBookFilter}
                onDelete={handleDeleteByFacet}
              />
            </aside>

            {/* Main column */}
            <main>
              <form
                className="flex gap-2 mb-3"
                onSubmit={(e) => {
                  e.preventDefault()
                  if (search.trim()) void runSearch(search.trim())
                }}
              >
                <input
                  value={search}
                  onChange={(e) => setSearch(e.target.value)}
                  placeholder={sourceFilter ? `Search knowledge (within ${sourceFilter})…` : 'Search knowledge…'}
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

              <div className="flex items-center justify-between mb-3 text-xs font-body text-on-surface-variant/70">
                <span>{headerLine}</span>
                {loading && <span className="text-primary-container">Loading…</span>}
              </div>

              {/* Selection toolbar */}
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
                  <KnowledgeCard
                    key={entry.id}
                    entry={entry}
                    selected={selected.has(entry.id)}
                    onToggleSelect={toggleSelect}
                    onDeleteBySource={handleDeleteBySource}
                  />
                ))}
                {!loading && entries.length === 0 && (
                  <p className="text-sm font-body text-on-surface-variant/60">
                    No knowledge chunks match. Try clearing filters or run an Iris knowledge ingest.
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
            </main>
          </div>
        </div>
      </div>
    </div>
  )
}
