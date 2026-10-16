# zeus/pheme/audio.py - Morning-listen MP3 for the Pheme digest.
#
# The shared newsletter path (_generate_audio) sends the whole script as one
# request under the voice client's 20s fail-fast timeout. Kokoro runs on CPU on
# a busy host (~0.4x realtime measured 2026-10-16), so every digest-length synth
# timed out and no digest ever shipped audio. Here the script is synthesized one
# paragraph at a time with a generous per-chunk timeout, as raw PCM, then
# encoded once to MP3: Telegram plays MP3 inline (WAV arrives as a file), and
# byte-concatenating per-chunk MP3s would leave a first-chunk duration header.
from __future__ import annotations

import logging
import os
import re
import uuid
from datetime import datetime, timezone
from pathlib import Path

logger = logging.getLogger("zeus.pheme.audio")

_MAX_CHUNK_CHARS = 700


def _audio_dir() -> Path:
    return Path(os.getenv("NEWSLETTER_AUDIO_DIR", "zeus/data/audio"))


def _env_float(name: str, default: float) -> float:
    try:
        return float(os.getenv(name, str(default)))
    except ValueError:
        return default


def split_script(script: str, max_chars: int = _MAX_CHUNK_CHARS) -> list[str]:
    """Paragraphs, with overlong ones split on sentence boundaries."""
    chunks: list[str] = []
    for para in re.split(r"\n\s*\n", script.strip()):
        para = " ".join(para.split())
        if not para:
            continue
        if len(para) <= max_chars:
            chunks.append(para)
            continue
        current = ""
        for sentence in re.split(r"(?<=[.!?])\s+", para):
            if current and len(current) + len(sentence) + 1 > max_chars:
                chunks.append(current)
                current = sentence
            else:
                current = f"{current} {sentence}".strip()
        if current:
            chunks.append(current)
    return chunks


def encode_mp3(pcm: bytes, sample_rate: int, kbps: int = 64) -> bytes:
    import lameenc

    enc = lameenc.Encoder()
    enc.set_bit_rate(kbps)
    enc.set_in_sample_rate(sample_rate)
    enc.set_channels(1)
    enc.set_quality(2)
    return bytes(enc.encode(pcm) + enc.flush())


async def synthesize_briefing(script: str, *, prefix: str = "pheme") -> str | None:
    """Render ``script`` to an MP3 under NEWSLETTER_AUDIO_DIR. Returns the
    filename, or None if nothing could be synthesized. A failed paragraph is
    skipped rather than sinking the whole track."""
    from zeus.voice.tts import VoiceboxTTS

    chunks = split_script(script)
    if not chunks:
        return None
    tts = VoiceboxTTS()
    tts.response_format = "pcm"
    tts.timeout = _env_float("PHEME_AUDIO_CHUNK_TIMEOUT_SEC", 300.0)
    sample_rate = int(_env_float("PHEME_AUDIO_SAMPLE_RATE", 24000))
    gap = b"\x00\x00" * int(sample_rate * 0.6)  # 16-bit mono silence between paragraphs

    pcm = bytearray()
    failed = 0
    for i, chunk in enumerate(chunks):
        try:
            data = await tts.synthesize(chunk)
        except Exception as exc:
            failed += 1
            logger.warning("pheme audio chunk %d/%d failed: %r", i + 1, len(chunks), exc)
            continue
        if len(data) % 2:
            data = data[:-1]
        if pcm:
            pcm += gap
        pcm += data
    if not pcm:
        return None
    if failed:
        logger.warning("pheme audio shipped with %d of %d paragraphs missing", failed, len(chunks))

    mp3 = encode_mp3(bytes(pcm), sample_rate)
    out_dir = _audio_dir()
    out_dir.mkdir(parents=True, exist_ok=True)
    ts = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    filename = f"{prefix}_{ts}_{uuid.uuid4().hex[:8]}.mp3"
    (out_dir / filename).write_bytes(mp3)
    logger.info(
        "pheme audio: %s (%.0fs, %d bytes)", filename, len(pcm) / 2 / sample_rate, len(mp3)
    )
    return filename
