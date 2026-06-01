// zeus/frontend/src/components/jobs/JobsTable.tsx
import { useShallow } from 'zustand/react/shallow'

import {
  lastRunByJob,
  nextFireByJob,
  selectFilteredJobs,
  useKronosStore,
} from '../../store/kronosStore'
import type { SortDir, SortKey } from '../../types/kronos'
import { JobsTableRow } from './JobsTableRow'

interface Props {
  onSelect: (id: string) => void
}

const COLUMNS: Array<{ key: SortKey | null; label: string; align?: 'right' }> = [
  { key: 'name', label: 'Name' },
  { key: 'category', label: 'Category' },
  { key: null, label: 'Schedule' },
  { key: 'next_fire', label: 'Next' },
  { key: 'last_run', label: 'Last' },
  { key: 'enabled', label: 'On' },
  { key: null, label: '', align: 'right' },
]

export function JobsTable({ onSelect }: Props) {
  const jobs = useKronosStore(useShallow(selectFilteredJobs))
  const runs = useKronosStore((s) => s.runs)
  const upcoming = useKronosStore((s) => s.upcoming)
  const sort = useKronosStore((s) => s.sort)
  const setSort = useKronosStore((s) => s.setSort)
  const loading = useKronosStore((s) => s.loading)

  const lastByJob = lastRunByJob(runs)
  const nextByJob = nextFireByJob(upcoming)

  const cycleSort = (key: SortKey) => {
    if (sort.key !== key) {
      setSort({ key, dir: 'asc' })
      return
    }
    const dir: SortDir = sort.dir === 'asc' ? 'desc' : 'asc'
    setSort({ key, dir })
  }

  if (jobs.length === 0 && !loading) {
    return (
      <div className="text-center py-16 border border-dashed border-outline-variant/30 rounded">
        <p className="font-headline font-semibold text-on-surface mb-1">No jobs match</p>
        <p className="font-body text-sm text-on-surface-variant">
          Adjust filters or seed jobs in <code className="font-mono text-xs">zeus/data/kronos.yaml</code>.
        </p>
      </div>
    )
  }

  return (
    <div className="border border-outline-variant/20 rounded overflow-hidden">
      <table className="w-full">
        <thead className="bg-surface-container-high">
          <tr>
            {COLUMNS.map((col, i) => (
              <th
                key={i}
                className={[
                  'py-2 px-3 text-[10px] font-label uppercase tracking-widest text-on-surface-variant/70 select-none',
                  col.align === 'right' ? 'text-right' : 'text-left',
                  col.key ? 'cursor-pointer hover:text-on-surface' : '',
                ].join(' ')}
                onClick={col.key ? () => cycleSort(col.key as SortKey) : undefined}
              >
                {col.label}
                {col.key && sort.key === col.key && (
                  <span className="ml-1 text-on-surface">{sort.dir === 'asc' ? '↑' : '↓'}</span>
                )}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {jobs.map((j) => (
            <JobsTableRow
              key={j.id}
              job={j}
              lastRun={lastByJob.get(j.id)}
              nextFire={nextByJob.get(j.id)}
              onSelect={onSelect}
            />
          ))}
        </tbody>
      </table>
    </div>
  )
}
