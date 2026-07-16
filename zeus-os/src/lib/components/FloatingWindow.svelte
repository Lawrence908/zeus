<script lang="ts">
  import { fade, scale } from 'svelte/transition';
  import { cubicOut } from 'svelte/easing';

  import type { FloatingWindow } from '$lib/wm/workspace';
  import { closeFloating, raiseFloating, updateFloating, viewport } from '$lib/wm/store';

  import Terminal from '$lib/apps/Terminal.svelte';
  import Chat from '$lib/apps/Chat.svelte';
  import SystemMonitor from '$lib/apps/SystemMonitor.svelte';
  import FileManager from '$lib/apps/FileManager.svelte';
  import Tools from '$lib/apps/Tools.svelte';
  import Jobs from '$lib/apps/Jobs.svelte';
  import TokenUsage from '$lib/apps/TokenUsage.svelte';
  import Settings from '$lib/apps/Settings.svelte';
  import Memories from '$lib/apps/Memories.svelte';
  import Knowledge from '$lib/apps/Knowledge.svelte';
  import Agents from '$lib/apps/Agents.svelte';
  import Ingest from '$lib/apps/Ingest.svelte';
  import Obsidian from '$lib/apps/Obsidian.svelte';
  import Editor from '$lib/apps/Editor.svelte';
  import HomeAssistant from '$lib/apps/HomeAssistant.svelte';
  import Linear from '$lib/apps/Linear.svelte';
  import Processes from '$lib/apps/Processes.svelte';
  import Network from '$lib/apps/Network.svelte';
  import Notepad from '$lib/apps/Notepad.svelte';
  import Calendar from '$lib/apps/Calendar.svelte';
  import Images from '$lib/apps/Images.svelte';
  import Placeholder from '$lib/apps/Placeholder.svelte';

  export let win: FloatingWindow;
  export let focused: boolean;

  const components: Record<string, typeof Terminal> = {
    Terminal,
    Chat,
    SystemMonitor,
    FileManager,
    Tools,
    Jobs,
    TokenUsage,
    Settings,
    Memories,
    Knowledge,
    Agents,
    Ingest,
    Obsidian,
    Editor,
    HomeAssistant,
    Linear,
    Processes,
    Network,
    Notepad,
    Calendar,
    Images,
    Placeholder
  };
  $: Comp = components[win.app.kind] ?? Placeholder;

  const MIN_W = 280;
  const MIN_H = 180;

  interface DragState {
    mode: 'move' | 'n' | 's' | 'e' | 'w' | 'ne' | 'nw' | 'se' | 'sw';
    startX: number;
    startY: number;
    startRect: { x: number; y: number; w: number; h: number };
  }
  let drag: DragState | null = null;

  function clampToViewport(r: { x: number; y: number; w: number; h: number }, v: { x: number; y: number; w: number; h: number }) {
    const maxX = v.x + v.w - 60;
    const minX = v.x - r.w + 60;
    const minY = v.y;
    const maxY = v.y + v.h - 40;
    return {
      x: Math.min(maxX, Math.max(minX, r.x)),
      y: Math.min(maxY, Math.max(minY, r.y)),
      w: Math.max(MIN_W, r.w),
      h: Math.max(MIN_H, r.h)
    };
  }

  function onPointerDown(mode: DragState['mode'], ev: PointerEvent) {
    if (ev.button !== 0) return;
    ev.preventDefault();
    raiseFloating(win.id);
    drag = {
      mode,
      startX: ev.clientX,
      startY: ev.clientY,
      startRect: { x: win.x, y: win.y, w: win.w, h: win.h }
    };
    const target = ev.target as Element;
    target.setPointerCapture(ev.pointerId);
  }

  function onPointerMove(ev: PointerEvent) {
    if (!drag) return;
    const dx = ev.clientX - drag.startX;
    const dy = ev.clientY - drag.startY;
    const r = { ...drag.startRect };
    switch (drag.mode) {
      case 'move':
        r.x += dx;
        r.y += dy;
        break;
      case 'e':
        r.w += dx;
        break;
      case 's':
        r.h += dy;
        break;
      case 'w':
        r.x += dx;
        r.w -= dx;
        break;
      case 'n':
        r.y += dy;
        r.h -= dy;
        break;
      case 'se':
        r.w += dx;
        r.h += dy;
        break;
      case 'sw':
        r.x += dx;
        r.w -= dx;
        r.h += dy;
        break;
      case 'ne':
        r.y += dy;
        r.w += dx;
        r.h -= dy;
        break;
      case 'nw':
        r.x += dx;
        r.y += dy;
        r.w -= dx;
        r.h -= dy;
        break;
    }
    const clamped = clampToViewport(r, $viewport);
    updateFloating(win.id, clamped);
  }

  function onPointerUp(ev: PointerEvent) {
    if (!drag) return;
    const target = ev.target as Element;
    try {
      target.releasePointerCapture(ev.pointerId);
    } catch {
      /* ignore */
    }
    drag = null;
  }
