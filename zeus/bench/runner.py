# zeus/bench/runner.py — Run prompt suites against Ollama models and record tok/s.
#
# Uses Ollama's native /api/generate response fields (eval_count, eval_duration)
# instead of counting tokens client-side, so numbers are exact.
from __future__ import annotations

import asyncio
import json
import logging
import os
import time
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Iterable

import httpx

logger = logging.getLogger("zeus.bench")

OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11435")
RESULTS_PATH = Path(os.getenv("ZEUS_BENCHMARKS_PATH", "zeus/data/benchmarks.json"))

DEFAULT_PROMPTS: list[dict[str, Any]] = [
    {
        "id": "short",
        "prompt": "Reply with only the number: 2+2=?",
        "max_tokens": 16,
    },
    {
        "id": "medium",
        "prompt": "Write a 3-sentence summary of how REST APIs work.",
        "max_tokens": 200,
    },
    {
        "id": "long",
        "prompt": (
            "Explain how a hash table works, including collision handling, "
            "load factor, and a concrete worked example with 5 keys."
        ),
        "max_tokens": 600,
    },
]


@dataclass
class PromptResult:
    prompt_id: str
    eval_count: int
    eval_duration_s: float
    prompt_eval_count: int
    prompt_eval_duration_s: float
    total_duration_s: float
    tokens_per_second: float
    ttft_ms: float | None


@dataclass
class BenchmarkResult:
    model: str
    host: str
    started_at: float
    finished_at: float
    tokens_per_second: float  # weighted across prompts
    ttft_ms: float | None
    prompt_eval_tps: float
    total_eval_tokens: int
    total_eval_seconds: float
    error: str | None = None
    prompts: list[PromptResult] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        d = asdict(self)
        return d


