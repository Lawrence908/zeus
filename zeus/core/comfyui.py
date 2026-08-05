# zeus/core/comfyui.py — Pygmalion: ComfyUI image-generation client + failover
#
# Zeus has no image model of its own (Ollama runs LLMs/embeddings only). Image
# generation is a separate engine — ComfyUI — living on the same two GPUs as the
# Ollama fabric (homelab-docs/network.md §9):
#
#   PRIMARY   Apollo  RTX 5080 16GB  http://192.168.50.30:8188   (FLUX, fast, not always on)
#   FALLBACK  daedalus RTX 3080 10GB http://host.docker.internal:8188 (SDXL --lowvram, always on)
#
# Routing is done HERE, not in a Caddy load-balancer: ComfyUI's API is a
# multi-step, stateful exchange (POST /prompt -> poll /history/{id} -> GET /view)
# that a dumb LB can split across nodes on a mid-request failover. We health-check
# the primary (GET /system_stats) and pick the fallback ourselves, then keep the
# whole exchange on the chosen node.
#
# Graphs are built in Python rather than loaded from exported JSON so parameters
# stay type-safe and install-specific filenames (checkpoints, CLIP, VAE) are env
# overridable without editing a fragile placeholder-substituted template.
from __future__ import annotations

import asyncio
import logging
import os
import time
import uuid
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import httpx
from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel, Field

logger = logging.getLogger("zeus.comfyui")

# --- config (all env-overridable so ops can retarget without code edits) ---


def enabled() -> bool:
    return os.getenv("ZEUS_IMAGE_ENABLED", "0").strip().lower() in {"1", "true", "yes", "y"}


def _primary_url() -> str:
    return os.getenv("ZEUS_COMFYUI_PRIMARY_URL", "").strip().rstrip("/")


def _fallback_url() -> str:
    return os.getenv("ZEUS_COMFYUI_FALLBACK_URL", "").strip().rstrip("/")


def images_dir() -> Path:
    d = Path(os.getenv("ZEUS_IMAGES_DIR", "/app/zeus/data/images"))
    d.mkdir(parents=True, exist_ok=True)
    return d


# Model per node. FLUX on the 16GB primary, SDXL on the 10GB fallback. Set either
# to "sdxl" if a node lacks the FLUX weights (the graph would 400 otherwise).
def _primary_model() -> str:
    return os.getenv("ZEUS_COMFYUI_PRIMARY_MODEL", "flux").strip().lower()


def _fallback_model() -> str:
    return os.getenv("ZEUS_COMFYUI_FALLBACK_MODEL", "sdxl").strip().lower()


# Checkpoint / component filenames as they appear in each ComfyUI's models dir.
_SDXL_CKPT = lambda: os.getenv("ZEUS_COMFYUI_SDXL_CKPT", "sd_xl_base_1.0.safetensors")
_FLUX_UNET = lambda: os.getenv("ZEUS_COMFYUI_FLUX_UNET", "flux1-dev.safetensors")
_FLUX_CLIP_L = lambda: os.getenv("ZEUS_COMFYUI_FLUX_CLIP_L", "clip_l.safetensors")
_FLUX_T5 = lambda: os.getenv("ZEUS_COMFYUI_FLUX_T5", "t5xxl_fp8_e4m3fn.safetensors")
_FLUX_VAE = lambda: os.getenv("ZEUS_COMFYUI_FLUX_VAE", "ae.safetensors")
_FLUX_DTYPE = lambda: os.getenv("ZEUS_COMFYUI_FLUX_DTYPE", "fp8_e4m3fn")

_HEALTH_TIMEOUT = 3.0
_SUBMIT_TIMEOUT = 15.0
_POLL_INTERVAL = 1.0
_POLL_TIMEOUT = 180.0  # FLUX ~10-30s; lowvram SDXL on the 3080 is much slower


@dataclass
class GeneratedImage:
    filename: str  # basename on disk under images_dir()
    path: str  # absolute local path
    node: str  # "primary" | "fallback"
    model: str  # "flux" | "sdxl"
    seed: int
    width: int
    height: int


class ComfyUIError(RuntimeError):
    pass


# --- graph builders (ComfyUI "prompt"/API format: {node_id: {class_type, inputs}}) ---


