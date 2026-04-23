// zeus/core/static/viz/audio.js — Web Audio API mic level for Phaos (listening state)
/**
 * Opens the microphone and returns a function that returns a smoothed level in [0,1].
 * Call dispose() when done to release the mic.
 */
export async function createMicAnalyzer() {
  const stream = await navigator.mediaDevices.getUserMedia({
    audio: {
      echoCancellation: true,
      noiseSuppression: true,
      autoGainControl: true,
    },
    video: false,
  });

  const ctx = new AudioContext();
  const source = ctx.createMediaStreamSource(stream);
  const analyser = ctx.createAnalyser();
  analyser.fftSize = 256;
  analyser.smoothingTimeConstant = 0.65;
  source.connect(analyser);

  const data = new Uint8Array(analyser.frequencyBinCount);
  let smooth = 0;

  function level() {
    analyser.getByteFrequencyData(data);
    let sum = 0;
    for (let i = 0; i < data.length; i += 1) {
      sum += data[i];
    }
    const raw = sum / (data.length * 255);
    const shaped = Math.min(1, Math.pow(raw * 2.2, 0.65));
    smooth = smooth * 0.72 + shaped * 0.28;
    return smooth;
  }

  function dispose() {
    source.disconnect();
    analyser.disconnect();
    stream.getTracks().forEach((t) => t.stop());
    return ctx.close();
  }

  return { level, dispose, audioContext: ctx };
}
