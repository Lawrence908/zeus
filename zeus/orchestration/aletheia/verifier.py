# zeus/orchestration/aletheia/verifier.py
"""Independent resolution of a Reference against the filesystem.

Two jobs, both mechanical (no LLM):

1. ``resolve(ref)`` - resolve a reference from scratch and return a status +
   evidence. This is the *primary*, high-precision drift path: the extractor
   finds backticked references and the verifier checks them directly, no worker
   spend at all.
2. ``verify_finding(finding)`` - re-resolve a *worker-produced* finding and
   confirm or drop it. A worker (LLM) can widen recall into prose; the verifier
   is the trust boundary that keeps precision. A finding whose independent
   resolution disagrees with the worker is dropped and logged.

Resolution errs toward ``unverifiable`` over ``missing`` wherever a mechanical
check is genuinely ambiguous (composed FastAPI routes, arbitrary shell), because
a false ``missing`` is drift-noise a human has to triage. ``changed`` is *not*
inferred here: contradiction-of-behaviour is not mechanically decidable and is
left to the worker + human, per the design.
"""

from __future__ import annotations

import logging
import os
import re

from zeus.orchestration.aletheia import config
from zeus.orchestration.aletheia.extract import ExtractedReference
from zeus.orchestration.aletheia.models import (
    Finding,
    FindingStatus,
    Reference,
    ReferenceKind,
)

logger = logging.getLogger("zeus.aletheia.verifier")

# Directories never worth walking during resolution.
_SKIP_DIRS = {".git", "node_modules", "__pycache__", ".venv", "venv", ".mypy_cache",
              ".ruff_cache", ".pytest_cache", "dist", "build", "_app"}
_MAX_FILES = 60000  # hard cap on a resolution scan

_CONFIDENCE = {
    ReferenceKind.PATH: 0.95,
    ReferenceKind.SYMBOL: 0.75,
    ReferenceKind.ENV_VAR: 0.9,
    ReferenceKind.ENDPOINT: 0.6,
    ReferenceKind.COMMAND: 0.6,
    ReferenceKind.CONFIG_KEY: 0.5,
}


class ResolveResult:
    def __init__(self, status: FindingStatus, evidence: str = "", confidence: float = 0.5):
        self.status = status
        self.evidence = evidence
        self.confidence = confidence


def _roots() -> list[str]:
    return config.observe_roots()


def _iter_files(exts: set[str] | None = None):
    """Walk observe roots, yielding (abs_path, rel_path) for non-excluded files."""
    count = 0
    for root in _roots():
        for dirpath, dirnames, filenames in os.walk(root):
            dirnames[:] = [d for d in dirnames if d not in _SKIP_DIRS]
            for fn in filenames:
                if exts is not None and fn.rsplit(".", 1)[-1].lower() not in exts:
                    continue
                ap = os.path.join(dirpath, fn)
                rel = os.path.relpath(ap, root)
                if config.path_excluded(rel):
                    continue
                count += 1
                if count > _MAX_FILES:
                    logger.warning("aletheia verifier hit file cap (%d)", _MAX_FILES)
                    return
                yield ap, rel


def _read(ap: str) -> str:
    try:
        with open(ap, encoding="utf-8", errors="replace") as f:
            return f.read()
    except OSError:
        return ""


# ---------------------------------------------------------------------------
# Per-kind resolvers
# ---------------------------------------------------------------------------


def _resolve_path(target: str) -> ResolveResult:
    tgt = target.rstrip("/")
    is_dir = target.endswith("/")
    if config.path_excluded(tgt):
        return ResolveResult(FindingStatus.UNVERIFIABLE, "path is under an exclusion glob")
    for root in _roots():
        cand = os.path.join(root, tgt)
        if (is_dir and os.path.isdir(cand)) or (not is_dir and os.path.exists(cand)):
            return ResolveResult(FindingStatus.OK, f"exists at {os.path.relpath(cand, root)}", 0.98)
    # Not where documented; look for the basename elsewhere -> moved.
    base = os.path.basename(tgt)
    for ap, rel in _iter_files():
        if os.path.basename(rel) == base:
            return ResolveResult(FindingStatus.MOVED, f"basename found at {rel}", 0.75)
    return ResolveResult(FindingStatus.MISSING, "no such path under any observe root", 0.9)


_DEF_RE_CACHE: dict[str, re.Pattern] = {}


def _def_pattern(sym: str) -> re.Pattern:
    if sym not in _DEF_RE_CACHE:
        s = re.escape(sym)
        _DEF_RE_CACHE[sym] = re.compile(
            rf"^\s*(?:async\s+def|def|class)\s+{s}\b|^\s*{s}\s*[:=]", re.MULTILINE
        )
    return _DEF_RE_CACHE[sym]


def _find_symbol_files(sym: str) -> list[str]:
    pat = _def_pattern(sym)
    hits: list[str] = []
    for ap, rel in _iter_files(exts={"py", "ts", "tsx", "js", "go", "rs"}):
        if pat.search(_read(ap)):
            hits.append(rel)
            if len(hits) >= 8:
                break
    return hits


