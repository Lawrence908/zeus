// src/lib/api/voice.ts — WebSocket + REST client for the voice pipeline.
//
// - subscribeVoiceState: connects to /ws/voice-state with exponential backoff,
//   invokes callback with {state, level} frames.
// - voiceInteract: POSTs 16 kHz mono WAV to /voice/interact and returns the
//   transcript + assistant reply + metadata.
// - synthesize: optional GET /voice/tts?text=... proxy to Voicebox. Returns
//   WAV bytes when the endpoint is enabled server-side; caller can fall back
//   to the browser Web Speech API when the request 404s.
import type { VoiceStateName } from '$lib/voice/orb';
import { API_BASE, wsUrl } from './base';

export interface VoiceStateFrame {
  type?: string;
  state?: VoiceStateName;
  audio_level?: number;
  timestamp_ms?: number;
  metadata?: Record<string, unknown>;
}

export interface VoiceStateCallbacks {
  onFrame: (frame: VoiceStateFrame) => void;
  onOpen?: () => void;
  onClose?: () => void;
}

const MIN_BACKOFF_MS = 1000;
const MAX_BACKOFF_MS = 30000;

export function subscribeVoiceState(cbs: VoiceStateCallbacks): () => void {
  let ws: WebSocket | null = null;
  let closed = false;
  let backoff = MIN_BACKOFF_MS;
  let timer: ReturnType<typeof setTimeout> | null = null;

  function connect() {
    if (closed) return;
    try {
      ws = new WebSocket(wsUrl('/ws/voice-state'));
    } catch {
      scheduleReconnect();
      return;
    }
    ws.onopen = () => {
      backoff = MIN_BACKOFF_MS;
      cbs.onOpen?.();
    };
    ws.onmessage = (ev) => {
      try {
        const frame = JSON.parse(ev.data as string) as VoiceStateFrame;
        cbs.onFrame(frame);
      } catch {
        /* ignore malformed frames */
      }
    };
    ws.onclose = () => {
      cbs.onClose?.();
      scheduleReconnect();
    };
    ws.onerror = () => {
      ws?.close();
    };
  }

  function scheduleReconnect() {
    if (closed) return;
    timer = setTimeout(() => {
      backoff = Math.min(backoff * 2, MAX_BACKOFF_MS);
      connect();
    }, backoff);
  }

  connect();

  return () => {
    closed = true;
    if (timer) clearTimeout(timer);
    ws?.close();
  };
}

export interface VoiceInteractResult {
  transcript: string;
  session_id?: string;
  assistant_message: string;
  model_used?: string;
  latency_ms?: number;
  context_sources?: string[];
  topic?: string;
  aegis_flags?: string[];
}

export async function voiceInteract(
  wavBytes: Uint8Array,
  sessionId?: string,
  opts: { use_context?: boolean; max_tokens?: number } = {}
): Promise<VoiceInteractResult> {
  const form = new FormData();
  const blobPart = new Uint8Array(wavBytes);
  form.append('audio', new Blob([blobPart.buffer], { type: 'audio/wav' }), 'voice.wav');
  if (sessionId) form.append('session_id', sessionId);
  form.append('use_context', opts.use_context === false ? 'false' : 'true');
  form.append('max_tokens', String(opts.max_tokens ?? 512));
  const res = await fetch(API_BASE + '/voice/interact', { method: 'POST', body: form });
  const raw = (await res.json().catch(() => ({}))) as Record<string, unknown>;
  if (!res.ok) {
    const d = raw.detail;
    const detail = typeof d === 'string' ? d : `HTTP ${res.status}`;
    throw new Error(detail);
  }
  return {
    transcript: String(raw.transcript ?? '').trim(),
    session_id: typeof raw.session_id === 'string' ? raw.session_id : undefined,
    assistant_message: String(raw.assistant_message ?? '').trim(),
    model_used: typeof raw.model_used === 'string' ? raw.model_used : undefined,
    latency_ms: typeof raw.latency_ms === 'number' ? raw.latency_ms : undefined,
    context_sources: Array.isArray(raw.context_sources) ? (raw.context_sources as string[]) : undefined,
    topic: typeof raw.topic === 'string' ? raw.topic : undefined,
    aegis_flags: Array.isArray(raw.aegis_flags) ? (raw.aegis_flags as string[]) : undefined
  };
}

export interface VoiceStreamCallbacks {
  onTranscript?: (text: string) => void;
  onToken?: (text: string) => void;
  /** One self-contained WAV per sentence, in order. Play back-to-back. */
  onAudio?: (seq: number, wav: Blob) => void;
  onDone?: (info: { session_id?: string; model_used?: string; latency_ms?: number }) => void;
  onError?: (detail: string) => void;
}

