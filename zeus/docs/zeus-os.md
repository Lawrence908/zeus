# Zeus OS

Hyprland-style tiling window manager that runs in a browser. Side-by-side with the React dashboard at `zeus/frontend/` — Zeus OS is the spatial, keyboard-driven surface; the React app stays as the data-dense fallback.

## URLs

- Dev: `http://localhost:8231` (host Vite, proxies to Zeus core at `:8203`)
- Prod (after `npm run build`): `http://localhost:8203/os/`
- Phase 2 will land `https://zeus-os.chrislawrence.ca` via Caddy

## Code

```
zeus-os/                       SvelteKit + TS + Tailwind, adapter-static
  src/lib/wm/                  BSP tree, workspaces, store, keybind dispatcher
  src/lib/components/          Desktop, Window, Panel, Launcher, Cheatsheet, MobileShell
  src/lib/apps/                Terminal, Chat, SystemMonitor, FileManager, Placeholder
  src/lib/api/                 typed clients for the bridge + chat SSE
  src/lib/themes/              Catppuccin Mocha, Tokyo Night, Gruvbox Dark

zeus/core/_fs.py               shared allowlist + ripgrep helpers (vault + zeus_os)
zeus/core/zeus_os/             FastAPI bridge package
  router.py                    mounts subrouters under /zeus-os
  pty_ws.py                    WebSocket PTY (container bash -i, SSH upgrade gated)
  sys_ws.py                    1Hz /proc CPU+mem (GPU stubbed)
  fs_router.py                 REST /fs/{list,file,write,search,roots}
  config_router.py             REST /config (read/write ~/.zeus/zeus-os/config.json)
  apps_router.py               REST /apps (launcher registry)
```

## Bridge endpoints

All mounted at `/zeus-os/*` on Zeus core:

| Method | Path | Purpose |
|---|---|---|
| WS | `/zeus-os/pty` | bash -i over JSON frames (input/resize/signal → output/exit) |
| WS | `/zeus-os/sys/stream` | 1Hz `{cpu_pct, mem, load, gpu}` push |
| GET | `/zeus-os/fs/roots` | configured read/write roots |
| GET | `/zeus-os/fs/list?path=` | directory listing |
| GET | `/zeus-os/fs/file?path=` | read file (1 MB cap) |
| POST | `/zeus-os/fs/write` | atomic write, gated by `ZEUS_OS_FS_WRITE_ENABLED` |
| POST | `/zeus-os/fs/search` | ripgrep across configured read roots |
| GET | `/zeus-os/config` | user preferences |
| PUT | `/zeus-os/config` | persist preferences (atomic) |
| GET | `/zeus-os/apps` | launcher registry |

Existing endpoints reused without changes: `POST /chat/stream` (SSE), `GET /status`, `GET /admin/metrics`.

## Environment

Configured in `.env` (see `.env.example` for the full list):

```ini
ZEUS_OS_FS_ROOTS=/app/zeus,/app/zeus/data,/root/.zeus
ZEUS_OS_FS_WRITE_ROOTS=/root/.zeus
ZEUS_OS_FS_WRITE_ENABLED=1
ZEUS_OS_CONFIG_DIR=/root/.zeus/zeus-os
ZEUS_OS_PTY_CWD=/app/zeus
ZEUS_OS_PTY_HOST_SSH=0
```

Notes:
- Roots are container-paths because the FastAPI runs inside `zeus-core`. Phase 1.5 re-roots to `/home/chris/...` once the PTY upgrades to host SSH.
- A separate `ZEUS_FILE_READ_ROOTS` controls the LLM-facing `/vault/*` allowlist. Keep them distinct so widening the WM's view doesn't widen the model's.

## Keymap (default)

| Combo | Action |
|---|---|
| Super+Return | Open Terminal in focused split |
| Super+D / Ctrl+Space | Launcher |
| Super+Shift+Q | Close focused window |
| Super+F | Toggle floating (Phase 1.5) |
| Super+R | Cycle theme |
| Super+/ | Cheatsheet |
| Super+H/J/K/L | Focus left/down/up/right |
| Super+Shift+H/J/K/L | Move window |
| Super+V / Super+S | Split vertical / horizontal |
| Super+1..0 | Switch workspace |
| Super+Shift+1..0 | Move focused window to workspace N |

`Super` = Meta by default; switch to Alt in `~/.zeus/zeus-os/config.json` if your host WM captures Meta.

## Roadmap

- **Phase 1 (now)** — tiling WM shell, Terminal (container PTY), Chat, System Monitor, File Manager, theme switcher, mobile shell. Placeholder windows for everything else so the launcher feels complete.
- **Phase 1.5** — host-shell PTY via SSH from the container; nvidia-smi GPU stats over the same channel; restore-on-reload (sessions persisted in `~/.zeus/zeus-os/sessions.json`).
- **Phase 2** — plain-markdown Obsidian vault setup + viewer, Monaco code editor (lazy-loaded chunk), Home Assistant + Linear panels, Caddy `zeus-os.chrislawrence.ca`.
- **Phase 3** — image viewer, htop-style process manager, Tailscale peer list, scratchpad notepad, Google Calendar panel.
