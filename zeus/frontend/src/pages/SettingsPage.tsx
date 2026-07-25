// zeus/frontend/src/pages/SettingsPage.tsx
import { useState, useEffect, useCallback, type ReactNode } from 'react'
import { TopNav } from '../components/layout/TopNav'
import { useSettingsStore, type OllamaModelInfo } from '../store/settingsStore'

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

function formatBytes(bytes: number | null): string {
  if (bytes == null) return ''
  if (bytes < 1024 ** 3) return `${(bytes / 1024 ** 2).toFixed(0)} MB`
  return `${(bytes / 1024 ** 3).toFixed(1)} GB`
}

export function SettingsPage() {
  const [activeSection, setActiveSection] = useState<Section>('model')
  const [availableModels, setAvailableModels] = useState<OllamaModelInfo[]>([])
  const [activeModelInfo, setActiveModelInfo] = useState<{
    provider: string; model: string; gpu_available: boolean | null
  } | null>(null)
  const [modelLoading, setModelLoading] = useState(false)
  const [modelError, setModelError] = useState<string>('')

  const [telegramSaving, setTelegramSaving] = useState(false)
  const [telegramStatus, setTelegramStatus] = useState<string>('')
  const [telegramTokenMasked, setTelegramTokenMasked] = useState<string | null>(null)

  type BenchmarkResult = {
    model: string
    host: string
    started_at: number
    finished_at: number
    tokens_per_second: number
    ttft_ms: number | null
    prompt_eval_tps: number
    total_eval_tokens: number
    error: string | null
  }
  type BenchmarksPayload = {
    results: Record<string, BenchmarkResult>
    updated_at: number | null
    status: { running: boolean; current: string | null; queued: string[]; completed: string[] }
  }
  const [benchmarks, setBenchmarks] = useState<BenchmarksPayload | null>(null)
  const [benchStarting, setBenchStarting] = useState(false)

  const fetchBenchmarks = useCallback(async () => {
    try {
      const res = await fetch('/models/benchmarks')
      if (res.ok) setBenchmarks(await res.json() as BenchmarksPayload)
    } catch {
      // ignore
    }
  }, [])

  useEffect(() => {
    void fetchBenchmarks()
  }, [fetchBenchmarks])

  // Poll while a run is in progress
  useEffect(() => {
    if (!benchmarks?.status.running) return
    const id = setInterval(() => { void fetchBenchmarks() }, 2000)
    return () => clearInterval(id)
  }, [benchmarks?.status.running, fetchBenchmarks])

  const handleRunBenchmarks = async (models?: string[]) => {
    setBenchStarting(true)
    try {
      const res = await fetch('/models/benchmarks/run', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ models: models ?? null }),
      })
      if (res.ok) {
        await fetchBenchmarks()
      }
    } finally {
      setBenchStarting(false)
    }
  }

  const {
    theme, setTheme,
    modelEnv, setModelEnv,
    ollamaModel, setOllamaModel,
    aegisEnabled, setAegisEnabled,
    activePolicy, setActivePolicy,
    telegramEnabled, setTelegramEnabled,
    telegramBotToken, setTelegramBotToken,
    telegramChatIds, setTelegramChatIds,
    autoSummarize, setAutoSummarize,
    sessionWindowSize, setSessionWindowSize,
    voiceReplyEnabled, setVoiceReplyEnabled,
  } = useSettingsStore()

  const fetchModels = useCallback(async () => {
    try {
      const [modelsRes, activeRes] = await Promise.all([
        fetch('/models'),
        fetch('/models/active'),
      ])
      if (modelsRes.ok) {
        const data = await modelsRes.json() as { models: OllamaModelInfo[] }
        setAvailableModels(data.models)
      }
      if (activeRes.ok) {
        const data = await activeRes.json() as {
          provider: string; model: string; gpu_available: boolean | null
        }
        setActiveModelInfo(data)
        if (data.model && !ollamaModel) {
          setOllamaModel(data.model)
        }
      }
    } catch {
      // backend not available
    }
  }, [ollamaModel, setOllamaModel])

  useEffect(() => {
    void fetchModels()
  }, [fetchModels])

  useEffect(() => {
    let cancelled = false
    const loadTelegram = async () => {
      try {
        const res = await fetch('/admin/settings')
        if (!res.ok) return
        const data = await res.json() as {
          telegram?: {
            enabled?: boolean
            allowed_chat_ids?: number[]
            bot_token_masked?: string | null
            aegis_policy?: string | null
          }
        }
        if (cancelled) return
        const tg = data.telegram ?? {}
        if (typeof tg.enabled === 'boolean') setTelegramEnabled(tg.enabled)
        if (Array.isArray(tg.allowed_chat_ids)) {
          setTelegramChatIds(tg.allowed_chat_ids.join('\n'))
        }
        setTelegramTokenMasked(tg.bot_token_masked ?? null)
        // Never populate the real token into the local store.
        setTelegramBotToken('')
      } catch {
        // backend not available
      }
    }
    void loadTelegram()
    return () => { cancelled = true }
  }, [setTelegramEnabled, setTelegramChatIds, setTelegramBotToken])

  const handleSaveTelegram = async () => {
    setTelegramSaving(true)
    setTelegramStatus('')
    try {
      const chatIds = telegramChatIds
        .split(/[\s,]+/)
        .map((s) => s.trim())
        .filter(Boolean)
        .map((s) => Number(s))
        .filter((n) => Number.isFinite(n) && !Number.isNaN(n))

      const payload: {
        telegram: {
          enabled: boolean
          allowed_chat_ids: number[]
          bot_token?: string
        }
      } = {
        telegram: {
          enabled: telegramEnabled,
          allowed_chat_ids: chatIds,
        },
      }
      if (telegramBotToken.trim()) {
        payload.telegram.bot_token = telegramBotToken.trim()
      }

      const res = await fetch('/admin/settings', {
        method: 'PATCH',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      })
      if (!res.ok) {
        const text = await res.text().catch(() => '')
        setTelegramStatus(`Save failed (${res.status}) ${text}`.trim())
        return
      }
      setTelegramStatus('Saved. Bot restarted.')
      setTelegramBotToken('')
      // Refresh masked token display
      const refreshed = await fetch('/admin/settings')
      if (refreshed.ok) {
        const data = await refreshed.json() as {
          telegram?: { bot_token_masked?: string | null }
        }
        setTelegramTokenMasked(data.telegram?.bot_token_masked ?? null)
      }
    } catch (err) {
      setTelegramStatus(`Save failed: ${err instanceof Error ? err.message : String(err)}`)
    } finally {
      setTelegramSaving(false)
    }
  }

  const handleModelSwitch = async (modelName: string) => {
    setModelLoading(true)
    setModelError('')
    try {
      const res = await fetch('/models/active', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ model: modelName }),
      })
      if (res.ok) {
        const data = await res.json() as { provider: string; model: string }
        setOllamaModel(data.model)
        setActiveModelInfo(prev => prev ? { ...prev, model: data.model } : null)
      } else {
        setModelError(`Failed to switch model (${res.status})`)
      }
    } catch {
      setModelError('Backend unavailable')
    } finally {
      setModelLoading(false)
    }
  }

  return (
    <div className="flex flex-col h-screen bg-background">
      <TopNav />

      <div className="flex flex-col md:flex-row flex-1 overflow-hidden pt-[52px]">
        {/* Settings nav — horizontal scroll strip on mobile, side column on desktop */}
        <aside className="w-full md:w-[220px] shrink-0 border-b md:border-b-0 md:border-r border-outline-variant/20 bg-surface-container-lowest/50 p-2 md:p-4 overflow-x-auto md:overflow-visible">
          <div className="mb-4 hidden md:block">
            <span className="text-[10px] font-label uppercase tracking-[0.2em] text-on-surface-variant/40">
              Configuration
            </span>
          </div>
          <nav className="flex md:flex-col gap-0.5 flex-nowrap">
            {SECTIONS.map((section) => (
              <button
                key={section.id}
                onClick={() => setActiveSection(section.id)}
                className={[
                  'flex items-center gap-2.5 px-3 py-2 rounded text-sm font-body transition-colors text-left shrink-0 whitespace-nowrap',
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
        <div className="flex-1 overflow-y-auto custom-scrollbar px-4 md:px-8 py-6 md:py-8 max-w-2xl">
          {/* Model section */}
          {activeSection === 'model' && (
            <div>
              <SectionTitle>Model Configuration</SectionTitle>

              {/* Active model status card */}
              {activeModelInfo && (
                <div className="mb-6 p-4 bg-surface-container-low rounded-lg border border-outline-variant/20">
                  <div className="flex items-center justify-between mb-2">
                    <FieldLabel>Active Model</FieldLabel>
                    <div className="flex items-center gap-2">
                      {activeModelInfo.gpu_available === true && (
                        <span className="flex items-center gap-1 text-[10px] font-label uppercase tracking-wider px-2 py-0.5 rounded-full bg-green-500/10 text-green-400 border border-green-500/20">
                          <span className="w-1.5 h-1.5 rounded-full bg-green-400" />
                          GPU
                        </span>
                      )}
                      {activeModelInfo.gpu_available === false && (
                        <span className="flex items-center gap-1 text-[10px] font-label uppercase tracking-wider px-2 py-0.5 rounded-full bg-amber-500/10 text-amber-400 border border-amber-500/20">
                          <span className="w-1.5 h-1.5 rounded-full bg-amber-400" />
                          CPU
                        </span>
                      )}
                      <span className="text-[10px] font-label uppercase tracking-wider px-2 py-0.5 rounded-full bg-surface-container-high text-on-surface-variant/60 border border-outline-variant/20">
                        {activeModelInfo.provider}
                      </span>
                    </div>
                  </div>
                  <p className="text-sm font-body font-medium" style={{ color: '#00d4ff' }}>
                    {activeModelInfo.model}
                  </p>
                  {activeModelInfo.gpu_available === false && (
                    <p className="mt-2 text-xs font-body text-amber-400/80">
                      Running on CPU. Recreate the Ollama container to restore GPU access:
                      <code className="ml-1 text-[11px] bg-surface-container-high px-1.5 py-0.5 rounded">
                        docker compose up -d --force-recreate ollama
                      </code>
                    </p>
                  )}
                </div>
              )}

              {/* Provider toggle */}
              <div className="mb-6">
                <FieldLabel>Provider</FieldLabel>
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
                      <span className="text-sm font-body text-on-surface">
                        {env === 'dev' ? 'Claude (API)' : 'Ollama (Local)'}
                      </span>
                    </label>
                  ))}
                </div>
              </div>

              {/* Ollama model picker */}
              <div className="mb-4">
                <div className="flex items-center justify-between mb-2">
                  <FieldLabel>Available Ollama Models</FieldLabel>
                  <div className="flex items-center gap-3">
                    <button
                      onClick={() => void handleRunBenchmarks()}
                      disabled={benchStarting || benchmarks?.status.running}
                      className="text-[10px] font-label uppercase tracking-wider text-on-surface-variant/60 hover:text-on-surface transition-colors flex items-center gap-1 disabled:opacity-40"
                    >
                      <span className="material-symbols-outlined" style={{ fontSize: 12 }}>speed</span>
                      {benchmarks?.status.running
                        ? `Benchmarking ${benchmarks.status.current ?? '...'}`
                        : 'Run Benchmarks'}
                    </button>
                    <button
                      onClick={() => void fetchModels()}
                      className="text-[10px] font-label uppercase tracking-wider text-on-surface-variant/60 hover:text-on-surface transition-colors flex items-center gap-1"
                    >
                      <span className="material-symbols-outlined" style={{ fontSize: 12 }}>refresh</span>
                      Refresh
                    </button>
                  </div>
                </div>

                {modelError && (
                  <p className="text-xs font-body text-red-400 mb-2">{modelError}</p>
                )}

                {availableModels.length === 0 ? (
                  <div className="p-4 bg-surface-container/40 rounded border border-outline-variant/10 text-center">
                    <p className="text-sm font-body text-on-surface-variant/60">
                      No models found. Pull models with:
                    </p>
                    <code className="text-xs text-on-surface-variant/80 mt-1 block">
                      docker compose exec ollama ollama pull llama3.1:8b-instruct-q4_K_M
                    </code>
                  </div>
                ) : (
                  <div className="flex flex-col gap-1.5">
                    {availableModels.map((m) => {
                      const isActive = activeModelInfo?.model === m.name
                      return (
                        <button
                          key={m.name}
                          onClick={() => void handleModelSwitch(m.name)}
                          disabled={modelLoading || isActive}
                          className={[
                            'flex items-center justify-between p-3 rounded-lg border transition-all text-left',
                            isActive
                              ? 'bg-primary-container/10 border-primary-container/30'
                              : 'bg-surface-container-low/50 border-outline-variant/15 hover:border-outline-variant/40 hover:bg-surface-container-low',
                            modelLoading ? 'opacity-60 cursor-wait' : '',
                          ].join(' ')}
                        >
                          <div className="flex-1 min-w-0">
                            <div className="flex items-center gap-2">
                              {isActive && (
                                <span className="w-2 h-2 rounded-full shrink-0" style={{ backgroundColor: '#00d4ff' }} />
                              )}
                              <span className={[
                                'text-sm font-body truncate',
                                isActive ? 'font-medium' : 'text-on-surface',
                              ].join(' ')}
                                style={isActive ? { color: '#00d4ff' } : undefined}
                              >
                                {m.name}
                              </span>
                            </div>
                            <div className="flex items-center gap-3 mt-1 ml-4">
                              {m.parameter_size && (
                                <span className="text-[10px] font-label text-on-surface-variant/50">
                                  {m.parameter_size}
                                </span>
                              )}
                              {m.quantization_level && (
                                <span className="text-[10px] font-label text-on-surface-variant/50">
                                  {m.quantization_level}
                                </span>
                              )}
                              {m.family && (
                                <span className="text-[10px] font-label text-on-surface-variant/40">
                                  {m.family}
                                </span>
                              )}
                              {m.size != null && (
                                <span className="text-[10px] font-label text-on-surface-variant/40">
                                  {formatBytes(m.size)}
                                </span>
                              )}
                              {(() => {
                                const b = benchmarks?.results[m.name]
                                if (!b) return null
                                if (b.error) {
                                  return (
                                    <span className="text-[10px] font-label text-red-400/80" title={b.error}>
                                      bench failed
                                    </span>
                                  )
                                }
                                return (
                                  <span
                                    className="text-[10px] font-label"
                                    style={{ color: '#00d4ff' }}
                                    title={`TTFT ${b.ttft_ms ?? '?'} ms · prompt-eval ${b.prompt_eval_tps} tok/s`}
                                  >
                                    {b.tokens_per_second.toFixed(1)} tok/s
                                  </span>
                                )
                              })()}
                              {benchmarks?.status.running && benchmarks.status.current === m.name && (
                                <span className="text-[10px] font-label text-amber-400/80">
                                  benchmarking…
                                </span>
                              )}
                            </div>
                          </div>
                          {isActive && (
                            <span className="text-[10px] font-label uppercase tracking-wider px-2 py-0.5 rounded-full shrink-0 ml-2"
                              style={{ backgroundColor: 'rgba(0,212,255,0.1)', color: '#00d4ff', border: '1px solid rgba(0,212,255,0.2)' }}
                            >
                              Active
                            </span>
                          )}
                        </button>
                      )
                    })}
                  </div>
                )}
              </div>

              <div className="mt-4 p-3 bg-surface-container/30 rounded border border-outline-variant/10">
                <p className="text-[10px] font-label uppercase tracking-widest text-on-surface-variant/40 mb-1">
                  Pull new models
                </p>
                <code className="text-xs font-body text-on-surface-variant/70 block">
                  docker compose exec ollama ollama pull &lt;model:tag&gt;
                </code>
              </div>
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
                  placeholder={telegramTokenMasked ? `Saved: ${telegramTokenMasked} — leave blank to keep` : '••••••••••••••••••••••'}
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
                  One Telegram chat ID per line. Empty means allow all.
                </p>
              </div>

              <div className="flex items-center gap-3">
                <button
                  type="button"
                  onClick={handleSaveTelegram}
                  disabled={telegramSaving}
                  className="px-4 py-2 rounded text-sm font-body bg-primary-container text-on-primary-container hover:opacity-90 disabled:opacity-40 transition-opacity"
                >
                  {telegramSaving ? 'Saving…' : 'Save & Restart Bot'}
                </button>
                {telegramStatus && (
                  <span className="text-xs font-body text-on-surface-variant/70">{telegramStatus}</span>
                )}
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

              {activeModelInfo && (
                <div className="p-3 bg-surface-container-low rounded border border-outline-variant/20">
                  <FieldLabel>Current Model</FieldLabel>
                  <p className="text-sm font-body text-on-surface">{activeModelInfo.model}</p>
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
