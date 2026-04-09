// zeus/frontend/src/components/chat/ChatInput.tsx
import { useState, useRef, useCallback, type KeyboardEvent, type ChangeEvent } from 'react'
import { useChatStore } from '../../store/chatStore'
import { useSettingsStore } from '../../store/settingsStore'

export interface ChatInputVoiceProps {
  isRecording: boolean
  isVoiceSending: boolean
  onToggleMic: () => void
}

interface ChatInputProps {
  onSend: (message: string) => Promise<void>
  voice?: ChatInputVoiceProps
}

export function ChatInput({ onSend, voice }: ChatInputProps) {
  const [value, setValue] = useState('')
  const textareaRef = useRef<HTMLTextAreaElement>(null)
  const isStreaming = useChatStore((s) => s.isStreaming)
  const { modelEnv } = useSettingsStore()

  const micBusy = Boolean(voice?.isRecording || voice?.isVoiceSending)
  const inputLocked = isStreaming || Boolean(voice?.isVoiceSending)

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
    if (!trimmed || inputLocked) return
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
            disabled={inputLocked}
            rows={1}
            placeholder="Awaiting tactical input..."
            className="flex-1 bg-transparent resize-none outline-none text-sm font-body text-on-surface placeholder:text-on-surface-variant/40 leading-6 disabled:opacity-50 max-h-[192px] overflow-y-auto custom-scrollbar"
          />

          {/* Mic — push-to-talk: click start, click stop → /voice/interact */}
          <button
            type="button"
            onClick={() => voice?.onToggleMic()}
            disabled={!voice || isStreaming || Boolean(voice?.isVoiceSending)}
            title={
              voice
                ? voice.isRecording
                  ? 'Stop and send to Zeus'
                  : voice.isVoiceSending
                    ? 'Transcribing…'
                    : 'Voice: click to start, click again to stop'
                : 'Voice unavailable'
            }
            className="w-8 h-8 flex items-center justify-center transition-colors disabled:opacity-30 shrink-0 rounded text-on-surface-variant hover:text-primary"
            style={{
              color: voice?.isRecording ? '#ff6b6b' : voice?.isVoiceSending ? '#00d4ff' : undefined,
              boxShadow: voice?.isRecording ? '0 0 0 2px rgba(255,107,107,0.35)' : undefined,
            }}
          >
            {voice?.isVoiceSending ? (
              <span
                className="w-3.5 h-3.5 border-2 border-current border-t-transparent rounded-full"
                style={{ animation: 'orb-spin-slow 0.7s linear infinite' }}
              />
            ) : (
              <span className="material-symbols-outlined" style={{ fontSize: 18 }}>
                {voice?.isRecording ? 'stop_circle' : 'mic'}
              </span>
            )}
          </button>

          {/* Send button */}
          <button
            onClick={() => void handleSend()}
            disabled={inputLocked || !value.trim() || micBusy}
            title="Send message"
            className="w-8 h-8 flex items-center justify-center rounded transition-all disabled:opacity-30 disabled:cursor-not-allowed shrink-0"
            style={{
              backgroundColor: value.trim() && !inputLocked && !micBusy ? '#00d4ff' : undefined,
              color: value.trim() && !inputLocked && !micBusy ? '#003642' : '#859398',
            }}
          >
            {isStreaming && !micBusy ? (
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
            Shift+Enter newline · Mic: click start / click stop
          </span>
          <span className="text-[10px] font-label tracking-widest uppercase text-on-surface-variant/40">
            {modelLabel}
          </span>
        </div>
      </div>
    </div>
  )
}
