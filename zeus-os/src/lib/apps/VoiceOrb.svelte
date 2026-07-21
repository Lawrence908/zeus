<script lang="ts">
  import { onDestroy, onMount } from 'svelte';
  import type { AppInstance } from '$lib/wm/tree';

  import { createPhaosOrb, type OrbHandle, type VoiceStateName } from '$lib/voice/orb';
  import { mediaBlobToWav16kMono, pickMediaRecorderMime } from '$lib/voice/audioWav';
  import { subscribeVoiceState, voiceInteract, synthesize } from '$lib/api/voice';
  import {
    voiceState,
    voiceLevel,
    voiceConnected,
    voicePttTrigger,
    pushVoiceTurn
  } from '$lib/voice/store';
  import { notify } from '$lib/notify/store';

  export let app: AppInstance;
  void app;

  let container: HTMLDivElement;
  let orb: OrbHandle | null = null;
  let raf = 0;
  let lastT = 0;

  let uiState: VoiceStateName = 'idle';
  let level = 0;
  let connected = false;
  let recording = false;
  let sending = false;
  let statusHint = '';
  let mimeUsed = '';

  let mediaStream: MediaStream | null = null;
  let mediaRecorder: MediaRecorder | null = null;
  let chunks: Blob[] = [];

  const unsubState = voiceState.subscribe((v) => {
    uiState = v;
    orb?.setStateName(v);
  });
  const unsubLevel = voiceLevel.subscribe((v) => {
    level = v;
    orb?.setLevel(v);
  });
  const unsubConn = voiceConnected.subscribe((v) => {
    connected = v;
  });

  let lastPtt = 0;
  const unsubPtt = voicePttTrigger.subscribe((n) => {
    if (n === lastPtt) return;
    lastPtt = n;
    void toggleRecording();
  });

  onMount(() => {
    orb = createPhaosOrb(container);
    orb.setStateName(uiState);
    orb.setLevel(level);

    lastT = performance.now();
    const loop = (t: number) => {
      const dt = Math.min(0.1, (t - lastT) / 1000);
      lastT = t;
      orb?.tick(dt);
      raf = requestAnimationFrame(loop);
    };
    raf = requestAnimationFrame(loop);

    const wsUnsub = subscribeVoiceState({
      onFrame: (frame) => {
        if (frame.state) voiceState.set(frame.state);
        if (typeof frame.audio_level === 'number') voiceLevel.set(frame.audio_level);
      },
      onOpen: () => voiceConnected.set(true),
      onClose: () => voiceConnected.set(false)
    });

    return () => {
      wsUnsub();
    };
  });

  onDestroy(() => {
    unsubState();
    unsubLevel();
    unsubConn();
    unsubPtt();
    cancelAnimationFrame(raf);
    orb?.dispose();
    mediaStream?.getTracks().forEach((t) => t.stop());
    mediaRecorder = null;
    chunks = [];
  });

  function newId(): string {
    return `voice-${Date.now()}-${Math.random().toString(36).slice(2, 8)}`;
  }

  function speakBrowserFallback(text: string): void {
    if (typeof window === 'undefined' || !window.speechSynthesis) return;
    const t = text.trim();
    if (!t) return;
    window.speechSynthesis.cancel();
    const u = new SpeechSynthesisUtterance(t);
    u.rate = 1;
    window.speechSynthesis.speak(u);
  }

  async function speakReply(text: string): Promise<void> {
    voiceState.set('speaking');
    try {
      const wav = await synthesize(text);
      if (!wav) {
        speakBrowserFallback(text);
        return;
      }
      const url = URL.createObjectURL(wav);
      const audio = new Audio(url);
      await audio.play().catch(() => speakBrowserFallback(text));
      audio.onended = () => URL.revokeObjectURL(url);
    } catch {
      speakBrowserFallback(text);
    } finally {
      voiceState.set('idle');
    }
  }

  async function startRecording(): Promise<void> {
    if (recording || sending) return;
    if (!navigator.mediaDevices?.getUserMedia) {
      statusHint = 'Microphone unavailable (HTTPS required on some browsers)';
      notify({ title: 'Voice', body: statusHint, kind: 'warn', ttlMs: 3000 });
      return;
    }
    try {
      mediaStream = await navigator.mediaDevices.getUserMedia({
        audio: { echoCancellation: true, noiseSuppression: true }
      });
    } catch (e) {
      statusHint = `Mic error: ${e instanceof Error ? e.message : String(e)}`;
      notify({ title: 'Voice', body: statusHint, kind: 'err', ttlMs: 3000 });
      return;
    }
    chunks = [];
    const mime = pickMediaRecorderMime();
    mimeUsed = mime || '(browser default)';
    mediaRecorder = mime
      ? new MediaRecorder(mediaStream, { mimeType: mime })
      : new MediaRecorder(mediaStream);
    mediaRecorder.ondataavailable = (e) => {
      if (e.data.size > 0) chunks.push(e.data);
    };
    mediaRecorder.start(250);
    recording = true;
    statusHint = 'Listening… press again to send';
    voiceState.set('listening');
  }

  async function stopAndSend(): Promise<void> {
    if (!mediaRecorder || !recording) return;
    const mr = mediaRecorder;
    await new Promise<void>((resolve) => {
      mr.onstop = () => resolve();
      mr.stop();
    });
    const captured = chunks.slice();
    chunks = [];
    mediaStream?.getTracks().forEach((t) => t.stop());
    mediaStream = null;
    mediaRecorder = null;
    recording = false;
    voiceState.set('processing');
    sending = true;

    const mime = captured[0]?.type || 'audio/webm';
    const blob = new Blob(captured, { type: mime });
    if (blob.size < 256) {
      statusHint = 'Recording too short';
      voiceState.set('idle');
      sending = false;
      return;
    }

    try {
      const wav = await mediaBlobToWav16kMono(blob);
      const result = await voiceInteract(wav);
      pushVoiceTurn({
        id: newId(),
        transcript: result.transcript,
        reply: result.assistant_message,
        model: result.model_used,
        contextSources: result.context_sources,
        sessionId: result.session_id,
        ts: Date.now()
      });
      statusHint = result.transcript ? `“${result.transcript.slice(0, 60)}”` : '';
      if (result.assistant_message) {
        await speakReply(result.assistant_message);
      } else {
        voiceState.set('idle');
      }
    } catch (e) {
      statusHint = e instanceof Error ? e.message : String(e);
      notify({ title: 'Voice error', body: statusHint.slice(0, 140), kind: 'err' });
      voiceState.set('idle');
    } finally {
      sending = false;
    }
  }

  function cancelRecording(): void {
    if (!recording || !mediaRecorder) return;
    mediaRecorder.onstop = null;
    mediaRecorder.stop();
    chunks = [];
    mediaStream?.getTracks().forEach((t) => t.stop());
    mediaStream = null;
    mediaRecorder = null;
    recording = false;
    statusHint = 'Cancelled';
    voiceState.set('idle');
  }

  async function toggleRecording(): Promise<void> {
    if (sending) return;
    if (recording) {
      await stopAndSend();
    } else {
      await startRecording();
    }
  }

  function stateBadgeClass(s: VoiceStateName): string {
    switch (s) {
      case 'listening':
      case 'wake_detected':
        return 'bg-accent/20 text-accent';
      case 'processing':
        return 'bg-warn/20 text-warn';
      case 'speaking':
        return 'bg-ok/20 text-ok';
      default:
        return 'bg-surface-2/70 text-muted';
    }
  }
