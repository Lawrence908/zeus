// zeus/frontend/src/store/chatStore.ts
import { create } from 'zustand'

export interface Message {
  id: string
  role: 'user' | 'assistant'
  content: string
  timestamp: number
  source?: string
  aegis_flags?: string[]
  context_sources?: string[]
  model_used?: string
  isStreaming?: boolean
}

export interface Session {
  id: string
  topic?: string
  turn_count: number
  updated_at: number
  source?: string
}

interface ChatStore {
  sessions: Session[]
  activeSessionId: string | null
  messages: Message[]
  isStreaming: boolean
  setSessions: (s: Session[]) => void
  setActiveSession: (id: string | null) => void
  setMessages: (m: Message[]) => void
  addMessage: (m: Message) => void
  appendToLastMessage: (token: string) => void
  setStreaming: (b: boolean) => void
}

export const useChatStore = create<ChatStore>((set) => ({
  sessions: [],
  activeSessionId: null,
  messages: [],
  isStreaming: false,

  setSessions: (sessions) => set({ sessions: Array.isArray(sessions) ? sessions : [] }),
  setActiveSession: (activeSessionId) => set({ activeSessionId }),
  setMessages: (messages) => set({ messages: Array.isArray(messages) ? messages : [] }),

  addMessage: (message) =>
    set((state) => ({ messages: [...state.messages, message] })),

  appendToLastMessage: (token) =>
    set((state) => {
      const messages = [...state.messages]
      const last = messages[messages.length - 1]
      if (last && last.role === 'assistant') {
        messages[messages.length - 1] = {
          ...last,
          content: last.content + token,
        }
      }
      return { messages }
    }),

  setStreaming: (isStreaming) => set({ isStreaming }),
}))
