# zeus/ingest/run.py — Iris ingest CLI
#
# Local raw context (paths relative to Zeus repo root):
#   zeus/data/raw/chat-history/       — ChatGPT exports (conversations-*.json)
#   zeus/data/raw/context-pack-core/ — curated markdown pack (directory of .md files)
#   zeus/data/raw/jobkit-archive/    — JobKit archive (.md ingested; .yml not handled by markdown source)
#   zeus/data/raw/notes/             — symlinks / vault mirrors (use **/*.md under this tree)
#
# Usage (run from repo root; always --dry-run first):
#   python -m zeus.ingest.run --source chatgpt --path zeus/data/raw/chat-history --dry-run
#   python -m zeus.ingest.run --source chatgpt --path zeus/data/raw/chat-history --llm claude
#
#   python -m zeus.ingest.run --source markdown --base-dir zeus/data/raw/context-pack-core --dry-run
#   python -m zeus.ingest.run --source markdown --base-dir zeus/data/raw/jobkit-archive --dry-run
#   python -m zeus.ingest.run --source markdown --base-dir zeus/data/raw/notes --dry-run
#
# Curated baseline (same file as in default --source all; use alone to skip other sources):
#   python -m zeus.ingest.run --source context_pack --path zeus/data/raw/context_pack.md --dry-run
#
#   python -m zeus.ingest.run --dry-run              # default --source all (see below)
#
# Default ingest (--source all): context_pack.md + markdown under raw/{context-pack-core,jobkit-archive,notes},
# plus chatgpt, email, obsidian, git, gcal, bookmarks when configured / paths exist. Omit --source to use all.
import argparse
import asyncio
import logging
import os
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Literal

from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger("iris")

_NOISY_LOGGERS = (
    "httpx",
    "httpcore",
    "httpcore.http11",
    "httpcore.connection",
    "mem0",
    "mem0.memory",
    "mem0.vector_stores",
    "mem0.vector_stores.qdrant",
    "qdrant_client",
    "openai",
    "anthropic",
)


def configure_ingest_logging(
    *,
    plain: bool,
    verbose: bool,
    log_console: object | None = None,
) -> None:
    """Console logging for Iris CLI: readable by default; --verbose enables firehose."""
    root = logging.getLogger()
    for h in root.handlers[:]:
        root.removeHandler(h)

    level = logging.DEBUG if verbose else logging.INFO
    root.setLevel(level)

    if plain:
        logging.basicConfig(
            level=level,
            format="%(asctime)s [%(name)s] %(levelname)s %(message)s",
            datefmt="%H:%M:%S",
            force=True,
        )
    else:
        try:
            from rich.console import Console
            from rich.logging import RichHandler

            rc = log_console if log_console is not None else Console(stderr=True)
            logging.basicConfig(
                level=level,
                format="%(message)s",
                datefmt="%H:%M:%S",
                handlers=[
                    RichHandler(
                        console=rc,
                        rich_tracebacks=True,
                        show_path=False,
                        markup=False,
                    )
                ],
                force=True,
            )
        except ImportError:
            logging.basicConfig(
                level=level,
                format="%(asctime)s [%(name)s] %(levelname)s %(message)s",
                datefmt="%H:%M:%S",
                force=True,
            )

    logging.getLogger("iris").setLevel(logging.DEBUG if verbose else logging.INFO)

    if not verbose:
        for name in _NOISY_LOGGERS:
            logging.getLogger(name).setLevel(logging.WARNING)


def _ingest_ui_from_args(args: argparse.Namespace) -> Literal["auto", "rich", "plain"]:
    if getattr(args, "plain", False):
        return "plain"
    if getattr(args, "rich", False):
        return "rich"
    return "auto"


def _use_rich_output(args: argparse.Namespace) -> bool:
    """Rich tables / colors for summary when not --plain."""
    return not getattr(args, "plain", False)

# Single curated file (ContextPackSource — high-priority metadata). Always this path for --source all
# so --path can target chatgpt/obsidian/etc. without breaking the context pack.
DEFAULT_CONTEXT_PACK_PATH = "zeus/data/raw/context_pack.md"

# Markdown globs under zeus/data/raw for --source all (context_pack.md is ingested separately above).
_RAW_MARKDOWN_GLOBS_FOR_ALL = [
    "context-pack-core/**/*.md",
    "jobkit-archive/**/*.md",
    "notes/**/*.md",
]


