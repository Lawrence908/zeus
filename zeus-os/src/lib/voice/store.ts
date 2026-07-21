// src/lib/voice/store.ts — Svelte stores that carry voice state across apps.
//
// - voiceState / voiceLevel / voiceConnected: synced from /ws/voice-state.
// - voicePttTrigger: incremented every time a global PTT keybind fires. The
//   Voice Orb subscribes to changes and toggles its record state.
// - voiceTurns: queue of {transcript, reply} turns emitted by the Orb. Chat
//   windows subscribe and append matching turns to their message list.
import { writable } from 'svelte/store';
import type { VoiceStateName } from './orb';

export const voiceState = writable<VoiceStateName>('idle');
export const voiceLevel = writable<number>(0);
export const voiceConnected = writable<boolean>(false);

/** Incremented on every global PTT hotkey press. */
export const voicePttTrigger = writable<number>(0);

export interface VoiceTurn {
  id: string;
  transcript: string;
  reply: string;
  model?: string;
  contextSources?: string[];
  ts: number;
  sessionId?: string;
}

/** Newest first, capped at 32 to keep memory bounded. */
export const voiceTurns = writable<VoiceTurn[]>([]);

export function pushVoiceTurn(turn: VoiceTurn): void {
  voiceTurns.update((xs) => {
    const next = [turn, ...xs];
    return next.length > 32 ? next.slice(0, 32) : next;
  });
}

export function triggerVoicePtt(): void {
  voicePttTrigger.update((n) => n + 1);
}
