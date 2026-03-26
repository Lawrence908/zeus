# zeus/ingest/run.py — Iris ingest CLI
# Usage:
#   python -m zeus.ingest.run --source markdown --glob "data/raw/**/*.md" --dry-run
#   python -m zeus.ingest.run --source chatgpt --path zeus/data/raw/chat-history
#   python -m zeus.ingest.run --source chatgpt --llm claude   # fast cloud extraction
#   python -m zeus.ingest.run --source all  # runs all configured sources from iris.yaml defaults
#
# Always run --dry-run first to preview chunk output before writing to mnemosyne.
import argparse
import asyncio
import logging
import os
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s [%(name)s] %(levelname)s %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger("iris")


def _fmt_duration(seconds: float) -> str:
    """Human-readable duration string."""
    if seconds < 60:
        return f"{seconds:.1f}s"
    minutes, secs = divmod(int(seconds), 60)
    hours, minutes = divmod(minutes, 60)
    if hours:
        return f"{hours}h {minutes}m {secs}s"
    return f"{minutes}m {secs}s"


def build_sources(args) -> list:
    """Construct IngestSource instances from CLI args."""
    from zeus.ingest.sources.bookmarks import BookmarksSource
    from zeus.ingest.sources.chatgpt import ChatGPTSource
    from zeus.ingest.sources.context_pack import ContextPackSource
    from zeus.ingest.sources.email import EmailSource
    from zeus.ingest.sources.gcal import GoogleCalendarSource
    from zeus.ingest.sources.git import GitSource
    from zeus.ingest.sources.markdown import MarkdownSource
    from zeus.ingest.sources.obsidian import ObsidianSource

    sources = []

    if args.source in ("context_pack", "all"):
        context_pack_path = args.path or "zeus/data/raw/context_pack.md"
        if not Path(context_pack_path).exists():
            if args.source == "context_pack":
                logger.error(f"context pack not found: {context_pack_path}")
                sys.exit(1)
            logger.warning(f"skipping context_pack — file not found: {context_pack_path}")
        else:
            sources.append(
                ContextPackSource(
                    path=context_pack_path,
                    chunk_size=min(args.chunk_size, 256),
                    chunk_overlap=min(args.chunk_overlap, 32),
                    user_id=args.user_id,
                )
            )

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
        path = args.path or "zeus/data/raw/chat-history"
        if not Path(path).exists():
            # Fall back to legacy single-file path
            legacy = Path("zeus/data/raw/chatgpt_export.json")
            if legacy.exists():
                path = str(legacy)
            elif args.source == "chatgpt":
                logger.error(f"chatgpt export not found: {path}")
                sys.exit(1)
            else:
                logger.warning(f"skipping chatgpt — not found: {path}")
                path = None

        if path:
            sources.append(
                ChatGPTSource(
                    path=path,
                    chunk_size=args.chunk_size,
                    chunk_overlap=args.chunk_overlap,
                    user_id=args.user_id,
                )
            )

    if args.source in ("email", "all"):
        try:
            cfg = EmailSource.from_env(limit=args.email_limit)
        except Exception as e:
            if args.source == "email":
                logger.error(f"email config invalid: {e}")
                sys.exit(1)
            logger.warning(f"skipping email — config invalid: {e}")
        else:
            sources.append(
                EmailSource(
                    config=cfg,
                    chunk_size=args.chunk_size,
                    chunk_overlap=args.chunk_overlap,
                    user_id=args.user_id,
                )
            )

    if args.source in ("obsidian", "all"):
        vault_path = args.path or os.getenv("OBSIDIAN_VAULT_PATH", "")
        if not vault_path or not Path(vault_path).is_dir():
            if args.source == "obsidian":
                logger.error("obsidian vault not found — set OBSIDIAN_VAULT_PATH or use --path")
                sys.exit(1)
            if vault_path:
                logger.warning("skipping obsidian — vault not found: %s", vault_path)
        else:
            sources.append(
                ObsidianSource(
                    vault_path=vault_path,
                    chunk_size=args.chunk_size,
                    chunk_overlap=args.chunk_overlap,
                    user_id=args.user_id,
                )
            )

    if args.source in ("git", "all"):
        repo_path = args.path or os.getenv("ZEUS_REPO_PATH", ".")
        if not Path(repo_path, ".git").is_dir():
            if args.source == "git":
                logger.error("git repo not found at %s — use --path or set ZEUS_REPO_PATH", repo_path)
                sys.exit(1)
            logger.warning("skipping git — no .git directory at %s", repo_path)
        else:
            sources.append(
                GitSource(
                    repo_path=repo_path,
                    max_commits=args.git_max_commits,
                    user_id=args.user_id,
                )
            )

    if args.source in ("gcal", "all"):
        try:
            sources.append(
                GoogleCalendarSource(
                    days_back=args.gcal_days_back,
                    days_forward=args.gcal_days_forward,
                    user_id=args.user_id,
                )
            )
        except Exception as exc:
            if args.source == "gcal":
                logger.error("gcal config invalid: %s", exc)
                sys.exit(1)
            logger.warning("skipping gcal — %s", exc)

    if args.source in ("bookmarks", "all"):
        export_path = args.path or os.getenv("BOOKMARKS_EXPORT_PATH", "zeus/data/raw/bookmarks.html")
        if not Path(export_path).exists():
            if args.source == "bookmarks":
                logger.error("bookmarks export not found: %s", export_path)
                sys.exit(1)
            logger.warning("skipping bookmarks — export not found: %s", export_path)
        else:
            sources.append(
                BookmarksSource(
                    export_path=export_path,
                    user_id=args.user_id,
                )
            )

    if not sources:
        logger.error(f"no sources configured for --source={args.source!r}")
        sys.exit(1)

    return sources


