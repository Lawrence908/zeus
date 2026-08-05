# zeus/core/mesh.py — Outbound mesh choke point (mesh-outbound-spec.md)
#
# POST /mesh/notify   {text, channel?, destination?, priority?, dedupe_key?, source?}
#
# The ONLY code allowed to originate unsolicited / commanded LoRa traffic. All
# outbound policy lives here so the meshtastic-sender stays a dumb radio driver:
# master gate → Aegis → quiet hours → rate limit → dedupe → chunk → send → audit.
# Everything is fail-closed and default-off (ZEUS_MESH_OUTBOUND_ENABLED).
#
# Anti-spam is structural: dedupe + rate-limit + quiet-hours live HERE, downstream
# of any caller, so even a runaway Kairos plan can only *ask* to send — this
# endpoint decides. See mesh-outbound-spec.md for the design rationale.
from __future__ import annotations

import hashlib
import ipaddress
import logging
import os
import socket
import sqlite3
import threading
import time
from datetime import datetime, time as dtime
from pathlib import Path
from typing import Any

import httpx
from fastapi import APIRouter
from pydantic import BaseModel, Field

from zeus.safety.policy_engine import aegis_enabled, evaluate_text

logger = logging.getLogger("zeus.mesh")

router = APIRouter(tags=["mesh"])

_AEGIS_POLICY = "meshtastic"
_CHUNK_BYTES = 200  # leave headroom under the sender's 230-byte text cap
_VALID_PRIORITIES = ("low", "normal", "critical")


# ------------------------------------------------------------------
# Config (read at call time so runtime toggles apply without restart)
# ------------------------------------------------------------------


def _truthy(name: str, default: str = "false") -> bool:
    return os.getenv(name, default).strip().lower() in ("1", "true", "yes", "y", "on")


def _outbound_enabled() -> bool:
    return _truthy("ZEUS_MESH_OUTBOUND_ENABLED")


def _sender_url() -> str:
    return os.getenv("ZEUS_MESH_SENDER_URL", "http://meshtastic-sender:8000").rstrip("/")


def _core_url() -> str:
    # Loopback to our own app for read-only command handlers. Defaults to the
    # container-internal port (:8000); the container also sets ZEUS_CORE_URL.
    return os.getenv("ZEUS_CORE_URL", "http://127.0.0.1:8000").rstrip("/")


def _default_channel() -> int:
    try:
        return int(os.getenv("ZEUS_MESH_DEFAULT_CHANNEL", "1"))
    except ValueError:
        return 1


def _audit_db_path() -> Path:
    return Path(os.getenv("ZEUS_MESH_AUDIT_DB", "zeus/data/mesh.db"))


def _dedupe_window_s() -> float:
    try:
        return float(os.getenv("ZEUS_MESH_DEDUPE_MIN", "30")) * 60.0
    except ValueError:
        return 30 * 60.0


def _rate_per_min() -> float:
    try:
        return float(os.getenv("ZEUS_MESH_RATE_PER_MIN", "6"))
    except ValueError:
        return 6.0


def _rate_burst() -> float:
    try:
        return float(os.getenv("ZEUS_MESH_RATE_BURST", "3"))
    except ValueError:
        return 3.0


# ------------------------------------------------------------------
# Quiet hours
# ------------------------------------------------------------------


def _parse_quiet_hours() -> tuple[dtime, dtime] | None:
    """Parse ZEUS_MESH_QUIET_HOURS='HH:MM-HH:MM' into a (start, end) pair.

    Returns None when unset or malformed (fail-open on the parse: a bad config
    should not silently suppress every alert). Window wrap over midnight is
    handled at comparison time.
    """
    raw = os.getenv("ZEUS_MESH_QUIET_HOURS", "22:00-07:00").strip()
    if not raw:
        return None
    try:
        start_s, end_s = raw.split("-", 1)
        sh, sm = (int(x) for x in start_s.strip().split(":", 1))
        eh, em = (int(x) for x in end_s.strip().split(":", 1))
        return dtime(sh, sm), dtime(eh, em)
    except (ValueError, TypeError):
        logger.warning("ZEUS_MESH_QUIET_HOURS malformed: %r", raw)
        return None


def _in_quiet_hours(now: dtime | None = None) -> bool:
    window = _parse_quiet_hours()
    if window is None:
        return False
    start, end = window
    now = now or datetime.now().time()
    if start <= end:
        return start <= now < end
    # Wraps past midnight (e.g. 22:00-07:00): inside if before end OR after start.
    return now >= start or now < end


# ------------------------------------------------------------------
# Rate limiting (in-process token buckets: global + per source)
# ------------------------------------------------------------------

_buckets: dict[str, list[float]] = {}  # key -> [tokens, last_refill_ts]
_bucket_lock = threading.Lock()


