// zeus/frontend/src/components/common/SourceBadge.tsx

interface SourceBadgeProps {
  source: string
}

const SOURCE_CONFIG: Record<string, { icon: string; label: string }> = {
  web: { icon: 'language', label: 'WEB' },
  chat: { icon: 'chat', label: 'CHAT' },
  telegram: { icon: 'send', label: 'TELEGRAM' },
  voice: { icon: 'mic', label: 'VOICE' },
  voice_interact: { icon: 'mic', label: 'VOICE' },
}

const DEFAULT_CONFIG = { icon: 'hub', label: 'UNKNOWN' }

export function SourceBadge({ source }: SourceBadgeProps) {
  const config = SOURCE_CONFIG[source] ?? DEFAULT_CONFIG

  return (
    <span className="inline-flex items-center gap-0.5 px-1.5 py-0.5 bg-surface-container-high rounded text-[10px] font-label font-medium uppercase tracking-wider text-on-surface-variant border border-outline-variant/30">
      <span className="material-symbols-outlined" style={{ fontSize: 11 }}>
        {config.icon}
      </span>
      {config.label}
    </span>
  )
}
