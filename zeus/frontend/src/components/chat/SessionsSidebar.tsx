// zeus/frontend/src/components/chat/SessionsSidebar.tsx
import { useEffect, useState, useCallback } from 'react'
import { useChatStore, type Session } from '../../store/chatStore'
import { SourceBadge } from '../common/SourceBadge'

function timeAgo(timestamp: number): string {
  const seconds = Math.floor((Date.now() - timestamp) / 1000)
  if (seconds < 60) return 'just now'
  const minutes = Math.floor(seconds / 60)
  if (minutes < 60) return `${minutes}m ago`
  const hours = Math.floor(minutes / 60)
  if (hours < 24) return `${hours}h ago`
  const days = Math.floor(hours / 24)
  return `${days}d ago`
}

export function SessionsSidebar() {
  const { sessions, activeSessionId, setSessions, setActiveSession, setMessages } = useChatStore()
  const [memoryLoad, setMemoryLoad] = useState(64)

  const fetchSessions = useCallback(async () => {
    try {
      const res = await fetch('/chat/sessions')
      if (res.ok) {
        const data = await res.json() as { sessions?: Session[] } | Session[]
        const list = Array.isArray(data) ? data : (data as { sessions?: Session[] }).sessions ?? []
        setSessions(list)
      }
    } catch {
      // backend not available during dev — use empty state
    }
  }, [setSessions])

  const fetchMemoryLoad = useCallback(async () => {
    try {
      const res = await fetch('/admin/metrics')
      if (res.ok) {
        const data = await res.json() as { memory_load?: number }
        if (typeof data.memory_load === 'number') {
          setMemoryLoad(data.memory_load)
        }
      }
    } catch {
      // fallback to 64%
    }
  }, [])

  useEffect(() => {
    void fetchSessions()
    void fetchMemoryLoad()
    const interval = setInterval(() => {
      void fetchSessions()
    }, 30_000)
    return () => clearInterval(interval)
  }, [fetchSessions, fetchMemoryLoad])

  const handleSessionClick = async (session: Session) => {
    setActiveSession(session.id)
    try {
      const res = await fetch(`/chat/sessions/${session.id}/messages`)
      if (res.ok) {
        const data = await res.json() as { messages?: import('../../store/chatStore').Message[] }
        if (Array.isArray(data.messages)) {
          setMessages(data.messages)
        }
      }
    } catch {
      setMessages([])
    }
  }

  const handleNewSession = async () => {
    setActiveSession(null)
    setMessages([])
    try {
      const res = await fetch('/chat/sessions', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({}) })
      if (res.ok) {
        const newSession = await res.json() as Session
        setSessions([newSession, ...sessions])
        setActiveSession(newSession.id)
      }
    } catch {
      // create local session
    }
    await fetchSessions()
  }

  return (
    <aside className="w-[240px] shrink-0 border-r border-outline-variant/20 flex flex-col bg-surface-container-lowest/50">
      {/* New Session button */}
      <div className="p-3 border-b border-outline-variant/20">
        <button
          onClick={() => void handleNewSession()}
          className="w-full py-2 px-3 text-xs font-label font-semibold tracking-[0.15em] uppercase text-on-primary-container border border-primary-container/40 rounded hover:bg-primary-container/10 transition-colors"
          style={{ color: '#00d4ff', borderColor: 'rgba(0, 212, 255, 0.3)' }}
        >
          + New Session
        </button>
      </div>

      {/* Session list */}
      <div className="flex-1 overflow-y-auto custom-scrollbar py-2">
        {sessions.length === 0 ? (
          <div className="px-3 py-6 text-center">
            <p className="text-xs font-body text-on-surface-variant/50">No sessions yet</p>
          </div>
        ) : (
          sessions.map((session) => {
            const isActive = session.id === activeSessionId
            return (
              <button
                key={session.id}
                onClick={() => void handleSessionClick(session)}
                className={[
                  'w-full text-left px-3 py-2.5 transition-colors',
                  'border-l-2',
                  isActive
                    ? 'border-primary-container bg-surface-container-low/60'
                    : 'border-transparent hover:bg-surface-container-low/30',
                ].join(' ')}
              >
                <div className="flex items-start justify-between gap-1 mb-1">
                  <span
                    className={[
                      'text-xs font-body font-medium truncate flex-1',
                      isActive ? 'text-primary-container' : 'text-on-surface',
                    ].join(' ')}
                    style={isActive ? { color: '#00d4ff' } : undefined}
                  >
                    {session.topic ?? 'Untitled Session'}
                  </span>
                  {session.source && <SourceBadge source={session.source} />}
                </div>
                <div className="flex items-center gap-2 text-[10px] font-label text-on-surface-variant/50 uppercase tracking-wider">
                  <span>{session.turn_count} turns</span>
                  <span>·</span>
                  <span>{timeAgo(session.updated_at)}</span>
                </div>
              </button>
            )
          })
        )}
      </div>

      {/* Memory load bar */}
      <div className="p-3 border-t border-outline-variant/20">
        <div className="flex items-center justify-between mb-1">
          <span className="text-[10px] font-label uppercase tracking-widest text-on-surface-variant/50">
            Memory Load
          </span>
          <span className="text-[10px] font-label text-on-surface-variant/70">
            {memoryLoad}%
          </span>
        </div>
        <div className="h-1 bg-surface-container-high rounded-full overflow-hidden">
          <div
            className="h-full rounded-full transition-all duration-500"
            style={{
              width: `${memoryLoad}%`,
              background: memoryLoad > 80
                ? 'linear-gradient(90deg, #6001d1, #ffb4ab)'
                : 'linear-gradient(90deg, #6001d1, #00d4ff)',
            }}
          />
        </div>
      </div>
    </aside>
  )
}
