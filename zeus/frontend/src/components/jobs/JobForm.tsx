// zeus/frontend/src/components/jobs/JobForm.tsx
//
// Shared form for create + edit. Handles:
//   - Recurring (cron + tz) vs one-off (run_at datetime) schedule
//   - Built-in executor (dotted path, dropdown from /kronos/executors) vs
//     agent (target name + endpoint)
//   - Params as a JSON-validated textarea
//   - Tags as comma-separated chips
import { useEffect, useMemo, useState } from 'react'

import { kronosApi } from '../../api/kronos'
import { useKronosStore, KRONOS_CATEGORIES } from '../../store/kronosStore'
import type {
  ExecutorInfo,
  JobCategory,
  JobDefinition,
} from '../../types/kronos'
import { CronBuilder, validateCron } from './CronBuilder'
import { CronPreview } from './CronPreview'

interface Props {
  mode: 'create' | 'edit'
  initial?: JobDefinition
  onSaved: (job: JobDefinition) => void
  onCancel: () => void
  onDelete?: () => Promise<void>
}

interface FormState {
  id: string
  name: string
  description: string
  category: JobCategory
  scheduleKind: 'recurring' | 'oneoff'
  cron: string
  timezone: string
  runAtLocal: string // value of <input type="datetime-local">
  dispatch: 'builtin' | 'agent'
  executor: string
  agent: string
  endpoint: string
  paramsJson: string
  safety_policy: string
  timeout_seconds: number
  max_retries: number
  tagsInput: string
  enabled: boolean
}

const POLICIES = [
  'standard',
  'personal',
  'voice',
  'ingest',
  'memory',
  'code_execution',
  'citation_required',
  'default',
]

const baseInput =
  'bg-surface-container-high border border-outline-variant/30 rounded px-3 py-1.5 text-xs ' +
  'font-body text-on-surface outline-none focus:border-primary-container/50 transition-colors'
const baseSelect = baseInput
const baseTextarea = baseInput + ' font-mono resize-y'

function browserTz(): string {
  try {
    return Intl.DateTimeFormat().resolvedOptions().timeZone
  } catch {
    return 'UTC'
  }
}

function slugify(s: string): string {
  return (
    s
      .toLowerCase()
      .replace(/[^a-z0-9]+/g, '-')
      .replace(/^-+|-+$/g, '')
      .slice(0, 60) || 'job'
  )
}

function initialState(initial?: JobDefinition): FormState {
  if (initial) {
    return {
      id: initial.id,
      name: initial.name,
      description: initial.description,
      category: initial.category,
      scheduleKind: initial.schedule.run_at ? 'oneoff' : 'recurring',
      cron: initial.schedule.cron ?? '0 9 * * *',
      timezone: initial.schedule.timezone || browserTz(),
      runAtLocal: initial.schedule.run_at
        ? new Date(initial.schedule.run_at).toISOString().slice(0, 16)
        : '',
      dispatch: initial.agent ? 'agent' : 'builtin',
      executor: initial.executor ?? '',
      agent: initial.agent ?? '',
      endpoint: initial.endpoint || '/run',
      paramsJson: JSON.stringify(initial.params ?? {}, null, 2),
      safety_policy: initial.safety_policy || 'standard',
      timeout_seconds: initial.timeout_seconds,
      max_retries: initial.max_retries,
      tagsInput: initial.tags.join(', '),
      enabled: initial.enabled,
    }
  }
  return {
    id: '',
    name: '',
    description: '',
    category: 'custom',
    scheduleKind: 'recurring',
    cron: '0 9 * * *',
    timezone: browserTz(),
    runAtLocal: '',
    dispatch: 'builtin',
    executor: '',
    agent: '',
    endpoint: '/run',
    paramsJson: '{}',
    safety_policy: 'standard',
    timeout_seconds: 300,
    max_retries: 1,
    tagsInput: '',
    enabled: true,
  }
}

