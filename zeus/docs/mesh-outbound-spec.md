# Zeus Mesh Outbound + Break-Glass Spec

Covers two capabilities that share one primitive:

1. **Proactive push** — Kairos originates alerts *to* the mesh (inverts today's request/reply).
2. **Break-glass management** — you text a command from a field device and drive the homelab over LoRa when WAN/cell is down.

Companion to [meshtastic-bridge.md](meshtastic-bridge.md) (the existing inbound chat bridge). This doc adds the *outbound* and *command* directions. Ops/backlog context lives in `/mnt/storage/apps/meshtastic-mqtt/ROADMAP.md`.

## Why one spec

Today the only way a packet leaves the gateway is as a *reply* to inbound chat: Node-RED → `meshtastic-sender:/send`. Both new features need Zeus to originate or command traffic that was **not** solicited by an inbound chat turn. They share:

- the same radio driver (`meshtastic-sender`),
- the same 200-byte chunking + `wantAck` reliability concerns,
- the same need for Aegis on mesh text, rate limiting, dedupe, quiet hours, and an audit trail.

So we build **one hardened choke point** and give it two callers, rather than two parallel pipes. The existing security-model rule "No downlink amplification / no autonomous broadcast" is deliberately relaxed here behind explicit, default-off gates.

## Architecture

```
                          ┌────────────────────────── zeus-core (:8203) ──────────────────────────┐
                          │                                                                        │
  Kairos observers ──────►│  ┌──────────────┐   POST /mesh/notify   ┌───────────────────────────┐  │
  (health/cal/news)       │  │ mesh_notify  │──────────────────────►│  MeshOutbound (mesh.py)    │  │
                          │  │ Kairos tool  │                        │  - ZEUS_MESH_OUTBOUND gate │  │
                          │  └──────────────┘                        │  - Aegis (meshtastic pol.) │  │
                          │                                          │  - token-bucket rate limit │  │
  inbound !command  ─────►│  Node-RED command router                 │  - dedupe window           │  │
  (from mesh, via NR) ───►│  ── POST /mesh/command ──► CommandExec ──►│  - quiet hours / priority  │  │
                          │       (LLM-free, READ-ONLY grammar)      │  - chunk + wantAck         │  │
                          │       - !status / !ping / !svc / !help   └─────────────┬─────────────┘  │
                          │                                                        │                │
                          └──────────────────────────────────────────────────────┼────────────────┘
                                                                                  │ POST /send
                                                                                  ▼
                                                              meshtastic-sender (dumb TCP driver)
                                                                    │ wantAck=True
                                                                    ▼  TCPInterface → Heltec V3 → LoRa
```

**Design rule: all policy lives in zeus-core; the sender stays a dumb driver.** Aegis, dedupe state, quiet hours, rate limits, and the audit DB already have a home in Zeus. The sender only learns two new things: `wantAck` and a `/status` endpoint.

---

## Component 1 — MeshOutbound choke point (`zeus/core/mesh.py`)

New FastAPI module mounted on the bus. **The only code allowed to send unsolicited/commanded mesh traffic.** Node-RED's existing reply path stays as-is for normal chat; everything new routes here.

`POST /mesh/notify`

```json
{
  "text": "olympus GPU 92C, throttling",
  "channel": 1,
  "destination": null,          // null = channel broadcast; node-num = PKI DM (phase 5)
  "priority": "critical",       // "low" | "normal" | "critical"
  "dedupe_key": "health:gpu_temp",
  "source": "kairos"            // "kairos" | "command" | "manual"
}
```

Enforcement pipeline (in order, fail-closed):

1. **Master gate** — `ZEUS_MESH_OUTBOUND_ENABLED` (default `0`). Off = 403. This is the deliberate flip of the "no autonomous broadcast" rule.
2. **Aegis** — `evaluate_text()` under the new `meshtastic` policy. Rejection returns filtered text + `aegis_flags`, mirroring Telegram.
3. **Quiet hours** — `ZEUS_MESH_QUIET_HOURS` (e.g. `22:00-07:00`, local). `low`/`normal` are dropped-and-logged (or queued to next window); `critical` always passes.
4. **Rate limit** — global + per-source token bucket (`ZEUS_MESH_RATE_PER_MIN`, `ZEUS_MESH_RATE_BURST`). Protects LoRa duty cycle. `critical` draws from a reserved burst allowance.
5. **Dedupe** — if `dedupe_key` fired within `ZEUS_MESH_DEDUPE_MIN` (default 30) and the payload signature is unchanged, drop. This is what stops a persistent condition ("GPU hot") from re-firing every 60s Kairos cycle.
6. **Chunk** — reuse the 200-byte rule + `[N/M]` prefix from the existing chunker.
7. **Send** — `POST meshtastic-sender:/send` with `wantAck=True`.
8. **Audit** — one row to `zeus/data/mesh.db` regardless of outcome (sent / deduped / quiet / rejected).

Returns `{ok, delivered, reason, chunks}`.

---

## Component 2 — Kairos proactive push

### New observers (`zeus/orchestration/daemon.py`)
Follow the existing `ObservationSource` protocol. Each emits an `Observation` with a severity hint in `raw`:

- `ServerHealthObserver` — polls `/admin/system`; flags GPU temp, disk %, or a down container past threshold.
- `CalendarObserver` — event starting within N minutes (uses `/calendar/today`).
- `NewsletterObserver` — new digest ready (uses existing `zeus_newsletter_latest` dispatch).

Extensible; add a swarm-run observer later once you want run-status on mesh.

### New Kairos tool: `mesh_notify`
This is the sensitive part. Kairos' default allowlist is **read-only**; `mesh_notify` writes to the radio. Per the [Agentic Safety Contract](../../CLAUDE.md#agentic-safety-contract), widening the allowlist needs a safety note — **this section is that note.**

Gating (all must be true):
- `ZEUS_MESH_OUTBOUND_ENABLED=1` (choke point live)
- `ZEUS_KAIROS_MESH_NOTIFY=1` (Kairos specifically may push)
- `mesh_notify` present in `ZEUS_KAIROS_TOOL_ALLOWLIST`

Dispatch: a `mesh_notify` branch in `KairosAgent._dispatch` that maps observation severity → `priority`, sets `dedupe_key = f"{obs.source}:{signature}"`, and POSTs `/mesh/notify` with `source="kairos"`. The Aegis pre-hook already runs on the tool args before dispatch (existing code path), and the choke point runs Aegis on the *text* again — two layers.

**Why no flood is possible:** even a runaway plan can't spam the mesh because dedupe + rate-limit + quiet-hours all live *downstream* in the choke point, not in Kairos. Kairos can *ask* to send every cycle; the choke point decides.

---

## Component 3 — Break-glass management

The out-of-band control channel for when the normal path (WAN, cell, wifi) is dead. **Key property: the command path must not depend on the internet or the chat LLM** — it's deterministic parsing + local HTTP to Core, so it works during an ISP outage even though `ZEUS_ENV=dev` chat would be unreachable.

### Node-RED command router (before the Zeus chat path)
Classify inbound mesh text:
- Starts with `!` → **command** → `POST /mesh/command` (LLM-free).
- Otherwise → existing Zeus chat path (unchanged).

### `POST /mesh/command` (`zeus/core/mesh.py`)
Small fixed grammar, **read-only only**. No mutation path exists — the command handler can observe the homelab but cannot change it. This is the deliberate safety choice: even a fully compromised channel yields nothing but read access you already gate behind the PSK + sender allowlist.

| Command | Action | Source |
|---|---|---|
| `!status` | summarize `/admin/system` + sender `/status` + key container health | read |
| `!ping <host>` | reachability of a homelab host | read |
| `!svc <name>` | is a named service up | read |
| `!help` | list commands | static |

Any `!`-command that isn't in this table returns `!help` rather than falling through to anything mutating. There is no `!restart`, no action-runner call, no shell — that tier is explicitly **not pursued** (see Out of scope).

Replies route back out through `/mesh/notify` with `source="command"`, `priority="normal"` (solicited → bypasses quiet hours), fully audited.

### Node-RED command router (to wire in the UI)
The router lives in the Node-RED flow (not the repo). Contract for phase 3:

1. On the existing `msh/+/2/json/zeus/+` inbound subscription, add a `switch`/`function` node **before** the Zeus chat path.
2. If `payload.payload.text` (trimmed) starts with `!` → route to command, else → existing chat path (unchanged).
3. Command branch: `POST http://zeus-core:8000/mesh/command` with
   ```json
   { "text": "<inbound text>", "sender_node": <payload.payload.from> }
   ```
4. Core computes the reply and sends it back through `/mesh/notify` itself, so the command branch is **fire-and-forget** — Node-RED does not need to publish the reply. The HTTP response `{command, reply, delivered, reason}` is for logging only.

Because Core owns the reply send, the whole break-glass path depends on nothing but Core + the sender being up — no internet, no LLM.

### Command env
```
ZEUS_MESH_PING_ALLOWLIST=          # extra hostnames/IPs !ping may reach (private/loopback always allowed)
```
`!svc` needs docker visibility from the zeus-core container to be useful (mounts the docker socket / CLI); without it, it honestly reports "no docker visibility from core".

### Out of scope
- **Mutating commands over mesh** (`!restart`, service toggles, host wake). Deliberately dropped for the safest read-only posture. Revisit only with a fresh safety review if a concrete need appears; it would require its own env gate, `confirm` token, curated action allowlist, and audit before reconsideration.
- **`!ping` as ICMP.** Implemented as a TCP-connect reachability probe (default port 22) — better "is it up" signal in a homelab and needs no raw-socket privilege.

---

## Shared plumbing

### Mesh Aegis policy (`zeus/safety/policies/meshtastic.yaml`)
Backlog item Z2. Stricter than `standard`: aggressive prompt-injection rejection, never permits write-tool arguments, applied to **both** inbound mesh text and outbound notify text.

### Audit DB (`zeus/data/mesh.db`)
Backlog item O3. One table: `ts, direction (in/out), source, sender_node, text, priority, delivered, reason, aegis_flags`. Covers proactive pushes and every command. Feeds a future Grafana panel (O1).

### Sender changes (`meshtastic-sender/app.py`)
- `wantAck=True` on `sendText` (backlog R1) — biggest single reliability win, and these messages matter more than casual chat.
- `GET /status` (backlog O2) — `!status` needs radio reachability + last-TX.
- Stays a dumb driver otherwise.

### Config surface (all default-off / conservative)
```
ZEUS_MESH_OUTBOUND_ENABLED=0      # master outbound gate (push + command replies)
ZEUS_KAIROS_MESH_NOTIFY=0         # Kairos may push
ZEUS_MESH_QUIET_HOURS=22:00-07:00 # low/normal suppressed; critical always
ZEUS_MESH_RATE_PER_MIN=6
ZEUS_MESH_RATE_BURST=3
ZEUS_MESH_DEDUPE_MIN=30
```

Note: `/mesh/command` is read-only and needs only `ZEUS_MESH_OUTBOUND_ENABLED` (so its replies can reach the radio). There is no admin/mutation gate because there is no mutation path.

---

## Rollout phases

| Phase | Scope | Proves |
|---|---|---|
| 1 | Sender `wantAck` + `/status`; `meshtastic.yaml` policy; `mesh.db`; `/mesh/notify` choke point (no callers) — curl-tested | The primitive is safe in isolation |
| 2 | `ServerHealthObserver` + `mesh_notify` tool, alert-only, quiet hours on | Proactive push works and does **not** spam over several days |
| 3 | `/mesh/command` read-only (`!status`/`!ping`/`!svc`/`!help`) + Node-RED router | Break-glass read path works internet-free |
| 4 (opt) | PKI direct-message replies (privacy); more observers (calendar/newsletter/swarm) | Per-node private replies; broader alerting |

## Safety summary (per Agentic Safety Contract)

- Two default-off env gates (`ZEUS_MESH_OUTBOUND_ENABLED`, `ZEUS_KAIROS_MESH_NOTIFY`); nothing autonomous ships until you flip them.
- Kairos cannot flood: dedupe + rate-limit + quiet-hours enforced downstream of the agent.
- Aegis runs twice on outbound (tool-arg pre-hook + text at the choke point).
- Break-glass is **read-only** — no mutation path exists over mesh at all, so the blast radius of a compromised channel is bounded to read access already behind the PSK.
- Every inbound command and outbound send lands in `mesh.db`.
- No new inbound trust: the existing PSK channel + Node-RED sender allowlist remain the only entry.

## Decisions (resolved)
- Mutating tier — **read-only only** (no mesh mutation path).
- Quiet hours — **`22:00–07:00`** local; `critical` (server-down / GPU-hot) bypasses.
- Phase-2 alert set — **GPU temp, disk %, container-down.** (UPS/power can be added later if a monitored UPS lands.)

## Related
- [meshtastic-bridge.md](meshtastic-bridge.md) — inbound chat bridge (the other direction).
- [../../CLAUDE.md](../../CLAUDE.md) — Agentic Safety Contract, Kairos, Olympian tool pack.
- `zeus/orchestration/daemon.py` — Kairos observe/decide/act loop this extends.
- `/mnt/storage/apps/meshtastic-mqtt/ROADMAP.md` — ops backlog (R1, Z2, O2, O3 folded in here).