def _fmt_duration(seconds: float) -> str:
    """Human-readable duration string."""
    if seconds < 60:
        return f"{seconds:.1f}s"
    minutes, secs = divmod(int(seconds), 60)
    hours, minutes = divmod(minutes, 60)
    if hours:
        return f"{hours}h {minutes}m {secs}s"
    return f"{minutes}m {secs}s"


def _apply_config_overrides(sources: list, ingest_cfg) -> list:
    """Apply target overrides from zeus/ingest/config.yaml onto built sources.

    Each source class has a class-level ``target`` default from task D; the
    config file is allowed to override it per-source. Also rejects Phase 2-only
    targets (reference) since the pipeline does not yet handle them.
    """
    if ingest_cfg is None:
        return sources
    # Class name → config key (lowercase without the "Source" suffix, with
    # a couple of special cases that don't follow the pattern).
    CLASS_TO_KEY = {
        "ContextPackSource": "context_pack",
        "MarkdownSource": "markdown",
        "ChatGPTSource": "chatgpt",
        "ObsidianSource": "obsidian",
        "EmailSource": "email",
        "NewsletterSource": "newsletter",
        "BookmarksSource": "bookmarks",
        "GitSource": "git",
        "GoogleCalendarSource": "gcal",
        "DocsSource": "docs",
        "KiwixZimSource": "kiwix_zim",
    }
    for source in sources:
        key = CLASS_TO_KEY.get(type(source).__name__)
        if not key:
            continue
        src_cfg = ingest_cfg.sources.get(key)
        if src_cfg is None:
            continue
        src_cfg.reject_if_phase2_only(key)
        source.target = src_cfg.target
        if key == "kiwix_zim":
            if src_cfg.books is not None:
                source.books = set(src_cfg.books)
            if src_cfg.max_zim_mb is not None:
                source.max_zim_mb = src_cfg.max_zim_mb
    return sources


def _filter_sources_by_target(sources: list, target_filter: str) -> list:
    """--target {memory,knowledge,both} keeps only sources routed to the chosen layer."""
    if target_filter in ("both", "all", ""):
        return sources
    kept = [s for s in sources if getattr(s, "target", "memory") == target_filter]
    dropped = [type(s).__name__ for s in sources if s not in kept]
    if dropped:
        logger.info(
            "iris: --target=%s filter dropped %s source(s): %s",
            target_filter,
            len(dropped),
            ", ".join(dropped),
        )
    return kept


