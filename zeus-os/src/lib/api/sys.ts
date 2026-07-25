// src/lib/api/sys.ts — system stats WebSocket.
import { wsUrl } from './base';

export interface MemSample {
  total: number;
  used: number;
  available: number;
}

export interface GpuSample {
  util: number;
  mem_used: number;
  mem_total: number;
  temp_c: number;
}

export interface SysSample {
  cpu_pct: number | null;
  mem: MemSample | null;
  load: number[] | null;
  gpu: GpuSample | null;
}

export interface SysStream {
  close: () => void;
}

export function openSysStream(onSample: (s: SysSample) => void): SysStream {
  let ws: WebSocket | null = null;
  let closed = false;
  let attempt = 0;

  function connect() {
    if (closed) return;
    ws = new WebSocket(wsUrl('/zeus-os/sys/stream'));
    ws.onmessage = (ev) => {
      try {
        onSample(JSON.parse(ev.data));
      } catch {
        /* ignore malformed frames */
      }
    };
    ws.onclose = () => {
      if (closed) return;
      attempt += 1;
      const delay = Math.min(5000, 500 * 2 ** Math.min(attempt, 4));
      setTimeout(connect, delay);
    };
    ws.onerror = () => ws?.close();
  }

  connect();

  return {
    close() {
      closed = true;
      ws?.close();
    }
  };
}
