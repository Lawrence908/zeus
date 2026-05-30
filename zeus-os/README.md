# Zeus OS

Hyprland-style tiling window manager that runs in a browser, dedicated to interacting with the [Zeus](../) assistant and the tools it orchestrates. Side-by-side with the React `zeus/frontend/` dashboard — Zeus OS is the spatial, keyboard-driven view; the React app stays as the data-dense fallback.

## Run it

```sh
# Dev (host Vite on :8231 → proxies to Zeus core at :8203)
npm install
npm run dev

# Prod build (emits into ../zeus/core/static/zeus-os/, served by FastAPI at /os/)
npm run build
```

Open `http://localhost:8231` for dev or `http://localhost:8203/os/` after a build. Phase 1 keybinds:

| Combo | Action |
|---|---|
| Super+Return | Open Terminal in focused split |
| Super+D / Ctrl+Space | Launcher |
| Super+H/J/K/L | Focus left/down/up/right |
| Super+Shift+H/J/K/L | Move window |
| Super+V / Super+S | Split vertical / horizontal |
| Super+Shift+Q | Close focused window |
| Super+F | Toggle floating |
| Super+1..0 | Switch workspace |
| Super+Shift+1..0 | Move window to workspace N |
| Super+R | Cycle theme |
| Super+/ | Cheatsheet |

`Super` is Meta by default; switch to Alt in settings if your OS captures Meta.

## Layout

- `src/lib/wm/` — BSP tiling tree, workspaces, keymap dispatcher
- `src/lib/components/` — Desktop, Window, Panel, Launcher, MobileShell
- `src/lib/apps/` — Terminal, Chat, SystemMonitor, FileManager, Placeholder
- `src/lib/api/` — typed clients for the `/zeus-os/*` bridge and the existing Zeus chat
- `src/lib/themes/` — token data for theme presets

The backend bridge is added into Zeus core under `/zeus-os/*` — see `../zeus/core/zeus_os/`.
