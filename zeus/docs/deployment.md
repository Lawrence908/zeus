# Deployment Runbook

Deploying Zeus from a dev host to the always-on host. As of April 2026, the always-on host is **daedalus** (RTX 3080, Proxmox VM with ~90–100 GB RAM). **Olympus** (dedicated RTX 3080 server) is the eventual target; the procedure below is the same.

Before deploying: confirm all smoke tests pass locally with `ZEUS_ENV=dev`, and that the retrieval eval (`pytest tests/retrieval_eval.py` or `python -m zeus.memory.eval`) is at or above the baseline (hit@5 ≥ 0.867).

## Environment differences

| | Dev | Prod |
|---|---|---|
| `ZEUS_ENV` | `dev` | `prod` |
| Chat LLM | Claude Sonnet 4.6 via Anthropic API | Ollama `qwen2.5:7b-instruct` |
| Small-LLM chain | Full chain (Gemini paid, Groq, OpenRouter, Haiku, Ollama) | Same; Ollama is the guaranteed local fallback |
| VRAM budget | 16 GB (5080) | 10 GB (3080) |
| Logging | DEBUG, text | INFO, structured |

## VRAM budget on 3080 (10 GB)

| Component | VRAM |
|---|---|
| `qwen2.5:7b-instruct` Q4_K_M | ~5.5 GB |
| `nomic-embed-text:v1.5` | ~0.3 GB |
| WhisperLiveKit large-v3 | ~3.0 GB |
| Activation / KV cache scratch | ~0.3 GB |
| **Total** | **~9.1 GB** |

Margin: ~0.9 GB. Do not load extra chat models concurrently; `OLLAMA_MAX_LOADED_MODELS=2` (one embed + one chat) is the ceiling. See [model-comparison.md](model-comparison.md) for measured tok/s across candidate models.

## Pre-deployment checklist

On the dev host:

- [ ] Unit tests pass.
- [ ] Retrieval eval at or above baseline.
- [ ] Memory-architecture Phase 1 migration completed (or re-confirmed) per [docs/memory-architecture-plan.md](../../docs/memory-architecture-plan.md).
- [ ] `zeus/data/sessions.db` behavior verified if `ZEUS_SESSION_BACKEND=sqlite`.
- [ ] Smoke: `docker compose up qdrant ollama whisper -d && curl -s localhost:8203/status`.
- [ ] `main` branch clean; changes committed and pushed.

## First deploy (daedalus or Olympus)

### 1. Install prerequisites

```bash
sudo apt update
sudo apt install -y git python3.11 python3.11-venv python3-pip \
  portaudio19-dev ffmpeg curl docker.io docker-compose-plugin
sudo usermod -aG docker $USER
```

NVIDIA Container Toolkit (required for Ollama GPU and Whisper GPU):

```bash
curl -fsSL https://nvidia.github.io/libnvidia-container/gpgkey | \
  sudo gpg --dearmor -o /usr/share/keyrings/nvidia-container-toolkit-keyring.gpg
curl -s -L https://nvidia.github.io/libnvidia-container/stable/deb/nvidia-container-toolkit.list | \
  sed 's#deb https://#deb [signed-by=/usr/share/keyrings/nvidia-container-toolkit-keyring.gpg] https://#g' | \
  sudo tee /etc/apt/sources.list.d/nvidia-container-toolkit.list
sudo apt update && sudo apt install -y nvidia-container-toolkit
sudo nvidia-ctk runtime configure --runtime=docker
sudo systemctl restart docker
docker run --rm --gpus all nvidia/cuda:12.0-base nvidia-smi
```

### 2. Clone and configure

```bash
sudo mkdir -p /opt/zeus && sudo chown $USER /opt/zeus
git clone https://github.com/<github-user>/zeus.git /opt/zeus
cd /opt/zeus
cp .env.example .env
nano .env
```

Minimum prod settings in `.env`:

```bash
ZEUS_ENV=prod
ZEUS_LLM=ollama
ZEUS_OLLAMA_MODEL=qwen2.5:7b-instruct
ZEUS_EMBED_MODEL=nomic-embed-text
QDRANT_URL=http://zeus-qdrant:6333
OLLAMA_URL=http://zeus-ollama:11434
ZEUS_KNOWLEDGE_HYBRID=1
ZEUS_KNOWLEDGE_RERANK=0
ZEUS_SESSION_BACKEND=sqlite
# Small-LLM keys as applicable (ANTHROPIC_API_KEY, GOOGLE_API_KEY, GROQ_API_KEY, ...)
```

