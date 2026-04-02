// zeus/frontend/src/components/orb/AudioBars.tsx
import { useMemo } from 'react'

interface AudioBarsProps {
  level: number
  barCount?: number
  height?: number
}

const RANDOM_FACTORS = [0.6, 0.8, 1.0, 0.9, 0.7, 1.0, 0.85, 0.95, 0.75, 1.0, 0.8, 0.65, 0.9, 0.7, 0.85]

export function AudioBars({ level, barCount = 15, height = 32 }: AudioBarsProps) {
  const factors = useMemo(() => RANDOM_FACTORS.slice(0, barCount), [barCount])
  const isActive = level > 0.05

  return (
    <div
      className="flex items-end gap-[2px]"
      style={{ height }}
    >
      {factors.map((factor, i) => {
        const barHeight = Math.max(0.1, level * factor)
        const delay = `${(i * 80) % 400}ms`

        return (
          <div
            key={i}
            className="flex-1 rounded-sm transition-all duration-100"
            style={{
              height: `${barHeight * 100}%`,
              minHeight: 2,
              backgroundColor: `rgba(0, 212, 255, ${isActive ? 0.4 + barHeight * 0.6 : 0.2})`,
              animation: isActive ? `bar-bounce ${400 + i * 30}ms ease-in-out ${delay} infinite` : 'none',
              transformOrigin: 'bottom',
            }}
          />
        )
      })}
    </div>
  )
}