def _take_token(key: str) -> bool:
    """Consume one token from ``key``'s bucket. False when empty."""
    rate = _rate_per_min() / 60.0  # tokens per second
    burst = _rate_burst()
    now = time.monotonic()
    with _bucket_lock:
        tokens, last = _buckets.get(key, [burst, now])
        tokens = min(burst, tokens + (now - last) * rate)
        if tokens >= 1.0:
            _buckets[key] = [tokens - 1.0, now]
            return True
        _buckets[key] = [tokens, now]
        return False


# ------------------------------------------------------------------
# Dedupe (in-process; keyed by dedupe_key + payload signature)
# ------------------------------------------------------------------

_dedupe: dict[str, list] = {}  # dedupe_key -> [last_ts, signature]
_dedupe_lock = threading.Lock()


def _signature(text: str) -> str:
    return hashlib.sha1(text.strip().encode("utf-8", "replace")).hexdigest()[:16]


def _is_duplicate(dedupe_key: str, sig: str) -> bool:
    """True if this key fired the same payload within the dedupe window.

    A *changed* signature always passes (the condition changed, so re-alert);
    an unchanged signature within the window is suppressed. Prevents a standing
    condition ("GPU hot") from re-firing every Kairos cycle.
    """
    window = _dedupe_window_s()
    now = time.monotonic()
    with _dedupe_lock:
        prev = _dedupe.get(dedupe_key)
        if prev and prev[1] == sig and (now - prev[0]) < window:
            return True
        _dedupe[dedupe_key] = [now, sig]
        return False


# ------------------------------------------------------------------
# Audit (SQLite; also used by /mesh/command later)
# ------------------------------------------------------------------

_AUDIT_INIT_SQL = """
CREATE TABLE IF NOT EXISTS mesh_audit (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ts REAL NOT NULL,
    direction TEXT NOT NULL,
    source TEXT,
    sender_node TEXT,
    text TEXT,
    priority TEXT,
    delivered INTEGER NOT NULL DEFAULT 0,
    reason TEXT,
    aegis_flags TEXT
);
CREATE INDEX IF NOT EXISTS ix_mesh_audit_ts ON mesh_audit (ts);
"""


def _audit(
    *,
    direction: str,
    source: str | None,
    text: str,
    priority: str | None = None,
    sender_node: str | None = None,
    delivered: bool = False,
    reason: str | None = None,
    aegis_flags: list[str] | None = None,
) -> None:
    path = _audit_db_path()
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        conn = sqlite3.connect(str(path))
        try:
            conn.executescript(_AUDIT_INIT_SQL)
            conn.execute(
                "INSERT INTO mesh_audit "
                "(ts, direction, source, sender_node, text, priority, delivered, reason, aegis_flags) "
                "VALUES (?,?,?,?,?,?,?,?,?)",
                (
                    time.time(),
                    direction,
                    source,
                    sender_node,
                    text[:512],
                    priority,
                    1 if delivered else 0,
                    reason,
                    ",".join(aegis_flags) if aegis_flags else None,
                ),
            )
            conn.commit()
        finally:
            conn.close()
    except Exception as exc:  # audit must never break the send path
        logger.warning("mesh audit write failed: %s", exc)


# ------------------------------------------------------------------
# Chunking (byte-aware, [N/M] prefixed)
# ------------------------------------------------------------------


def _chunk(text: str, limit: int = _CHUNK_BYTES) -> list[str]:
    """Split ``text`` into chunks whose UTF-8 encoding fits ``limit`` bytes.

    A single-chunk message carries no prefix; multi-chunk parts get an
    ``[i/n] `` prefix so the receiver can order and spot gaps. The prefix is
    counted against the limit so a part never exceeds the sender's cap.
    """
    text = " ".join(text.replace("\r", " ").replace("\n", " ").split())
    if len(text.encode("utf-8")) <= limit:
        return [text]

    # First pass with a conservative payload budget to leave room for prefixes.
    budget = limit - len("[99/99] ")
    raw: list[str] = []
    cur = ""
    for ch in text:
        if len((cur + ch).encode("utf-8")) > budget:
            raw.append(cur)
            cur = ch
        else:
            cur += ch
    if cur:
        raw.append(cur)

    n = len(raw)
    return [f"[{i}/{n}] {part}" for i, part in enumerate(raw, 1)]


# ------------------------------------------------------------------
# Sender call
# ------------------------------------------------------------------


