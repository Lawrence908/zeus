// zeus/frontend/src/components/chat/ChatInput.tsx
import { useState, useRef, useCallback, type KeyboardEvent, type ChangeEvent } from 'react'
import { useChatStore } from '../../store/chatStore'
import { useVoiceStore } from '../../store/voiceStore'
import { useSettingsStore } from '../../store/settingsStore'

interface ChatInputProps {
  onSend: (message: string) => Promise<void>
}

export function ChatInput({ onSend }: ChatInputProps) {
  const [value, setValue] = useState('')
  const textareaRef = useRef<HTMLTextAreaElement>(null)
  const isStreaming = useChatStore((s) => s.isStreaming)
  const { state: voiceState } = useVoiceStore()
  const { modelEnv } = useSettingsStore()

  const modelLabel = modelEnv === 'dev' ? 'Claude Sonnet 4.6' : 'Qwen 2.5-7B'

  const adjustHeight = useCallback(() => {
    const ta = textareaRef.current
    if (!ta) return
    ta.style.height = 'auto'
    const maxHeight = 8 * 24 // 8 rows * ~24px line height
    ta.style.height = `${Math.min(ta.scrollHeight, maxHeight)}px`
  }, [])

  const handleChange = (e: ChangeEvent<HTMLTextAreaElement>) => {
    setValue(e.target.value)
    adjustHeight()
  }

  const handleSend = async () => {
    const trimmed = value.trim()
    if (!trimmed || isStreaming) return
    setValue('')
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto'
    }
    await onSend(trimmed)
  }

  const handleKeyDown = (e: KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      void handleSend()
    }
  }

  const handleMicClick = () => {
    // Trigger wake word / voice capture — voiceStore handles actual state
    console.log('Voice capture requested, current state:', voiceState)
  }

  return (
    <div className="px-4 pb-4 pt-2">
      <div className="glass-panel border border-outline-variant/30 rounded-lg focus-within:border-primary-container/50 transition-colors">
        <div className="flex items-end gap-2 p-3">
          {/* Textarea */}
          <textarea
            ref={textareaRef}
            value={value}
            onChange={handleChange}
            onKeyDown={handleKeyDown}
            disabled={isStreaming}
            rows={1}
            placeholder="Awaiting tactical input..."
            className="flex-1 bg-transparent resize-none outline-none text-sm font-body text-on-surface placeholder:text-on-surface-variant/40 leading-6 disabled:opacity-50 max-h-[192px] overflow-y-auto custom-scrollbar"
          />

          {/* Mic button */}
          <button
            onClick={handleMicClick}
            disabled={isStreaming}
            title="Voice input"
            className="w-8 h-8 flex items-center justify-center text-on-surface-variant hover:text-primary transition-colors disabled:opacity-30 shrink-0"
          >
            <span className="material-symbols-outlined" style={{ fontSize: 18 }}>mic</span>
          </button>

          {/* Send button */}
          <button
            onClick={() => void handleSend()}
            disabled={isStreaming || !value.trim()}
            title="Send message"
            className="w-8 h-8 flex items-center justify-center rounded transition-all disabled:opacity-30 disabled:cursor-not-allowed shrink-0"
            style={{
              backgroundColor: value.trim() && !isStreaming ? '#00d4ff' : undefined,
              color: value.trim() && !isStreaming ? '#003642' : '#859398',
            }}
          >
            {isStreaming ? (
              <span
                className="w-3 h-3 border-2 border-on-surface-variant/30 border-t-on-surface-variant rounded-full"
                style={{ animation: 'orb-spin-slow 0.6s linear infinite' }}
              />
            ) : (
              <span className="material-symbols-outlined" style={{ fontSize: 18 }}>send</span>
            )}
          </button>
        </div>

        {/* Footer row */}
        <div className="flex items-center justify-between px-3 pb-2">
          <span className="text-[10px] font-label tracking-widest uppercase text-on-surface-variant/30">
            Shift + Enter for new line
          </span>
          <span className="text-[10px] font-label tracking-widest uppercase text-on-surface-variant/40">
            {modelLabel}
          </span>
        </div>
      </div>
    </div>
  )
}
