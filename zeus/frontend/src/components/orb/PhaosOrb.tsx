// zeus/frontend/src/components/orb/PhaosOrb.tsx
// Unified Phaos Orb component — renders the R3F 3D orb (LAB-288).
// Supports compact (sidebar panel) and fullscreen (/viz route) modes.

import { useVoiceStore, type VoiceState } from '../../store/voiceStore'
import { AudioBars } from './AudioBars'
import { PhaosOrb3D } from './PhaosOrb3D'

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

export function PhaosOrb({ size = 'compact' }: PhaosOrbProps) {
  const { state, level } = useVoiceStore()
  const label = getStateLabel(state)

  const isCompact = size === 'compact'

  return (
    <div className={`flex flex-col items-center ${isCompact ? 'gap-3' : 'gap-6'}`}>
      {/* Ghost text label (fullscreen only) */}
      {!isCompact && (
        <div
          className="absolute text-[10vw] font-headline font-black tracking-[0.2em] uppercase pointer-events-none select-none"
          style={{ color: 'rgba(226, 226, 235, 0.04)' }}
        >
          {label}
        </div>
      )}

      {/* 3D Orb canvas */}
      <PhaosOrb3D
        className="relative"
        style={{
          width: isCompact ? 160 : 400,
          height: isCompact ? 160 : 400,
        }}
      />

      {/* State label */}
      <div className="flex flex-col items-center gap-1">
        <span
          className="font-label text-xs tracking-[0.2em] uppercase font-medium"
          style={{ color: state === 'idle' ? '#859398' : '#00d4ff' }}
        >
          {label}
        </span>

        {/* Audio bars */}
        <AudioBars
          level={level}
          barCount={isCompact ? 15 : 24}
          height={isCompact ? 24 : 48}
        />
      </div>
    </div>
  )
}
