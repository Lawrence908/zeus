// zeus/frontend/src/components/jobs/JobCategoryBadge.tsx
// Coloured pill per JobCategory. Colour map matches docs/kronos-frontend-plan.md.
import type { JobCategory } from '../../types/kronos'

const CATEGORY_CLASSES: Record<JobCategory, string> = {
  briefing: 'bg-blue-500/15 text-blue-300 border-blue-500/30',
  ingest: 'bg-emerald-500/15 text-emerald-300 border-emerald-500/30',
  memory_review: 'bg-purple-500/15 text-purple-300 border-purple-500/30',
  maintenance: 'bg-zinc-500/15 text-zinc-300 border-zinc-500/30',
  research: 'bg-orange-500/15 text-orange-300 border-orange-500/30',
  job_search: 'bg-pink-500/15 text-pink-300 border-pink-500/30',
  health: 'bg-cyan-500/15 text-cyan-300 border-cyan-500/30',
  custom: 'bg-surface-container-high text-on-surface-variant border-outline-variant/30',
}

export function JobCategoryBadge({ category }: { category: JobCategory }) {
  return (
    <span
      className={[
        'inline-block text-[9px] font-label uppercase tracking-widest px-1.5 py-0.5 rounded border',
        CATEGORY_CLASSES[category] ?? CATEGORY_CLASSES.custom,
      ].join(' ')}
    >
      {category.replace('_', ' ')}
    </span>
  )
}
