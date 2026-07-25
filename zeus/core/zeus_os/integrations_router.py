# zeus/core/zeus_os/integrations_router.py — Config + thin proxies for
# external integrations (Home Assistant, Linear). Lives under /zeus-os/ so
# the SPA's same-origin fetches just work without a separate base URL.
from __future__ import annotations

import asyncio
import logging
import os
import re
from typing import Any
from urllib.parse import urlparse

import httpx
import websockets
from fastapi import APIRouter, Body, HTTPException, Request, WebSocket, WebSocketDisconnect
from fastapi.responses import Response

logger = logging.getLogger("zeus.zeus_os.integrations")

router = APIRouter()


# ─── Home Assistant ─────────────────────────────────────────────────────────


def _ha_origin() -> str:
    return (
        os.getenv("ZEUS_OS_HA_URL")
        or os.getenv("HASS_URL")
        or os.getenv("HOME_ASSISTANT_URL")
        or "http://daedalus.sunfish-prometheus.ts.net:8154"
    ).rstrip("/")


def _ha_cf_credentials() -> tuple[str | None, str | None]:
    """Return (CF-Access-Client-Id, CF-Access-Client-Secret) for the proxy.

    Accepts the Zeus-namespaced names first, then the Cloudflare-conventional
    names so it picks up creds from `cloudflared` setups without extra config.
    """
    cid = os.getenv("ZEUS_OS_HA_CF_CLIENT_ID") or os.getenv("CF_ACCESS_CLIENT_ID")
    secret = os.getenv("ZEUS_OS_HA_CF_CLIENT_SECRET") or os.getenv("CF_ACCESS_CLIENT_SECRET")
    return cid, secret


@router.get("/ha/config")
def ha_config() -> dict[str, Any]:
    """Tell the SPA whether to load HA directly or through the reverse proxy.

    Iframes can't add custom headers, so when a service token is configured
    we route the iframe through /zeus-os/ha/proxy/ and inject the CF Access
    headers server-side. Without a token the SPA falls back to the raw URL
    and the user gets the existing "open ↗" affordance for X-Frame-Options
    blockages.
    """
    cid, _ = _ha_cf_credentials()
    if cid:
        return {
            "url": "/zeus-os/ha/proxy/",
            "mode": "proxy",
            "upstream": _ha_origin(),
        }
    return {"url": _ha_origin(), "mode": "direct", "upstream": _ha_origin()}


# Hop-by-hop headers that must not be forwarded between the upstream and the
# client (RFC 7230 §6.1). We strip them in both directions.
_HOP_BY_HOP = frozenset(
    {
        "connection",
        "keep-alive",
        "proxy-authenticate",
        "proxy-authorization",
        "te",
        "trailers",
        "transfer-encoding",
        "upgrade",
    }
)


def _filter_request_headers(headers: dict[str, str]) -> dict[str, str]:
    out: dict[str, str] = {}
    for k, v in headers.items():
        lk = k.lower()
        if lk in _HOP_BY_HOP:
            continue
        if lk == "host":
            continue
        out[k] = v
    return out


def _filter_response_headers(headers: httpx.Headers) -> dict[str, str]:
    out: dict[str, str] = {}
    for k, v in headers.items():
        lk = k.lower()
        if lk in _HOP_BY_HOP:
            continue
        # Strip framing-blockers so the iframe can render. Caddy already does
        # this for X-Frame-Options on its public route; we belt-and-brace it
        # here for the in-cluster path too.
        if lk in ("x-frame-options", "content-security-policy", "content-encoding", "content-length"):
            continue
        out[k] = v
    return out


