// zeus/frontend/src/hooks/useAnimationFrame.ts
import { useEffect, useRef } from 'react'

export function useAnimationFrame(callback: (time: number, delta: number) => void) {
  const callbackRef = useRef(callback)
  callbackRef.current = callback

  useEffect(() => {
    let rafId: number
    let prev = performance.now()

    const loop = (now: number) => {
      const delta = (now - prev) / 1000
      prev = now
      callbackRef.current(now / 1000, delta)
      rafId = requestAnimationFrame(loop)
    }

    rafId = requestAnimationFrame(loop)
    return () => cancelAnimationFrame(rafId)
  }, [])
}
