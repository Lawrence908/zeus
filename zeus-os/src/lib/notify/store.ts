// src/lib/notify/store.ts — tiny pub/sub for toast notifications.
import { writable } from 'svelte/store';

export type ToastKind = 'info' | 'ok' | 'warn' | 'err';

export interface Toast {
  id: string;
  title: string;
  body?: string;
  kind: ToastKind;
  createdAt: number;
  ttlMs: number;
}

export const toasts = writable<Toast[]>([]);

let _counter = 0;

export interface NotifyOpts {
  title: string;
  body?: string;
  kind?: ToastKind;
  ttlMs?: number;
}

export function notify(opts: NotifyOpts): string {
  _counter += 1;
  const id = `t-${_counter}`;
  const t: Toast = {
    id,
    title: opts.title,
    body: opts.body,
    kind: opts.kind ?? 'info',
    createdAt: performance.now(),
    ttlMs: opts.ttlMs ?? 3500
  };
  toasts.update((arr) => [...arr, t]);
  if (t.ttlMs > 0) {
    setTimeout(() => dismiss(id), t.ttlMs);
  }
  return id;
}

export function dismiss(id: string) {
  toasts.update((arr) => arr.filter((t) => t.id !== id));
}
