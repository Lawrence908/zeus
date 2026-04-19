# zeus/ingest/sources/markdown.py — Iris markdown source parser
# Reads .md files from a glob pattern and yields chunks.
# Strips frontmatter and splits on heading boundaries before word-chunking,
# so chunk boundaries respect document structure rather than cutting mid-section.
import fnmatch
import glob as stdlib_glob
import re
from pathlib import Path
from typing import AsyncIterator

from zeus.ingest.pipeline import Chunk, chunk_text

# Matches YAML frontmatter block at the start of a file
_FRONTMATTER_RE = re.compile(r"^\s*---\s*\n.*?\n---\s*\n", re.DOTALL)

# Split on H1/H2/H3 headings — keeps the heading as the start of each section
_HEADING_SPLIT_RE = re.compile(r"(?=^#{1,3} )", re.MULTILINE)


def _strip_frontmatter(text: str) -> str:
    return _FRONTMATTER_RE.sub("", text).strip()


def _extract_frontmatter_title(text: str) -> str | None:
    """Pull 'title:' from YAML frontmatter if present."""
    match = re.search(r"^title:\s*(.+)$", text, re.MULTILINE)
    return match.group(1).strip() if match else None


def _recursive_name_glob(pattern: str) -> str | None:
    """If pattern is **/<name-only glob>, return the name part; else None.

    pathlib.Path.glob('**/*.md') does not enter symlinked directories; we handle
    the common **/<fnmatch> case by walking and following dir symlinks so vault
    mounts under base_dir work.
    """
    if "**" not in pattern:
        return None
    if pattern.startswith("**/"):
        tail = pattern[3:]
    else:
        parts = pattern.split("**/", 1)
        if len(parts) != 2 or "/" in parts[0] or "/" in parts[1]:
            return None
        tail = parts[1]
    if not tail or "/" in tail:
        return None
    return tail


def _walk_files_matching_name(
    directory: Path, name_glob: str, rel_parts: list[str]
) -> list[tuple[Path, str]]:
    """Recurse under directory, following symlinked dirs; match file basenames with name_glob."""
    out: list[tuple[Path, str]] = []
    try:
        entries = sorted(directory.iterdir(), key=lambda p: p.name.lower())
    except OSError:
        return out
    for entry in entries:
        name = entry.name
        rel = "/".join([*rel_parts, name]) if rel_parts else name
        try:
            if entry.is_symlink():
                resolved = entry.resolve()
                if resolved.is_dir():
                    out.extend(_walk_files_matching_name(resolved, name_glob, [*rel_parts, name]))
                elif resolved.is_file() and fnmatch.fnmatch(name, name_glob):
                    out.append((resolved, rel))
            elif entry.is_dir():
                out.extend(_walk_files_matching_name(entry, name_glob, [*rel_parts, name]))
            elif entry.is_file() and fnmatch.fnmatch(name, name_glob):
                out.append((entry, rel))
        except (OSError, RuntimeError):
            continue
    return out


class MarkdownSource:
    """Ingest .md files from one or more glob patterns."""

    target: str = "knowledge"

    def __init__(
        self,
        globs: list[str],
        base_dir: str | Path = ".",
        chunk_size: int = 512,
        chunk_overlap: int = 64,
        user_id: str = "chris",
    ) -> None:
        self.globs = globs
        self.base_dir = Path(base_dir)
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.user_id = user_id

    def _iter_file_relpairs(self) -> list[tuple[Path, str]]:
        pairs: list[tuple[Path, str]] = []
        seen_rel: set[str] = set()
        base = self.base_dir

        for pattern in self.globs:
            name_glob = _recursive_name_glob(pattern)
            if name_glob is not None:
                for path, rel in _walk_files_matching_name(base.resolve(), name_glob, []):
                    if rel not in seen_rel:
                        seen_rel.add(rel)
                        pairs.append((path, rel))
            elif "**" in pattern:
                for pstr in stdlib_glob.glob(str(base / pattern), recursive=True):
                    path = Path(pstr)
                    if not path.is_file():
                        continue
                    try:
                        rel = str(path.resolve().relative_to(base.resolve()))
                    except ValueError:
                        rel = path.name
                    if rel not in seen_rel:
                        seen_rel.add(rel)
                        pairs.append((path, rel))
            else:
                for path in sorted(base.glob(pattern)):
                    if not path.is_file():
                        continue
                    rel = str(path.relative_to(base))
                    if rel not in seen_rel:
                        seen_rel.add(rel)
                        pairs.append((path, rel))

        pairs.sort(key=lambda pr: pr[1].lower())
        return pairs

    async def chunks(self) -> AsyncIterator[Chunk]:
        for path, rel_path in self._iter_file_relpairs():
            try:
                raw = path.read_text(encoding="utf-8")
            except OSError as e:
                import logging
                logging.getLogger("iris").warning(f"markdown: cannot read {path} — {e}")
                continue

            title = _extract_frontmatter_title(raw)
            body = _strip_frontmatter(raw)

            # Split on headings first to avoid cutting mid-section
            sections = _HEADING_SPLIT_RE.split(body)
            for section in sections:
                section = section.strip()
                if not section:
                    continue

                for text in chunk_text(section, self.chunk_size, self.chunk_overlap):
                    yield Chunk(
                        text=text,
                        source=f"markdown:{rel_path}",
                        metadata={
                            "file": rel_path,
                            "title": title or path.stem,
                            "type": "markdown",
                        },
                        user_id=self.user_id,
                    )
