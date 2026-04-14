# zeus/bench/__main__.py — CLI entry: python -m zeus.bench [model ...]
from __future__ import annotations

import argparse
import asyncio
import logging
import sys

from zeus.bench.runner import BenchmarkRunner, save_results


async def _amain(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(
        prog="zeus.bench",
        description="Benchmark Ollama chat models on this host (tok/s, TTFT).",
    )
    parser.add_argument(
        "models",
        nargs="*",
        help="Model names to benchmark. Defaults to all chat models in Ollama.",
    )
    parser.add_argument(
        "--ollama-url",
        default=None,
        help="Override Ollama base URL (otherwise OLLAMA_URL env or default).",
    )
    parser.add_argument(
        "--no-save",
        action="store_true",
        help="Run but do not persist results to zeus/data/benchmarks.json.",
    )
    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="INFO logging.",
    )
    args = parser.parse_args(argv)

    logging.basicConfig(
        level=logging.INFO if args.verbose else logging.WARNING,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )

    runner_kwargs = {}
    if args.ollama_url:
        runner_kwargs["ollama_url"] = args.ollama_url
    runner = BenchmarkRunner(**runner_kwargs)

    import httpx
    async with httpx.AsyncClient() as client:
        models = args.models or await runner.list_models(client)

    if not models:
        print("No models to benchmark.", file=sys.stderr)
        return 1

    print(f"Benchmarking {len(models)} model(s) on {runner.host_label}: {', '.join(models)}")
    print()

    def progress(evt):
        if evt["event"] == "start":
            print(f"  → {evt['model']} ...", flush=True)
            return
        r = evt["result"]
        err = r.get("error")
        if err:
            print(f"    FAILED: {err}")
            return
        tps = r.get("tokens_per_second") or 0.0
        ttft = r.get("ttft_ms")
        pe = r.get("prompt_eval_tps") or 0.0
        total_tokens = r.get("total_eval_tokens") or 0
        ttft_str = f"{ttft:.0f} ms" if isinstance(ttft, (int, float)) else "n/a"
        note = "  (no tokens — model returned empty)" if total_tokens == 0 else ""
        print(
            f"    {tps:>6.1f} tok/s  "
            f"TTFT {ttft_str}  "
            f"prompt-eval {pe:.0f} tok/s  "
            f"[{total_tokens} tok]{note}"
        )

    results = await runner.run_models(models, on_progress=progress)

    if not args.no_save:
        payload = save_results(results)
        print()
        print(f"Saved {len(results)} result(s) to benchmarks store.")
        print(f"updated_at = {payload['updated_at']}")
    return 0


def main() -> None:
    sys.exit(asyncio.run(_amain(sys.argv[1:])))


if __name__ == "__main__":
    main()