def build_sources(args, *, cli_mode: bool = True) -> list:
    """Construct IngestSource instances from CLI args.

    When cli_mode is False (HTTP trigger), missing required sources raise ValueError
    instead of sys.exit so FastAPI can return 4xx.
    """

    def fail_hard(msg: str) -> None:
        logger.error(msg)
        if cli_mode:
            sys.exit(1)
        raise ValueError(msg)

    from zeus.ingest.sources.bookmarks import BookmarksSource
    from zeus.ingest.sources.chatgpt import ChatGPTSource
    from zeus.ingest.sources.context_pack import ContextPackSource
    from zeus.ingest.sources.docs import DocsSource
    from zeus.ingest.sources.email import EmailSource
    from zeus.ingest.sources.gcal import GoogleCalendarSource
    from zeus.ingest.sources.git import GitSource
    from zeus.ingest.sources.kiwix_zim import KiwixZimSource
    from zeus.ingest.sources.markdown import MarkdownSource
    from zeus.ingest.sources.newsletter import NewsletterSource
    from zeus.ingest.sources.obsidian import ObsidianSource

    sources = []

    if args.source in ("context_pack", "all"):
        if args.source == "context_pack":
            context_pack_path = args.path or DEFAULT_CONTEXT_PACK_PATH
        else:
            context_pack_path = DEFAULT_CONTEXT_PACK_PATH
        if not Path(context_pack_path).exists():
            if args.source == "context_pack":
                fail_hard(f"context pack not found: {context_pack_path}")
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
        if args.source == "all" and args.glob is None and args.base_dir is None:
            globs = _RAW_MARKDOWN_GLOBS_FOR_ALL
            base = Path("zeus/data/raw")
        else:
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
                fail_hard(f"chatgpt export not found: {path}")
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
                fail_hard(f"email config invalid: {e}")
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
                fail_hard("obsidian vault not found — set OBSIDIAN_VAULT_PATH or use --path")
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
                fail_hard(f"git repo not found at {repo_path} — use --path or set ZEUS_REPO_PATH")
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
                fail_hard(f"gcal config invalid: {exc}")
            logger.warning("skipping gcal — %s", exc)

    if args.source in ("bookmarks", "all"):
        export_path = args.path or os.getenv("BOOKMARKS_EXPORT_PATH", "zeus/data/raw/bookmarks.html")
        if not Path(export_path).exists():
            if args.source == "bookmarks":
                fail_hard(f"bookmarks export not found: {export_path}")
            logger.warning("skipping bookmarks — export not found: %s", export_path)
        else:
            sources.append(
                BookmarksSource(
                    export_path=export_path,
                    user_id=args.user_id,
                )
            )

    if args.source in ("docs", "all"):
        repo_root = args.path or "."
        if not Path(repo_root, "CLAUDE.md").is_file():
            if args.source == "docs":
                fail_hard(f"docs: CLAUDE.md not found under {repo_root}; pass --path <repo-root>")
            logger.warning("skipping docs, no CLAUDE.md under %s", repo_root)
        else:
            sources.append(
                DocsSource(
                    repo_root=repo_root,
                    chunk_size=args.chunk_size,
                    chunk_overlap=args.chunk_overlap,
                    user_id=args.user_id,
                )
            )

    if args.source in ("kiwix_zim", "all"):
        zim_dir = args.path or os.getenv("ZEUS_KIWIX_ZIM_DIR", "")
        # books list + max_zim_mb come from zeus/ingest/config.yaml via
        # _apply_config_overrides; CLI only supplies zim_dir.
        if not zim_dir or not Path(zim_dir).is_dir():
            if args.source == "kiwix_zim":
                fail_hard(
                    "kiwix_zim: zim_dir not found — "
                    "set ZEUS_KIWIX_ZIM_DIR or use --path"
                )
            if zim_dir:
                logger.warning("skipping kiwix_zim — zim_dir not found: %s", zim_dir)
        else:
            sources.append(
                KiwixZimSource(
                    zim_dir=zim_dir,
                    chunk_size=args.chunk_size,
                    chunk_overlap=args.chunk_overlap,
                    user_id=args.user_id,
                )
            )

    if args.source in ("newsletter", "all"):
        try:
            nl_cfg = NewsletterSource.from_env()
        except Exception as e:
            if args.source == "newsletter":
                fail_hard(f"newsletter config invalid: {e}")
            logger.warning("skipping newsletter — config invalid: %s", e)
        else:
            sources.append(
                NewsletterSource(
                    config=nl_cfg,
                    chunk_size=args.chunk_size,
                    chunk_overlap=args.chunk_overlap,
                    user_id=args.user_id,
                )
            )

    if not sources:
        fail_hard(f"no sources configured for --source={args.source!r}")

    return sources


def build_sources_for_trigger(
    source: str,
    *,
    user_id: str = "user",
    chunk_size: int = 512,
    chunk_overlap: int = 64,
) -> list:
    """Build ingest sources for a named trigger (MCP / HTTP). Raises ValueError on failure."""
    from types import SimpleNamespace

    args = SimpleNamespace(
        source=source,
        path=None,
        glob=None,
        base_dir=None,
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        user_id=user_id,
        email_limit=200,
        git_max_commits=500,
        gcal_days_back=90,
        gcal_days_forward=30,
        config=None,
        no_config=False,
        target="both",
    )
    return build_sources(args, cli_mode=False)


