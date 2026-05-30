// src/lib/api/pty.ts — PTY WebSocket client.
import { wsUrl } from './base';

export interface PtyClient {
  send: (data: string) => void;
  resize: (cols: number, rows: number) => void;
  close: () => void;
}

export interface OpenPtyOpts {
  cwd?: string;
  cols?: number;
  rows?: number;
  onOutput: (chunk: string) => void;
  onExit?: (code: number) => void;
}

export function openPty(opts: OpenPtyOpts): PtyClient {
  const params: Record<string, string | number> = {};
  if (opts.cwd) params.cwd = opts.cwd;
  if (opts.cols) params.cols = opts.cols;
  if (opts.rows) params.rows = opts.rows;
  const ws = new WebSocket(wsUrl('/zeus-os/pty', params));

  ws.onmessage = (ev) => {
    try {
      const frame = JSON.parse(ev.data);
      if (frame.type === 'output' && typeof frame.data === 'string') {
        opts.onOutput(frame.data);
      } else if (frame.type === 'exit') {
        opts.onExit?.(typeof frame.code === 'number' ? frame.code : -1);
      }
    } catch {
      /* ignore */
    }
  };

  function safeSend(payload: object) {
    if (ws.readyState === WebSocket.OPEN) {
      ws.send(JSON.stringify(payload));
    } else {
      ws.addEventListener('open', () => ws.send(JSON.stringify(payload)), { once: true });
    }
  }

  return {
    send(data: string) {
      safeSend({ type: 'input', data });
    },
    resize(cols: number, rows: number) {
      safeSend({ type: 'resize', cols, rows });
    },
    close() {
      try {
        ws.close();
      } catch {
        /* ignore */
      }
    }
  };
}
