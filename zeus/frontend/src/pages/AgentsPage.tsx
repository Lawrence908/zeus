// zeus/frontend/src/pages/AgentsPage.tsx — Olympian agent orchestration panel
import { useEffect, useState, useCallback, useRef } from 'react'
import { TopNav } from '../components/layout/TopNav'
import { AegisBadge } from '../components/common/AegisBadge'

// ---------------------------------------------------------------------------
// Types — mirrors zeus/orchestration/bus.py + runtime.py response shapes
// ---------------------------------------------------------------------------

type AgentStatusValue = 'stopped' | 'starting' | 'running' | 'error'

interface AgentInfo {
  status: AgentStatusValue
  description: string
  model: string
  models: Record<string, string>
  auto_start: boolean
  tools: string[]
  safety_policy: string
  error: string | null
}

interface OrchestrationStatus {
  environment: string
  ruflo_version: string
  active_model?: string
  agents: Record<string, AgentInfo>
}

interface TaskSummary {
  task_id: string
  agent: string
  description: string
  status: string
  elapsed_ms: number | null
  step_count: number
  results_count: number
}

interface StepResult {
  step_name: string
  status: string
  duration_ms: number | null
  data: Record<string, unknown> | null
  error: string | null
}

interface TaskDetail {
  id: string
  agent_name: string
  description: string
  status: string
  elapsed_ms: number | null
  steps: { name: string; endpoint: string; method: string; on_failure: string }[]
  results: StepResult[]
}

// ---------------------------------------------------------------------------
// Status badge helper
// ---------------------------------------------------------------------------

function statusColor(status: AgentStatusValue): { bg: string; text: string; dot: string } {
  switch (status) {
    case 'running':
      return { bg: 'bg-primary-container/20', text: 'text-primary', dot: 'bg-primary animate-pulse' }
    case 'starting':
      return { bg: 'bg-tertiary-container/20', text: 'text-tertiary', dot: 'bg-tertiary animate-pulse' }
    case 'error':
      return { bg: 'bg-error-container/20', text: 'text-error', dot: 'bg-error' }
    default:
      return { bg: 'bg-surface-container-high', text: 'text-on-surface-variant', dot: 'bg-outline' }
  }
}

function taskStatusBadge(status: string): { bg: string; text: string } {
  switch (status) {
    case 'done':
      return { bg: 'bg-primary-container/20 border-primary/30', text: 'text-primary' }
    case 'running':
      return { bg: 'bg-tertiary-container/20 border-tertiary/30', text: 'text-tertiary' }
    case 'failed':
      return { bg: 'bg-error-container/20 border-error/30', text: 'text-error' }
    default:
      return { bg: 'bg-surface-container-high border-outline-variant/30', text: 'text-on-surface-variant' }
  }
}

function stepStatusBadge(status: string): string {
  switch (status) {
    case 'ok':
      return 'text-primary'
    case 'skipped':
      return 'text-on-surface-variant'
    case 'failed':
      return 'text-error'
    default:
      return 'text-on-surface-variant'
  }
}

// ---------------------------------------------------------------------------
// AgentCard
// ---------------------------------------------------------------------------

interface AgentCardProps {
  name: string
  agent: AgentInfo
  environment: string
  isSelected: boolean
  onSelect: () => void
  onToggle: (action: 'start' | 'stop') => void
  isToggling: boolean
}