### 3. Pull models

```bash
docker compose up qdrant ollama -d
docker exec zeus-ollama ollama pull qwen2.5:7b-instruct
docker exec zeus-ollama ollama pull nomic-embed-text:v1.5
docker exec zeus-ollama ollama list
```

### 4. Bring up Zeus Core

```bash
docker compose up -d
docker compose ps
curl -s localhost:8203/status | python3 -m json.tool
```

### 5. First ingest

```bash
# Memory layer (curated profile sources; uses small_llm_call fact extraction)
docker exec zeus-core python -m zeus.ingest.run --target memory

# Knowledge layer (bulk sources; raw embed + Qdrant upsert, no LLM)
docker exec zeus-core python -m zeus.ingest.run --target knowledge
```

Expect `zeus_memories` to land in the 100–500 point range, `zeus_knowledge` in the thousands to tens of thousands. Verify:

```bash
curl -s http://localhost:6333/collections/zeus_memories | jq '.result.points_count'
curl -s http://localhost:6333/collections/zeus_knowledge | jq '.result.points_count'
```

### 6. Smoke

```bash
curl -s -X POST localhost:8203/context/query \
  -H "Content-Type: application/json" \
  -d '{"query":"what am I working on","top_k":3}' | python3 -m json.tool

curl -s -X POST localhost:8203/chat/message \
  -H "Content-Type: application/json" \
  -d '{"session_id":"smoke","message":"summarize my current projects"}' | python3 -m json.tool
```

Run the benchmark suite once on the new host:

```bash
docker exec zeus-core python -m zeus.bench
```

Results land in `zeus/data/benchmarks.json` and are surfaced in the React Settings page.

## Updating

From the dev host, once `main` has the new commit:

```bash
ssh <host>
cd /opt/zeus
git pull origin main
docker compose pull      # if images changed
docker compose up -d --build
curl -s localhost:8203/status | python3 -m json.tool
```

For pure Python edits during iteration, `compose.override.yaml` bind-mounts `./zeus` into `zeus-core` read-only; `docker compose restart zeus-core` is enough. Production hosts should **not** apply the override: deploy a baked image.

## Monitoring

```bash
# Health
curl -s localhost:8203/status | jq
curl -s localhost:8203/admin/metrics | jq

# Logs
docker compose logs -f zeus-core
docker compose logs -f zeus-ollama
docker compose logs -f zeus-qdrant

# VRAM
watch -n 2 nvidia-smi

# Small-LLM spend
sqlite3 zeus/data/small_llm_usage.db \
  "SELECT provider, COUNT(*), ROUND(SUM(cost_usd),4) FROM usage \
   WHERE ts > strftime('%s','now','-1 day') GROUP BY provider;"
```

## Telegram bot

Set in `.env`:

```bash
TELEGRAM_ENABLED=1
TELEGRAM_BOT_TOKEN=<from @BotFather>
TELEGRAM_ALLOWED_CHAT_IDS=<comma-separated chat ids>
TELEGRAM_AEGIS_POLICY=standard
```

The bot starts in the FastAPI lifespan. It can be restarted in place via `PATCH /admin/settings {"telegram": {...}}` from the React Settings page without restarting `zeus-core`.

## Voice pipeline (host-native)

Orpheus needs direct audio device access. Run on the host, not in Docker:

```bash
cd /opt/zeus
source .venv/bin/activate
python -m zeus.voice.pipeline
```

Set `ZEUS_VOICE_STATE_PUBLISH_URL=http://localhost:8203/voice-state/publish` (and optionally `ZEUS_VOICE_STATE_SECRET`) so Phaos state events reach the browser orb.

Optional systemd unit: see the legacy pattern in [roadmap.md](roadmap.md) Sprint 4; applies verbatim to Orpheus once the host path is stable.

## Rollback

```bash
cd /opt/zeus
git log --oneline -5
git checkout <last-good-sha>
docker compose up -d --build
curl -s localhost:8203/status | jq
```

To restore a Qdrant collection after a bad ingest, see the backup / restore runbook embedded in [docs/memory-architecture-plan.md](../../docs/memory-architecture-plan.md) step 7.

## Related

- [docs/nemoclaw-ops.md](../../docs/nemoclaw-ops.md): NemoClaw + OpenShell sandbox runbook (daedalus-specific)
- [model-comparison.md](model-comparison.md): measured tok/s per model on this class of GPU
- [ingest-guide.md](ingest-guide.md), [ingest-paths.md](ingest-paths.md): source ordering and paths
