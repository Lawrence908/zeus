<script lang="ts">
  import { onDestroy, onMount, tick } from 'svelte';
  import type { AppInstance } from '$lib/wm/tree';
  import {
    chatStream,
    createSession,
    deleteSession,
    listSessions,
    sessionMessages,
    type ChatSessionSummary
  } from '$lib/api/chat';
  import { getActiveModel, listModels, setActiveModel } from '$lib/api/models';
  import { notify } from '$lib/notify/store';
  import { readCodeClip, renderMarkdown } from '$lib/markdown';
  import { getChatSession, setChatSession, type ChatMsg as Msg, type ToolCall } from './chat-sessions';
  import { voiceTurns, type VoiceTurn } from '$lib/voice/store';

  export let app: AppInstance;

  // Rehydrate from the module-scoped registry so a float ↔ tile toggle (which
  // unmounts the component) keeps the conversation intact.
  const session = getChatSession(app.instanceId);
  let messages: Msg[] = session.messages;
  let sessionId: string | null = session.sessionId;

  // Mirror writes back to the registry on every change.
  $: setChatSession(app.instanceId, { messages, sessionId });

  let input = '';
  let sending = false;
  let viewport: HTMLDivElement;
  let copied: number | null = null;

  // ── session drawer + model picker ──
  let drawerOpen = false;
  let sessionList: ChatSessionSummary[] = [];
  let sessionsLoading = false;
  let models: string[] = [];
  let activeModel = '';
  let modelProvider = '';

  async function toggleDrawer() {
    drawerOpen = !drawerOpen;
    if (drawerOpen) await refreshSessions();
  }

  async function refreshSessions() {
    sessionsLoading = true;
    try {
      sessionList = (await listSessions(25)).sessions;
    } catch {
      sessionList = [];
    } finally {
      sessionsLoading = false;
    }
  }

  async function pickSession(id: string) {
    try {
      const res = await sessionMessages(id);
      messages = res.messages
        .filter((m) => m.content)
        .map((m) => ({ role: m.role, content: m.content }));
      sessionId = id;
      drawerOpen = false;
      await tick();
      scrollDown();
    } catch (e) {
      notify({ title: 'Load failed', body: String(e).slice(0, 140), kind: 'err' });
    }
  }

  async function newSession() {
    try {
      const s = await createSession();
      sessionId = s.id;
      messages = [];
      drawerOpen = false;
    } catch (e) {
      notify({ title: 'New session failed', body: String(e).slice(0, 140), kind: 'err' });
    }
  }

  async function removeSession(id: string, ev: Event) {
    ev.stopPropagation();
    try {
      await deleteSession(id);
      if (sessionId === id) {
        sessionId = null;
        messages = [];
      }
      await refreshSessions();
    } catch (e) {
      notify({ title: 'Delete failed', body: String(e).slice(0, 140), kind: 'err' });
    }
  }

  async function loadModels() {
    try {
      const [active, list] = await Promise.all([getActiveModel(), listModels()]);
      activeModel = active.model;
      modelProvider = active.provider;
      models = list.models.map((m) => m.name);
      if (activeModel && !models.includes(activeModel)) models = [activeModel, ...models];
    } catch {
      /* model switching unavailable (e.g. Claude dev mode without list) */
    }
  }

  async function onModelChange(ev: Event) {
    const next = (ev.target as HTMLSelectElement).value;
    if (!next || next === activeModel) return;
    const prev = activeModel;
    activeModel = next;
    try {
      await setActiveModel(next);
      notify({ title: 'Model', body: next, kind: 'ok', ttlMs: 2000 });
    } catch (e) {
      activeModel = prev;
      notify({ title: 'Model switch failed', body: String(e).slice(0, 140), kind: 'err' });
    }
  }

  function relTime(epochSec: number): string {
    const d = Date.now() / 1000 - epochSec;
    if (d < 60) return 'now';
    if (d < 3600) return `${Math.floor(d / 60)}m`;
    if (d < 86400) return `${Math.floor(d / 3600)}h`;
    return `${Math.floor(d / 86400)}d`;
  }

  async function send() {
    const text = input.trim();
    if (!text || sending) return;
    sending = true;
    input = '';
    messages = [
      ...messages,
      { role: 'user', content: text },
      { role: 'assistant', content: '', phase: 'queued' }
    ];
    await tick();
    scrollDown();

    try {
      await chatStream({
        message: text,
        sessionId,
        onPhase: (phase) => {
          messages[messages.length - 1].phase = phase;
          messages = messages;
        },
        onToken: (chunk) => {
          messages[messages.length - 1].content += chunk;
          messages[messages.length - 1].phase = undefined;
          messages = messages;
          scrollDown();
        },
        onDone: (meta) => {
          if (meta.session_id) sessionId = meta.session_id;
          // The chat backend may include tool_calls + model_used in done frame.
          // We accept whatever fields show up.
          const m = messages[messages.length - 1];
          const anyMeta = meta as Record<string, unknown>;
          if (Array.isArray(anyMeta.tool_calls)) m.toolCalls = anyMeta.tool_calls as ToolCall[];
          if (typeof anyMeta.model_used === 'string') m.model = anyMeta.model_used;
          if (typeof anyMeta.latency_ms === 'number') m.latency_ms = anyMeta.latency_ms;
          messages = messages;
        },
        onError: (detail) => {
          messages[messages.length - 1].content = `**[error]** ${detail}`;
          messages = messages;
          notify({ title: 'Chat error', body: detail.slice(0, 140), kind: 'err' });
        }
      });
    } finally {
      sending = false;
    }
  }

  function scrollDown() {
    if (!viewport) return;
    viewport.scrollTop = viewport.scrollHeight;
  }

  function onKey(ev: KeyboardEvent) {
    if (ev.key === 'Enter' && !ev.shiftKey) {
      ev.preventDefault();
      send();
    }
  }

  function copyMessage(i: number) {
    const text = messages[i]?.content ?? '';
    navigator.clipboard?.writeText(text).then(
      () => {
        copied = i;
        setTimeout(() => (copied = null), 1200);
      },
      () => notify({ title: 'Copy failed', kind: 'warn', ttlMs: 1500 })
    );
  }

  // Delegate clicks for the per-code-block copy buttons that `renderMarkdown`
  // injects. Walking up from the event target lets us catch clicks on the
  // button label too without explicit Svelte bindings for every block.
  function onChatClick(ev: MouseEvent) {
    const t = ev.target as HTMLElement | null;
    if (!t) return;
    const btn = t.closest('.code-copy-btn') as HTMLElement | null;
    if (!btn) return;
    const raw = readCodeClip(btn);
    if (raw === null) return;
    navigator.clipboard?.writeText(raw).then(
      () => {
        const orig = btn.textContent;
        btn.textContent = 'Copied';
        btn.classList.add('copied');
        setTimeout(() => {
          btn.textContent = orig ?? 'Copy';
          btn.classList.remove('copied');
        }, 1200);
      },
      () => notify({ title: 'Copy failed', kind: 'warn', ttlMs: 1500 })
    );
  }

  function stringifyArg(v: unknown): string {
    if (v === undefined || v === null) return '';
    if (typeof v === 'string') return v;
    try {
      return JSON.stringify(v, null, 2);
    } catch {
      return String(v);
    }
  }

  // Absorb voice turns into this chat window. Every currently-known turn at
  // mount time is treated as already-seen so a freshly opened Chat doesn't
  // retroactively backfill voice history; only new turns get appended.
  const seenTurns = new Set<string>();
  let voiceBaseline = false;
  const unsubVoice = voiceTurns.subscribe((xs) => {
    if (!voiceBaseline) {
      for (const t of xs) seenTurns.add(t.id);
      voiceBaseline = true;
      return;
    }
    // xs is newest-first; walk oldest→newest so appends land in order.
    for (let i = xs.length - 1; i >= 0; i--) {
      const t = xs[i];
      if (seenTurns.has(t.id)) continue;
      seenTurns.add(t.id);
      appendVoiceTurn(t);
    }
  });

  function appendVoiceTurn(t: VoiceTurn) {
    const added: Msg[] = [];
    if (t.transcript) added.push({ role: 'user', content: t.transcript });
    if (t.reply) {
      added.push({
        role: 'assistant',
        content: t.reply,
        model: t.model,
        latency_ms: undefined
      });
    }
    if (!added.length) return;
    messages = [...messages, ...added];
    if (t.sessionId && !sessionId) sessionId = t.sessionId;
    tick().then(scrollDown);
  }

  onMount(() => {
    void loadModels();
  });

  onDestroy(() => {
    unsubVoice();
  });
