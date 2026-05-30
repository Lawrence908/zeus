<script lang="ts">
  import { onMount, tick } from 'svelte';
  import type { AppInstance } from '$lib/wm/tree';
  import { chatStream } from '$lib/api/chat';

  export let app: AppInstance;
  void app;

  interface Msg {
    role: 'user' | 'assistant';
    content: string;
    phase?: string;
  }

  let messages: Msg[] = [];
  let input = '';
  let sessionId: string | null = null;
  let sending = false;
  let viewport: HTMLDivElement;

  async function send() {
    const text = input.trim();
    if (!text || sending) return;
    sending = true;
    input = '';
    messages = [...messages, { role: 'user', content: text }, { role: 'assistant', content: '', phase: 'queued' }];
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
        },
        onError: (detail) => {
          messages[messages.length - 1].content = `[error] ${detail}`;
          messages = messages;
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

  onMount(() => {
    /* nothing to load up front */
  });
</script>

<div class="h-full w-full flex flex-col">
  <div bind:this={viewport} class="flex-1 overflow-y-auto px-4 py-3 space-y-3 text-sm">
    {#each messages as m}
      <div class="flex gap-3">
        <div class="w-12 shrink-0 text-xs font-mono uppercase opacity-60">
          {m.role === 'user' ? 'you' : 'zeus'}
        </div>
        <div class="flex-1 whitespace-pre-wrap leading-relaxed">
          {#if m.phase}
            <span class="text-muted text-xs italic">{m.phase}…</span>
          {/if}
          {m.content}
        </div>
      </div>
    {:else}
      <div class="text-muted text-sm font-mono">Ask Zeus anything. Streaming over <code>/chat/stream</code>.</div>
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
