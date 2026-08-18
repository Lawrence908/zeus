# tests/test_comfyui.py — Pygmalion ComfyUI client: graph shape + failover/poll
#
# No GPU is touched: httpx.MockTransport stands in for ComfyUI so the stateful
# POST /prompt -> poll /history -> GET /view exchange, the slow-poll tolerance,
# and the primary->fallback failover can all be exercised deterministically.
# Async paths run via asyncio.run(), matching the repo's test convention.
from __future__ import annotations

import asyncio

import httpx
import pytest

from zeus.core import comfyui


# --- graph builders -------------------------------------------------------


def test_flux_graph_wiring():
    g = comfyui._flux_graph("a teapot", "ignored-negative", 768, 512, 20, 42)
    classes = {n["class_type"] for n in g.values()}
    assert {"UNETLoader", "DualCLIPLoader", "VAELoader", "FluxGuidance", "SamplerCustomAdvanced"} <= classes
    # FLUX is guidance-distilled: no SDXL-style negative conditioning node exists.
    assert sum(1 for n in g.values() if n["class_type"] == "CLIPTextEncode") == 1
    assert g["5"]["inputs"] == {"width": 768, "height": 512, "batch_size": 1}
    assert g["25"]["inputs"]["noise_seed"] == 42
    assert g["17"]["inputs"]["steps"] == 20


def test_sdxl_graph_wires_negative():
    g = comfyui._sdxl_graph("a teapot", "blurry, low quality", 1024, 1024, 25, 7)
    classes = [n["class_type"] for n in g.values()]
    assert "CheckpointLoaderSimple" in classes
    # Two CLIPTextEncode nodes: positive (6) and negative (7), the latter fed to KSampler.
    assert classes.count("CLIPTextEncode") == 2
    assert g["7"]["inputs"]["text"] == "blurry, low quality"
    assert g["3"]["inputs"]["negative"] == ["7", 0]
    assert g["3"]["inputs"]["seed"] == 7


def test_build_graph_dispatches_on_model():
    flux = comfyui._build_graph("flux", "p", "", 512, 512, 10, 1)
    sdxl = comfyui._build_graph("sdxl", "p", "", 512, 512, 10, 1)
    assert any(n["class_type"] == "UNETLoader" for n in flux.values())
    assert any(n["class_type"] == "CheckpointLoaderSimple" for n in sdxl.values())


# --- MockTransport helpers ------------------------------------------------

_DONE_HISTORY = {
    "abc": {
        "status": {"status_str": "success"},
        "outputs": {"9": {"images": [{"filename": "zeus_0001.png", "subfolder": "", "type": "output"}]}},
    }
}


def _client(handler) -> httpx.AsyncClient:
    return httpx.AsyncClient(transport=httpx.MockTransport(handler))


# --- _run_on_node ---------------------------------------------------------


def test_run_on_node_happy_path(monkeypatch):
    monkeypatch.setattr(comfyui, "_POLL_INTERVAL", 0.0)

    def handler(request: httpx.Request) -> httpx.Response:
        if request.url.path == "/prompt":
            return httpx.Response(200, json={"prompt_id": "abc"})
        if request.url.path == "/history/abc":
            return httpx.Response(200, json=_DONE_HISTORY)
        if request.url.path == "/view":
            return httpx.Response(200, content=b"PNGDATA")
        return httpx.Response(404)

    async def run():
        async with _client(handler) as client:
            return await comfyui._run_on_node(client, "http://node:8188", {"x": 1})

    assert asyncio.run(run()) == b"PNGDATA"


