// src/lib/voice/orb.ts — Phaos voice orb, v2.
//
// Modern AI-voice-assistant visualization (ChatGPT/Gemini-live style): a fluid
// fbm-displaced blob with a bright additive core and a soft halo, all driven
// by a smoothed audio level (fast attack, slow decay) and state-tinted color
// palettes that crossfade instead of snapping. Idle colors are pulled from the
// active theme's --accent / --accent-2 CSS vars so the orb matches the shell.
import * as THREE from 'three';

const BLOB_VERT = /* glsl */ `
uniform float uTime;
uniform float uLevel;
uniform float uEnergy;

varying vec3 vWorldPos;
varying vec3 vWorldNormal;
varying float vDisp;

float hash(vec3 p) {
  return fract(sin(dot(p, vec3(127.1, 311.7, 74.7))) * 43758.5453);
}

float noise(vec3 p) {
  vec3 i = floor(p);
  vec3 f = fract(p);
  f = f * f * (3.0 - 2.0 * f);
  return mix(
    mix(mix(hash(i + vec3(0,0,0)), hash(i + vec3(1,0,0)), f.x),
        mix(hash(i + vec3(0,1,0)), hash(i + vec3(1,1,0)), f.x), f.y),
    mix(mix(hash(i + vec3(0,0,1)), hash(i + vec3(1,0,1)), f.x),
        mix(hash(i + vec3(0,1,1)), hash(i + vec3(1,1,1)), f.x), f.y),
    f.z
  );
}

float fbm(vec3 p) {
  float v = 0.0;
  float a = 0.55;
  for (int i = 0; i < 4; i++) {
    v += a * noise(p);
    p = p * 2.02 + vec3(17.3, 9.1, 4.7);
    a *= 0.5;
  }
  return v;
}

void main() {
  vec3 pos = position;
  float t = uTime;

  // Gentle breathing at rest; audio level opens the deformation up.
  float breathe = 0.03 * sin(t * 1.4);
  float amp = 0.05 + breathe + uLevel * 0.55 + uEnergy * 0.10;

  // Two fbm layers drifting in opposite directions gives the "liquid" look.
  float n1 = fbm(pos * 2.1 + vec3(0.0, t * 0.35, 0.0));
  float n2 = fbm(pos * 4.3 - vec3(t * 0.5, 0.0, t * 0.22));
  float disp = (n1 * 0.7 + n2 * 0.45 - 0.55) * amp;
  pos += normal * disp;

  vDisp = disp;
  vec4 worldPos = modelMatrix * vec4(pos, 1.0);
  vWorldPos = worldPos.xyz;
  vWorldNormal = normalize(mat3(modelMatrix) * normal);
  gl_Position = projectionMatrix * modelViewMatrix * vec4(pos, 1.0);
}
`;

const BLOB_FRAG = /* glsl */ `
uniform vec3 uColorA;   // deep body color
uniform vec3 uColorB;   // rim / fresnel color
uniform vec3 uColorC;   // hot highlight color
uniform float uLevel;
uniform float uTime;
uniform float uEnergy;
uniform vec3 uCamPos;

varying vec3 vWorldPos;
varying vec3 vWorldNormal;
varying float vDisp;

void main() {
  vec3 viewDir = normalize(uCamPos - vWorldPos);
  vec3 n = normalize(vWorldNormal);
  float fresnel = pow(1.0 - clamp(dot(n, viewDir), 0.0, 1.0), 2.4);

  // Body gradient: deep color in the middle, rim color at grazing angles,
  // hot color blooming out of displacement peaks + audio level.
  float hot = clamp(vDisp * 3.0 + uLevel * 0.55, 0.0, 1.0);
  vec3 col = mix(uColorA, uColorB, fresnel);
  col = mix(col, uColorC, hot * 0.65);

  // Subtle iridescent shimmer while processing/speaking.
  col += uColorB * uEnergy * 0.12 * (0.5 + 0.5 * sin(uTime * 6.0 + vWorldPos.y * 4.0));

  float alpha = 0.62 + fresnel * 0.3 + uLevel * 0.08;
  gl_FragColor = vec4(col, clamp(alpha, 0.0, 1.0));
}
`;

const CORE_VERT = /* glsl */ `
varying vec3 vNormal;
varying vec3 vView;
void main() {
  vNormal = normalize(normalMatrix * normal);
  vec4 mv = modelViewMatrix * vec4(position, 1.0);
  vView = normalize(-mv.xyz);
  gl_Position = projectionMatrix * mv;
}
`;

const CORE_FRAG = /* glsl */ `
uniform vec3 uColorC;
uniform float uLevel;
varying vec3 vNormal;
varying vec3 vView;
void main() {
  // Soft center-weighted glow: brightest facing the camera, fading at rim.
  float facing = clamp(dot(normalize(vNormal), normalize(vView)), 0.0, 1.0);
  float g = pow(facing, 1.6) * (0.5 + uLevel * 0.9);
  gl_FragColor = vec4(uColorC * g, g * 0.85);
}
`;

