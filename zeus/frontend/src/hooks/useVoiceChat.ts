// zeus/frontend/src/hooks/useVoiceChat.ts — Push-to-talk → /voice/interact → chat transcript
import { useRef, useState, useCallback, useEffect } from 'react'
import { useChatStore } from '../store/chatStore'
import { useVoiceStore } from '../store/voiceStore'
import { useSettingsStore } from '../store/settingsStore'
import { mediaBlobToWav16kMono, pickMediaRecorderMime } from '../utils/audioWav'

function generateId(): string {
  return `msg-${Date.now()}-${Math.random().toString(36).slice(2, 9)}`
}

function speakBrowserTts(text: string) {
  if (typeof window === 'undefined' || !window.speechSynthesis) return
  const t = text.trim()
  if (!t) return
  window.speechSynthesis.cancel()
  const u = new SpeechSynthesisUtterance(t)
  u.rate = 1
  window.speechSynthesis.speak(u)
}

export interface UseVoiceChatOptions {
  /** e.g. refresh session list after a voice turn */
  onTurnComplete?: () => void | Promise<void>
}

export function useVoiceChat(opts?: UseVoiceChatOptions) {
  const isStreaming = useChatStore((s) => s.isStreaming)
  const addMessage = useChatStore((s) => s.addMessage)
  const setActiveSession = useChatStore((s) => s.setActiveSession)
  const setVoiceUiState = useVoiceStore((s) => s.setState)
  const voiceReplyEnabled = useSettingsStore((s) => s.voiceReplyEnabled)

  const [isRecording, setIsRecording] = useState(false)
  const [isVoiceSending, setIsVoiceSending] = useState(false)
  const mediaRecorderRef = useRef<MediaRecorder | null>(null)
  const chunksRef = useRef<Blob[]>([])
  const streamRef = useRef<MediaStream | null>(null)

  useEffect(() => {
    return () => {
      const mr = mediaRecorderRef.current
      if (mr && mr.state !== 'inactive') {
        mr.onstop = null
        mr.stop()
      }
      streamRef.current?.getTracks().forEach((t) => t.stop())
    }
  }, [])

  const releaseStream = useCallback(() => {
    streamRef.current?.getTracks().forEach((t) => t.stop())
    streamRef.current = null
    mediaRecorderRef.current = null
  }, [])

  /** Toggle: start recording if idle; stop and send if recording. */
  const toggleRecording = useCallback(async () => {
    if (isStreaming || isVoiceSending) return

    if (isRecording && mediaRecorderRef.current) {
      const mr = mediaRecorderRef.current
      await new Promise<void>((resolve) => {
        mr.onstop = () => resolve()
        mr.stop()
      })
      const chunks = chunksRef.current.slice()
      chunksRef.current = []
      releaseStream()
      setIsRecording(false)
      setVoiceUiState('processing')

      const mime = chunks[0]?.type || 'audio/webm'
      const blob = new Blob(chunks, { type: mime })
      if (blob.size < 256) {
        setVoiceUiState('idle')
        addMessage({
          id: generateId(),
          role: 'assistant',
          content: '_Recording too short — hold the mic a little longer._',
          timestamp: Date.now(),
          source: 'web',
        })
        return
      }

      let wavBytes: Uint8Array
      try {
        wavBytes = await mediaBlobToWav16kMono(blob)
      } catch {
        setVoiceUiState('idle')
        addMessage({
          id: generateId(),
          role: 'assistant',
          content: '_Could not decode audio. Try again or use another browser._',
          timestamp: Date.now(),
          source: 'web',
        })
        return
      }

      const sessionId = useChatStore.getState().activeSessionId
      const form = new FormData()
      form.append('audio', new Blob([wavBytes], { type: 'audio/wav' }), 'voice.wav')
      if (sessionId) form.append('session_id', sessionId)
      form.append('use_context', 'true')
      form.append('max_tokens', '512')

      setIsVoiceSending(true)
      try {
        const res = await fetch('/voice/interact', { method: 'POST', body: form })
        const raw = (await res.json().catch(() => ({}))) as Record<string, unknown>

        if (!res.ok) {
          const d = raw.detail
          const detail =
            typeof d === 'string'
              ? d
              : Array.isArray(d)
                ? d.map((x) => (typeof x === 'object' && x && 'msg' in x ? String((x as { msg: string }).msg) : JSON.stringify(x))).join('; ')
                : `HTTP ${res.status}`
          addMessage({
            id: generateId(),
            role: 'assistant',
            content: `_${detail}_`,
            timestamp: Date.now(),
            source: 'web',
          })
          return
        }

        const transcript = String(raw.transcript ?? '').trim()
        const reply = String(raw.assistant_message ?? '').trim()
        if (typeof raw.session_id === 'string') {
          setActiveSession(raw.session_id)
        }

        if (transcript) {
          addMessage({
            id: generateId(),
            role: 'user',
            content: transcript,
            timestamp: Date.now(),
            source: 'voice',
          })
        }
        addMessage({
          id: generateId(),
          role: 'assistant',
          content: reply || '_(empty reply)_',
          timestamp: Date.now(),
          source: 'voice',
          context_sources: Array.isArray(raw.context_sources)
            ? (raw.context_sources as string[])
            : undefined,
          model_used: typeof raw.model_used === 'string' ? raw.model_used : undefined,
        })

        if (voiceReplyEnabled && reply) {
          speakBrowserTts(reply)
        }
        void Promise.resolve(opts?.onTurnComplete?.())
      } catch {
        addMessage({
          id: generateId(),
          role: 'assistant',
          content: '_Voice request failed — is Zeus Core running?_',
          timestamp: Date.now(),
          source: 'web',
        })
      } finally {
        setIsVoiceSending(false)
        setVoiceUiState('idle')
      }
      return
    }

    // Start recording
    if (!navigator.mediaDevices?.getUserMedia) {
      addMessage({
        id: generateId(),
        role: 'assistant',
        content: '_Microphone not available in this context (HTTPS required on some browsers)._',
        timestamp: Date.now(),
        source: 'web',
      })
      return
    }

    try {
      const stream = await navigator.mediaDevices.getUserMedia({
        audio: {
          echoCancellation: true,
          noiseSuppression: true,
        },
      })
      streamRef.current = stream
      chunksRef.current = []

      const mime = pickMediaRecorderMime()
      const mr = mime ? new MediaRecorder(stream, { mimeType: mime }) : new MediaRecorder(stream)
      mr.ondataavailable = (e) => {
        if (e.data.size > 0) chunksRef.current.push(e.data)
      }
      mr.start(250)
      mediaRecorderRef.current = mr
      setIsRecording(true)
      setVoiceUiState('listening')
    } catch (e) {
      const msg = e instanceof Error ? e.message : String(e)
      addMessage({
        id: generateId(),
        role: 'assistant',
        content: `_Mic permission or device error: ${msg}_`,
        timestamp: Date.now(),
        source: 'web',
      })
    }
  }, [
    isStreaming,
    isVoiceSending,
    isRecording,
    addMessage,
    setActiveSession,
    setVoiceUiState,
    releaseStream,
    voiceReplyEnabled,
    opts?.onTurnComplete,
  ])

  return {
    isRecording,
    isVoiceSending,
    toggleRecording,
    /** Stop without sending (e.g. unmount) */
    cancelRecording: useCallback(() => {
      if (!isRecording || !mediaRecorderRef.current) return
      mediaRecorderRef.current.onstop = null
      mediaRecorderRef.current.stop()
      chunksRef.current = []
      releaseStream()
      setIsRecording(false)
      setVoiceUiState('idle')
    }, [isRecording, releaseStream, setVoiceUiState]),
  }
}