async def _send_chunks(chunks: list[str], channel: int, destination: int | None) -> bool:
    """POST each chunk to the meshtastic-sender. True only if all succeed."""
    url = f"{_sender_url()}/send"
    async with httpx.AsyncClient(timeout=20.0) as client:
        for part in chunks:
            payload: dict[str, Any] = {"text": part, "channel": channel}
            if destination is not None:
                payload["destination"] = destination
            try:
                r = await client.post(url, json=payload)
                r.raise_for_status()
            except Exception as exc:
                logger.warning("mesh sender call failed: %s", exc)
                return False
    return True


# ------------------------------------------------------------------
# Endpoint
# ------------------------------------------------------------------


class MeshNotifyRequest(BaseModel):
    text: str = Field(..., min_length=1, max_length=4096)
    channel: int | None = None
    destination: int | None = None  # None = channel broadcast; node-num = PKI DM (phase 5)
    priority: str = "normal"
    dedupe_key: str | None = None
    source: str = "manual"


@router.post("/mesh/notify")
async def mesh_notify(req: MeshNotifyRequest) -> dict[str, Any]:
    """Originate an outbound mesh message through the full policy pipeline.

    Returns {ok, delivered, reason, chunks}. ``ok`` reflects a well-formed,
    permitted request; ``delivered`` reflects the radio actually accepting it.
    A suppressed message (quiet hours, rate limit, dedupe) returns ok=True,
    delivered=False with a reason — the caller is not at fault.
    """
    priority = req.priority.strip().lower()
    if priority not in _VALID_PRIORITIES:
        priority = "normal"
    channel = req.channel if req.channel is not None else _default_channel()
    source = (req.source or "manual").strip() or "manual"
    text = req.text.strip()

    def _result(delivered: bool, reason: str, chunks: int = 0, flags: list[str] | None = None):
        _audit(
            direction="out",
            source=source,
            text=text,
            priority=priority,
            delivered=delivered,
            reason=reason,
            aegis_flags=flags,
        )
        return {"ok": reason != "outbound_disabled", "delivered": delivered, "reason": reason, "chunks": chunks}

    # 1. Master gate.
    if not _outbound_enabled():
        return _result(False, "outbound_disabled")

    # 2. Aegis on the outbound text (never transmit rejected content).
    if aegis_enabled():
        outcome = evaluate_text(text, policy_name=_AEGIS_POLICY)
        if outcome.status == "rejected":
            logger.warning("mesh notify aegis-rejected source=%s", source)
            return _result(False, "aegis_rejected", flags=outcome.flags or None)
        aegis_flags = outcome.flags or None
    else:
        aegis_flags = None

    # 3. Quiet hours (critical bypasses).
    if priority != "critical" and _in_quiet_hours():
        return _result(False, "quiet_hours", flags=aegis_flags)

    # 4. Dedupe (only when a key is supplied).
    if req.dedupe_key:
        if _is_duplicate(req.dedupe_key, _signature(text)):
            return _result(False, "deduped", flags=aegis_flags)

    # 5. Rate limit (critical bypasses; global + per-source buckets).
    if priority != "critical":
        if not _take_token("__global__") or not _take_token(f"src:{source}"):
            return _result(False, "rate_limited", flags=aegis_flags)

    # 6. Chunk + 7. Send.
    chunks = _chunk(text)
    delivered = await _send_chunks(chunks, channel, req.destination)
    return _result(delivered, "sent" if delivered else "send_failed", chunks=len(chunks), flags=aegis_flags)


# ------------------------------------------------------------------
# Break-glass commands (READ-ONLY, LLM-free)
# ------------------------------------------------------------------
#
# Deterministic parsing + local loopback only — NO cloud LLM, NO internet — so
# `!status` works during a WAN outage, which is the whole point. There is no
# mutation path: unknown commands return help, never fall through to anything
# that changes state. Replies route out via the /mesh/notify choke point.

_HELP_TEXT = "cmds: !status | !ping <host[:port]> | !svc <name> | !help"


async def _loopback_json(path: str, base: str | None = None, timeout: float = 6.0) -> dict[str, Any]:
    url = f"{(base or _core_url())}{path}"
    async with httpx.AsyncClient(timeout=timeout) as client:
        r = await client.get(url)
        r.raise_for_status()
        return r.json() or {}


