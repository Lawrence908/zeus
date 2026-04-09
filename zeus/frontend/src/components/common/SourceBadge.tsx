// zeus/frontend/src/components/common/SourceBadge.tsx

interface SourceBadgeProps {
  source: 'web' | 'telegram' | 'voice'
}

const SOURCE_CONFIG = {
  web: { icon: 'language', label: 'WEB' },
  telegram: { icon: 'send', label: 'TELEGRAM' },
  voice: { icon: 'mic', label: 'VOICE' },
}

export function SourceBadge({ source }: SourceBadgeProps) {
  const config = SOURCE_CONFIG[source]

  return (
    <span className="inline-flex items-center gap-0.5 px-1.5 py-0.5 bg-surface-container-high rounded text-[10px] font-label font-medium uppercase tracking-wider text-on-surface-variant border border-outline-variant/30">
      <span className="material-symbols-outlined" style={{ fontSize: 11 }}>
        {config.icon}
      </span>
      {config.label}
    </span>
  )
}