function AgentCard({ name, agent, isSelected, onSelect, onToggle, isToggling, environment }: AgentCardProps) {
  const sc = statusColor(agent.status)
  const altEnv = environment === 'dev' ? 'prod' : 'dev'
  const altModel = agent.models?.[altEnv]
  const isLocal = !agent.model.includes('claude')
  const tooltip = altModel ? `${altEnv}: ${altModel}` : undefined

  return (
    <div
      onClick={onSelect}
      role="button"
      tabIndex={0}
      onKeyDown={(e) => {
        if (e.key === 'Enter' || e.key === ' ') {
          e.preventDefault()
          onSelect()
        }
      }}
      className={[
        'text-left p-4 rounded border transition-all cursor-pointer',
        isSelected
          ? 'border-primary-container/60 bg-surface-container-low'
          : 'border-outline-variant/20 bg-surface-container/40 hover:border-outline-variant/50',
      ].join(' ')}
    >
      {/* Header row: name + status */}
      <div className="flex items-start justify-between gap-2 mb-2">
        <div className="flex items-center gap-2">
          <span className={['w-1.5 h-1.5 rounded-full shrink-0', sc.dot].join(' ')} />
          <span className="font-headline font-semibold text-sm text-on-surface">{name}</span>
        </div>
        <span
          className={[
            'text-[9px] font-label uppercase tracking-widest shrink-0 px-1.5 py-0.5 rounded border',
            sc.bg,
            sc.text,
            'border-current/20',
          ].join(' ')}
        >
          {agent.status.toUpperCase()}
        </span>
      </div>

      {/* Description */}
      {agent.description && (
        <p className="text-xs font-body text-on-surface-variant mb-3 leading-relaxed">
          {agent.description}
        </p>
      )}

      {/* Error message */}
      {agent.error && (
        <p className="text-xs font-body text-error mb-3 leading-relaxed">{agent.error}</p>
      )}

      {/* Badges row */}
      <div className="flex flex-wrap gap-1.5 items-center mb-3">
        <span
          className={[
            'text-[9px] font-label uppercase tracking-wider px-1.5 py-0.5 rounded border',
            isLocal
              ? 'bg-primary-container/20 border-primary/30 text-primary'
              : 'bg-tertiary-container/20 border-tertiary/30 text-tertiary',
          ].join(' ')}
          title={tooltip}
        >
          {isLocal ? '⬡ ' : '☁ '}{agent.model || 'no model'}
        </span>
        <AegisBadge />
        <span className="text-[9px] font-label text-on-surface-variant/50">
          policy: {agent.safety_policy}
        </span>
      </div>

      {/* Tools */}
      {agent.tools.length > 0 && (
        <div className="flex flex-wrap gap-1 mb-3">
          {agent.tools.map((tool) => (
            <span
              key={tool}
              className="text-[9px] font-mono px-1.5 py-0.5 bg-surface-container-highest/60 rounded text-on-surface-variant/70"
            >
              {tool}
            </span>
          ))}
        </div>
      )}

      {/* Start/stop toggle */}
      <div className="flex items-center justify-end">
        {agent.status === 'running' ? (
          <button
            onClick={(e) => {
              e.stopPropagation()
              onToggle('stop')
            }}
            disabled={isToggling}
            className="px-3 py-1 text-[10px] font-label font-semibold uppercase tracking-widest rounded border border-error/30 text-error hover:bg-error-container/20 transition-colors disabled:opacity-40"
          >
            {isToggling ? 'Stopping...' : 'Stop'}
          </button>
        ) : agent.status !== 'error' ? (
          <button
            onClick={(e) => {
              e.stopPropagation()
              onToggle('start')
            }}
            disabled={isToggling}
            className="px-3 py-1 text-[10px] font-label font-semibold uppercase tracking-widest rounded border border-primary/30 text-primary hover:bg-primary-container/20 transition-colors disabled:opacity-40"
          >
            {isToggling ? 'Starting...' : 'Start'}
          </button>
        ) : null}
      </div>
    </div>
  )
}

// ---------------------------------------------------------------------------
// TaskResultView — collapsible step results for a single task
// ---------------------------------------------------------------------------

