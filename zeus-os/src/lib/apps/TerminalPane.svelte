<script lang="ts">
  import { onDestroy, onMount, tick } from 'svelte';
  import { notify } from '$lib/notify/store';
  import { mountPane, unmountPane } from './terminal-sessions';

  export let instanceId: string;
  export let tabId: string;
  export let visible: boolean = true;
  export let onExit: ((code: number) => void) | undefined = undefined;

  let host: HTMLDivElement;
  let fitFn: (() => void) | null = null;
  let ro: ResizeObserver | null = null;
  let attached = false;

  async function attach() {
    if (!host || attached) return;
    try {
      const { fit } = await mountPane(instanceId, tabId, host, { onExit });
      fitFn = fit;
      attached = true;
      // Refit shortly after attach so xterm sees the final container size.
      await tick();
      fitFn?.();
    } catch (err) {
      notify({ title: 'Terminal failed to start', body: String(err), kind: 'err' });
    }
  }

  onMount(() => {
    attach();
    ro = new ResizeObserver(() => {
      if (visible) fitFn?.();
    });
    if (host) ro.observe(host);
  });

  onDestroy(() => {
    ro?.disconnect();
    unmountPane(instanceId, tabId, host);
    attached = false;
  });

  // Refit when this pane becomes visible (tab switch within a window).
  $: if (visible && fitFn) {
    queueMicrotask(() => fitFn?.());
  }
</script>

<div bind:this={host} class="h-full w-full" style:display={visible ? '' : 'none'}></div>
