// zeus/frontend/src/store/settingsStore.ts
import { create } from 'zustand'
import { persist } from 'zustand/middleware'

export interface OllamaModelInfo {
  name: string
  size: number | null
  parameter_size: string | null
  quantization_level: string | null
  modified_at: string | null
  family: string | null
}

interface SettingsStore {
  theme: 'dark' | 'light'
  modelEnv: 'dev' | 'prod'
  /** Currently selected Ollama model (synced with backend via POST /models/active). */
  ollamaModel: string
  aegisEnabled: boolean
  activePolicy: string
  telegramEnabled: boolean
  telegramBotToken: string
  telegramChatIds: string
  autoSummarize: boolean
  sessionWindowSize: number
  /** Browser SpeechSynthesis for assistant replies after voice turns (until LuxTTS/Voicebox). */
  voiceReplyEnabled: boolean
  setTheme: (t: 'dark' | 'light') => void
  setModelEnv: (e: 'dev' | 'prod') => void
  setOllamaModel: (m: string) => void
  setAegisEnabled: (v: boolean) => void
  setActivePolicy: (p: string) => void
  setTelegramEnabled: (v: boolean) => void
  setTelegramBotToken: (t: string) => void
  setTelegramChatIds: (ids: string) => void
  setAutoSummarize: (v: boolean) => void
  setSessionWindowSize: (n: number) => void
  setVoiceReplyEnabled: (v: boolean) => void
}

export const useSettingsStore = create<SettingsStore>()(
  persist(
    (set) => ({
      theme: 'dark',
      modelEnv: 'dev',
      ollamaModel: '',
      aegisEnabled: true,
      activePolicy: 'default',
      telegramEnabled: false,
      telegramBotToken: '',
      telegramChatIds: '',
      autoSummarize: true,
      sessionWindowSize: 16,
      voiceReplyEnabled: false,
      setTheme: (theme) => set({ theme }),
      setModelEnv: (modelEnv) => set({ modelEnv }),
      setOllamaModel: (ollamaModel) => set({ ollamaModel }),
      setAegisEnabled: (aegisEnabled) => set({ aegisEnabled }),
      setActivePolicy: (activePolicy) => set({ activePolicy }),
      setTelegramEnabled: (telegramEnabled) => set({ telegramEnabled }),
      setTelegramBotToken: (telegramBotToken) => set({ telegramBotToken }),
      setTelegramChatIds: (telegramChatIds) => set({ telegramChatIds }),
      setAutoSummarize: (autoSummarize) => set({ autoSummarize }),
      setSessionWindowSize: (sessionWindowSize) => set({ sessionWindowSize }),
      setVoiceReplyEnabled: (voiceReplyEnabled) => set({ voiceReplyEnabled }),
    }),
    {
      name: 'zeus-settings',
      partialize: (state) => {
        const { telegramBotToken: _, ...rest } = state
        return rest
      },
    }
  )
)
