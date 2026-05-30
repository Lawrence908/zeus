// src/lib/api/chat.ts — wraps Zeus core SSE chat at POST /chat/stream.
//
// Event types from the server: "phase" (status updates), "token" (content),
// "done" (final), "error".

import { API_BASE } from './base';

export interface ChatStreamOpts {
  message: string;
  sessionId?: string | null;
  onPhase?: (phase: string) => void;
  onToken: (chunk: string) => void;
  onDone?: (meta: { session_id?: string; latency_ms?: number; model_used?: string }) => void;
  onError?: (detail: string) => void;
  signal?: AbortSignal;
}

export async function chatStream(opts: ChatStreamOpts): Promise<void> {
  const body = JSON.stringify({
    message: opts.message,
    session_id: opts.sessionId ?? undefined,
    use_context: true
  });

  const res = await fetch(API_BASE + '/chat/stream', {
    method: 'POST',
    headers: { 'content-type': 'application/json' },
    body,
    signal: opts.signal
  });
  if (!res.ok || !res.body) {
    const detail = await res.text().catch(() => '');
    opts.onError?.(`${res.status} ${res.statusText}: ${detail.slice(0, 200)}`);
    return;
  }

  const reader = res.body.getReader();
  const decoder = new TextDecoder('utf-8');
  let buffer = '';

  while (true) {
    const { value, done } = await reader.read();
    if (done) break;
    buffer += decoder.decode(value, { stream: true });
    // SSE frames are "\n\n" separated. Each frame may contain multiple lines.
    let idx: number;
    while ((idx = buffer.indexOf('\n\n')) !== -1) {
      const raw = buffer.slice(0, idx);
      buffer = buffer.slice(idx + 2);
      parseFrame(raw, opts);
    }
  }
}

function parseFrame(raw: string, opts: ChatStreamOpts) {
  const lines = raw.split('\n');
  let data = '';
  for (const line of lines) {
    if (line.startsWith(':')) continue; // SSE comment / keepalive
    if (line.startsWith('data:')) {
      data += line.slice(5).trimStart();
    }
  }
  if (!data) return;
  try {
    const frame = JSON.parse(data);
    if (frame.type === 'token' && typeof frame.content === 'string') {
      opts.onToken(frame.content);
    } else if (frame.type === 'phase' && typeof frame.detail === 'string') {
      opts.onPhase?.(frame.detail);
    } else if (frame.type === 'done') {
      opts.onDone?.(frame);
    } else if (frame.type === 'error' && typeof frame.detail === 'string') {
      opts.onError?.(frame.detail);
    }
  } catch {
    // Ignore non-JSON frames (older fallbacks).
  }
}