/**
 * Streaming voice turn. POSTs the WAV to /voice/interact/stream and dispatches
 * SSE events as they arrive so the first sentence can play while the rest is
 * still being generated. Resolves with the accumulated transcript + reply text
 * (so the caller can push a turn and, if no audio arrived, use browser speech).
 */
export async function voiceInteractStream(
  wavBytes: Uint8Array,
  sessionId: string | undefined,
  cbs: VoiceStreamCallbacks,
  opts: { use_context?: boolean; max_tokens?: number } = {}
): Promise<{ transcript: string; reply: string; session_id?: string; audioCount: number }> {
  const form = new FormData();
  const blobPart = new Uint8Array(wavBytes);
  form.append('audio', new Blob([blobPart.buffer], { type: 'audio/wav' }), 'voice.wav');
  if (sessionId) form.append('session_id', sessionId);
  form.append('use_context', opts.use_context === false ? 'false' : 'true');
  form.append('max_tokens', String(opts.max_tokens ?? 512));

  const res = await fetch(API_BASE + '/voice/interact/stream', { method: 'POST', body: form });
  if (!res.ok || !res.body) {
    const raw = (await res.json().catch(() => ({}))) as Record<string, unknown>;
    const d = raw.detail;
    throw new Error(typeof d === 'string' ? d : `HTTP ${res.status}`);
  }

  let transcript = '';
  let reply = '';
  let sessionOut: string | undefined;
  let audioCount = 0;

  const reader = res.body.getReader();
  const decoder = new TextDecoder();
  let buf = '';
  // Parse SSE frames (blank-line delimited); each carries one `data:` JSON line.
  for (;;) {
    const { value, done } = await reader.read();
    if (done) break;
    buf += decoder.decode(value, { stream: true });
    let idx: number;
    while ((idx = buf.indexOf('\n\n')) !== -1) {
      const frame = buf.slice(0, idx);
      buf = buf.slice(idx + 2);
      const line = frame.split('\n').find((l) => l.startsWith('data:'));
      if (!line) continue;
      const rawData = line.slice(5).trim();
      if (!rawData) continue;
      let evt: Record<string, unknown>;
      try {
        evt = JSON.parse(rawData) as Record<string, unknown>;
      } catch {
        continue;
      }
      switch (evt.type) {
        case 'transcript':
          transcript = String(evt.text ?? '');
          cbs.onTranscript?.(transcript);
          break;
        case 'token': {
          const piece = String(evt.content ?? '');
          reply += piece;
          cbs.onToken?.(piece);
          break;
        }
        case 'audio': {
          const b64 = String(evt.data ?? '');
          if (b64) {
            audioCount += 1;
            cbs.onAudio?.(Number(evt.seq ?? audioCount), base64ToWavBlob(b64));
          }
          break;
        }
        case 'done':
          sessionOut = typeof evt.session_id === 'string' ? evt.session_id : sessionOut;
          cbs.onDone?.({
            session_id: sessionOut,
            model_used: typeof evt.model_used === 'string' ? evt.model_used : undefined,
            latency_ms: typeof evt.latency_ms === 'number' ? evt.latency_ms : undefined
          });
          break;
        case 'error':
          cbs.onError?.(String(evt.detail ?? 'stream error'));
          break;
        default:
          break;
      }
    }
  }
  return { transcript, reply: reply.trim(), session_id: sessionOut, audioCount };
}

function base64ToWavBlob(b64: string): Blob {
  const bin = atob(b64);
  const bytes = new Uint8Array(bin.length);
  for (let i = 0; i < bin.length; i++) bytes[i] = bin.charCodeAt(i);
  return new Blob([bytes], { type: 'audio/wav' });
}

/**
 * Optional Voicebox proxy: returns WAV bytes for the given text.
 * Returns null when the endpoint is disabled (404) so callers can fall back
 * to the browser Web Speech API.
 */
export async function synthesize(text: string, timeoutMs = 22000): Promise<Blob | null> {
  const t = text.trim();
  if (!t) return null;
  // Abort a slow synth so the caller can fall back to Web Speech promptly
  // rather than leaving the orb stuck in "speaking" while the host is busy.
  const ctrl = new AbortController();
  const timer = setTimeout(() => ctrl.abort(), timeoutMs);
  try {
    const res = await fetch(API_BASE + '/voice/tts?text=' + encodeURIComponent(t), {
      signal: ctrl.signal
    });
    // 404/501 (disabled) or 502/503 (upstream unreachable/slow): treat as "no
    // server voice" and let the caller use the browser fallback.
    if (res.status === 404 || res.status === 501 || res.status === 502 || res.status === 503)
      return null;
    if (!res.ok) throw new Error(`tts HTTP ${res.status}`);
    return await res.blob();
  } catch (e) {
    // AbortError or network failure → fall back rather than surfacing an error.
    if (e instanceof DOMException && e.name === 'AbortError') return null;
    throw e;
  } finally {
    clearTimeout(timer);
  }
}
