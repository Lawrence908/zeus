# Zeus Phase 3-4 Implementation Prompt for Cursor

**Copy this entire prompt into Cursor's AI assistant to get context-aware help building Phase 3-4.**

---

## Quick Context

This assumes you've completed **Phase 2 (Data Brain)** — query engine, data ingest, retrieval tuning are done.

### Key Reference
- Project Architecture: `CLAUDE.md`
- Full Roadmap: `docs/zeus_linear_ticket_plan.md`
- Phase 2 Context: `docs/PHASE2_CURSOR_PROMPT.md`

---

## Phase Overview

**Phase 3: Voice Loop (Orpheus)** — Make Zeus conversational via voice.
- Speech-to-text (STT) with WhisperLiveKit
- Text-to-speech (TTS) with Voicebox → LuxTTS
- Wake word detection with openWakeWord
- Voice state visualization (Phaos) via WebSocket

**Phase 4: MCP Server (Oracle Extended)** — Expose Zeus as an MCP server.
- Context API endpoints exposed via MCP protocol
- Memory search as MCP tool
- Ingest trigger as MCP tool
- Integration with Claude Desktop, Cursor, and other MCP clients

**Why Together?** Phase 4 can run in parallel with Phase 3. MCP server uses the APIs built in Phase 2. Voice pipeline depends on Phase 2 + MCP tools for agent integration.

---

## Current Status

### ✓ Partially Done
**Phaos (Voice-State Visualization)** — `zeus/voice/state.py`
- Voice-state protocol + hub/emitter pattern defined
- WebSocket endpoint wired up: `zeus/core/voice_ws.py`
- Visualization UI assets exist: `zeus/core/static/viz/`
- Served via `/viz` route in `zeus/core/chat.py`
- **Needs:** Full front-end integration with actual STT/TTS state updates

### ⧬ Not Started

**Phase 3: Voice Loop**
- WhisperLiveKit STT integration
- Voicebox TTS client (with LuxTTS backend)
- openWakeWord daemon
- Orpheus pipeline: microphone → STT → query engine → TTS → speaker
- Voice endpoint wired into FastAPI
- Phaos visualization updates during voice interactions

**Phase 4: MCP Server**
- MCP server skeleton
- Tool definitions (context/query, memory/search, ingest/trigger)
- MCP protocol scaffolding
- Integration tests with Claude Desktop or Cursor

---

## Phase 3: Voice Loop Implementation

### Architecture

```
Microphone
    ↓ [VAD: Voice Activity Detection]
Audio Stream
    ↓ [STT: WhisperLiveKit]
Transcript
    ↓ [Query Engine from Phase 2]
LLM Response
    ↓ [TTS: Voicebox client → LuxTTS]
Audio Stream
    ↓
Speaker

(Parallel: Phaos WebSocket publishes state for visualization)
```

### Tasks (Priority Order)

#### Phase 3a: STT Integration (LAB-51)

**WhisperLiveKit Setup**
- Container in docker-compose: Whisper server on port 9000
- Async audio streaming client in `zeus/voice/stt.py`
- Confidence threshold + language detection
- Returns `(transcript, confidence, language)`

**Key File:** `zeus/voice/stt.py`
```python
class WhisperSTTClient:
    async def transcribe_stream(self, audio_stream, language="en"):
        """Stream audio to Whisper, yield transcripts as they arrive"""
```

**Test:**
```bash
curl -X POST http://localhost:9000/asr \
  -H "Content-Type: audio/wav" \
  --data-binary @sample.wav
```

#### Phase 3b: TTS Integration (LAB-53)

**Voicebox REST Client**
- REST client calling Voicebox service
- Voice cloning support (optional speaker embedding)
- Returns audio stream (mp3/wav)

**Key File:** `zeus/voice/tts.py`
```python
class VoiceboxTTSClient:
    async def speak(self, text: str, voice_id: str = "default") -> bytes:
        """Stream TTS audio, return bytes"""
```

**Integration:**
- Voicebox service on port 8080 (Docker)
- Async streaming to speaker output

