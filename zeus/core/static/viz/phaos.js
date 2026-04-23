// zeus/core/static/viz/phaos.js — Phaos VizEngine: WS state + mic + orb + optional XR
import { createMicAnalyzer } from './audio.js';
import { createPhaosOrb } from './orb.js';
import { attachXRButton } from './xr.js';

/**
 * @typedef {Object} PhaosOptions
 * @property {HTMLElement} container
 * @property {string} [wsPath='/ws/voice-state']
 * @property {boolean} [enableMic=true]
 * @property {boolean} [enableXR=true]
 */

/**
 * @param {PhaosOptions} options
 */
export async function initPhaos(options) {
  const {
    container,
    wsPath = '/ws/voice-state',
    enableMic = true,
    enableXR = true,
  } = options;

  const orb = createPhaosOrb(container);
  if (enableXR) {
    try {
      attachXRButton(orb.renderer, container);
    } catch (_) {
      /* XR not supported */
    }
  }

  /** @type {{ level: () => number, dispose: () => Promise<void> } | null} */
  let mic = null;
  if (enableMic) {
    try {
      mic = await createMicAnalyzer();
    } catch (_) {
      mic = null;
    }
  }

  const proto = location.protocol === 'https:' ? 'wss:' : 'ws:';
  const ws = new WebSocket(`${proto}//${location.host}${wsPath}`);

  let serverLevel = 0;
  let state = 'idle';

  ws.addEventListener('message', (ev) => {
    try {
      const d = JSON.parse(ev.data);
      if (d.type === 'voice_state') {
        state = d.state || 'idle';
        serverLevel = typeof d.audio_level === 'number' ? d.audio_level : 0;
        orb.setStateName(state);
        if (state !== 'listening') {
          orb.setLevel(serverLevel);
        }
      }
    } catch (_) {
      /* ignore */
    }
  });

  let pingInterval = null;
  ws.addEventListener('open', () => {
    if (pingInterval) clearInterval(pingInterval);
    pingInterval = setInterval(() => {
      if (ws.readyState === WebSocket.OPEN) {
        ws.send(JSON.stringify({ type: 'ping' }));
      }
    }, 25000);
  });

  let last = performance.now();
  let raf = 0;

  function frame(now) {
    const dt = Math.min(0.05, (now - last) / 1000);
    last = now;

    let lvl = serverLevel;
    if (state === 'listening' && mic) {
      lvl = Math.max(lvl, mic.level());
    } else if (state === 'speaking') {
      lvl = Math.max(lvl, serverLevel);
    }
    orb.setLevel(lvl);
    orb.tick(dt);
    raf = requestAnimationFrame(frame);
  }

  raf = requestAnimationFrame(frame);

  function destroy() {
    if (pingInterval) clearInterval(pingInterval);
    cancelAnimationFrame(raf);
    ws.close();
    orb.dispose();
    if (mic) {
      mic.dispose();
    }
  }

  /** Browsers start AudioContext suspended; call after a user gesture (click/tap). */
  async function resumeAudio() {
    if (mic?.audioContext?.state === 'suspended') {
      await mic.audioContext.resume();
    }
  }

  return { orb, ws, destroy, resumeAudio, mic };
}
