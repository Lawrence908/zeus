"""zeus/voice/wake.py — Orpheus wake word detection (openWakeWord)."""

from __future__ import annotations

import logging
import os
import pathlib

import numpy as np
import pyaudio
import openwakeword
from openwakeword.model import Model
from openwakeword.utils import download_models

logger = logging.getLogger("orpheus")


ALIASES: dict[str, str] = {
    "zeus": "hey_jarvis",
    "hey_zeus": "hey_jarvis",
}


def _normalize_model_name(model_name: str) -> str:
    key = model_name.strip().lower().replace(" ", "_")
    return ALIASES.get(key, key)


def _ensure_openwakeword_models(model_key: str) -> str:
    """
    PyPI wheels ship without .tflite assets; download into package resources on first use.
    See openwakeword.utils.download_models.
    """
    key = _normalize_model_name(model_key)
    # Custom model file path support
    if os.path.isfile(model_key):
        return model_key
    if key not in openwakeword.MODELS:
        supported = ", ".join(sorted(openwakeword.MODELS.keys()))
        raise ValueError(
            f"Unsupported WAKE_WORD_MODEL='{model_key}'. "
            f"Use one of: {supported}, one of aliases: {', '.join(sorted(ALIASES.keys()))}, "
            "or provide an absolute path to a custom .tflite/.onnx model."
        )
    path = openwakeword.MODELS[key]["model_path"]
    model_dir = str(pathlib.Path(path).parent)
    if os.path.isfile(path) and os.path.getsize(path) > 0:
        return key
    stem = os.path.splitext(os.path.basename(path))[0]
    logger.info(f"orpheus: downloading openWakeWord model assets ({stem}) …")
    download_models(model_names=[stem], target_directory=model_dir)
    if not os.path.isfile(path) or os.path.getsize(path) == 0:
        raise RuntimeError(
            "openWakeWord model download did not produce a valid model file. "
            f"Expected: {path}. Check network access to github.com releases and re-run."
        )
    return key


class WakeWordDetector:
    def __init__(
        self,
        *,
        model_name: str | None = None,
        threshold: float | None = None,
    ) -> None:
        self.model_name = (model_name or os.getenv("WAKE_WORD_MODEL", "hey_jarvis")).strip()
        self.threshold = float(threshold if threshold is not None else os.getenv("WAKE_WORD_THRESHOLD", "0.5"))
        self.inference_framework = os.getenv("WAKE_WORD_INFERENCE_FRAMEWORK", "onnx").strip().lower()
        if self.inference_framework not in {"onnx", "tflite"}:
            raise ValueError("WAKE_WORD_INFERENCE_FRAMEWORK must be 'onnx' or 'tflite'")
        self.chunk_size = 1280  # ~80ms at 16kHz
        self.rate = 16000
        resolved_model = _ensure_openwakeword_models(self.model_name)
        self._model = Model(
            wakeword_models=[resolved_model],
            inference_framework=self.inference_framework,
        )

    def listen(self) -> None:
        """Block until wake word detected."""
        audio = pyaudio.PyAudio()
        stream = audio.open(
            format=pyaudio.paInt16,
            channels=1,
            rate=self.rate,
            input=True,
            frames_per_buffer=self.chunk_size,
        )
        try:
            while True:
                chunk = stream.read(self.chunk_size, exception_on_overflow=False)
                audio_np = np.frombuffer(chunk, dtype=np.int16)
                prediction = self._model.predict(audio_np)
                score = float(max(prediction.values()))
                if score >= self.threshold:
                    return
        finally:
            stream.stop_stream()
            stream.close()
            audio.terminate()

