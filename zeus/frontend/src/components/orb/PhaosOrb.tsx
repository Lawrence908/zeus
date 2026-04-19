// zeus/frontend/src/components/orb/PhaosOrb.tsx
// Voice state indicator — renders waveform bars + state label.
// Supports compact (sidebar panel) and fullscreen (/viz route) modes.

import { useVoiceStore, type VoiceState } from '../../store/voiceStore'
import { VoiceWaveform } from '../voice/VoiceWaveform'

interface PhaosOrbProps {
  size?: 'compact' | 'fullscreen'
}

function getStateLabel(state: VoiceState): string {
  switch (state) {
    case 'listening': return 'LISTENING'
    case 'processing': return 'PROCESSING'
    case 'speaking': return 'SPEAKING'
    case 'wake_detected': return 'WAKE DETECTED'
    default: return 'IDLE'
  }
}

function getStateColor(state: VoiceState): string {
  switch (state) {
    case 'idle': return '#859398'
    case 'wake_detected':
    case 'listening': return '#00d4ff'
    case 'processing': return '#a57aff'
    case 'speaking': return '#ff9966'
  }
}

export function PhaosOrb({ size = 'compact' }: PhaosOrbProps) {
  const { state } = useVoiceStore()
  const isCompact = size === 'compact'

  return (
    <div className={`flex flex-col items-center ${isCompact ? 'gap-3' : 'gap-5'}`}>
      <VoiceWaveform size={size} />
      <span
        className="font-label text-xs tracking-[0.2em] uppercase font-medium"
        style={{ color: getStateColor(state) }}
      >
        {getStateLabel(state)}
      </span>
    </div>
  )
}
