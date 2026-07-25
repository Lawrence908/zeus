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

/**
 * Optional Voicebox proxy: returns WAV bytes for the given text.
 * Returns null when the endpoint is disabled (404) so callers can fall back
 * to the browser Web Speech API.
 */
export async function synthesize(text: string): Promise<Blob | null> {
  const t = text.trim();
  if (!t) return null;
  const res = await fetch(API_BASE + '/voice/tts?text=' + encodeURIComponent(t));
  if (res.status === 404 || res.status === 501) return null;
  if (!res.ok) throw new Error(`tts HTTP ${res.status}`);
  return await res.blob();
}