**Test:**
```bash
curl -X POST http://localhost:8080/speak \
  -H "Content-Type: application/json" \
  -d '{"text": "hello world", "voice_id": "default"}' \
  > output.wav
```

#### Phase 3c: Wake Word Detection (LAB-52)

**openWakeWord Daemon**
- CPU-efficient always-on listening
- Detects wake phrase (default: "Hey Zeus")
- Runs in background thread / separate process
- Publishes `wake_detected` event to Phaos WebSocket

**Key File:** `zeus/voice/wake_word.py`
```python
class WakeWordDetector:
    def start_listening(self, phrase="hey zeus"):
        """Start background listening, emit events on detection"""

    async def event_stream(self):
        """Yield wake events for WebSocket publishing"""
```

**Integration:**
- Docker container with openWakeWord model
- Audio input from system microphone (or virtual audio device)
- Event emission to Phaos

#### Phase 3d: Orpheus Pipeline (LAB-55)

**End-to-End Voice Handler**
- Listen for wake word
- Capture audio until VAD detects silence
- Pass to STT
- Pass transcript to query engine (Phase 2)
- Pass LLM response to TTS
- Play audio
- Update Phaos visualization throughout

**Key File:** `zeus/voice/pipeline.py`
```python
class OrpheusPipeline:
    async def handle_voice_interaction(self):
        """Orchestrate: wake → STT → query → TTS → play"""
```

**Endpoint:** `POST /voice/interact`
- Returns audio stream + transcript + response text

**Test:**
```bash
# Test with audio file
curl -X POST http://localhost:8203/voice/interact \
  -H "Content-Type: audio/wav" \
  --data-binary @question.wav \
  > response.wav && play response.wav
```

#### Phase 3e: Phaos Visualization (LAB-54)

**Voice State Updates**
- Emit state changes to WebSocket: `listening`, `transcribing`, `thinking`, `speaking`, `idle`
- Include metadata: transcript, confidence, response text, latency
- Frontend visualizes as waveform + status + transcript

**Key File:** Already wired (`zeus/core/voice_ws.py`)
```python
# Publish from Orpheus pipeline:
await voice_state_hub.emit("listening")
await voice_state_hub.emit("transcribing", {"transcript": "...", "confidence": 0.95})
await voice_state_hub.emit("thinking")
await voice_state_hub.emit("speaking", {"response": "..."})
```

**Frontend:** `zeus/core/static/viz/index.html`
- Already serves on `/viz`
- Connect to WebSocket, update UI based on state events

---

## Phase 4: MCP Server Implementation

### What is MCP?

Model Context Protocol = a standardized way for tools (like Claude Desktop, Cursor) to expose capabilities to LLMs.

**Zeus exposes:**
1. `context/query` — semantic search over your knowledge base
2. `memory/search` — search your memory (hybrid vector+graph)
3. `ingest/trigger` — ingest new data from specified source

### Architecture

```
Claude Desktop / Cursor
    ↓ [MCP Protocol over stdio/HTTP]
Zeus MCP Server
    ↓
FastAPI (Phase 2 Context API)
    ↓
Qdrant + Ollama
```

### Tasks (Priority Order)

#### Phase 4a: MCP Server Skeleton (LAB-104)

**Key File:** `zeus/mcp/server.py`
```python
from mcp.server import Server

server = Server("Zeus Context Server")

# Tool definitions registered here
```

**Setup:**
- MCP SDK installation
- Server init with tool registry
- Stdio transport (for Claude Desktop) + HTTP transport (for testing)

**Test:**
```bash
python -m zeus.mcp.server
# Should start listening for MCP calls
```

#### Phase 4b: Tool Definitions (LAB-107)

**Tool 1: context/query**
```python
@server.tool()
def context_query(q: str, max_results: int = 5, include_metadata: bool = True):
    """
    Search your personal knowledge base.
    Returns relevant documents with source metadata.
    """
    # Call POST /context/query from Phase 2
```

