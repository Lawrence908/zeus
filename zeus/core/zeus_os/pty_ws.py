# zeus/core/zeus_os/pty_ws.py — WebSocket-driven PTY for the WM terminal.
#
# Phase 1: spawns `bash -i` inside the zeus-core container. Visible filesystem
# is the container view (./zeus, ./zeus/data, ~/.zeus, the Obsidian mount, the
# Kiwix ZIM mount). Phase 1.5 swaps the spawn for `ssh chris@host.docker.internal`
# when ZEUS_OS_PTY_HOST_SSH=1.
#
# Wire frames (JSON over text):
#   client → server: {"type":"input","data":"<utf8>"}
#                    {"type":"resize","cols":120,"rows":40}
#   server → client: {"type":"output","data":"<utf8>"}
#                    {"type":"exit","code":<int>}
from __future__ import annotations

import asyncio
import fcntl
import json
import logging
import os
import pty
import shlex
import signal
import struct
import termios
from typing import Any

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

logger = logging.getLogger("zeus.zeus_os.pty")

router = APIRouter()


_READ_CHUNK = 4096
_MAX_INPUT_BYTES = 64 * 1024


def _spawn_shell(cwd: str | None) -> tuple[int, int]:
    """Fork a child running the configured shell; return (pid, master_fd)."""
    if os.getenv("ZEUS_OS_PTY_HOST_SSH", "0").strip().lower() in ("1", "true", "yes", "on"):
        host = os.getenv("ZEUS_OS_PTY_SSH_HOST", "chris@host.docker.internal")
        cmd_str = os.getenv("ZEUS_OS_PTY_SSH_COMMAND", "bash -il")
        identity = os.getenv("ZEUS_OS_PTY_SSH_IDENTITY", "/root/.ssh/id_ed25519_zeus_os")
        known_hosts = os.getenv("ZEUS_OS_PTY_SSH_KNOWN_HOSTS", "/root/.zeus/zeus-os/known_hosts")
        argv = [
            "ssh",
            "-tt",
            "-i", identity,
            "-o", "BatchMode=yes",
            "-o", "StrictHostKeyChecking=accept-new",
            "-o", f"UserKnownHostsFile={known_hosts}",
            "-o", "ServerAliveInterval=30",
            "-o", "ServerAliveCountMax=3",
            host,
            cmd_str,
        ]
    else:
        shell = os.getenv("ZEUS_OS_PTY_SHELL") or os.getenv("SHELL") or "/bin/bash"
        argv = shlex.split(shell) + ["-i"]

    pid, master_fd = pty.fork()
    if pid == 0:
        # Child process.
        env = os.environ.copy()
        env.setdefault("TERM", "xterm-256color")
        env.setdefault("LANG", "en_US.UTF-8")
        env.setdefault("LC_ALL", "en_US.UTF-8")
        env["ZEUS_OS"] = "1"
        target_cwd = cwd or os.getenv("ZEUS_OS_PTY_CWD", "/app/zeus")
        try:
            os.chdir(target_cwd)
        except OSError:
            try:
                os.chdir(os.path.expanduser("~"))
            except OSError:
                pass
        try:
            os.execvpe(argv[0], argv, env)
        except OSError as exc:
            os.write(2, f"failed to exec {argv[0]}: {exc}\n".encode("utf-8"))
            os._exit(127)
    return pid, master_fd


def _set_winsize(fd: int, rows: int, cols: int) -> None:
    try:
        rows = max(1, min(500, int(rows)))
        cols = max(1, min(500, int(cols)))
    except (TypeError, ValueError):
        return
    try:
        fcntl.ioctl(fd, termios.TIOCSWINSZ, struct.pack("HHHH", rows, cols, 0, 0))
    except OSError:
        pass


def _reap(pid: int, master_fd: int) -> int:
    """Best-effort cleanup: close fd, terminate child, return exit code."""
    try:
        os.close(master_fd)
    except OSError:
        pass
    try:
        os.kill(pid, signal.SIGHUP)
    except OSError:
        pass
    try:
        _, status = os.waitpid(pid, os.WNOHANG)
        if status == 0:
            return -1
        if os.WIFEXITED(status):
            return os.WEXITSTATUS(status)
        if os.WIFSIGNALED(status):
            return 128 + os.WTERMSIG(status)
    except OSError:
        pass
    return -1


@router.websocket("/pty")
async def pty_ws(ws: WebSocket) -> None:
    await ws.accept()
    cwd_q = ws.query_params.get("cwd")
    cols_q = ws.query_params.get("cols")
    rows_q = ws.query_params.get("rows")

    try:
        pid, master_fd = _spawn_shell(cwd_q)
    except OSError as exc:
        await ws.send_text(json.dumps({"type": "exit", "code": -1, "error": str(exc)}))
        await ws.close()
        return

    if cols_q and rows_q:
        _set_winsize(master_fd, rows_q, cols_q)

    loop = asyncio.get_event_loop()
    stop = asyncio.Event()

    async def pump_pty_to_ws() -> None:
        # Drain the pty master in a background thread; the event loop just
        # forwards bytes as they arrive.
        try:
            while not stop.is_set():
                try:
                    data = await loop.run_in_executor(None, _safe_read, master_fd)
                except OSError:
                    break
                if not data:
                    break
                try:
                    await ws.send_text(json.dumps({
                        "type": "output",
                        "data": data.decode("utf-8", errors="replace"),
                    }))
                except (RuntimeError, WebSocketDisconnect):
                    break
        finally:
            stop.set()

    async def pump_ws_to_pty() -> None:
        try:
            while not stop.is_set():
                try:
                    msg = await ws.receive_text()
                except WebSocketDisconnect:
                    return
                if len(msg) > _MAX_INPUT_BYTES:
                    continue
                try:
                    frame = json.loads(msg)
                except json.JSONDecodeError:
                    continue
                ftype = frame.get("type")
                if ftype == "input":
                    data = frame.get("data", "")
                    if not isinstance(data, str):
                        continue
                    try:
                        await loop.run_in_executor(None, os.write, master_fd, data.encode("utf-8"))
                    except OSError:
                        return
                elif ftype == "resize":
                    _set_winsize(master_fd, frame.get("rows", 24), frame.get("cols", 80))
                elif ftype == "signal":
                    sig = frame.get("name", "INT")
                    try:
                        os.kill(pid, getattr(signal, f"SIG{sig}", signal.SIGINT))
                    except OSError:
                        pass
        finally:
            stop.set()

    pump_out = asyncio.create_task(pump_pty_to_ws())
    pump_in = asyncio.create_task(pump_ws_to_pty())
    await asyncio.wait({pump_out, pump_in}, return_when=asyncio.FIRST_COMPLETED)
    stop.set()
    for t in (pump_out, pump_in):
        if not t.done():
            t.cancel()

    code = _reap(pid, master_fd)
    try:
        await ws.send_text(json.dumps({"type": "exit", "code": code}))
    except (RuntimeError, WebSocketDisconnect):
        pass
    try:
        await ws.close()
    except RuntimeError:
        pass


def _safe_read(fd: int) -> bytes:
    try:
        return os.read(fd, _READ_CHUNK)
    except OSError:
        return b""
