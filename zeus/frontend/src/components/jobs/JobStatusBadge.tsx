// zeus/frontend/src/components/jobs/JobStatusBadge.tsx
// Coloured pill for a JobRun status. Reuses existing M3 Tailwind tokens.
import type { JobStatus } from '../../types/kronos'

interface Props {
  status: JobStatus
  size?: 'sm' | 'xs'
}

function classes(status: JobStatus): { bg: string; text: string; dot: string } {
  switch (status) {
    case 'success':
      return {
        bg: 'bg-primary-container/20 border-primary/30',
        text: 'text-primary',
        dot: 'bg-primary',
      }
    case 'running':
    case 'pending':
      return {
        bg: 'bg-tertiary-container/20 border-tertiary/30',
        text: 'text-tertiary',
        dot: 'bg-tertiary animate-pulse',
      }
    case 'failed':
    case 'timeout':
    case 'lost':
      return {
        bg: 'bg-error-container/20 border-error/30',
        text: 'text-error',
        dot: 'bg-error',
      }
    case 'cancelled':
    default:
      return {
        bg: 'bg-surface-container-high border-outline-variant/30',
        text: 'text-on-surface-variant',
        dot: 'bg-outline',
      }
  }
}

export function JobStatusBadge({ status, size = 'xs' }: Props) {
  const c = classes(status)
  const padding = size === 'sm' ? 'px-2 py-0.5' : 'px-1.5 py-0.5'
  const text = size === 'sm' ? 'text-[10px]' : 'text-[9px]'
  return (
    <span
      className={[
        'inline-flex items-center gap-1.5 font-label uppercase tracking-widest rounded border',
        padding,
        text,
        c.bg,
        c.text,
      ].join(' ')}
    >
      <span className={['w-1.5 h-1.5 rounded-full shrink-0', c.dot].join(' ')} />
      {status}
    </span>
  )
}

export function statusDotClass(status: JobStatus): string {
  return classes(status).dot
}