</script>

<div class="h-full w-full flex flex-col relative">
  <div class="absolute top-2 left-2 right-2 flex items-center justify-between text-xs font-mono z-10">
    <span class="px-2 py-0.5 rounded-md {stateBadgeClass(uiState)}">{uiState}</span>
    <span class="text-muted/70">
      {connected ? 'phaos' : 'offline'}
      {#if recording}· rec{/if}
      {#if sending}· processing{/if}
    </span>
  </div>

  <div bind:this={container} class="flex-1 min-h-0"></div>

  <div class="border-t border-border/40 px-3 py-2 flex flex-col gap-2 text-xs">
    <div class="flex items-center gap-2">
      <button
        class="px-3 py-1.5 rounded-md text-sm font-mono transition-colors
               {recording ? 'bg-err/80 text-bg' : 'bg-accent text-bg'}
               disabled:opacity-50"
        on:click={() => toggleRecording()}
        disabled={sending}
      >
        {recording ? '■ Stop & Send' : '● Push to talk'}
      </button>
      {#if recording}
        <button
          class="px-2 py-1.5 rounded-md text-sm font-mono border border-border/60 text-muted hover:text-fg"
          on:click={cancelRecording}
        >
          Cancel
        </button>
      {/if}
      <span class="text-muted/70 truncate">{statusHint}</span>
    </div>
    <p class="text-[10px] text-muted/60 font-mono">
      Global hotkey: <span class="text-fg">Super+M</span> · Level {Math.round(level * 100)}%
      {#if mimeUsed}· {mimeUsed}{/if}
    </p>
  </div>
</div>

<style>
  :global(.window-shell canvas) {
    display: block;
    width: 100% !important;
    height: 100% !important;
  }
</style>
