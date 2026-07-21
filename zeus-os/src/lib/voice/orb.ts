// src/lib/voice/orb.ts — TypeScript port of the Phaos icosahedron orb
// (originally at zeus/core/static/viz/orb.js). Shader-driven displacement +
// fresnel glow that reflects voice state (idle / listening / processing /
// speaking) and audio level.
import * as THREE from 'three';

const VERT = /* glsl */ `
uniform float uTime;
uniform float uLevel;
uniform int uState;
uniform vec3 cameraPos;

varying vec3 vWorldPos;
varying vec3 vWorldNormal;

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

void main() {
  vec3 pos = position;
  float t = uTime;
  float amp = 0.06 + uLevel * 0.42;
  if (uState == 2) amp += 0.12;
  if (uState == 3) amp += 0.06;
  float n1 = noise(pos * 3.2 + t * 0.55);
  float n2 = noise(pos * 6.1 - t * 0.95);
  float disp = (n1 * 0.65 + n2 * 0.35) * amp;
  pos += normal * disp;

  vec4 worldPos = modelMatrix * vec4(pos, 1.0);
  vWorldPos = worldPos.xyz;
  vWorldNormal = normalize(mat3(modelMatrix) * normal);
  gl_Position = projectionMatrix * modelViewMatrix * vec4(pos, 1.0);
}
`;

const FRAG = /* glsl */ `
uniform vec3 uColorA;
uniform vec3 uColorB;
uniform float uLevel;
uniform float uTime;
uniform int uState;
uniform vec3 cameraPos;

varying vec3 vWorldPos;
varying vec3 vWorldNormal;

void main() {
  vec3 viewDir = normalize(cameraPos - vWorldPos);
  vec3 n = normalize(vWorldNormal);
  float fresnel = pow(1.0 - clamp(dot(n, viewDir), 0.0, 1.0), 2.2);
  float pulse = uLevel * 0.35;
  if (uState == 2) pulse += 0.08 * sin(uTime * 8.0);
  vec3 col = mix(uColorA, uColorB, fresnel + pulse);
  float alpha = 0.78 + fresnel * 0.2 + uLevel * 0.08;
  gl_FragColor = vec4(col, alpha);
}
`;

export type VoiceStateName =
  | 'idle'
  | 'wake_detected'
  | 'listening'
  | 'processing'
  | 'speaking';

const STATE_MAP: Record<VoiceStateName, number> = {
  idle: 0,
  wake_detected: 1,
  listening: 1,
  processing: 2,
  speaking: 3
};

export interface OrbHandle {
  setStateName(name: VoiceStateName): void;
  setLevel(v: number): void;
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
  const SPHERE_RADIUS = 1.7;

  function fitCameraDistance(w: number, h: number): number {
    const aspect = w / Math.max(h, 1);
    const vFovRad = (camera.fov * Math.PI) / 180;
    const tanHalf = Math.tan(vFovRad / 2);
    const dVert = SPHERE_RADIUS / tanHalf;
    const dHoriz = SPHERE_RADIUS / (tanHalf * aspect);
    return Math.max(3.2, dVert, dHoriz);
  }

  camera.position.set(0, 0, 3.4);

  scene.add(new THREE.AmbientLight(0x334466, 0.4));
  const key = new THREE.PointLight(0x88ccff, 1.4, 24);
  key.position.set(2.5, 1.5, 4);
  scene.add(key);
  const rim = new THREE.PointLight(0xff8866, 0.6, 16);
  rim.position.set(-3, -1, 2);
  scene.add(rim);

  const geo = new THREE.IcosahedronGeometry(1, 7);
  const mat = new THREE.ShaderMaterial({
    uniforms: {
      uTime: { value: 0 },
      uLevel: { value: 0 },
      uState: { value: 0 },
      uColorA: { value: new THREE.Color(0x4488ff) },
      uColorB: { value: new THREE.Color(0xaaddff) },
      cameraPos: { value: new THREE.Vector3() }
    },
    vertexShader: VERT,
    fragmentShader: FRAG,
    transparent: true,
    side: THREE.DoubleSide,
    depthWrite: false
  });

  const mesh = new THREE.Mesh(geo, mat);
  scene.add(mesh);

  function setStateName(name: VoiceStateName): void {
    mat.uniforms.uState.value = STATE_MAP[name] ?? 0;
    if (name === 'speaking') {
      mat.uniforms.uColorA.value.setHex(0xff9966);
      mat.uniforms.uColorB.value.setHex(0xff4400);
    } else if (name === 'processing') {
      mat.uniforms.uColorA.value.setHex(0x9966ff);
      mat.uniforms.uColorB.value.setHex(0x66ddff);
    } else {
      mat.uniforms.uColorA.value.setHex(0x4488ff);
      mat.uniforms.uColorB.value.setHex(0xaaddff);
    }
  }

  function setLevel(v: number): void {
    mat.uniforms.uLevel.value = Math.max(0, Math.min(1, v));
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
    mat.uniforms.uTime.value += dt;
    mat.uniforms.cameraPos.value.copy(camera.position);
    mesh.rotation.y += dt * 0.15;
    renderer.render(scene, camera);
  }

  function dispose(): void {
    ro.disconnect();
    geo.dispose();
    mat.dispose();
    renderer.dispose();
    if (renderer.domElement.parentNode === container) {
      container.removeChild(renderer.domElement);
    }
  }

  return { setStateName, setLevel, tick, resize, dispose };
}