@router.api_route(
    "/ha/proxy/{path:path}",
    methods=["GET", "POST", "PUT", "PATCH", "DELETE", "HEAD", "OPTIONS"],
)
async def ha_http_proxy(path: str, request: Request) -> Response:
    """HTTP reverse proxy to Home Assistant with CF Access headers injected.

    Path is appended to ZEUS_OS_HA_URL; query string is preserved. Cookies,
    method, body all forwarded. Response headers are filtered to remove
    hop-by-hop and frame-blocker headers.
    """
    cid, secret = _ha_cf_credentials()
    if not cid or not secret:
        raise HTTPException(
            status_code=503,
            detail=(
                "Service-token mode requires ZEUS_OS_HA_CF_CLIENT_ID and "
                "ZEUS_OS_HA_CF_CLIENT_SECRET. Set them in zeus/.env and "
                "restart zeus-core."
            ),
        )

    target = f"{_ha_origin()}/{path}"
    if request.url.query:
        target = f"{target}?{request.url.query}"

    headers = _filter_request_headers({k: v for k, v in request.headers.items()})
    headers["cf-access-client-id"] = cid
    headers["cf-access-client-secret"] = secret
    # Force uncompressed upstream responses so we don't have to worry about
    # brotli / zstd support in httpx. The browser still gets gzip from FastAPI
    # if it asked for it (uvicorn doesn't compress by default, fine).
    headers["accept-encoding"] = "identity"

    body = await request.body()
    async with httpx.AsyncClient(timeout=httpx.Timeout(60.0), follow_redirects=False) as client:
        try:
            upstream = await client.request(
                request.method,
                target,
                headers=headers,
                content=body,
            )
        except httpx.HTTPError as exc:
            raise HTTPException(status_code=502, detail=f"HA unreachable: {exc}") from exc

    out_headers = _filter_response_headers(upstream.headers)
    body = _rewrite_ha_body(upstream.content, upstream.headers.get("content-type", ""))
    return Response(
        content=body,
        status_code=upstream.status_code,
        headers=out_headers,
        media_type=upstream.headers.get("content-type"),
    )


# HA's frontend uses root-absolute URLs everywhere — `<link href="/foo">`,
# `import("/frontend_latest/X.js")`, etc. Iframed under /zeus-os/ha/proxy/
# those resolve against the parent origin (Zeus) and 404 / hit the SPA
# fallback. Rewrite well-known prefixes into proxy-relative paths.
#
# HA doesn't support sub-path mounting, so we have to do this client-side
# (HTML/JS body munging) rather than via an HA setting.
_PROXY_PREFIX = "/zeus-os/ha/proxy"

# Prefixes the HA frontend asks for. Keep this list close to what HA
# actually emits — narrower than `/.+` so we don't accidentally clobber
# non-asset values inside the body.
_HA_PATH_PREFIXES = (
    "static",
    "frontend_latest",
    "frontend_es5",
    "frontend_es6",
    "hacsfiles",
    "polyfills",
    "api",
    "auth",
    "manifest.json",
    "service_worker.js",
    "favicon.ico",
    "robots.txt",
    "lovelace",
)


def _rewrite_ha_body(content: bytes, content_type: str) -> bytes:
    ct = (content_type or "").lower()
    if not (ct.startswith("text/html") or ct.startswith("text/javascript") or ct.startswith("application/javascript")):
        return content
    try:
        text = content.decode("utf-8")
    except UnicodeDecodeError:
        return content
    prefixes = "|".join(re.escape(p) for p in _HA_PATH_PREFIXES)
    # Match a leading slash + HA prefix, but only when the slash is at the
    # START of a URL string (preceded by `=`, `(`, `"`, `'`, `,`, whitespace,
    # or line start). Otherwise we'd rewrite `/favicon.ico` inside an
    # already-rewritten `/zeus-os/ha/proxy/static/icons/favicon.ico` because
    # `favicon.ico` is itself a known prefix.
    pattern = re.compile(
        rf'''(?P<boundary>[=("'\s,;|]|^)/(?!zeus-os/)(?P<path>{prefixes})(?=[/"\'?#\s)\]])''',
        re.MULTILINE,
    )
    rewritten, _count = pattern.subn(
        lambda m: f"{m.group('boundary')}{_PROXY_PREFIX}/{m.group('path')}",
        text,
    )
    return rewritten.encode("utf-8")


