// zeus/frontend/src/components/common/AegisBadge.tsx

interface AegisBadgeProps {
  flags?: string[]
}

export function AegisBadge({ flags }: AegisBadgeProps) {
  const hasFlags = flags && flags.length > 0

  if (hasFlags) {
    return (
      <span className="inline-flex items-center gap-1 px-1.5 py-0.5 bg-error-container/30 border border-error/30 rounded text-[10px] font-label font-medium uppercase tracking-wider text-error">
        <span className="material-symbols-outlined" style={{ fontSize: 11 }}>
          warning
        </span>
        {flags.join(', ')}
      </span>
    )
  }

  return (
    <span className="inline-flex items-center gap-1 px-1.5 py-0.5 bg-surface-container-high rounded text-[10px] font-label font-medium uppercase tracking-wider text-primary border border-outline-variant/20">
      <span className="material-symbols-outlined" style={{ fontSize: 11 }}>
        security
      </span>
      Aegis Secure
    </span>
  )
}
