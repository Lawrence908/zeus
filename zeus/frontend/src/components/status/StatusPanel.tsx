// zeus/frontend/src/components/status/StatusPanel.tsx
import { useEffect, useState } from 'react'
import { PhaosOrb } from '../orb/PhaosOrb'
import { AudioBars } from '../orb/AudioBars'
import { useVoiceStore } from '../../store/voiceStore'
import type { VoiceState } from '../../store/voiceStore'

interface ServiceHealth {
  name: string
  status: string
  latency_ms?: number | null
}

interface StatusData {
  version?: string
  environment?: string
  uptime_seconds?: number
  services?: ServiceHealth[]
}

interface MetricsData {
  avg_latency_ms?: number | null
}

function getStateLabel(state: VoiceState): string {
  switch (state) {
    case 'listening': return 'LISTENING'
    case 'processing': return 'PROCESSING'
    case 'speaking': return 'SPEAKING'
    case 'wake_detected': return 'WAKE DETECTED'
    default: return 'IDLE'
  }
}

interface MetricRowProps {
  label: string
  value: string
  status?: 'ok' | 'warn' | 'error'
}

function MetricRow({ label, value, status = 'ok' }: MetricRowProps) {
  const valueColor = {
    ok: 'text-primary',
    warn: 'text-tertiary',
    error: 'text-error',
  }[status]

  return (
    <div className="flex items-center justify-between py-1.5">
      <span className="text-[10px] font-label uppercase tracking-widest text-on-surface-variant/60">
        {label}
      </span>
      <span className={`text-[11px] font-label font-semibold ${valueColor}`}>
        {value}
      </span>
    </div>
  )
}

export function StatusPanel() {
  const { state, level } = useVoiceStore()
  const [status, setStatus] = useState<StatusData>({})
  const [metrics, setMetrics] = useState<MetricsData>({})

  useEffect(() => {
    const fetchAll = async () => {
      try {
        const [statusRes, metricsRes] = await Promise.all([
          fetch('/status'),
          fetch('/admin/metrics'),
        ])
        if (statusRes.ok) {
          setStatus(await statusRes.json() as StatusData)
        }
        if (metricsRes.ok) {
          setMetrics(await metricsRes.json() as MetricsData)
        }
      } catch {
        // backend not available
      }
    }

    void fetchAll()
    const interval = setInterval(() => void fetchAll(), 15_000)
    return () => clearInterval(interval)
  }, [])

  return (
    <aside className="w-[280px] shrink-0 border-l border-outline-variant/20 flex flex-col bg-surface-container-lowest/30">
      {/* Orb panel */}
      <div className="flex flex-col items-center p-6 border-b border-outline-variant/20 gap-3">
        <PhaosOrb size="compact" />
        <span
          className="text-[10px] font-label tracking-[0.2em] uppercase font-medium"
          style={{ color: state === 'idle' ? '#859398' : '#00d4ff' }}
        >
          {getStateLabel(state)}
        </span>
        <AudioBars level={level} barCount={15} height={20} />
      </div>

      {/* System metrics */}
      <div className="flex-1 p-4 overflow-y-auto custom-scrollbar">
        <div className="mb-3">
          <span className="text-[10px] font-label uppercase tracking-[0.2em] text-on-surface-variant/40">
            System Metrics
          </span>
        </div>

        <div className="divide-y divide-outline-variant/10">
          {(() => {
            const qdrant = status.services?.find((s) => s.name === 'qdrant')
            const qdrantStatus = qdrant?.status?.toUpperCase() ?? '—'
            const coreStatus: 'ok' | 'warn' | 'error' = qdrant
              ? qdrant.status === 'up' ? 'ok' : 'error'
              : 'ok'
            const avgLatency = metrics.avg_latency_ms
            const latencyValue = typeof avgLatency === 'number' ? `${Math.round(avgLatency)}ms` : '—'
            const latencyStatus: 'ok' | 'warn' | 'error' =
              typeof avgLatency === 'number' && avgLatency > 1000 ? 'warn' : 'ok'
            return (
              <>
                <MetricRow label="Core Health" value={qdrantStatus} status={coreStatus} />
                <MetricRow label="Model Env" value={status.environment?.toUpperCase() ?? '—'} status="ok" />
                <MetricRow label="Uptime" value={status.uptime_seconds != null ? `${Math.floor(status.uptime_seconds)}s` : '—'} status="ok" />
                <MetricRow label="Avg Latency" value={latencyValue} status={latencyStatus} />
              </>
            )
          })()}
        </div>

        {/* Neural stream decoration */}
        <div className="mt-4 pt-3 border-t border-outline-variant/10">
          <div
            className="h-16 rounded flex items-center justify-center relative overflow-hidden"
            style={{
              background: 'linear-gradient(135deg, rgba(0,212,255,0.05) 0%, rgba(96,1,209,0.08) 100%)',
              border: '1px solid rgba(60,73,78,0.3)',
            }}
          >
            <div className="flex items-end gap-0.5 h-8">
              {Array.from({ length: 20 }, (_, i) => (
                <div
                  key={i}
                  className="w-1 rounded-sm"
                  style={{
                    height: `${20 + Math.sin(i * 0.8) * 50 + 30}%`,
                    backgroundColor: `rgba(0, 212, 255, ${0.1 + Math.abs(Math.sin(i * 0.5)) * 0.3})`,
                  }}
                />
              ))}
            </div>
            <span className="absolute bottom-1 right-2 text-[9px] font-label uppercase tracking-widest text-on-surface-variant/30">
              Neural Stream
            </span>
          </div>
        </div>
      </div>
    </aside>
  )
}
