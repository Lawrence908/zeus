// zeus/frontend/src/components/orb/PhaosOrb3D.tsx
// React Three Fiber port of zeus/core/static/viz/orb.js (LAB-288)
// Preserves GLSL vertex/fragment shaders verbatim from the original Three.js implementation.

import { useRef, useMemo } from 'react'
import { Canvas, useFrame, useThree } from '@react-three/fiber'
import * as THREE from 'three'
import { useVoiceStore, type VoiceState } from '../../store/voiceStore'

// ---------------------------------------------------------------------------
// GLSL shaders — verbatim from orb.js
// ---------------------------------------------------------------------------

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
`

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
`

// ---------------------------------------------------------------------------
// State → shader uniform mapping (mirrors orb.js STATE_MAP + setStateName)
// ---------------------------------------------------------------------------

const STATE_MAP: Record<VoiceState, number> = {
  idle: 0,
  wake_detected: 1,
  listening: 1,
  processing: 2,
  speaking: 3,
  // error maps to idle visuals
}

interface StateColors {
  colorA: number
  colorB: number
}

function getStateColors(state: VoiceState): StateColors {
  switch (state) {
    case 'speaking':
      return { colorA: 0xff9966, colorB: 0xff4400 }
    case 'processing':
      return { colorA: 0x9966ff, colorB: 0x66ddff }
    default:
      return { colorA: 0x4488ff, colorB: 0xaaddff }
  }
}

// ---------------------------------------------------------------------------
// OrbMesh — the animated icosahedron with shader material
// ---------------------------------------------------------------------------

function OrbMesh() {
  const meshRef = useRef<THREE.Mesh>(null)
  const { camera } = useThree()
  const { state, level } = useVoiceStore()

  const uniforms = useMemo(
    () => ({
      uTime: { value: 0 },
      uLevel: { value: 0 },
      uState: { value: 0 },
      uColorA: { value: new THREE.Color(0x4488ff) },
      uColorB: { value: new THREE.Color(0xaaddff) },
      cameraPos: { value: new THREE.Vector3() },
    }),
    [],
  )

  useFrame((_rootState, delta) => {
    uniforms.uTime.value += delta
    uniforms.uLevel.value = Math.max(0, Math.min(1, level))
    uniforms.uState.value = STATE_MAP[state] ?? 0

    const colors = getStateColors(state)
    uniforms.uColorA.value.setHex(colors.colorA)
    uniforms.uColorB.value.setHex(colors.colorB)

    uniforms.cameraPos.value.copy(camera.position)

    if (meshRef.current) {
      meshRef.current.rotation.y += delta * 0.15
    }
  })

  return (
    <mesh ref={meshRef}>
      <icosahedronGeometry args={[1, 7]} />
      <shaderMaterial
        uniforms={uniforms}
        vertexShader={VERT}
        fragmentShader={FRAG}
        transparent
        side={THREE.DoubleSide}
        depthWrite={false}
      />
    </mesh>
  )
}

// ---------------------------------------------------------------------------
// Scene lighting — matches orb.js exactly
// ---------------------------------------------------------------------------

function OrbLighting() {
  return (
    <>
      <ambientLight color={0x334466} intensity={0.4} />
      <pointLight color={0x88ccff} intensity={1.4} distance={24} position={[2.5, 1.5, 4]} />
      <pointLight color={0xff8866} intensity={0.6} distance={16} position={[-3, -1, 2]} />
    </>
  )
}

// ---------------------------------------------------------------------------
// Adaptive camera — keeps sphere in frustum (mirrors fitCameraDistance)
// ---------------------------------------------------------------------------

const SPHERE_RADIUS = 1.7

function AdaptiveCamera() {
  const { camera, size } = useThree()

  useFrame(() => {
    if (camera instanceof THREE.PerspectiveCamera) {
      const w = size.width
      const h = Math.max(size.height, 1)
      const aspect = w / h
      const vFovRad = (camera.fov * Math.PI) / 180
      const tanHalf = Math.tan(vFovRad / 2)
      const dVert = SPHERE_RADIUS / tanHalf
      const dHoriz = SPHERE_RADIUS / (tanHalf * aspect)
      camera.position.z = Math.max(3.2, dVert, dHoriz)
    }
  })

  return null
}

// ---------------------------------------------------------------------------
// PhaosOrb3D — the exported component with Canvas wrapper
// ---------------------------------------------------------------------------

interface PhaosOrb3DProps {
  className?: string
  style?: React.CSSProperties
}

export function PhaosOrb3D({ className, style }: PhaosOrb3DProps) {
  return (
    <div className={className} style={style}>
      <Canvas
        camera={{ fov: 50, near: 0.1, far: 100, position: [0, 0, 3.4] }}
        gl={{
          antialias: true,
          alpha: true,
          toneMapping: THREE.ACESFilmicToneMapping,
          outputColorSpace: THREE.SRGBColorSpace,
        }}
        style={{ background: 'transparent' }}
      >
        <AdaptiveCamera />
        <OrbLighting />
        <OrbMesh />
      </Canvas>
    </div>
  )
}
