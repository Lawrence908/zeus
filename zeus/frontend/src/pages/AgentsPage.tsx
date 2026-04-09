// zeus/frontend/src/pages/AgentsPage.tsx
import { useEffect, useState, useRef } from 'react'
import { TopNav } from '../components/layout/TopNav'
import { AegisBadge } from '../components/common/AegisBadge'

interface Agent {
  name: string
  model: string
  description?: string
  aegis_policy?: string
  status?: 'idle' | 'running'
}

interface AgentCardProps {
  agent: Agent
  isSelected: boolean
  onSelect: () => void
}

function AgentCard({ agent, isSelected, onSelect }: AgentCardProps) {
  const isRunning = agent.status === 'running'

  return (
    <button
      onClick={onSelect}
      className={[
        'text-left p-4 rounded border transition-all',
        isSelected
          ? 'border-primary-container/60 bg-surface-container-low'
          : 'border-outline-variant/20 bg-surface-container/40 hover:border-outline-variant/50',
      ].join(' ')}
    >
      <div className="flex items-start justify-between gap-2 mb-2">
        <div className="flex items-center gap-2">
          <span
            className={[
              'w-1.5 h-1.5 rounded-full shrink-0',
              isRunning ? 'bg-primary-container animate-pulse' : 'bg-outline',
            ].join(' ')}
          />
          <span className="font-headline font-semibold text-sm text-on-surface">
            {agent.name}
          </span>
        </div>
        <span className="text-[9px] font-label uppercase tracking-widest text-on-surface-variant/50 shrink-0">
          {isRunning ? 'RUNNING' : 'IDLE'}
        </span>
      </div>

      {agent.description && (
        <p className="text-xs font-body text-on-surface-variant mb-3 leading-relaxed">
          {agent.description}
        </p>
      )}

      <div className="flex flex-wrap gap-1.5 items-center">
        <span className="text-[9px] font-label uppercase tracking-wider px-1.5 py-0.5 bg-surface-container-high rounded border border-outline-variant/20 text-on-surface-variant">
          {agent.model}
        </span>
        <AegisBadge />
        {agent.aegis_policy && (
          <span className="text-[9px] font-label text-on-surface-variant/50">
            policy: {agent.aegis_policy}
          </span>
        )}
      </div>
    </button>
  )
}

