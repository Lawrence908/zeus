# zeus/docs/nemoclaw-ops.md — NemoClaw + OpenClaw Operational Runbook
#
# For Zeus homelab on daedalus (Ubuntu 24.04, RTX 3080).
# Access from Apollo via SSH tunnel. NemoClaw alpha (0.0.16+), Mar 2026.

## Architecture Overview

```
Apollo (workstation)                    daedalus (RTX 3080 server)
┌─────────────────────┐                ┌──────────────────────────────────────────┐
│ Browser             │  SSH -L        │  zeus-ollama (Docker):11435 → ctr 11434 │
│ http://127.0.0.1:   │◄──────────────►│  OpenShell Gateway  :8080               │
│   18789 (UI)        │  18789,18080   │  OpenClaw UI fwd    :18789              │
│   18080 (GW debug)  │                │  Zeus Core (Docker) :8203               │
└─────────────────────┘                │  Qdrant (Docker)    :6333               │
                                       └──────────────────────────────────────────┘
```

**Single Ollama runtime (current homelab):** **zeus-ollama** (`compose.yaml`, host port **11435** → container **11434**). Zeus Core and NemoClaw inference both target this instance when the OpenShell provider base URL points at it.

**OpenShell provider name (example):** `ollama-local` with `OPENAI_BASE_URL=http://<daedalus-LAN-IP>:11435/v1` — the name is arbitrary; rename to `zeus-ollama` if you prefer consistency with the container.

Zeus Aegis (in-process YAML regex on LLM outputs) and NemoClaw/OpenShell (OS-level sandbox
enforcement) are complementary layers — no overlap. See `zeus/safety/policy_engine.py`.

---

## SSH Aliases (Apollo — add to ~/.bashrc or ~/.bash_aliases)

```bash
# --- NemoClaw SSH tunnels (Apollo → daedalus) ---
# Main tunnel: OpenClaw UI + OpenShell gateway debug
alias nemotunnel='ssh -N -L 18789:127.0.0.1:18789 -L 18080:127.0.0.1:8080 chris@daedalus'

# If local port 18080 is busy on Apollo, use an alternate
alias nemotunnel-alt='ssh -N -L 18789:127.0.0.1:18789 -L 28080:127.0.0.1:8080 chris@daedalus'

# Quick open after tunnel is up
alias nemoui='xdg-open http://127.0.0.1:18789/ 2>/dev/null || echo "Open http://127.0.0.1:18789/ in browser"'
```

After adding, run `source ~/.bashrc` (or restart shell).

Usage:
1. `nemotunnel` (runs in foreground — Ctrl+C to stop; or add `&` to background)
2. In another terminal: `nemoui` or open `http://127.0.0.1:18789/` in browser
3. First time: append `#token=<gateway-token>` to the URL

---

## Server Aliases (daedalus — add to ~/.bashrc or ~/.bash_aliases)

