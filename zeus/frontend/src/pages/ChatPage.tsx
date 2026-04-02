// zeus/frontend/src/pages/ChatPage.tsx
import { useEffect } from 'react'
import { TopNav } from '../components/layout/TopNav'
import { SessionsSidebar } from '../components/chat/SessionsSidebar'
import { MessageList } from '../components/chat/MessageList'
import { ChatInput } from '../components/chat/ChatInput'
import { StatusPanel } from '../components/status/StatusPanel'
import { useChatStore } from '../store/chatStore'
import { useStreamingChat } from '../hooks/useStreamingChat'
import { useVoiceState } from '../hooks/useVoiceState'

export function ChatPage() {
  const { sessions, activeSessionId, setSessions, setActiveSession, setMessages } = useChatStore()
  const { send } = useStreamingChat()

  // Connect voice WebSocket
  useVoiceState()

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
    // Refresh sessions list to update turn counts
    try {
      const res = await fetch('/chat/sessions')
      if (res.ok) {
        const raw = await res.json() as { sessions?: import('../store/chatStore').Session[] } | import('../store/chatStore').Session[]
        setSessions(Array.isArray(raw) ? raw : (raw as { sessions?: import('../store/chatStore').Session[] }).sessions ?? [])
      }
    } catch {
      // ignore
    }
  }

  // Suppress unused warning — sessions used by SessionsSidebar via store
  void sessions

  return (
    <div className="flex flex-col h-screen bg-background">
      <TopNav />

      {/* Main layout below nav */}
      <div className="flex flex-1 overflow-hidden pt-[52px]">
        <SessionsSidebar />

        {/* Center: messages + input */}
        <div className="flex flex-col flex-1 overflow-hidden">
          <MessageList />
          <ChatInput onSend={handleSend} />
        </div>

        <StatusPanel />
      </div>
    </div>
  )
}