function TaskResultView({ task }: { task: TaskDetail }) {
  const [expanded, setExpanded] = useState<Record<number, boolean>>({})

  const toggle = (idx: number) =>
    setExpanded((prev) => ({ ...prev, [idx]: !prev[idx] }))

  const tsb = taskStatusBadge(task.status)

  return (
    <div className="border border-outline-variant/20 rounded bg-surface-container/30 p-4">
      <div className="flex items-center justify-between gap-3 mb-3">
        <div className="flex items-center gap-2">
          <span className="font-headline font-semibold text-sm text-on-surface">
            Task: {task.agent_name}
          </span>
          <span
            className={[
              'text-[9px] font-label uppercase tracking-widest px-1.5 py-0.5 rounded border',
              tsb.bg,
              tsb.text,
            ].join(' ')}
          >
            {task.status}
          </span>
        </div>
        {task.elapsed_ms !== null && (
          <span className="text-[10px] font-mono text-on-surface-variant/50">
            {(task.elapsed_ms / 1000).toFixed(1)}s
          </span>
        )}
      </div>

      {task.description && (
        <p className="text-xs font-body text-on-surface-variant mb-3">{task.description}</p>
      )}

      {/* Step results */}
      {task.results.length === 0 && task.status === 'running' && (
        <p className="text-xs text-on-surface-variant/60 italic">Executing steps...</p>
      )}

      <div className="space-y-1">
        {task.results.map((result, idx) => {
          const isOpen = expanded[idx] ?? false
          return (
            <div
              key={idx}
              className="border border-outline-variant/15 rounded bg-surface-container-lowest/50"
            >
              <button
                onClick={() => toggle(idx)}
                className="w-full flex items-center justify-between gap-2 px-3 py-2 text-left"
              >
                <div className="flex items-center gap-2">
                  <span className={['text-xs font-label font-semibold uppercase', stepStatusBadge(result.status)].join(' ')}>
                    {result.status}
                  </span>
                  <span className="text-xs font-body text-on-surface">
                    {result.step_name}
                  </span>
                </div>
                <div className="flex items-center gap-2">
                  {result.duration_ms !== null && (
                    <span className="text-[10px] font-mono text-on-surface-variant/50">
                      {result.duration_ms.toFixed(0)}ms
                    </span>
                  )}
                  <span
                    className="material-symbols-outlined text-on-surface-variant/40 transition-transform"
                    style={{ fontSize: 16, transform: isOpen ? 'rotate(180deg)' : undefined }}
                  >
                    expand_more
                  </span>
                </div>
              </button>
              {isOpen && (
                <div className="px-3 pb-3 text-xs font-mono">
                  {result.error ? (
                    <pre className="text-error whitespace-pre-wrap">{result.error}</pre>
                  ) : result.data ? (
                    <pre className="text-on-surface-variant whitespace-pre-wrap">
                      {JSON.stringify(result.data, null, 2)}
                    </pre>
                  ) : (
                    <span className="text-on-surface-variant/40 italic">No data</span>
                  )}
                </div>
              )}
            </div>
          )
        })}
      </div>
    </div>
  )
}

// ---------------------------------------------------------------------------
// RecentTasksList
// ---------------------------------------------------------------------------

function RecentTasksList({
  tasks,
  onSelect,
  selectedTaskId,
}: {
  tasks: TaskSummary[]
  onSelect: (taskId: string) => void
  selectedTaskId: string | null
}) {
  if (tasks.length === 0) {
    return (
      <p className="text-xs text-on-surface-variant/60 py-4 text-center">No recent tasks.</p>
    )
  }

  return (
    <div className="space-y-1">
      {tasks.map((t) => {
        const tsb = taskStatusBadge(t.status)
        return (
          <button
            key={t.task_id}
            onClick={() => onSelect(t.task_id)}
            className={[
              'w-full flex items-center justify-between gap-3 px-3 py-2 rounded text-left transition-colors',
              selectedTaskId === t.task_id
                ? 'bg-surface-container-low border border-primary-container/40'
                : 'hover:bg-surface-container/60 border border-transparent',
            ].join(' ')}
          >
            <div className="flex items-center gap-2 min-w-0">
              <span
                className={[
                  'text-[9px] font-label uppercase tracking-widest px-1.5 py-0.5 rounded border shrink-0',
                  tsb.bg,
                  tsb.text,
                ].join(' ')}
              >
                {t.status}
              </span>
              <span className="text-xs font-body text-on-surface truncate">
                {t.agent} {t.description ? `— ${t.description}` : ''}
              </span>
            </div>
            <div className="flex items-center gap-2 shrink-0">
              <span className="text-[10px] font-mono text-on-surface-variant/50">
                {t.results_count}/{t.step_count} steps
              </span>
              {t.elapsed_ms !== null && (
                <span className="text-[10px] font-mono text-on-surface-variant/50">
                  {(t.elapsed_ms / 1000).toFixed(1)}s
                </span>
              )}
            </div>
          </button>
        )
      })}
    </div>
  )
}

// ---------------------------------------------------------------------------
// TaskDispatchPanel
// ---------------------------------------------------------------------------