def _sdxl_graph(prompt: str, negative: str, width: int, height: int, steps: int, seed: int) -> dict[str, Any]:
    return {
        "4": {"class_type": "CheckpointLoaderSimple", "inputs": {"ckpt_name": _SDXL_CKPT()}},
        "6": {"class_type": "CLIPTextEncode", "inputs": {"text": prompt, "clip": ["4", 1]}},
        "7": {"class_type": "CLIPTextEncode", "inputs": {"text": negative, "clip": ["4", 1]}},
        "5": {"class_type": "EmptyLatentImage", "inputs": {"width": width, "height": height, "batch_size": 1}},
        "3": {
            "class_type": "KSampler",
            "inputs": {
                "seed": seed,
                "steps": steps,
                "cfg": 7.0,
                "sampler_name": "euler",
                "scheduler": "normal",
                "denoise": 1.0,
                "model": ["4", 0],
                "positive": ["6", 0],
                "negative": ["7", 0],
                "latent_image": ["5", 0],
            },
        },
        "8": {"class_type": "VAEDecode", "inputs": {"samples": ["3", 0], "vae": ["4", 2]}},
        "9": {"class_type": "SaveImage", "inputs": {"images": ["8", 0], "filename_prefix": "zeus"}},
    }


def _flux_graph(prompt: str, negative: str, width: int, height: int, steps: int, seed: int) -> dict[str, Any]:
    # flux1-dev canonical API workflow. FLUX is guidance-distilled (cfg=1), so the
    # negative prompt is not wired — SDXL-style negatives have no effect here.
    guidance = float(os.getenv("ZEUS_COMFYUI_FLUX_GUIDANCE", "3.5"))
    return {
        "12": {"class_type": "UNETLoader", "inputs": {"unet_name": _FLUX_UNET(), "weight_dtype": _FLUX_DTYPE()}},
        "11": {
            "class_type": "DualCLIPLoader",
            "inputs": {"clip_name1": _FLUX_CLIP_L(), "clip_name2": _FLUX_T5(), "type": "flux"},
        },
        "10": {"class_type": "VAELoader", "inputs": {"vae_name": _FLUX_VAE()}},
        "6": {"class_type": "CLIPTextEncode", "inputs": {"text": prompt, "clip": ["11", 0]}},
        "26": {"class_type": "FluxGuidance", "inputs": {"conditioning": ["6", 0], "guidance": guidance}},
        "5": {"class_type": "EmptySD3LatentImage", "inputs": {"width": width, "height": height, "batch_size": 1}},
        "22": {"class_type": "BasicGuider", "inputs": {"model": ["12", 0], "conditioning": ["26", 0]}},
        "16": {"class_type": "KSamplerSelect", "inputs": {"sampler_name": "euler"}},
        "17": {
            "class_type": "BasicScheduler",
            "inputs": {"model": ["12", 0], "scheduler": "simple", "steps": steps, "denoise": 1.0},
        },
        "25": {"class_type": "RandomNoise", "inputs": {"noise_seed": seed}},
        "13": {
            "class_type": "SamplerCustomAdvanced",
            "inputs": {
                "noise": ["25", 0],
                "guider": ["22", 0],
                "sampler": ["16", 0],
                "sigmas": ["17", 0],
                "latent_image": ["5", 0],
            },
        },
        "8": {"class_type": "VAEDecode", "inputs": {"samples": ["13", 0], "vae": ["10", 0]}},
        "9": {"class_type": "SaveImage", "inputs": {"images": ["8", 0], "filename_prefix": "zeus"}},
    }


def _build_graph(model: str, prompt: str, negative: str, width: int, height: int, steps: int, seed: int) -> dict[str, Any]:
    if model == "flux":
        return _flux_graph(prompt, negative, width, height, steps, seed)
    return _sdxl_graph(prompt, negative, width, height, steps, seed)


# --- ComfyUI HTTP exchange on a single node ---


async def _healthy(client: httpx.AsyncClient, base: str) -> bool:
    if not base:
        return False
    try:
        r = await client.get(f"{base}/system_stats", timeout=_HEALTH_TIMEOUT)
        return r.status_code == 200
    except httpx.HTTPError:
        return False


async def _run_on_node(client: httpx.AsyncClient, base: str, graph: dict[str, Any]) -> bytes:
    client_id = uuid.uuid4().hex
    submit = await client.post(
        f"{base}/prompt", json={"prompt": graph, "client_id": client_id}, timeout=_SUBMIT_TIMEOUT
    )
    if submit.status_code >= 400:
        raise ComfyUIError(f"ComfyUI /prompt {submit.status_code}: {submit.text[:300]}")
    prompt_id = submit.json().get("prompt_id")
    if not prompt_id:
        raise ComfyUIError(f"ComfyUI /prompt returned no prompt_id: {submit.text[:200]}")

    deadline = time.monotonic() + _POLL_TIMEOUT
    outputs: dict[str, Any] | None = None
    while time.monotonic() < deadline:
        await asyncio.sleep(_POLL_INTERVAL)
        h = await client.get(f"{base}/history/{prompt_id}", timeout=_HEALTH_TIMEOUT)
        if h.status_code != 200:
            continue
        entry = h.json().get(prompt_id)
        if entry and entry.get("outputs"):
            status = (entry.get("status") or {}).get("status_str")
            if status == "error":
                raise ComfyUIError(f"ComfyUI reported an execution error for prompt {prompt_id}")
            outputs = entry["outputs"]
            break
    if outputs is None:
        raise ComfyUIError(f"ComfyUI timed out after {_POLL_TIMEOUT:.0f}s waiting for prompt {prompt_id}")

    for node_out in outputs.values():
        for img in node_out.get("images", []) or []:
            params = {
                "filename": img.get("filename", ""),
                "subfolder": img.get("subfolder", ""),
                "type": img.get("type", "output"),
            }
            view = await client.get(f"{base}/view", params=params, timeout=_SUBMIT_TIMEOUT)
            if view.status_code == 200 and view.content:
                return view.content
    raise ComfyUIError("ComfyUI produced no retrievable image in its outputs")


