<script lang="ts">
  import { onDestroy, onMount } from 'svelte';
  import { openPty, type PtyClient } from '$lib/api/pty';
  import { notify } from '$lib/notify/store';

  export let visible: boolean = true;
  export let onExit: ((code: number) => void) | undefined = undefined;

  let container: HTMLDivElement;
  let pty: PtyClient | null = null;
  let term: import('@xterm/xterm').Terminal | null = null;
  let fit: import('@xterm/addon-fit').FitAddon | null = null;
  let mounted = false;
  let ro: ResizeObserver | null = null;

  async function init() {
    if (!container) return;
    const { Terminal } = await import('@xterm/xterm');
    const { FitAddon } = await import('@xterm/addon-fit');
    const { WebLinksAddon } = await import('@xterm/addon-web-links');
    await import('@xterm/xterm/css/xterm.css');

    term = new Terminal({
      fontFamily: 'JetBrains Mono, ui-monospace, monospace',
      fontSize: 13,
      cursorBlink: true,
      allowProposedApi: true,
      theme: themeFromCss()
    });
    fit = new FitAddon();
    term.loadAddon(fit);
    term.loadAddon(new WebLinksAddon());
    term.open(container);
    try {
      fit.fit();
    } catch {
      /* container may be hidden */
    }
    mounted = true;

    pty = openPty({
      cols: term.cols,
      rows: term.rows,
      onOutput: (chunk) => term?.write(chunk),
      onExit: (code) => {
        if (term) {
          term.writeln('');
          term.writeln(`[2m[process exited (${code})][0m`);
        }
        onExit?.(code);
      }
    });

    term.onData((data) => pty?.send(data));
    term.onResize(({ cols, rows }) => pty?.resize(cols, rows));

    ro = new ResizeObserver(() => {
      if (!fit || !mounted || !visible) return;
      try {
        fit.fit();
      } catch {
        /* ignore */
      }
    });
    ro.observe(container);
  }

  function themeFromCss() {
    const css = getComputedStyle(document.documentElement);
    const rgb = (name: string) => {
      const v = css.getPropertyValue(name).trim();
      if (!v) return undefined;
      const [r, g, b] = v.split(/\s+/).map(Number);
      return `#${[r, g, b].map((n) => n.toString(16).padStart(2, '0')).join('')}`;
    };
    return {
      background: rgb('--surface') ?? '#1e1e2e',
      foreground: rgb('--fg') ?? '#cdd6f4',
      cursor: rgb('--accent') ?? '#89b4fa'
    };
  }

  // Refit when this pane becomes visible (tab switch).
  $: if (visible && fit && mounted) {
    queueMicrotask(() => {
      try {
        fit?.fit();
      } catch {
        /* ignore */
      }
    });
  }

  onMount(() => {
    init().catch((err) => notify({ title: 'Terminal failed to start', body: String(err), kind: 'err' }));
  });

  onDestroy(() => {
    ro?.disconnect();
    pty?.close();
    term?.dispose();
  });
</script>

<div bind:this={container} class="h-full w-full p-1 font-mono" style:display={visible ? '' : 'none'}></div>
