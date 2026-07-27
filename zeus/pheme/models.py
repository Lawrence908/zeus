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

    status: Literal["new", "development"] = "new"
    note: str = Field(default="", description="One sentence: what changed since prior coverage")


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
    significance: float = 0.0
    unique_count: int = 0      # distinct stories after syndication dedup
    outlet_count: int = 0      # distinct outlet domains across all copies


class PhemeDigest(BaseModel):
    id: str
    trigger: Literal["daily", "breaking"]
    generated_at: str
    lead: str = ""                                          # synthesized lead summary
    insights: list[str] = Field(default_factory=list)       # cross-story observations
    connections: list[Correlation] = Field(default_factory=list)
    clusters: list[ClusterSummary] = Field(default_factory=list)
    body: str = ""                                          # full personal digest (markdown-ish plain text)
    public_lead: str = ""                                   # trimmed lead tweet text
    public_thread: list[str] = Field(default_factory=list)  # follow-up tweets
    stats: dict[str, Any] = Field(default_factory=dict)