```bash
# --- NemoClaw sandbox management ---
alias nemo-status='nemoclaw my-assistant status'
alias nemo-statusj='nemoclaw my-assistant status --json'
alias nemo-logs='nemoclaw my-assistant logs'
alias nemo-logsf='nemoclaw my-assistant logs -f'
alias nemo-connect='nemoclaw my-assistant connect'
alias nemo-list='nemoclaw list'
alias nemo-policies='nemoclaw my-assistant policy-list'
alias nemo-policyadd='nemoclaw my-assistant policy-add'

# --- OpenShell gateway ---
alias nemo-term='openshell term'
alias nemo-fwd='openshell forward start 18789 my-assistant -g nemoclaw --background'
alias nemo-fwdlist='openshell forward list'
alias nemo-fwdstop='openshell forward stop 18789 my-assistant'
alias nemo-inference='openshell inference get'

# --- Quick health check ---
alias nemo-health='nemoclaw my-assistant status && openshell forward list'

# --- Backup (run before destroy or upgrades) ---
nemo-backup() {
  local SANDBOX=my-assistant
  local BACKUP_DIR=~/.nemoclaw/backups/$(date +%Y%m%d-%H%M%S)
  mkdir -p "$BACKUP_DIR"/{cron,devices,credentials,identity,memory}
  echo "Backing up to $BACKUP_DIR ..."
  openshell sandbox download "$SANDBOX" /sandbox/.openclaw/openclaw.json "$BACKUP_DIR/"
  openshell sandbox download "$SANDBOX" /sandbox/.openclaw/models.json "$BACKUP_DIR/" 2>/dev/null
  openshell sandbox download "$SANDBOX" /sandbox/.openclaw/cron/jobs.json "$BACKUP_DIR/cron/" 2>/dev/null
  openshell sandbox download "$SANDBOX" /sandbox/.openclaw/devices "$BACKUP_DIR/devices/" 2>/dev/null
  openshell sandbox download "$SANDBOX" /sandbox/.openclaw/credentials "$BACKUP_DIR/credentials/" 2>/dev/null
  openshell sandbox download "$SANDBOX" /sandbox/.openclaw/identity "$BACKUP_DIR/identity/" 2>/dev/null
  openshell sandbox download "$SANDBOX" /sandbox/.openclaw/memory/main.sqlite "$BACKUP_DIR/memory/" 2>/dev/null
  openshell sandbox download "$SANDBOX" /sandbox/.openclaw/workspace "$BACKUP_DIR/workspace/"
  openshell sandbox download "$SANDBOX" /sandbox/.bashrc "$BACKUP_DIR/" 2>/dev/null
  openshell sandbox download "$SANDBOX" /sandbox/.gitconfig "$BACKUP_DIR/" 2>/dev/null
  openshell policy get "$SANDBOX" --full > "$BACKUP_DIR/policy_active.yaml" 2>/dev/null
  echo "Backup complete: $BACKUP_DIR"
}
```

---

## Phase 1: allowedOrigins + trustedProxies

Edit `/sandbox/.openclaw/openclaw.json` (via `nemo-connect` or the Config tab in the UI).

Merge these keys into the existing `gateway` block:

```json
{
  "gateway": {
    "controlUi": {
      "enabled": true,
      "allowedOrigins": [
        "http://127.0.0.1:18789",
        "http://localhost:18789"
      ]
    },
    "trustedProxies": [
      "127.0.0.1",
      "::1",
      "10.0.0.0/8",
      "172.16.0.0/12",
      "192.168.0.0/16",
      "100.64.0.0/10"
    ]
  }
}
```

- `100.64.0.0/10` = Tailscale CGNAT range. Add if you want Tailscale hostname access later.
- If you add a Tailscale origin (e.g. `http://daedalus.tail12345.ts.net:18789`), add it to `allowedOrigins` too.
- **Do not** use `dangerouslyAllowHostHeaderOriginFallback: true` except for one-off debugging.

**Verify:** Open `http://127.0.0.1:18789/` from Apollo. Debug tab should show Health: green.