async def _cmd_status() -> str:
    """Compact one-line host + radio health for a single-packet reply."""
    parts: list[str] = []
    try:
        sysd = await _loopback_json("/admin/system")
        up_d = round((sysd.get("uptime_seconds") or 0) / 86400.0, 1)
        parts.append(f"up {up_d}d")
        load = sysd.get("load_avg") or []
        if load:
            parts.append(f"load {load[0]:.1f}")
        disks = sysd.get("disks") or []
        if disks:
            worst = max(disks, key=lambda d: d.get("percent_used") or 0)
            parts.append(f"disk {worst.get('path')} {worst.get('percent_used'):.0f}%")
        mem = sysd.get("memory") or {}
        if mem.get("percent_used") is not None:
            parts.append(f"mem {mem['percent_used']:.0f}%")
        for g in sysd.get("gpus") or []:
            parts.append(f"GPU{g.get('index')} {g.get('temperature_c'):.0f}C")
    except Exception as exc:
        parts.append(f"host:? ({type(exc).__name__})")
    try:
        st = await _loopback_json("/status", base=_sender_url())
        parts.append("radio " + ("ok" if st.get("radio_reachable") else "DOWN"))
        parts.append(f"tx {st.get('tx_ok', 0)}/{st.get('tx_fail', 0)}")
    except Exception:
        parts.append("radio:?")
    return "; ".join(parts)


def _ping_target_allowed(ip: str) -> bool:
    """Restrict !ping to private/loopback targets unless explicitly allowlisted.

    Stops the command being used as a public port scanner if the channel is
    ever abused. ZEUS_MESH_PING_ALLOWLIST adds specific hostnames/IPs.
    """
    try:
        addr = ipaddress.ip_address(ip)
        if addr.is_private or addr.is_loopback or addr.is_link_local:
            return True
    except ValueError:
        pass
    allow = {h.strip() for h in os.getenv("ZEUS_MESH_PING_ALLOWLIST", "").split(",") if h.strip()}
    return ip in allow


def _cmd_ping(arg: str) -> str:
    """TCP reachability probe (not ICMP): `<host[:port]>`, default port 22.

    A TCP connect is a better 'is it up' signal in a homelab than ICMP and needs
    no raw-socket privilege. Targets are restricted to private ranges by default.
    """
    if not arg:
        return "ping: usage !ping <host[:port]>"
    host, _, port_s = arg.partition(":")
    host = host.strip()
    try:
        port = int(port_s) if port_s.strip() else 22
    except ValueError:
        return "ping: bad port"
    try:
        infos = socket.getaddrinfo(host, port, proto=socket.IPPROTO_TCP)
        ip = infos[0][4][0]
    except OSError:
        return f"{host}: DNS fail"
    if not (_ping_target_allowed(host) or _ping_target_allowed(ip)):
        return f"{host}: target not allowed"
    start = time.monotonic()
    try:
        with socket.create_connection((ip, port), timeout=2.0):
            ms = (time.monotonic() - start) * 1000.0
            return f"{host}:{port} reachable {ms:.0f}ms"
    except OSError:
        return f"{host}:{port} UNREACHABLE"


async def _cmd_svc(arg: str) -> str:
    if not arg:
        return "svc: usage !svc <name>"
    name = arg.strip()
    try:
        sysd = await _loopback_json("/admin/system")
    except Exception:
        return "svc: host unreachable"
    docker = sysd.get("docker")
    if not docker or not docker.get("names"):
        return "svc: no docker visibility from core"
    names = set(docker.get("names") or [])
    if docker.get("names_truncated"):
        # running_count exceeds the reported name cap; a miss may be a false negative.
        return f"{name}: " + ("up" if name in names else "not in first 20 (truncated)")
    return f"{name}: " + ("up" if name in names else "DOWN")


async def _dispatch_command(cmd: str, arg: str) -> str:
    if cmd == "help":
        return _HELP_TEXT
    if cmd == "status":
        return await _cmd_status()
    if cmd == "ping":
        return _cmd_ping(arg)
    if cmd == "svc":
        return await _cmd_svc(arg)
    # Unknown command -> help. Never falls through to anything mutating.
    return _HELP_TEXT


class MeshCommandRequest(BaseModel):
    text: str = Field(..., min_length=1, max_length=230)
    sender_node: int | None = None


@router.post("/mesh/command")
async def mesh_command(req: MeshCommandRequest) -> dict[str, Any]:
    """Handle a read-only break-glass command and reply over the mesh.

    Returns {command, reply, delivered, reason}. The reply is computed locally
    (no LLM, no internet) and sent back through the /mesh/notify choke point.
    """
    raw = req.text.strip()
    token, _, rest = raw.partition(" ")
    cmd = token.lstrip("!").lower()
    arg = rest.strip()

    reply = await _dispatch_command(cmd, arg)

    _audit(
        direction="in",
        source="command",
        text=raw,
        sender_node=str(req.sender_node) if req.sender_node is not None else None,
        delivered=True,
        reason=f"cmd:{cmd}",
    )

    # Reply routes back out through the choke point (source="command",
    # normal priority so it is subject to quiet hours like any reply).
    out = await mesh_notify(
        MeshNotifyRequest(text=reply, priority="normal", source="command")
    )
    return {
        "command": cmd,
        "reply": reply,
        "delivered": bool(out.get("delivered")),
        "reason": out.get("reason"),
    }
