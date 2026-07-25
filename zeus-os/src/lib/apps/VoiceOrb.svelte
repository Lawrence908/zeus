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

  // ── live audio level analysis ──
  // While recording we compute RMS from the mic locally so the orb reacts to
  // the user's voice in real time (the server-side level only covers Orpheus).
  // During TTS playback we analyze the output the same way.
  let audioCtx: AudioContext | null = null;
  let analyser: AnalyserNode | null = null;
  let levelRaf = 0;
  let simTimer: ReturnType<typeof setInterval> | null = null;

  function ensureAudioCtx(): AudioContext {
    if (!audioCtx || audioCtx.state === 'closed') {
      audioCtx = new AudioContext();
    }
    if (audioCtx.state === 'suspended') void audioCtx.resume();
    return audioCtx;
  }

  function startLevelLoop() {
    stopLevelLoop();
    const buf = new Uint8Array(analyser?.fftSize ?? 0);
    const loop = () => {
      if (!analyser) return;
      analyser.getByteTimeDomainData(buf);
      let sum = 0;
      for (let i = 0; i < buf.length; i++) {
        const c = (buf[i] - 128) / 128;
        sum += c * c;
      }
      const rms = Math.sqrt(sum / buf.length);
      // Log-ish curve so quiet speech still moves the orb perceptibly.
      voiceLevel.set(Math.min(1, Math.pow(rms * 2.6, 0.7)));
      levelRaf = requestAnimationFrame(loop);
    };
    levelRaf = requestAnimationFrame(loop);
  }

  function stopLevelLoop() {
    if (levelRaf) cancelAnimationFrame(levelRaf);
    levelRaf = 0;
    if (simTimer) clearInterval(simTimer);
    simTimer = null;
    analyser?.disconnect();
    analyser = null;
    voiceLevel.set(0);
  }

  /** Fake a speech envelope when we have no analyzable audio (Web Speech). */
  function startSimulatedLevel() {
    stopLevelLoop();
    let t = 0;
    simTimer = setInterval(() => {
      t += 0.09;
      const v = 0.3 + 0.22 * Math.abs(Math.sin(t * 2.1)) + 0.12 * Math.abs(Math.sin(t * 5.7));
      voiceLevel.set(v);
    }, 50);
  }

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

    // Repaint the orb palette when the shell theme changes.
    const themeObserver = new MutationObserver(() => orb?.refreshTheme());
    themeObserver.observe(document.documentElement, {
      attributes: true,
      attributeFilter: ['data-theme']
    });

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
      themeObserver.disconnect();
      wsUnsub();
    };
  });

  onDestroy(() => {
    unsubState();
    unsubLevel();
    unsubConn();
    unsubPtt();
    cancelAnimationFrame(raf);
    stopLevelLoop();
    void audioCtx?.close().catch(() => undefined);
    audioCtx = null;
    orb?.dispose();
    mediaStream?.getTracks().forEach((t) => t.stop());
    mediaRecorder = null;
    chunks = [];
  });

  function newId(): string {
    return `voice-${Date.now()}-${Math.random().toString(36).slice(2, 8)}`;
  }

  /** Speak via Web Speech, resolving when the utterance actually finishes. */
  function speakBrowserFallback(text: string): Promise<void> {
    return new Promise((resolve) => {
      if (typeof window === 'undefined' || !window.speechSynthesis) return resolve();
      const t = text.trim();
      if (!t) return resolve();
      window.speechSynthesis.cancel();
      const u = new SpeechSynthesisUtterance(t);
      u.rate = 1;
      u.onend = () => resolve();
      u.onerror = () => resolve();
      startSimulatedLevel();
      window.speechSynthesis.speak(u);
    });
  }

  /** Play Voicebox WAV through an analyser so the orb follows the reply. */
  function playWavAnalyzed(wav: Blob): Promise<void> {
    return new Promise((resolve, reject) => {
      const url = URL.createObjectURL(wav);
      const audio = new Audio(url);
      const cleanup = () => {
        stopLevelLoop();
        URL.revokeObjectURL(url);
      };
      try {
        const ctx = ensureAudioCtx();
        const src = ctx.createMediaElementSource(audio);
        analyser = ctx.createAnalyser();
        analyser.fftSize = 1024;
        src.connect(analyser);
        analyser.connect(ctx.destination);
        startLevelLoop();
      } catch {
        /* still play without analysis */
      }
      audio.onended = () => {
        cleanup();
        resolve();
      };
      audio.onerror = () => {
        cleanup();
        reject(new Error('playback failed'));
      };
      audio.play().catch((e) => {
        cleanup();
        reject(e instanceof Error ? e : new Error(String(e)));
      });
    });
  }

  async function speakReply(text: string): Promise<void> {
    voiceState.set('speaking');
    try {
      const wav = await synthesize(text);
      if (wav) {
        await playWavAnalyzed(wav);
      } else {
        await speakBrowserFallback(text);
      }
    } catch {
      await speakBrowserFallback(text);
    } finally {
      stopLevelLoop();
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

    // Drive the orb from the live mic while recording.
    try {
      const ctx = ensureAudioCtx();
      const src = ctx.createMediaStreamSource(mediaStream);
      analyser = ctx.createAnalyser();
      analyser.fftSize = 1024;
      src.connect(analyser);
      startLevelLoop();
    } catch {
      /* level analysis is best-effort */
    }

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
    stopLevelLoop();
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
    stopLevelLoop();
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
