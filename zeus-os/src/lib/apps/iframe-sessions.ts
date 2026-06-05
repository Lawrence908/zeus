// src/lib/apps/iframe-sessions.ts — keep <iframe> elements alive across
// component unmount/remount so float-toggling doesn't reload the embedded
// page. Same pattern as terminal-sessions.ts: a module-scope <iframe> lives
// in a detached node, then gets re-parented into whichever host div is
// currently visible.

import { onAppDestroyed } from '$lib/wm/store';

interface IframeSession {
  url: string;
  iframe: HTMLIFrameElement;
}

const _sessions = new Map<string, IframeSession>();

/**
 * Mount (or rebuild) the iframe for `instanceId` into `host`. If the URL
 * changed since last mount the existing iframe is torn down and replaced
 * — otherwise the live element is re-parented and its session continues.
 */
export function mountIframe(instanceId: string, host: HTMLElement, url: string, title: string): void {
  let s = _sessions.get(instanceId);
  if (s && s.url !== url) {
    try {
      s.iframe.remove();
    } catch {
      /* ignore */
    }
    _sessions.delete(instanceId);
    s = undefined;
  }
  if (!s) {
    const iframe = document.createElement('iframe');
    iframe.src = url;
    iframe.title = title;
    iframe.className = 'h-full w-full border-0';
    s = { url, iframe };
    _sessions.set(instanceId, s);
  }
  if (s.iframe.parentElement !== host) {
    host.appendChild(s.iframe);
  }
}

/** Detach the iframe from `host` on component unmount; the element stays alive. */
export function unmountIframe(instanceId: string, host: HTMLElement | null): void {
  const s = _sessions.get(instanceId);
  if (!s || !host) return;
  if (s.iframe.parentElement === host) {
    host.removeChild(s.iframe);
  }
}

// Clean up when the WM tells us the window is closed for real.
onAppDestroyed((instanceId) => {
  const s = _sessions.get(instanceId);
  if (!s) return;
  try {
    s.iframe.remove();
  } catch {
    /* ignore */
  }
  _sessions.delete(instanceId);
});
