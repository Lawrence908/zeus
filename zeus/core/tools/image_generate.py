# zeus/core/tools/image_generate.py — Pygmalion: chat-path image generation tool
#
# Wraps zeus.core.comfyui.generate_image() so the chat LLM, Kairos (via the
# allowlist), and — mirrored in zeus/mcp/tools.py — MCP clients can request an
# image. Runs ComfyUI on Apollo's RTX 5080 (FLUX) when up, else the always-on
# daedalus RTX 3080 (SDXL). Returns a viewable /images/<file>.png URL; the built
# React SPA and MCP clients resolve it same-origin against zeus-core.
#
# Gated by ZEUS_IMAGE_ENABLED (register_if_configured is a no-op when unset),
# mirroring web_search's BRAVE_API_KEY gate.
from __future__ import annotations

import logging
import os
from typing import Any

from zeus.core.tools import registry
from zeus.core.tools.base import ToolResult, ToolSpec

logger = logging.getLogger("zeus.tools.image_generate")

_SCHEMA: dict[str, Any] = {
    "type": "object",
    "properties": {
        "prompt": {
            "type": "string",
            "description": "Full description of the image to generate. Be specific and vivid; sent to the image model verbatim.",
        },
        "negative_prompt": {
            "type": "string",
            "description": "Things to avoid in the image (SDXL only; ignored by FLUX). Optional.",
        },
        "width": {"type": "integer", "minimum": 256, "maximum": 1536, "description": "Image width in px (default 1024, rounded to a multiple of 8)."},
        "height": {"type": "integer", "minimum": 256, "maximum": 1536, "description": "Image height in px (default 1024, rounded to a multiple of 8)."},
        "seed": {"type": "integer", "description": "Optional seed for reproducibility; omit for a random image."},
    },
    "required": ["prompt"],
}

_SPEC = ToolSpec(
    name="image_generate",
    description=(
        "Generate an image from a text description using the local ComfyUI "
        "GPUs. Call this whenever the user asks you to draw, create, render, "
        "design, or generate a picture, image, logo, artwork, or illustration. "
        "Returns a URL to the finished PNG — include that URL in your reply so "
        "the user can open it. Generation takes several seconds to a minute; "
        "call the tool once and wait. Do NOT describe an image you did not "
        "actually generate through this tool."
    ),
    parameters=_SCHEMA,
    aegis_policy="tool_arguments",
    timeout_seconds=200.0,
    cacheable=False,
)


async def _handler(args: dict[str, Any]) -> ToolResult:
    from zeus.core.comfyui import ComfyUIError, generate_image

    prompt = str(args.get("prompt") or "").strip()
    if not prompt:
        return ToolResult(call_id="", name=_SPEC.name, content="image_generate requires a non-empty 'prompt'.", is_error=True)

    try:
        img = await generate_image(
            prompt=prompt,
            negative_prompt=str(args.get("negative_prompt") or ""),
            width=int(args.get("width") or 1024),
            height=int(args.get("height") or 1024),
            seed=args.get("seed"),
        )
    except ComfyUIError as exc:
        return ToolResult(call_id="", name=_SPEC.name, content=f"image_generate failed: {exc}", is_error=True)
    except Exception as exc:  # noqa: BLE001 — surface any unexpected failure to the model, not a 500
        logger.exception("image_generate unexpected error")
        return ToolResult(call_id="", name=_SPEC.name, content=f"image_generate error: {exc}", is_error=True)

    # Root-relative URL resolves same-origin in the browser SPA.
    url = f"/images/{img.filename}"
    body = (
        f"Generated image: {url}\n"
        f"({img.width}x{img.height}, model={img.model}, node={img.node}, seed={img.seed}). "
        f"Share the URL with the user."
    )
    return ToolResult(call_id="", name=_SPEC.name, content=body)


def register_if_configured() -> bool:
    """Register image_generate iff ZEUS_IMAGE_ENABLED is truthy. Returns True on register."""
    if os.getenv("ZEUS_IMAGE_ENABLED", "0").strip().lower() not in {"1", "true", "yes", "y"}:
        logger.info("image_generate not registered: ZEUS_IMAGE_ENABLED is off")
        return False
    registry.register(_SPEC, _handler)
    logger.info("image_generate registered")
    return True