</script>

<div class="h-full w-full flex flex-col relative" on:click={onChatClick} role="presentation">
  <div class="flex items-center gap-2 px-2 py-1 border-b border-border/30 text-xs font-mono">
    <button
      class="px-1.5 py-0.5 rounded text-muted hover:text-fg hover:bg-surface2/60"
      class:text-accent={drawerOpen}
      on:click={toggleDrawer}
      title="Sessions"
    >☰</button>
    <button
      class="px-1.5 py-0.5 rounded text-muted hover:text-fg hover:bg-surface2/60"
      on:click={newSession}
      title="New session"
    >+</button>
    <span class="text-muted/60 truncate flex-1">
      {sessionId ? sessionId.slice(0, 8) : 'new chat'}
    </span>
    {#if models.length}
      <select
        class="bg-surface text-muted text-[10px] rounded border border-border/50 px-1 py-0.5 outline-none max-w-[180px]"
        value={activeModel}
        on:change={onModelChange}
        title="Active model ({modelProvider})"
      >
        {#each models as m (m)}
          <option value={m}>{m}</option>
        {/each}
      </select>
    {:else if activeModel}
      <span class="text-muted/60 text-[10px]">{activeModel}</span>
    {/if}
  </div>

  {#if drawerOpen}
    <div class="absolute left-0 top-[26px] bottom-0 w-64 z-20 border-r border-border/50 overflow-y-auto surface-blur"
      style="background: rgb(var(--surface) / 0.92);">
      {#if sessionsLoading}
        <p class="text-muted text-xs px-3 py-2 font-mono">loading…</p>
      {:else}
        {#each sessionList as s (s.id)}
          <button
            class="w-full text-left px-3 py-2 border-b border-border/20 hover:bg-surface2/60 group/sess"
            class:bg-surface2={s.id === sessionId}
            on:click={() => pickSession(s.id)}
          >
            <span class="flex items-center justify-between gap-2 text-xs">
              <span class="truncate text-fg">{s.topic ?? s.summary?.slice(0, 40) ?? s.id.slice(0, 8)}</span>
              <span
                class="opacity-0 group-hover/sess:opacity-60 hover:!opacity-100 hover:text-err shrink-0"
                role="button"
                tabindex="0"
                on:click={(ev) => removeSession(s.id, ev)}
                on:keydown={(ev) => ev.key === 'Enter' && removeSession(s.id, ev)}
              >×</span>
            </span>
            <span class="flex gap-2 text-[10px] text-muted font-mono">
              <span>{s.turn_count} turns</span>
              <span>{relTime(s.updated_at)}</span>
              {#if s.metadata?.source}<span>{s.metadata.source}</span>{/if}
            </span>
          </button>
        {:else}
          <p class="text-muted text-xs px-3 py-2 font-mono">No sessions yet.</p>
        {/each}
      {/if}
    </div>
  {/if}

  <div bind:this={viewport} class="flex-1 overflow-y-auto px-4 py-3 space-y-3 text-sm">
    {#each messages as m, i}
      <div class="flex gap-3 group">
        <div class="w-12 shrink-0 text-xs font-mono uppercase opacity-60 pt-1">
          {m.role === 'user' ? 'you' : 'zeus'}
        </div>
        <div class="flex-1 min-w-0">
          {#if m.phase}
            <span class="text-muted text-xs italic">{m.phase}…</span>
          {/if}
          {#if m.content}
            <div class="prose-chat leading-relaxed">{@html renderMarkdown(m.content)}</div>
          {/if}
          {#if m.toolCalls && m.toolCalls.length}
            <details class="mt-2 text-xs">
              <summary class="text-muted cursor-pointer select-none">
                {m.toolCalls.length} tool call{m.toolCalls.length === 1 ? '' : 's'}
              </summary>
              <div class="mt-1 space-y-2">
                {#each m.toolCalls as tc}
                  <div class="border border-border/40 rounded-wm p-2">
                    <p class="font-mono text-accent">{tc.name ?? 'unknown'}</p>
                    {#if tc.arguments !== undefined}
                      <pre class="text-muted mt-1 whitespace-pre-wrap break-words">{stringifyArg(tc.arguments)}</pre>
                    {/if}
                    {#if tc.result !== undefined}
                      <p class="text-fg mt-1">result:</p>
                      <pre class="text-muted whitespace-pre-wrap break-words">{stringifyArg(tc.result).slice(0, 600)}</pre>
                    {/if}
                    {#if tc.error}
                      <p class="text-err mt-1">{tc.error}</p>
                    {/if}
                  </div>
                {/each}
              </div>
            </details>
          {/if}
          {#if m.role === 'assistant' && (m.model || m.latency_ms !== undefined)}
            <p class="mt-1 text-[10px] text-muted/70 font-mono">
              {m.model ?? ''}{m.model && m.latency_ms !== undefined ? ' · ' : ''}{m.latency_ms !== undefined ? `${m.latency_ms}ms` : ''}
            </p>
          {/if}
        </div>
        {#if m.content}
          <button
            class="opacity-0 group-hover:opacity-60 hover:!opacity-100 text-muted text-xs px-1 self-start transition-opacity"
            on:click={() => copyMessage(i)}
            title="Copy message"
          >
            {copied === i ? '✓' : '⧉'}
          </button>
        {/if}
      </div>
    {:else}
      <div class="text-muted text-sm font-mono">Ask Zeus anything. Markdown + code blocks render inline; tool calls collapse into cards.</div>
    {/each}
  </div>
  <form
    class="border-t border-border/40 p-2 flex gap-2"
    on:submit|preventDefault={send}
  >
    <textarea
      bind:value={input}
      on:keydown={onKey}
      placeholder="Message Zeus…  ⏎ to send, Shift+⏎ for newline"
      class="flex-1 resize-none bg-transparent outline-none text-fg placeholder:text-muted/60 text-sm font-mono p-2"
      rows="1"
    ></textarea>
    <button
      type="submit"
      disabled={sending || !input.trim()}
      class="px-3 py-1.5 rounded-md bg-accent text-bg text-sm font-mono disabled:opacity-40"
    >
      Send
    </button>
  </form>
</div>

<style>
  /* In-component prose styles for rendered markdown. Catppuccin-friendly. */
  :global(.prose-chat) {
    color: rgb(var(--fg));
  }
  :global(.prose-chat p) {
    margin: 0.25rem 0;
  }
  :global(.prose-chat ul, .prose-chat ol) {
    margin: 0.25rem 0 0.25rem 1.25rem;
    padding-left: 0.5rem;
  }
  :global(.prose-chat ul) {
    list-style: disc;
  }
  :global(.prose-chat ol) {
    list-style: decimal;
  }
  :global(.prose-chat li) {
    margin: 0.1rem 0;
  }
  :global(.prose-chat code) {
    background: rgb(var(--surface-2) / 0.7);
    padding: 0.05rem 0.3rem;
    border-radius: 4px;
    font-size: 0.9em;
  }
  :global(.prose-chat pre.hljs) {
    background: rgb(var(--surface-2) / 0.55);
    border: 1px solid rgb(var(--border-color) / 0.5);
    border-radius: 6px;
    padding: 0.6rem 0.7rem;
    margin: 0;
    overflow-x: auto;
    font-size: 0.85rem;
    line-height: 1.4;
  }
  :global(.prose-chat pre.hljs code) {
    background: transparent;
    padding: 0;
    border-radius: 0;
    font-size: inherit;
  }
  :global(.prose-chat .code-block-wrap) {
    position: relative;
    margin: 0.5rem 0;
  }
  :global(.prose-chat .code-lang) {
    position: absolute;
    top: 0.35rem;
    left: 0.55rem;
    font-size: 0.62rem;
    font-family: 'JetBrains Mono', ui-monospace, monospace;
    text-transform: uppercase;
    letter-spacing: 0.04em;
    color: rgb(var(--muted));
    opacity: 0.7;
    pointer-events: none;
    user-select: none;
  }
  :global(.prose-chat .code-copy-btn) {
    position: absolute;
    top: 0.3rem;
    right: 0.4rem;
    padding: 0.15rem 0.5rem;
    font-size: 0.65rem;
    font-family: 'JetBrains Mono', ui-monospace, monospace;
    text-transform: uppercase;
    letter-spacing: 0.04em;
    color: rgb(var(--muted));
    background: rgb(var(--surface) / 0.85);
    border: 1px solid rgb(var(--border-color) / 0.6);
    border-radius: 4px;
    cursor: pointer;
    opacity: 0;
    transition: opacity 140ms ease-out, color 140ms ease-out, border-color 140ms ease-out;
  }
  :global(.prose-chat .code-block-wrap:hover .code-copy-btn) {
    opacity: 0.9;
  }
  :global(.prose-chat .code-copy-btn:hover) {
    color: rgb(var(--fg));
    border-color: rgb(var(--accent));
  }
  :global(.prose-chat .code-copy-btn.copied) {
    opacity: 1;
    color: rgb(var(--ok));
    border-color: rgb(var(--ok));
  }
  :global(.prose-chat blockquote) {
    border-left: 3px solid rgb(var(--accent) / 0.6);
    padding-left: 0.6rem;
    color: rgb(var(--muted));
    margin: 0.4rem 0;
  }
  :global(.prose-chat a) {
    color: rgb(var(--accent));
    text-decoration: underline;
    text-underline-offset: 2px;
  }
  :global(.prose-chat h1, .prose-chat h2, .prose-chat h3, .prose-chat h4) {
    margin: 0.6rem 0 0.3rem;
    font-weight: 600;
    color: rgb(var(--fg));
  }
  :global(.prose-chat h1) {
    font-size: 1.1rem;
  }
  :global(.prose-chat h2) {
    font-size: 1rem;
  }
  :global(.prose-chat h3) {
    font-size: 0.95rem;
  }
  :global(.prose-chat table) {
    border-collapse: collapse;
    margin: 0.4rem 0;
  }
  :global(.prose-chat th, .prose-chat td) {
    border: 1px solid rgb(var(--border-color) / 0.6);
    padding: 0.2rem 0.5rem;
  }
</style>
