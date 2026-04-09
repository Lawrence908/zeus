// zeus/frontend/src/components/chat/ChatBubble.tsx
import type { Message } from '../../store/chatStore'
import { MarkdownMessage } from './MarkdownMessage'
import { SourceBadge } from '../common/SourceBadge'
import { AegisBadge } from '../common/AegisBadge'

interface ChatBubbleProps {
  message: Message
}

function ThinkingIndicator() {
  return (
    <div className="flex items-center gap-2 text-on-surface-variant">
      <div className="flex gap-1">
        {[0, 1, 2].map((i) => (
          <span
            key={i}
            className="w-1.5 h-1.5 rounded-full bg-primary/50"
            style={{
              animation: `thinking-dot 1.4s ease-in-out ${i * 0.16}s infinite`,
              display: 'inline-block',
            }}
          />
        ))}
      </div>
      <span className="text-xs font-label tracking-widest uppercase text-on-surface-variant/60">
        Processing Data Streams...
      </span>
    </div>
  )
}

function AssistantBubble({ message }: ChatBubbleProps) {
  const showThinking = message.isStreaming && message.content === ''

  return (
    <div className="flex flex-col gap-2 max-w-[85%]">
      {/* Header */}
      <div className="flex items-center gap-1.5">
        <span className="material-symbols-outlined text-primary-container" style={{ fontSize: 14 }}>
          bolt
        </span>
        <span className="font-label text-[10px] font-semibold tracking-[0.15em] uppercase text-primary-container">
          Zeus Intelligence
        </span>
      </div>

      {/* Message body */}
      <div className="bg-surface-container/40 border border-outline-variant/10 rounded p-5 text-sm text-on-surface font-body leading-relaxed">
        {showThinking ? (
          <ThinkingIndicator />
        ) : (
          <MarkdownMessage content={message.content} />
        )}
      </div>

      {/* Badges */}
      <div className="flex flex-wrap gap-1.5 items-center">
        {message.source && <SourceBadge source={message.source} />}
        {message.model_used && (
          <span className="text-[10px] font-label text-on-surface-variant/50 uppercase tracking-wider">
            {message.model_used}
          </span>
        )}
        {message.context_sources && message.context_sources.map((src) => (
          <span
            key={src}
            className="text-[10px] font-label px-1.5 py-0.5 bg-surface-container-high border border-outline-variant/20 rounded text-on-surface-variant uppercase tracking-wider"
          >
            {src}
          </span>
        ))}
        <AegisBadge flags={message.aegis_flags} />
      </div>
    </div>
  )
}

function UserBubble({ message }: ChatBubbleProps) {
  return (
    <div className="flex flex-col items-end gap-2 max-w-[85%] ml-auto">
      {/* Header */}
      <div className="flex items-center gap-1.5">
        <span className="font-label text-[10px] font-semibold tracking-[0.15em] uppercase text-on-surface-variant">
          Operator Alpha
        </span>
        <span className="material-symbols-outlined text-on-surface-variant" style={{ fontSize: 14 }}>
          person
        </span>
      </div>

      {/* Message body */}
      <div className="bg-primary-container/5 border border-primary/10 rounded p-4 text-sm text-on-surface font-body leading-relaxed text-right">
        <MarkdownMessage content={message.content} />
      </div>
      {message.source && message.source !== 'web' && (
        <div className="flex justify-end">
          <SourceBadge source={message.source} />
        </div>
      )}
    </div>
  )
}

export function ChatBubble({ message }: ChatBubbleProps) {
  return (
    <div className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'} mb-6`}>
      {message.role === 'assistant' ? (
        <AssistantBubble message={message} />
      ) : (
        <UserBubble message={message} />
      )}
    </div>
  )
}
