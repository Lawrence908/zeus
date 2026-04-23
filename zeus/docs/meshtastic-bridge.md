# Zeus Meshtastic Bridge

## Goal

Let the user talk to Zeus over LoRa mesh from field devices (phone, tablet, standalone Meshtastic nodes) by bridging a Meshtastic gateway radio to the `/chat/message` endpoint through MQTT + Node-RED. Works off-grid as long as a mesh-reachable gateway is online.

## User Stories

- As the user in the field with no cell service, I can send a text message on a private mesh channel and get a Zeus reply back on the same channel.
- As the user, my field conversations share session continuity per originating node so Zeus has memory across turns.
- As the homelab operator, Zeus never reacts to random LongFast traffic from strangers; only allowlisted senders on the private channel reach the LLM.

## Architecture

```
┌──────────────┐    LoRa (915 MHz)    ┌──────────────────────────┐
│  Mesh nodes  │◄────────────────────►│  Heltec V3 (!9e9f3224)   │
│ (phone/tabs/ │                      │  192.168.50.170          │
│  other radios│                      │  USB-powered on atlas    │
└──────────────┘                      └────────────┬─────────────┘
                                                   │ WiFi 2.4 GHz
                                                   │ (TiNi WiFi)
                                                   │
                                                   ▼ MQTT
                      ┌────────────────────────────────────────────────┐
                      │ daedalus (192.168.50.128) — homelab-web docker │
                      │                                                │
                      │  mqtt-broker (:8150 LAN / :1883 internal)      │
                      │    user "meshtastic" receives mesh traffic     │
                      │    user "homeassistant" reads msh/ + publishes │
                      │    user "nodered" reads msh/ + pub/sub sensors │
                      │                                                │
                      │         ▲                       ▲              │
                      │         │                       │              │
                      │         ▼                       ▼              │
                      │  ┌─────────────┐       ┌─────────────────┐    │
                      │  │ Home        │       │ Node-RED        │    │
                      │  │ Assistant   │       │ (:8155)         │    │
                      │  │ (:8154)     │       │                 │    │
                      │  │ core MQTT   │       │ mqtt in flows   │    │
                      │  └─────────────┘       └────────┬────────┘    │
                      │                                 │              │
                      │                                 ▼              │
                      │                        ┌────────────────┐      │
                      │                        │ Zeus Core      │      │
                      │                        │ (:8203 planned)│      │
                      │                        └────────────────┘      │
                      └────────────────────────────────────────────────┘

                      
Mesh device  --LoRa-->  Gateway radio  --WiFi-->  mqtt-broker
(phone/tablet)         (Heltec V3)               (homelab-web)
                                                     |
                                                     | sub: msh/+/2/json/zeus/+
                                                     v
                                                 Node-RED
                                                 filter + transform
                                                     |
                                                     | POST /chat/message
                                                     v
                                                 zeus-core:8000
                                                 (Aegis + QueryEngine)
                                                     |
                                                     | assistant_message
                                                     v
                                                 Node-RED
                                                 chunk + transform
                                                     |
                                                     | pub: msh/US/2/json/mqtt/!<gateway>
                                                     v
                                                 mqtt-broker
                                                     |
                                                     | gateway downlinks to LoRa
                                                     v
                                                 Mesh device receives reply
```

Gateway radio, broker, Node-RED, and zeus-core all live on the `homelab-web` Docker network on the daedalus host. The gateway radio is the only component that touches the LoRa physical layer.

## Topics

Meshtastic 2.7 publishes on `msh/<region>/<version>/<encoding>/<channel>/<senderNodeId>`.

| Topic pattern                              | Direction | Purpose                            |
|--------------------------------------------|-----------|------------------------------------|
| `msh/+/2/json/zeus/+`                      | inbound   | Private-channel JSON frames, subscribed by Node-RED |
| `msh/+/2/e/zeus/+`                         | inbound   | Encrypted protobuf, ignored by Node-RED |
| `msh/+/2/json/mqtt/!<gateway_node_id>`     | outbound  | JSON downlink sent by Node-RED, transmitted to LoRa by the gateway |

Only the `zeus` channel is bridged to the LLM. LongFast stays public and is not forwarded.

## Session Convention

Session id follows the Telegram precedent: `meshtastic:<from_node_num>`. One session per originating node means memory persists across turns from the same device but does not bleed between users on the same channel. Matches the pattern in `zeus/integrations/telegram/bot.py`.

Example: a phone publishing `payload.from = 2661166808` maps to session `meshtastic:2661166808`.