def test_run_on_node_tolerates_slow_poll(monkeypatch):
    """A /history poll that ReadTimeouts must NOT abort the run — the job is
    still cooking on a busy GPU. This is the exact regression that silently
    dropped FLUX jobs to the SDXL fallback."""
    monkeypatch.setattr(comfyui, "_POLL_INTERVAL", 0.0)
    calls = {"history": 0}

    def handler(request: httpx.Request) -> httpx.Response:
        if request.url.path == "/prompt":
            return httpx.Response(200, json={"prompt_id": "abc"})
        if request.url.path == "/history/abc":
            calls["history"] += 1
            if calls["history"] == 1:
                raise httpx.ReadTimeout("stall", request=request)
            return httpx.Response(200, json=_DONE_HISTORY)
        if request.url.path == "/view":
            return httpx.Response(200, content=b"PNGDATA")
        return httpx.Response(404)

    async def run():
        async with _client(handler) as client:
            return await comfyui._run_on_node(client, "http://node:8188", {"x": 1})

    assert asyncio.run(run()) == b"PNGDATA"
    assert calls["history"] == 2  # first timed out and was retried, not raised


def test_run_on_node_raises_on_execution_error(monkeypatch):
    monkeypatch.setattr(comfyui, "_POLL_INTERVAL", 0.0)

    def handler(request: httpx.Request) -> httpx.Response:
        if request.url.path == "/prompt":
            return httpx.Response(200, json={"prompt_id": "abc"})
        if request.url.path == "/history/abc":
            return httpx.Response(200, json={"abc": {"status": {"status_str": "error"}, "outputs": {"9": {}}}})
        return httpx.Response(404)

    async def run():
        async with _client(handler) as client:
            await comfyui._run_on_node(client, "http://node:8188", {"x": 1})

    with pytest.raises(comfyui.ComfyUIError):
        asyncio.run(run())


# --- generate_image failover ---------------------------------------------


def test_generate_image_fails_over_to_fallback(monkeypatch, tmp_path):
    monkeypatch.setenv("ZEUS_IMAGE_ENABLED", "1")
    monkeypatch.setenv("ZEUS_COMFYUI_PRIMARY_URL", "http://primary:8188")
    monkeypatch.setenv("ZEUS_COMFYUI_FALLBACK_URL", "http://fallback:8188")
    monkeypatch.setattr(comfyui, "images_dir", lambda: tmp_path)

    async def fake_healthy(client, base):
        return True

    async def fake_run(client, base, graph):
        if "primary" in base:
            raise httpx.ReadTimeout("stall")  # str() == '' — the silent case
        return b"FALLBACKPNG"

    monkeypatch.setattr(comfyui, "_healthy", fake_healthy)
    monkeypatch.setattr(comfyui, "_run_on_node", fake_run)

    img = asyncio.run(comfyui.generate_image(prompt="a teapot", width=512, height=512, seed=3))
    assert img.node == "fallback"
    assert img.model == "sdxl"
    assert (tmp_path / img.filename).read_bytes() == b"FALLBACKPNG"


def test_generate_image_uses_primary_when_healthy(monkeypatch, tmp_path):
    monkeypatch.setenv("ZEUS_IMAGE_ENABLED", "1")
    monkeypatch.setenv("ZEUS_COMFYUI_PRIMARY_URL", "http://primary:8188")
    monkeypatch.setenv("ZEUS_COMFYUI_FALLBACK_URL", "http://fallback:8188")
    monkeypatch.setattr(comfyui, "images_dir", lambda: tmp_path)

    async def fake_healthy(client, base):
        return "primary" in base

    async def fake_run(client, base, graph):
        assert "primary" in base
        return b"FLUXPNG"

    monkeypatch.setattr(comfyui, "_healthy", fake_healthy)
    monkeypatch.setattr(comfyui, "_run_on_node", fake_run)

    img = asyncio.run(comfyui.generate_image(prompt="a teapot", width=512, height=512, seed=3))
    assert img.node == "primary"
    assert img.model == "flux"


def test_generate_image_disabled_raises(monkeypatch):
    monkeypatch.setenv("ZEUS_IMAGE_ENABLED", "0")
    with pytest.raises(comfyui.ComfyUIError):
        asyncio.run(comfyui.generate_image(prompt="a teapot"))
