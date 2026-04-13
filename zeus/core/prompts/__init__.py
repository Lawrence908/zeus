# zeus/core/prompts/__init__.py — System prompt templates + loader
"""
Edit the .md files in this folder to iterate on Zeus's system prompts without
touching Python code. Templates use `{{PLACEHOLDER}}` markers (double braces) so
they don't collide with markdown or code blocks inside the template body.

Reload behavior:
    - Set ZEUS_PROMPT_RELOAD=1 to re-read templates from disk on every call
      (useful when tweaking prompts against a running zeus-core).
    - Default: cached once per process, mirrors production behavior.
"""
from __future__ import annotations

import os
from pathlib import Path

_PROMPT_DIR = Path(__file__).resolve().parent
_cache: dict[str, str] = {}


def _load_raw(name: str) -> str:
    if not os.getenv("ZEUS_PROMPT_RELOAD") and name in _cache:
        return _cache[name]
    path = _PROMPT_DIR / f"{name}.md"
    text = path.read_text(encoding="utf-8")
    _cache[name] = text
    return text


def render(name: str, **variables: str) -> str:
    """Load template `<name>.md` and replace `{{KEY}}` markers with variables.

    Keys in the template are uppercase; pass lowercase kwargs — they will be
    upper-cased automatically so call sites stay Pythonic.
    """
    template = _load_raw(name)
    for key, value in variables.items():
        template = template.replace("{{" + key.upper() + "}}", value)
    return template