## Node-RED Flow Contract

Node-RED is the bridge runtime. It does four things in order:

1. Subscribe to `msh/+/2/json/zeus/+` with user `nodered`
2. Filter to text messages from allowlisted senders
3. Call `POST http://zeus-core:8000/chat/message`
4. Publish the `assistant_message` back as an MQTT JSON downlink

### Filter rules

- Drop unless `payload.payload.type === "text"` (skip nodeinfo, telemetry, routing)
- Drop unless `payload.payload.from` is in the allowlist env var
- Optional: drop if `payload.payload.to` is not broadcast and is not the gateway node id

### Request mapping (Node-RED `http request` node)

```json
{
  "session_id": "meshtastic:<from_node_num>",
  "message": "<payload.payload.payload.text>",
  "max_tokens": 180,
  "use_context": true
}
```

`max_tokens: 180` keeps the Zeus reply under the 234-byte LoRa packet limit after UTF-8 encoding. Responses longer than one LoRa packet are not currently chunked; future work in the backlog.

### Response mapping

Extract `assistant_message` from the response body. Truncate to 230 bytes. Publish to topic `msh/US/2/json/mqtt/!9e9f3224` with payload:

```json
{
  "from": 2661233188,
  "type": "sendtext",
  "payload": "<reply text>",
  "channel": 1
}
```

`channel: 1` is the `zeus` private channel index. `from` is the gateway radio's node num in decimal.

## Aegis

Aegis runs on the zeus-core side of the boundary via `aegis_bus_post_hook` inside `QueryEngine`. The Meshtastic source is passed as `source="meshtastic"` so the query log distinguishes mesh traffic from chat, voice, and telegram.

Node-RED itself does not run Aegis. The allowlist is the only gatekeeper on the bridge side, and it exists to prevent random LongFast traffic from reaching the LLM at all rather than to do content filtering.

If Aegis blocks a reply, the response comes back with `aegis_flags` populated and `assistant_message` already filtered by the core, matching Telegram behavior.

## Security Model

- **Broker** is LAN-only, auth required. Five users in the mosquitto ACL, each scoped to only the topics they need.
- **Private channel** uses a 32-byte AES256 PSK generated on the gateway radio and imported on each trusted mesh device as a QR/URL. Anyone without the PSK cannot decrypt zeus-channel traffic, even in radio range.
- **Sender allowlist** lives in Node-RED env config and is the authoritative decision for which `from` node nums trigger Zeus. Add a node num here when onboarding a new device.
- **Aegis policy** is selected via `ZEUS_AEGIS_POLICY` (or per-source override if added later).
- **No downlink amplification**: Node-RED only publishes in response to allowlisted inbound messages. No autonomous broadcast.

## Operational Notes

- Gateway radio must be on WiFi with `network.wifi_enabled=True`. ESP32-S3 chips only see 2.4 GHz SSIDs. Verify via `meshtastic --port /dev/ttyUSB0 --get network.wifi_enabled`.
- Downlink requires `downlink_enabled=True` on the target channel. Without it, MQTT-to-LoRa packets are dropped silently.
- LoRa packet size ceiling is ~234 bytes of text; plan reply length accordingly.
- Region must be set on the gateway radio or LoRa TX is disabled and no downlink reaches the mesh.
- Homelab operator keeps the gateway radio on USB power at the daedalus host; a disconnected battery is fine as long as USB is reliable.

## Out of Scope

- **Multi-chunk replies.** Zeus replies longer than a single LoRa packet get truncated by Node-RED. Chunking with reassembly markers is a backlog item.
- **Public mesh access.** LongFast is intentionally not bridged. A new channel plus explicit allowlist entries would be required to expand access.
- **Voice on mesh.** Orpheus stays on the homelab network. Mesh is text only.
- **In-process bot.** A native `zeus/integrations/meshtastic/bot.py` that parallels the Telegram bot would remove the Node-RED hop and give tighter session + Aegis integration. Deferred until the bridge proves its value in field use.

## Related

- [chat-interface-spec.md](chat-interface-spec.md): the `/chat/message` endpoint this bridge calls.
- [sessions-spec.md](sessions-spec.md): session id rules and packing; the `meshtastic:<num>` convention follows these.
- `zeus/integrations/telegram/bot.py`: precedent for a text interface bridging into `QueryEngine` with a per-chat session and Aegis policy hook.
- `/mnt/storage/apps/meshtastic-mqtt/INTEGRATION_PLAN.md` on the daedalus host: broker + gateway + channel ops documentation, credentials, and verification commands.
