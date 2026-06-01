// zeus/frontend/src/components/jobs/JobFilters.tsx
import { KRONOS_CATEGORIES, useKronosStore } from '../../store/kronosStore'
import type { JobCategory, StatusFilter } from '../../types/kronos'

const STATUS_OPTIONS: Array<{ value: StatusFilter; label: string }> = [
  { value: 'all', label: 'All Status' },
  { value: 'enabled', label: 'Enabled' },
  { value: 'disabled', label: 'Disabled' },
  { value: 'failed', label: 'Last run failed' },
  { value: 'overdue', label: 'Overdue' },
]

const baseSelect =
  'bg-surface-container-high border border-outline-variant/30 rounded px-3 py-1.5 text-xs ' +
  'font-body text-on-surface outline-none focus:border-primary-container/50 transition-colors'

export function JobFilters() {
  const filters = useKronosStore((s) => s.filters)
  const setFilter = useKronosStore((s) => s.setFilter)

  return (
    <div className="flex flex-wrap items-center gap-3">
      <select
        value={filters.category}
        onChange={(e) =>
          setFilter('category', e.target.value as JobCategory | 'all')
        }
        className={baseSelect}
      >
        <option value="all">All Categories</option>
        {KRONOS_CATEGORIES.map((c) => (
          <option key={c} value={c}>
            {c.replace('_', ' ')}
          </option>
        ))}
      </select>

      <select
        value={filters.status}
        onChange={(e) => setFilter('status', e.target.value as StatusFilter)}
        className={baseSelect}
      >
        {STATUS_OPTIONS.map((opt) => (
          <option key={opt.value} value={opt.value}>
            {opt.label}
          </option>
        ))}
      </select>

      <input
        type="search"
        value={filters.search}
        onChange={(e) => setFilter('search', e.target.value)}
        placeholder="Search jobs..."
        className={[baseSelect, 'flex-1 min-w-[180px]'].join(' ')}
      />
    </div>
  )
}