export type VoiceStateName =
  | 'idle'
  | 'wake_detected'
  | 'listening'
  | 'processing'
  | 'speaking';

interface Palette {
  a: THREE.Color; // body
  b: THREE.Color; // rim
  c: THREE.Color; // hot core
  energy: number; // ambient agitation independent of audio level
}

function cssRgb(varName: string, fallback: number): THREE.Color {
  if (typeof window === 'undefined') return new THREE.Color(fallback);
  const raw = getComputedStyle(document.documentElement).getPropertyValue(varName).trim();
  const parts = raw.split(/\s+/).map(Number);
  if (parts.length === 3 && parts.every((p) => Number.isFinite(p))) {
    return new THREE.Color(parts[0] / 255, parts[1] / 255, parts[2] / 255);
  }
  return new THREE.Color(fallback);
}

function themedPalettes(): Record<VoiceStateName, Palette> {
  const accent = cssRgb('--accent', 0x89b4fa);
  const accent2 = cssRgb('--accent-2', 0xcba6f7);
  const idleBody = accent.clone().multiplyScalar(0.35);
  return {
    idle: { a: idleBody, b: accent.clone(), c: accent2.clone(), energy: 0.0 },
    wake_detected: {
      a: accent.clone().multiplyScalar(0.5),
      b: accent.clone().lerp(new THREE.Color(0xffffff), 0.35),
      c: accent2.clone(),
      energy: 0.35
    },
    listening: {
      a: accent.clone().multiplyScalar(0.5),
      b: accent.clone().lerp(new THREE.Color(0xffffff), 0.35),
      c: accent2.clone().lerp(new THREE.Color(0xffffff), 0.2),
      energy: 0.25
    },
    processing: {
      a: new THREE.Color(0x4a2c8f).lerp(accent2, 0.3),
      b: accent2.clone(),
      c: new THREE.Color(0x9be8ff),
      energy: 0.75
    },
    speaking: {
      a: new THREE.Color(0x8f3a1e),
      b: new THREE.Color(0xffab70),
      c: new THREE.Color(0xffe0b0),
      energy: 0.5
    }
  };
}

function haloTexture(): THREE.Texture {
  const size = 256;
  const canvas = document.createElement('canvas');
  canvas.width = size;
  canvas.height = size;
  const ctx = canvas.getContext('2d')!;
  const g = ctx.createRadialGradient(size / 2, size / 2, 0, size / 2, size / 2, size / 2);
  g.addColorStop(0, 'rgba(255,255,255,0.85)');
  g.addColorStop(0.25, 'rgba(255,255,255,0.28)');
  g.addColorStop(0.6, 'rgba(255,255,255,0.07)');
  g.addColorStop(1, 'rgba(255,255,255,0)');
  ctx.fillStyle = g;
  ctx.fillRect(0, 0, size, size);
  const tex = new THREE.CanvasTexture(canvas);
  tex.needsUpdate = true;
  return tex;
}

export interface OrbHandle {
  setStateName(name: VoiceStateName): void;
  setLevel(v: number): void;
  /** Re-read theme CSS vars (call after a theme switch). */
  refreshTheme(): void;
  tick(dt: number): void;
  resize(): void;
  dispose(): void;
}

