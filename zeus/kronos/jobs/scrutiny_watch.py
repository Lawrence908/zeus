# zeus/kronos/jobs/scrutiny_watch.py
# Daily congressional-trading "catch and research" watcher.
#
# The weekly congressional_scrutiny brief is the narrative summary a human
# reads. This job is the always-on funnel underneath it: every morning it
# CATCHES the fresh scrutiny + herding-cluster signals from CapitolScope,
# TRIAGES which are genuinely new/intensifying (deduped against a persistent
# store so the same cluster is never re-worked), scores each for research
# worth, and ESCALATES only the standouts (triage score >= threshold) into a
# real multi-agent deep_research run for web verification. Everything below the
# bar is flagged with a ready-to-run topic so you can fire it yourself.
#
# Persistence lives in zeus/data/scrutiny_watch.db (stdlib sqlite3, no new
# deps) so "interesting data" is durable across runs: first_seen/last_seen,
# times_seen, the triage score, and any research job spawned for it.
#
# Escalation is decoupled from this job's timeout: it POSTs a one-off Kronos
# deep_research job (run_at ~now) exactly like the chat tool does, so each
# heavy research run executes under its own timeout, not this daily tick.
#
# Privacy: congressional disclosures are public. Synthesis/triage stays on the
# local Ollama by default (min_privacy_tier=1, model_hint="ollama").
from __future__ import annotations

import asyncio
import logging
import os
import sqlite3
import uuid
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

import httpx
from pydantic import BaseModel, Field

from zeus.core.small_llm import small_llm_call
from zeus.mcp.tools import capitolscope_context_pack

logger = logging.getLogger("zeus.kronos.scrutiny_watch")

# Relative, gitignored default (under the writable data mount, NOT the indexed
# docs/ tree the check-docs hook scans). Overridden in-container by
# ZEUS_BRIEFINGS_DIR. Runtime artifacts, not documentation.
BRIEFINGS_DIR = Path(os.getenv("ZEUS_BRIEFINGS_DIR", "zeus/data/briefings"))
# Relative default (resolved from CWD) so it lands under the writable, host-
# persisted data mount both in-container (CWD /app -> /app/zeus/data) and on the
# host (CWD repo root -> zeus/zeus/data). An absolute host path would resolve to
# an ephemeral container-internal dir. Mirrors ZEUS_KRONOS_DB_PATH.
WATCH_DB_PATH = Path(os.getenv("ZEUS_SCRUTINY_WATCH_DB", "zeus/data/scrutiny_watch.db"))


# ---------------------------------------------------------------- triage schema
class TriageItem(BaseModel):
    id: str = Field(description="Echo back the candidate's id (e.g. c1, c2) exactly.")
    score: int = Field(description="Research-worthiness 0-10.", ge=0, le=10)
    worth_researching: bool
    hypothesis: str = Field(description="One-sentence event/market linkage hypothesis.")
    confirm_refute: str = Field(description="What evidence would confirm or refute it.")
    suggested_topic: str = Field(description="A specific deep_research topic sentence to verify this.")


class TriageResult(BaseModel):
    items: list[TriageItem] = Field(default_factory=list)


TRIAGE_SYSTEM = """\
You are a triage analyst for a private congressional-trading research desk.
Your input is a list of CANDIDATE signals derived from public U.S. congressional
stock-trading disclosures (STOCK Act filings): herding clusters, high-scrutiny
members, and newly-active tickers, all flagged as new or intensifying this cycle.

For EACH candidate, decide whether it is worth spending a multi-agent web-research
run on, and score it 0-10:
- 8-10: dense herding (several members, same ticker+side, tight window) OR a
  high-scrutiny member newly concentrated in one name, with a plausible current
  catalyst worth verifying. Reserve for the clear standouts.
- 5-7: a real, specific signal but with weaker linkage or thinner participation.
- 0-4: routine, diffuse, or stale; not worth a research run.

Hard rules:
- These are SIGNALS, not proof. Disclosures lag and any event link is a
  hypothesis, never insider-trading proof and never investment advice.
- Ground the hypothesis in the specific candidate. Do NOT invent members,
  tickers, figures, or trades not present in the input.
- The suggested_topic must be a concrete, verification-oriented sentence a web
  researcher could run (name the ticker/sector and the catalyst to check).
- Echo each candidate's id (c1, c2, ...) back EXACTLY so results can be matched.
Return one item per candidate."""

