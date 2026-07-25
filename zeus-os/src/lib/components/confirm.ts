// src/lib/components/confirm.ts — promise-based confirm dialog.
//
// Apps call `confirmDialog('Delete 3 memories?')` and await a boolean; the
// singleton ConfirmHost (mounted in +page.svelte) renders the themed modal.
// Replaces browser-native confirm(), which fights the WM aesthetic and blocks
// the event loop.
import { writable } from 'svelte/store';

export interface PendingConfirm {
  title: string;
  message: string;
  confirmLabel: string;
  danger: boolean;
  resolve: (ok: boolean) => void;
}

export const pendingConfirm = writable<PendingConfirm | null>(null);

export function confirmDialog(
  message: string,
  opts: { title?: string; confirmLabel?: string; danger?: boolean } = {}
): Promise<boolean> {
  return new Promise((resolve) => {
    pendingConfirm.set({
      title: opts.title ?? 'Confirm',
      message,
      confirmLabel: opts.confirmLabel ?? 'Confirm',
      danger: opts.danger ?? true,
      resolve: (ok) => {
        pendingConfirm.set(null);
        resolve(ok);
      }
    });
  });
}
