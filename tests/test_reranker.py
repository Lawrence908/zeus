# tests/test_reranker.py — rerank-gateway HTTP client: score-order preservation
#
# No gateway is touched: httpx.MockTransport stands in for services/rerank-gateway
# so the one piece of genuinely new logic can be exercised deterministically.
#
# That logic is the scatter. The gateway speaks TEI's wire format, which returns
# [{"index": i, "score": s}, ...] sorted BY SCORE, not by index. Both callers
# (KnowledgeStore._rerank at library.py:401, MemoryStore._rerank at store.py:348)
# do `zip(hits, scores)`, so a client that returned the gateway's order verbatim
# would pair every score with the wrong document — silently, with no exception
# and no obviously-wrong output. That is the failure this file exists to catch.
from __future__ import annotations

import httpx
import pytest

from zeus.memory import reranker


def _client(handler) -> reranker.RerankClient:
    """A RerankClient whose HTTP calls are served by `handler`."""
    c = reranker.RerankClient(url="http://gateway.invalid:8191")
    c._http = httpx.Client(transport=httpx.MockTransport(handler))
    return c


def test_scores_come_back_in_caller_order():
    """The gateway sorts by score; score_pairs must undo that."""

    def handler(request: httpx.Request) -> httpx.Response:
        body = request.read()
        assert b'"raw_scores": true' in body or b'"raw_scores":true' in body
        # Deliberately returned worst-last and NOT in index order.
        return httpx.Response(
            200,
            json=[
                {"index": 2, "score": 9.0},
                {"index": 0, "score": 5.0},
                {"index": 1, "score": -3.0},
            ],
        )

    c = _client(handler)
    pairs = [("q", "first"), ("q", "second"), ("q", "third")]
    assert c.score_pairs(pairs) == [5.0, -3.0, 9.0]


def test_multiple_queries_are_grouped_and_rescattered():
    """Pairs with different queries go out as separate calls, order preserved.

    Both real call sites pass one constant query, but the signature accepts
    arbitrary pairs and must stay honest about it.
    """
    seen: list[dict] = []

    def handler(request: httpx.Request) -> httpx.Response:
        import json

        payload = json.loads(request.read())
        seen.append(payload)
        # Score by position within this query's own texts list, reversed, so a
        # naive implementation that ignores `index` produces a wrong answer.
        n = len(payload["texts"])
        return httpx.Response(
            200,
            json=[{"index": i, "score": float(n - i)} for i in reversed(range(n))],
        )

    c = _client(handler)
    # Interleaved on purpose: positions 0 and 2 are query A, position 1 is B.
    pairs = [("A", "a1"), ("B", "b1"), ("A", "a2")]
    scores = c.score_pairs(pairs)

    assert len(seen) == 2
    assert {tuple(p["texts"]) for p in seen} == {("a1", "a2"), ("b1",)}
    # Query A has two texts -> scores 2.0, 1.0. Query B has one -> 1.0.
    assert scores == [2.0, 1.0, 1.0]


def test_empty_input_makes_no_request():
    def handler(request: httpx.Request) -> httpx.Response:  # pragma: no cover
        raise AssertionError("no HTTP call should be made for an empty pair list")

    assert _client(handler).score_pairs([]) == []


def test_gateway_error_raises_so_callers_fail_open():
    """A 503 must propagate.

    KnowledgeStore._rerank and MemoryStore._rerank both catch Exception and keep
    the pre-rerank order. Swallowing the error here instead would hand them a
    list of zeros, which sorts into an arbitrary order rather than the original.
    """

    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(503, text="no rerank node is usable")

    with pytest.raises(httpx.HTTPStatusError):
        _client(handler).score_pairs([("q", "t")])


def test_partial_response_leaves_unscored_texts_at_zero():
    """A node that drops candidates must not shift the remaining scores."""

    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json=[{"index": 1, "score": 4.0}])

    assert _client(handler).score_pairs([("q", "a"), ("q", "b")]) == [0.0, 4.0]
