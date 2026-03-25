// zeus/core/static/viz/orb.js — Three.js Phaos orb (noise displacement + fresnel glow)
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

const STATE_MAP = {
  idle: 0,
  wake_detected: 1,
  listening: 1,
  processing: 2,
  speaking: 3,
};

/**
 * @param {HTMLElement} container
 */
export function createPhaosOrb(container) {
  const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
  renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
  renderer.setSize(container.clientWidth, container.clientHeight);
  renderer.setClearColor(0x000000, 0);
  renderer.xr.enabled = true;
  renderer.outputColorSpace = THREE.SRGBColorSpace;
  renderer.toneMapping = THREE.ACESFilmicToneMapping;
  container.appendChild(renderer.domElement);

  const scene = new THREE.Scene();
  const camera = new THREE.PerspectiveCamera(
    50,
    container.clientWidth / Math.max(container.clientHeight, 1),
    0.1,
    100,
  );
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
      cameraPos: { value: new THREE.Vector3() },
    },
    vertexShader: VERT,
    fragmentShader: FRAG,
    transparent: true,
    side: THREE.DoubleSide,
    depthWrite: false,
  });

  const mesh = new THREE.Mesh(geo, mat);
  scene.add(mesh);

  function setStateName(name) {
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

  function setLevel(v) {
    mat.uniforms.uLevel.value = Math.max(0, Math.min(1, v));
  }

  function resize() {
    const w = container.clientWidth;
    const h = Math.max(container.clientHeight, 1);
    camera.aspect = w / h;
    camera.updateProjectionMatrix();
    renderer.setSize(w, h);
  }

  window.addEventListener('resize', resize);

  function tick(dt) {
    mat.uniforms.uTime.value += dt;
    mat.uniforms.cameraPos.value.copy(camera.position);
    mesh.rotation.y += dt * 0.15;
    renderer.render(scene, camera);
  }

  function dispose() {
    window.removeEventListener('resize', resize);
    geo.dispose();
    mat.dispose();
    renderer.dispose();
    if (renderer.domElement.parentNode === container) {
      container.removeChild(renderer.domElement);
    }
  }

  return {
    renderer,
    scene,
    camera,
    mesh,
    material: mat,
    setStateName,
    setLevel,
    tick,
    dispose,
    resize,
  };
}
