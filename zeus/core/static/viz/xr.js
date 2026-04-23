// zeus/core/static/viz/xr.js — WebXR entry (VR); AR can use ARButton the same way later
import { VRButton } from 'three/addons/webxr/VRButton.js';

/**
 * Adds Three.js VR button for immersive headset sessions.
 * @param {import('three').WebGLRenderer} renderer
 * @param {HTMLElement} [host] — if set, button is appended here; else document.body
 */
export function attachXRButton(renderer, host) {
  const el = VRButton.createButton(renderer);
  el.style.position = 'relative';
  el.style.marginTop = '8px';
  el.style.bottom = 'auto';
  el.style.left = 'auto';
  (host || document.body).appendChild(el);
  return el;
}

/**
 * Optional: immersive AR (passthrough) — enable when testing on supported devices.
 * import { ARButton } from 'three/addons/webxr/ARButton.js';
 * export function attachARButton(renderer, host) {
 *   const el = ARButton.createButton(renderer, { requiredFeatures: ['local-floor'] });
 *   (host || document.body).appendChild(el);
 *   return el;
 * }
 */
