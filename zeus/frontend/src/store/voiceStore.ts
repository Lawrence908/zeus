// zeus/frontend/src/store/voiceStore.ts
import { create } from 'zustand'

export type VoiceState = 'idle' | 'wake_detected' | 'listening' | 'processing' | 'speaking'

interface VoiceStore {
  state: VoiceState
  level: number
  connected: boolean
  setState: (s: VoiceState) => void
  setLevel: (l: number) => void
  setConnected: (c: boolean) => void
}

export const useVoiceStore = create<VoiceStore>((set) => ({
  state: 'idle',
  level: 0,
  connected: false,
  setState: (s) => set({ state: s }),
  setLevel: (l) => set({ level: l }),
  setConnected: (c) => set({ connected: c }),
}))
