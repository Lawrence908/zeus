// zeus/frontend/src/store/toolsStore.ts — Tools page state + polling
//
// Two long-lived data streams:
//   - tools directory (rarely changes; fetched on mount + every 30s)
//   - recent invocations (polled every 5s while the Invocations tab is visible)
// Cache stats are refetched on every invocation poll tick so the Cache panel
// stays fresh without its own timer.
import { create } from 'zustand'

// ---------------------------------------------------------------------------
// Types — mirror zeus/core/admin.py response shapes
// ---------------------------------------------------------------------------

export type ToolSource = 'chat' | 'mcp'

export interface ToolSpec {
  source: ToolSource
  name: string
  description: string
  parameters: Record<string, unknown>
  cacheable: boolean
  aegis_policy: string | null
  timeout_seconds: number | null
  write_gated: boolean
  write_enabled_now?: boolean
}

export interface ToolsMeta {
  chat: {
    enabled: boolean
    max_calls_per_query: number
    count: number
  }
  mcp: {
    write_enabled: boolean
    count: number
  }
}

export interface ToolInvocation {
  ts: number
  tool: string
  source: 'chat' | 'chat_async' | 'direct'
  args: Record<string, unknown>
  content: string
  is_error: boolean
  cache_hit: boolean
  duration_ms: number
  aegis_flags: string[]
  aegis_rejected: boolean
}

export interface CacheStats {
  size: number
  hits: number
  misses: number
  ttl_seconds: number
  max_entries: number
  registered_tools?: Array<{ name: string; cacheable: boolean }>
}

// ---------------------------------------------------------------------------
// Store
// ---------------------------------------------------------------------------

interface ToolsState {
  tools: ToolSpec[]
  meta: ToolsMeta | null
  invocations: ToolInvocation[]
  cacheStats: CacheStats | null
  loading: boolean
  error: string | null
  // Filters
  search: string
  sourceFilter: ToolSource | 'all'
  // Actions
  fetchTools: () => Promise<void>
  fetchInvocations: () => Promise<void>
  fetchCacheStats: () => Promise<void>
  clearCache: () => Promise<void>
  setSearch: (s: string) => void
  setSourceFilter: (s: ToolSource | 'all') => void
}

export const useToolsStore = create<ToolsState>((set, get) => ({
  tools: [],
  meta: null,
  invocations: [],
  cacheStats: null,
  loading: false,
  error: null,
  search: '',
  sourceFilter: 'all',

  fetchTools: async () => {
    set({ loading: true, error: null })
    try {
      const res = await fetch('/admin/tools')
      if (!res.ok) throw new Error(`HTTP ${res.status}`)
      const data = (await res.json()) as {
        tools: ToolSpec[]
        chat: ToolsMeta['chat']
        mcp: ToolsMeta['mcp']
      }
      set({
        tools: data.tools ?? [],
        meta: { chat: data.chat, mcp: data.mcp },
        loading: false,
      })
    } catch (err) {
      set({ error: err instanceof Error ? err.message : String(err), loading: false })
    }
  },

  fetchInvocations: async () => {
    try {
      const res = await fetch('/admin/tools/invocations?limit=50')
      if (!res.ok) return
      const data = (await res.json()) as { invocations: ToolInvocation[] }
      set({ invocations: data.invocations ?? [] })
    } catch {
      // transient; next tick will retry
    }
  },

  fetchCacheStats: async () => {
    try {
      const res = await fetch('/admin/tool_cache/stats')
      if (!res.ok) return
      const data = (await res.json()) as CacheStats
      set({ cacheStats: data })
    } catch {
      // transient
    }
  },

  clearCache: async () => {
    try {
      await fetch('/admin/tool_cache/clear', { method: 'POST' })
    } finally {
      // Always refresh so the UI reflects the post-clear state (size=0).
      void get().fetchCacheStats()
    }
  },

  setSearch: (s) => set({ search: s }),
  setSourceFilter: (s) => set({ sourceFilter: s }),
}))