class BenchmarkRunner:
    def __init__(
        self,
        ollama_url: str = OLLAMA_URL,
        prompts: list[dict[str, Any]] | None = None,
        host_label: str | None = None,
    ) -> None:
        self.ollama_url = ollama_url.rstrip("/")
        self.prompts = prompts or DEFAULT_PROMPTS
        self.host_label = host_label or os.getenv("ZEUS_HOST_LABEL", os.uname().nodename)

    async def list_models(self, client: httpx.AsyncClient) -> list[str]:
        resp = await client.get(f"{self.ollama_url}/api/tags", timeout=10.0)
        resp.raise_for_status()
        data = resp.json()
        # Skip embedding models — they don't accept /api/generate.
        return [
            m["name"]
            for m in data.get("models", [])
            if "embed" not in m["name"].lower()
        ]

    async def _run_one_prompt(
        self,
        client: httpx.AsyncClient,
        model: str,
        prompt: dict[str, Any],
    ) -> PromptResult:
        body = {
            "model": model,
            "prompt": prompt["prompt"],
            "stream": True,
            "keep_alive": "10m",
            "options": {
                "num_predict": prompt.get("max_tokens", 256),
                "temperature": 0.1,
            },
        }
        ttft_ms: float | None = None
        last_payload: dict[str, Any] = {}
        t0 = time.monotonic()
        async with client.stream(
            "POST",
            f"{self.ollama_url}/api/generate",
            json=body,
            timeout=httpx.Timeout(connect=10.0, read=600.0, write=10.0, pool=10.0),
        ) as resp:
            resp.raise_for_status()
            async for line in resp.aiter_lines():
                if not line:
                    continue
                try:
                    chunk = json.loads(line)
                except json.JSONDecodeError:
                    continue
                # TTFT = time to first streamed chunk from the server, regardless
                # of content. Covers models that emit only <think> blocks first.
                if ttft_ms is None:
                    ttft_ms = (time.monotonic() - t0) * 1000
                if chunk.get("done"):
                    last_payload = chunk

        eval_count = int(last_payload.get("eval_count", 0))
        eval_duration_s = float(last_payload.get("eval_duration", 0)) / 1e9
        prompt_eval_count = int(last_payload.get("prompt_eval_count", 0))
        prompt_eval_duration_s = float(last_payload.get("prompt_eval_duration", 0)) / 1e9
        total_duration_s = float(last_payload.get("total_duration", 0)) / 1e9

        tps = (eval_count / eval_duration_s) if eval_duration_s > 0 else 0.0
        return PromptResult(
            prompt_id=prompt["id"],
            eval_count=eval_count,
            eval_duration_s=eval_duration_s,
            prompt_eval_count=prompt_eval_count,
            prompt_eval_duration_s=prompt_eval_duration_s,
            total_duration_s=total_duration_s,
            tokens_per_second=round(tps, 2),
            ttft_ms=round(ttft_ms, 1) if ttft_ms is not None else None,
        )

    async def run_model(
        self,
        model: str,
        client: httpx.AsyncClient | None = None,
    ) -> BenchmarkResult:
        owns_client = client is None
        if owns_client:
            client = httpx.AsyncClient()
        started = time.time()
        result = BenchmarkResult(
            model=model,
            host=self.host_label,
            started_at=started,
            finished_at=started,
            tokens_per_second=0.0,
            ttft_ms=None,
            prompt_eval_tps=0.0,
            total_eval_tokens=0,
            total_eval_seconds=0.0,
        )
        try:
            # Warm-up so first prompt isn't penalised by model load time.
            # Ask for a real output so the model actually runs its graph, not
            # just loads weights — some runtimes (Qwen3 with thinking mode) can
            # return instantly on a trivial prompt without exercising generation.
            await self._run_one_prompt(
                client,
                model,
                {"id": "warmup", "prompt": "Say hello.", "max_tokens": 32},
            )

            for spec in self.prompts:
                logger.info("bench %s/%s", model, spec["id"])
                pr = await self._run_one_prompt(client, model, spec)
                result.prompts.append(pr)

            total_eval_tokens = sum(p.eval_count for p in result.prompts)
            total_eval_seconds = sum(p.eval_duration_s for p in result.prompts)
            total_prompt_tokens = sum(p.prompt_eval_count for p in result.prompts)
            total_prompt_seconds = sum(p.prompt_eval_duration_s for p in result.prompts)

            result.total_eval_tokens = total_eval_tokens
            result.total_eval_seconds = round(total_eval_seconds, 3)
            result.tokens_per_second = round(
                total_eval_tokens / total_eval_seconds, 2
            ) if total_eval_seconds > 0 else 0.0
            result.prompt_eval_tps = round(
                total_prompt_tokens / total_prompt_seconds, 2
            ) if total_prompt_seconds > 0 else 0.0
            result.ttft_ms = next(
                (p.ttft_ms for p in result.prompts if p.ttft_ms is not None),
                None,
            )
        except Exception as exc:
            logger.exception("benchmark failed for %s: %s", model, exc)
            result.error = f"{type(exc).__name__}: {exc}"
        finally:
            result.finished_at = time.time()
            if owns_client:
                await client.aclose()
        return result

    async def run_models(
        self,
        models: Iterable[str],
        on_progress=None,
    ) -> list[BenchmarkResult]:
        results: list[BenchmarkResult] = []
        async with httpx.AsyncClient() as client:
            for model in models:
                if on_progress:
                    on_progress({"event": "start", "model": model})
                res = await self.run_model(model, client=client)
                results.append(res)
                if on_progress:
                    on_progress({"event": "done", "model": model, "result": res.to_dict()})
        return results


def load_results(path: Path = RESULTS_PATH) -> dict[str, Any]:
    if not path.is_file():
        return {"results": {}, "updated_at": None}
    try:
        return json.loads(path.read_text("utf-8"))
    except Exception as exc:
        logger.warning("failed to load %s: %s", path, exc)
        return {"results": {}, "updated_at": None}


def save_results(
    new_results: list[BenchmarkResult],
    path: Path = RESULTS_PATH,
) -> dict[str, Any]:
    existing = load_results(path)
    by_model: dict[str, Any] = dict(existing.get("results", {}))
    for r in new_results:
        by_model[r.model] = r.to_dict()
    payload = {"results": by_model, "updated_at": time.time()}
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(payload, indent=2), "utf-8")
    tmp.replace(path)
    return payload
