// src/lib/apps/chat-sessions.ts — module-level registry of per-window chat
// state, keyed by AppInstance.instanceId. Lets Chat windows survive the
// float ↔ tile toggle (which tears down the component) without losing their
// message history or backend session id.
import { onAppDestroyed } from '$lib/wm/store';

export interface ToolCall {
  name?: string;
  arguments?: unknown;
  result?: unknown;
  error?: string;
}

export interface ChatMsg {
  role: 'user' | 'assistant';
  content: string;
  phase?: string;
  toolCalls?: ToolCall[];
  model?: string;
  latency_ms?: number;
}

export interface ChatSession {
  messages: ChatMsg[];
  sessionId: string | null;
}

const _sessions = new Map<string, ChatSession>();

export function getChatSession(instanceId: string): ChatSession {
  let s = _sessions.get(instanceId);
  if (!s) {
    s = { messages: [], sessionId: null };
    _sessions.set(instanceId, s);
  }
  return s;
}

export function setChatSession(instanceId: string, patch: Partial<ChatSession>) {
  const s = getChatSession(instanceId);
  Object.assign(s, patch);
}

// Clear when the WM tells us the window was closed for real.
onAppDestroyed((id) => {
  _sessions.delete(id);
});
