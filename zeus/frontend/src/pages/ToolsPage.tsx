// zeus/frontend/src/pages/ToolsPage.tsx — Browse chat-path + MCP tools
import { Fragment, useCallback, useEffect, useMemo, useRef, useState } from 'react'
import { TopNav } from '../components/layout/TopNav'
import {
  CacheStats,
  ToolInvocation,
  ToolSource,
  ToolSpec,
  useToolsStore,
} from '../store/toolsStore'

// ---------------------------------------------------------------------------
// Small presentation helpers
// ---------------------------------------------------------------------------

type TabKey = 'directory' | 'invocations' | 'cache'

function SourceBadge({ source }: { source: ToolSource }) {
  const chat = source === 'chat'
  return (
    <span
      className={[
        'text-[9px] font-label uppercase tracking-widest px-1.5 py-0.5 rounded border',
        chat
          ? 'bg-primary-container/20 border-primary/30 text-primary'
          : 'bg-tertiary-container/20 border-tertiary/30 text-tertiary',
      ].join(' ')}
      title={chat ? 'Called by the Zeus chat LLM during /chat/message' : 'Exposed to external MCP clients (Claude Desktop, Cursor)'}
    >
      {chat ? 'CHAT' : 'MCP'}
    </span>
  )
}

function BoolBadge({ value, label }: { value: boolean; label: string }) {
  return (
    <span
      className={[
        'text-[9px] font-label uppercase tracking-widest px-1.5 py-0.5 rounded border',
        value
          ? 'bg-primary-container/20 border-primary/30 text-primary'
          : 'bg-surface-container-high border-outline-variant/30 text-on-surface-variant/60',
      ].join(' ')}
    >
      {label}
    </span>
  )
}

function fmtTs(ts: number): string {
  const d = new Date(ts * 1000)
  return d.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit', hour12: false })
}

function fmtJson(value: unknown): string {
  try {
    return JSON.stringify(value, null, 2)
  } catch {
    return String(value)
  }
}

// ---------------------------------------------------------------------------
// ToolDirectory
// ---------------------------------------------------------------------------