async def _select_node() -> tuple[str, str, str]:
    """Return (base_url, node_label, model) for the first healthy node."""
    primary, fallback = _primary_url(), _fallback_url()
    async with httpx.AsyncClient() as client:
        if await _healthy(client, primary):
            return primary, "primary", _primary_model()
        if await _healthy(client, fallback):
            logger.info("comfyui: primary unhealthy, using fallback")
            return fallback, "fallback", _fallback_model()
    raise ComfyUIError(
        "No ComfyUI node reachable. Checked "
        f"primary={primary or '(unset)'} and fallback={fallback or '(unset)'}."
    )


# --- public entry point ---


async def generate_image(
    *,
    prompt: str,
    negative_prompt: str = "",
    width: int = 1024,
    height: int = 1024,
    steps: int | None = None,
    seed: int | None = None,
) -> GeneratedImage:
    if not enabled():
        raise ComfyUIError("Image generation is disabled. Set ZEUS_IMAGE_ENABLED=1 and restart zeus-core.")
    prompt = (prompt or "").strip()
    if not prompt:
        raise ComfyUIError("A non-empty 'prompt' is required.")

    # Clamp to sane, multiple-of-8 dimensions (ComfyUI requires it) and bounds.
    width = max(256, min(1536, (int(width) // 8) * 8))
    height = max(256, min(1536, (int(height) // 8) * 8))
    if seed is None:
        seed = uuid.uuid4().int % (2**63)
    seed = int(seed)

    base, node, model = await _select_node()
    eff_steps = int(steps) if steps else (20 if model == "flux" else 25)
    eff_steps = max(1, min(60, eff_steps))
    graph = _build_graph(model, prompt, negative_prompt.strip(), width, height, eff_steps, seed)

    async with httpx.AsyncClient() as client:
        try:
            png = await _run_on_node(client, base, graph)
        except (httpx.HTTPError, ComfyUIError) as exc:
            # Mid-request failure on the primary: try the fallback once.
            fb = _fallback_url()
            if node == "primary" and fb and await _healthy(client, fb):
                logger.warning("comfyui: primary failed (%s); retrying on fallback", exc)
                node, model = "fallback", _fallback_model()
                graph = _build_graph(model, prompt, negative_prompt.strip(), width, height, eff_steps, seed)
                png = await _run_on_node(client, fb, graph)
            else:
                raise

    filename = f"zeus-{int(time.time())}-{seed % 100000}.png"
    out_path = images_dir() / filename
    out_path.write_bytes(png)
    logger.info("comfyui: wrote %s (node=%s model=%s %dx%d)", filename, node, model, width, height)
    return GeneratedImage(
        filename=filename,
        path=str(out_path),
        node=node,
        model=model,
        seed=seed,
        width=width,
        height=height,
    )


# --- HTTP surface (MCP clients call this via ZEUS_CORE_URL; the chat tool calls
#     generate_image() in-process instead) ---

router = APIRouter(tags=["images"])


class ImageRequest(BaseModel):
    prompt: str
    negative_prompt: str = ""
    width: int = 1024
    height: int = 1024
    steps: int | None = Field(default=None, ge=1, le=60)
    seed: int | None = None


@router.post("/images/generate")
async def images_generate(req: ImageRequest, request: Request) -> dict[str, Any]:
    if not enabled():
        raise HTTPException(status_code=503, detail="Image generation disabled (ZEUS_IMAGE_ENABLED=0).")
    try:
        img = await generate_image(
            prompt=req.prompt,
            negative_prompt=req.negative_prompt,
            width=req.width,
            height=req.height,
            steps=req.steps,
            seed=req.seed,
        )
    except ComfyUIError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc
    url = str(request.base_url).rstrip("/") + f"/images/{img.filename}"
    return {
        "url": url,
        "path": img.path,
        "node": img.node,
        "model": img.model,
        "seed": img.seed,
        "width": img.width,
        "height": img.height,
    }