TRIAGE_USER = """\
Cycle date: {date}
Reporting window: {period}

Candidates (each line: ID | kind | detail):
{candidates}

Triage every candidate. Score research-worth, give a one-line hypothesis, a
confirm/refute test, and a concrete deep_research topic sentence. Echo each
id verbatim."""


# ---------------------------------------------------------------- candidates
def _fmt_money(n) -> str:
    try:
        n = float(n)
    except (TypeError, ValueError):
        return "n/a"
    a = abs(n)
    if a >= 1e9:
        return f"${n / 1e9:.1f}B"
    if a >= 1e6:
        return f"${n / 1e6:.1f}M"
    if a >= 1e3:
        return f"${n / 1e3:.0f}K"
    return f"${n:.0f}"


def _build_candidates(cp: dict[str, Any]) -> list[dict[str, str]]:
    """Flatten the context pack into fingerprinted candidate signals.

    Fingerprints are stable across runs so persistence can dedup:
      cluster:<ticker>:<direction>:<window_start>
      member:<member>
      newticker:<ticker>
    """
    out: list[dict[str, str]] = []

    for c in cp.get("notable_clusters", []) or []:
        tkr = str(c.get("ticker", "?"))
        direction = str(c.get("direction", "?"))
        wstart = str(c.get("window_start", "?"))
        ret = c.get("avg_return_30d")
        ret_s = "n/a" if ret is None else f"{ret * 100:+.1f}%"
        fp = f"cluster:{tkr}:{direction}:{wstart}"
        detail = (
            f"{c.get('member_count', '?')} members {direction} {tkr} "
            f"({wstart}..{c.get('window_end', '?')}), avg 30d ret {ret_s}, "
            f"lead {c.get('lead_member', '?')}"
        )
        out.append({"fingerprint": fp, "kind": "cluster", "detail": detail})

    for m in cp.get("scrutiny_movers", []) or []:
        member = str(m.get("member", "?"))
        fp = f"member:{member}"
        detail = (
            f"{member} ({m.get('party', '?')}) scrutiny score {m.get('scrutiny_score', '?')}, "
            f"leading factor {m.get('leading_factor', '?')}"
        )
        out.append({"fingerprint": fp, "kind": "scrutiny_mover", "detail": detail})

    for t in cp.get("active_tickers", []) or []:
        if not t.get("new_this_week"):
            continue
        tkr = str(t.get("ticker", "?"))
        fp = f"newticker:{tkr}"
        detail = (
            f"{tkr} [{t.get('sector', '?')}] NEW this week: {t.get('net_direction', '?')}, "
            f"{t.get('members', '?')} members (delta {t.get('member_delta', 0):+d}), "
            f"{_fmt_money(t.get('notional'))}"
        )
        out.append({"fingerprint": fp, "kind": "new_ticker", "detail": detail})

    return out


# ---------------------------------------------------------------- persistence
# Mirrors zeus/kronos/storage.py: a fresh short-lived autocommit connection per
# operation, each run via asyncio.to_thread. Never hold a connection across
# to_thread boundaries — sqlite3 connections are thread-bound.
def _connect() -> sqlite3.Connection:
    WATCH_DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    return sqlite3.connect(WATCH_DB_PATH, isolation_level=None, timeout=10)