**Tool 2: memory/search**
```python
@server.tool()
def memory_search(query: str, token_budget: int = 2000):
    """
    Search your hybrid memory (vector + graph + KV).
    Returns results with token budgeting.
    """
    # Call POST /memory/search from Phase 2
```

**Tool 3: ingest/trigger**
```python
@server.tool()
def ingest_trigger(source: str):
    """
    Trigger data ingestion from a source (chatgpt, markdown, email, etc).
    Returns ingestion status and chunk count.
    """
    # Call POST /ingest/trigger from Phase 2
```

#### Phase 4c: MCP Integration Testing (LAB-108)

**Test Framework:**
- MCP SDK provides test harness
- Simulate Claude Desktop / Cursor client
- Call each tool and verify responses

**Key Tests:**
- Can call `context/query` and get results
- Can call `memory/search` with token budgeting
- Can call `ingest/trigger` and monitor progress
- Metadata is properly formatted
- Error handling works (invalid query, source not found, etc.)

**Integration:**
```bash
# Start Zeus services
docker compose up -d

# Start MCP server
python -m zeus.mcp.server

# Test with MCP client
mcp_client = MCPClient("stdio", ["python", "-m", "zeus.mcp.server"])
result = mcp_client.call_tool("context/query", {"q": "what did i learn about AI?"})
```

---

## Key Files to Work On

### Phase 3

```
zeus/
├── voice/
│   ├── __init__.py
│   ├── state.py              ← done (voice-state protocol)
│   ├── stt.py                ← NEW: WhisperLiveKit client
│   ├── tts.py                ← NEW: Voicebox client
│   ├── wake_word.py          ← NEW: openWakeWord detector
│   └── pipeline.py           ← NEW: Orpheus orchestration
├── core/
│   ├── voice_ws.py           ← done (WebSocket plumbing)
│   ├── chat.py               ← add /voice/interact route
│   ├── main.py               ← wire in voice routes
│   └── static/viz/           ← done (visualization UI)
└── docker-compose.yaml       ← add whisper, voicebox containers
```

### Phase 4

```
zeus/
├── mcp/
│   ├── __init__.py
│   ├── server.py             ← NEW: MCP server skeleton
│   ├── tools/
│   │   ├── context.py        ← NEW: context/query tool
│   │   ├── memory.py         ← NEW: memory/search tool
│   │   └── ingest.py         ← NEW: ingest/trigger tool
│   └── integration_test.py    ← NEW: MCP integration tests
└── docker-compose.yaml       ← may add for testing
```

---

## Docker Services to Add

### Phase 3: Voice Loop

```yaml
# compose.yaml additions

services:
  # STT: WhisperLiveKit
  whisper:
    image: onerahmet/openai-whisper-api:latest
    container_name: zeus-whisper
    ports:
      - "${WHISPER_PORT:-9000}:9000"
    environment:
      - WHISPER_MODEL=base  # or tiny, small, medium, large
    restart: unless-stopped
    networks:
      - web

  # TTS: Voicebox REST wrapper
  voicebox:
    image: voicebox/api:latest  # custom image wrapping LuxTTS
    container_name: zeus-voicebox
    ports:
      - "${VOICEBOX_PORT:-8080}:8080"
    environment:
      - VOICE_CLONING=true
      - SAMPLE_RATE=22050
    restart: unless-stopped
    networks:
      - web

  # Wake Word: openWakeWord
  # (Runs as standalone service, publishes to Phaos via HTTP/WebSocket)
  wake_word:
    build:
      context: .
      dockerfile: zeus/voice/Dockerfile.wake_word
    container_name: zeus-wake-word
    environment:
      - PHAOS_WEBSOCKET_URL=ws://zeus-core:8000/voice/ws
      - WAKE_PHRASE=hey zeus
    depends_on:
      - zeus-core
    restart: unless-stopped
    networks:
      - web
```

---

## Environment Variables

Add to `.env`:

```env
# Phase 3: Voice
WHISPER_PORT=9000
WHISPER_MODEL=base  # tiny, small, medium, large
VOICEBOX_PORT=8080
VOICE_CLONING=true
WAKE_PHRASE="hey zeus"
PHAOS_WEBSOCKET_URL=ws://zeus-core:8000/voice/ws

# Phase 4: MCP
MCP_TRANSPORT=stdio  # or http
MCP_PORT=5005
```

