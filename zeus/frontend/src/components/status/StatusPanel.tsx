// zeus/frontend/src/components/status/StatusPanel.tsx
import { useEffect, useState } from 'react'
import { PhaosOrb } from '../orb/PhaosOrb'

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

interface ActiveModelData {
  provider?: string
  model?: string
  gpu_available?: boolean | null
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

  const isLong = value.length > 14
  if (isLong) {
    return (
      <div className="flex flex-col gap-1 py-1.5">
        <span className="text-[10px] font-label uppercase tracking-widest text-on-surface-variant/60">
          {label}
        </span>
        <span className={`text-[10px] font-label font-semibold break-all ${valueColor}`} title={value}>
          {value}
        </span>
      </div>
    )
  }

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

interface StatusPanelProps {
  // On mobile the panel is an off-canvas drawer; on desktop it is always inline.
  open?: boolean
  onClose?: () => void
}

export function StatusPanel({ open = false, onClose }: StatusPanelProps = {}) {
  const [status, setStatus] = useState<StatusData>({})
  const [metrics, setMetrics] = useState<MetricsData>({})
  const [activeModel, setActiveModel] = useState<ActiveModelData>({})

  useEffect(() => {
    const fetchAll = async () => {
      try {
        const [statusRes, metricsRes, modelRes] = await Promise.all([
          fetch('/status'),
          fetch('/admin/metrics'),
          fetch('/models/active'),
        ])
        if (statusRes.ok) {
          setStatus(await statusRes.json() as StatusData)
        }
        if (metricsRes.ok) {
          setMetrics(await metricsRes.json() as MetricsData)
        }
        if (modelRes.ok) {
          setActiveModel(await modelRes.json() as ActiveModelData)
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
    <>
      {/* Mobile backdrop */}
      {open && (
        <button
          className="md:hidden fixed inset-0 top-[52px] z-30 bg-black/50"
          aria-label="Close status panel"
          onClick={() => onClose?.()}
        />
      )}
      <aside
        className={[
          'fixed top-[52px] bottom-0 right-0 z-40 w-[280px] max-w-[85vw] transform transition-transform duration-200',
          'md:static md:top-0 md:z-auto md:max-w-none md:translate-x-0 md:transition-none',
          'shrink-0 border-l border-outline-variant/20 flex flex-col bg-surface-container-lowest md:bg-surface-container-lowest/30',
          open ? 'translate-x-0' : 'translate-x-full',
        ].join(' ')}
      >
      {/* Mobile close */}
      <div className="md:hidden flex justify-end px-2 pt-2">
        <button
          onClick={() => onClose?.()}
          className="w-9 h-9 flex items-center justify-center text-on-surface-variant hover:text-on-surface"
          aria-label="Close status panel"
        >
          <span className="material-symbols-outlined text-[20px]">close</span>
        </button>
      </div>
      {/* Voice state indicator */}
      <div className="flex flex-col items-center p-6 pt-2 md:pt-6 border-b border-outline-variant/20">
        <PhaosOrb size="compact" />
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
            const modelName = activeModel.model ?? '—'
            const modelStatus: 'ok' | 'warn' | 'error' =
              activeModel.provider === 'ollama' && activeModel.gpu_available === false ? 'warn' : 'ok'
            return (
              <>
                <MetricRow label="Core Health" value={qdrantStatus} status={coreStatus} />
                <MetricRow label="Active Model" value={modelName} status={modelStatus} />
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
    </>
  )
}
