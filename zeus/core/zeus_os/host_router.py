# zeus/core/zeus_os/host_router.py — Host-side process + network introspection.
#
# Runs read-only host commands through the same SSH channel used by the Zeus
# OS Terminal app (configured by ZEUS_OS_PTY_*). Gated on the same env vars,
# so when host SSH isn't wired the endpoints return a degraded payload
# instead of a 500.
from __future__ import annotations

import asyncio
import json
import logging
import os
import shlex
from typing import Any

from fastapi import APIRouter

logger = logging.getLogger("zeus.zeus_os.host")

router = APIRouter()


def _ssh_args() -> list[str] | None:
    """Build the SSH base argv if host PTY mode is enabled; else None."""
    enabled = os.getenv("ZEUS_OS_PTY_HOST_SSH", "0").strip().lower() in ("1", "true", "yes", "on")
    if not enabled:
        return None
    host = os.getenv("ZEUS_OS_PTY_SSH_HOST", "chris@host.docker.internal")
    identity = os.getenv("ZEUS_OS_PTY_SSH_IDENTITY", "/root/.ssh/id_ed25519_zeus_os")
    known_hosts = os.getenv("ZEUS_OS_PTY_SSH_KNOWN_HOSTS", "/root/.zeus/zeus-os/known_hosts")
    return [
        "ssh",
        "-i", identity,
        "-o", "BatchMode=yes",
        "-o", "StrictHostKeyChecking=accept-new",
        "-o", f"UserKnownHostsFile={known_hosts}",
        "-o", "ControlMaster=auto",
        "-o", "ControlPath=/tmp/zeus_os_host_ssh-%C",
        "-o", "ControlPersist=60",
        "-o", "ConnectTimeout=3",
        host,
    ]


async def _ssh_run(cmd: str, timeout: float = 6.0) -> tuple[int, str, str]:
    """Run a shell command on the host via SSH. Returns (rc, stdout, stderr).

    rc=-1 with stderr describing the failure when SSH isn't configured or the
    process can't be spawned.
    """
    base = _ssh_args()
    if base is None:
        return -1, "", "host SSH not configured (ZEUS_OS_PTY_HOST_SSH=0)"
    argv = base + [cmd]
    try:
        proc = await asyncio.create_subprocess_exec(
            *argv,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        stdout, stderr = await asyncio.wait_for(proc.communicate(), timeout=timeout)
        return proc.returncode or 0, stdout.decode("utf-8", "replace"), stderr.decode("utf-8", "replace")
    except asyncio.TimeoutError:
        return -1, "", f"timed out after {timeout}s"
    except OSError as exc:
        return -1, "", str(exc)


# ─── Processes ───────────────────────────────────────────────────────────────


@router.get("/sys/processes")
async def host_processes(limit: int = 40) -> dict[str, Any]:
    """Top processes by CPU on the host (via SSH).

    Returns {processes: [{pid, user, pcpu, pmem, rss_mb, comm, cmd}], ts}.
    """
    limit = max(1, min(200, int(limit)))
    # ps fields chosen for portability across Ubuntu/Debian; rss is in KB.
    # We use rss instead of %mem alone because %mem rounds to 1 digit on
    # newer ps which makes near-zero processes look identical.
    cmd = (
        "ps -eo pid,user,pcpu,pmem,rss,comm,args --sort=-pcpu --no-headers"
        f" | head -n {limit}"
    )
    rc, stdout, stderr = await _ssh_run(cmd, timeout=5.0)
    procs: list[dict[str, Any]] = []
    if rc == 0 and stdout:
        for line in stdout.splitlines():
            parts = line.split(None, 6)
            if len(parts) < 6:
                continue
            pid, user, pcpu, pmem, rss, comm = parts[:6]
            args = parts[6] if len(parts) > 6 else comm
            try:
                procs.append({
                    "pid": int(pid),
                    "user": user,
                    "pcpu": float(pcpu),
                    "pmem": float(pmem),
                    "rss_mb": round(int(rss) / 1024.0, 1),
                    "comm": comm,
                    "cmd": args[:300],
                })
            except ValueError:
                continue
    return {
        "processes": procs,
        "ts": _utc_now_iso(),
        "ok": rc == 0,
        "error": stderr.strip() if rc != 0 else None,
    }


# ─── Network ────────────────────────────────────────────────────────────────


@router.get("/sys/network")
async def host_network() -> dict[str, Any]:
    """Tailscale peers + local IPv4 interface addresses (via SSH)."""
    # Tailscale: --json gives a structured snapshot. Older clients may not
    # support it; we fall back to parsing the text form.
    ts_rc, ts_out, ts_err = await _ssh_run("tailscale status --json 2>/dev/null || tailscale status", timeout=5.0)
    ts_peers: list[dict[str, Any]] = []
    ts_self: dict[str, Any] = {}
    ts_raw_text = ""
    if ts_rc == 0 and ts_out:
        stripped = ts_out.strip()
        if stripped.startswith("{"):
            try:
                data = json.loads(stripped)
                self_obj = data.get("Self") or {}
                ts_self = {
                    "hostname": self_obj.get("HostName"),
                    "dns_name": self_obj.get("DNSName"),
                    "os": self_obj.get("OS"),
                    "ip": (self_obj.get("TailscaleIPs") or [None])[0],
                    "online": self_obj.get("Online", False),
                }
                for _, p in (data.get("Peer") or {}).items():
                    ts_peers.append({
                        "hostname": p.get("HostName"),
                        "dns_name": p.get("DNSName"),
                        "os": p.get("OS"),
                        "ip": (p.get("TailscaleIPs") or [None])[0],
                        "online": p.get("Online", False),
                        "last_seen": p.get("LastSeen"),
                        "rx_bytes": p.get("RxBytes"),
                        "tx_bytes": p.get("TxBytes"),
                    })
            except json.JSONDecodeError:
                ts_raw_text = stripped
        else:
            ts_raw_text = stripped

    # Local interfaces: prefer JSON output (`ip -j` on iproute2 ≥ 4.6).
    iface_rc, iface_out, _ = await _ssh_run("ip -4 -j addr 2>/dev/null", timeout=3.0)
    interfaces: list[dict[str, Any]] = []
    if iface_rc == 0 and iface_out.strip().startswith("["):
        try:
            for iface in json.loads(iface_out):
                addrs = [a.get("local") for a in iface.get("addr_info", []) if a.get("local")]
                if not addrs:
                    continue
                interfaces.append({
                    "name": iface.get("ifname"),
                    "state": iface.get("operstate"),
                    "addrs": addrs,
                    "mac": iface.get("address"),
                    "mtu": iface.get("mtu"),
                })
        except (json.JSONDecodeError, AttributeError, TypeError) as exc:
            logger.debug("parse iface json failed: %s", exc)

    return {
        "tailscale": {
            "self": ts_self,
            "peers": ts_peers,
            "raw": ts_raw_text or None,
            "ok": ts_rc == 0,
            "error": ts_err.strip() if ts_rc != 0 else None,
        },
        "interfaces": interfaces,
        "ts": _utc_now_iso(),
    }


def _utc_now_iso() -> str:
    from datetime import datetime, timezone
    return datetime.now(tz=timezone.utc).isoformat()