---

## Testing & Validation

### Phase 3: Voice Loop

**Unit Tests**
- STT: Transcribe sample audio, verify output format
- TTS: Generate speech from text, verify audio quality
- Wake word: Detect wake phrase in audio samples
- Pipeline: Mock STT/TTS, verify orchestration flow

**Integration Tests**
- End-to-end: mic → STT → query → TTS → speaker
- Phaos updates during interaction
- Error handling (no audio, STT timeout, TTS failure)

**Smoke Tests**
```bash
# Start all services
docker compose up -d

# Test STT
curl -X POST http://localhost:9000/asr \
  -H "Content-Type: audio/wav" \
  --data-binary @test.wav

# Test TTS
curl -X POST http://localhost:8080/speak \
  -H "Content-Type: application/json" \
  -d '{"text": "hello"}'

# Test voice interaction endpoint
curl -X POST http://localhost:8203/voice/interact \
  -H "Content-Type: audio/wav" \
  --data-binary @question.wav > response.wav

# Test Phaos visualization
open http://localhost:8203/viz
# (should show voice state updates as you speak)
```

### Phase 4: MCP Server

**Unit Tests**
- Tool schemas are valid MCP format
- Tool calls are properly serialized/deserialized
- Error responses follow MCP spec

**Integration Tests**
- MCP client can discover tools
- Can call `context/query` and get results
- Can call `memory/search` with metadata
- Can call `ingest/trigger` and monitor progress
- Supports stdio transport (Claude Desktop)
- Supports HTTP transport (testing)

**Smoke Tests**
```bash
# Start Zeus services
docker compose up -d

# Start MCP server
python -m zeus.mcp.server

# Test with MCP SDK client
python -c "
from mcp.client import ClientSession
client = ClientSession()
# Discover tools
tools = client.list_tools()
# Call tool
result = client.call_tool('context_query', {'q': 'what did i say about memory?'})
print(result)
"
```

---

## Implementation Notes

### Phase 3 Architecture Decisions

**Why WhisperLiveKit over other STT?**
- Real-time streaming (lower latency)
- Runs locally or on-prem
- Handles multiple languages
- Good accuracy for personal use

**Why Voicebox?**
- 150x realtime speed (conversational TTS latency)
- Voice cloning (personalization)
- Runs on consumer GPUs
- Better than Coqui/Bark for quality

**Why openWakeWord?**
- CPU-efficient (always-on detection)
- Customizable wake phrase
- No cloud calls
- False positive rate tunable

**Phaos (Visualization) Strategy:**
- WebSocket publishes state events
- Frontend renders real-time visualization
- Shows: waveform, transcript, response, latency
- Useful for debugging + user experience

### Phase 4 Architecture Decisions

**Why MCP?**
- Standardized tool protocol (Claude Desktop, Cursor, others)
- Exposes Zeus capabilities without re-implementing
- Can add new tools easily (agents, reports, etc.)
- Integrates with existing LLM workflows

**Tool Design:**
- `context/query` — most powerful tool (semantic search over all knowledge)
- `memory/search` — specialized (token budgeting for agent context)
- `ingest/trigger` — admin/maintenance (add new data sources)

**Transport:**
- **stdio** for Claude Desktop (automated discovery)
- **HTTP** for testing + Cursor integration

---

## Commit Message Format