function ToolDirectory({ tools }: { tools: ToolSpec[] }) {
  const { search, sourceFilter, setSearch, setSourceFilter } = useToolsStore()
  const [expandedName, setExpandedName] = useState<string | null>(null)

  const filtered = useMemo(() => {
    const q = search.trim().toLowerCase()
    return tools.filter((t) => {
      if (sourceFilter !== 'all' && t.source !== sourceFilter) return false
      if (!q) return true
      return t.name.includes(q) || t.description.toLowerCase().includes(q)
    })
  }, [tools, search, sourceFilter])

  return (
    <div>
      {/* Filter bar */}
      <div className="flex flex-wrap items-center gap-3 mb-4">
        <input
          type="text"
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          placeholder="Filter tools by name or description..."
          className="flex-1 min-w-[240px] bg-surface-container-high border border-outline-variant/30 rounded px-3 py-2 text-sm font-body text-on-surface placeholder:text-on-surface-variant/40 outline-none focus:border-primary-container/50"
        />
        <div className="flex items-center gap-1 rounded border border-outline-variant/30 bg-surface-container-high p-0.5">
          {(['all', 'chat', 'mcp'] as const).map((k) => (
            <button
              key={k}
              onClick={() => setSourceFilter(k)}
              className={[
                'px-3 py-1.5 text-[10px] font-label font-semibold uppercase tracking-widest rounded transition-colors',
                sourceFilter === k
                  ? 'bg-primary-container/30 text-primary'
                  : 'text-on-surface-variant hover:text-on-surface',
              ].join(' ')}
            >
              {k === 'all' ? 'All' : k.toUpperCase()}
            </button>
          ))}
        </div>
      </div>

      {/* Table */}
      {filtered.length === 0 ? (
        <div className="text-center py-16 border border-dashed border-outline-variant/30 rounded">
          <p className="font-body text-sm text-on-surface-variant">No tools match the current filter.</p>
        </div>
      ) : (
        <div className="border border-outline-variant/20 rounded overflow-hidden">
          <table className="w-full text-sm">
            <thead className="bg-surface-container-high text-[10px] font-label uppercase tracking-widest text-on-surface-variant/70">
              <tr>
                <th className="text-left px-3 py-2 font-label font-semibold">Name</th>
                <th className="text-left px-3 py-2 font-label font-semibold">Source</th>
                <th className="text-left px-3 py-2 font-label font-semibold">Description</th>
                <th className="text-left px-3 py-2 font-label font-semibold">Flags</th>
                <th className="text-right px-3 py-2 font-label font-semibold">Timeout</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-outline-variant/10">
              {filtered.map((t) => {
                const isOpen = expandedName === t.name
                return (
                  <Fragment key={t.name}>
                    <tr
                      onClick={() => setExpandedName(isOpen ? null : t.name)}
                      className={[
                        'cursor-pointer hover:bg-surface-container/40',
                        isOpen ? 'bg-surface-container-low' : '',
                      ].join(' ')}
                    >
                      <td className="px-3 py-2 font-mono text-xs text-on-surface">{t.name}</td>
                      <td className="px-3 py-2"><SourceBadge source={t.source} /></td>
                      <td className="px-3 py-2 text-xs text-on-surface-variant max-w-xl">
                        <span className="line-clamp-2">{t.description}</span>
                      </td>
                      <td className="px-3 py-2">
                        <div className="flex flex-wrap gap-1">
                          {t.cacheable && <BoolBadge value label="cacheable" />}
                          {t.write_gated && (
                            <span
                              className={[
                                'text-[9px] font-label uppercase tracking-widest px-1.5 py-0.5 rounded border',
                                t.write_enabled_now
                                  ? 'bg-tertiary-container/20 border-tertiary/30 text-tertiary'
                                  : 'bg-surface-container-high border-outline-variant/30 text-on-surface-variant/60',
                              ].join(' ')}
                              title={t.write_enabled_now ? 'ZEUS_MCP_ALLOW_WRITE=true' : 'Write-gated (currently disabled)'}
                            >
                              {t.write_enabled_now ? 'write-on' : 'write-gated'}
                            </span>
                          )}
                          {t.aegis_policy && (
                            <span
                              className="text-[9px] font-label uppercase tracking-widest px-1.5 py-0.5 rounded border bg-error-container/10 border-error/30 text-error/80"
                              title={`Aegis policy: ${t.aegis_policy}`}
                            >
                              aegis:{t.aegis_policy}
                            </span>
                          )}
                        </div>
                      </td>
                      <td className="px-3 py-2 text-right font-mono text-[11px] text-on-surface-variant/60">
                        {t.timeout_seconds != null ? `${t.timeout_seconds}s` : '—'}
                      </td>
                    </tr>
                    {isOpen && (
                      <tr className="bg-surface-container-lowest/60">
                        <td colSpan={5} className="px-6 py-3">
                          <div className="mb-3">
                            <div className="text-[10px] font-label uppercase tracking-widest text-on-surface-variant/70 mb-1">
                              Description
                            </div>
                            <p className="text-xs font-body text-on-surface-variant leading-relaxed whitespace-pre-wrap">
                              {t.description}
                            </p>
                          </div>
                          <div>
                            <div className="text-[10px] font-label uppercase tracking-widest text-on-surface-variant/70 mb-1">
                              Parameters (JSON Schema)
                            </div>
                            <pre className="text-[11px] font-mono text-on-surface-variant bg-surface-container-lowest rounded p-3 overflow-x-auto custom-scrollbar">
                              {fmtJson(t.parameters)}
                            </pre>
                          </div>
                        </td>
                      </tr>
                    )}
                  </Fragment>
                )
              })}
            </tbody>
          </table>
        </div>
      )}
    </div>
  )
}

// ---------------------------------------------------------------------------
// InvocationsFeed
// ---------------------------------------------------------------------------

