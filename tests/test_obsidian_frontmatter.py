# tests/test_obsidian_frontmatter.py — Obsidian YAML frontmatter parsing
from zeus.ingest.sources.obsidian import _parse_frontmatter


def test_parse_list_tags_and_nested():
    text = """---
tags: [python, homelab]
project:
  name: Zeus
  phase: 2
---

Body line one.
"""
    meta, body = _parse_frontmatter(text)
    assert meta["tags"] == ["python", "homelab"]
    assert meta["project"] == {"name": "Zeus", "phase": 2}
    assert body.startswith("Body line one.")


def test_no_frontmatter():
    meta, body = _parse_frontmatter("# Just a note\n\nHello")
    assert meta == {}
    assert "# Just a note" in body


def test_invalid_yaml_returns_empty_meta():
    text = """---
tags: [unclosed
---

rest
"""
    meta, body = _parse_frontmatter(text)
    assert meta == {}
    assert "rest" in body