```bash
# Phase 3 STT
git checkout -b chrislawrencedev/LAB-51-whisper-stt-integration
git commit -m "Integrate WhisperLiveKit for real-time speech-to-text

- WhisperSTTClient with streaming support
- Language detection and confidence scoring
- Docker compose service for Whisper server
- Basic smoke tests

(LAB-51)"

# Phase 3 Voice Pipeline
git checkout -b chrislawrencedev/LAB-55-orpheus-voice-pipeline
git commit -m "Implement end-to-end voice interaction pipeline

- Wake word detection → STT → query → TTS → speaker
- Phaos WebSocket integration for state updates
- /voice/interact endpoint for voice queries
- Error handling and timeout management

Depends on LAB-51, LAB-52, LAB-53, LAB-54
(LAB-55)"

# Phase 4 MCP
git checkout -b chrislawrencedev/LAB-104-mcp-server
git commit -m "Implement MCP server for Claude Desktop integration

- MCP server skeleton with stdio transport
- Tool definitions (context/query, memory/search, ingest/trigger)
- Integration tests with MCP SDK client

Depends on Phase 2 (query engine, context API)
(LAB-104, LAB-107, LAB-108)"
```

---

## Dependency Chain

```
Phase 2 (Data Brain)
    ↓ [Query Engine, Context API]
Phase 3a (STT)
    ↓
Phase 3b (TTS)
    ↓
Phase 3c (Wake Word)
    ↓
Phase 3d (Orpheus Pipeline)
    ↓
Phase 3e (Phaos Viz)

    (In Parallel: Phase 4 MCP Server)
```

**Critical Path:** Phase 2 → Phase 3a → Phase 3d (can skip 3b, 3c for text-only MVP)

---

## Testing Scenarios

### Happy Path: Voice Query

1. User says: "Hey Zeus, what did I discuss about memory systems?"
2. Wake word detected → Phaos shows `listening`
3. Audio captured until VAD detects silence
4. STT transcribes: "What did I discuss about memory systems?"
5. Phaos shows `transcribing` with confidence
6. Query engine searches Qdrant
7. Phaos shows `thinking`
8. LLM generates response: "You discussed vector databases, hybrid storage..."
9. TTS generates audio
10. Phaos shows `speaking`
11. Audio plays to speaker
12. Phaos returns to `idle`

### Error Case: STT Timeout

1. User is silent for >30s
2. STT timeout
3. Phaos shows `error: speech timeout`
4. Return to listening state
5. User can retry

### MCP Integration

1. User opens Claude Desktop
2. MCP server exposes `context/query` tool
3. User asks Claude: "What did I learn about X?"
4. Claude calls `context/query` with user query
5. Zeus returns search results
6. Claude synthesizes response from results

---

## Reference Docs

- **Phase 2 Context:** `docs/PHASE2_CURSOR_PROMPT.md`
- **Architecture & Standards:** `CLAUDE.md`
- **Full Roadmap:** `docs/zeus_linear_ticket_plan.md`
- **MCP Specification:** https://spec.modelcontextprotocol.io/
- **OpenAI Whisper API:** https://openai.com/research/robust-speech-recognition
- **Voicebox Docs:** (internal or research paper)
- **openWakeWord:** https://github.com/dscripka/openWakeWord

---

## Questions to Ask While Implementing

**Phase 3:**
1. Should wake word detection be always-on or triggered manually?
2. What audio device do we listen to? (system microphone, virtual loopback, etc.)
3. How long should we wait for VAD silence before ending recording? (1s, 2s?)
4. Should we support voice cloning? (requires speaker embeddings)
5. How should we handle multiple concurrent voice queries?

**Phase 4:**
1. Should MCP tools be read-only or allow mutations (ingest/trigger)?
2. How should we handle large result sets in MCP responses?
3. Should MCP server be a separate process or integrated into Zeus Core?

---

## How to Use This in Cursor

1. Copy this entire prompt
2. Open Cursor → New Chat
3. Paste the prompt
4. Ask specific questions like:
   - "Help me implement the WhisperLiveKit STT client"
   - "What's the best way to structure the Orpheus pipeline?"
   - "Design the MCP tool schemas for context/query and memory/search"
   - "Write the integration tests for the voice pipeline"
   - "Review this code for compliance with code standards"

Cursor will have full context and can provide implementation-ready code.

---

**Last Updated:** 2026-03-25
**Estimated Timeline:** Phase 3 (voice) ~3-4 weeks, Phase 4 (MCP) ~2 weeks
**Critical Blocker:** Phase 2 must be complete before starting Phase 3 or 4