export function JobForm({ mode, initial, onSaved, onCancel, onDelete }: Props) {
  const [state, setState] = useState<FormState>(() => initialState(initial))
  const [executors, setExecutors] = useState<ExecutorInfo[]>([])
  const [submitting, setSubmitting] = useState(false)
  const [deleting, setDeleting] = useState(false)
  const [confirmDelete, setConfirmDelete] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const createJob = useKronosStore((s) => s.createJob)
  const updateJob = useKronosStore((s) => s.updateJob)

  useEffect(() => {
    let cancelled = false
    void kronosApi
      .listExecutors()
      .then((list) => {
        if (!cancelled) setExecutors(list)
      })
      .catch(() => {
        // best-effort; freeform input still works
      })
    return () => {
      cancelled = true
    }
  }, [])

  const update = <K extends keyof FormState>(key: K, value: FormState[K]) =>
    setState((s) => ({ ...s, [key]: value }))

  // Auto-derive id from name on create (only while user hasn't customized).
  const [idTouched, setIdTouched] = useState(false)
  useEffect(() => {
    if (mode === 'create' && !idTouched && state.name) {
      setState((s) => ({ ...s, id: slugify(s.name) }))
    }
  }, [mode, idTouched, state.name])

  const paramsValidation = useMemo(() => {
    if (!state.paramsJson.trim()) return { ok: true, parsed: {} as Record<string, unknown> }
    try {
      const parsed = JSON.parse(state.paramsJson)
      if (typeof parsed !== 'object' || parsed === null || Array.isArray(parsed)) {
        return { ok: false, error: 'Params must be a JSON object' }
      }
      return { ok: true, parsed: parsed as Record<string, unknown> }
    } catch (err) {
      return { ok: false, error: err instanceof Error ? err.message : String(err) }
    }
  }, [state.paramsJson])

  const cronValidation = useMemo(
    () => (state.scheduleKind === 'recurring' ? validateCron(state.cron) : { ok: true }),
    [state.scheduleKind, state.cron],
  )

  const submitDisabled =
    submitting ||
    !state.name.trim() ||
    !state.id.trim() ||
    !paramsValidation.ok ||
    !cronValidation.ok ||
    (state.scheduleKind === 'oneoff' && !state.runAtLocal) ||
    (state.dispatch === 'builtin' && !state.executor.trim()) ||
    (state.dispatch === 'agent' && !state.agent.trim())

  const handleSubmit = async () => {
    setError(null)
    if (submitDisabled) return
    setSubmitting(true)
    try {
      const payload: Partial<JobDefinition> = {
        id: state.id.trim(),
        name: state.name.trim(),
        description: state.description.trim(),
        category: state.category,
        schedule: {
          cron: state.scheduleKind === 'recurring' ? state.cron.trim() : null,
          timezone: state.timezone,
          run_at:
            state.scheduleKind === 'oneoff'
              ? new Date(state.runAtLocal).toISOString()
              : null,
        },
        executor: state.dispatch === 'builtin' ? state.executor.trim() : null,
        agent: state.dispatch === 'agent' ? state.agent.trim() : null,
        endpoint: state.endpoint || '/run',
        params: paramsValidation.ok ? paramsValidation.parsed ?? {} : {},
        safety_policy: state.safety_policy,
        timeout_seconds: Math.max(1, state.timeout_seconds),
        max_retries: Math.max(0, state.max_retries),
        tags: state.tagsInput
          .split(',')
          .map((t) => t.trim())
          .filter(Boolean),
        enabled: state.enabled,
      }
      const result =
        mode === 'create'
          ? await createJob(payload)
          : await updateJob(initial!.id, payload)
      onSaved(result)
    } catch (err) {
      setError(err instanceof Error ? err.message : String(err))
    } finally {
      setSubmitting(false)
    }
  }

  const handleDelete = async () => {
    if (!onDelete) return
    setDeleting(true)
    try {
      await onDelete()
    } catch (err) {
      setError(err instanceof Error ? err.message : String(err))
    } finally {
      setDeleting(false)
    }
  }

  return (
    <div className="space-y-5">
      {error && (
        <div className="rounded border border-error/40 bg-error-container/20 text-error px-3 py-2 text-xs">
          {error}
        </div>
      )}

      {/* Identity */}
      <Section title="Identity">
        <Field label="Name" required>
          <input
            type="text"
            value={state.name}
            onChange={(e) => update('name', e.target.value)}
            className={baseInput}
            placeholder="Daily Briefing"
          />
        </Field>
        <Field label="ID" hint={mode === 'create' ? 'Auto-derived from name' : 'Locked'}>
          <input
            type="text"
            value={state.id}
            disabled={mode === 'edit'}
            onChange={(e) => {
              setIdTouched(true)
              update('id', e.target.value)
            }}
            className={[baseInput, 'font-mono', mode === 'edit' ? 'opacity-60' : ''].join(' ')}
          />
        </Field>
        <Field label="Description">
          <textarea
            value={state.description}
            onChange={(e) => update('description', e.target.value)}
            rows={2}
            className={[baseTextarea, 'font-body'].join(' ')}
          />
        </Field>
        <Field label="Category">
          <select
            value={state.category}
            onChange={(e) => update('category', e.target.value as JobCategory)}
            className={baseSelect}
          >
            {KRONOS_CATEGORIES.map((c) => (
              <option key={c} value={c}>
                {c.replace('_', ' ')}
              </option>
            ))}
          </select>
        </Field>
      </Section>

      {/* Schedule */}
      <Section title="Schedule">
        <RadioGroup
          name="scheduleKind"
          value={state.scheduleKind}
          options={[
            { value: 'recurring', label: 'Recurring (cron)' },
            { value: 'oneoff', label: 'One-off (single fire)' },
          ]}
          onChange={(v) => update('scheduleKind', v as 'recurring' | 'oneoff')}
        />
        {state.scheduleKind === 'recurring' ? (
          <>
            <CronBuilder
              value={state.cron}
              timezone={state.timezone}
              onChange={(v) => update('cron', v)}
              onTimezoneChange={(v) => update('timezone', v)}
            />
            <CronPreview cron={state.cron} timezone={state.timezone} count={5} />
          </>
        ) : (
          <Field label="Fire at" hint={`${state.timezone} — interpreted as your browser TZ`}>
            <input
              type="datetime-local"
              value={state.runAtLocal}
              onChange={(e) => update('runAtLocal', e.target.value)}
              className={baseInput}
            />
          </Field>
        )}
      </Section>

      {/* Dispatch */}
      <Section title="Dispatch">
        <RadioGroup
          name="dispatch"
          value={state.dispatch}
          options={[
            { value: 'builtin', label: 'Built-in Python' },
            { value: 'agent', label: 'Agent (via bus)' },
          ]}
          onChange={(v) => update('dispatch', v as 'builtin' | 'agent')}
        />
        {state.dispatch === 'builtin' ? (
          <Field label="Executor (dotted path)">
            <input
              type="text"
              list="kronos-executor-options"
              value={state.executor}
              onChange={(e) => update('executor', e.target.value)}
              placeholder="zeus.kronos.jobs.health_check.run_service_health"
              className={[baseInput, 'font-mono'].join(' ')}
            />
            <datalist id="kronos-executor-options">
              {executors.map((e) => (
                <option key={e.dotted_path} value={e.dotted_path}>
                  {e.function}
                </option>
              ))}
            </datalist>
          </Field>
        ) : (
          <>
            <Field label="Agent name">
              <input
                type="text"
                value={state.agent}
                onChange={(e) => update('agent', e.target.value)}
                placeholder="iris"
                className={baseInput}
              />
            </Field>
            <Field label="Endpoint">
              <input
                type="text"
                value={state.endpoint}
                onChange={(e) => update('endpoint', e.target.value)}
                placeholder="/run"
                className={[baseInput, 'font-mono'].join(' ')}
              />
            </Field>
          </>
        )}
      </Section>

      {/* Params */}
      <Section title="Params (JSON)">
        <textarea
          value={state.paramsJson}
          onChange={(e) => update('paramsJson', e.target.value)}
          rows={6}
          spellCheck={false}
          className={[
            baseTextarea,
            'w-full',
            paramsValidation.ok ? '' : 'border-error/60',
          ].join(' ')}
        />
        {!paramsValidation.ok && (
          <p className="text-[10px] font-mono text-error">{paramsValidation.error}</p>
        )}
      </Section>

      {/* Runtime */}
      <Section title="Runtime">
        <Field label="Safety policy">
          <input
            type="text"
            list="kronos-policy-options"
            value={state.safety_policy}
            onChange={(e) => update('safety_policy', e.target.value)}
            className={[baseInput, 'font-mono'].join(' ')}
          />
          <datalist id="kronos-policy-options">
            {POLICIES.map((p) => (
              <option key={p} value={p} />
            ))}
          </datalist>
        </Field>
        <div className="grid grid-cols-2 gap-3">
          <Field label="Timeout (s)">
            <input
              type="number"
              min={1}
              value={state.timeout_seconds}
              onChange={(e) => update('timeout_seconds', Number(e.target.value))}
              className={baseInput}
            />
          </Field>
          <Field label="Max retries">
            <input
              type="number"
              min={0}
              value={state.max_retries}
              onChange={(e) => update('max_retries', Number(e.target.value))}
              className={baseInput}
            />
          </Field>
        </div>
        <Field label="Tags" hint="Comma-separated">
          <input
            type="text"
            value={state.tagsInput}
            onChange={(e) => update('tagsInput', e.target.value)}
            placeholder="news, morning"
            className={baseInput}
          />
        </Field>
        <label className="flex items-center gap-2 text-xs font-body text-on-surface mt-1">
          <input
            type="checkbox"
            checked={state.enabled}
            onChange={(e) => update('enabled', e.target.checked)}
            className="accent-primary"
          />
          Enabled on save
        </label>
      </Section>

      {/* Footer actions */}
      <div className="flex items-center justify-between gap-3 pt-4 border-t border-outline-variant/15">
        <button
          onClick={onCancel}
          className="px-3 py-1.5 text-[10px] font-label font-semibold uppercase tracking-widest rounded border border-outline-variant/40 text-on-surface-variant hover:bg-surface-container-high transition-colors"
        >
          Cancel
        </button>
        <div className="flex items-center gap-2">
          <button
            onClick={() => void handleSubmit()}
            disabled={submitDisabled}
            className="px-4 py-1.5 text-[10px] font-label font-semibold uppercase tracking-widest rounded transition-all disabled:opacity-40 disabled:cursor-not-allowed"
            style={{
              backgroundColor: submitDisabled ? 'rgba(60,73,78,0.4)' : '#00d4ff',
              color: submitDisabled ? '#859398' : '#003642',
            }}
          >
            {submitting ? 'Saving...' : mode === 'create' ? 'Create job' : 'Save changes'}
          </button>
        </div>
      </div>

      {/* Danger zone (edit mode only) */}
      {mode === 'edit' && onDelete && (
        <div className="border border-error/30 rounded p-4 mt-6 bg-error-container/10">
          <div className="flex items-start justify-between gap-3">
            <div>
              <h4 className="text-[10px] font-label uppercase tracking-widest text-error">
                Danger zone
              </h4>
              <p className="text-xs font-body text-on-surface-variant mt-1">
                Delete this job and all its run history. Cannot be undone.
              </p>
            </div>
            {confirmDelete ? (
              <div className="flex items-center gap-2">
                <button
                  onClick={() => setConfirmDelete(false)}
                  className="px-3 py-1.5 text-[10px] font-label font-semibold uppercase tracking-widest rounded border border-outline-variant/40 text-on-surface-variant"
                >
                  Cancel
                </button>
                <button
                  onClick={() => void handleDelete()}
                  disabled={deleting}
                  className="px-3 py-1.5 text-[10px] font-label font-semibold uppercase tracking-widest rounded bg-error text-on-error disabled:opacity-50"
                >
                  {deleting ? 'Deleting...' : 'Confirm delete'}
                </button>
              </div>
            ) : (
              <button
                onClick={() => setConfirmDelete(true)}
                className="px-3 py-1.5 text-[10px] font-label font-semibold uppercase tracking-widest rounded border border-error/40 text-error hover:bg-error-container/20"
              >
                Delete
              </button>
            )}
          </div>
        </div>
      )}
    </div>
  )
}

