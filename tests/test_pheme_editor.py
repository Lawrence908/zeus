# tests/test_pheme_editor.py - Claude editor stage, morning audio, recurring-report handling.
#
# No network: the Claude CLI and Kokoro are never called. Covers the parts that
# decide what reaches the reader: index validation, link attachment, section
# ordering, child-env isolation, script chunking, MP3 encoding, rendering.
from __future__ import annotations

import pytest

from zeus.pheme import editor
from zeus.pheme.audio import encode_mp3, split_script
from zeus.pheme.delivery import format_digest_html
from zeus.pheme.models import (
    ClusterSummary,
    DigestStory,
    EditorOutput,
    EditorStory,
    EditorTweet,
    PhemeDigest,
)
from zeus.pheme.pipeline import _compose_editor_body, _is_recurring_report


def _cluster(key: str, urls: list[str], **kw) -> ClusterSummary:
    return ClusterSummary(key=key, name=key, item_ids=[f"canary:{key}"], urls=urls, **kw)


CANDS = [
    _cluster("ecb", ["https://www.reuters.com/a", "https://apnews.com/b", "https://reuters.com/c"]),
    _cluster("chips", ["https://www.ft.com/x"]),
    _cluster("quake", ["https://bbc.co.uk/q"], thread_status="development", thread_days=3),
]


def _story(index: int, section: str, headline: str = "H") -> EditorStory:
    return EditorStory(
        index=index, section=section, headline=headline, summary="S.", why_it_matters="W.", watch=""
    )


def test_apply_drops_bad_and_duplicate_indices_and_groups_sections():
    out = EditorOutput(
        stories=[
            _story(1, "Business & markets", "ECB holds"),
            _story(9, "World"),                  # out of range
            _story(3, "World", "Quake toll rises"),
            _story(1, "World"),                  # duplicate
            _story(2, "Business & markets", "Chip curbs"),
        ],
        public_lead="x" * 400,
        public_thread=[EditorTweet(index=1, text="ECB holds rates."), EditorTweet(index=99, text="no link")],
    )
    clusters, stories, lead, thread = editor.apply_editor_output(out, CANDS, max_stories=8)
    # Grouped by section in order of first appearance; numbering follows this order.
    assert [c.key for c in clusters] == ["ecb", "chips", "quake"]
    assert [s.cluster_key for s in stories] == ["ecb", "chips", "quake"]
    assert len(lead) <= 270
    # Links come from cluster data, never from the model.
    assert thread[0] == "ECB holds rates. https://www.reuters.com/a"
    assert thread[1] == "no link"


def test_apply_rejects_empty_choice_and_unknown_section():
    with pytest.raises(editor.EditorFailed):
        editor.apply_editor_output(EditorOutput(stories=[_story(7, "World")]), CANDS, max_stories=8)
    _, stories, _, _ = editor.apply_editor_output(
        EditorOutput(stories=[_story(2, "Sports")]), CANDS, max_stories=8
    )
    assert stories[0].section == "World"


def test_distinct_links_dedupes_outlets():
    assert editor.distinct_links(CANDS[0]) == [
        ("reuters.com", "https://www.reuters.com/a"),
        ("apnews.com", "https://apnews.com/b"),
    ]


def test_child_env_strips_api_key_and_isolates_config(monkeypatch, tmp_path):
    monkeypatch.setenv("ANTHROPIC_API_KEY", "sk-should-never-pass")
    monkeypatch.setenv("CLAUDE_CODE_OAUTH_TOKEN", "oat-token")
    monkeypatch.delenv("PHEME_CLAUDE_USE_HOST_LOGIN", raising=False)
    env = editor._child_env(str(tmp_path))
    assert "ANTHROPIC_API_KEY" not in env
    assert env["CLAUDE_CODE_OAUTH_TOKEN"] == "oat-token"
    assert env["HOME"] == env["CLAUDE_CONFIG_DIR"] == str(tmp_path)


def test_child_env_requires_token(monkeypatch, tmp_path):
    monkeypatch.delenv("CLAUDE_CODE_OAUTH_TOKEN", raising=False)
    monkeypatch.delenv("PHEME_CLAUDE_USE_HOST_LOGIN", raising=False)
    with pytest.raises(editor.EditorFailed):
        editor._child_env(str(tmp_path))


def test_prompt_marks_static_threads_and_lists_outlets():
    c = _cluster("quake", ["https://bbc.co.uk/q"], thread_status="development", thread_days=4,
                 thread_static=True)
    text = editor.build_user_prompt(
        trigger="daily", date_label="Friday, October 16, 2026", candidates=[c],
        excerpts={"quake": [("bbc.co.uk", "Quake", "Body text")]}, background=["Scrutiny: x"],
        correlations=[], facts=["Works on construction ERP"], liked=[], disliked=[],
    )
    assert "[1] quake" in text and "first seen 4 days ago" in text
    assert "nothing substantive new" in text
    assert "Background reports" in text and "bbc.co.uk" in text


def test_recurring_report_detection():
    assert _is_recurring_report(ClusterSummary(key="k", item_ids=["capitolscope:window:2026-10-16:scrutiny"]))
    assert not _is_recurring_report(
        ClusterSummary(key="k", item_ids=["capitolscope:window:x", "canary:abc"])
    )
    assert not _is_recurring_report(ClusterSummary(key="k", item_ids=["capitolscope:trade:1"]))


def test_split_script_paragraphs_and_long_sentences():
    long_para = " ".join(["This is a sentence of moderate length."] * 40)
    chunks = split_script(f"Good morning.\n\n{long_para}\n\n  \n\nThat's it.", max_chars=200)
    assert chunks[0] == "Good morning." and chunks[-1] == "That's it."
    assert all(len(c) <= 200 for c in chunks)
    assert len(chunks) > 3


def test_encode_mp3_produces_frames():
    pcm = b"\x00\x00" * 24000  # one second of silence at 24 kHz mono
    mp3 = encode_mp3(pcm, 24000)
    assert len(mp3) > 1000
    assert mp3[:3] == b"ID3" or mp3[0] == 0xFF


def _edited_digest() -> PhemeDigest:
    stories = [
        DigestStory(cluster_key="ecb", section="Business & markets", headline="ECB <holds>",
                    summary="Rates unchanged.", why_it_matters="Cut odds rise.", watch="Nov CPI."),
        DigestStory(cluster_key="quake", section="World", headline="Quake toll rises",
                    summary="Toll at 40.", why_it_matters="Aid stretched."),
    ]
    return PhemeDigest(
        id="d1", trigger="daily", generated_at="2026-10-16T13:30:00+00:00",
        lead="Rates and rubble.", insights=["Both test capacity."],
        editor_connections=["Members sold banks ahead of the ECB call."],
        clusters=[CANDS[0], CANDS[2]], stories=stories, editor="claude-opus-5-5",
    )


def test_editor_html_rendering():
    html = format_digest_html(_edited_digest())
    assert "<b>BUSINESS &amp; MARKETS</b>" in html
    assert "ECB &lt;holds&gt;" in html                       # escaped
    assert "day 3" not in html                                 # loose thread days not shown
    assert html.count('href="https://www.reuters.com/a"') == 1
    assert "apnews.com</a>" in html
    assert "The bigger picture" in html and "Congress x news" in html


def test_editor_plain_body():
    d = _edited_digest()
    body = _compose_editor_body(d.lead, d.stories, d.clusters, d.insights, d.editor_connections)
    assert body.startswith("Rates and rubble.")
    assert "1. ECB <holds>" in body and "2. Quake toll rises" in body
    assert "Source: https://www.reuters.com/a (also apnews.com)" in body
