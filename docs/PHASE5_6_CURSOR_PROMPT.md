# Zeus Phase 5-6 Implementation Prompt for Cursor

**Copy this entire prompt into Cursor's AI assistant to get context-aware help building Phase 5-6.**

---

## Quick Context

This assumes you've completed **Phase 3 (Voice Loop)** and **Phase 4 (MCP Server)** — voice pipeline is working, MCP tools are exposed.

### Key Reference
- Project Architecture: `CLAUDE.md`
- Full Roadmap: `docs/zeus_linear_ticket_plan.md`
- Phase 3-4 Context: `docs/PHASE3_4_CURSOR_PROMPT.md`

---

## Phase Overview

**Phase 5: Ruflo Agents (Olympians)** — Build a swarm of task-specific agents.
- Ruflo orchestration engine (scheduler, task dispatcher)
- Three specialized agents: Personal, Dev, Research
- NemoClaw safety layer (Aegis) enforcing policies on agent output
- Multi-agent orchestration tests

**Phase 6: Deploy to Olympus** — Ship Zeus to production (RTX 3080 server).
- Production docker-compose stack with all services
- Deployment procedures (Tailscale access, health checks)
- Always-on service mode (systemd timer or daemon)
- Production voice pipeline optimizations for 10GB VRAM (Qwen2.5-7B Q4_K_M)

**Why Together?** Phase 5 builds the agent orchestration layer (uses Zeus Core APIs + MCP tools). Phase 6 takes the validated stack and deploys it to the production RTX 3080 server (Olympus). Both can run in parallel; Phase 6 deployment depends on Phase 5 agents being testable.

---

## Current Status

### ✓ Partially Done

**Ruflo Configuration** — `zeus/orchestration/`
- `ruflo.yaml` defined (scheduler config, task registry)
- Agent YAML skeletons exist: `agents/personal.yaml`, `agents/dev.yaml`, `agents/research.yaml`
- **Needs:** Runtime implementation (task dispatch, agent communication, policy enforcement)

**Docker Compose Skeleton** — `docker-compose.yaml`
- Core services wired (zeus-core, redis, qdrant, ollama)
- **Needs:** Production-specific config (resource limits, networking, health checks, restart policies)

### ⧬ Not Started

**Phase 5: Agent Orchestration**
- Ruflo runtime engine (scheduler, task dispatcher)
- Agent worker pools (async task execution)
- NemoClaw safety layer integration with Aegis policies
- Agent-to-agent communication (via Redis queue or fastapi events)
- Multi-agent test harness

**Phase 6: Production Deployment**
- Systemd services for always-on operation
- Server health checks + automated recovery
- Production docker-compose overrides
- Ollama model optimization for 3080 (Qwen Q4_K_M tuning)
- Tailscale VPN setup for secure remote access
- Admin dashboard for monitoring

---

## Phase 5: Ruflo Agents Implementation

### Architecture

```
User Query (text or voice)
    ↓ [Zeus Core: session, voice, chat routes]
    ↓
Ruflo Orchestration Engine
    ↓ [Task Router: which agent(s) should handle this?]
    ├─ Personal Agent (memory synthesis, reflection)
    ├─ Dev Agent (code generation, testing)
    └─ Research Agent (fact lookup, synthesis)
    ↓
Agent Workers [async task pools]
    ↓
Tool Calls [MCP tools, Core APIs, external services]
    ↓
Aegis Safety Filter [policy enforcement on output]
    ↓
Response → User
```

### Task Breakdown

#### Phase 5a: Ruflo Runtime Engine (LAB-112)

