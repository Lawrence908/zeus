// zeus/frontend/src/components/chat/MessageList.tsx
import { useEffect, useRef } from 'react'
import { useChatStore } from '../../store/chatStore'
import { ChatBubble } from './ChatBubble'

export function MessageList() {
  const messages = useChatStore((s) => s.messages)
  const bottomRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  return (
    <div className="flex-1 overflow-y-auto custom-scrollbar px-6 py-6">
      {messages.length === 0 ? (
        <div className="flex flex-col items-center justify-center h-full gap-4 text-center">
          <span
            className="font-headline font-bold text-4xl"
            style={{ color: '#00d4ff', textShadow: '0 0 30px rgba(0,212,255,0.3)' }}
          >
            ⚡
          </span>
          <div>
            <p className="font-headline font-semibold text-on-surface text-lg mb-1">
              Zeus Intelligence Online
            </p>
            <p className="font-body text-sm text-on-surface-variant">
              Awaiting tactical input. How can I assist?
            </p>
          </div>
        </div>
      ) : (
        <>
          {messages.map((message) => (
            <ChatBubble key={message.id} message={message} />
          ))}
          <div ref={bottomRef} />
        </>
      )}
    </div>
  )
}
