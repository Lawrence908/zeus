# zeus/ingest/run.py — Iris ingest CLI
# Usage:
#   python -m zeus.ingest.run --source markdown --glob "data/raw/**/*.md" --dry-run
#   python -m zeus.ingest.run --source chatgpt --path data/raw/chatgpt_export.json
#   python -m zeus.ingest.run --source all  # runs all configured sources from iris.yaml defaults
#
# Always run --dry-run first to preview chunk output before writing to mnemosyne.
import argparse
import asyncio
import logging
import sys
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s [%(name)s] %(levelname)s %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger("iris")


def build_sources(args) -> list:
    """Construct IngestSource instances from CLI args."""
    from zeus.ingest.sources.chatgpt import ChatGPTSource
    from zeus.ingest.sources.markdown import MarkdownSource

    sources = []

    if args.source in ("markdown", "all"):
        globs = args.glob if args.glob else ["**/*.md"]
        base = Path(args.base_dir) if args.base_dir else Path(".")
        sources.append(
            MarkdownSource(
                globs=globs,
                base_dir=base,
                chunk_size=args.chunk_size,
                chunk_overlap=args.chunk_overlap,
                user_id=args.user_id,
            )
        )

    if args.source in ("chatgpt", "all"):
        path = args.path or "zeus/data/raw/chatgpt_export.json"
        if not Path(path).exists():
            if args.source == "chatgpt":
                logger.error(f"chatgpt export not found: {path}")
                sys.exit(1)
            else:
                logger.warning(f"skipping chatgpt — file not found: {path}")
        else:
            sources.append(
                ChatGPTSource(
                    path=path,
                    chunk_size=args.chunk_size,
                    chunk_overlap=args.chunk_overlap,
                    user_id=args.user_id,
                )
            )

    if not sources:
        logger.error(f"no sources configured for --source={args.source!r}")
        sys.exit(1)

    return sources


async def main(args) -> None:
    from zeus.ingest.pipeline import run_ingest

    sources = build_sources(args)

    mode = "DRY RUN" if args.dry_run else "LIVE"
    logger.info(f"iris: starting {mode} ingest — {len(sources)} source(s)")

    results = await run_ingest(
        sources=sources,
        chunk_size=args.chunk_size,
        dry_run=args.dry_run,
    )

    # Summary table
    print("\n── Iris Ingest Summary ──────────────────────")
    total_processed = total_stored = total_errors = 0
    for r in results:
        status = "✓" if not r.errors else "⚠"
        print(f"  {status} {r.source:<20} {r.chunks_stored}/{r.chunks_processed} chunks stored")
        if r.errors:
            for err in r.errors[:5]:
                print(f"      ! {err}")
            if len(r.errors) > 5:
                print(f"      ... and {len(r.errors) - 5} more errors")
        total_processed += r.chunks_processed
        total_stored += r.chunks_stored
        total_errors += len(r.errors)

    print(f"  {'─' * 40}")
    print(f"  Total: {total_stored}/{total_processed} stored, {total_errors} errors")
    if args.dry_run:
        print("  [dry-run] nothing written to mnemosyne")
    print()


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description="Iris — Zeus ingest pipeline CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Preview markdown chunking without writing anything
  python -m zeus.ingest.run --source markdown --glob "zeus/data/raw/**/*.md" --dry-run

  # Ingest ChatGPT export (live)
  python -m zeus.ingest.run --source chatgpt --path zeus/data/raw/conversations.json

  # Run all sources with custom chunk size
  python -m zeus.ingest.run --source all --chunk-size 256 --dry-run
        """,
    )
    p.add_argument(
        "--source",
        choices=["markdown", "chatgpt", "all"],
        required=True,
        help="Which source type to ingest",
    )
    p.add_argument(
        "--path",
        help="Path to a single file (chatgpt source)",
    )
    p.add_argument(
        "--glob",
        nargs="+",
        help="Glob pattern(s) for markdown source (default: **/*.md)",
    )
    p.add_argument(
        "--base-dir",
        help="Base directory for glob expansion (default: .)",
    )
    p.add_argument(
        "--dry-run",
        action="store_true",
        help="Chunk and log without writing to mnemosyne",
    )
    p.add_argument(
        "--chunk-size",
        type=int,
        default=512,
        help="Words per chunk (default: 512)",
    )
    p.add_argument(
        "--chunk-overlap",
        type=int,
        default=64,
        help="Overlap words between chunks (default: 64)",
    )
    p.add_argument(
        "--user-id",
        default="chris",
        help="mem0 user ID to store memories under (default: chris)",
    )
    return p.parse_args()


if __name__ == "__main__":
    args = parse_args()
    asyncio.run(main(args))
