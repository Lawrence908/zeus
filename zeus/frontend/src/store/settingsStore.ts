// zeus/frontend/src/store/settingsStore.ts
import { create } from 'zustand'
import { persist } from 'zustand/middleware'

interface SettingsStore {
  theme: 'dark' | 'light'
  modelEnv: 'dev' | 'prod'
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
    }
  )
)
