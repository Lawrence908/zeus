#!/usr/bin/env python3
# scripts/smoke_test.py — Zeus stack smoke test
# Verifies each layer of the stack is reachable and minimally functional.
# Run this before doing any ingest or query work.
#
# Usage:
#   python scripts/smoke_test.py
#   python scripts/smoke_test.py --skip-core   # if zeus-core isn't running yet
#   python scripts/smoke_test.py --skip-ingest # skip the dry-run ingest check
import argparse
import asyncio
import os
import sys
import time
from dataclasses import dataclass, field
from pathlib import Path

# Allow running from repo root without installing the package
sys.path.insert(0, str(Path(__file__).parent.parent))

from dotenv import load_dotenv

load_dotenv()

QDRANT_URL = os.getenv("QDRANT_URL", "http://localhost:6333")
OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434")
ZEUS_CORE_URL = os.getenv("ZEUS_CORE_URL", "http://localhost:8000")
EMBED_MODEL = os.getenv("ZEUS_EMBED_MODEL", "nomic-embed-text")

GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
CYAN = "\033[96m"
RESET = "\033[0m"
BOLD = "\033[1m"


@dataclass
class CheckResult:
    name: str
    passed: bool
    detail: str = ""
    latency_ms: float | None = None
    skipped: bool = False
    warnings: list[str] = field(default_factory=list)


def ok(name: str, detail: str = "", latency_ms: float | None = None, warnings: list[str] | None = None) -> CheckResult:
    return CheckResult(name=name, passed=True, detail=detail, latency_ms=latency_ms, warnings=warnings or [])


def fail(name: str, detail: str = "") -> CheckResult:
    return CheckResult(name=name, passed=False, detail=detail)


def skip(name: str, reason: str = "") -> CheckResult:
    return CheckResult(name=name, passed=True, detail=reason, skipped=True)


async def check_qdrant() -> CheckResult:
    import httpx
    try:
        t0 = time.monotonic()
        async with httpx.AsyncClient() as client:
            r = await client.get(f"{QDRANT_URL}/healthz", timeout=5)
        latency = (time.monotonic() - t0) * 1000
        if r.status_code == 200:
            return ok("Qdrant health", f"{QDRANT_URL}", latency)
        return fail("Qdrant health", f"HTTP {r.status_code}")
    except Exception as e:
        return fail("Qdrant health", f"{e}\n    → Is Qdrant running? Try: docker compose up qdrant -d")


async def check_qdrant_collections() -> CheckResult:
    import httpx
    try:
        async with httpx.AsyncClient() as client:
            r = await client.get(f"{QDRANT_URL}/collections", timeout=5)
        data = r.json()
        collections = [c["name"] for c in data.get("result", {}).get("collections", [])]
        detail = f"{len(collections)} collection(s): {collections}" if collections else "no collections yet (expected until first ingest)"
        return ok("Qdrant collections", detail)
    except Exception as e:
        return fail("Qdrant collections", str(e))


async def check_ollama() -> CheckResult:
    import httpx
    try:
        t0 = time.monotonic()
        async with httpx.AsyncClient() as client:
            r = await client.get(f"{OLLAMA_URL}/api/tags", timeout=5)
        latency = (time.monotonic() - t0) * 1000
        if r.status_code == 200:
            models = [m["name"] for m in r.json().get("models", [])]
            return ok("Ollama health", f"{len(models)} model(s) loaded", latency)
        return fail("Ollama health", f"HTTP {r.status_code}")
    except Exception as e:
        return fail("Ollama health", f"{e}\n    → Is Ollama running? Try: docker compose up ollama -d")


async def check_embed_model() -> CheckResult:
    """Verify nomic-embed-text is pulled and can embed a string."""
    import httpx
    try:
        # First check the model is listed
        async with httpx.AsyncClient() as client:
            r = await client.get(f"{OLLAMA_URL}/api/tags", timeout=5)
        models = [m["name"] for m in r.json().get("models", [])]
        model_present = any(EMBED_MODEL in m for m in models)

        if not model_present:
            return fail(
                f"Embed model ({EMBED_MODEL})",
                f"Model not found in Ollama.\n    → Pull it: ollama pull {EMBED_MODEL}",
            )

        # Actually embed a short string to confirm it works end-to-end
        t0 = time.monotonic()
        async with httpx.AsyncClient() as client:
            r = await client.post(
                f"{OLLAMA_URL}/api/embeddings",
                json={"model": EMBED_MODEL, "prompt": "zeus smoke test"},
                timeout=30,
            )
        latency = (time.monotonic() - t0) * 1000

        if r.status_code != 200:
            return fail(f"Embed model ({EMBED_MODEL})", f"Embed call failed: HTTP {r.status_code}")

        embedding = r.json().get("embedding", [])
        dim = len(embedding)
        if dim == 0:
            return fail(f"Embed model ({EMBED_MODEL})", "Got empty embedding vector")

        warnings = []
        if dim != 768:
            warnings.append(f"Expected 768-dim vector, got {dim} — check QDRANT_COLLECTION embedding_model_dims in memory/config.py")

        return ok(f"Embed model ({EMBED_MODEL})", f"{dim}-dim vector in {latency:.0f}ms", latency, warnings)

    except Exception as e:
        return fail(f"Embed model ({EMBED_MODEL})", str(e))


