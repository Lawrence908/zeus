// zeus/frontend/src/utils/audioWav.ts
// Utility: convert a MediaRecorder blob (webm/ogg) to 16 kHz mono WAV for /voice/interact.

/**
 * Pick the best MIME type that MediaRecorder supports, preferring webm opus.
 * Returns undefined if none of the preferred types is supported.
 */
export function pickMediaRecorderMime(): string | undefined {
  const preferred = [
    'audio/webm;codecs=opus',
    'audio/webm',
    'audio/ogg;codecs=opus',
    'audio/ogg',
  ]
  for (const mime of preferred) {
    if (typeof MediaRecorder !== 'undefined' && MediaRecorder.isTypeSupported(mime)) {
      return mime
    }
  }
  return undefined
}

/**
 * Decode a media blob via the Web Audio API and re-encode as 16 kHz mono
 * linear-PCM WAV (16-bit). Returns a Uint8Array containing the full WAV file.
 */
export async function mediaBlobToWav16kMono(blob: Blob): Promise<Uint8Array> {
  const arrayBuffer = await blob.arrayBuffer()
  const audioCtx = new OfflineAudioContext(1, 1, 16000)
  const decoded = await audioCtx.decodeAudioData(arrayBuffer)

  // Resample to 16 kHz mono
  const targetSampleRate = 16000
  const offlineCtx = new OfflineAudioContext(
    1,
    Math.ceil(decoded.duration * targetSampleRate),
    targetSampleRate,
  )
  const source = offlineCtx.createBufferSource()
  source.buffer = decoded
  source.connect(offlineCtx.destination)
  source.start()
  const rendered = await offlineCtx.startRendering()

  const samples = rendered.getChannelData(0)
  return encodeWav(samples, targetSampleRate)
}

/** Encode float32 PCM samples into a 16-bit WAV file. */
function encodeWav(samples: Float32Array, sampleRate: number): Uint8Array {
  const numChannels = 1
  const bitsPerSample = 16
  const bytesPerSample = bitsPerSample / 8
  const blockAlign = numChannels * bytesPerSample
  const dataSize = samples.length * bytesPerSample
  const headerSize = 44
  const buffer = new ArrayBuffer(headerSize + dataSize)
  const view = new DataView(buffer)

  // RIFF header
  writeString(view, 0, 'RIFF')
  view.setUint32(4, 36 + dataSize, true)
  writeString(view, 8, 'WAVE')

  // fmt chunk
  writeString(view, 12, 'fmt ')
  view.setUint32(16, 16, true) // chunk size
  view.setUint16(20, 1, true) // PCM
  view.setUint16(22, numChannels, true)
  view.setUint32(24, sampleRate, true)
  view.setUint32(28, sampleRate * blockAlign, true)
  view.setUint16(32, blockAlign, true)
  view.setUint16(34, bitsPerSample, true)

  // data chunk
  writeString(view, 36, 'data')
  view.setUint32(40, dataSize, true)

  // PCM samples (float32 -> int16)
  let offset = 44
  for (let i = 0; i < samples.length; i++) {
    const s = Math.max(-1, Math.min(1, samples[i]))
    view.setInt16(offset, s < 0 ? s * 0x8000 : s * 0x7fff, true)
    offset += 2
  }

  return new Uint8Array(buffer)
}

function writeString(view: DataView, offset: number, str: string): void {
  for (let i = 0; i < str.length; i++) {
    view.setUint8(offset + i, str.charCodeAt(i))
  }
}