export function createPhaosOrb(container: HTMLElement): OrbHandle {
  const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
  renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
  renderer.setSize(container.clientWidth, container.clientHeight);
  renderer.setClearColor(0x000000, 0);
  renderer.outputColorSpace = THREE.SRGBColorSpace;
  renderer.toneMapping = THREE.ACESFilmicToneMapping;
  container.appendChild(renderer.domElement);

  const scene = new THREE.Scene();
  const camera = new THREE.PerspectiveCamera(
    50,
    container.clientWidth / Math.max(container.clientHeight, 1),
    0.1,
    100
  );
  const SPHERE_RADIUS = 1.85;

  function fitCameraDistance(w: number, h: number): number {
    const aspect = w / Math.max(h, 1);
    const vFovRad = (camera.fov * Math.PI) / 180;
    const tanHalf = Math.tan(vFovRad / 2);
    const dVert = SPHERE_RADIUS / tanHalf;
    const dHoriz = SPHERE_RADIUS / (tanHalf * aspect);
    return Math.max(3.2, dVert, dHoriz);
  }

  camera.position.set(0, 0, 3.6);

  let palettes = themedPalettes();

  // ── main blob ──
  const blobGeo = new THREE.IcosahedronGeometry(1, 7);
  const blobMat = new THREE.ShaderMaterial({
    uniforms: {
      uTime: { value: 0 },
      uLevel: { value: 0 },
      uEnergy: { value: 0 },
      uColorA: { value: palettes.idle.a.clone() },
      uColorB: { value: palettes.idle.b.clone() },
      uColorC: { value: palettes.idle.c.clone() },
      uCamPos: { value: new THREE.Vector3() }
    },
    vertexShader: BLOB_VERT,
    fragmentShader: BLOB_FRAG,
    transparent: true,
    side: THREE.DoubleSide,
    depthWrite: false
  });
  const blob = new THREE.Mesh(blobGeo, blobMat);
  scene.add(blob);

  // ── inner core (additive glow) ──
  const coreGeo = new THREE.SphereGeometry(0.55, 32, 32);
  const coreMat = new THREE.ShaderMaterial({
    uniforms: {
      uColorC: { value: palettes.idle.c.clone() },
      uLevel: { value: 0 }
    },
    vertexShader: CORE_VERT,
    fragmentShader: CORE_FRAG,
    transparent: true,
    blending: THREE.AdditiveBlending,
    depthWrite: false
  });
  const core = new THREE.Mesh(coreGeo, coreMat);
  scene.add(core);

  // ── halo sprite ──
  const haloMat = new THREE.SpriteMaterial({
    map: haloTexture(),
    color: palettes.idle.b.clone(),
    transparent: true,
    blending: THREE.AdditiveBlending,
    depthWrite: false,
    opacity: 0.55
  });
  const halo = new THREE.Sprite(haloMat);
  halo.scale.setScalar(4.2);
  halo.position.z = -0.5;
  scene.add(halo);

  // ── smoothing state ──
  let targetLevel = 0;
  let level = 0;
  let stateName: VoiceStateName = 'idle';
  const cur: Palette = {
    a: palettes.idle.a.clone(),
    b: palettes.idle.b.clone(),
    c: palettes.idle.c.clone(),
    energy: 0
  };

  function setStateName(name: VoiceStateName): void {
    stateName = name in palettes ? name : 'idle';
  }

  function setLevel(v: number): void {
    targetLevel = Math.max(0, Math.min(1, v));
  }

  function refreshTheme(): void {
    palettes = themedPalettes();
  }

  function resize(): void {
    const w = container.clientWidth;
    const h = Math.max(container.clientHeight, 1);
    camera.aspect = w / h;
    camera.position.z = fitCameraDistance(w, h);
    camera.updateProjectionMatrix();
    renderer.setSize(w, h);
  }

  const ro = new ResizeObserver(() => resize());
  ro.observe(container);
  resize();

  function tick(dt: number): void {
    // Fast attack / slow decay makes the blob feel responsive without jitter.
    const rate = targetLevel > level ? 14 : 3.2;
    level += (targetLevel - level) * Math.min(1, dt * rate);

    const target = palettes[stateName];
    const cf = Math.min(1, dt * 4.5); // color crossfade
    cur.a.lerp(target.a, cf);
    cur.b.lerp(target.b, cf);
    cur.c.lerp(target.c, cf);
    cur.energy += (target.energy - cur.energy) * cf;

    blobMat.uniforms.uTime.value += dt * (1 + cur.energy * 1.6);
    blobMat.uniforms.uLevel.value = level;
    blobMat.uniforms.uEnergy.value = cur.energy;
    (blobMat.uniforms.uColorA.value as THREE.Color).copy(cur.a);
    (blobMat.uniforms.uColorB.value as THREE.Color).copy(cur.b);
    (blobMat.uniforms.uColorC.value as THREE.Color).copy(cur.c);
    blobMat.uniforms.uCamPos.value.copy(camera.position);

    coreMat.uniforms.uLevel.value = level + cur.energy * 0.35;
    (coreMat.uniforms.uColorC.value as THREE.Color).copy(cur.c);
    const corePulse = 1 + level * 0.35 + 0.04 * Math.sin(blobMat.uniforms.uTime.value * 2.2);
    core.scale.setScalar(corePulse);

    haloMat.color.copy(cur.b);
    haloMat.opacity = 0.4 + level * 0.45 + cur.energy * 0.15;
    halo.scale.setScalar(4.0 + level * 1.4 + cur.energy * 0.5);

    blob.rotation.y += dt * (0.12 + cur.energy * 0.25);
    blob.rotation.x = 0.15 * Math.sin(blobMat.uniforms.uTime.value * 0.3);

    renderer.render(scene, camera);
  }

  function dispose(): void {
    ro.disconnect();
    blobGeo.dispose();
    blobMat.dispose();
    coreGeo.dispose();
    coreMat.dispose();
    haloMat.map?.dispose();
    haloMat.dispose();
    renderer.dispose();
    if (renderer.domElement.parentNode === container) {
      container.removeChild(renderer.domElement);
    }
  }

  return { setStateName, setLevel, refreshTheme, tick, resize, dispose };
}
