# zeus/pheme/models.py - Pydantic schemas for Pheme pipeline stages.
#
# Each stage schema is deliberately small: qwen2.5:7b is unreliable at large
# structured outputs, so every LLM call validates against one narrow model.
from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, Field


class ItemExtraction(BaseModel):
    """Stage 1 output for one news item."""

    entities: list[str] = Field(default_factory=list, description="People, orgs, tickers, bill ids")
    topics: list[str] = Field(default_factory=list, description="2-4 short topic tags")
    claim: str = Field(default="", description="One neutral sentence stating what happened")


class ClusterName(BaseModel):
    """Stage 2 output when overlap alone cannot name a cluster."""

    name: str = Field(..., description="3-8 word neutral name for the story")


class ThreadNote(BaseModel):
    """Stage 3 output relating a cluster to prior coverage."""

    status: Literal["new", "development"] = "development"
    changed: bool = Field(
        default=True,
        description="false when today adds nothing substantive to the story",
    )
    note: str = Field(default="", description="One sentence news update: what is new today")


class SameStory(BaseModel):
    """Stage 2 coherence veto for weak two-item merges."""

    same: bool = Field(..., description="true only if both items report the same real-world story")


class CorrelationJudgment(BaseModel):
    """Stage 4 output for one CapitolScope x Canary candidate pair."""

    connected: bool = False
    claim: str = Field(default="", description="One sentence stating the connection and linking entity")
    confidence: float = Field(default=0.0, ge=0.0, le=1.0)


class ClusterScores(BaseModel):
    """Stage 5 output: profile-relevance scores for the candidate clusters."""

    scores: list[float] = Field(
        default_factory=list,
        description="One 0.0-1.0 relevance score per cluster, same order as input",
    )


class InsightList(BaseModel):
    """Stage 6 output: cross-story observations for the digest."""

    insights: list[str] = Field(
        default_factory=list,
        description="2-4 one-sentence analytical observations across today's stories",
    )


class Correlation(BaseModel):
    entities: list[str] = Field(default_factory=list)
    claim: str = ""
    source_ids: list[str] = Field(default_factory=list)
    confidence: float = 0.0


class ClusterSummary(BaseModel):
    """Materialized cluster carried between stages and into the digest."""

    key: str
    name: str = ""
    item_ids: list[str] = Field(default_factory=list)       # "source:source_id"
    titles: list[str] = Field(default_factory=list)
    sources: list[str] = Field(default_factory=list)
    urls: list[str] = Field(default_factory=list)
    entities: list[str] = Field(default_factory=list)
    topics: list[str] = Field(default_factory=list)
    claim: str = ""
    thread_status: str = "new"
    thread_note: str = ""
    thread_id: str = ""        # persistent story-thread identity (threads.db)
    thread_days: int = 0       # how many days this story has run (1 = first day)
    thread_static: bool = False  # development day with nothing substantive new
    significance: float = 0.0
    unique_count: int = 0      # distinct stories after syndication dedup
    outlet_count: int = 0      # distinct outlet domains across all copies


class EditorStory(BaseModel):
    """One story as written by the Claude editor stage (zeus/pheme/editor.py)."""

    index: int = Field(..., description="Candidate number from the input list")
    section: str = ""
    headline: str = ""
    summary: str = ""          # what happened plus the context needed to follow it
    why_it_matters: str = ""
    watch: str = ""            # optional: the next concrete thing to look for


class EditorTweet(BaseModel):
    index: int = Field(..., description="Candidate number whose link is attached")
    text: str = ""


class EditorOutput(BaseModel):
    """Whole-digest output of the Claude editor stage. URLs are never part of
    the model's output: links are attached deterministically by candidate index."""

    lead: str = ""
    stories: list[EditorStory] = Field(default_factory=list)
    insights: list[str] = Field(default_factory=list)
    connections: list[str] = Field(default_factory=list)
    audio_script: str = ""
    public_lead: str = ""
    public_thread: list[EditorTweet] = Field(default_factory=list)


class DigestStory(BaseModel):
    """Editorial copy for one rendered story, aligned with PhemeDigest.clusters."""

    cluster_key: str
    section: str = ""
    headline: str = ""
    summary: str = ""
    why_it_matters: str = ""
    watch: str = ""


class PhemeDigest(BaseModel):
    id: str
    trigger: Literal["daily", "breaking"]
    generated_at: str
    lead: str = ""                                          # synthesized lead summary
    insights: list[str] = Field(default_factory=list)       # cross-story observations
    connections: list[Correlation] = Field(default_factory=list)
    clusters: list[ClusterSummary] = Field(default_factory=list)
    # Claude editor output, same order as clusters. Empty on the local path,
    # which renders from cluster names and claims instead.
    stories: list[DigestStory] = Field(default_factory=list)
    editor_connections: list[str] = Field(default_factory=list)
    editor: str = "local"                                   # "local" or the Claude model that served
    body: str = ""                                          # full personal digest (markdown-ish plain text)
    audio_file: str | None = None                           # TTS filename under NEWSLETTER_AUDIO_DIR
    audio_url: str | None = None                            # served via /api/newsletter/audio/
    public_lead: str = ""                                   # trimmed lead tweet text
    public_thread: list[str] = Field(default_factory=list)  # follow-up tweets
    stats: dict[str, Any] = Field(default_factory=dict)
