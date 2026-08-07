# zeus/pheme/pipeline.py - Pheme staged analytical pipeline (local Ollama only).
#
# Deterministic control flow, one narrow LLM call per stage, every stage result
# cached under zeus/data/pheme/<run>/ so re-runs skip completed stages.
# Non-LLM math (entity overlap, embedding neighbours) replaces LLM calls
# wherever possible; the 3080's wall-clock is the real budget.
#
# Stages:
#   1 extract    - entities/topics/claim per item (LLM, only for items missing them)
#   2 cluster    - union-find over entity overlap + qdrant recommend-by-id (LLM names only)
#   3 thread     - prior-coverage lookup per cluster (non-LLM query + one-line note)
#   4 correlate  - CapitolScope x Canary candidate pairs only, LLM judgment
#   5 rank       - heuristic + one profile-relevance call; writes significance back
#   6 synthesize - lead paragraph (LLM) + deterministic body and public trim
from __future__ import annotations

import asyncio
import hashlib
import logging
import math
import os
import re
import uuid
from datetime import datetime, timedelta, timezone
from typing import Any, Literal

from pydantic import BaseModel

from zeus.memory.news import NewsHit, NewsStore, get_news_store
from zeus.pheme.cache import StageCache, run_key
from zeus.pheme.llm import PhemeLLMFailed, pheme_llm_call, pheme_llm_text
from zeus.pheme.models import (
    ClusterName,
    ClusterScores,
    ClusterSummary,
    Correlation,
    CorrelationJudgment,
    InsightList,
    ItemExtraction,
    PhemeDigest,
    ThreadNote,
)

logger = logging.getLogger("zeus.pheme.pipeline")

NEWS_SOURCES = ["canary", "capitolscope"]


def _max_items() -> int:
    try:
        return max(1, int(os.getenv("PHEME_MAX_ITEMS_PER_RUN", "200")))
    except ValueError:
        return 200


def _top_n() -> int:
    try:
        return max(1, int(os.getenv("PHEME_DIGEST_TOP_N", "6")))
    except ValueError:
        return 6


def _cluster_sim_threshold() -> float:
    try:
        return float(os.getenv("PHEME_CLUSTER_SIM", "0.75"))
    except ValueError:
        return 0.75


def _max_correlation_pairs() -> int:
    try:
        return max(1, int(os.getenv("PHEME_MAX_CORRELATION_PAIRS", "12")))
    except ValueError:
        return 12


def _cluster_merge_sim() -> float:
    # Cluster-level second-pass merge threshold. Measured on real data
    # (2026-07-26 Berlin split): same-story cross-outlet pairs score 0.80-0.90,
    # syndicated copies 0.93+, unrelated stories well below 0.75.
    try:
        return float(os.getenv("PHEME_CLUSTER_MERGE_SIM", "0.78"))
    except ValueError:
        return 0.78


class _Item(BaseModel):
    key: str          # "source:source_id"
    point_id: str
    source: str
    source_id: str
    title: str
    text: str
    url: str
    published_at: str
    entities: list[str] = []
    topics: list[str] = []
    claim: str = ""

    @classmethod
    def from_hit(cls, hit: NewsHit) -> "_Item":
        p = hit.payload
        return cls(
            key=f"{p.get('source', '')}:{p.get('source_id', '')}",
            point_id=hit.id,
            source=str(p.get("source", "")),
            source_id=str(p.get("source_id", "")),
            title=hit.title,
            text=hit.text,
            url=hit.url,
            published_at=hit.published_at,
            entities=[str(e) for e in p.get("entities") or []],
            topics=[str(t) for t in p.get("topics") or []],
            claim=str(p.get("claim", "") or ""),
        )


def _norm_entities(entities: list[str]) -> set[str]:
    return {e.strip().casefold() for e in entities if e and e.strip()}


# Generic words that must not link two stories on their own ("police", "us").
_ENTITY_TOKEN_STOPWORDS = {
    "the", "and", "for", "with", "from", "new", "news", "police", "government",
    "president", "state", "states", "united", "national", "city", "county",
    "house", "senate", "court", "party", "minister", "attack", "event",
}
_DIGIT_RESIDUE_RE = re.compile(r"^[a-z]{0,2}\d")


def _entity_tokens(entities: list[str]) -> set[str]:
    """Salient single tokens from entity phrases, for fuzzy cluster matching.

    The 7B extractor is inconsistent about phrase boundaries ("berlin" vs
    "berlin police" vs "berlin pride attack"), so exact-phrase overlap misses
    same-story clusters. Token overlap generates merge candidates; the
    embedding check makes the final call.
    """
    tokens: set[str] = set()
    for phrase in entities:
        for tok in phrase.casefold().split():
            tok = tok.strip(".,;:!?()[]'\"")
            if len(tok) < 3 or tok in _ENTITY_TOKEN_STOPWORDS or _DIGIT_RESIDUE_RE.match(tok):
                continue
            tokens.add(tok)
    return tokens


def _generic_tokens(token_sets: list[set[str]], *, floor: int = 3, frac: float = 0.08) -> set[str]:
    """Tokens frequent across today's corpus ("earnings", "election", "trump").

    Frequent tokens may support a cluster merge or thread match but never
    carry one - that is how Franklin Electric earnings ended up glued to the
    Nvidia/Microsoft AI-letter thread (2026-07-28 digest).
    """
    df: dict[str, int] = {}
    for tokens in token_sets:
        for tok in tokens:
            df[tok] = df.get(tok, 0) + 1
    threshold = max(floor, int(frac * len(token_sets)))
    return {tok for tok, n in df.items() if n > threshold}