Known blockers: [NVIDIA/NemoClaw#739](https://github.com/NVIDIA/NemoClaw/issues/739),
[#759](https://github.com/NVIDIA/NemoClaw/issues/759) — `openclaw.json` is root-owned.
Workaround you already applied:
```bash
docker exec openshell-cluster-nemoclaw kubectl exec -n openshell my-assistant -- \
  chown -R sandbox:sandbox /sandbox/.openclaw /sandbox/.openclaw-data
```

---

## Phase 2: Align Ollama Inference (Zeus Ollama on 11435)

**Current layout:** one Ollama — **zeus-ollama** on host port **11435**. There is no separate host
daemon on `11434` unless you install it; `ollama list` on the host may be talking to
`OLLAMA_HOST` pointing at 11435.

### DNS vs LAN IP gotchas

- **`host.openshell.internal`** resolves **inside the sandbox**. `openshell inference set` runs
  endpoint verification from the **host**, where that name often does not resolve — verification
  can time out even when inference works from the sandbox.
- Use the daedalus **LAN IP** in `OPENAI_BASE_URL` for provider create (example below), or pass
  **`--no-verify`** to `openshell inference set` if verification fails spuriously.

### Working pattern (substitute your LAN IP)

```bash
# LAN IP of daedalus (example: 192.168.50.128)
hostname -I | awk '{print $1}'

openshell provider delete ollama-local 2>/dev/null || true

openshell provider create \
  --name ollama-local \
  --type openai \
  --credential OPENAI_API_KEY=unused \
  --config OPENAI_BASE_URL=http://192.168.50.128:11435/v1

openshell inference set --provider ollama-local --model qwen2.5:7b-instruct --no-verify
```

Confirm Ollama from the host:

```bash
curl -s http://192.168.50.128:11435/v1/models
ollama pull qwen2.5:7b-instruct   # if missing
```

Check gateway routing:

```bash
openshell inference get
# Expect: Route inference.local → provider ollama-local → qwen2.5:7b-instruct
```

`nemoclaw my-assistant status` may still show **unknown** model/provider — gateway routing is what
matters. See [NemoClaw#759](https://github.com/NVIDIA/NemoClaw/issues/759).

If the sandbox gets **403** to `host.openshell.internal:11435`, apply **Phase 5** custom policy
(`allowed_ips` for Docker bridge).

**Optional:** delete `ollama-local` and recreate the same URL under `--name zeus-ollama` for naming
alignment with the container.

**VRAM note:** If you later run a **second** Ollama on 11434, two daemons on a 10GB card can cause
OOM or churn; prefer one Ollama or stagger workloads.

---

## Phase 2b: OpenClaw `api` field (Ollama vs Responses API)

OpenClaw **2026.3.x** may set `models.providers.inference.api` to **`openai-responses`**. That
makes the gateway use **`POST /v1/responses`**. **Ollama does not implement the Responses API** —
only **`/v1/chat/completions`** — so requests **time out** and logs show
`path=/v1/responses` / `upstream unavailable`.

**Fix:** In `/sandbox/.openclaw/openclaw.json`, set:

```json
"models": {
  "providers": {
    "inference": {
      "api": "openai-completions"
    }
  }
}
```

(Adjust nesting to match your file — key path is `models.providers.inference.api`.)

**Valid `api` values** (OpenClaw gateway; use exact strings):

`openai-completions` · `openai-responses` · `openai-codex-responses` · `anthropic-messages` ·
`google-generative-ai` · `github-copilot` · `bedrock-converse-stream` · `ollama`

For Ollama behind an OpenAI-compatible base URL, use **`openai-completions`** or **`ollama`**.

**Do not** set `"api": "openai"` alone — validation expects one of the strings above.

**Patch in sandbox** (`nemoclaw my-assistant connect`):

```bash
python3 -c "
import json
p = '/sandbox/.openclaw/openclaw.json'
with open(p) as f:
    cfg = json.load(f)
cfg['models']['providers']['inference']['api'] = 'openai-completions'
with open(p, 'w') as f:
    json.dump(cfg, f, indent=2)
print('api ->', cfg['models']['providers']['inference']['api'])
"
```

**Restart OpenClaw gateway inside the sandbox** (paths may vary by image):

```bash
pkill -f 'openclaw' 2>/dev/null; sleep 2
HOME=/sandbox nohup openclaw gateway run > /tmp/gateway.log 2>&1 &
sleep 3
curl -s http://127.0.0.1:18789/health && echo ' OK'
```

**Verify in logs:** sandbox proxy should show `path=/v1/chat/completions`, not `/v1/responses`.

---

## Phase 3: OpenClaw Control UI Quick Reference

Access: `http://127.0.0.1:18789/` (append `#token=<value>` if first session).

| Tab | Purpose | Key Actions |
|---|---|---|
| Chat | Talk to sandboxed agent | Test inference, `/nemoclaw status` slash command |
| Overview | System snapshot | Uptime, gateway info, quick health |
| Instances | Connected devices | Browser session, paired nodes |
| Sessions | Active sessions | Per-session verbose/thinking overrides, delete (no confirm!) |
| Channels | WhatsApp/Telegram/Discord | QR login, per-channel config (skip if not using messaging) |
| Config | Edit `openclaw.json` | **Set allowedOrigins here** — hit Save, verify in Debug |
| Cron Jobs | Scheduled tasks | Add/run/enable/disable, run history |
| Skills | OpenClaw skills | Enable/disable, install from ClaHub |
| Nodes | Device nodes | Mobile pairing, capabilities |
| Debug | Health + events | Status snapshots, manual RPC calls, inference test |
| Logs | Gateway log tail | Filter, export — watch for policy denials and EACCES |

---

## Phase 4: exec-approvals.json

Located at `/sandbox/.openclaw/exec-approvals.json`.

Two config surfaces control exec gating (must agree):
- `approvals.exec` in `openclaw.json`
- `exec-approvals.json` standalone file

For full auto-approval:
```json
{"security": "full", "ask": "off"}
```

Ref: [openclaw/openclaw#15047](https://github.com/openclaw/openclaw/issues/15047)

---

## Phase 5: Network Policies

### View current policies

```bash
nemoclaw my-assistant policy-list
```

### Add preset interactively

```bash
nemoclaw my-assistant policy-add
```

### Custom policy YAML for Zeus LAN services

Save as `~/.nemoclaw/policy-zeus.yaml` on daedalus, then apply:

```yaml
---
version: 1
network_policies:
  allow_zeus_ollama:
    name: allow_zeus_ollama
    endpoints:
      - host: host.openshell.internal
        port: 11435
        allowed_ips:
          - 172.17.0.1
    binaries:
      - path: /usr/bin/node

  allow_zeus_core:
    name: allow_zeus_core
    endpoints:
      - host: host.openshell.internal
        port: 8203
        allowed_ips:
          - 172.17.0.1
    binaries:
      - path: /usr/bin/node
      - path: /usr/bin/curl
```

Apply dynamically (no restart):
```bash
openshell policy set my-assistant --policy ~/.nemoclaw/policy-zeus.yaml --wait
```

For static changes, edit `nemoclaw-blueprint/policies/openclaw-sandbox.yaml` and re-onboard.

The `allowed_ips: [172.17.0.1]` (Docker bridge) is critical — without it the sandbox gets 403.
Credit: [WilliamD's DGX Spark playbook](https://forums.developer.nvidia.com/t/openshell-openclaw-sglang-comfyui/364781).

npm policy deny fix: the `npm_registry` preset only allows `openclaw` and `npm` binaries.
If `node` or `nemoclaw-start` triggers the request, it's denied. Known issue:
[NVIDIA/NemoClaw#19](https://github.com/NVIDIA/NemoClaw/issues/19).

---

## Phase 5 Validation Outcome

Fill in after running the steps above. Use `docker network inspect bridge` to find bridge IP.

- Docker bridge IP on daedalus: **`<fill in>`** (expected: `172.17.0.1`)
- Policy file written to: `~/.nemoclaw/policy-zeus.yaml`
- Applied with: `openshell policy set my-assistant --policy ~/.nemoclaw/policy-zeus.yaml --wait`
- `nemoclaw my-assistant policy-list` shows `allow_zeus_ollama` and `allow_zeus_core`: ✅ / ❌
- `curl http://host.openshell.internal:11435/v1/models` from sandbox returns 200: ✅ / ❌
- `curl http://host.openshell.internal:8203/health` from sandbox returns 200: ✅ / ❌
- No 403 entries in `nemo-logs` after apply: ✅ / ❌

---

## Phase 6: Comprehensive Backup

Use the `nemo-backup` function defined in the aliases section above.

What persists across sandbox **restarts** (PVC-backed):
- `/sandbox/.openclaw/workspace/`
- `/sandbox/.openclaw-data/`

What dies on `nemoclaw destroy`: **everything**.

Known bug: `openshell sandbox upload` may fail (SSH tar exit 255). Workaround:
```bash
cat "$src" | docker exec -i openshell-cluster-nemoclaw \
  kubectl exec -i -n openshell my-assistant -- \
  su -s /bin/bash sandbox -c "cat > ${dst}"
```

### Phase 6 Backup — First Run Notes

Fill in after running `nemo-backup`. Non-fatal failures (empty dirs) are expected on first run.

| File / Dir | Status |
|---|---|
| `openclaw.json` | ✅ / ❌ |
| `workspace/` | ✅ / ❌ (or: SSH tar 255 → used kubectl pipe) |
| `memory/main.sqlite` | ✅ / ❌ (missing if no memory yet — non-fatal) |
| `credentials/` | ✅ / ❌ (empty — non-fatal) |
| `devices/` | ✅ / ❌ (empty if no paired devices — non-fatal) |
| `policy_active.yaml` | ✅ / ❌ (fallback: `nemoclaw my-assistant policy-list > policy_active.yaml`) |

Backup location: `~/.nemoclaw/backups/<timestamp>/`

---

## Phase 7: Zeus Aegis vs NemoClaw Mental Model

| Layer | What It Does | Where It Runs | Config |
|---|---|---|---|
| Zeus Aegis | Regex rules on LLM output content | In-process (Zeus Core) | `zeus/safety/policies/*.yaml`, `ZEUS_AEGIS_ENABLED=1` |
| NemoClaw/OpenShell | OS-level sandbox (Landlock, seccomp, netns) | daedalus host | `openclaw-sandbox.yaml`, `openshell policy set` |

No overlap: Aegis filters *what the LLM says*; NemoClaw restricts *what the agent can do*.
Future bridge: `NEMOCLAW_RUNTIME_URL` env var reserved in `compose.yaml` line 97.

---

## Context Budget Warning

OpenClaw's ecosystem (workspace markdown + system prompts) consumes ~16K tokens.
`qwen2.5:7b-instruct` has limited effective context compared to 120B+ models.

Recommendations:
- Keep SOUL.md, IDENTITY.md, AGENTS.md lean (2-3 paragraphs each).
- Avoid `--light-context` on cron jobs that need tool/skill access.
- Complex multi-skill cron jobs may not work reliably at 7B model size.
- Consider upgrading to a 14B+ model if sandbox agent tasks grow in complexity.
  On a 3080 (10GB), `qwen2.5:14b-instruct-q4_k_m` requires unloading `nomic-embed-text` first
  (`OLLAMA_MAX_LOADED_MODELS=1`). Try this before expanding SOUL/IDENTITY/AGENTS.

Slim templates for SOUL.md, IDENTITY.md, and AGENTS.md are in `zeus/safety/workspace-templates/`
(~350 tokens total vs ~16K default). Upload with `openshell sandbox upload` or the kubectl pipe
workaround (see Phase 6 above). After upload, restart the OpenClaw gateway inside the sandbox and
run a quick chat test ("what model are you?") to confirm context reduction is working.

---

## Troubleshooting Checklist

When Health goes offline or WebSocket disconnects:

1. `nemo-status` — check sandbox state
2. `nemo-term` — OpenShell TUI, look for errors
3. `nemo-fwdlist` — verify port forward is active
4. Check SSH tunnel is alive on Apollo
5. Browser DevTools → Network → WS tab → look for disconnects
6. Re-establish forward: `nemo-fwd`
7. After machine reboot: sandbox may need re-registration
   ([NVIDIA/NemoClaw#486](https://github.com/NVIDIA/NemoClaw/issues/486))
8. If `nemoclaw logs` fails: `openshell logs my-assistant --tail`

### Token / Auth

- Retrieve gateway token: check `~/.nemoclaw/` on daedalus or
  `openshell gateway token`
- Token rotation: destroy + re-onboard (no standalone command in alpha)
- Never expose `#token=...` URL via Cloudflare Tunnel without Zero Trust

### Sandbox Permissions

If `EACCES` errors return:
```bash
docker exec openshell-cluster-nemoclaw kubectl exec -n openshell my-assistant -- \
  chown -R sandbox:sandbox /sandbox/.openclaw /sandbox/.openclaw-data
```

### Python in Sandbox

- `urllib.request` is **blocked** — use `subprocess.run(["curl", ...])` instead
- Provider env vars are NOT expanded inside the sandbox — inject secrets as files
- Variables don't persist between separate `exec bash` calls — read inline with `$(cat file)`

### Inference routing to wrong endpoint

- **Symptom:** OpenShell sandbox logs show `POST ... path=/v1/responses` and
  `upstream unavailable: request to http://.../v1/responses timed out`; Chat may show empty
  assistant text or tools that “complete” with no payload.
- **Cause:** `openclaw.json` has `"api": "openai-responses"` while the backend is Ollama (no
  Responses API).
- **Fix:** Set `models.providers.inference.api` to **`openai-completions`** (or **`ollama`**),
  restart the OpenClaw gateway — see **Phase 2b**.

### TLS handshake EOF on `inference.local`

- **Symptom:** `Inference interception denied ... host=inference.local reason=TLS handshake failed: tls handshake eof`
- **Cause:** After HTTP failures or mis-routing, a client may attempt **HTTPS** to an endpoint that
  only speaks **plain HTTP** (Ollama).
- **Fix:** Correct the **`api`** field (Phase 2b) so `/v1/chat/completions` succeeds; ensure
  provider base URL is **`http://.../v1`** not `https://` for local Ollama.

---

## Alpha Caveats (NemoClaw 0.0.16+, Mar 2026)

- `openclaw.json` root-owned permissions: [#759](https://github.com/NVIDIA/NemoClaw/issues/759)
- OpenClaw version pinned in Dockerfile: [#739](https://github.com/NVIDIA/NemoClaw/issues/739)
- `nemoclaw logs` may not work: [#253](https://github.com/NVIDIA/NemoClaw/issues/253)
- `dangerouslyDisableDeviceAuth` reverse proxy bug: [#563](https://github.com/NVIDIA/NemoClaw/issues/563)
- `openshell sandbox upload` SSH tar exit 255 — use kubectl stdin pipe
- No standalone token rotation command
- Session corruption with consecutive user messages (no assistant reply between them)

---

## Next session — continuation prompt (copy-paste)

Use this to resume NemoClaw / OpenClaw work in a new chat. Repo: **zeus** on daedalus; runbook:
**`docs/nemoclaw-ops.md`** (this file).

```
You are helping me continue Zeus + NemoClaw/OpenClaw on daedalus (RTX 3080).

Context already done (see zeus/docs/nemoclaw-ops.md):
- Single Ollama: zeus-ollama on host port 11435; OpenShell provider (e.g. ollama-local) uses LAN IP + --no-verify where needed.
- openclaw.json models.providers.inference.api set to openai-completions (not openai-responses) for Ollama.
- allowedOrigins for Control UI; SSH tunnel from Apollo (18789, 18080).

Continue with this plan:
1. Confirm gateway.trustedProxies CIDRs in openclaw.json match how we access the UI (LAN, Tailscale) and add any missing allowedOrigins if we use non-localhost hostnames.
2. Apply and validate Phase 5 custom network policy (~/.nemoclaw/policy-zeus.yaml) for host.openshell.internal:11435 and :8203; adjust allowed_ips if Docker bridge is not 172.17.0.1.
3. Run a first real backup using the nemo-backup shell function; note any download failures and document workarounds.
4. Context budget: trim OpenClaw workspace markdown (SOUL.md, IDENTITY.md, AGENTS.md, etc.) so qwen2.5:7b-instruct behaves less tool-happy and stays within effective context; optional model upgrade notes.
5. Optional cleanup: rename OpenShell provider from ollama-local to zeus-ollama (delete/recreate) without breaking inference route.
6. Agent quality pass: simple chat (“what model are you?”) vs tool-heavy behavior; Web Search / tool output empty — decide if policy, skill, or model limits.

Use the repo and nemoclaw-ops.md; do not run git commands for me (give me commands to run).
```

---

## References

- [NVIDIA NemoClaw Commands](https://docs.nvidia.com/nemoclaw/latest/reference/commands.html)
- [NVIDIA NemoClaw Network Policies](https://docs.nvidia.com/nemoclaw/latest/reference/network-policies.html)
- [NVIDIA NemoClaw Backup/Restore](https://docs.nvidia.com/nemoclaw/latest/workspace/backup-restore.html)
- [NVIDIA NemoClaw Monitoring](https://docs.nvidia.com/nemoclaw/latest/monitoring/monitor-sandbox-activity.html)
- [NVIDIA NemoClaw Switch Inference](https://docs.nvidia.com/nemoclaw/latest/inference/switch-inference-providers.html)
- [WilliamD DGX Spark Playbook (NVIDIA Forums)](https://forums.developer.nvidia.com/t/openshell-openclaw-sglang-comfyui/364781)
- [NemoClaw#739 — allowedOrigins + Dockerfile pin](https://github.com/NVIDIA/NemoClaw/issues/739)
- [NemoClaw#759 — openclaw.json permissions](https://github.com/NVIDIA/NemoClaw/issues/759)
- [OpenClaw Control UI Audit](https://github.com/openclaw/openclaw/issues/38420)
