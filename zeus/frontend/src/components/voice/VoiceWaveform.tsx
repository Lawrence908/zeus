// zeus/frontend/src/components/voice/VoiceWaveform.tsx
import { useRef, useCallback } from 'react'
import { useVoiceStore, type VoiceState } from '../../store/voiceStore'
import { useAnimationFrame } from '../../hooks/useAnimationFrame'

interface VoiceWaveformProps {
  size?: 'compact' | 'fullscreen'
  className?: string
}

// Bell-curve factors: center bars taller, edges shorter
const FACTORS_5 = [0.55, 0.8, 1.0, 0.8, 0.55]
const FACTORS_7 = [0.45, 0.65, 0.85, 1.0, 0.85, 0.65, 0.45]

function getBarColor(state: VoiceState): string {
  switch (state) {
    case 'idle':
      return 'rgba(133, 147, 152, 0.35)'
    case 'wake_detected':
    case 'listening':
      return '#00d4ff'
    case 'processing':
      return '#a57aff'
    case 'speaking':
      return '#ff9966'
  }
}

function computeTargets(
  state: VoiceState,
  level: number,
  time: number,
  factors: number[],
): number[] {
  const count = factors.length
  switch (state) {
    case 'idle':
      return factors.map((_, i) =>
        Math.sin(time * 0.8 + i * 0.7) * 0.10 + 0.18
      )
    case 'wake_detected':
      return factors.map((f) => 0.35 + f * 0.1)
    case 'listening':
      return factors.map((f) =>
        Math.max(0.15, level * f + Math.sin(time * 4 + f * 3) * 0.04)
      )
    case 'processing':
      return factors.map((_, i) =>
        0.25 + 0.45 * Math.abs(Math.sin(time * 2.5 - i * (Math.PI / count)))
      )
    case 'speaking':
      return factors.map((f) =>
        Math.max(0.15, level * f + Math.sin(time * 3 + f * 2) * 0.03)
      )
  }
}

export function VoiceWaveform({ size = 'compact', className = '' }: VoiceWaveformProps) {
  const isCompact = size === 'compact'
  const barCount = isCompact ? 5 : 7
  const factors = isCompact ? FACTORS_5 : FACTORS_7
  const maxHeight = isCompact ? 40 : 96
  const barWidth = isCompact ? 4 : 6
  const gap = isCompact ? 3 : 4

  const barRefs = useRef<(HTMLDivElement | null)[]>([])
  const currentHeights = useRef<number[]>(new Array(barCount).fill(0.18))

  const animate = useCallback((time: number) => {
    const state = useVoiceStore.getState().state
    const level = useVoiceStore.getState().level

    const targets = computeTargets(state, level, time, factors)
    const smoothing = state === 'speaking' ? 0.08 : 0.15

    for (let i = 0; i < barCount; i++) {
      const current = currentHeights.current[i]
      const next = current + (targets[i] - current) * smoothing
      currentHeights.current[i] = next

      const el = barRefs.current[i]
      if (el) {
        el.style.height = `${Math.max(0.15, next) * 100}%`
        el.style.backgroundColor = getBarColor(state)
      }
    }
  }, [barCount, factors])

  useAnimationFrame(animate)

  const totalWidth = barCount * barWidth + (barCount - 1) * gap

  return (
    <div
      className={`flex items-center justify-center ${className}`}
      style={{ height: maxHeight, width: totalWidth }}
    >
      <div className="flex items-center h-full" style={{ gap }}>
        {Array.from({ length: barCount }, (_, i) => (
          <div
            key={i}
            ref={(el) => { barRefs.current[i] = el }}
            className="rounded-full"
            style={{
              width: barWidth,
              height: '18%',
              backgroundColor: 'rgba(133, 147, 152, 0.35)',
              transition: 'background-color 300ms ease',
              willChange: 'height',
            }}
          />
        ))}
      </div>
    </div>
  )
}