@router.websocket("/ha/proxy/api/websocket")
async def ha_ws_proxy(ws: WebSocket) -> None:
    """WebSocket bridge: ws://us/zeus-os/ha/proxy/api/websocket ⇄ wss://ha/api/websocket.

    HA's frontend uses a single WS for live state updates; without this the
    dashboard renders but nothing animates. Service-token credentials go in
    the upstream Sec-WebSocket-Protocol / connection headers exactly like
    a normal HTTP request.
    """
    cid, secret = _ha_cf_credentials()
    if not cid or not secret:
        await ws.close(code=4401, reason="no service token configured")
        return

    parsed = urlparse(_ha_origin())
    scheme = "wss" if parsed.scheme == "https" else "ws"
    upstream_url = f"{scheme}://{parsed.netloc}/api/websocket"

    extra_headers = [
        ("CF-Access-Client-Id", cid),
        ("CF-Access-Client-Secret", secret),
    ]

    await ws.accept()
    try:
        async with websockets.connect(
            upstream_url,
            extra_headers=extra_headers,
            open_timeout=10,
            ping_interval=20,
        ) as upstream:
            async def client_to_upstream() -> None:
                try:
                    while True:
                        msg = await ws.receive_text()
                        await upstream.send(msg)
                except WebSocketDisconnect:
                    pass

            async def upstream_to_client() -> None:
                try:
                    async for msg in upstream:
                        if isinstance(msg, bytes):
                            await ws.send_bytes(msg)
                        else:
                            await ws.send_text(msg)
                except websockets.exceptions.ConnectionClosed:
                    pass

            await asyncio.gather(client_to_upstream(), upstream_to_client(), return_exceptions=True)
    except Exception as exc:
        logger.warning("HA WS bridge failed: %s", exc)
        try:
            await ws.close(code=1011, reason=f"upstream: {exc}")
        except RuntimeError:
            pass


# ─── Linear ─────────────────────────────────────────────────────────────────


_LINEAR_ENDPOINT = "https://api.linear.app/graphql"


def _linear_key() -> str | None:
    return os.getenv("LINEAR_API_KEY") or os.getenv("ZEUS_LINEAR_API_KEY") or None


@router.get("/linear/status")
def linear_status() -> dict[str, Any]:
    """Quick health-and-config probe so the SPA can show a sensible empty state."""
    key = _linear_key()
    return {
        "configured": bool(key),
        "team_key": os.getenv("ZEUS_LINEAR_TEAM_KEY", "LAB"),
    }


@router.post("/linear/query")
async def linear_query(body: dict[str, Any] = Body(...)) -> dict[str, Any]:
    """Proxy GraphQL requests to Linear, attaching the server-side API key.

    The frontend sends `{query, variables?}` and we forward verbatim. Keeping
    the key server-side avoids shipping it to the browser.
    """
    key = _linear_key()
    if not key:
        raise HTTPException(
            status_code=503,
            detail="LINEAR_API_KEY is not set in zeus/.env. Add it and restart zeus-core.",
        )
    q = body.get("query")
    if not isinstance(q, str) or not q.strip():
        raise HTTPException(status_code=400, detail="query is required")
    variables = body.get("variables") or {}
    payload = {"query": q, "variables": variables}
    async with httpx.AsyncClient(timeout=20.0) as client:
        try:
            r = await client.post(
                _LINEAR_ENDPOINT,
                json=payload,
                headers={"Authorization": key, "Content-Type": "application/json"},
            )
        except httpx.HTTPError as exc:
            raise HTTPException(status_code=502, detail=f"linear unreachable: {exc}") from exc
    if r.status_code >= 400:
        raise HTTPException(status_code=r.status_code, detail=r.text[:500])
    return r.json()
