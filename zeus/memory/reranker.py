# zeus/memory/reranker.py — BGE cross-encoder reranker for KnowledgeStore.
#
# Runs BAAI/bge-reranker-v2-m3 (278M params, Apache 2.0) on CPU by default.
# Loaded lazily on first use so a fresh repo boot stays fast when the
# reranker isn't in the hot path. First call downloads ~1.1GB from
# HuggingFace into the container's HF cache.
#
# Env:
#   ZEUS_RERANKER_MODEL — override model id (default BAAI/bge-reranker-v2-m3)
#   ZEUS_RERANKER_DEVICE — "cpu" (default) | "cuda" | "cuda:0"
#   ZEUS_RERANKER_FP16 — "1" to use fp16 weights (smaller VRAM, slightly lossy)
#
# Olympus (RTX 3080 10GB) rule: run this on CPU or the dev 5080. The 3080
# stays dedicated to qwen2.5:7b for chat. See CLAUDE.md.
from __future__ import annotations

import logging
import os
import threading
from typing import Sequence

logger = logging.getLogger("zeus.memory.reranker")

_DEFAULT_MODEL = os.getenv("ZEUS_RERANKER_MODEL", "BAAI/bge-reranker-v2-m3")
_DEFAULT_DEVICE = os.getenv("ZEUS_RERANKER_DEVICE", "cpu")
_USE_FP16 = os.getenv("ZEUS_RERANKER_FP16", "0").strip() in ("1", "true", "yes")


class BgeReranker:
    """Thin wrapper around sentence-transformers CrossEncoder.

    Loads a BGE cross-encoder reranker (default ``BAAI/bge-reranker-v2-m3``).
    ``predict(pairs)`` returns relevance logits — higher = more relevant; the
    caller (``KnowledgeStore._rerank``) sorts descending.

    sentence-transformers is used instead of FlagEmbedding because FlagEmbedding
    1.x pins an older ``transformers`` that lacks symbols present in 5.x (see
    ``is_torch_fx_available`` regression). sentence-transformers 5.x tracks
    recent ``transformers`` releases and exposes the same BGE checkpoints.
    """

    def __init__(
        self,
        *,
        model_id: str = _DEFAULT_MODEL,
        device: str = _DEFAULT_DEVICE,
        use_fp16: bool = _USE_FP16,
    ) -> None:
        from sentence_transformers import CrossEncoder

        logger.info(
            "loading reranker %s (device=%s, fp16=%s) — first run downloads ~1GB",
            model_id,
            device,
            use_fp16,
        )
        kwargs: dict = {}
        if use_fp16 and device.startswith("cuda"):
            import torch

            kwargs["model_kwargs"] = {"torch_dtype": torch.float16}
        self._model = CrossEncoder(model_id, device=device, **kwargs)
        self.model_id = model_id
        self.device = device

    def score_pairs(self, pairs: Sequence[tuple[str, str]]) -> list[float]:
        if not pairs:
            return []
        raw = self._model.predict(list(pairs))
        try:
            return [float(x) for x in raw]
        except TypeError:
            return [float(raw)]


_shared: BgeReranker | None = None
_shared_lock = threading.Lock()


def get_reranker() -> BgeReranker:
    """Process-wide singleton. Thread-safe double-checked lock on init."""
    global _shared
    if _shared is None:
        with _shared_lock:
            if _shared is None:
                _shared = BgeReranker()
    return _shared