async def main(args) -> None:
    from zeus.ingest.pipeline import run_ingest
    from zeus.memory.config import get_token_usage, reset_token_usage

    if args.llm:
        os.environ["ZEUS_LLM"] = args.llm
        logger.info(f"iris: LLM override → {args.llm}")

    sources = build_sources(args)

    mode = "DRY RUN" if args.dry_run else "LIVE"
    llm_label = args.llm or os.getenv("ZEUS_LLM", "auto")
    logger.info(f"iris: starting {mode} ingest — {len(sources)} source(s), llm={llm_label}")

    reset_token_usage()
    wall_start = time.monotonic()
    start_ts = datetime.now(timezone.utc)

    results = await run_ingest(
        sources=sources,
        chunk_size=args.chunk_size,
        dry_run=args.dry_run,
    )

    wall_elapsed = time.monotonic() - wall_start
    tokens = get_token_usage()

    _print_summary(results, args, llm_label, wall_elapsed, start_ts, tokens)


def _print_summary(results, args, llm_label, wall_elapsed, start_ts, tokens):
    """Print a detailed ingest summary to stdout."""
    total_processed = total_stored = total_errors = 0
    total_ops: dict[str, int] = {"ADD": 0, "UPDATE": 0, "DELETE": 0, "NONE": 0}

    print()
    print("┌─────────────────────────────────────────────────────────┐")
    print("│                  Iris Ingest Summary                    │")
    print("├─────────────────────────────────────────────────────────┤")

    for r in results:
        status = "✓" if not r.errors else "⚠"
        rate = r.chunks_stored / r.elapsed_sec if r.elapsed_sec > 0 else 0
        print(f"│  {status} {r.source}")
        print(f"│    Chunks: {r.chunks_stored}/{r.chunks_processed} stored "
              f"in {_fmt_duration(r.elapsed_sec)} "
              f"({rate:.2f} chunks/s)")

        ops_parts = []
        for op in ("ADD", "UPDATE", "DELETE", "NONE"):
            count = r.mem0_ops.get(op, 0)
            if count > 0:
                ops_parts.append(f"{count} {op}")
            total_ops[op] += count
        if ops_parts:
            print(f"│    Memory ops: {', '.join(ops_parts)}")

        if r.errors:
            print(f"│    Errors: {len(r.errors)}")
            for err in r.errors[:3]:
                print(f"│      ! {err[:80]}")
            if len(r.errors) > 3:
                print(f"│      ... and {len(r.errors) - 3} more")

        total_processed += r.chunks_processed
        total_stored += r.chunks_stored
        total_errors += len(r.errors)

    print("├─────────────────────────────────────────────────────────┤")

    overall_rate = total_stored / wall_elapsed if wall_elapsed > 0 else 0
    print(f"│  Chunks:     {total_stored}/{total_processed} stored, "
          f"{total_errors} errors")
    print(f"│  Wall time:  {_fmt_duration(wall_elapsed)} "
          f"({overall_rate:.2f} chunks/s)")
    print(f"│  Started:    {start_ts.strftime('%Y-%m-%d %H:%M:%S UTC')}")

    ops_line = ", ".join(f"{v} {k}" for k, v in total_ops.items() if v > 0)
    if ops_line:
        print(f"│  Memory ops: {ops_line}")

    if tokens.llm_calls > 0:
        print(f"│  LLM calls:  {tokens.llm_calls}")
        print(f"│  Tokens:     {tokens.input_tokens:,} in + "
              f"{tokens.output_tokens:,} out = "
              f"{tokens.total_tokens:,} total")

    print(f"│  LLM:        {llm_label}")
    if args.dry_run:
        print("│  [dry-run]   Nothing written to mnemosyne")

    print("└─────────────────────────────────────────────────────────┘")
    print()


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description="Iris — Zeus ingest pipeline CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Preview markdown chunking without writing anything
  python -m zeus.ingest.run --source markdown --glob "zeus/data/raw/**/*.md" --dry-run

  # Ingest ChatGPT export using Claude for fast extraction
  python -m zeus.ingest.run --source chatgpt --llm claude

  # Ingest with local Ollama (slow but free)
  python -m zeus.ingest.run --source chatgpt --llm ollama

  # Run all sources with custom chunk size
  python -m zeus.ingest.run --source all --chunk-size 256 --dry-run
        """,
    )
    p.add_argument(
        "--source",
        choices=["context_pack", "markdown", "chatgpt", "email",
                 "obsidian", "git", "gcal", "bookmarks", "all"],
        required=True,
        help="Which source type to ingest",
    )
    p.add_argument(
        "--path",
        help="Path to a file or directory (chatgpt: dir with conversations-NNN.json)",
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
        "--llm",
        choices=["claude", "ollama"],
        default=None,
        help="LLM for fact extraction (overrides ZEUS_LLM env var)",
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
    p.add_argument(
        "--email-limit",
        type=int,
        default=200,
        help="Max number of emails to ingest (default: 200; newest first)",
    )
    p.add_argument(
        "--git-max-commits",
        type=int,
        default=500,
        help="Max git commits to ingest (default: 500)",
    )
    p.add_argument(
        "--gcal-days-back",
        type=int,
        default=90,
        help="Days back to fetch Google Calendar events (default: 90)",
    )
    p.add_argument(
        "--gcal-days-forward",
        type=int,
        default=30,
        help="Days forward to fetch Google Calendar events (default: 30)",
    )
    return p.parse_args()


if __name__ == "__main__":
    args = parse_args()
    asyncio.run(main(args))
