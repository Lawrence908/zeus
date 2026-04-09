// zeus/frontend/src/pages/VizPage.tsx
import { useNavigate } from 'react-router-dom'
import { TopNav } from '../components/layout/TopNav'
import { PhaosOrb } from '../components/orb/PhaosOrb'
import { AudioBars } from '../components/orb/AudioBars'
import { useVoiceStore, type VoiceState } from '../store/voiceStore'
import { useVoiceState } from '../hooks/useVoiceState'

function getStateLabel(state: VoiceState): string {
  switch (state) {
    case 'listening': return 'LISTENING'
    case 'processing': return 'PROCESSING'
    case 'speaking': return 'SPEAKING'
    case 'wake_detected': return 'WAKE DETECTED'
    default: return 'IDLE'
  }
}

function CornerAccent({ position }: { position: 'tl' | 'tr' | 'bl' | 'br' }) {
  const styles: Record<string, string> = {
    tl: 'top-4 left-4 border-t-2 border-l-2',
    tr: 'top-4 right-4 border-t-2 border-r-2',
    bl: 'bottom-4 left-4 border-b-2 border-l-2',
    br: 'bottom-4 right-4 border-b-2 border-r-2',
  }

  return (
    <div
      className={`absolute w-8 h-8 ${styles[position]} border-outline-variant/40`}
    />
  )
}

export function VizPage() {
  const navigate = useNavigate()
  const { state, level } = useVoiceStore()
  useVoiceState()

  const stateLabel = getStateLabel(state)

  return (
    <div className="flex flex-col h-screen bg-black relative overflow-hidden">
      <TopNav />

      {/* Nebula bleed */}
      <div className="absolute inset-0 nebula-bleed pointer-events-none" />

      {/* Corner accents */}
      <CornerAccent position="tl" />
      <CornerAccent position="tr" />
      <CornerAccent position="bl" />
      <CornerAccent position="br" />

      {/* Ghost text */}
      <div
        className="absolute inset-0 flex items-center justify-center pointer-events-none select-none"
        style={{ paddingTop: 52 }}
      >
        <span
          className="font-headline font-black uppercase tracking-[0.2em] text-center"
          style={{
            fontSize: '10vw',
            color: 'rgba(226, 226, 235, 0.04)',
          }}
        >
          {stateLabel}
        </span>
      </div>

      {/* HUD top-left */}
      <div className="absolute top-20 left-8 flex flex-col gap-2">
        <div className="flex flex-col gap-0.5">
          <span className="text-[9px] font-label uppercase tracking-[0.2em] text-on-surface-variant/40">
            Signal Strength
          </span>
          <span className="text-sm font-label font-semibold text-primary">
            —94 dBm
          </span>
        </div>
        <div className="flex flex-col gap-0.5">
          <span className="text-[9px] font-label uppercase tracking-[0.2em] text-on-surface-variant/40">
            Latency
          </span>
          <span className="text-sm font-label font-semibold text-primary">
            12ms
          </span>
        </div>
      </div>

      {/* HUD top-right */}
      <div className="absolute top-20 right-8 flex flex-col items-end gap-2">
        <div className="flex flex-col items-end gap-0.5">
          <span className="text-[9px] font-label uppercase tracking-[0.2em] text-on-surface-variant/40">
            Core Temperature
          </span>
          <span className="text-sm font-label font-semibold text-primary">
            62°C
          </span>
        </div>
        <div className="flex flex-col items-end gap-0.5">
          <span className="text-[9px] font-label uppercase tracking-[0.2em] text-on-surface-variant/40">
            Processing
          </span>
          <span className="text-sm font-label font-semibold text-primary">
            72%
          </span>
        </div>
      </div>

      {/* Center orb */}
      <div
        className="flex-1 flex items-center justify-center relative"
        style={{ paddingTop: 52 }}
      >
        <PhaosOrb size="fullscreen" />
      </div>

      {/* Audio bars bottom */}
      <div className="flex justify-center pb-24 px-8">
        <div className="w-full max-w-md">
          <AudioBars level={level} barCount={32} height={64} />
        </div>
      </div>

      {/* Bottom-right controls */}
      <div className="absolute bottom-8 right-8 flex flex-col items-end gap-2">
        <button
          className="flex items-center gap-1.5 px-3 py-1.5 text-[10px] font-label uppercase tracking-widest text-on-surface-variant border border-outline-variant/30 rounded hover:border-outline-variant transition-colors"
        >
          <span className="material-symbols-outlined" style={{ fontSize: 14 }}>view_in_ar</span>
          WebXR
        </button>
        <button
          onClick={() => navigate('/')}
          className="flex items-center gap-1.5 px-3 py-1.5 text-[10px] font-label uppercase tracking-widest border rounded transition-colors"
          style={{
            color: '#00d4ff',
            borderColor: 'rgba(0, 212, 255, 0.4)',
          }}
        >
          <span className="material-symbols-outlined" style={{ fontSize: 14 }}>close</span>
          Close Portal
        </button>
      </div>
    </div>
  )
}