function Section({ title, children }: { title: string; children: React.ReactNode }) {
  return (
    <section className="space-y-2">
      <h3 className="text-[10px] font-label uppercase tracking-widest text-on-surface-variant/60">
        {title}
      </h3>
      <div className="space-y-2">{children}</div>
    </section>
  )
}

function Field({
  label,
  hint,
  required,
  children,
}: {
  label: string
  hint?: string
  required?: boolean
  children: React.ReactNode
}) {
  return (
    <label className="block">
      <div className="flex items-center justify-between mb-1">
        <span className="text-[10px] font-label uppercase tracking-widest text-on-surface-variant/60">
          {label}
          {required && <span className="text-error ml-1">*</span>}
        </span>
        {hint && (
          <span className="text-[10px] font-body text-on-surface-variant/50">{hint}</span>
        )}
      </div>
      {children}
    </label>
  )
}

function RadioGroup<T extends string>({
  name,
  value,
  options,
  onChange,
}: {
  name: string
  value: T
  options: Array<{ value: T; label: string }>
  onChange: (v: T) => void
}) {
  return (
    <div className="flex items-center gap-4">
      {options.map((opt) => (
        <label
          key={opt.value}
          className="flex items-center gap-2 text-xs font-body text-on-surface cursor-pointer"
        >
          <input
            type="radio"
            name={name}
            value={opt.value}
            checked={value === opt.value}
            onChange={() => onChange(opt.value)}
            className="accent-primary"
          />
          {opt.label}
        </label>
      ))}
    </div>
  )
}