async def check_zeus_core() -> CheckResult:
    import httpx
    try:
        t0 = time.monotonic()
        async with httpx.AsyncClient() as client:
            r = await client.get(f"{ZEUS_CORE_URL}/status", timeout=5)
        latency = (time.monotonic() - t0) * 1000
        if r.status_code == 200:
            data = r.json()
            env = data.get("environment", "?")
            version = data.get("version", "?")
            services = {s["name"]: s["status"] for s in data.get("services", [])}
            detail = f"v{version} [{env}] — services: {services}"
            warnings = [f"{name} is down" for name, status in services.items() if status != "up"]
            return ok("Zeus Core /status", detail, latency, warnings)
        return fail("Zeus Core /status", f"HTTP {r.status_code}")
    except Exception as e:
        return fail("Zeus Core /status", f"{e}\n    → Start it: uvicorn zeus.core.main:app --reload")


async def check_iris_dry_run() -> CheckResult:
    """Run a tiny in-memory dry_run ingest to verify the pipeline code path."""
    try:
        import tempfile

        from zeus.ingest.pipeline import run_ingest
        from zeus.ingest.sources.markdown import MarkdownSource

        # Write a tiny temp markdown file
        sample = "# Zeus Test\n\nThis is a smoke test chunk. It verifies that Iris can read, parse, and chunk a markdown file correctly.\n"
        with tempfile.NamedTemporaryFile(suffix=".md", mode="w", delete=False) as f:
            f.write(sample)
            tmp_path = Path(f.name)

        source = MarkdownSource(
            globs=[tmp_path.name],
            base_dir=tmp_path.parent,
            chunk_size=64,
            chunk_overlap=8,
        )

        t0 = time.monotonic()
        results = await run_ingest([source], dry_run=True)
        latency = (time.monotonic() - t0) * 1000

        tmp_path.unlink(missing_ok=True)

        r = results[0]
        if r.chunks_processed == 0:
            return fail("Iris dry-run ingest", "No chunks produced from test document")
        if r.errors:
            return fail("Iris dry-run ingest", f"Errors: {r.errors}")

        return ok("Iris dry-run ingest", f"{r.chunks_processed} chunk(s) from test doc in {latency:.0f}ms", latency)

    except Exception as e:
        return fail("Iris dry-run ingest", str(e))


def print_result(r: CheckResult) -> None:
    if r.skipped:
        icon = f"{YELLOW}SKIP{RESET}"
    elif r.passed:
        icon = f"{GREEN} OK {RESET}"
    else:
        icon = f"{RED}FAIL{RESET}"

    latency_str = f"  {r.latency_ms:.0f}ms" if r.latency_ms is not None else ""
    print(f"  [{icon}] {r.name}{latency_str}")

    if r.detail:
        # indent detail lines
        for line in r.detail.split("\n"):
            print(f"         {line}")

    for w in r.warnings:
        print(f"         {YELLOW}⚠ {w}{RESET}")


async def run_checks(args: argparse.Namespace) -> int:
    print(f"\n{BOLD}{CYAN}── Zeus Stack Smoke Test ────────────────────{RESET}")
    print(f"  Qdrant:    {QDRANT_URL}")
    print(f"  Ollama:    {OLLAMA_URL}")
    print(f"  Zeus Core: {ZEUS_CORE_URL}")
    print(f"  Env:       {os.getenv('ZEUS_ENV', 'dev')}")
    print()

    checks: list[CheckResult] = []

    # Layer 1: Infrastructure
    print(f"{BOLD}Infrastructure{RESET}")
    checks.append(await check_qdrant())
    checks.append(await check_qdrant_collections())
    checks.append(await check_ollama())
    print()

    # Layer 2: Models
    print(f"{BOLD}Models{RESET}")
    checks.append(await check_embed_model())
    print()

    # Layer 3: Zeus services
    print(f"{BOLD}Zeus Services{RESET}")
    if args.skip_core:
        checks.append(skip("Zeus Core /status", "skipped via --skip-core"))
    else:
        checks.append(await check_zeus_core())

    if args.skip_ingest:
        checks.append(skip("Iris dry-run ingest", "skipped via --skip-ingest"))
    else:
        checks.append(await check_iris_dry_run())
    print()

    # Print all results
    print(f"{BOLD}Results{RESET}")
    for r in checks:
        print_result(r)

    failures = [r for r in checks if not r.passed and not r.skipped]
    warnings_total = sum(len(r.warnings) for r in checks)

    print()
    if not failures:
        status = f"{GREEN}{BOLD}All checks passed{RESET}"
        if warnings_total:
            status += f" {YELLOW}({warnings_total} warning(s)){RESET}"
        print(f"  {status}")
        print()
        if not args.skip_ingest and not args.skip_core:
            print(f"  {CYAN}Ready to ingest. Try:{RESET}")
            print(f"    python -m zeus.ingest.run --source markdown --glob 'zeus/data/raw/**/*.md' --dry-run")
        return 0
    else:
        print(f"  {RED}{BOLD}{len(failures)} check(s) failed{RESET}")
        print()
        return 1


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Zeus stack smoke test")
    p.add_argument("--skip-core", action="store_true", help="Skip Zeus Core /status check")
    p.add_argument("--skip-ingest", action="store_true", help="Skip Iris dry-run ingest check")
    return p.parse_args()


if __name__ == "__main__":
    args = parse_args()
    sys.exit(asyncio.run(run_checks(args)))
