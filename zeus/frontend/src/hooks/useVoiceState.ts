// zeus/frontend/src/hooks/useVoiceState.ts
import { useEffect, useRef } from 'react'
import { useVoiceStore, type VoiceState } from '../store/voiceStore'

const MIN_BACKOFF = 1000
const MAX_BACKOFF = 30000

export function useVoiceState() {
  const { state, level, connected, setState, setLevel, setConnected } = useVoiceStore()
  const wsRef = useRef<WebSocket | null>(null)
  const backoffRef = useRef(MIN_BACKOFF)
  const timerRef = useRef<ReturnType<typeof setTimeout> | null>(null)
  const unmountedRef = useRef(false)

  useEffect(() => {
    unmountedRef.current = false

    function connect() {
      if (unmountedRef.current) return

      const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:'
      const ws = new WebSocket(`${protocol}//${window.location.host}/ws/voice-state`)
      wsRef.current = ws

      ws.onopen = () => {
        if (unmountedRef.current) { ws.close(); return }
        backoffRef.current = MIN_BACKOFF
        setConnected(true)
      }

      ws.onmessage = (event: MessageEvent) => {
        try {
          const data = JSON.parse(event.data as string) as { state?: VoiceState; level?: number }
          if (data.state) setState(data.state)
          if (typeof data.level === 'number') setLevel(data.level)
        } catch {
          // malformed frame — ignore
        }
      }

      ws.onclose = () => {
        if (unmountedRef.current) return
        setConnected(false)
        // exponential backoff reconnect
        timerRef.current = setTimeout(() => {
          backoffRef.current = Math.min(backoffRef.current * 2, MAX_BACKOFF)
          connect()
        }, backoffRef.current)
      }

      ws.onerror = () => {
        ws.close()
      }
    }

    connect()

    return () => {
      unmountedRef.current = true
      if (timerRef.current) clearTimeout(timerRef.current)
      wsRef.current?.close()
    }
  }, [setState, setLevel, setConnected])

  return { state, level, connected }
}
