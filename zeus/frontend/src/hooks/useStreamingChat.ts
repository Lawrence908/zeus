// zeus/frontend/src/hooks/useStreamingChat.ts
import { useRef, useCallback } from 'react'
import { useChatStore } from '../store/chatStore'

function generateId(): string {
  return `msg-${Date.now()}-${Math.random().toString(36).slice(2, 9)}`
}

export function useStreamingChat() {
  const { addMessage, appendToLastMessage, setStreaming, isStreaming } = useChatStore()
  const abortRef = useRef<AbortController | null>(null)

  const abort = useCallback(() => {
    abortRef.current?.abort()
  }, [])

  const send = useCallback(
    async (message: string, sessionId: string | null) => {
      if (isStreaming) return

      // Add user message immediately
      addMessage({
        id: generateId(),
        role: 'user',
        content: message,
        timestamp: Date.now(),
        source: 'web',
      })

      // Placeholder assistant message
      const assistantId = generateId()
      addMessage({
        id: assistantId,
        role: 'assistant',
        content: '',
        timestamp: Date.now(),
        isStreaming: true,
      })

      setStreaming(true)
      abortRef.current = new AbortController()

      try {
        const response = await fetch('/chat/stream', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ message, session_id: sessionId }),
          signal: abortRef.current.signal,
        })

        if (!response.ok || !response.body) {
          throw new Error(`HTTP ${response.status}`)
        }

        const reader = response.body.getReader()
        const decoder = new TextDecoder()
        let buf = ''

        while (true) {
          const { done, value } = await reader.read()
          if (done) break

          buf += decoder.decode(value, { stream: true })
          const lines = buf.split('\n')
          // Keep the last (possibly incomplete) line in the buffer
          buf = lines.pop() ?? ''

          for (const line of lines) {
            if (line.startsWith('data: ')) {
              const data = line.slice(6).trim()
              if (data === '[DONE]') {
                break
              }
              if (data) {
                try {
                  const parsed = JSON.parse(data) as {
                    type?: string
                    token?: string
                    content?: string
                    session_id?: string
                    detail?: string
                  }
                  if (parsed.type === 'done' && typeof parsed.session_id === 'string') {
                    useChatStore.getState().setActiveSession(parsed.session_id)
                    continue
                  }
                  if (parsed.type === 'error' && typeof parsed.detail === 'string') {
                    appendToLastMessage(`\n\n_[${parsed.detail}]_`)
                    continue
                  }
                  if (parsed.type === 'phase') {
                    continue
                  }
                  const token = parsed.token ?? parsed.content ?? ''
                  if (token) appendToLastMessage(token)
                } catch {
                  // raw token fallback
                  appendToLastMessage(data)
                }
              }
            }
          }
        }
      } catch (err) {
        if ((err as Error).name === 'AbortError') {
          // user aborted — leave content as-is
        } else {
          // SSE failed — try plain POST fallback
          try {
            const fallbackRes = await fetch('/chat/message', {
              method: 'POST',
              headers: { 'Content-Type': 'application/json' },
              body: JSON.stringify({ message, session_id: sessionId }),
            })
            if (fallbackRes.ok) {
              const data = await fallbackRes.json() as {
                assistant_message?: string
                session_id?: string
              }
              const content = data.assistant_message ?? ''
              appendToLastMessage(content)
              if (typeof data.session_id === 'string') {
                useChatStore.getState().setActiveSession(data.session_id)
              }
            } else {
              appendToLastMessage('\n\n_[Error: Could not reach Zeus backend]_')
            }
          } catch {
            appendToLastMessage('\n\n_[Error: Zeus backend unavailable]_')
          }
        }
      } finally {
        // Mark streaming done — mutate the message in store via setStreaming
        setStreaming(false)
        // Clear the isStreaming flag on the assistant message by appending empty string
        // (the flag is checked by content being empty, not a separate store field per message)
        useChatStore.setState((state) => ({
          messages: state.messages.map((m) =>
            m.id === assistantId ? { ...m, isStreaming: false } : m
          ),
        }))
      }
    },
    [addMessage, appendToLastMessage, setStreaming, isStreaming]
  )

  return { send, isStreaming, abort }
}