def _clean_extracted_entities(entities: list[str]) -> list[str]:
    """Drop URL/id residue the extractor sometimes emits (e.g. 'n2430637')."""
    out = []
    for e in entities:
        s = e.strip()
        alpha = sum(1 for c in s if c.isalpha())
        if alpha >= 3 and not _DIGIT_RESIDUE_RE.match(s.casefold()):
            out.append(s)
    return out


# Filename-shaped or word-poor strings (GDELT residue) must never surface in
# cluster names, takes, or tweets.
_JUNK_TEXT_RE = re.compile(r"^article[ _-][0-9a-f]{4,}", re.IGNORECASE)


def _is_junk_text(text: str) -> bool:
    s = text.strip()
    if not s:
        return True
    if _JUNK_TEXT_RE.match(s) or s.lower().endswith((".html", ".htm")):
        return True
    words = s.split()
    alpha = sum(1 for w in words if any(c.isalpha() for c in w) and not all(c in "0123456789abcdef" for c in w.lower()))
    return alpha < max(2, len(words) // 2)


# ---------------------------------------------------------------------------
# Stage 1 - extract
# ---------------------------------------------------------------------------

_EXTRACT_SYSTEM = """\
You extract structured metadata from one news item for an analysis pipeline.
Return JSON only. Rules:
- entities: proper nouns worth cross-referencing - people, organizations,
  countries, and stock tickers. When a publicly traded company is mentioned,
  include its ticker symbol (e.g. "Nvidia" -> also "NVDA").
- topics: 2-4 short lowercase tags (e.g. "semiconductors", "middle-east").
- claim: exactly one neutral sentence stating what happened. No opinion.
"""


async def _stage_extract(items: list[_Item], store: NewsStore, cache: StageCache) -> None:
    from zeus.pheme.tickers import resolve_tickers

    cached: dict[str, Any] = cache.get("stage1_extract") or {}
    for item in items:
        changed = False
        if not (item.entities and item.claim):
            if item.key in cached:
                data = cached[item.key]
            else:
                try:
                    parsed = await pheme_llm_call(
                        system=_EXTRACT_SYSTEM,
                        user=f"Title: {item.title}\n\nText: {item.text[:2000]}",
                        response_format=ItemExtraction,
                        max_tokens=350,
                        caller="pheme.extract",
                    )
                except PhemeLLMFailed as exc:
                    logger.warning("extract failed for %s: %s", item.key, exc)
                    continue
                data = parsed.model_dump()
                cached[item.key] = data
                cache.put("stage1_extract", cached)
            merged_entities = sorted(
                _norm_entities(_clean_extracted_entities(item.entities))
                | _norm_entities(_clean_extracted_entities(data.get("entities") or []))
            )
            item.entities = merged_entities or item.entities
            item.topics = item.topics or [str(t) for t in data.get("topics") or []]
            item.claim = item.claim or str(data.get("claim", ""))
            changed = True

        # Deterministic ticker <-> company-name enrichment for every item
        # (including ones that skipped extraction): this is what lets stage 4
        # key a CapitolScope trade against name-only prose.
        extras = resolve_tickers(item.entities, f"{item.title}. {item.claim} {item.text[:800]}")
        if extras:
            item.entities = sorted(set(item.entities) | set(extras))
            changed = True

        if changed:
            store.set_analysis(
                item.source,
                item.source_id,
                entities=item.entities,
                topics=item.topics,
                extra={"claim": item.claim},
            )


# ---------------------------------------------------------------------------
# Stage 2 - cluster + dedup
# ---------------------------------------------------------------------------

_NAME_SYSTEM = """\
You headline one real-world news story that several items all cover.
Return JSON only: a specific news headline of 4-9 words saying who did what,
e.g. "Oil Falls as US-Iran Talks Resume" or "Berlin Pride Attacker Shot Dead".
Never a topic label or keyword list; never words like Story, Reports, Update,
Coverage, News.
"""

# Headline sanity: an acceptable name is short, or reads like a sentence
# (contains a connective/verb-ish function word), and never ends in a
# topic-label noun. Failures fall back to the best member headline.
_LABEL_NOUN_RE = re.compile(r"(story|stories|reports?|updates?|coverage|news)\s*$", re.IGNORECASE)
_FUNCTION_WORDS = {
    "as", "in", "on", "to", "of", "at", "for", "with", "after", "over", "amid",
    "into", "from", "by", "against", "despite", "is", "are", "falls", "rises",
}


def _looks_like_headline(name: str) -> bool:
    words = name.strip().split()
    if not words or _LABEL_NOUN_RE.search(name):
        return False
    if len(words) <= 4:
        return True
    return any(w.casefold().strip(".,'") in _FUNCTION_WORDS for w in words)


class _UnionFind:
    def __init__(self, keys: list[str]) -> None:
        self.parent = {k: k for k in keys}

    def find(self, k: str) -> str:
        while self.parent[k] != k:
            self.parent[k] = self.parent[self.parent[k]]
            k = self.parent[k]
        return k

    def union(self, a: str, b: str) -> None:
        ra, rb = self.find(a), self.find(b)
        if ra != rb:
            self.parent[rb] = ra


def _url_domain(url: str) -> str:
    try:
        return url.split("//", 1)[-1].split("/", 1)[0].removeprefix("www.").casefold()
    except Exception:
        return ""


def _syndication_sim() -> float:
    # Near-copy threshold: syndicated wire copies measure 0.93+ on this corpus.
    try:
        return float(os.getenv("PHEME_SYNDICATION_SIM", "0.95"))
    except ValueError:
        return 0.95


def _dedupe_syndicated(
    items: list["_Item"],
    neighbor_map: dict[str, list[tuple[str, float]]],
    threshold: float,
) -> dict[str, list["_Item"]]:
    """Group near-identical copies (same wire story, many outlets).

    Returns canonical_key -> all copies (canonical first). Canonical is the
    copy with a clean title, then the longest text - the best face for the
    story; the rest only contribute outlet count and URLs.
    """
    uf = _UnionFind([i.key for i in items])
    for key, neighbours in neighbor_map.items():
        for other_key, score in neighbours:
            if score >= threshold:
                uf.union(key, other_key)
    groups: dict[str, list[_Item]] = {}
    for item in items:
        groups.setdefault(uf.find(item.key), []).append(item)

    out: dict[str, list[_Item]] = {}
    for members in groups.values():
        members.sort(
            key=lambda m: (not _is_junk_text(m.title), len(m.text), m.published_at),
            reverse=True,
        )
        out[members[0].key] = members
    return out


async def _stage_cluster(
    items: list[_Item], store: NewsStore, cache: StageCache, fp: str
) -> list[ClusterSummary]:
    cached = cache.get("stage2_clusters", fingerprint=fp)
    if cached:
        return [ClusterSummary(**c) for c in cached]

    by_point = {i.point_id: i for i in items}

    # One qdrant recommend-by-id pass per item feeds both edge sets below.
    # k=12: syndicated near-copies (0.93+) crowd a small window and hide
    # same-story cross-outlet neighbours at 0.80-0.90 (the Berlin split).
    neighbor_map: dict[str, list[tuple[str, float]]] = {}
    for item in items:
        hits = await asyncio.to_thread(store.similar, item.point_id, 12)
        neighbor_map[item.key] = [
            (by_point[pid].key, score) for pid, score in hits if pid in by_point
        ]

    # Collapse syndicated near-copies first so cluster size measures genuine
    # distinct coverage, not how many regional outlets ran the same wire text.
    dupe_groups = _dedupe_syndicated(items, neighbor_map, _syndication_sim())
    canonical_items = [group[0] for group in dupe_groups.values()]
    canonical_of = {m.key: group[0].key for group in dupe_groups.values() for m in group}
    if len(canonical_items) < len(items):
        logger.info(
            "syndication dedup: %d items -> %d distinct stories",
            len(items), len(canonical_items),
        )

    uf = _UnionFind([i.key for i in canonical_items])

    # Entity-overlap edges (the Ground News move: one story, multiple sources).
    # Company name + its ticker collapse to one identity here, otherwise the
    # ticker enrichment makes every single-company match count as two shared
    # entities and glues loosely related market stories together.
    from zeus.pheme.tickers import NAME_TO_TICKER

    def _edge_entities(entities: list[str]) -> set[str]:
        return {
            NAME_TO_TICKER.get(e, e.upper() if e.upper() in NAME_TO_TICKER.values() else e).casefold()
            for e in _norm_entities(entities)
        }

    for idx, a in enumerate(canonical_items):
        ea = _edge_entities(a.entities)
        if not ea:
            continue
        for b in canonical_items[idx + 1 :]:
            eb = _edge_entities(b.entities)
            shared = ea & eb
            if not shared:
                continue
            jaccard = len(shared) / max(1, len(ea | eb))
            if len(shared) >= 2 or jaccard >= 0.34:
                uf.union(a.key, b.key)

    # Embedding-neighbour edges, endpoints mapped onto canonicals.
    sim_threshold = _cluster_sim_threshold()
    for item in items:
        a = canonical_of[item.key]
        for other_key, score in neighbor_map[item.key]:
            if score >= sim_threshold:
                uf.union(a, canonical_of[other_key])

    def _build_groups() -> dict[str, list[_Item]]:
        out: dict[str, list[_Item]] = {}
        for item in canonical_items:
            out.setdefault(uf.find(item.key), []).append(item)
        return out

    groups = _build_groups()

    # Second pass: merge same-story clusters that exact-phrase entity overlap
    # missed. Candidates share >= 2 salient entity tokens with at least one
    # distinctive (non-run-frequent); an embedding bridge (rep item's
    # neighbour in the other cluster >= PHEME_CLUSTER_MERGE_SIM) makes the
    # final call so generic token overlap alone never merges.
    merge_sim = _cluster_merge_sim()
    roots = list(groups)
    token_sets = {
        root: _entity_tokens([e for m in members for e in m.entities])
        for root, members in groups.items()
    }
    run_generic = _generic_tokens(list(token_sets.values()))
    for i, ra in enumerate(roots):
        for rb in roots[i + 1 :]:
            if uf.find(ra) == uf.find(rb):
                continue
            shared_tokens = token_sets[ra] & token_sets[rb]
            if len(shared_tokens) < 2 or not (shared_tokens - run_generic):
                continue
            small, large = sorted((ra, rb), key=lambda r: len(groups[r]))
            # Bridge targets include syndicated copies of the large cluster's
            # members, not just canonicals - a wire copy is a valid bridge.
            large_points = {
                dupe.point_id
                for m in groups[large]
                for dupe in dupe_groups.get(m.key, [m])
            }
            rep = groups[small][0]
            bridged = any(
                pid in large_points and score >= merge_sim
                for pid, score in await asyncio.to_thread(store.similar, rep.point_id, 25)
            )
            if bridged:
                uf.union(ra, rb)
                logger.info(
                    "merged clusters on embedding bridge (>=%.2f): %d + %d items",
                    merge_sim, len(groups[ra]), len(groups[rb]),
                )
    groups = _build_groups()

    # Coherence veto: small groups where some member shares no distinctive
    # entity with the rest were usually glued by a borderline embedding edge
    # (Spain retail sales + French wildfires, 2026-07-28). One cheap yes/no
    # LLM call decides; "no" splits the outlier back out.
    from zeus.pheme.models import SameStory

    for root in list(groups):
        members = groups[root]
        if not 2 <= len(members) <= 3:
            continue
        for member in list(members):
            others = [m for m in members if m.key != member.key]
            if not others:
                continue
            own = _entity_tokens(member.entities) - run_generic
            rest = set().union(*(_entity_tokens(o.entities) for o in others)) - run_generic
            if own & rest:
                continue
            try:
                verdict = await pheme_llm_call(
                    system=(
                        "You judge whether two news items report the same "
                        "real-world story. Return JSON only: same (bool). "
                        "Related topics or the same region are NOT the same story."
                    ),
                    user=(
                        f"Item A: {member.title or member.claim or member.text[:150]}\n"
                        f"Item B: {others[0].title or others[0].claim or others[0].text[:150]}"
                    ),
                    response_format=SameStory,
                    max_tokens=40,
                    caller="pheme.coherence",
                )
            except PhemeLLMFailed:
                continue
            if not verdict.same:
                members.remove(member)
                groups[member.key] = [member]
                logger.info(
                    "coherence veto split %r out of %r", member.title[:40], root
                )
        if not members:
            groups.pop(root, None)

    clusters: list[ClusterSummary] = []
    for root, members in groups.items():
        members.sort(key=lambda i: i.published_at, reverse=True)
        # All copies (canonical + syndicated) for provenance, outlets, and
        # significance write-backs; `members` stays the distinct-story view.
        all_members = [d for m in members for d in dupe_groups.get(m.key, [m])]
        outlets = sorted({_url_domain(m.url) for m in all_members if m.url} - {""})
        entities = sorted({e for m in members for e in _norm_entities(m.entities)})
        topics = sorted({t for m in members for t in m.topics})
        # Representative text must never be filename residue: prefer the newest
        # member with a clean claim, then a clean title, then clean body text.
        claim = next(
            (m.claim for m in members if m.claim and not _is_junk_text(m.claim)), ""
        ) or next(
            (m.text[:200] for m in members if not _is_junk_text(m.text[:200])), ""
        )
        name = next((m.title for m in members if not _is_junk_text(m.title)), "")
        if not name:
            name = claim[:60] if claim else members[0].title
        if len(members) > 1:
            titles = "\n".join(
                f"- {m.title}: {m.claim or m.text[:120]}"
                for m in members[:6]
                if not _is_junk_text(m.title) or m.claim
            )
            try:
                named = await pheme_llm_call(
                    system=_NAME_SYSTEM,
                    user=f"Items covering one story:\n{titles}",
                    response_format=ClusterName,
                    max_tokens=60,
                    caller="pheme.cluster_name",
                )
                candidate = named.name.strip()
                if candidate and not _is_junk_text(candidate) and _looks_like_headline(candidate):
                    name = candidate
            except PhemeLLMFailed:
                pass
        seen_domains: set[str] = set()
        urls: list[str] = []
        for m in all_members:
            domain = _url_domain(m.url)
            if m.url and domain not in seen_domains:
                seen_domains.add(domain)
                urls.append(m.url)
        clusters.append(
            ClusterSummary(
                key=root,
                name=name,
                item_ids=[m.key for m in all_members],
                titles=[m.title for m in members],
                sources=sorted({m.source for m in all_members}),
                urls=urls,
                entities=entities[:12],
                topics=topics[:8],
                claim=claim,
                unique_count=len(members),
                outlet_count=len(outlets),
            )
        )
    clusters.sort(key=lambda c: len(c.item_ids), reverse=True)
    cache.put("stage2_clusters", [c.model_dump() for c in clusters], fingerprint=fp)
    return clusters


# ---------------------------------------------------------------------------
# Stage 3 - thread to history
# ---------------------------------------------------------------------------

_THREAD_NOTE_SYSTEM = """\
You write the daily update line for an ongoing news story. You get what was
known on previous days, then what is known today. Return JSON only:
- changed: true when today brings a substantive development, false otherwise.
- note: ONE sentence written like a news update about the events themselves,
  e.g. "Talks continue in Vienna while oil extends its slide." When changed
  is false: "No major developments; <one short clause on where things stand>."
Never use the words "coverage", "claim", "information", "reported", or refer
to the reporting itself. Plain text, neutral, no preamble.
"""


async def _stage_thread(
    clusters: list[ClusterSummary], store: NewsStore, cache: StageCache, since: str, fp: str
) -> None:
    """Attach persistent story-thread identity (zeus/pheme/threads.py).

    A cluster matching a thread first seen on an earlier day is a
    "development" with a real day count and a history-grounded change note;
    everything else starts a new thread. The cached path skips registry
    writes so a same-item-set rerun never inflates day counts.
    """
    cached: dict[str, Any] = cache.get("stage3_thread", fingerprint=fp) or {}
    if cached:
        for cluster in clusters:
            data = cached.get(cluster.key) or {}
            cluster.thread_status = data.get("status", "new")
            cluster.thread_note = data.get("note", "")
            cluster.thread_id = data.get("thread_id", "")
            cluster.thread_days = int(data.get("days", 1))
            cluster.thread_static = bool(data.get("static", False))
        return

    from functools import partial

    from zeus.pheme.threads import match_and_update

    rows = [
        (c.key, _entity_tokens(c.entities) | _entity_tokens([c.name]), c.name, c.claim)
        for c in clusters
    ]
    generic = _generic_tokens([r[1] for r in rows])
    matches = await asyncio.to_thread(
        partial(match_and_update, rows, generic_tokens=generic)
    )

    for cluster in clusters:
        m = matches.get(cluster.key)
        if m is None:
            continue
        cluster.thread_id = m.thread_id
        cluster.thread_days = m.days_seen
        if m.is_new:
            cluster.thread_status = "new"
            cluster.thread_note = ""
        else:
            cluster.thread_status = "development"
            cluster.thread_note = ""
            history_lines = "\n".join(
                f"- {h.get('date')}: {h.get('claim') or h.get('name')}"
                for h in m.prior_history
                if h.get("claim") or h.get("name")
            )
            if history_lines:
                try:
                    note = await pheme_llm_call(
                        system=_THREAD_NOTE_SYSTEM,
                        user=(
                            f"Known on previous days (story began {m.first_seen}):\n{history_lines}\n\n"
                            f"Known today ({cluster.name}): {cluster.claim}"
                        ),
                        response_format=ThreadNote,
                        max_tokens=150,
                        caller="pheme.thread",
                    )
                    if note.note.strip() and not _is_junk_text(note.note):
                        cluster.thread_note = note.note.strip()
                    cluster.thread_static = not note.changed
                except PhemeLLMFailed:
                    pass
        cached[cluster.key] = {
            "status": cluster.thread_status,
            "note": cluster.thread_note,
            "thread_id": cluster.thread_id,
            "days": cluster.thread_days,
            "static": cluster.thread_static,
        }
    cache.put("stage3_thread", cached, fingerprint=fp)


# ---------------------------------------------------------------------------
# Stage 4 - cross-source correlate (the edge stage)
# ---------------------------------------------------------------------------

_CORRELATE_SYSTEM = """\
You judge whether a congressional-trading signal and a news story are
meaningfully connected. A meaningful connection is a congressional trade,
herding cluster, or bill touching a sector or ticker that lines up with a
news story about the same company, sector, or policy area. Coincidental
co-mentions are not connections. Return JSON only: connected (bool), claim
(one sentence naming the linking entity when connected), confidence (0-1).
Example claim: "Congressional selling of XOM lines up with reporting on new
Gulf drilling restrictions (linking entity: XOM / Energy)."
"""


async def _stage_correlate(
    items: list[_Item], cache: StageCache, fp: str
) -> list[Correlation]:
    cached = cache.get("stage4_correlations", fingerprint=fp)
    if cached is not None:
        return [Correlation(**c) for c in cached]

    cs_items = [i for i in items if i.source == "capitolscope"]
    news_items = [i for i in items if i.source == "canary"]
    candidates: list[tuple[_Item, _Item, set[str]]] = []
    seen_pairs: set[tuple[str, str]] = set()
    for cs in cs_items:
        e_cs = _norm_entities(cs.entities)
        if not e_cs:
            continue
        for art in news_items:
            shared = e_cs & _norm_entities(art.entities)
            if shared and (cs.key, art.key) not in seen_pairs:
                seen_pairs.add((cs.key, art.key))
                candidates.append((cs, art, shared))
    # Strongest overlap first; never brute-force all pairs.
    candidates.sort(key=lambda t: len(t[2]), reverse=True)
    candidates = candidates[: _max_correlation_pairs()]

    correlations: list[Correlation] = []
    for cs, art, shared in candidates:
        try:
            verdict = await pheme_llm_call(
                system=_CORRELATE_SYSTEM,
                user=(
                    f"Congressional signal: {cs.title}\n{cs.text[:600]}\n\n"
                    f"News story: {art.title}\n{art.claim or art.text[:600]}\n\n"
                    f"Shared entities: {', '.join(sorted(shared))}"
                ),
                response_format=CorrelationJudgment,
                max_tokens=200,
                caller="pheme.correlate",
            )
        except PhemeLLMFailed as exc:
            logger.warning("correlate failed for %s x %s: %s", cs.key, art.key, exc)
            continue
        if verdict.connected and verdict.confidence >= 0.5 and verdict.claim.strip():
            correlations.append(
                Correlation(
                    entities=sorted(shared),
                    claim=verdict.claim.strip(),
                    source_ids=[cs.key, art.key],
                    confidence=round(verdict.confidence, 2),
                )
            )
    correlations.sort(key=lambda c: c.confidence, reverse=True)
    cache.put("stage4_correlations", [c.model_dump() for c in correlations], fingerprint=fp)
    return correlations


# ---------------------------------------------------------------------------
# Stage 5 - rank + select
# ---------------------------------------------------------------------------

_RANK_SYSTEM = """\
You score how relevant each news story is to this specific reader, given
their profile facts. Return JSON only: scores, one float 0.0-1.0 per story,
in the same order as the numbered list. 1.0 = directly touches their work,
projects, or holdings; 0.0 = no plausible interest. Differentiate: stories
differ in relevance, so identical scores for every story are wrong unless
the list is truly uniform.
"""


async def _score_relevance(
    clusters: list[ClusterSummary], facts: list[str]
) -> list[float] | None:
    """One scoring call over the candidate clusters; retried once when the
    model returns a degenerate uniform vector."""
    listing = "\n".join(
        f"{i + 1}. {c.name} [{', '.join(c.entities[:4])}]: {c.claim[:150]}"
        for i, c in enumerate(clusters)
    )
    feedback_block = ""
    try:
        from zeus.pheme.feedback import recent_reaction_summary

        liked, disliked = recent_reaction_summary()
        if liked:
            feedback_block += "\nRecently upvoted stories:\n" + "\n".join(f"- {n}" for n in liked)
        if disliked:
            feedback_block += "\nRecently downvoted stories:\n" + "\n".join(f"- {n}" for n in disliked)
    except Exception as exc:
        logger.debug("reaction summary unavailable: %s", exc)
    user = (
        "Reader profile:\n" + "\n".join(f"- {f}" for f in facts)
        + feedback_block
        + f"\n\nStories:\n{listing}"
    )
    for attempt in range(2):
        try:
            scored = await pheme_llm_call(
                system=_RANK_SYSTEM,
                user=user if attempt == 0 else user
                + "\n\nYour previous scores were all identical, which is not a "
                "credible ranking. Score each story on its own merits.",
                response_format=ClusterScores,
                max_tokens=250,
                caller="pheme.rank",
            )
        except PhemeLLMFailed as exc:
            logger.warning("relevance scoring failed: %s", exc)
            return None
        scores = [max(0.0, min(1.0, float(s))) for s in scored.scores[: len(clusters)]]
        if len(scores) >= min(3, len(clusters)) and (
            len(set(scores)) > 1 or len(clusters) <= 3
        ):
            logger.info("pheme rank relevance scores: %s", scores)
            return scores
        logger.warning("relevance scores degenerate (%s), retrying", scores[:5])
    return None


def _cluster_heuristic(cluster: ClusterSummary, correlated_keys: set[str]) -> float:
    heuristic = 0.0
    # Distinct-story size term (post-dedup): breadth of genuine coverage,
    # not how many regional outlets ran the same wire copy.
    n = cluster.unique_count or len(cluster.item_ids)
    if n > 1:
        heuristic += min(0.35, 0.08 * math.log2(n) + 0.06)
    # Outlet breadth is still real signal (14 outlets picked it up), just a
    # weaker one than distinct coverage.
    if cluster.outlet_count > 1:
        heuristic += min(0.15, 0.04 * math.log2(cluster.outlet_count))
    if len(cluster.sources) > 1:
        heuristic += 0.2                                                   # cross-source story
    if cluster.thread_status == "development":
        if cluster.thread_static:
            # A story that keeps running with nothing new should sink, not
            # coast on its development bonus (UK election at "day 3" with
            # "no new information" was still #2 on 2026-07-28).
            heuristic -= min(0.12, 0.04 * max(0, cluster.thread_days - 1))
        else:
            heuristic += 0.1                                               # substantive development
    if any(k in correlated_keys for k in cluster.item_ids):
        heuristic += 0.25                                                  # part of the edge
    return max(0.0, heuristic)


async def _stage_rank(
    clusters: list[ClusterSummary],
    correlations: list[Correlation],
    items_by_key: dict[str, _Item],
    store: NewsStore,
    cache: StageCache,
    fp: str,
) -> None:
    correlated_keys = {sid for c in correlations for sid in c.source_ids}
    heuristics = [_cluster_heuristic(c, correlated_keys) for c in clusters]

    # Relevance-scoring candidates are the top clusters by heuristic, not by
    # raw size: a 1-item correlation-bearing cluster matters more to this
    # reader than the fifth syndicated wire story.
    candidate_idx = sorted(
        range(len(clusters)), key=lambda i: heuristics[i], reverse=True
    )[:15]

    relevance: list[float] = [0.5] * len(clusters)
    cached = cache.get("stage5_rank", fingerprint=fp)
    if cached and len(cached.get("relevance", [])) == len(clusters):
        relevance = [float(x) for x in cached["relevance"]]
    else:
        facts: list[str] = []
        try:
            from zeus.memory.search import get_profile_facts, search_memories

            # Profile facts are partitioned by ZEUS_USER_ID (memories are
            # stored under "chris", not the generic default).
            user_id = os.getenv("ZEUS_USER_ID", "user")
            facts = await asyncio.to_thread(get_profile_facts, user_id, 6)
            # The generic profile query surfaces working-style facts; news
            # ranking needs the interest facts specifically, so fetch them
            # with a targeted query and merge.
            interest_hits = await asyncio.to_thread(
                search_memories,
                "news market interests follows reads congressional trading semiconductors",
                user_id,
                6,
            )
            for hit in interest_hits:
                text = str(hit.get("memory", "")).strip()
                if text and text not in facts:
                    facts.append(text)
        except Exception as exc:
            logger.warning("profile facts unavailable for ranking: %s", exc)
        if not facts:
            logger.warning("no profile facts; relevance stays neutral 0.5 for all clusters")
        elif clusters:
            scores = await _score_relevance([clusters[i] for i in candidate_idx], facts)
            if scores:
                # Clusters below the candidate cut were never judged; they must
                # not outrank scored candidates by keeping the neutral default.
                relevance = [0.2] * len(clusters)
                for pos, s in enumerate(scores):
                    relevance[candidate_idx[pos]] = s
        cache.put("stage5_rank", {"relevance": relevance}, fingerprint=fp)

    fb_weights: dict[str, float] = {}
    fb_scale = 0.0
    try:
        from zeus.pheme.feedback import cluster_feedback_score, feedback_weight, preference_weights

        fb_weights = preference_weights()
        fb_scale = feedback_weight()
        if fb_weights:
            logger.info("pheme rank using %d feedback preference tokens", len(fb_weights))
    except Exception as exc:
        logger.debug("feedback weights unavailable: %s", exc)

    for i, cluster in enumerate(clusters):
        heuristic = heuristics[i]
        # 65/35 blend: the local 7B scores conservatively (mostly zeros), so
        # structural evidence keeps the upper hand and relevance nudges.
        base = 0.65 * min(1.0, heuristic / 0.9) + 0.35 * relevance[i]
        # Reader feedback term: thumbs on past digests nudge matching
        # entities/topics up or down (see zeus/pheme/feedback.py).
        if fb_weights and fb_scale:
            base += fb_scale * cluster_feedback_score(
                cluster.entities, cluster.topics, fb_weights
            )
        cluster.significance = round(max(0.0, min(1.0, base)), 3)
        for key in cluster.item_ids:
            item = items_by_key.get(key)
            if item is not None:
                await asyncio.to_thread(
                    store.set_analysis,
                    item.source,
                    item.source_id,
                    significance=cluster.significance,
                )
    clusters.sort(key=lambda c: c.significance, reverse=True)


# ---------------------------------------------------------------------------
# Stage 6 - synthesize
# ---------------------------------------------------------------------------

_LEAD_SYSTEM = """\
You write the lead paragraph of a personal news digest. 2-4 sentences,
plain text, no markdown, no preamble, voice-friendly. Lead with the most
significant story; mention the cross-source connection when one exists.
Neutral tone, no investment advice.
"""


_INSIGHTS_SYSTEM = """\
You write the insight section of a personal news digest: observations that
read ACROSS today's stories, not restatements of any single one. Look for
shared drivers, tensions between stories, second-order implications, and
things worth watching next. Return JSON only: 2-4 insights, each exactly one
sentence, plain text, neutral tone, no investment advice, no hedging filler.
"""


async def _synthesize_insights(
    top: list[ClusterSummary], correlations: list[Correlation]
) -> list[str]:
    if not top:
        return []
    story_block = "\n".join(
        f"- {c.name} ({c.thread_status}): {c.claim[:180]}"
        + (f" | what changed: {c.thread_note}" if c.thread_note else "")
        for c in top
    )
    conn_block = "\n".join(f"- {c.claim}" for c in correlations[:3]) or "(none)"
    user = f"Today's stories:\n{story_block}\n\nCross-source connections:\n{conn_block}"
    raw: list[str] = []
    try:
        parsed = await pheme_llm_call(
            system=_INSIGHTS_SYSTEM,
            user=user,
            response_format=InsightList,
            max_tokens=400,
            caller="pheme.insights",
        )
        raw = list(parsed.insights)
    except PhemeLLMFailed as exc:
        logger.warning("structured insight synthesis failed: %s", exc)
    if not raw:
        # qwen2.5:7b often returns a schema-valid but EMPTY {"insights": []}
        # while producing good observations in free text (2026-07-28 digest
        # shipped with no insights because of this). Fall back to text mode
        # and split lines.
        try:
            text = await pheme_llm_text(
                system=_INSIGHTS_SYSTEM.replace("Return JSON only:", "Write plain text:")
                + "\nOne insight per line. No bullets, no numbering, no preamble.",
                user=user,
                max_tokens=400,
                caller="pheme.insights_text",
            )
            raw = [ln.strip(" -*•") for ln in text.split("\n") if ln.strip()]
        except PhemeLLMFailed as exc:
            logger.warning("text insight fallback failed: %s", exc)
            return []
    out = []
    for line in raw[:4]:
        line = line.strip()
        if line and not _is_junk_text(line):
            out.append(line)
    return out


def _audio_enabled() -> bool:
    return os.getenv("PHEME_AUDIO", "1").strip() not in ("0", "false", "no")


def _audio_summary_dict(
    lead: str, insights: list[str], top: list[ClusterSummary]
) -> dict[str, Any]:
    """Map a digest onto the newsletter _generate_audio() shape.

    The TTS script becomes: lead, then per-story one-liners as 'highlights',
    then insights as the 'advice' closer. Voice-friendly: no URLs, no markup.
    """
    bullets = []
    for cluster in top:
        take = _one_line_take(cluster)
        line = f"{cluster.name}. {take}" if take else cluster.name
        if cluster.thread_status == "development" and cluster.thread_days > 1:
            line = f"Day {cluster.thread_days} of {line}"
        bullets.append(line)
    return {
        "summary": lead.strip(),
        "bullets": bullets,
        "advice": " ".join(insights),
    }


def _coverage_label(cluster: ClusterSummary) -> str:
    """Human coverage line: distinct stories + outlet breadth when they differ."""
    n = cluster.unique_count or len(cluster.item_ids)
    label = f"{n} stories" if n > 1 else "1 story"
    if cluster.outlet_count > n:
        label += f" · {cluster.outlet_count} outlets"
    return label


def _one_line_take(cluster: ClusterSummary) -> str:
    take = cluster.thread_note or cluster.claim
    take = take.strip().rstrip(".")
    if _is_junk_text(take):
        return ""
    return (take[:200] + "…") if len(take) > 200 else take


def _compose_body(
    lead: str,
    insights: list[str],
    correlations: list[Correlation],
    top: list[ClusterSummary],
) -> str:
    lines: list[str] = [lead.strip(), ""]
    if insights:
        lines.append("Insights:")
        for ins in insights:
            lines.append(f"- {ins}")
        lines.append("")
    if correlations:
        lines.append("Connections (congressional signal x news):")
        for c in correlations[:5]:
            lines.append(f"- {c.claim} (confidence {c.confidence:.0%})")
        lines.append("")
    lines.append("Top stories:")
    for i, cluster in enumerate(top, 1):
        if cluster.thread_status == "development":
            marker = f"day {cluster.thread_days}" if cluster.thread_days > 1 else "developing"
        else:
            marker = "new"
        lines.append(f"{i}. {cluster.name} ({_coverage_label(cluster)}, {marker})")
        take = _one_line_take(cluster)
        if take:
            lines.append(f"   {take}.")
        if cluster.urls:
            extra = len(cluster.urls) - 1
            lines.append(
                f"   {cluster.urls[0]}" + (f" (+{extra} more)" if extra > 0 else "")
            )
    return "\n".join(lines).strip()


def _compose_public_trim(
    correlations: list[Correlation], top: list[ClusterSummary]
) -> tuple[str, list[str]]:
    """Public Twitter trim: headline plus one-line take, distinct from the personal digest."""
    if correlations:
        lead = correlations[0].claim
    elif top:
        lead = f"{top[0].name}: {_one_line_take(top[0])}."
    else:
        return "", []
    if len(lead) > 270:
        lead = lead[:267].rstrip() + "…"
    thread: list[str] = []
    for cluster in top:
        if len(thread) >= 3:
            break
        take = _one_line_take(cluster)
        # Public surface: never tweet filename residue.
        if _is_junk_text(cluster.name) and not take:
            continue
        tweet = f"{cluster.name} - {take}." if take else cluster.name
        if cluster.urls:
            tweet = f"{tweet[:240].rstrip()} {cluster.urls[0]}"
        thread.append(tweet[:280])
    return lead, thread


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

async def run_pheme_pipeline(
    trigger: Literal["daily", "breaking"],
    *,
    since: str | None = None,
    scope_item_keys: list[str] | None = None,
    store: NewsStore | None = None,
) -> PhemeDigest:
    """Run the staged pipeline over freshly ingested items and return a digest.

    ``since`` defaults to 24h back for daily runs, 6h for breaking runs.
    ``scope_item_keys`` (breaking) restricts the run to one cluster's items.
    """
    store = store or get_news_store()
    now = datetime.now(timezone.utc)
    if since is None:
        lookback = 24 if trigger == "daily" else 6
        since = (now - timedelta(hours=lookback)).isoformat()

    hits = await asyncio.to_thread(
        store.scroll_recent, since=since, sources=NEWS_SOURCES, limit=_max_items()
    )
    items = [_Item.from_hit(h) for h in hits if h.id]
    if scope_item_keys:
        wanted = set(scope_item_keys)
        items = [i for i in items if i.key in wanted]

    digest_id = uuid.uuid4().hex[:12]
    if not items:
        logger.info("pheme %s run: no fresh items since %s", trigger, since)
        return PhemeDigest(
            id=digest_id,
            trigger=trigger,
            generated_at=now.isoformat(),
            stats={"items": 0, "since": since},
        )

    cache = StageCache(run_key(trigger, now))
    logger.info("pheme %s run: %d item(s) since %s", trigger, len(items), since)

    # Item-set fingerprint: stages 2+ invalidate automatically when a rerun
    # sees a different set of fresh items (stage 1 stays per-item keyed).
    fp = hashlib.sha1(",".join(sorted(i.key for i in items)).encode()).hexdigest()[:12]
    await _stage_extract(items, store, cache)
    clusters = await _stage_cluster(items, store, cache, fp)
    await _stage_thread(clusters, store, cache, since, fp)
    correlations = await _stage_correlate(items, cache, fp)
    items_by_key = {i.key: i for i in items}
    await _stage_rank(clusters, correlations, items_by_key, store, cache, fp)

    # Undisplayable clusters (junk name, no claim - e.g. an all-junk-title
    # GDELT group) never reach the digest regardless of score.
    top = [c for c in clusters if not (_is_junk_text(c.name) and not c.claim.strip())][: _top_n()]
    conn_block = "\n".join(f"- {c.claim}" for c in correlations[:3]) or "(none found)"
    story_block = "\n".join(
        f"- {c.name} ({c.thread_status}): {c.claim[:150]}" for c in top
    )
    try:
        lead = await pheme_llm_text(
            system=_LEAD_SYSTEM,
            user=f"Cross-source connections:\n{conn_block}\n\nTop stories:\n{story_block}",
            max_tokens=300,
            caller="pheme.synthesize",
        )
    except PhemeLLMFailed as exc:
        logger.warning("lead synthesis failed, using fallback: %s", exc)
        lead = top[0].claim if top else "No significant news in this window."

    insights = await _synthesize_insights(top, correlations)

    # Morning-listen track via the newsletter TTS path. Best-effort: returns
    # None whenever Voicebox is unreachable, and the digest ships without it.
    audio_file: str | None = None
    if _audio_enabled() and top:
        try:
            from zeus.core.newsletter import _generate_audio

            audio_file = await _generate_audio(_audio_summary_dict(lead, insights, top))
        except Exception as exc:
            logger.warning("digest audio generation failed: %s", exc)

    public_lead, public_thread = _compose_public_trim(correlations, top)
    digest = PhemeDigest(
        id=digest_id,
        trigger=trigger,
        generated_at=now.isoformat(),
        lead=lead,
        insights=insights,
        connections=correlations,
        clusters=top,
        body=_compose_body(lead, insights, correlations, top),
        audio_file=audio_file,
        audio_url=f"/api/newsletter/audio/{audio_file}" if audio_file else None,
        public_lead=public_lead,
        public_thread=public_thread,
        stats={
            "items": len(items),
            "clusters": len(clusters),
            "correlations": len(correlations),
            "since": since,
        },
    )
    cache.put("digest", digest.model_dump(), fingerprint=fp)
    _record_manifest_entry(digest)
    return digest


def _record_manifest_entry(digest: PhemeDigest) -> None:
    """Mirror the digest into the newsletter manifest so the /newsletters UI
    and zeus_newsletter_latest surface Pheme as a sibling digest type."""
    if not digest.clusters:
        return
    try:
        from zeus.core.newsletter import (
            DigestEntry,
            _append_digest,
            _load_manifest,
            _manifest_lock,
            _save_manifest,
        )

        entry = DigestEntry(
            id=digest.id,
            newsletter_type="pheme",
            date=digest.generated_at,
            summary=digest.lead,
            bullets=[f"{c.name}: {_one_line_take(c)}" for c in digest.clusters],
            advice="\n".join(c.claim for c in digest.connections[:3]),
            audio_file=digest.audio_file,
            audio_url=digest.audio_url,
            generated_at=digest.generated_at,
        )
        with _manifest_lock:
            manifest = _load_manifest()
            _append_digest(manifest, entry.model_dump())
            _save_manifest(manifest)
    except Exception as exc:
        logger.warning("failed to mirror pheme digest into newsletter manifest: %s", exc)
