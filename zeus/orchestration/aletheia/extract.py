# zeus/orchestration/aletheia/extract.py
"""Extract concrete references out of a markdown doc.

v1 is deliberately backtick-scoped (see the design's open question): inline code
spans are high-precision, prose claims are not. This catches paths, symbols, env
vars, endpoints, and commands - the cheap, mechanically-checkable drift - and
knowingly misses architectural prose ("QueryEngine fans out into four blocks").
Widening to prose is a precision/recall tradeoff to measure later, not assume.

Fenced code blocks (``` ... ```) are stripped first: they are examples and
command output, and mining them tanks precision.
"""

from __future__ import annotations

import re

from pydantic import BaseModel

from zeus.orchestration.aletheia.models import Reference, ReferenceKind

# A fenced block: ``` ... ``` or ~~~ ... ~~~ (kept multiline, non-greedy).
_FENCE_RE = re.compile(r"(^|\n)(```|~~~).*?\n\2", re.DOTALL)

# Inline code span: `text` (single backtick, no embedded backtick).
_INLINE_RE = re.compile(r"`([^`\n]+)`")

# --- classifiers, most specific first ---------------------------------------

_ENV_VAR_RE = re.compile(r"^[A-Z][A-Z0-9]*(_[A-Z0-9]+)+$")
_ENDPOINT_RE = re.compile(
    r"^((?P<method>GET|POST|PUT|PATCH|DELETE)\s+)?(?P<path>/[A-Za-z0-9_\-./{}:]*)$"
)
_COMMAND_HEADS = (
    "python", "python3", "pip", "docker", "git", "npm", "pnpm", "yarn",
    "pytest", "curl", "uvicorn", "node", "make", "bash", "sh",
)
# file::symbol  OR  Dotted.path.symbol (has a dot, no slash, not a bare filename)
_FILE_SYMBOL_RE = re.compile(r"^[\w./-]+\.(py|ts|tsx|js|go|rs|java)::[\w.]+$")
_DOTTED_SYMBOL_RE = re.compile(r"^[A-Za-z_]\w*(\.[A-Za-z_]\w*)+$")
# A path: has a slash and a filename, or a bare filename with a code-ish ext.
_PATH_RE = re.compile(r"^[\w][\w./-]*\.[A-Za-z0-9]{1,6}$")
_DIR_RE = re.compile(r"^[\w][\w./-]*/$")

# Code file extensions that mark a dotted token as a *path*, not a symbol.
_CODE_EXTS = {
    "py", "ts", "tsx", "js", "jsx", "go", "rs", "java", "md", "mdx", "rst",
    "yaml", "yml", "toml", "json", "sh", "txt", "cfg", "ini", "html", "css",
}


class ExtractedReference(BaseModel):
    doc_line: int
    claim: str          # the surrounding line, trimmed - the human-readable context
    reference: Reference


def _strip_fences(text: str) -> str:
    """Blank out fenced blocks, preserving newlines so line numbers stay true."""
    def _blank(m: re.Match) -> str:
        return m.group(0).count("\n") * "\n"

    return _FENCE_RE.sub(_blank, text)


def _classify(token: str) -> Reference | None:
    t = token.strip()
    if not t or len(t) > 200:
        return None

    # env var
    if _ENV_VAR_RE.match(t):
        return Reference(kind=ReferenceKind.ENV_VAR, target=t)

    # command (multi-word starting with a known command head)
    head = t.split()[0]
    if " " in t and head in _COMMAND_HEADS:
        return Reference(kind=ReferenceKind.COMMAND, target=t)

    # endpoint (optionally METHOD-prefixed route)
    m = _ENDPOINT_RE.match(t)
    if m and "/" in t and not t.endswith((".py", ".ts", ".md")):
        method = (m.group("method") or "").upper()
        path = m.group("path")
        target = f"{method} {path}".strip()
        return Reference(kind=ReferenceKind.ENDPOINT, target=target)

    # file::symbol
    if _FILE_SYMBOL_RE.match(t):
        return Reference(kind=ReferenceKind.SYMBOL, target=t)

    # path (has slash + extension, or trailing-slash directory)
    if "/" in t and (_PATH_RE.match(t) or _DIR_RE.match(t)):
        return Reference(kind=ReferenceKind.PATH, target=t.rstrip())
    # bare filename with a code-ish extension
    if _PATH_RE.match(t):
        ext = t.rsplit(".", 1)[-1].lower()
        if ext in _CODE_EXTS:
            return Reference(kind=ReferenceKind.PATH, target=t)

    # dotted symbol (Class.method / module.attr) - only if the last-segment ext
    # is not a file extension (which would make it a path handled above).
    if "/" not in t and _DOTTED_SYMBOL_RE.match(t):
        last_ext = t.rsplit(".", 1)[-1].lower()
        if last_ext not in _CODE_EXTS:
            return Reference(kind=ReferenceKind.SYMBOL, target=t)

    return None


def extract_references(text: str) -> list[ExtractedReference]:
    """All classifiable backticked references, in document order, de-duped.

    De-dup is by (line, kind, target): the same token repeated on one line is
    one reference; the same token on different lines is kept (distinct context).
    """
    cleaned = _strip_fences(text)
    lines = cleaned.split("\n")

    out: list[ExtractedReference] = []
    seen: set[tuple[int, str, str]] = set()
    for i, line in enumerate(lines, start=1):
        for m in _INLINE_RE.finditer(line):
            ref = _classify(m.group(1))
            if ref is None:
                continue
            key = (i, ref.kind.value, ref.normalised_target())
            if key in seen:
                continue
            seen.add(key)
            out.append(
                ExtractedReference(
                    doc_line=i,
                    claim=line.strip()[:280],
                    reference=ref,
                )
            )
    return out
