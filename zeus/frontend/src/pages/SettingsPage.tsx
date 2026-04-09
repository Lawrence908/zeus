// zeus/frontend/src/pages/SettingsPage.tsx
import { useState, useEffect, type ReactNode } from 'react'
import { TopNav } from '../components/layout/TopNav'
import { useSettingsStore } from '../store/settingsStore'

type Section = 'model' | 'aegis' | 'telegram' | 'sessions' | 'voice' | 'appearance'

const SECTIONS: { id: Section; label: string; icon: string }[] = [
  { id: 'model', label: 'Model', icon: 'model_training' },
  { id: 'aegis', label: 'Aegis Safety', icon: 'shield_with_heart' },
  { id: 'telegram', label: 'Telegram', icon: 'send' },
  { id: 'sessions', label: 'Sessions', icon: 'chat_bubble' },
  { id: 'voice', label: 'Voice', icon: 'mic' },
  { id: 'appearance', label: 'Appearance', icon: 'contrast' },
]

interface ToggleProps {
  checked: boolean
  onChange: (v: boolean) => void
  label?: string
}

function Toggle({ checked, onChange, label }: ToggleProps) {
  return (
    <label className="flex items-center gap-3 cursor-pointer">
      <input
        type="checkbox"
        role="switch"
        className="sr-only"
        checked={checked}
        onChange={() => onChange(!checked)}
      />
      <div
        className="relative w-10 h-5 rounded-full transition-colors"
        style={{ backgroundColor: checked ? '#00d4ff' : '#3c494e' }}
      >
        <div
          className="absolute top-0.5 w-4 h-4 rounded-full bg-white transition-transform"
          style={{ transform: checked ? 'translateX(20px)' : 'translateX(2px)' }}
        />
      </div>
      {label && (
        <span className="text-sm font-body text-on-surface">{label}</span>
      )}
    </label>
  )
}

interface FieldLabelProps {
  children: ReactNode
  htmlFor?: string
}

function FieldLabel({ children, htmlFor }: FieldLabelProps) {
  return (
    <label
      htmlFor={htmlFor}
      className="block text-[10px] font-label uppercase tracking-widest text-on-surface-variant/60 mb-1"
    >
      {children}
    </label>
  )
}

function SectionTitle({ children }: { children: ReactNode }) {
  return (
    <h2 className="font-headline font-semibold text-base text-on-surface mb-4 pb-2 border-b border-outline-variant/20">
      {children}
    </h2>
  )
}

function inputClass() {
  return 'w-full bg-surface-container-high border border-outline-variant/30 rounded px-3 py-2 text-sm font-body text-on-surface placeholder:text-on-surface-variant/40 outline-none focus:border-primary-container/50 transition-colors'
}