function TaskDispatchPanel({
  agents,
  selectedAgent,
  onSelectAgent,
  onTaskCreated,
}: {
  agents: Record<string, AgentInfo>
  selectedAgent: string | null
  onSelectAgent: (name: string | null) => void
  onTaskCreated: (taskId: string) => void
}) {
  const [description, setDescription] = useState('')
  const [stepsJson, setStepsJson] = useState('')
  const [showSteps, setShowSteps] = useState(false)
  const [submitting, setSubmitting] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const agentNames = Object.keys(agents)

  const handleSubmit = async () => {
    if (!selectedAgent || submitting) return

    setSubmitting(true)
    setError(null)

    try {
      let steps: unknown = null
      if (showSteps && stepsJson.trim()) {
        try {
          steps = JSON.parse(stepsJson)
        } catch {
          setError('Invalid JSON in steps field')
          setSubmitting(false)
          return
        }
      }

      const res = await fetch('/orchestration/tasks', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          agent: selectedAgent,
          task_description: description,
          ...(steps !== null ? { steps } : {}),
        }),
      })

      if (!res.ok) {
        const body = await res.json().catch(() => ({})) as { detail?: string }
        throw new Error(body.detail ?? `HTTP ${res.status}`)
      }

      const data = (await res.json()) as { task_id: string }
      onTaskCreated(data.task_id)
      setDescription('')
      setStepsJson('')
    } catch (err) {
      setError(err instanceof Error ? err.message : String(err))
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <div className="border border-outline-variant/20 rounded bg-surface-container/30 p-5">
      <h2 className="font-headline font-semibold text-sm text-on-surface mb-4 uppercase tracking-widest">
        Dispatch Task
      </h2>

      {error && (
        <div className="mb-3 rounded border border-error/40 bg-error-container/20 text-error px-3 py-2 text-xs">
          {error}
        </div>
      )}

      {/* Agent selector */}
      <div className="mb-3">
        <label className="block text-[10px] font-label uppercase tracking-widest text-on-surface-variant/60 mb-1">
          Agent
        </label>
        <select
          value={selectedAgent ?? ''}
          onChange={(e) => onSelectAgent(e.target.value || null)}
          className="w-full bg-surface-container-high border border-outline-variant/30 rounded px-3 py-2 text-sm font-body text-on-surface outline-none focus:border-primary-container/50 transition-colors"
        >
          <option value="">Select agent...</option>
          {agentNames.map((a) => (
            <option key={a} value={a}>
              {a}
            </option>
          ))}
        </select>
      </div>

      {/* Task description */}
      <div className="mb-3">
        <label className="block text-[10px] font-label uppercase tracking-widest text-on-surface-variant/60 mb-1">
          Task Description
        </label>
        <textarea
          value={description}
          onChange={(e) => setDescription(e.target.value)}
          rows={3}
          placeholder="Describe what the agent should do..."
          className="w-full bg-surface-container-high border border-outline-variant/30 rounded px-3 py-2 text-sm font-body text-on-surface placeholder:text-on-surface-variant/40 outline-none focus:border-primary-container/50 transition-colors resize-none"
        />
      </div>

      {/* Optional steps JSON */}
      <div className="mb-4">
        <button
          onClick={() => setShowSteps(!showSteps)}
          className="flex items-center gap-1 text-[10px] font-label uppercase tracking-widest text-on-surface-variant/60 hover:text-on-surface-variant transition-colors"
        >
          <span
            className="material-symbols-outlined transition-transform"
            style={{ fontSize: 14, transform: showSteps ? 'rotate(180deg)' : undefined }}
          >
            expand_more
          </span>
          Custom Steps (JSON)
        </button>
        {showSteps && (
          <textarea
            value={stepsJson}
            onChange={(e) => setStepsJson(e.target.value)}
            rows={6}
            placeholder='[{"name": "step1", "endpoint": "/...", "method": "POST", "on_failure": "abort"}]'
            className="mt-2 w-full bg-surface-container-high border border-outline-variant/30 rounded px-3 py-2 text-xs font-mono text-on-surface placeholder:text-on-surface-variant/40 outline-none focus:border-primary-container/50 transition-colors resize-none"
          />
        )}
      </div>

      {/* Submit */}
      <button
        onClick={() => void handleSubmit()}
        disabled={!selectedAgent || submitting}
        className="flex items-center gap-2 px-4 py-2 text-xs font-label font-semibold uppercase tracking-widest rounded transition-all disabled:opacity-40 disabled:cursor-not-allowed"
        style={{
          backgroundColor: selectedAgent && !submitting ? '#00d4ff' : 'rgba(60,73,78,0.4)',
          color: selectedAgent && !submitting ? '#003642' : '#859398',
        }}
      >
        {submitting && (
          <span
            className="w-3 h-3 border-2 border-current/30 border-t-current rounded-full inline-block"
            style={{ animation: 'orb-spin-slow 0.6s linear infinite' }}
          />
        )}
        {submitting ? 'Dispatching...' : 'Dispatch Task'}
      </button>
    </div>
  )
}

