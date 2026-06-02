<script lang="ts">
  import type { AppInstance } from '$lib/wm/tree';

  export let app: AppInstance;
</script>

<div class="h-full w-full flex flex-col items-center justify-center text-center p-6 select-none">
  <p class="text-4xl mb-3 opacity-60">🪵</p>
  <h3 class="text-fg text-lg font-mono">{app.title}</h3>
  <p class="text-muted text-sm mt-2 max-w-xs">
    Not implemented yet. Coming in Phase 2 — drop notes in
    <code class="text-accent">~/.zeus/zeus-os/apps.json</code> to pin custom entries here.
  </p>
</div>