async def main(args, *, log_console: object | None = None) -> None:
    from zeus.ingest.config import DEFAULT_CONFIG_PATH, load_ingest_config
    from zeus.ingest.pipeline import run_ingest
    from zeus.memory.config import get_token_usage, reset_token_usage

    if args.llm:
        os.environ["ZEUS_LLM"] = args.llm
        logger.info("iris: LLM override → %s", args.llm)

    ingest_cfg = None
    if not args.no_config:
        cfg_path = args.config or DEFAULT_CONFIG_PATH
        try:
            ingest_cfg = load_ingest_config(cfg_path)
            logger.info("iris: loaded routing config from %s", cfg_path)
        except FileNotFoundError:
            if args.config:
                logger.error("iris: --config file not found: %s", cfg_path)
                sys.exit(1)
            logger.info(
                "iris: no %s found; using class-level source targets", cfg_path
            )
        except Exception as exc:
            logger.error("iris: failed to load ingest config: %s", exc)
            sys.exit(1)

    sources = build_sources(args)
    sources = _apply_config_overrides(sources, ingest_cfg)
    sources = _filter_sources_by_target(sources, args.target)

    if not sources:
        logger.error(
            "iris: no sources remain after applying --target=%s filter", args.target
        )
        sys.exit(1)

    routing = ", ".join(
        f"{type(s).__name__}→{getattr(s, 'target', 'memory')}" for s in sources
    )
    logger.info("iris: routing — %s", routing)

    mode = "DRY RUN" if args.dry_run else "LIVE"
    llm_label = args.llm or os.getenv("ZEUS_LLM", "auto")
    logger.info(
        "iris: starting %s ingest — %s source(s), llm=%s",
        mode,
        len(sources),
        llm_label,
    )

    reset_token_usage()
    wall_start = time.monotonic()
    start_ts = datetime.now(timezone.utc)

    results = await run_ingest(
        sources=sources,
        chunk_size=args.chunk_size,
        dry_run=args.dry_run,
        ingest_ui=_ingest_ui_from_args(args),
        console=log_console,
    )

    wall_elapsed = time.monotonic() - wall_start
    tokens = get_token_usage()

    _print_summary(
        results,
        args,
        llm_label,
        wall_elapsed,
        start_ts,
        tokens,
        use_rich=_use_rich_output(args),
    )


def _print_summary(
    results,
    args,
    llm_label,
    wall_elapsed,
    start_ts,
    tokens,
    *,
    use_rich: bool = False,
):
    """Print a detailed ingest summary to stdout."""
    if use_rich:
        try:
            _print_summary_rich(
                results, args, llm_label, wall_elapsed, start_ts, tokens
            )
            return
        except ImportError:
            pass

    _print_summary_plain(
        results, args, llm_label, wall_elapsed, start_ts, tokens
    )


def _print_summary_plain(results, args, llm_label, wall_elapsed, start_ts, tokens):
    total_processed = total_stored = total_errors = 0
    total_ops: dict[str, int] = {"ADDED": 0, "SKIPPED": 0, "RAW_FALLBACKS": 0, "EXTRACTIONS": 0}

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
        for op in ("ADDED", "SKIPPED", "RAW_FALLBACKS", "EXTRACTIONS"):
            count = r.memory_ops.get(op, 0)
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