def _resolve_symbol(target: str) -> ResolveResult:
    if "::" in target:  # file::symbol -> we can detect moves precisely
        file_part, sym = target.split("::", 1)
        sym = sym.split(".")[-1]
        file_ok = any(os.path.exists(os.path.join(r, file_part)) for r in _roots())
        hits = _find_symbol_files(sym)
        if file_ok and any(h == file_part or h.endswith("/" + file_part) for h in hits):
            return ResolveResult(FindingStatus.OK, f"{sym} defined in {file_part}", 0.9)
        if hits:
            return ResolveResult(FindingStatus.MOVED, f"{sym} defined in {hits[0]} not {file_part}", 0.8)
        return ResolveResult(FindingStatus.MISSING, f"{sym} not defined anywhere", 0.8)
    # Dotted symbol (Class.method / module.attr): confirm the final segment
    # exists as a def/class somewhere. We do not claim "moved" for these - a
    # bare method name is too common to attribute a move confidently.
    sym = target.split(".")[-1]
    hits = _find_symbol_files(sym)
    if hits:
        return ResolveResult(FindingStatus.OK, f"{sym} defined in {hits[0]}", 0.7)
    return ResolveResult(FindingStatus.MISSING, f"{sym} not defined anywhere", 0.7)


def _resolve_env_var(target: str) -> ResolveResult:
    # Env vars are referenced from code/config, not defined in one place; found
    # anywhere outside the docs == real. Search code + config, not markdown.
    needle = target
    for ap, rel in _iter_files(exts={"py", "ts", "tsx", "js", "yaml", "yml", "toml", "sh", "env", "cfg", "ini"}):
        if needle in _read(ap):
            return ResolveResult(FindingStatus.OK, f"referenced in {rel}", 0.9)
    return ResolveResult(FindingStatus.MISSING, "not referenced in any code/config file", 0.85)


_ROUTE_DECORATOR_RE = re.compile(r"""\.(get|post|put|patch|delete)\(\s*["']([^"']+)["']""")


def _resolve_endpoint(target: str) -> ResolveResult:
    parts = target.split()
    path = parts[-1]
    tail = "/" + path.rstrip("/").rsplit("/", 1)[-1] if "/" in path else path
    full_found = False
    tail_found = False
    for ap, rel in _iter_files(exts={"py"}):
        text = _read(ap)
        for _verb, route in _ROUTE_DECORATOR_RE.findall(text):
            if route == path:
                full_found = True
            if route == tail:  # composed with a router prefix
                tail_found = True
        if full_found:
            return ResolveResult(FindingStatus.OK, f"route {path} in {rel}", 0.85)
    if tail_found:
        # Route exists as a subpath under some prefix; can't confirm the full
        # documented path mechanically -> don't cry drift.
        return ResolveResult(FindingStatus.UNVERIFIABLE, f"subpath {tail} exists; prefix unresolved", 0.5)
    return ResolveResult(FindingStatus.MISSING, f"no route decorator for {path}", 0.6)


_MODULE_RE = re.compile(r"-m\s+([\w.]+)")


def _resolve_command(target: str) -> ResolveResult:
    m = _MODULE_RE.search(target)
    if m:
        mod = m.group(1).replace(".", os.sep)
        for root in _roots():
            for cand in (f"{mod}.py", os.path.join(mod, "__main__.py"), os.path.join(mod, "__init__.py")):
                if os.path.exists(os.path.join(root, cand)):
                    return ResolveResult(FindingStatus.OK, f"module resolves to {cand}", 0.8)
        return ResolveResult(FindingStatus.MISSING, f"python module {m.group(1)} not found", 0.7)
    # Arbitrary shell: not mechanically decidable.
    return ResolveResult(FindingStatus.UNVERIFIABLE, "command not mechanically verifiable", 0.4)


def resolve(ref: Reference) -> ResolveResult:
    tgt = ref.normalised_target()
    try:
        if ref.kind == ReferenceKind.PATH:
            return _resolve_path(tgt)
        if ref.kind == ReferenceKind.SYMBOL:
            return _resolve_symbol(tgt)
        if ref.kind == ReferenceKind.ENV_VAR:
            return _resolve_env_var(tgt)
        if ref.kind == ReferenceKind.ENDPOINT:
            return _resolve_endpoint(tgt)
        if ref.kind == ReferenceKind.COMMAND:
            return _resolve_command(tgt)
    except Exception as exc:  # a resolver bug must not abort a sweep
        logger.warning("aletheia resolve error for %s %r: %s", ref.kind.value, tgt, exc)
        return ResolveResult(FindingStatus.UNVERIFIABLE, f"resolver error: {exc}")
    return ResolveResult(FindingStatus.UNVERIFIABLE, "no resolver for this kind")


# ---------------------------------------------------------------------------
# Finding construction + acceptance
# ---------------------------------------------------------------------------


def finding_from_reference(ex: ExtractedReference, doc_path: str) -> Finding:
    """Mechanical drift path: resolve an extracted reference into a verified Finding."""
    res = resolve(ex.reference)
    return Finding(
        doc_path=doc_path,
        doc_line=ex.doc_line,
        claim=ex.claim,
        reference=ex.reference,
        status=res.status,
        evidence=res.evidence,
        confidence=res.confidence,
        verified=True,          # produced by the verifier itself
        verifier_status=res.status,
    )


def verify_finding(finding: Finding) -> Finding:
    """Acceptance check for a worker-produced finding.

    Re-resolves independently. Confirms only on exact status agreement; any
    disagreement drops the finding (marks unverified) and logs a worker error.
    """
    res = resolve(finding.reference)
    finding.verifier_status = res.status
    if res.status == finding.status:
        finding.verified = True
        if res.evidence:
            finding.evidence = res.evidence
        finding.confidence = max(finding.confidence, res.confidence)
    else:
        finding.verified = False
        logger.info(
            "aletheia: dropped finding (worker=%s verifier=%s) doc=%s ref=%s",
            finding.status.value, res.status.value, finding.doc_path,
            finding.reference.normalised_target(),
        )
    return finding