export function AgentsPage() {
  const [agents, setAgents] = useState<Agent[]>([])
  const [selectedAgent, setSelectedAgent] = useState<string | null>(null)
  const [taskInput, setTaskInput] = useState('')
  const [response, setResponse] = useState('')
  const [isInvoking, setIsInvoking] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const abortRef = useRef<AbortController | null>(null)

  useEffect(() => {
    const fetchAgents = async () => {
      try {
        const res = await fetch('/admin/agents')
        if (res.ok) {
          const data = await res.json() as Agent[]
          setAgents(Array.isArray(data) ? data : [])
        }
      } catch {
        // backend not available
      }
    }
    void fetchAgents()
  }, [])

  const handleInvoke = async () => {
    if (!selectedAgent || !taskInput.trim() || isInvoking) return

    setIsInvoking(true)
    setResponse('')
    setError(null)
    abortRef.current = new AbortController()

    try {
      const res = await fetch('/orchestration/call', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ agent: selectedAgent, task: taskInput }),
        signal: abortRef.current.signal,
      })

      if (!res.ok) throw new Error(`HTTP ${res.status}`)
      if (!res.body) throw new Error('No response body')

      const reader = res.body.getReader()
      const decoder = new TextDecoder()
      let buf = ''

      while (true) {
        const { done, value } = await reader.read()
        if (done) break

        buf += decoder.decode(value, { stream: true })
        const lines = buf.split('\n')
        buf = lines.pop() ?? ''

        for (const line of lines) {
          if (line.startsWith('data: ')) {
            const data = line.slice(6).trim()
            if (data === '[DONE]') break
            if (data) {
              try {
                const parsed = JSON.parse(data) as { token?: string; content?: string }
                setResponse((prev) => prev + (parsed.token ?? parsed.content ?? ''))
              } catch {
                setResponse((prev) => prev + data)
              }
            }
          }
        }
      }
    } catch (err) {
      if ((err as Error).name !== 'AbortError') {
        setError((err as Error).message)
      }
    } finally {
      setIsInvoking(false)
    }
  }

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
              Ruflo-managed task-specific agents. Select an agent and submit a task.
            </p>
          </div>

          {/* Agent grid */}
          {agents.length === 0 ? (
            <div className="text-center py-16 border border-dashed border-outline-variant/30 rounded">
              <span
                className="text-4xl mb-4 block"
                style={{ color: 'rgba(0, 212, 255, 0.3)' }}
              >
                ⚡
              </span>
              <p className="font-headline font-semibold text-on-surface mb-1">
                No Agents Registered
              </p>
              <p className="font-body text-sm text-on-surface-variant">
                Define agents in <code className="font-mono text-xs text-primary-fixed-dim">orchestration/agents/*.yaml</code>
              </p>
            </div>
          ) : (
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3 mb-8">
              {agents.map((agent) => (
                <AgentCard
                  key={agent.name}
                  agent={agent}
                  isSelected={selectedAgent === agent.name}
                  onSelect={() => setSelectedAgent(agent.name)}
                />
              ))}
            </div>
          )}

          {/* Invoke panel */}
          <div className="border border-outline-variant/20 rounded bg-surface-container/30 p-5">
            <h2 className="font-headline font-semibold text-sm text-on-surface mb-4 uppercase tracking-widest">
              Invoke Agent
            </h2>

            {/* Agent selector */}
            <div className="mb-3">
              <label className="block text-[10px] font-label uppercase tracking-widest text-on-surface-variant/60 mb-1">
                Agent
              </label>
              <select
                value={selectedAgent ?? ''}
                onChange={(e) => setSelectedAgent(e.target.value || null)}
                className="w-full bg-surface-container-high border border-outline-variant/30 rounded px-3 py-2 text-sm font-body text-on-surface outline-none focus:border-primary-container/50 transition-colors"
              >
                <option value="">Select agent...</option>
                {agents.map((a) => (
                  <option key={a.name} value={a.name}>{a.name}</option>
                ))}
              </select>
            </div>

            {/* Task input */}
            <div className="mb-3">
              <label className="block text-[10px] font-label uppercase tracking-widest text-on-surface-variant/60 mb-1">
                Task
              </label>
              <textarea
                value={taskInput}
                onChange={(e) => setTaskInput(e.target.value)}
                rows={4}
                placeholder="Describe the task for the agent..."
                className="w-full bg-surface-container-high border border-outline-variant/30 rounded px-3 py-2 text-sm font-body text-on-surface placeholder:text-on-surface-variant/40 outline-none focus:border-primary-container/50 transition-colors resize-none"
              />
            </div>

            {/* Submit */}
            <button
              onClick={() => void handleInvoke()}
              disabled={!selectedAgent || !taskInput.trim() || isInvoking}
              className="flex items-center gap-2 px-4 py-2 text-xs font-label font-semibold uppercase tracking-widest rounded transition-all disabled:opacity-40 disabled:cursor-not-allowed"
              style={{
                backgroundColor: selectedAgent && taskInput.trim() && !isInvoking ? '#00d4ff' : 'rgba(60,73,78,0.4)',
                color: selectedAgent && taskInput.trim() && !isInvoking ? '#003642' : '#859398',
              }}
            >
              {isInvoking && (
                <span
                  className="w-3 h-3 border-2 border-current/30 border-t-current rounded-full inline-block"
                  style={{ animation: 'orb-spin-slow 0.6s linear infinite' }}
                />
              )}
              {isInvoking ? 'Invoking...' : 'Invoke Agent'}
            </button>

            {/* Response stream */}
            {(response || error) && (
              <div className="mt-4 bg-surface-container-lowest border border-outline-variant/20 rounded p-4">
                <div className="flex items-center gap-1.5 mb-3">
                  <span className="material-symbols-outlined text-primary-container" style={{ fontSize: 14 }}>bolt</span>
                  <span className="text-[10px] font-label uppercase tracking-widest text-primary-container">
                    Agent Response
                  </span>
                </div>
                {error ? (
                  <p className="text-xs font-body text-error">{error}</p>
                ) : (
                  <pre className="text-xs font-body text-on-surface whitespace-pre-wrap leading-relaxed">
                    {response}
                    {isInvoking && (
                      <span className="inline-block w-1.5 h-3 bg-primary ml-0.5 animate-pulse" />
                    )}
                  </pre>
                )}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}
