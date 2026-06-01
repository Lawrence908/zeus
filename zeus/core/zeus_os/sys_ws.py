# zeus/core/zeus_os/sys_ws.py — 1Hz system stats stream.
#
# Phase 1: container-view CPU + memory from /proc. GPU stats are stubbed (None)
# until Phase 1.5 wires nvidia-smi over the host-SSH PTY channel.
from __future__ import annotations

import asyncio
import json
import logging
import os
import shutil
from typing import Any

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

logger = logging.getLogger("zeus.zeus_os.sys")

router = APIRouter()


_CPU_PREV: dict[str, tuple[int, int]] = {}


def _read_cpu_total() -> tuple[int, int] | None:
    """Returns (total_jiffies, idle_jiffies) from /proc/stat 'cpu ' line."""
    try:
        with open("/proc/stat", "r", encoding="utf-8") as fh:
            for line in fh:
                if line.startswith("cpu "):
                    parts = line.split()
                    nums = [int(x) for x in parts[1:]]
                    # user nice system idle iowait irq softirq steal guest guest_nice
                    idle = nums[3] + (nums[4] if len(nums) > 4 else 0)
                    total = sum(nums)
                    return total, idle
    except (OSError, ValueError) as exc:
        logger.debug("read /proc/stat failed: %s", exc)
    return None


def _read_mem() -> dict[str, int] | None:
    try:
        info: dict[str, int] = {}
        with open("/proc/meminfo", "r", encoding="utf-8") as fh:
            for line in fh:
                k, _, rest = line.partition(":")
                v = rest.strip().split()
                if not v:
                    continue
                try:
                    info[k] = int(v[0]) * 1024  # kB → bytes
                except ValueError:
                    continue
        if "MemTotal" not in info:
            return None
        total = info["MemTotal"]
        # MemAvailable is the canonical "available" since 3.14; fall back if absent.
        avail = info.get("MemAvailable", info.get("MemFree", 0))
        used = max(0, total - avail)
        return {"total": total, "used": used, "available": avail}
    except OSError as exc:
        logger.debug("read /proc/meminfo failed: %s", exc)
    return None


def _read_loadavg() -> list[float] | None:
    try:
        with open("/proc/loadavg", "r", encoding="utf-8") as fh:
            parts = fh.read().split()
        return [float(parts[0]), float(parts[1]), float(parts[2])]
    except (OSError, ValueError, IndexError):
        return None


_NVIDIA_QUERY = "utilization.gpu,memory.used,memory.total,temperature.gpu"


def _parse_nvidia_csv(stdout: bytes) -> dict[str, Any] | None:
    try:
        line = stdout.decode("utf-8", errors="replace").splitlines()[0]
        util, mem_used_mib, mem_total_mib, temp = [s.strip() for s in line.split(",")]
        return {
            "util": float(util),
            "mem_used": int(mem_used_mib) * 1024 * 1024,
            "mem_total": int(mem_total_mib) * 1024 * 1024,
            "temp_c": float(temp),
        }
    except (ValueError, IndexError, UnicodeDecodeError):
        return None


async def _read_gpu_local() -> dict[str, Any] | None:
    if shutil.which("nvidia-smi") is None:
        return None
    try:
        proc = await asyncio.create_subprocess_exec(
            "nvidia-smi",
            f"--query-gpu={_NVIDIA_QUERY}",
            "--format=csv,noheader,nounits",
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.DEVNULL,
        )
        stdout, _ = await asyncio.wait_for(proc.communicate(), timeout=2.0)
    except (asyncio.TimeoutError, OSError):
        return None
    return _parse_nvidia_csv(stdout)


async def _read_gpu_ssh() -> dict[str, Any] | None:
    host = os.getenv("ZEUS_OS_PTY_SSH_HOST", "chris@host.docker.internal")
    identity = os.getenv("ZEUS_OS_PTY_SSH_IDENTITY", "/root/.ssh/id_ed25519_zeus_os")
    known_hosts = os.getenv("ZEUS_OS_PTY_SSH_KNOWN_HOSTS", "/root/.zeus/zeus-os/known_hosts")
    # ControlMaster: reuse one multiplexed SSH connection across the 1Hz polls
    # so each sample is ~30ms instead of a full handshake.
    ctl_path = "/tmp/zeus_os_gpu_ssh-%C"
    args = [
        "ssh",
        "-i", identity,
        "-o", "BatchMode=yes",
        "-o", "StrictHostKeyChecking=accept-new",
        "-o", f"UserKnownHostsFile={known_hosts}",
        "-o", "ControlMaster=auto",
        "-o", f"ControlPath={ctl_path}",
        "-o", "ControlPersist=60",
        "-o", "ConnectTimeout=3",
        host,
        f"nvidia-smi --query-gpu={_NVIDIA_QUERY} --format=csv,noheader,nounits",
    ]
    try:
        proc = await asyncio.create_subprocess_exec(
            *args,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.DEVNULL,
        )
        stdout, _ = await asyncio.wait_for(proc.communicate(), timeout=4.0)
    except (asyncio.TimeoutError, OSError):
        return None
    if proc.returncode != 0:
        return None
    return _parse_nvidia_csv(stdout)


async def _read_gpu() -> dict[str, Any] | None:
    """Sample GPU. Order of preference:
      1) ZEUS_OS_GPU_LOCAL=1  → in-container nvidia-smi (rare; needs GPU reservation).
      2) ZEUS_OS_GPU_SSH=1    → ssh out to the host (Phase 1.5 default once compose is updated).
    Returns None when neither path yields a parseable sample.
    """
    if os.getenv("ZEUS_OS_GPU_LOCAL", "0").strip().lower() in ("1", "true", "yes", "on"):
        sample = await _read_gpu_local()
        if sample is not None:
            return sample
    if os.getenv("ZEUS_OS_GPU_SSH", "0").strip().lower() in ("1", "true", "yes", "on"):
        return await _read_gpu_ssh()
    return None


@router.websocket("/sys/stream")
async def sys_stream(ws: WebSocket) -> None:
    await ws.accept()
    prev = _read_cpu_total()
    try:
        while True:
            await asyncio.sleep(1.0)
            cur = _read_cpu_total()
            cpu_pct: float | None = None
            if prev is not None and cur is not None:
                dt_total = max(1, cur[0] - prev[0])
                dt_idle = max(0, cur[1] - prev[1])
                cpu_pct = round(100.0 * (dt_total - dt_idle) / dt_total, 1)
            prev = cur
            mem = _read_mem()
            load = _read_loadavg()
            gpu = await _read_gpu()
            payload = {
                "cpu_pct": cpu_pct,
                "mem": mem,
                "load": load,
                "gpu": gpu,
            }
            try:
                await ws.send_text(json.dumps(payload))
            except (RuntimeError, WebSocketDisconnect):
                return
    except WebSocketDisconnect:
        return
    except Exception as exc:
        logger.warning("sys stream error: %s", exc)
        try:
            await ws.close()
        except RuntimeError:
            pass
