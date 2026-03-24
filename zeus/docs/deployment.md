# Olympus Deployment Runbook

This document covers deploying Zeus from the Apollo dev tower to Olympus (RTX 3080 production server). Run this after Sprint 3 is validated locally.

**Prerequisite:** All smoke tests pass on Apollo with `ZEUS_ENV=dev`. Voice loop works end-to-end locally.

---

## Environment Differences

| | Apollo (dev) | Olympus (prod) |
|---|---|---|
| `ZEUS_ENV` | `dev` | `prod` |
| LLM | Claude API (Sonnet 4.6) | Ollama → Qwen2.5-7B Q4_K_M |
| VRAM | 16GB (5080) | 10GB (3080) |
| Logging | DEBUG, text | INFO, JSON |
| Whisper model | large-v3 | large-v3 (fits in VRAM budget) |

---

## VRAM Budget on Olympus (3080, 10GB)

| Component | VRAM |
|---|---|
| Qwen2.5-7B Q4_K_M | ~5.5 GB |
| nomic-embed-text | ~0.3 GB |
| WhisperLiveKit large-v3 | ~3.0 GB |
| **Total** | **~8.8 GB** |

Margin: ~1.2GB. Don't load additional models concurrently. `OLLAMA_MAX_LOADED_MODELS=1` is already set in `.env.example`.

If you're tight on VRAM, swap Whisper to `medium` (~1.5GB) — latency impact is small.

---

## Pre-Deployment Checklist

On **Apollo** (before leaving dev):

- [ ] `python scripts/smoke_test.py` — all checks pass
- [ ] Iris ingest complete — Qdrant collection has data
- [ ] Oracle `/context/query` returns sensible results
- [ ] Voice loop end-to-end test: wake → STT → LLM → TTS
- [ ] All code committed and pushed to `main`
- [ ] `main` branch is clean: `git status` shows nothing uncommitted

---

## Olympus Setup (first time only)

SSH into Olympus:
```bash
ssh chris@olympus   # or whatever your SSH alias is
```

**1. Install system deps:**
```bash
sudo apt update
sudo apt install -y git python3.11 python3.11-venv python3-pip \
  portaudio19-dev ffmpeg curl docker.io docker-compose-plugin
sudo usermod -aG docker $USER
```

**2. NVIDIA Container Toolkit** (if not already installed):
```bash
curl -fsSL https://nvidia.github.io/libnvidia-container/gpgkey | sudo gpg --dearmor -o /usr/share/keyrings/nvidia-container-toolkit-keyring.gpg
curl -s -L https://nvidia.github.io/libnvidia-container/stable/deb/nvidia-container-toolkit.list | \
  sed 's#deb https://#deb [signed-by=/usr/share/keyrings/nvidia-container-toolkit-keyring.gpg] https://#g' | \
  sudo tee /etc/apt/sources.list.d/nvidia-container-toolkit.list
sudo apt update && sudo apt install -y nvidia-container-toolkit
sudo nvidia-ctk runtime configure --runtime=docker
sudo systemctl restart docker
```

Verify:
```bash
docker run --rm --gpus all nvidia/cuda:12.0-base nvidia-smi
```

**3. Clone repo:**
```bash
git clone https://github.com/[chris]/zeus.git /opt/zeus
cd /opt/zeus
python3.11 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt --break-system-packages
```

**4. Create `.env`:**
```bash
cp .env.example .env
nano .env
```

Set:
```bash
ZEUS_ENV=prod
# No ANTHROPIC_API_KEY needed in prod
ZEUS_PROD_MODEL=qwen2.5:7b-instruct-q4_K_M
ZEUS_EMBED_MODEL=nomic-embed-text
QDRANT_URL=http://localhost:6333
OLLAMA_URL=http://localhost:11434
ZEUS_CORE_PORT=8000
ORPHEUS_VOICE_ID=<copy from Apollo .env>
VOICEBOX_URL=http://localhost:5050
```

**5. Pull models:**
```bash
docker compose up ollama -d
docker exec zeus-ollama ollama pull qwen2.5:7b-instruct-q4_K_M
docker exec zeus-ollama ollama pull nomic-embed-text

# Verify
docker exec zeus-ollama ollama list
```

---

## First Prod Deploy

**Start services:**
```bash
cd /opt/zeus
docker compose up qdrant ollama -d

# Wait for both to be healthy
docker compose ps
```

