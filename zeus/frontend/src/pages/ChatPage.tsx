// zeus/frontend/src/pages/ChatPage.tsx
import { useEffect, useCallback, useState } from 'react'
import { TopNav } from '../components/layout/TopNav'
import { SessionsSidebar } from '../components/chat/SessionsSidebar'
import { MessageList } from '../components/chat/MessageList'
import { ChatInput } from '../components/chat/ChatInput'
import { StatusPanel } from '../components/status/StatusPanel'
import { useChatStore } from '../store/chatStore'
import { useStreamingChat } from '../hooks/useStreamingChat'
import { useVoiceState } from '../hooks/useVoiceState'
import { useVoiceChat } from '../hooks/useVoiceChat'

export function ChatPage() {
  const { sessions, activeSessionId, setSessions, setActiveSession, setMessages } = useChatStore()
  const { send } = useStreamingChat()

  // Mobile-only off-canvas drawers (sessions on the left, status on the right).
  const [sidebarOpen, setSidebarOpen] = useState(false)
  const [statusOpen, setStatusOpen] = useState(false)

  // Connect voice WebSocket (Phaos / host-native Orpheus state)
  useVoiceState()

  const refreshSessions = useCallback(async () => {
    try {
      const res = await fetch('/chat/sessions')
      if (res.ok) {
        const raw = await res.json() as { sessions?: import('../store/chatStore').Session[] } | import('../store/chatStore').Session[]
        setSessions(Array.isArray(raw) ? raw : (raw as { sessions?: import('../store/chatStore').Session[] }).sessions ?? [])
      }
    } catch {
      // ignore
    }
  }, [setSessions])

  const voice = useVoiceChat({ onTurnComplete: refreshSessions })

  useEffect(() => {
    const fetchSessions = async () => {
      try {
        const res = await fetch('/chat/sessions')
        if (res.ok) {
          const raw = await res.json() as { sessions?: import('../store/chatStore').Session[] } | import('../store/chatStore').Session[]
          const data = Array.isArray(raw) ? raw : (raw as { sessions?: import('../store/chatStore').Session[] }).sessions ?? []
          setSessions(data)
          if (data.length > 0 && !activeSessionId) {
            setActiveSession(data[0].id)
            // Load messages for first session
            try {
              const msgRes = await fetch(`/chat/sessions/${data[0].id}/messages`)
              if (msgRes.ok) {
                const msgData = await msgRes.json() as { messages?: import('../store/chatStore').Message[] }
                if (Array.isArray(msgData.messages)) {
                  setMessages(msgData.messages)
                }
              }
            } catch {
              // no messages yet
            }
          }
        }
      } catch {
        // backend not available in dev without server
      }
    }

    void fetchSessions()
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [])

  const handleSend = async (message: string) => {
    await send(message, activeSessionId)
    await refreshSessions()
  }

  // Suppress unused warning — sessions used by SessionsSidebar via store
  void sessions

  return (
    <div className="flex flex-col h-screen bg-background">
      <TopNav
        mobileLeftSlot={
          <button
            onClick={() => { setStatusOpen(false); setSidebarOpen((v) => !v) }}
            className="w-9 h-9 flex items-center justify-center text-on-surface-variant hover:text-on-surface"
            title="Sessions"
            aria-label="Toggle sessions"
          >
            <span className="material-symbols-outlined text-[20px]">forum</span>
          </button>
        }
        mobileRightSlot={
          <button
            onClick={() => { setSidebarOpen(false); setStatusOpen((v) => !v) }}
            className="w-9 h-9 flex items-center justify-center text-on-surface-variant hover:text-on-surface"
            title="System status"
            aria-label="Toggle status panel"
          >
            <span className="material-symbols-outlined text-[20px]">monitoring</span>
          </button>
        }
      />

      {/* Main layout below nav */}
      <div className="flex flex-1 overflow-hidden pt-[52px]">
        <SessionsSidebar open={sidebarOpen} onClose={() => setSidebarOpen(false)} />

        {/* Center: messages + input */}
        <div className="flex flex-col flex-1 min-w-0 overflow-hidden">
          <MessageList />
          <ChatInput
            onSend={handleSend}
            voice={{
              isRecording: voice.isRecording,
              isVoiceSending: voice.isVoiceSending,
              onToggleMic: () => {
                void voice.toggleRecording()
              },
            }}
          />
        </div>

        <StatusPanel open={statusOpen} onClose={() => setStatusOpen(false)} />
      </div>
    </div>
  )
}