**Ruflo Initialization & Scheduling**
- Load `orchestration/ruflo.yaml` config at startup
- Initialize task scheduler (Ruflo's internal scheduler)
- Register agent pools in Redis (or in-memory)
- Health check / startup test

**Key File:** `zeus/orchestration/ruflo_engine.py`
```python
class RufloEngine:
    def __init__(self, config_path):
        """Initialize Ruflo engine from YAML config"""

    async def dispatch_task(self, task_name, params, priority="normal"):
        """Dispatch a task to appropriate agent(s)"""

    async def run(self):
        """Main event loop: poll for tasks, dispatch to workers"""
```

**Integration:**
- Ruflo engine started as a background task in Zeus Core
- Tasks queued via Redis (for cluster) or in-memory queue
- Engine polls and dispatches to agent workers

**Test:**
```bash
# Start Zeus services
docker compose up -d

# Test Ruflo engine via API
curl -X POST http://localhost:8203/orchestration/task \
  -H "Content-Type: application/json" \
  -d '{
    "task": "summarize_learning",
    "params": {"topic": "vector databases"},
    "agent_pool": "personal"
  }'
```

#### Phase 5b: Personal Agent (LAB-113)

**Purpose:** Reflection + personal knowledge synthesis
- Analyzes user queries related to personal learning
- Searches memory (mnemosyne), synthesizes insights
- Generates personalized responses grounded in past interactions
- Uses memory search + context query MCP tools

**Key File:** `zeus/orchestration/agents/personal_agent.py`
```python
class PersonalAgent:
    async def handle_query(self, query: str, context: dict) -> str:
        """Synthesize personal insights from query"""

    async def reflect(self, timeframe: str = "week"):
        """Weekly/monthly reflection on learning"""
```

**Agent Definition:** `zeus/orchestration/agents/personal.yaml`
```yaml
name: Personal Agent
description: Synthesizes personal learning and reflection
model: qwen2.5-7b-instruct  # prod | claude-sonnet-4-6  # dev
tools:
  - context/query
  - memory/search
context:
  - oracle.context_api
  - mnemosyne.memory_search
safety:
  policy: reflection
```

**Integration:**
- Triggered by queries mentioning learning, memory, reflection
- Calls `context/query` for document search
- Calls `memory/search` for hybrid memory lookup
- Output passes through Aegis policy filter

#### Phase 5c: Dev Agent (LAB-114)

**Purpose:** Code generation, testing, debugging assistance
- Analyzes code-related queries
- Can read Zeus codebase, suggest refactors, generate code snippets
- Triggers test runs, interprets results
- Uses MCP tools + filesystem access

**Key File:** `zeus/orchestration/agents/dev_agent.py`
```python
class DevAgent:
    async def handle_query(self, query: str, context: dict) -> str:
        """Generate code or provide dev advice"""

    async def suggest_refactor(self, file_path: str) -> str:
        """Suggest refactoring for a file"""
```

**Agent Definition:** `zeus/orchestration/agents/dev.yaml`
```yaml
name: Dev Agent
description: Code generation, refactoring, testing
model: claude-sonnet-4-6  # code quality requires Claude
tools:
  - context/query
  - ingest/trigger
  - filesystem.read
  - filesystem.write
  - subprocess.run_test
context:
  - oracle.context_api
safety:
  policy: code_execution
```

#### Phase 5d: Research Agent (LAB-116)

**Purpose:** Fact lookup, synthesis, external source integration
- Handles research queries (fact-checking, background synthesis)
- Searches personal knowledge base + web sources (MCP integration)
- Summarizes findings with citations
- Uses context/query + web search tools

**Key File:** `zeus/orchestration/agents/research_agent.py`
```python
class ResearchAgent:
    async def handle_query(self, query: str, context: dict) -> str:
        """Research a topic with citations"""

    async def fact_check(self, claim: str) -> bool:
        """Verify a claim against knowledge base"""
```

**Agent Definition:** `zeus/orchestration/agents/research.yaml`
```yaml
name: Research Agent
description: Fact lookup, synthesis, source integration
model: claude-sonnet-4-6  # reasoning + synthesis
tools:
  - context/query
  - web_search  # future: integrate web search MCP
  - citation_builder
context:
  - oracle.context_api
safety:
  policy: citation_required
```

#### Phase 5e: NemoClaw Safety Layer (LAB-119 — Aegis)

**Policy Enforcement on Agent Output**
- NemoClaw + OpenShell policies loaded from `safety/policies/`
- Policies defined per agent (personal, dev, research)
- Safety filter runs before response sent to user
- Logs policy violations for audit

**Key Files:**
- `zeus/safety/policy_engine.py` — Policy evaluator
- `zeus/safety/policies/personal.yaml` — Personal agent policy
- `zeus/safety/policies/code_execution.yaml` — Dev agent policy
- `zeus/safety/policies/citation_required.yaml` — Research agent policy

**Policy Example (YAML):**
```yaml
name: code_execution
description: Enforce safe code generation practices
rules:
  - name: no_rm_command
    pattern: "rm\\s+-rf\\s+/"
    action: reject
    message: "Code that deletes system files is not allowed"
  - name: sql_injection_check
    pattern: "SELECT.*FROM.*WHERE.*\\$"
    action: flag_for_review
  - name: credential_check
    pattern: "(password|api_key|secret)\\s*=\\s*['\"].*['\"]"
    action: reject
    message: "Hardcoded credentials are not allowed"
```

**Integration:**
```python
# In agent response handler:
async def send_response(agent_response: str, agent_type: str):
    safety_filter = AegisPolicyEngine(policy=f"policies/{agent_type}.yaml")
    filtered_response = await safety_filter.evaluate(agent_response)
    if filtered_response.status == "rejected":
        return {"error": filtered_response.message}
    return {"response": filtered_response.text, "flags": filtered_response.flags}
```

**Test:**
```bash
# Test safety policy with code generation
curl -X POST http://localhost:8203/orchestration/task \
  -H "Content-Type: application/json" \
  -d '{
    "task": "write_code",
    "params": {"spec": "refactor zeus/voice/stt.py"},
    "agent_pool": "dev"
  }' | jq '.response'
```

#### Phase 5f: Multi-Agent Orchestration Test (LAB-120)

**Orchestration Test Suite**
- Unit tests for each agent
- Integration tests: multi-agent task chains
- Policy enforcement tests (safety layer)
- Communication tests (Redis queue or fastapi events)

**Key File:** `zeus/orchestration/test_orchestration.py`

**Test Scenarios:**
```python
@pytest.mark.asyncio
async def test_personal_agent_query():
    """Personal agent can synthesize memory"""
    agent = PersonalAgent()
    response = await agent.handle_query(
        "What did I learn about memory systems?",
        context={"memory_backend": "mnemosyne"}
    )
    assert "vector" in response.lower()

@pytest.mark.asyncio
async def test_multi_agent_task_chain():
    """Multiple agents work together on complex query"""
    engine = RufloEngine("orchestration/ruflo.yaml")
    await engine.start()

    # User asks: "How can I optimize my voice pipeline?"
    # Should route to: Dev Agent (code) + Research Agent (patterns)
    response = await engine.dispatch_task(
        "optimize_voice",
        params={"aspect": "latency"},
        priority="high"
    )
    assert response.status == "success"
    assert len(response.agents_used) >= 2

@pytest.mark.asyncio
async def test_safety_policy_enforcement():
    """Aegis blocks unsafe code suggestions"""
    dev_agent = DevAgent()
    response = await dev_agent.handle_query(
        "Write code to delete all files in /",
        context={}
    )
    # Safety filter should reject
    assert response.status == "rejected"
```

---

## Phase 6: Deploy to Olympus Implementation

### Architecture

```
Dev Tower (RTX 5080) — Development
    ↓ [validate agents, voice, MCP]
    ↓ [prepare production config]
    ↓
Git Push → Main
    ↓
Olympus Server (RTX 3080)
    ↓ [deploy via Tailscale]
    ├─ Docker Compose Stack
    ├─ Systemd Services (always-on)
    ├─ Health Checks + Auto-recovery
    └─ Admin Dashboard
```

### Task Breakdown

#### Phase 6a: Docker Compose Production Stack (LAB-124)

**Production docker-compose.yaml Overrides**
- Separate `docker-compose.prod.yaml` with:
  - Resource limits (CPU, memory, GPU)
  - Restart policies (always-on)
  - Health checks (liveness, readiness)
  - Networking (Tailscale integration)
  - Volume mounts for persistent data
  - Ollama model optimization for Q4_K_M on 3080

**Key Changes from Dev:**
```yaml
# dev: unlimited resources, quick restart, verbose logging
# prod: tight limits, conservative restart, structured logging

services:
  zeus-core:
    image: zeus:prod
    deploy:
      resources:
        limits:
          cpus: '4'
          memory: 8G
        reservations:
          cpus: '2'
          memory: 4G
          devices:
            - driver: nvidia
              count: 1
              capabilities: [gpu]
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8203/health"]
      interval: 30s
      timeout: 10s
      retries: 3
    environment:
      - ZEUS_ENV=prod
      - ZEUS_LOG_LEVEL=info
      - OLLAMA_KEEP_ALIVE=24h

  ollama:
    image: ollama/ollama:latest
    environment:
      - OLLAMA_MODELS=/models
    volumes:
      - ollama_models:/models
    deploy:
      resources:
        limits:
          memory: 10G
        devices:
          - driver: nvidia
            device_ids: ['0']  # GPU 0 on 3080
            capabilities: [gpu]
    restart: unless-stopped

  qdrant:
    image: qdrant/qdrant:latest
    volumes:
      - qdrant_data:/qdrant/storage
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:6333/health"]
      interval: 30s
```

**Key File:** `docker-compose.prod.yaml`

#### Phase 6b: Server Deployment (LAB-128)

**Deployment Procedures**
- Tailscale setup for secure remote access
- Docker + docker-compose on Olympus
- Git clone Zeus repo to `/opt/zeus`
- Pull production docker images
- Initialize volumes (Ollama models, Qdrant data)
- Start services via `docker compose -f docker-compose.prod.yaml up -d`

**Deployment Script:** `deploy/deploy_to_olympus.sh`
```bash
#!/bin/bash
# Deployment to Olympus (RTX 3080 server)

set -e

# 1. SSH into Olympus via Tailscale IP
OLYMPUS_IP=100.x.x.x
ssh root@$OLYMPUS_IP <<'EOF'
  cd /opt/zeus

  # 2. Pull latest from main
  git pull origin main

  # 3. Load production environment
  export ZEUS_ENV=prod

  # 4. Pull docker images
  docker compose -f docker-compose.prod.yaml pull

  # 5. Initialize Ollama models (if not present)
  docker compose -f docker-compose.prod.yaml run --rm ollama ollama pull qwen2.5-7b-instruct:q4_k_m

  # 6. Start all services
  docker compose -f docker-compose.prod.yaml up -d

  # 7. Health check
  curl http://localhost:8203/health
  echo "Zeus is live on Olympus!"
EOF
```

#### Phase 6c: Always-On Service Mode (LAB-140)

**Systemd Service + Timer for Always-On Operation**

**Systemd Service File:** `/etc/systemd/system/zeus.service`
```ini
[Unit]
Description=Zeus Personal AI Assistant
After=network-online.target docker.service
Wants=network-online.target

[Service]
Type=oneshot
WorkingDirectory=/opt/zeus
ExecStart=/opt/zeus/deploy/start_zeus.sh
ExecStop=/opt/zeus/deploy/stop_zeus.sh
RemainAfterExit=yes
Restart=on-failure
RestartSec=10

[Install]
WantedBy=multi-user.target
```

**Startup Script:** `deploy/start_zeus.sh`
```bash
#!/bin/bash
cd /opt/zeus
export ZEUS_ENV=prod
docker compose -f docker-compose.prod.yaml up -d --remove-orphans
echo "$(date): Zeus services started" >> /var/log/zeus.log
```

**Shutdown Script:** `deploy/stop_zeus.sh`
```bash
#!/bin/bash
cd /opt/zeus
docker compose -f docker-compose.prod.yaml down
echo "$(date): Zeus services stopped" >> /var/log/zeus.log
```

**Enable & Start:**
```bash
sudo systemctl enable zeus.service
sudo systemctl start zeus.service
sudo systemctl status zeus.service
```

#### Phase 6d: Server Voice Pipeline Optimization (LAB-141)

**Tuning for RTX 3080 (10GB VRAM)**

1. **Ollama Model Optimization**
   - Use Qwen2.5-7B-Instruct Q4_K_M (fits in 10GB with 2GB headroom)
   - Enable KV cache quantization
   - Set context length to 2048 (not 4096)
   - Tune `OLLAMA_KEEP_ALIVE` to 24h (always loaded)

   **Config:** `models/ollama_prod_config.yaml`
   ```yaml
   model: qwen2.5-7b-instruct:q4_k_m
   options:
     num_ctx: 2048
     num_gpu: 1  # GPU 0
     f16_kv: false  # Use Q4 KV cache
     main_gpu: 0
     memory_limit: 10737418240  # 10GB
   ```

2. **Voice Pipeline Optimization**
   - STT (Whisper): Keep base model (smallest)
   - TTS (Voicebox): Cache voice embeddings
   - Query engine: Optimize token budgets (reduce from 4096 to 2048)
   - MCP tool calls: Increase timeout from 10s to 30s (slower CPU)

   **Config:** `zeus/core/config.py`
   ```python
   # Production settings
   PROD_CONFIG = {
       "stl_model": "base",
       "max_tokens": 2048,
       "query_timeout": 30,
       "tts_cache_voices": True,
       "ollama_keep_alive": 86400,  # 24h
   }
   ```

3. **Health Check + Auto-Recovery**
   - Monitor Ollama process + VRAM usage
   - Restart Ollama if VRAM > 9.5GB (OOM prevention)
   - Health check endpoint at `/health` (already exists)

   **Monitoring Script:** `deploy/health_check.sh`
   ```bash
   #!/bin/bash
   # Monitor Zeus health every 5 minutes

   HEALTH_URL="http://localhost:8203/health"
   OLLAMA_VRAM_LIMIT=9.5

   while true; do
     # Check Zeus health
     if ! curl -f $HEALTH_URL > /dev/null 2>&1; then
       echo "$(date): Health check failed, restarting..." >> /var/log/zeus.log
       systemctl restart zeus.service
     fi

     # Check VRAM usage
     VRAM_USED=$(nvidia-smi --query-gpu=memory.used --format=csv,noheader,nounits)
     if (( $(echo "$VRAM_USED > $OLLAMA_VRAM_LIMIT * 1024" | bc -l) )); then
       echo "$(date): VRAM critical ($VRAM_USED MB), restarting Ollama..." >> /var/log/zeus.log
       docker restart zeus-ollama
     fi

     sleep 300  # Check every 5 minutes
   done
   ```

   **Install as Cron Job:**
   ```bash
   (crontab -l 2>/dev/null; echo "*/5 * * * * /opt/zeus/deploy/health_check.sh") | crontab -
   ```

---

## Key Files to Work On

### Phase 5

```
zeus/
├── orchestration/
│   ├── ruflo.yaml              ← done (config)
│   ├── ruflo_engine.py         ← NEW: scheduler + dispatcher
│   ├── agents/
│   │   ├── personal.yaml       ← done (config)
│   │   ├── personal_agent.py   ← NEW: implementation
│   │   ├── dev.yaml            ← done (config)
│   │   ├── dev_agent.py        ← NEW: implementation
│   │   ├── research.yaml       ← done (config)
│   │   ├── research_agent.py   ← NEW: implementation
│   │   └── __init__.py
│   └── test_orchestration.py   ← NEW: multi-agent tests
├── safety/
│   ├── policy_engine.py        ← NEW: NemoClaw evaluator
│   └── policies/
│       ├── personal.yaml       ← NEW: reflection policy
│       ├── code_execution.yaml ← NEW: dev agent policy
│       ├── citation_required.yaml ← NEW: research policy
│       └── __init__.py
└── core/
    └── main.py                 ← wire in Ruflo engine at startup
```

### Phase 6

```
deploy/
├── docker-compose.prod.yaml    ← NEW: production overrides
├── deploy_to_olympus.sh        ← NEW: deployment script
├── start_zeus.sh               ← NEW: systemd startup
├── stop_zeus.sh                ← NEW: systemd shutdown
├── health_check.sh             ← NEW: monitoring + recovery
└── README.md                   ← procedures + troubleshooting

zeus/
├── models/
│   └── ollama_prod_config.yaml ← NEW: 3080 optimization
├── core/
│   └── config.py               ← update with prod settings
└── docker-compose.yaml         ← update health checks
```

---

## Docker Services to Add / Modify

### Phase 5: Ruflo Agent Bus (Optional Redis)

```yaml
# If using Redis for agent task queue:
redis:
  image: redis:latest
  container_name: zeus-redis
  ports:
    - "${REDIS_PORT:-6379}:6379"
  volumes:
    - redis_data:/data
  restart: unless-stopped
  networks:
    - web
```

### Phase 6: Production Compose Overrides

Add to `docker-compose.prod.yaml`:

```yaml
version: '3.9'

services:
  zeus-core:
    deploy:
      resources:
        limits:
          cpus: '4'
          memory: 8G
        devices:
          - driver: nvidia
            count: 1
            capabilities: [gpu]
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8203/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  ollama:
    deploy:
      resources:
        limits:
          memory: 10G
        devices:
          - driver: nvidia
            device_ids: ['0']
            capabilities: [gpu]
    environment:
      - OLLAMA_KEEP_ALIVE=86400
    restart: unless-stopped

  qdrant:
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:6333/health"]
      interval: 30s
```

---

## Environment Variables

### Phase 5

```env
# Orchestration
RUFLO_CONFIG=orchestration/ruflo.yaml
RUFLO_SCHEDULER=internal  # or redis for clustering
RUFLO_TASK_TIMEOUT=60

# Safety
AEGIS_POLICY_DIR=zeus/safety/policies/
AEGIS_ENFORCE=true
AEGIS_LOG_VIOLATIONS=true

# Agents
AGENT_POOL_SIZE=3
AGENT_TASK_QUEUE_MAX=100
```

### Phase 6

```env
# Deployment
ZEUS_ENV=prod
ZEUS_LOG_LEVEL=info
DEPLOY_TARGET=olympus
OLYMPUS_IP=100.x.x.x

# Ollama Production
OLLAMA_KEEP_ALIVE=86400
OLLAMA_MODELS=/models
OLLAMA_MEMORY_LIMIT=10737418240

# Health Checks
HEALTH_CHECK_INTERVAL=300
VRAM_CRITICAL_THRESHOLD=9.5
```

---

## Testing & Validation

### Phase 5: Agent Orchestration

**Unit Tests**
- Each agent responds correctly to queries
- Safety policies reject/flag appropriately
- Agent tools (MCP calls) succeed

**Integration Tests**
- Ruflo dispatches tasks to correct agents
- Multi-agent chains work (e.g., Dev + Research)
- Redis queue handles task backlog
- Policy enforcement blocks unsafe output

**Smoke Tests**
```bash
# Start Zeus services
docker compose up -d

# Test Personal Agent
curl -X POST http://localhost:8203/orchestration/task \
  -H "Content-Type: application/json" \
  -d '{
    "task": "reflect",
    "params": {"period": "week"},
    "agent_pool": "personal"
  }' | jq '.response'

# Test Dev Agent
curl -X POST http://localhost:8203/orchestration/task \
  -d '{
    "task": "code_review",
    "params": {"file": "zeus/core/main.py"},
    "agent_pool": "dev"
  }' | jq '.response'

# Test Research Agent
curl -X POST http://localhost:8203/orchestration/task \
  -d '{
    "task": "research",
    "params": {"topic": "vector databases"},
    "agent_pool": "research"
  }' | jq '.response'

# Test Safety Policy
curl -X POST http://localhost:8203/orchestration/task \
  -d '{
    "task": "write_code",
    "params": {"spec": "rm -rf /"},
    "agent_pool": "dev"
  }' | jq '.response'
# Should be rejected
```

### Phase 6: Production Deployment

**Pre-Deployment Checklist**
- [ ] All Phase 5 agents pass unit + integration tests
- [ ] docker-compose.prod.yaml validated on dev tower
- [ ] Ollama models pre-pulled (qwen2.5-7b-instruct:q4_k_m)
- [ ] Health check endpoints return 200
- [ ] Tailscale configured on Olympus
- [ ] Deployment script tested (dry-run first)

**Deployment Steps**
```bash
# 1. On dev tower: validate prod config
docker compose -f docker-compose.prod.yaml config > /tmp/config.yaml
# Review for correctness

# 2. On Olympus: pull latest + deploy
ssh root@100.x.x.x "cd /opt/zeus && bash deploy/deploy_to_olympus.sh"

# 3. Smoke test on Olympus
ssh root@100.x.x.x "curl http://localhost:8203/health"

# 4. Monitor logs
ssh root@100.x.x.x "docker compose logs -f"
```

**Post-Deployment Validation**
```bash
# Check services are running
docker ps

# Check VRAM usage
nvidia-smi

# Test voice interaction
curl -X POST http://localhost:8203/voice/interact \
  -H "Content-Type: audio/wav" \
  --data-binary @question.wav > response.wav

# Check Ollama model loaded
curl http://localhost:11434/api/tags

# Verify MCP server is running
curl http://localhost:5005/health

# Monitor health check
watch -n 30 'curl -s http://localhost:8203/health | jq .'
```

---

## Implementation Notes

### Phase 5 Architecture Decisions

**Why Ruflo for Agent Orchestration?**
- Claude Code native (uses Claude API under the hood)
- Built-in swarm support (multi-agent coordination)
- No framework lock-in (unlike LangGraph/CrewAI)
- Supports task dependency graphs
- Policy-aware (NemoClaw integrates cleanly)

**Why Three Agent Types?**
- **Personal:** Handles reflection, learning synthesis (low-risk operations)
- **Dev:** Code generation (high-risk, requires safety filter)
- **Research:** Fact-checking, synthesis (medium-risk, requires citations)
- Can add more agents later (Email Agent, Scheduler Agent, etc.)

**Why Aegis (NemoClaw)?**
- Purpose-built for policy enforcement on agent output
- Fine-grained rule definitions (regex patterns, semantic rules)
- Non-blocking (flags violations instead of crashing)
- Audit logs for compliance

### Phase 6 Architecture Decisions

**Why Separate docker-compose.prod.yaml?**
- Dev and prod have different constraints (memory, GPU, restart behavior)
- Single file would be unreadable
- Prod config can be version-controlled separately
- Easy to deploy to different hardware (3080 vs RTX 4090, etc.)

**Why Qwen2.5-7B Q4_K_M for 3080?**
- Fits in 10GB VRAM (production model is 7B parameters)
- Instruction-following quality suitable for agent tasks
- Q4 quantization: ~6GB at inference, ~2GB headroom for buffers
- Faster than larger models (14B, 34B) on 3080

**Why Systemd Service?**
- Persistent across reboots
- Integrated with OS logging (journalctl)
- Easy restart/stop/status monitoring
- Works with monitoring tools (Nagios, Prometheus, etc.)

**Why Tailscale for Remote Access?**
- Zero-trust VPN (no port forwarding needed)
- Encrypted end-to-end
- Can access from anywhere
- Works across NAT

---

## Commit Message Format

```bash
# Phase 5a: Ruflo Engine
git checkout -b chrislawrencedev/LAB-112-ruflo-engine
git commit -m "Implement Ruflo orchestration engine with task dispatch

- RufloEngine class with scheduler initialization
- Task router directs queries to appropriate agent pools
- Redis queue for task buffering (optional)
- Startup health check

(LAB-112)"

# Phase 5b: Personal Agent
git checkout -b chrislawrencedev/LAB-113-personal-agent
git commit -m "Implement Personal Agent for reflection and synthesis

- Queries mnemosyne memory + context API
- Generates personalized insights
- Passes through Aegis safety filter
- Unit tests for agent responses

(LAB-113)"

# Phase 6a: Production Compose
git checkout -b chrislawrencedev/LAB-124-prod-compose
git commit -m "Add production docker-compose.prod.yaml with resource limits

- Separate prod config (not replacing dev compose)
- GPU allocation for Ollama (10GB limit)
- Health checks for all services
- Restart policies and volumes

(LAB-124)"

# Phase 6b: Deployment to Olympus
git checkout -b chrislawrencedev/LAB-128-deployment-script
git commit -m "Add deployment script for Olympus server

- Tailscale SSH integration
- Docker image pull and model initialization
- Health check validation
- Rollback procedure

(LAB-128)"
```

---

## Dependency Chain

```
Phase 2 (Data Brain) + Phase 3 (Voice) + Phase 4 (MCP)
    ↓
Phase 5a (Ruflo Engine)
    ↓
Phase 5b, 5c, 5d (Agents)
    ↓
Phase 5e (Aegis Safety Filter)
    ↓
Phase 5f (Multi-Agent Tests)
    ↓
Phase 6a (Production Compose)
    ↓
Phase 6b (Deployment Script)
    ↓
Phase 6c (Systemd Service)
    ↓
Phase 6d (Ollama Tuning + Health Checks)
```

**Critical Path:** Phase 5a → Phase 5f → Phase 6b (agents must be tested before deployment)

---

## Testing Scenarios

### Happy Path: Multi-Agent Query

1. User asks: "How can I improve my voice pipeline?"
2. Ruflo routes to: Dev Agent (code optimization) + Research Agent (best practices)
3. Dev Agent: Reviews `zeus/voice/pipeline.py`, suggests refactors
4. Research Agent: Looks up papers on low-latency STT/TTS
5. Aegis evaluates both responses (code safe? citations present?)
6. Responses merged and sent to user

### Error Case: Unsafe Code Generation

1. User asks Dev Agent: "Write code to delete all system files"
2. Dev Agent generates code with `rm -rf /`
3. Aegis policy `code_execution.yaml` blocks it
4. Response: `{"error": "Code that deletes system files is not allowed"}`
5. Violation logged for audit

### Production Deployment

1. Main branch → automated test suite passes
2. Dev tower deploys locally, validates prod config
3. Manual approval: `ssh root@100.x.x.x bash deploy/deploy_to_olympus.sh`
4. Health checks: all services up, models loaded, VRAM OK
5. Voice test: send audio, get response back
6. Monitor logs for 24h, then set systemd auto-restart

---

## Reference Docs

- **Phase 3-4 Context:** `docs/PHASE3_4_CURSOR_PROMPT.md`
- **Architecture & Standards:** `CLAUDE.md`
- **Full Roadmap:** `docs/zeus_linear_ticket_plan.md`
- **Ruflo Docs:** https://github.com/run-llm/ruflo (Claude Code native)
- **NemoClaw/OpenShell:** (internal or custom implementation)
- **Ollama Model Optimization:** https://github.com/ollama/ollama/blob/main/docs/modelfile.md
- **Systemd Services:** https://man.archlinux.org/man/systemd.service.5
- **Tailscale Setup:** https://tailscale.com/kb/1017/install

---

## Questions to Ask While Implementing

**Phase 5:**
1. Should agents run in separate processes (pods) or same process (async tasks)?
2. How should agents communicate (Redis, FastAPI events, gRPC)?
3. Should agent outputs be cached? For how long?
4. What metrics should we track for each agent (latency, error rate)?
5. Should multi-agent chains be configurable (YAML) or hardcoded?

**Phase 6:**
1. Should Ollama model be pre-loaded on boot, or lazy-loaded on first use?
2. How do we handle model updates without downtime?
3. Should health checks be active (call endpoints) or passive (container check)?
4. How do we monitor GPU memory on production? (nvidia-smi polling?)
5. Should we support rolling deployment (blue-green) or simple restart?

---

## How to Use This in Cursor

1. Copy this entire prompt
2. Open Cursor → New Chat
3. Paste the prompt
4. Ask specific questions like:
   - "Implement the Ruflo orchestration engine with task dispatch"
   - "How should agents communicate with each other?"
   - "Design the Aegis safety policy enforcement layer"
   - "Help me write the deployment script for Olympus"
   - "What's the best way to optimize Ollama for the 3080?"
   - "Review this docker-compose.prod.yaml for production readiness"

Cursor will have full context and can provide implementation-ready code.

---

**Last Updated:** 2026-03-25
**Estimated Timeline:** Phase 5 (agents) ~2-3 weeks, Phase 6 (deployment) ~1 week
**Critical Blocker:** Phase 5 agents must pass all tests before Phase 6 deployment to Olympus
