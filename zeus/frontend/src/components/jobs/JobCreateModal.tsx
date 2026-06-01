// zeus/frontend/src/components/jobs/JobCreateModal.tsx
//
// Centred modal for "+ New Job". Renders JobForm in create mode; on save,
// closes and bubbles the new job's id back so the page can open the drawer.
import { useEffect } from 'react'

import type { JobDefinition } from '../../types/kronos'
import { JobForm } from './JobForm'

interface Props {
  onClose: () => void
  onCreated: (job: JobDefinition) => void
}

export function JobCreateModal({ onClose, onCreated }: Props) {
  // ESC closes
  useEffect(() => {
    const onKey = (e: KeyboardEvent) => {
      if (e.key === 'Escape') onClose()
    }
    window.addEventListener('keydown', onKey)
    return () => window.removeEventListener('keydown', onKey)
  }, [onClose])

  return (
    <>
      <div onClick={onClose} className="fixed inset-0 bg-black/50 z-40" />
      <div className="fixed inset-0 z-50 flex items-start justify-center pt-16 px-4 pointer-events-none">
        <div className="w-full max-w-2xl pointer-events-auto bg-surface-container-low border border-outline-variant/20 rounded shadow-2xl flex flex-col max-h-[85vh]">
          <header className="flex items-center justify-between gap-3 px-5 py-4 border-b border-outline-variant/15">
            <h2 className="font-headline font-bold text-base text-on-surface">
              New scheduled job
            </h2>
            <button
              onClick={onClose}
              className="w-8 h-8 flex items-center justify-center text-on-surface-variant hover:text-on-surface"
              title="Close (Esc)"
            >
              <span className="material-symbols-outlined text-[20px]">close</span>
            </button>
          </header>
          <div className="flex-1 overflow-y-auto custom-scrollbar p-5">
            <JobForm
              mode="create"
              onSaved={(job) => {
                onCreated(job)
              }}
              onCancel={onClose}
            />
          </div>
        </div>
      </div>
    </>
  )
}