// ---------------------------------------------------------------------------
// AgentsPage — main page component
// ---------------------------------------------------------------------------

export function AgentsPage() {
  const [status, setStatus] = useState<OrchestrationStatus | null>(null)
  const [selectedAgent, setSelectedAgent] = useState<string | null>(null)
  const [togglingAgent, setTogglingAgent] = useState<string | null>(null)
  const [fetchError, setFetchError] = useState<string | null>(null)

  // Task state
  const [recentTasks, setRecentTasks] = useState<TaskSummary[]>([])
  const [pollingTaskId, setPollingTaskId] = useState<string | null>(null)
  const [polledTask, setPolledTask] = useState<TaskDetail | null>(null)
  const [selectedViewTaskId, setSelectedViewTaskId] = useState<string | null>(null)
  const [viewedTask, setViewedTask] = useState<TaskDetail | null>(null)

  const pollRef = useRef<ReturnType<typeof setInterval> | null>(null)

  // ----- Fetch orchestration status -----
  const fetchStatus = useCallback(async () => {
    try {
      const res = await fetch('/orchestration/status')
      if (!res.ok) throw new Error(`HTTP ${res.status}`)
      const data = (await res.json()) as OrchestrationStatus
      setStatus(data)
      setFetchError(null)
    } catch (err) {
      setFetchError(err instanceof Error ? err.message : String(err))
    }
  }, [])

  // ----- Fetch recent tasks -----
  const fetchTasks = useCallback(async () => {
    try {
      const res = await fetch('/orchestration/tasks')
      if (res.ok) {
        const data = (await res.json()) as TaskSummary[]
        setRecentTasks(Array.isArray(data) ? data : [])
      }
    } catch {
      // ignore
    }
  }, [])

  // Initial load
  useEffect(() => {
    void fetchStatus()
    void fetchTasks()
  }, [fetchStatus, fetchTasks])

  // ----- Poll active task every 2s -----
  useEffect(() => {
    if (!pollingTaskId) return

    const poll = async () => {
      try {
        const res = await fetch(`/orchestration/tasks/${pollingTaskId}`)
        if (!res.ok) return
        const data = (await res.json()) as TaskDetail
        setPolledTask(data)

        // Also refresh recent tasks list
        void fetchTasks()

        if (data.status === 'done' || data.status === 'failed') {
          setPollingTaskId(null)
        }
      } catch {
        // ignore poll errors
      }
    }

    void poll()
    pollRef.current = setInterval(() => void poll(), 2000)

    return () => {
      if (pollRef.current) clearInterval(pollRef.current)
    }
  }, [pollingTaskId, fetchTasks])

  // ----- Fetch a specific task for viewing -----
  useEffect(() => {
    if (!selectedViewTaskId) {
      setViewedTask(null)
      return
    }
    const fetchTask = async () => {
      try {
        const res = await fetch(`/orchestration/tasks/${selectedViewTaskId}`)
        if (res.ok) {
          const data = (await res.json()) as TaskDetail
          setViewedTask(data)
        }
      } catch {
        // ignore
      }
    }
    void fetchTask()
  }, [selectedViewTaskId])

  // ----- Agent start/stop -----
  const handleToggleAgent = useCallback(
    async (name: string, action: 'start' | 'stop') => {
      setTogglingAgent(name)
      try {
        const res = await fetch(`/orchestration/agents/${name}/action`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ action }),
        })
        if (!res.ok) {
          const body = await res.json().catch(() => ({})) as { detail?: string }
          throw new Error(body.detail ?? `HTTP ${res.status}`)
        }
        // Refresh status after action
        await fetchStatus()
      } catch (err) {
        setFetchError(err instanceof Error ? err.message : String(err))
      } finally {
        setTogglingAgent(null)
      }
    },
    [fetchStatus],
  )

  // ----- Task created callback -----
  const handleTaskCreated = useCallback(
    (taskId: string) => {
      setPollingTaskId(taskId)
      setPolledTask(null)
      setSelectedViewTaskId(null)
      setViewedTask(null)
      void fetchTasks()
    },
    [fetchTasks],
  )

  // ----- Select a recent task for viewing -----
  const handleSelectRecentTask = useCallback((taskId: string) => {
    setSelectedViewTaskId((prev) => (prev === taskId ? null : taskId))
  }, [])

  const agents = status?.agents ?? {}
  const agentNames = Object.keys(agents)
  const activeTask = polledTask ?? viewedTask

  return (
    <div className="flex flex-col h-screen bg-background">
      <TopNav />

      <div className="flex-1 overflow-y-auto custom-scrollbar pt-[52px]">
        <div className="max-w-6xl mx-auto px-6 py-8">
          {/* Header */}
          <div className="mb-8">
            <h1 className="font-headline font-bold text-2xl text-on-surface mb-1">
              Olympian Agents
            </h1>
            <p className="font-body text-sm text-on-surface-variant">
              Ruflo-managed task-specific agents. Monitor status, start/stop agents, and dispatch tasks.
            </p>
            {status && (
              <div className="flex items-center gap-3 mt-2">
                <span
                  className={[
                    'text-[10px] font-label uppercase tracking-widest px-2 py-1 rounded border',
                    status.environment === 'prod'
                      ? 'bg-primary-container/20 border-primary/30 text-primary'
                      : 'bg-tertiary-container/20 border-tertiary/30 text-tertiary',
                  ].join(' ')}
                >
                  {status.environment === 'prod' ? '⬡ local' : '☁ cloud'} / {status.environment}
                </span>
                <span className="text-[10px] font-label text-on-surface-variant/40">
                  ruflo {status.ruflo_version}
                </span>
              </div>
            )}
          </div>

          {/* Error banner */}
          {fetchError && (
            <div className="mb-6 rounded border border-error/40 bg-error-container/20 text-error px-3 py-2 text-sm flex items-center justify-between">
              <span>{fetchError}</span>
              <button
                onClick={() => {
                  setFetchError(null)
                  void fetchStatus()
                }}
                className="text-xs font-label underline ml-4"
              >
                Retry
              </button>
            </div>
          )}

          {/* Agent grid */}
          {agentNames.length === 0 ? (
            <div className="text-center py-16 border border-dashed border-outline-variant/30 rounded mb-8">
              <span
                className="text-4xl mb-4 block"
                style={{ color: 'rgba(0, 212, 255, 0.3)' }}
              >
                &#9889;
              </span>
              <p className="font-headline font-semibold text-on-surface mb-1">
                No Agents Registered
              </p>
              <p className="font-body text-sm text-on-surface-variant">
                Define agents in{' '}
                <code className="font-mono text-xs text-primary-fixed-dim">
                  orchestration/agents/*.yaml
                </code>{' '}
                and ensure the runtime is initialised.
              </p>
            </div>
          ) : (
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3 mb-8">
              {agentNames.map((name) => (
                <AgentCard
                  key={name}
                  name={name}
                  agent={agents[name]}
                  environment={status?.environment ?? 'dev'}
                  isSelected={selectedAgent === name}
                  onSelect={() => setSelectedAgent(name)}
                  onToggle={(action) => void handleToggleAgent(name, action)}
                  isToggling={togglingAgent === name}
                />
              ))}
            </div>
          )}

          {/* Task dispatch panel */}
          <div className="mb-8">
            <TaskDispatchPanel
              agents={agents}
              selectedAgent={selectedAgent}
              onSelectAgent={setSelectedAgent}
              onTaskCreated={handleTaskCreated}
            />
          </div>

          {/* Active / viewed task result */}
          {activeTask && (
            <div className="mb-8">
              <h2 className="font-headline font-semibold text-sm text-on-surface mb-3 uppercase tracking-widest">
                {polledTask ? 'Active Task' : 'Task Detail'}
              </h2>
              <TaskResultView task={activeTask} />
            </div>
          )}

          {/* Recent tasks list */}
          <div className="border border-outline-variant/20 rounded bg-surface-container/30 p-5">
            <div className="flex items-center justify-between gap-3 mb-3">
              <h2 className="font-headline font-semibold text-sm text-on-surface uppercase tracking-widest">
                Recent Tasks
              </h2>
              <button
                onClick={() => void fetchTasks()}
                className="px-3 py-1.5 rounded text-xs font-label border border-outline-variant/40 hover:border-primary-container/40 transition-colors"
              >
                Refresh
              </button>
            </div>
            <RecentTasksList
              tasks={recentTasks}
              onSelect={handleSelectRecentTask}
              selectedTaskId={selectedViewTaskId}
            />
          </div>
        </div>
      </div>
    </div>
  )
}
