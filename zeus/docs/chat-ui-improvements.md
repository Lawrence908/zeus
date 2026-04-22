# Zeus chat UI improvements (static page)

> **Scope:** the legacy single-file browser chat at `zeus/core/static/chat.html`. The primary chat UI is now the React SPA in [zeus/frontend/](../frontend/) (built into `zeus/core/static/app/`). This checklist survives so the static fallback stays useful for dev smoke and offline debugging; new UI work should happen in the React app, not here.

Living checklist for the static browser chat. See also [`chat-interface-spec.md`](chat-interface-spec.md) for the HTTP surface shared by both UIs.

## Priority summary

| Priority | Feature | Notes |
|----------|---------|--------|
| 1 | Markdown (assistant only) | `marked` + DOMPurify via [`chat-markdown.js`](../core/static/chat-markdown.js); user bubbles stay plain text |
| 2 | Copy | Per-message control; copies raw assistant markdown / user plain text |
| 3 | Abort stream | `AbortController` on `POST /chat/stream`; Stop button while busy; no fallback to non-stream on user abort |
| 4 | Token estimate (stream) | `done` SSE includes `token_estimate` (~len/4), parity with `ChatMessageResponse` |
| 5 | Draft persist | `sessionStorage` key `zeus.chat.draft` scoped by session id or `new` |
| 6 | Session tabs | Tab strip + “All sessions” dialog; sidebar list removed |
| 7 | Light theme | `data-theme` on `<html>`, toggle in header, `localStorage` + `prefers-color-scheme` default |

## Security

- All assistant HTML goes through DOMPurify with a tight tag/attribute allowlist.
- Links: external `target="_blank"` and `rel="noopener noreferrer"` applied after sanitize.

## Abort semantics

- [`QueryEngine.query_stream`](../core/query.py) calls `append_turn` only after the LLM iterator completes. Client disconnect mid-stream should not persist a partial turn.
- If the server has already finished consuming the model stream before the client aborts, a full turn may still be saved.

## Acceptance (quick)

- Fenced code and lists render; scripts stripped from markdown.
- Copy works with keyboard focus and clipboard fallback toast on failure.
- Stop cancels without error toast; mic/send return to normal.
- Streaming meta line matches non-stream: `model · ms · ~N tok`.
- Refresh preserves composer draft for current session.
- Tabs switch sessions; “All sessions” lists the same set.
- Theme persists and avoids wrong-theme flash via inline boot script in `chat.html`.