function InvocationCard({ inv }: { inv: ToolInvocation }) {
  const [open, setOpen] = useState(false)
  const statusClass = inv.aegis_rejected
    ? 'text-error'
    : inv.is_error
      ? 'text-error'
      : inv.cache_hit
        ? 'text-tertiary'
        : 'text-primary'
  const label = inv.aegis_rejected
    ? 'AEGIS REJECT'
    : inv.is_error
      ? 'ERROR'
      : inv.cache_hit
        ? 'CACHE HIT'
        : 'OK'

  return (
    <div className="border border-outline-variant/15 rounded bg-surface-container-lowest/50">
      <button
        onClick={() => setOpen(!open)}
        className="w-full flex items-center gap-3 px-3 py-2 text-left hover:bg-surface-container/40"
      >
        <span className={['text-[9px] font-label font-semibold uppercase tracking-widest shrink-0', statusClass].join(' ')}>
          {label}
        </span>
        <span className="font-mono text-xs text-on-surface">{inv.tool}</span>
        <span className="text-[10px] font-mono text-on-surface-variant/50 shrink-0 ml-auto">
          {inv.duration_ms}ms
        </span>
        <span className="text-[10px] font-mono text-on-surface-variant/40 shrink-0">
          {fmtTs(inv.ts)}
        </span>
        <span
          className="material-symbols-outlined text-on-surface-variant/40 transition-transform shrink-0"
          style={{ fontSize: 16, transform: open ? 'rotate(180deg)' : undefined }}
        >
          expand_more
        </span>
      </button>
      {open && (
        <div className="px-3 pb-3 text-xs font-mono space-y-3">
          <div>
            <div className="text-[10px] font-label uppercase tracking-widest text-on-surface-variant/60 mb-1">Args</div>
            <pre className="text-[11px] bg-surface-container-lowest rounded p-2 overflow-x-auto custom-scrollbar text-on-surface-variant whitespace-pre-wrap">{fmtJson(inv.args)}</pre>
          </div>
          <div>
            <div className="text-[10px] font-label uppercase tracking-widest text-on-surface-variant/60 mb-1">Result</div>
            <pre className={['text-[11px] bg-surface-container-lowest rounded p-2 overflow-x-auto custom-scrollbar whitespace-pre-wrap', inv.is_error ? 'text-error' : 'text-on-surface-variant'].join(' ')}>{inv.content || '(empty)'}</pre>
          </div>
          {inv.aegis_flags.length > 0 && (
            <div className="flex flex-wrap gap-1">
              {inv.aegis_flags.map((f) => (
                <span key={f} className="text-[9px] font-label px-1.5 py-0.5 rounded border bg-error-container/10 border-error/30 text-error/80">
                  aegis:{f}
                </span>
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  )
}

function InvocationsFeed({ invocations }: { invocations: ToolInvocation[] }) {
  if (invocations.length === 0) {
    return (
      <div className="text-center py-16 border border-dashed border-outline-variant/30 rounded">
        <p className="font-body text-sm text-on-surface-variant">
          No invocations match the current filter. Try a different chip, or clear the filter to see everything.
        </p>
      </div>
    )
  }
  return (
    <div className="space-y-1">
      {invocations.map((inv, i) => (
        <InvocationCard key={`${inv.ts}-${inv.tool}-${i}`} inv={inv} />
      ))}
    </div>
  )
}


// ---------------------------------------------------------------------------
// InvocationsTab — filter chip row + feed
// ---------------------------------------------------------------------------

function InvocationsTab({ invocations }: { invocations: ToolInvocation[] }) {
  const [toolFilter, setToolFilter] = useState<string | null>(null)
  const [rejectedOnly, setRejectedOnly] = useState(false)

  // Distinct tool names seen in this batch, with counts — recalculated on
  // every fetch tick so the chip row reflects what's actually in the buffer.
  const toolCounts = useMemo(() => {
    const m = new Map<string, number>()
    for (const inv of invocations) {
      m.set(inv.tool, (m.get(inv.tool) ?? 0) + 1)
    }
    // Sort most-frequent first so high-volume tools anchor the left of the row.
    return [...m.entries()].sort((a, b) => b[1] - a[1])
  }, [invocations])

  const rejectedCount = useMemo(
    () => invocations.filter((i) => i.aegis_rejected).length,
    [invocations],
  )

  // Drop the filter if the selected tool rolls off the buffer entirely.
  useEffect(() => {
    if (toolFilter && !toolCounts.some(([name]) => name === toolFilter)) {
      setToolFilter(null)
    }
  }, [toolCounts, toolFilter])

  const filtered = useMemo(() => {
    return invocations.filter((inv) => {
      if (toolFilter && inv.tool !== toolFilter) return false
      if (rejectedOnly && !inv.aegis_rejected) return false
      return true
    })
  }, [invocations, toolFilter, rejectedOnly])

  if (invocations.length === 0) {
    return (
      <div className="text-center py-16 border border-dashed border-outline-variant/30 rounded">
        <p className="font-body text-sm text-on-surface-variant">
          No invocations yet. Send a chat message that would call a tool (e.g. "what time is it?").
        </p>
      </div>
    )
  }

  const Chip = ({
    active,
    onClick,
    children,
    tone = 'neutral',
    count,
    title,
  }: {
    active: boolean
    onClick: () => void
    children: React.ReactNode
    tone?: 'neutral' | 'warn'
    count?: number
    title?: string
  }) => {
    const activeCls =
      tone === 'warn'
        ? 'bg-error-container/30 text-error border-error/40'
        : 'bg-primary-container/30 text-primary border-primary/40'
    const inactiveCls =
      tone === 'warn'
        ? 'bg-surface-container/40 text-on-surface-variant hover:text-error border-outline-variant/20'
        : 'bg-surface-container/40 text-on-surface-variant hover:text-on-surface border-outline-variant/20'
    return (
      <button
        type="button"
        onClick={onClick}
        title={title}
        className={[
          'shrink-0 px-2.5 py-1 rounded border transition-colors text-[10px] font-label font-semibold uppercase tracking-widest flex items-center gap-1.5',
          active ? activeCls : inactiveCls,
        ].join(' ')}
      >
        <span>{children}</span>
        {count !== undefined && (
          <span
            className={[
              'font-mono px-1 rounded text-[9px]',
              active ? 'bg-black/10' : 'bg-surface-container-highest/70',
            ].join(' ')}
          >
            {count}
          </span>
        )}
      </button>
    )
  }

  return (
    <div>
      {/* Filter bar */}
      <div className="flex items-center gap-2 mb-4 flex-wrap">
        {/* All / per-tool chips (horizontally scrollable on small widths) */}
        <div className="flex items-center gap-1.5 flex-1 overflow-x-auto custom-scrollbar py-1 min-w-0">
          <Chip
            active={toolFilter === null}
            onClick={() => setToolFilter(null)}
            count={invocations.length}
          >
            All
          </Chip>
          {toolCounts.map(([name, count]) => (
            <Chip
              key={name}
              active={toolFilter === name}
              onClick={() => setToolFilter(toolFilter === name ? null : name)}
              count={count}
              title={`Show only ${name}`}
            >
              {name}
            </Chip>
          ))}
        </div>
        {/* Rejected-only toggle */}
        <Chip
          active={rejectedOnly}
          onClick={() => setRejectedOnly((v) => !v)}
          tone="warn"
          count={rejectedCount}
          title="Show only invocations that Aegis rejected"
        >
          Rejected only
        </Chip>
      </div>

      <InvocationsFeed invocations={filtered} />
    </div>
  )
}

// ---------------------------------------------------------------------------
// CacheControls
// ---------------------------------------------------------------------------

function CacheControls({ stats, onClear }: { stats: CacheStats | null; onClear: () => void }) {
  const [clearing, setClearing] = useState(false)
  const handleClear = async () => {
    setClearing(true)
    try {
      await onClear()
    } finally {
      setClearing(false)
    }
  }
  const hitRate =
    stats && stats.hits + stats.misses > 0
      ? ((stats.hits / (stats.hits + stats.misses)) * 100).toFixed(1)
      : null

  const Card = ({ label, value, hint }: { label: string; value: string | number; hint?: string }) => (
    <div className="border border-outline-variant/20 rounded bg-surface-container/40 p-4">
      <div className="text-[10px] font-label uppercase tracking-widest text-on-surface-variant/60 mb-1">
        {label}
      </div>
      <div className="font-mono text-2xl text-on-surface">{value}</div>
      {hint && <div className="text-[10px] font-mono text-on-surface-variant/40 mt-1">{hint}</div>}
    </div>
  )

  return (
    <div>
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 mb-5">
        <Card label="Size" value={stats?.size ?? '—'} hint={stats ? `of ${stats.max_entries}` : undefined} />
        <Card label="Hits" value={stats?.hits ?? '—'} />
        <Card label="Misses" value={stats?.misses ?? '—'} />
        <Card label="Hit rate" value={hitRate !== null ? `${hitRate}%` : '—'} hint={stats ? `ttl ${stats.ttl_seconds}s` : undefined} />
      </div>
      <button
        onClick={() => void handleClear()}
        disabled={clearing || !stats}
        className="px-4 py-2 text-xs font-label font-semibold uppercase tracking-widest rounded border border-error/30 text-error hover:bg-error-container/20 transition-colors disabled:opacity-40"
      >
        {clearing ? 'Clearing...' : 'Clear cache'}
      </button>
      <p className="mt-3 text-[11px] text-on-surface-variant/50 font-body">
        Only chat-path tools with <span className="font-mono">cacheable=true</span> use the cache (currently <span className="font-mono">web_search</span>).
        Clearing drops every entry but does not disable caching. Set <span className="font-mono">ZEUS_TOOL_CACHE_TTL_SECONDS=0</span> to turn caching off entirely.
      </p>
    </div>
  )
}

// ---------------------------------------------------------------------------
// ToolsPage
// ---------------------------------------------------------------------------

export function ToolsPage() {
  const {
    tools, meta, invocations, cacheStats, loading, error,
    fetchTools, fetchInvocations, fetchCacheStats, clearCache,
  } = useToolsStore()
  const [tab, setTab] = useState<TabKey>('directory')
  const pollRef = useRef<ReturnType<typeof setInterval> | null>(null)

  // Initial load.
  useEffect(() => {
    void fetchTools()
    void fetchInvocations()
    void fetchCacheStats()
  }, [fetchTools, fetchInvocations, fetchCacheStats])

  // Directory refresh every 30s (specs rarely change).
  useEffect(() => {
    const id = setInterval(() => void fetchTools(), 30_000)
    return () => clearInterval(id)
  }, [fetchTools])

  // Poll invocations + cache stats every 5s while on the Invocations or Cache tab.
  // Page Visibility API pauses polling when the tab is backgrounded.
  useEffect(() => {
    if (pollRef.current) {
      clearInterval(pollRef.current)
      pollRef.current = null
    }
    if (tab !== 'invocations' && tab !== 'cache') return
    const tick = () => {
      if (document.visibilityState === 'hidden') return
      void fetchInvocations()
      void fetchCacheStats()
    }
    tick()
    pollRef.current = setInterval(tick, 5_000)
    return () => {
      if (pollRef.current) {
        clearInterval(pollRef.current)
        pollRef.current = null
      }
    }
  }, [tab, fetchInvocations, fetchCacheStats])

  const handleClearCache = useCallback(async () => {
    await clearCache()
  }, [clearCache])

  return (
    <div className="flex flex-col h-screen bg-background">
      <TopNav />
      <div className="flex-1 overflow-y-auto custom-scrollbar pt-[52px]">
        <div className="max-w-6xl mx-auto px-6 py-8">
          {/* Header */}
          <div className="mb-6">
            <h1 className="font-headline font-bold text-2xl text-on-surface mb-1">Tools</h1>
            <p className="font-body text-sm text-on-surface-variant">
              Every tool Zeus knows about. Chat-path tools fire during /chat/message; MCP tools are exposed to Claude Desktop, Cursor, and other MCP clients.
            </p>
            {meta && (
              <div className="flex flex-wrap items-center gap-2 mt-3">
                <span className={[
                  'text-[10px] font-label uppercase tracking-widest px-2 py-1 rounded border',
                  meta.chat.enabled
                    ? 'bg-primary-container/20 border-primary/30 text-primary'
                    : 'bg-surface-container-high border-outline-variant/30 text-on-surface-variant/60',
                ].join(' ')}>
                  chat: {meta.chat.count} {meta.chat.enabled ? '(enabled)' : '(disabled)'}
                </span>
                <span className="text-[10px] font-label uppercase tracking-widest px-2 py-1 rounded border bg-tertiary-container/20 border-tertiary/30 text-tertiary">
                  mcp: {meta.mcp.count} {meta.mcp.write_enabled ? '(write-on)' : '(read-only)'}
                </span>
                <span className="text-[10px] font-label text-on-surface-variant/50">
                  max-calls/query: {meta.chat.max_calls_per_query}
                </span>
              </div>
            )}
          </div>

          {error && (
            <div className="mb-5 rounded border border-error/40 bg-error-container/20 text-error px-3 py-2 text-sm flex items-center justify-between">
              <span>{error}</span>
              <button onClick={() => void fetchTools()} className="text-xs font-label underline ml-4">Retry</button>
            </div>
          )}

          {/* Tabs */}
          <div className="flex items-center gap-1 border-b border-outline-variant/20 mb-5">
            {(['directory', 'invocations', 'cache'] as const).map((k) => (
              <button
                key={k}
                onClick={() => setTab(k)}
                className={[
                  'px-4 py-2 text-sm font-label font-medium transition-colors relative',
                  tab === k
                    ? 'text-primary-container after:absolute after:bottom-0 after:left-3 after:right-3 after:h-[2px] after:bg-primary-container'
                    : 'text-on-surface-variant hover:text-on-surface',
                ].join(' ')}
              >
                {k === 'directory' ? 'Directory' : k === 'invocations' ? 'Invocations' : 'Cache'}
                {k === 'invocations' && invocations.length > 0 && (
                  <span className="ml-2 text-[9px] font-mono px-1.5 py-0.5 rounded bg-surface-container-highest/60 text-on-surface-variant/60">
                    {invocations.length}
                  </span>
                )}
              </button>
            ))}
          </div>

          {/* Tab body */}
          {tab === 'directory' && (
            <ToolDirectory tools={tools} />
          )}
          {tab === 'invocations' && (
            <InvocationsTab invocations={invocations} />
          )}
          {tab === 'cache' && (
            <CacheControls stats={cacheStats} onClear={handleClearCache} />
          )}

          {loading && tools.length === 0 && (
            <p className="text-xs text-on-surface-variant/60 italic mt-4">Loading tools...</p>
          )}
        </div>
      </div>
    </div>
  )
}
