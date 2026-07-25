// src/lib/api/base.ts — common helpers for Zeus OS API clients.
//
// Same-origin in production (Zeus core serves /os/ on :8203). In dev the Vite
// proxy forwards /chat /zeus-os /vault /admin /... to the backend, so we don't
// need an explicit base URL.

export const API_BASE = '';

export function wsUrl(path: string, params?: Record<string, string | number>): string {
  if (typeof window === 'undefined') return '';
  const proto = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
  const search = params
    ? '?' +
      Object.entries(params)
        .map(([k, v]) => `${encodeURIComponent(k)}=${encodeURIComponent(String(v))}`)
        .join('&')
    : '';
  return `${proto}//${window.location.host}${path}${search}`;
}

export async function jsonFetch<T = unknown>(
  path: string,
  init: RequestInit = {}
): Promise<T> {
  const res = await fetch(API_BASE + path, {
    ...init,
    headers: {
      'content-type': 'application/json',
      ...(init.headers ?? {})
    }
  });
  if (!res.ok) {
    const detail = await res.text().catch(() => '');
    throw new Error(`${res.status} ${res.statusText}: ${detail.slice(0, 200)}`);
  }
  return res.json() as Promise<T>;
}