</script>

<div
  class="window-shell absolute overflow-hidden"
  class:focused
  style="left:{win.x}px; top:{win.y}px; width:{win.w}px; height:{win.h}px; z-index:{50 + win.z};"
  on:mousedown={() => raiseFloating(win.id)}
  role="group"
  aria-label={win.app.title}
  in:scale={{ duration: 200, start: 0.94, easing: cubicOut }}
  out:fade={{ duration: 120 }}
>
  <!-- header / drag handle -->
  <header
    class="flex items-center justify-between px-3 py-1.5 text-xs select-none cursor-move"
    style="background: rgb(var(--surface-2) / 0.78); border-bottom: 1px solid rgb(var(--border-color) / 0.7); height: 28px;"
    on:pointerdown={(ev) => onPointerDown('move', ev)}
    on:pointermove={onPointerMove}
    on:pointerup={onPointerUp}
    on:pointercancel={onPointerUp}
  >
    <span class="font-mono truncate text-muted">{win.app.title}</span>
    <button
      class="text-muted hover:text-err px-1"
      on:click|stopPropagation={() => closeFloating(win.id)}
      aria-label="Close window"
      title="Close"
    >
      ×
    </button>
  </header>

  <!-- app body -->
  <div class="absolute inset-0" style="top: 28px;">
    <svelte:component this={Comp} app={win.app} />
  </div>

  <!-- resize handles -->
  <span
    class="absolute left-0 right-0 top-0 h-1 cursor-n-resize z-10"
    on:pointerdown={(ev) => onPointerDown('n', ev)}
    on:pointermove={onPointerMove}
    on:pointerup={onPointerUp}
    on:pointercancel={onPointerUp}
  ></span>
  <span
    class="absolute left-0 right-0 bottom-0 h-1 cursor-s-resize z-10"
    on:pointerdown={(ev) => onPointerDown('s', ev)}
    on:pointermove={onPointerMove}
    on:pointerup={onPointerUp}
    on:pointercancel={onPointerUp}
  ></span>
  <span
    class="absolute left-0 top-0 bottom-0 w-1 cursor-w-resize z-10"
    on:pointerdown={(ev) => onPointerDown('w', ev)}
    on:pointermove={onPointerMove}
    on:pointerup={onPointerUp}
    on:pointercancel={onPointerUp}
  ></span>
  <span
    class="absolute right-0 top-0 bottom-0 w-1 cursor-e-resize z-10"
    on:pointerdown={(ev) => onPointerDown('e', ev)}
    on:pointermove={onPointerMove}
    on:pointerup={onPointerUp}
    on:pointercancel={onPointerUp}
  ></span>
  <span
    class="absolute left-0 top-0 w-3 h-3 cursor-nw-resize z-20"
    on:pointerdown={(ev) => onPointerDown('nw', ev)}
    on:pointermove={onPointerMove}
    on:pointerup={onPointerUp}
    on:pointercancel={onPointerUp}
  ></span>
  <span
    class="absolute right-0 top-0 w-3 h-3 cursor-ne-resize z-20"
    on:pointerdown={(ev) => onPointerDown('ne', ev)}
    on:pointermove={onPointerMove}
    on:pointerup={onPointerUp}
    on:pointercancel={onPointerUp}
  ></span>
  <span
    class="absolute left-0 bottom-0 w-3 h-3 cursor-sw-resize z-20"
    on:pointerdown={(ev) => onPointerDown('sw', ev)}
    on:pointermove={onPointerMove}
    on:pointerup={onPointerUp}
    on:pointercancel={onPointerUp}
  ></span>
  <span
    class="absolute right-0 bottom-0 w-3 h-3 cursor-se-resize z-20"
    on:pointerdown={(ev) => onPointerDown('se', ev)}
    on:pointermove={onPointerMove}
    on:pointerup={onPointerUp}
    on:pointercancel={onPointerUp}
  ></span>
</div>
