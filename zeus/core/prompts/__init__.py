# zeus/core/prompts/__init__.py — System prompt templates + loader
"""
System prompt loader with override/template layering.

Lookup order for a given `<name>.md`:
    1. `$ZEUS_PROMPT_OVERRIDE_DIR/<name>.md` — per-deployer personalized prompts
       (default: `zeus/prompts/overrides/<name>.md`, gitignored).
    2. `zeus/prompts/templates/<name>.md` — generic templates checked into the repo.

Templates use `{{PLACEHOLDER}}` markers (double braces) so they don't collide
with markdown or code blocks inside the template body. In addition to variables
passed by callers, the loader auto-injects:
    - `USER_NAME`          from `$ZEUS_USER_NAME` (default: "the user")
    - `USER_NAME_CAP`      capitalised form of `USER_NAME`
    - `USER_POSSESSIVE`    from `$ZEUS_USER_POSSESSIVE` (default: "their")
    - `USER_POSSESSIVE_CAP` capitalised form of `USER_POSSESSIVE`

Reload behavior:
    - Set ZEUS_PROMPT_RELOAD=1 to re-read templates from disk on every call
      (useful when tweaking prompts against a running zeus-core).
    - Default: cached once per process, mirrors production behavior.
"""
from __future__ import annotations

import os
from pathlib import Path

_PACKAGE_ROOT = Path(__file__).resolve().parents[2]  # .../zeus/ (the package dir)
_DEFAULT_OVERRIDE_DIR = _PACKAGE_ROOT / "prompts" / "overrides"
_TEMPLATE_DIR = _PACKAGE_ROOT / "prompts" / "templates"
_cache: dict[str, str] = {}


def _resolve_path(name: str) -> Path:
    override_dir = Path(os.getenv("ZEUS_PROMPT_OVERRIDE_DIR", str(_DEFAULT_OVERRIDE_DIR)))
    override = override_dir / f"{name}.md"
    if override.is_file():
        return override
    return _TEMPLATE_DIR / f"{name}.md"


def _load_raw(name: str) -> str:
    if not os.getenv("ZEUS_PROMPT_RELOAD") and name in _cache:
        return _cache[name]
    text = _resolve_path(name).read_text(encoding="utf-8")
    _cache[name] = text
    return text


def _user_identity() -> dict[str, str]:
    name = os.getenv("ZEUS_USER_NAME", "the user").strip() or "the user"
    possessive = os.getenv("ZEUS_USER_POSSESSIVE", "their").strip() or "their"
    return {
        "user_name": name,
        "user_name_cap": name[:1].upper() + name[1:] if name else name,
        "user_possessive": possessive,
        "user_possessive_cap": possessive[:1].upper() + possessive[1:] if possessive else possessive,
    }


def render(name: str, **variables: str) -> str:
    """Load template `<name>.md` and replace `{{KEY}}` markers with variables.

    Keys in the template are uppercase; pass lowercase kwargs — they will be
    upper-cased automatically so call sites stay Pythonic. User-identity vars
    (user_name, user_possessive, plus _cap variants) are auto-injected from
    env unless the caller overrides them explicitly.
    """
    merged = {**_user_identity(), **variables}
    template = _load_raw(name)
    for key, value in merged.items():
        template = template.replace("{{" + key.upper() + "}}", value)
    return template