def _ensure_schema() -> None:
    with _connect() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS signals (
                fingerprint     TEXT PRIMARY KEY,
                kind            TEXT NOT NULL,
                detail          TEXT NOT NULL,
                first_seen      TEXT NOT NULL,
                last_seen       TEXT NOT NULL,
                times_seen      INTEGER NOT NULL DEFAULT 1,
                triage_score    INTEGER,
                status          TEXT NOT NULL DEFAULT 'seen',
                research_job_id TEXT,
                research_path   TEXT,
                last_escalated  TEXT
            )
            """
        )


def _record_seen(candidates: list[dict[str, str]], now_iso: str) -> set[str]:
    """Upsert every candidate; return the set of fingerprints that are new
    (never seen before this run)."""
    new_fps: set[str] = set()
    with _connect() as conn:
        for c in candidates:
            fp = c["fingerprint"]
            row = conn.execute(
                "SELECT fingerprint FROM signals WHERE fingerprint = ?", (fp,)
            ).fetchone()
            if row is None:
                new_fps.add(fp)
                conn.execute(
                    "INSERT INTO signals (fingerprint, kind, detail, first_seen, last_seen, times_seen) "
                    "VALUES (?, ?, ?, ?, ?, 1)",
                    (fp, c["kind"], c["detail"], now_iso, now_iso),
                )
            else:
                conn.execute(
                    "UPDATE signals SET last_seen = ?, times_seen = times_seen + 1, detail = ? "
                    "WHERE fingerprint = ?",
                    (now_iso, c["detail"], fp),
                )
    return new_fps


def _in_cooldown(fp: str, cooldown_days: int, now: datetime) -> bool:
    with _connect() as conn:
        row = conn.execute(
            "SELECT last_escalated FROM signals WHERE fingerprint = ?", (fp,)
        ).fetchone()
    if not row or not row[0]:
        return False
    try:
        last = datetime.fromisoformat(row[0])
    except ValueError:
        return False
    return (now - last) < timedelta(days=cooldown_days)


def _mark_triaged(fp: str, score: int) -> None:
    with _connect() as conn:
        conn.execute("UPDATE signals SET triage_score = ? WHERE fingerprint = ?", (score, fp))


def _mark_escalated(fp: str, job_id: str, path: str, now_iso: str) -> None:
    with _connect() as conn:
        conn.execute(
            "UPDATE signals SET status = 'researching', research_job_id = ?, research_path = ?, "
            "last_escalated = ? WHERE fingerprint = ?",
            (job_id, path, now_iso, fp),
        )


# ---------------------------------------------------------------- escalation
def _slug(text: str, max_len: int = 50) -> str:
    import re

    s = re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")
    return s[:max_len] or "untitled"


async def _spawn_deep_research(topic: str, *, depth: str) -> dict[str, str]:
    """POST a one-off deep_research Kronos job (mirrors core/tools/deep_research).
    Returns {job_id, path} on success or {error} on failure. Never raises."""
    core_url = os.getenv("ZEUS_CORE_URL", "http://127.0.0.1:8203").rstrip("/")
    reports_dir = os.getenv("ZEUS_DEEP_RESEARCH_DIR", "/home/chris/zeus/docs/research").rstrip("/")
    today = datetime.now(timezone.utc).date().isoformat()
    short_id = uuid.uuid4().hex[:6]
    job_id = f"scrutiny-research-{today}-{_slug(topic, 30)}-{short_id}"
    run_at = (datetime.now(timezone.utc) + timedelta(seconds=5)).isoformat()
    timeout_by_depth = {"quick": 600, "standard": 1800, "deep": 3600}
    body = {
        "id": job_id,
        "name": f"Scrutiny research: {topic[:90]}",
        "description": "Auto-escalated from the daily scrutiny_watch triage.",
        "category": "research",
        "schedule": {"run_at": run_at},
        "executor": "zeus.kronos.jobs.deep_research.run_deep_research",
        "params": {"topic": topic, "depth": depth, "format": "markdown"},
        "safety_policy": "standard",
        "timeout_seconds": timeout_by_depth.get(depth, 1800),
        "max_retries": 0,
        "tags": ["research", "capitolscope", "scrutiny-escalation", depth],
        "enabled": True,
    }
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            r = await client.post(f"{core_url}/kronos/jobs", json=body)
        if r.status_code in (401, 403):
            return {"error": "kronos writes disabled (set ZEUS_KRONOS_ALLOW_WRITE=1)"}
        if r.status_code >= 400:
            return {"error": f"kronos {r.status_code}: {r.text[:200]}"}
    except Exception as exc:  # noqa: BLE001
        logger.warning("scrutiny_watch: deep_research spawn failed: %s", exc)
        return {"error": f"{type(exc).__name__}: {exc}"}
    # Predict the report path deep_research will write. It slugs with max_len=60
    # (see zeus/kronos/jobs/deep_research._slug), so match that exactly or the
    # recorded path won't point at the real file.
    return {"job_id": job_id, "path": f"{reports_dir}/{today}-{_slug(topic, 60)}.md"}


# ---------------------------------------------------------------- rendering
def _render_brief(
    *,
    period: str,
    escalated: list[dict[str, Any]],
    flagged: list[dict[str, Any]],
    n_candidates: int,
    n_new: int,
) -> str:
    stamp = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    lines = [
        f"# Scrutiny Watch — {stamp}",
        "",
        f"**Window:** {period}. Caught {n_candidates} signals "
        f"({n_new} new this cycle). Escalated {len(escalated)} to deep research; "
        f"flagged {len(flagged)} for optional follow-up.",
        "",
        "_Signals from public STOCK Act disclosures. Hypotheses only — not "
        "insider-trading proof, not investment advice._",
        "",
    ]

    if escalated:
        lines += ["## Escalated to deep research", ""]
        for e in escalated:
            lines.append(f"### {e['fingerprint']}  (score {e['score']}/10)")
            lines.append(f"- **Detail:** {e['detail']}")
            lines.append(f"- **Hypothesis:** {e['hypothesis']}")
            lines.append(f"- **Confirm/refute:** {e['confirm_refute']}")
            lines.append(f"- **Research topic:** {e['suggested_topic']}")
            if e.get("job_id"):
                lines.append(f"- **Research job:** `{e['job_id']}` -> `{e['path']}`")
            else:
                lines.append(f"- **Research job:** NOT SPAWNED ({e.get('spawn_error', '?')})")
            lines.append("")

    if flagged:
        lines += ["## Flagged (below auto-escalation bar — trigger manually if worth it)", ""]
        for f in flagged:
            lines.append(
                f"- **{f['fingerprint']}** (score {f['score']}/10) — {f['hypothesis']}"
            )
            lines.append(f"    - run: `deep_research topic=\"{f['suggested_topic']}\"`")
        lines.append("")

    if not escalated and not flagged:
        lines += ["## Quiet cycle", "", "No new or intensifying signals cleared triage.", ""]

    return "\n".join(lines)


# ---------------------------------------------------------------- writeback
async def _writeback(out_path: Path, period: str, n_escalated: int) -> dict[str, str]:
    results = {"inbox": "skipped", "library": "skipped"}
    core_url = os.getenv("ZEUS_CORE_URL", "http://127.0.0.1:8203").rstrip("/")
    note = f"Scrutiny watch ({period}): {n_escalated} escalated to research -> {out_path}"
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            r = await client.post(
                f"{core_url}/inbox/append",
                json={"text": note, "tags": ["capitolscope", "scrutiny", "watch", "auto"]},
            )
        results["inbox"] = "ok" if r.status_code < 400 else f"http_{r.status_code}"
    except Exception as exc:  # noqa: BLE001
        logger.warning("scrutiny_watch: inbox writeback failed: %s", exc)
        results["inbox"] = f"err: {type(exc).__name__}"

    try:
        text = out_path.read_text(encoding="utf-8")
        await asyncio.to_thread(_ingest_to_library, out_path=out_path, text=text, period=period)
        results["library"] = "ok"
    except Exception as exc:  # noqa: BLE001
        logger.warning("scrutiny_watch: library writeback failed: %s", exc)
        results["library"] = f"err: {type(exc).__name__}"
    return results


def _ingest_to_library(*, out_path: Path, text: str, period: str) -> None:
    from zeus.memory.library import KnowledgeChunk, get_knowledge_store

    ks = get_knowledge_store()
    chunk = KnowledgeChunk(
        text=text,
        source="scrutiny_watch",
        source_id=str(out_path),
        source_path=str(out_path),
        chunk_index=0,
        user_id="user",
        metadata={
            "kind": "scrutiny_watch_brief",
            "period": period,
            "generated_at_iso": datetime.now(timezone.utc).isoformat(),
        },
    )
    res = ks.add_chunks([chunk])
    if res.errors:
        raise RuntimeError(res.errors[0])


# ---------------------------------------------------------------- executor
async def run_scrutiny_watch(params: dict[str, Any]) -> dict[str, Any]:
    """Daily catch-triage-escalate over CapitolScope scrutiny + cluster signals.

    Params:
      days:               context-pack window (default 7)
      escalate_threshold: triage score at/above which deep_research auto-fires (default 8)
      max_escalations:    hard cap on auto research runs per cycle (default 2)
      max_candidates:     cap on signals sent to triage (default 12)
      cooldown_days:      do not re-escalate the same fingerprint within N days (default 14)
      depth:              deep_research depth for escalations (default "standard")
      only_new:           triage only signals unseen before this run (default True)
      providers:          hard-pin the small_llm chain (default ["ollama"] to keep
                          the daily cron local/free); set null to use DEFAULT_CHAIN
      model_hint:         model within the pinned provider (default "ollama")
    """
    days = int(params.get("days", 7))
    threshold = int(params.get("escalate_threshold", 8))
    max_escalations = int(params.get("max_escalations", 2))
    max_candidates = int(params.get("max_candidates", 12))
    cooldown_days = int(params.get("cooldown_days", 14))
    depth = str(params.get("depth", "standard")).lower()
    only_new = bool(params.get("only_new", True))
    providers = params.get("providers", ["ollama"]) or None
    model_hint = params.get("model_hint", "ollama")

    cp = await capitolscope_context_pack(days=days)
    if not cp or "error" in cp:
        return {"status": "error", "error": (cp or {}).get("error", "no data")}

    period = (
        f"{cp.get('this_week', {}).get('start', '?')} to "
        f"{cp.get('this_week', {}).get('end', '?')}"
    )
    candidates = _build_candidates(cp)
    if not candidates:
        return {"status": "ok", "note": "no candidate signals this cycle", "period": period}

    now = datetime.now(timezone.utc)
    now_iso = now.isoformat()
    await asyncio.to_thread(_ensure_schema)
    new_fps = await asyncio.to_thread(_record_seen, candidates, now_iso)

    # Choose what to triage: new-only by default, else all caught candidates.
    pool = [c for c in candidates if c["fingerprint"] in new_fps] if only_new else candidates
    pool = pool[:max_candidates]
    if not pool:
        return {
            "status": "ok",
            "note": "no new signals to triage",
            "period": period,
            "candidates_seen": len(candidates),
        }

    # LLM triage (structured). Present short opaque ids for the model to
    # echo — fingerprints contain spaces/punctuation the model normalizes,
    # so matching on an echoed id is far more robust.
    by_id = {f"c{i + 1}": c for i, c in enumerate(pool)}
    cand_lines = "\n".join(f"c{i + 1} | {c['kind']} | {c['detail']}" for i, c in enumerate(pool))
    user = TRIAGE_USER.format(date=now.date().isoformat(), period=period, candidates=cand_lines)
    result = await small_llm_call(
        system=TRIAGE_SYSTEM,
        user=user,
        max_tokens=int(params.get("max_tokens", 1800)),
        response_format=TriageResult,
        min_privacy_tier=1,
        model_hint=model_hint,
        providers=providers,
        caller="kronos.scrutiny_watch",
    )
    triage: TriageResult | None = result.parsed  # type: ignore[assignment]
    if triage is None:
        return {"status": "error", "error": "triage produced no structured output"}

    # Rank triage items by score, highest first.
    items = sorted(triage.items, key=lambda i: i.score, reverse=True)

    escalated: list[dict[str, Any]] = []
    flagged: list[dict[str, Any]] = []
    n_escalated = 0

    for it in items:
        cand = by_id.get(it.id.strip())
        if cand is None:
            continue  # model echoed an unknown id; skip
        fp = cand["fingerprint"]
        await asyncio.to_thread(_mark_triaged, fp, it.score)
        row = {
            "fingerprint": fp,
            "detail": cand["detail"],
            "score": it.score,
            "hypothesis": it.hypothesis,
            "confirm_refute": it.confirm_refute,
            "suggested_topic": it.suggested_topic,
        }

        eligible = (
            it.worth_researching
            and it.score >= threshold
            and n_escalated < max_escalations
            and not await asyncio.to_thread(_in_cooldown, fp, cooldown_days, now)
        )
        if eligible:
            spawn = await _spawn_deep_research(it.suggested_topic, depth=depth)
            if "error" in spawn:
                row["spawn_error"] = spawn["error"]
            else:
                row["job_id"] = spawn["job_id"]
                row["path"] = spawn["path"]
                await asyncio.to_thread(
                    _mark_escalated, fp, spawn["job_id"], spawn["path"], now_iso
                )
                n_escalated += 1
            escalated.append(row)
        else:
            flagged.append(row)

    brief = _render_brief(
        period=period,
        escalated=escalated,
        flagged=flagged,
        n_candidates=len(candidates),
        n_new=len(new_fps),
    )
    BRIEFINGS_DIR.mkdir(parents=True, exist_ok=True)
    stamp = now.strftime("%Y-%m-%d")
    path = BRIEFINGS_DIR / f"{stamp}-scrutiny-watch.md"
    path.write_text(brief + "\n", encoding="utf-8")

    writeback = await _writeback(path, period, n_escalated)

    return {
        "status": "ok",
        "path": str(path),
        "period": period,
        "candidates_seen": len(candidates),
        "new_this_cycle": len(new_fps),
        "triaged": len(pool),
        "escalated": n_escalated,
        "escalated_jobs": [e.get("job_id") for e in escalated if e.get("job_id")],
        "flagged": len(flagged),
        "provider": result.provider_used,
        "writeback": writeback,
    }