export function SettingsPage() {
  const [activeSection, setActiveSection] = useState<Section>('model')
  const [currentModel, setCurrentModel] = useState<string>('')

  const {
    theme, setTheme,
    modelEnv, setModelEnv,
    aegisEnabled, setAegisEnabled,
    activePolicy, setActivePolicy,
    telegramEnabled, setTelegramEnabled,
    telegramBotToken, setTelegramBotToken,
    telegramChatIds, setTelegramChatIds,
    autoSummarize, setAutoSummarize,
    sessionWindowSize, setSessionWindowSize,
    voiceReplyEnabled, setVoiceReplyEnabled,
  } = useSettingsStore()

  useEffect(() => {
    const fetchStatus = async () => {
      try {
        const res = await fetch('/status')
        if (res.ok) {
          const data = await res.json() as { model?: string; model_name?: string }
          setCurrentModel(data.model ?? data.model_name ?? '')
        }
      } catch {
        // backend not available
      }
    }
    void fetchStatus()
  }, [])

  return (
    <div className="flex flex-col h-screen bg-background">
      <TopNav />

      <div className="flex flex-1 overflow-hidden pt-[52px]">
        {/* Settings nav sidebar */}
        <aside className="w-[220px] shrink-0 border-r border-outline-variant/20 bg-surface-container-lowest/50 p-4">
          <div className="mb-4">
            <span className="text-[10px] font-label uppercase tracking-[0.2em] text-on-surface-variant/40">
              Configuration
            </span>
          </div>
          <nav className="flex flex-col gap-0.5">
            {SECTIONS.map((section) => (
              <button
                key={section.id}
                onClick={() => setActiveSection(section.id)}
                className={[
                  'flex items-center gap-2.5 px-3 py-2 rounded text-sm font-body transition-colors text-left',
                  activeSection === section.id
                    ? 'bg-surface-container-low text-primary-container'
                    : 'text-on-surface-variant hover:text-on-surface hover:bg-surface-container-low/50',
                ].join(' ')}
                style={activeSection === section.id ? { color: '#00d4ff' } : undefined}
              >
                <span className="material-symbols-outlined" style={{ fontSize: 16 }}>
                  {section.icon}
                </span>
                {section.label}
              </button>
            ))}
          </nav>
        </aside>

        {/* Settings content */}
        <div className="flex-1 overflow-y-auto custom-scrollbar px-8 py-8 max-w-2xl">
          {/* Model section */}
          {activeSection === 'model' && (
            <div>
              <SectionTitle>Model Configuration</SectionTitle>

              <div className="mb-6">
                <FieldLabel>Environment</FieldLabel>
                <div className="flex gap-3 mt-1">
                  {(['dev', 'prod'] as const).map((env) => (
                    <label key={env} className="flex items-center gap-2 cursor-pointer">
                      <input
                        type="radio"
                        name="modelEnv"
                        value={env}
                        checked={modelEnv === env}
                        onChange={() => setModelEnv(env)}
                        className="accent-primary-container"
                      />
                      <span className="text-sm font-body text-on-surface uppercase">
                        {env}
                      </span>
                      <span className="text-xs font-body text-on-surface-variant">
                        {env === 'dev' ? '— Claude Sonnet 4.6' : '— Qwen 2.5-7B Q4'}
                      </span>
                    </label>
                  ))}
                </div>
              </div>

              {currentModel && (
                <div className="p-3 bg-surface-container-low rounded border border-outline-variant/20">
                  <FieldLabel>Active Model (from /status)</FieldLabel>
                  <p className="text-sm font-body text-primary font-medium">{currentModel}</p>
                </div>
              )}
            </div>
          )}

          {/* Aegis section */}
          {activeSection === 'aegis' && (
            <div>
              <SectionTitle>Aegis Safety</SectionTitle>

              <div className="mb-6">
                <Toggle
                  checked={aegisEnabled}
                  onChange={setAegisEnabled}
                  label="Enable Aegis guardrails"
                />
                <p className="mt-1.5 text-xs font-body text-on-surface-variant/60">
                  NemoClaw + OpenShell policy enforcement on all LLM output.
                </p>
              </div>

              <div className="mb-6">
                <FieldLabel htmlFor="policy">Active Policy</FieldLabel>
                <input
                  id="policy"
                  type="text"
                  value={activePolicy}
                  onChange={(e) => setActivePolicy(e.target.value)}
                  placeholder="default"
                  className={inputClass()}
                  disabled={!aegisEnabled}
                />
              </div>
            </div>
          )}

          {/* Telegram section */}
          {activeSection === 'telegram' && (
            <div>
              <SectionTitle>Telegram Integration</SectionTitle>

              <div className="mb-6">
                <Toggle
                  checked={telegramEnabled}
                  onChange={setTelegramEnabled}
                  label="Enable Telegram bot"
                />
              </div>

              <div className="mb-4">
                <FieldLabel htmlFor="botToken">Bot Token</FieldLabel>
                <input
                  id="botToken"
                  type="password"
                  value={telegramBotToken}
                  onChange={(e) => setTelegramBotToken(e.target.value)}
                  placeholder="••••••••••••••••••••••"
                  className={inputClass()}
                  disabled={!telegramEnabled}
                />
              </div>

              <div className="mb-4">
                <FieldLabel htmlFor="chatIds">Allowed Chat IDs</FieldLabel>
                <textarea
                  id="chatIds"
                  value={telegramChatIds}
                  onChange={(e) => setTelegramChatIds(e.target.value)}
                  rows={4}
                  placeholder="One chat ID per line..."
                  className={`${inputClass()} resize-none`}
                  disabled={!telegramEnabled}
                />
                <p className="mt-1 text-xs font-body text-on-surface-variant/50">
                  One Telegram chat ID per line.
                </p>
              </div>
            </div>
          )}

          {/* Sessions section */}
          {activeSection === 'sessions' && (
            <div>
              <SectionTitle>Session Preferences</SectionTitle>

              <div className="mb-6">
                <Toggle
                  checked={autoSummarize}
                  onChange={setAutoSummarize}
                  label="Auto-summarize sessions"
                />
                <p className="mt-1.5 text-xs font-body text-on-surface-variant/60">
                  Generate rolling summaries as sessions grow.
                </p>
              </div>

              <div className="mb-4">
                <FieldLabel htmlFor="windowSize">
                  Session Window Size — {sessionWindowSize} turns
                </FieldLabel>
                <input
                  id="windowSize"
                  type="range"
                  min={4}
                  max={32}
                  step={4}
                  value={sessionWindowSize}
                  onChange={(e) => setSessionWindowSize(Number(e.target.value))}
                  className="w-full accent-primary-container mt-1"
                />
                <div className="flex justify-between text-[10px] font-label text-on-surface-variant/40 mt-1">
                  <span>4</span>
                  <span>32</span>
                </div>
              </div>
            </div>
          )}

          {/* Voice section */}
          {activeSection === 'voice' && (
            <div>
              <SectionTitle>Voice</SectionTitle>
              <p className="text-sm font-body text-on-surface-variant/80 mb-4">
                On the chat page, the microphone uses Zeus <code className="text-xs bg-surface-container-high px-1 rounded">/voice/interact</code>{' '}
                (Whisper STT, then the same session as text). High-quality TTS will use Voicebox / LuxTTS when wired; for now you can use the browser as a stand-in.
              </p>
              <div className="mb-6">
                <Toggle
                  checked={voiceReplyEnabled}
                  onChange={setVoiceReplyEnabled}
                  label="Speak assistant replies (browser TTS)"
                />
                <p className="mt-1.5 text-xs font-body text-on-surface-variant/60">
                  After a voice turn, read the reply with the OS voice. Disable for silent transcripts only.
                </p>
              </div>
            </div>
          )}

          {/* Appearance section */}
          {activeSection === 'appearance' && (
            <div>
              <SectionTitle>Appearance</SectionTitle>

              <div className="mb-6">
                <FieldLabel>Theme</FieldLabel>
                <div className="flex gap-3 mt-1">
                  {(['dark', 'light'] as const).map((t) => (
                    <label key={t} className="flex items-center gap-2 cursor-pointer">
                      <input
                        type="radio"
                        name="theme"
                        value={t}
                        checked={theme === t}
                        onChange={() => setTheme(t)}
                        className="accent-primary-container"
                      />
                      <span className="text-sm font-body text-on-surface capitalize">{t}</span>
                    </label>
                  ))}
                </div>
              </div>

              {currentModel && (
                <div className="p-3 bg-surface-container-low rounded border border-outline-variant/20">
                  <FieldLabel>Current Model</FieldLabel>
                  <p className="text-sm font-body text-on-surface">{currentModel}</p>
                </div>
              )}

              <div className="mt-6 p-4 bg-surface-container/40 rounded border border-outline-variant/10">
                <p className="text-[10px] font-label uppercase tracking-widest text-on-surface-variant/40 mb-3">
                  Color Preview
                </p>
                <div className="grid grid-cols-4 gap-1.5">
                  {[
                    { color: '#00d4ff', label: 'Primary' },
                    { color: '#6001d1', label: 'Secondary' },
                    { color: '#a7c2ff', label: 'Tertiary' },
                    { color: '#1e1f26', label: 'Surface' },
                  ].map((swatch) => (
                    <div key={swatch.label} className="flex flex-col items-center gap-1">
                      <div
                        className="w-8 h-8 rounded"
                        style={{ backgroundColor: swatch.color, border: '1px solid rgba(60,73,78,0.3)' }}
                      />
                      <span className="text-[9px] font-label text-on-surface-variant/50">{swatch.label}</span>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