**Run prod smoke test:**
```bash
source .venv/bin/activate
python scripts/smoke_test.py --skip-core
# Qdrant, Ollama, and embed model should all pass
# This embeds a test string through nomic-embed-text — confirms full embed path on prod
```

**Start Zeus Core:**
```bash
uvicorn zeus.core.main:app --host 0.0.0.0 --port 8000
# In a separate terminal:
python scripts/smoke_test.py
# All checks should pass now
```

**Run ingest on prod:**
```bash
# Copy your data from Apollo (or re-export from sources)
scp -r apollo:/opt/zeus/zeus/data/raw/ /opt/zeus/zeus/data/raw/

# Dry run first
python -m zeus.ingest.run --source all --dry-run

# Live ingest (this will use Qwen2.5-7B for extraction — slower than Claude but works)
python -m zeus.ingest.run --source all
```

**Verify Oracle:**
```bash
curl -s -X POST localhost:8000/context/query \
  -H "Content-Type: application/json" \
  -d '{"query": "what are my current projects", "top_k": 3}' | python3 -m json.tool
```

---

## Systemd Services (run-on-boot)

Create service files so everything restarts automatically after a reboot.

**Qdrant and Ollama** are managed by Docker's restart policy (`unless-stopped`) — already set in `compose.yaml`. Enable Docker to start on boot:
```bash
sudo systemctl enable docker
```

**Zeus Core:**
```bash
sudo tee /etc/systemd/system/zeus-core.service << 'EOF'
[Unit]
Description=Zeus Core FastAPI Service
After=network.target docker.service
Requires=docker.service

[Service]
Type=simple
User=chris
WorkingDirectory=/opt/zeus
Environment=ZEUS_ENV=prod
EnvironmentFile=/opt/zeus/.env
ExecStart=/opt/zeus/.venv/bin/uvicorn zeus.core.main:app --host 0.0.0.0 --port 8000
Restart=on-failure
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl daemon-reload
sudo systemctl enable zeus-core
sudo systemctl start zeus-core
sudo systemctl status zeus-core
```

**Orpheus (voice pipeline):**
```bash
sudo tee /etc/systemd/system/zeus-orpheus.service << 'EOF'
[Unit]
Description=Zeus Orpheus Voice Pipeline
After=network.target zeus-core.service
Requires=zeus-core.service

[Service]
Type=simple
User=chris
WorkingDirectory=/opt/zeus
Environment=ZEUS_ENV=prod
EnvironmentFile=/opt/zeus/.env
ExecStart=/opt/zeus/.venv/bin/python zeus/voice/pipeline.py
Restart=on-failure
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl daemon-reload
sudo systemctl enable zeus-orpheus
sudo systemctl start zeus-orpheus
```

**Check all services are running:**
```bash
systemctl status zeus-core zeus-orpheus
docker compose ps
```

---

## Updating Olympus (subsequent deploys)

From Apollo, once changes are merged to `main`:
```bash
# On Olympus
cd /opt/zeus
git pull origin main
source .venv/bin/activate
pip install -r requirements.txt   # in case deps changed

sudo systemctl restart zeus-core
sudo systemctl restart zeus-orpheus

# Verify
python scripts/smoke_test.py
```

If the compose file changed:
```bash
docker compose pull    # pull new images
docker compose up -d   # restart services with new config
```

---

## Rollback

If something breaks after a deploy:
```bash
# Roll back to previous commit
git log --oneline -5   # find the last good commit hash
git checkout <hash>
sudo systemctl restart zeus-core zeus-orpheus
python scripts/smoke_test.py
```

To go back to `main` after fix:
```bash
git checkout main
git pull
sudo systemctl restart zeus-core zeus-orpheus
```

---

## Monitoring

**Quick health check:**
```bash
curl -s localhost:8000/status | python3 -m json.tool
```

**Logs:**
```bash
# Zeus Core
journalctl -u zeus-core -f

# Orpheus
journalctl -u zeus-orpheus -f

# Qdrant
docker logs zeus-qdrant -f

# Ollama
docker logs zeus-ollama -f
```

**VRAM usage:**
```bash
watch -n 2 nvidia-smi
```

**Qdrant collection stats:**
```bash
curl -s localhost:6333/collections/zeus_memories | python3 -m json.tool
```