def _print_summary_rich(results, args, llm_label, wall_elapsed, start_ts, tokens):
    from rich.console import Console
    from rich.markdown import Markdown
    from rich.panel import Panel
    from rich.table import Table

    total_processed = total_stored = total_errors = 0
    total_ops: dict[str, int] = {"ADDED": 0, "SKIPPED": 0, "RAW_FALLBACKS": 0, "EXTRACTIONS": 0}

    console = Console(highlight=False)
    table = Table(show_header=True, header_style="bold cyan", expand=True)
    table.add_column("Source", style="bold", ratio=1)
    table.add_column("Result", justify="center")
    table.add_column("Chunks", justify="right")
    table.add_column("Time", justify="right")
    table.add_column("Rate", justify="right")
    table.add_column("Memory ops", ratio=1)

    for r in results:
        status = "ok" if not r.errors else "warnings"
        status_style = "green" if not r.errors else "yellow"
        rate = r.chunks_stored / r.elapsed_sec if r.elapsed_sec > 0 else 0
        ops_parts = []
        for op in ("ADDED", "SKIPPED", "RAW_FALLBACKS", "EXTRACTIONS"):
            count = r.memory_ops.get(op, 0)
            if count > 0:
                ops_parts.append(f"{count} {op}")
            total_ops[op] += count
        ops_str = ", ".join(ops_parts) if ops_parts else "—"
        table.add_row(
            r.source,
            f"[{status_style}]{status}[/{status_style}]",
            f"{r.chunks_stored}/{r.chunks_processed}",
            _fmt_duration(r.elapsed_sec),
            f"{rate:.2f}/s",
            ops_str,
        )
        total_processed += r.chunks_processed
        total_stored += r.chunks_stored
        total_errors += len(r.errors)

    overall_rate = total_stored / wall_elapsed if wall_elapsed > 0 else 0
    mode = "DRY RUN" if args.dry_run else "LIVE"
    ops_line = ", ".join(f"{v} {k}" for k, v in total_ops.items() if v > 0)

    lines = [
        f"**Mode:** {mode} · **LLM:** {llm_label}",
        "",
        f"- **Chunks:** {total_stored}/{total_processed} stored, "
        f"{total_errors} errors",
        f"- **Wall time:** {_fmt_duration(wall_elapsed)} "
        f"({overall_rate:.2f} chunks/s)",
        f"- **Started:** {start_ts.strftime('%Y-%m-%d %H:%M:%S UTC')}",
    ]
    if ops_line:
        lines.append(f"- **Memory ops:** {ops_line}")
    if tokens.llm_calls > 0:
        lines.append(
            f"- **LLM calls:** {tokens.llm_calls} · "
            f"**Tokens:** {tokens.input_tokens:,} in + "
            f"{tokens.output_tokens:,} out = {tokens.total_tokens:,} total"
        )
    if args.dry_run:
        lines.append("- *Nothing written to mnemosyne (dry-run)*")

    md = Markdown("\n".join(lines))

    console.print()
    console.print(
        Panel(
            table,
            title="[bold]Iris ingest — per source[/bold]",
            border_style="cyan",
        )
    )
    console.print(Panel(md, title="[bold]Summary[/bold]", border_style="dim"))
    console.print()

    for r in results:
        if not r.errors:
            continue
        console.print(f"[yellow]Errors — {r.source}[/yellow]")
        for err in r.errors[:5]:
            console.print(f"  • {err[:120]}")
        if len(r.errors) > 5:
            console.print(f"  … and {len(r.errors) - 5} more")


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description="Iris — Zeus ingest pipeline CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Raw layout: zeus/data/raw/{chat-history,context-pack-core,jobkit-archive,notes}/

  python -m zeus.ingest.run --source chatgpt --path zeus/data/raw/chat-history --dry-run
  python -m zeus.ingest.run --source chatgpt --path zeus/data/raw/chat-history --llm claude

  python -m zeus.ingest.run --source markdown --base-dir zeus/data/raw/context-pack-core --dry-run
  python -m zeus.ingest.run --source markdown --base-dir zeus/data/raw/jobkit-archive --dry-run
  python -m zeus.ingest.run --source markdown --base-dir zeus/data/raw/notes --dry-run

  python -m zeus.ingest.run --source context_pack --path zeus/data/raw/context_pack.md --dry-run

  python -m zeus.ingest.run --source chatgpt --llm ollama
  python -m zeus.ingest.run --chunk-size 256 --dry-run   # default --source all

  # all = context_pack.md + raw markdown globs + other sources (see build_sources)
        """,
    )
    p.add_argument(
        "--source",
        choices=["context_pack", "markdown", "chatgpt", "email",
                 "obsidian", "git", "gcal", "bookmarks", "newsletter",
                 "docs", "kiwix_zim", "all"],
        default="all",
        help="Which source type to ingest (default: all, includes zeus/data/raw/context_pack.md and project docs)",
    )
    p.add_argument(
        "--path",
        help="Override path for a single source (e.g. chatgpt dir). "
             "Not applied to context_pack when --source all (uses "
             f"{DEFAULT_CONTEXT_PACK_PATH}).",
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
        default="user",
        help="Memory partition key (default: user; ZEUS_USER_ID env overrides)",
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
    p.add_argument(
        "--config",
        default=None,
        help="Path to ingest config YAML (default: zeus/ingest/config.yaml)",
    )
    p.add_argument(
        "--no-config",
        action="store_true",
        help="Ignore zeus/ingest/config.yaml; use class-level source targets only",
    )
    p.add_argument(
        "--target",
        choices=["memory", "knowledge", "both"],
        default="both",
        help="Only run sources routed to this layer (default: both)",
    )
    p.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="DEBUG logging and noisy HTTP/mem0 loggers (default is quiet INFO)",
    )
    p.add_argument(
        "--plain",
        action="store_true",
        help="Plain text logs and ASCII summary (no Rich spinner or tables)",
    )
    p.add_argument(
        "--rich",
        action="store_true",
        help="Force Rich progress on stderr even when not a TTY",
    )
    return p.parse_args()


if __name__ == "__main__":
    args = parse_args()
    _log_console = None
    if not args.plain:
        try:
            from rich.console import Console

            _log_console = Console(stderr=True)
        except ImportError:
            pass
    configure_ingest_logging(
        plain=args.plain,
        verbose=args.verbose,
        log_console=_log_console,
    )
    asyncio.run(main(args, log_console=_log_console))
