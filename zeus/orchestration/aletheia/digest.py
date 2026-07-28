# zeus/orchestration/aletheia/digest.py
"""Weekly drift digest: a markdown report + idempotent Knowledge-layer ingest.

Because findings carry a stable identity across runs, the digest can separate:
  - new drift this week (identity not seen last week),
  - drift carried over (present both weeks - it has been sitting there), and
  - drift that disappeared (present last week, gone now - your fixes, reflected
    back).

The report is written to ``zeus/data/research/aletheia/weekly-<iso-week>.md`` and
ingested with ``source="aletheia"``, ``source_id=<iso-week>`` so re-running a
week is idempotent (``delete_by_source`` first).
"""

from __future__ import annotations

import asyncio
import logging
import os
from datetime import datetime, timedelta, timezone

from pydantic import BaseModel

from zeus.orchestration.aletheia import config
from zeus.orchestration.aletheia.models import Finding, iso_week
from zeus.orchestration.aletheia.store import AletheiaStore

logger = logging.getLogger("zeus.aletheia.digest")


class DigestResult(BaseModel):
    iso_week: str
    path: str
    total: int
    new: int
    carried: int
    resolved: int
    markdown: str
    ingested: bool = False


def prev_iso_week(week: str) -> str:
    """The ISO-week string seven days before the Monday of ``week``."""
    try:
        year, wk = week.split("-W")
        monday = datetime.fromisocalendar(int(year), int(wk), 1)
    except (ValueError, TypeError):
        monday = datetime.now(timezone.utc)
    return iso_week(monday - timedelta(days=7))


def _group_by_doc(findings: list[Finding]) -> dict[str, list[Finding]]:
    out: dict[str, list[Finding]] = {}
    for f in findings:
        out.setdefault(f.doc_path, []).append(f)
    return out


def render_markdown(
    week: str,
    findings: list[Finding],
    new_ids: set[str],
    resolved: list[Finding],
) -> str:
    lines = [
        f"# Aletheia drift digest - {week}",
        "",
        f"Generated {datetime.now(timezone.utc).date().isoformat()}. "
        f"{len(findings)} open drift finding(s) across "
        f"{len({f.doc_path for f in findings})} document(s); "
        f"{len(new_ids)} new this week; {len(resolved)} resolved since last week.",
        "",
    ]
    if not findings:
        lines += ["No open documentation drift this week.", ""]
    for doc, items in sorted(_group_by_doc(findings).items()):
        lines.append(f"## {doc}")
        lines.append("")
        for f in sorted(items, key=lambda x: x.doc_line):
            tag = "NEW" if f.identity() in new_ids else "carried"
            lines.append(
                f"- **{f.status.value}** [{tag}] `{f.reference.kind.value}` "
                f"`{f.reference.target}` (line {f.doc_line}) - {f.evidence}"
            )
        lines.append("")
    if resolved:
        lines.append("## Resolved since last week")
        lines.append("")
        for f in sorted(resolved, key=lambda x: x.doc_path):
            lines.append(
                f"- `{f.doc_path}`: `{f.reference.target}` ({f.status.value}) no longer flagged"
            )
        lines.append("")
    return "\n".join(lines)


async def generate_digest(
    store: AletheiaStore, *, week: str | None = None, ingest: bool = True
) -> DigestResult:
    week = week or iso_week()
    prev = prev_iso_week(week)

    findings = await store.findings_for_week(week, reportable_only=True)
    this_ids = {f.identity() for f in findings}
    prev_ids = await store.identities_for_week(prev)
    new_ids = this_ids - prev_ids
    carried = this_ids & prev_ids

    prev_findings = await store.findings_for_week(prev, reportable_only=True)
    resolved = [f for f in prev_findings if f.identity() not in this_ids]

    markdown = render_markdown(week, findings, new_ids, resolved)

    os.makedirs(config.digest_dir(), exist_ok=True)
    path = os.path.join(config.digest_dir(), f"weekly-{week}.md")
    with open(path, "w", encoding="utf-8") as f:
        f.write(markdown)

    result = DigestResult(
        iso_week=week, path=path, total=len(findings), new=len(new_ids),
        carried=len(carried), resolved=len(resolved), markdown=markdown,
    )

    if ingest:
        result.ingested = await _ingest_digest(week, path, markdown)
    logger.info(
        "aletheia digest %s: total=%d new=%d carried=%d resolved=%d ingested=%s",
        week, result.total, result.new, result.carried, result.resolved, result.ingested,
    )
    return result


async def _ingest_digest(week: str, path: str, markdown: str) -> bool:
    """Idempotent ingest into the Knowledge layer (delete-by-source first)."""
    def _do() -> bool:
        from zeus.memory.library import KnowledgeChunk, get_knowledge_store
        ks = get_knowledge_store()
        ks.delete_by_source("aletheia", week)
        ks.add_chunks([
            KnowledgeChunk(
                text=markdown,
                source="aletheia",
                source_id=week,
                source_path=path,
                metadata={"kind": "drift_digest", "iso_week": week},
            )
        ])
        return True

    try:
        return await asyncio.to_thread(_do)
    except Exception as exc:  # ingest is best-effort; the file on disk is the record
        logger.warning("aletheia digest ingest failed for %s: %s", week, exc)
        return False
