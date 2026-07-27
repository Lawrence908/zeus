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
    cached: dict[str, Any] = cache.get("stage1_extract") or {}
    for item in items:
        if item.entities and item.claim:
            continue
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
You name one real-world news story that several items all cover.
Return JSON only: a neutral 3-8 word name. No punctuation beyond spaces.
"""


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


async def _stage_cluster(
    items: list[_Item], store: NewsStore, cache: StageCache, fp: str
) -> list[ClusterSummary]:
    cached = cache.get("stage2_clusters", fingerprint=fp)
    if cached:
        return [ClusterSummary(**c) for c in cached]

    uf = _UnionFind([i.key for i in items])
    by_key = {i.key: i for i in items}
    by_point = {i.point_id: i for i in items}

    # Entity-overlap edges (the Ground News move: one story, multiple sources).
    for idx, a in enumerate(items):
        ea = _norm_entities(a.entities)
        if not ea:
            continue
        for b in items[idx + 1 :]:
            eb = _norm_entities(b.entities)
            shared = ea & eb
            if not shared:
                continue
            jaccard = len(shared) / max(1, len(ea | eb))
            if len(shared) >= 2 or jaccard >= 0.34:
                uf.union(a.key, b.key)

    # Embedding-neighbour edges via qdrant recommend-by-id (no re-embedding).
    # k=12: syndicated near-copies (0.93+) crowd a small window and hide
    # same-story cross-outlet neighbours at 0.80-0.90 (the Berlin split).
    sim_threshold = _cluster_sim_threshold()
    for item in items:
        for neighbour_id, score in await asyncio.to_thread(store.similar, item.point_id, 12):
            other = by_point.get(neighbour_id)
            if other is not None and score >= sim_threshold:
                uf.union(item.key, other.key)

    def _build_groups() -> dict[str, list[_Item]]:
        out: dict[str, list[_Item]] = {}
        for item in items:
            out.setdefault(uf.find(item.key), []).append(item)
        return out

    groups = _build_groups()

    # Second pass: merge same-story clusters that exact-phrase entity overlap
    # missed. Candidates share >= 2 salient entity tokens; an embedding bridge
    # (rep item's neighbour in the other cluster >= PHEME_CLUSTER_MERGE_SIM)
    # makes the final call so generic token overlap alone never merges.
    merge_sim = _cluster_merge_sim()
    roots = list(groups)
    token_sets = {
        root: _entity_tokens([e for m in members for e in m.entities])
        for root, members in groups.items()
    }
    for i, ra in enumerate(roots):
        for rb in roots[i + 1 :]:
            if uf.find(ra) == uf.find(rb):
                continue
            if len(token_sets[ra] & token_sets[rb]) < 2:
                continue
            small, large = sorted((ra, rb), key=lambda r: len(groups[r]))
            large_points = {m.point_id for m in groups[large]}
            rep = groups[small][0]  # newest member (sorted below is later; order here is scroll order)
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

    clusters: list[ClusterSummary] = []
    for root, members in groups.items():
        members.sort(key=lambda i: i.published_at, reverse=True)
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
                if named.name.strip() and not _is_junk_text(named.name):
                    name = named.name.strip()
            except PhemeLLMFailed:
                pass
        clusters.append(
            ClusterSummary(
                key=root,
                name=name,
                item_ids=[m.key for m in members],
                titles=[m.title for m in members],
                sources=sorted({m.source for m in members}),
                urls=[m.url for m in members if m.url],
                entities=entities[:12],
                topics=topics[:8],
                claim=claim,
            )
        )
    clusters.sort(key=lambda c: len(c.item_ids), reverse=True)
    cache.put("stage2_clusters", [c.model_dump() for c in clusters], fingerprint=fp)
    return clusters


# ---------------------------------------------------------------------------
# Stage 3 - thread to history
# ---------------------------------------------------------------------------

_THREAD_SYSTEM = """\
You compare today's news story against prior coverage of the same story.
Return JSON only: status is "development" when today's item advances a story
already covered before, otherwise "new". note is one sentence stating what
changed since the prior coverage (empty when status is "new").
"""


async def _stage_thread(
    clusters: list[ClusterSummary], store: NewsStore, cache: StageCache, since: str, fp: str
) -> None:
    cached: dict[str, Any] = cache.get("stage3_thread", fingerprint=fp) or {}
    for cluster in clusters:
        if cluster.key in cached:
            data = cached[cluster.key]
            cluster.thread_status = data.get("status", "new")
            cluster.thread_note = data.get("note", "")
            continue
        query = f"{cluster.name} {' '.join(cluster.entities[:5])}"
        prior = await asyncio.to_thread(
            store.search, query, 5, {"until": since}
        )
        prior = [h for h in prior if h.score >= 0.6 and f"{h.source}:{h.payload.get('source_id')}" not in cluster.item_ids]
        if prior:
            prior_lines = "\n".join(f"- {h.published_at[:10]}: {h.title}" for h in prior[:4])
            try:
                note = await pheme_llm_call(
                    system=_THREAD_SYSTEM,
                    user=(
                        f"Today's story: {cluster.name}\n{cluster.claim}\n\n"
                        f"Prior coverage:\n{prior_lines}"
                    ),
                    response_format=ThreadNote,
                    max_tokens=150,
                    caller="pheme.thread",
                )
                cluster.thread_status = note.status
                cluster.thread_note = note.note
            except PhemeLLMFailed:
                cluster.thread_status = "development"
                cluster.thread_note = ""
        cached[cluster.key] = {"status": cluster.thread_status, "note": cluster.thread_note}
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
    # Log-scaled size term so an 18-item story outranks a 4-item one
    # instead of both saturating a hard cap.
    n = len(cluster.item_ids)
    if n > 1:
        heuristic += min(0.35, 0.08 * math.log2(n) + 0.06)
    if len(cluster.sources) > 1:
        heuristic += 0.2                                                   # cross-source story
    if cluster.thread_status == "development":
        heuristic += 0.1                                                   # ongoing thread
    if any(k in correlated_keys for k in cluster.item_ids):
        heuristic += 0.25                                                  # part of the edge
    return heuristic


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
    try:
        parsed = await pheme_llm_call(
            system=_INSIGHTS_SYSTEM,
            user=f"Today's stories:\n{story_block}\n\nCross-source connections:\n{conn_block}",
            response_format=InsightList,
            max_tokens=400,
            caller="pheme.insights",
        )
    except PhemeLLMFailed as exc:
        logger.warning("insight synthesis failed: %s", exc)
        return []
    out = []
    for line in parsed.insights[:4]:
        line = line.strip()
        if line and not _is_junk_text(line):
            out.append(line)
    return out


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
        marker = "developing" if cluster.thread_status == "development" else "new"
        n = len(cluster.item_ids)
        count = f"{n} articles" if n > 1 else "1 article"
        lines.append(f"{i}. {cluster.name} ({count}, {marker})")
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

    top = clusters[: _top_n()]
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
            generated_at=digest.generated_at,
        )
        with _manifest_lock:
            manifest = _load_manifest()
            _append_digest(manifest, entry.model_dump())
            _save_manifest(manifest)
    except Exception as exc:
        logger.warning("failed to mirror pheme digest into newsletter manifest: %s", exc)
