// zeus/frontend/src/components/orb/PhaosOrb.tsx
// NOTE: CSS placeholder for the Phaos Orb visualization.
// The Three.js/R3F version (LAB-288) will replace this component later.

import { useVoiceStore, type VoiceState } from '../../store/voiceStore'
import { AudioBars } from './AudioBars'

interface PhaosOrbProps {
  size?: 'compact' | 'fullscreen'
}

function getOrbStyles(state: VoiceState): {
  core: string
  ring: string
  glow: string
} {
  switch (state) {
    case 'listening':
      return {
        core: 'from-primary/60 via-primary-container/80 to-accent/40',
        ring: 'border-primary-container/60',
        glow: '0 0 60px rgba(0, 212, 255, 0.5), 0 0 120px rgba(0, 212, 255, 0.2)',
      }
    case 'processing':
      return {
        core: 'from-secondary/60 via-secondary-container/60 to-primary/30',
        ring: 'border-secondary/50',
        glow: '0 0 60px rgba(96, 1, 209, 0.5), 0 0 120px rgba(0, 212, 255, 0.15)',
      }
    case 'speaking':
      return {
        core: 'from-primary/50 via-primary-container/70 to-accent/50',
        ring: 'border-primary/60',
        glow: '0 0 50px rgba(0, 212, 255, 0.4), 0 0 100px rgba(0, 212, 255, 0.15)',
      }
    case 'wake_detected':
      return {
        core: 'from-tertiary/40 via-primary-container/50 to-accent/30',
        ring: 'border-tertiary/40',
        glow: '0 0 40px rgba(167, 194, 255, 0.3), 0 0 80px rgba(0, 212, 255, 0.1)',
      }
    default:
      return {
        core: 'from-surface-container/60 via-primary/20 to-surface-container-high/40',
        ring: 'border-outline-variant/30',
        glow: '0 0 30px rgba(0, 212, 255, 0.15), 0 0 60px rgba(0, 212, 255, 0.05)',
      }
  }
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

function getAnimationClass(state: VoiceState): string {
  switch (state) {
    case 'listening': return 'animate-pulse-cyan'
    case 'processing': return 'pulsar'
    default: return ''
  }
}

export function PhaosOrb({ size = 'compact' }: PhaosOrbProps) {
  const { state, level } = useVoiceStore()
  const styles = getOrbStyles(state)
  const label = getStateLabel(state)
  const animClass = getAnimationClass(state)

  const isCompact = size === 'compact'
  const orbSize = isCompact ? 160 : 400
  const ringSize = isCompact ? 140 : 360
  const innerRingSize = isCompact ? 116 : 300
  const coreSize = isCompact ? 88 : 220

  return (
    <div className={`flex flex-col items-center gap-${isCompact ? '3' : '6'}`}>
      {/* Ghost text label (fullscreen only) */}
      {!isCompact && (
        <div
          className="absolute text-[10vw] font-headline font-black tracking-[0.2em] uppercase pointer-events-none select-none"
          style={{ color: 'rgba(226, 226, 235, 0.04)' }}
        >
          {label}
        </div>
      )}

      {/* Orb container */}
      <div
        className="relative flex items-center justify-center"
        style={{ width: orbSize, height: orbSize }}
      >
        {/* Outer spinning ring */}
        <div
          className={`absolute rounded-full border ${styles.ring} border-dashed orb-ring-slow`}
          style={{
            width: ringSize,
            height: ringSize,
            borderWidth: isCompact ? 1 : 2,
          }}
        />

        {/* Inner counter-spinning ring */}
        <div
          className={`absolute rounded-full border border-outline-variant/20 orb-ring-reverse`}
          style={{
            width: innerRingSize,
            height: innerRingSize,
            borderWidth: isCompact ? 1 : 2,
            borderStyle: 'dotted',
          }}
        />

        {/* Core sphere */}
        <div
          className={`relative rounded-full bg-gradient-to-br ${styles.core} flex items-center justify-center transition-all duration-500 ${animClass}`}
          style={{
            width: coreSize,
            height: coreSize,
            boxShadow: styles.glow,
          }}
        >
          {/* Inner highlight */}
          <div
            className="absolute rounded-full bg-white/5"
            style={{
              width: coreSize * 0.4,
              height: coreSize * 0.4,
              top: coreSize * 0.1,
              left: coreSize * 0.15,
            }}
          />
          {/* Zeus lightning mark */}
          <span
            className="font-headline font-bold select-none"
            style={{
              fontSize: isCompact ? 24 : 56,
              color: 'rgba(0, 212, 255, 0.8)',
              textShadow: '0 0 20px rgba(0, 212, 255, 0.6)',
            }}
          >
            ⚡
          </span>
        </div>
      </div>

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
