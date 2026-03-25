# Zeus — Linear Ticket Plan (Revised)

Full ticket structure for the Zeus project. Incorporates feedback on sprint ordering, Phaos subsystem, retrieval eval, collection versioning, and dependency awareness.

**Team:** Chris Lawrence Homelab
**Linear Projects:** Zeus 0–8 + Backlog

## Labels


| Label     | Color   | Subsystem                                              |
| --------- | ------- | ------------------------------------------------------ |
| mnemosyne | #7C3AED | Memory layer — mem0 + Qdrant                           |
| iris      | #10B981 | Ingest pipeline — data sources → chunks                |
| orpheus   | #F59E0B | Voice interface — STT, TTS, wake word                  |
| aegis     | #EF4444 | Safety layer — NemoClaw + OpenShell                    |
| oracle    | #3B82F6 | Zeus Context API — structured context                  |
| olympians | #EC4899 | Agent swarm — Ruflo-managed agents                     |
| phaos     | #06B6D4 | Voice-state visualization — Three.js, WebSocket, WebXR |


---

## Revised Sprint Ordering

Key changes from v1:

1. **Sessions & Chat moved to Project 1** — dev acceleration, text interface before voice
2. **Query Engine moved to Project 2** — it's the brain, not voice-specific
3. **MCP Server moved to Project 4** — use during agent development
4. **Phaos added as subsystem** — existing code tracked, future work planned
5. **Retrieval eval suite added** — ground-truth queries for tuning
6. **Collection versioning added** — Qdrant migration strategy
7. **Email ingest moved to Project 2** — it's a data source, not a deploy concern
8. **Ruflo validation spike added** — verify before betting architecture on it

---

## Project 0 — Foundation (Mostly Complete)


| Parent  | Title                              | Labels             | Subs |
| ------- | ---------------------------------- | ------------------ | ---- |
| LAB-43  | Repository & Dev Environment Setup | Feature, oracle    | 4    |
| LAB-130 | Qdrant & Ollama Infrastructure     | Feature, mnemosyne | 3    |
| LAB-134 | mem0 Initial Setup                 | Feature, mnemosyne | 3    |
| LAB-117 | Voice Tooling Validation           | Feature, orpheus   | 3    |
| LAB-135 | ChatGPT Data Export                | Feature, iris      | 2    |
| LAB-121 | Validate Ruflo v3.5 (spike)        | Feature, olympians | 0    |


## Project 1 — Text Chat + Sessions

**Status (24 Mar 2026):** Phase 1 shipped — `zeus/core/sessions.py`, `zeus/core/query.py`, chat SSE + session APIs + `chat.html` upgrades. Mark **LAB-184** and **LAB-187** done in Linear when validated.

| Parent  | Title               | Labels          | Subs |
| ------- | ------------------- | --------------- | ---- |
| LAB-184 | Session Layer       | Feature, oracle | 5    |
| LAB-187 | Text Chat Interface | Feature, oracle | 5    |


## Project 2 — Data Brain

**Status (24 Mar 2026):** **LAB-49 (Query Engine)** implemented as `zeus/core/query.py` (shared brain for chat + future voice). Mark **LAB-49** done in Linear after your smoke tests.

| Parent | Title                                | Labels             | Subs |
| ------ | ------------------------------------ | ------------------ | ---- |
| LAB-45 | ChatGPT Export Parser                | Feature, iris      | 5    |
| LAB-46 | Markdown File Walker                 | Feature, iris      | 5    |
| LAB-47 | Context-Pack Migration               | Feature, iris      | 4    |
| LAB-48 | Zeus Context API v1 (Oracle)         | Feature, oracle    | 6    |
| LAB-49 | Zeus Query Engine                    | Feature, oracle    | 4    |
| LAB-61 | mem0 Integration & Retrieval Quality | Feature, mnemosyne | 6    |
| LAB-56 | Privacy & Data Governance            | Feature, aegis     | 5    |
| LAB-64 | Phase 2 Data Sources — Email Ingest  | Feature, iris      | 4    |


## Project 3 — Voice Loop


| Parent | Title                           | Labels           | Subs |
| ------ | ------------------------------- | ---------------- | ---- |
| LAB-51 | WhisperLiveKit STT Setup        | Feature, orpheus | 4    |
| LAB-52 | openWakeWord Integration        | Feature, orpheus | 4    |
| LAB-53 | Voicebox TTS Client             | Feature, orpheus | 4    |
| LAB-54 | Phaos Voice-State Visualization | Feature, phaos   | 5    |
| LAB-55 | Voice Pipeline End-to-End       | Feature, orpheus | 5    |


## Project 4 — MCP Server


| Parent  | Title                   | Labels          | Subs |
| ------- | ----------------------- | --------------- | ---- |
| LAB-104 | MCP Server Core         | Feature, oracle | 4    |
| LAB-107 | MCP Tool Definitions    | Feature, oracle | 5    |
| LAB-108 | MCP Integration Testing | Feature, oracle | 4    |


## Project 5 — Ruflo Agents


| Parent  | Title                          | Labels             | Subs |
| ------- | ------------------------------ | ------------------ | ---- |
| LAB-112 | Ruflo Initialization           | Feature, olympians | 3    |
| LAB-113 | Zeus Personal Agent            | Feature, olympians | 4    |
| LAB-114 | Zeus Dev Agent                 | Feature, olympians | 4    |
| LAB-116 | Zeus Research Agent            | Feature, olympians | 4    |
| LAB-119 | NemoClaw Safety Layer (Aegis)  | Feature, aegis     | 5    |
| LAB-120 | Multi-Agent Orchestration Test | Feature, olympians | 4    |


## Project 6 — Deploy to Olympus


| Parent  | Title                           | Labels           | Subs |
| ------- | ------------------------------- | ---------------- | ---- |
| LAB-124 | Docker Compose Production Stack | Feature, oracle  | 4    |
| LAB-128 | Server Deployment               | Feature, oracle  | 4    |
| LAB-140 | Always-On Service Mode          | Feature, oracle  | 4    |
| LAB-141 | Server Voice Pipeline           | Feature, orpheus | 4    |


## Project 7 — Orchestration Runtime


| Parent  | Title                   | Labels             | Subs |
| ------- | ----------------------- | ------------------ | ---- |
| LAB-144 | Agent Runtime Engine    | Feature, olympians | 4    |
| LAB-145 | Agent Communication Bus | Feature, olympians | 4    |
| LAB-146 | Orchestration Hooks     | Feature, olympians | 4    |


## Project 8 — Observability + Admin


| Parent  | Title              | Labels          | Subs |
| ------- | ------------------ | --------------- | ---- |
| LAB-147 | Metrics Collection | Feature, oracle | 4    |
| LAB-148 | Admin API Routes   | Feature, oracle | 4    |
| LAB-149 | Admin Dashboard    | Feature, oracle | 4    |


## Backlog


| Title                                        | Labels             |
| -------------------------------------------- | ------------------ |
| VR Prototype — Zeus voice + avatar in Oculus | Feature, orpheus   |
| Meta AR Glasses Integration                  | Feature, orpheus   |
| Watch Vitals Integration                     | Feature, iris      |
| Web Dashboard                                | Feature, oracle    |
| Business Productization                      | Feature            |
| Model Fine-Tuning                            | Feature, mnemosyne |
| Graph Memory (mem0g)                         | Feature, mnemosyne |
| Memory Decay Policy                          | Feature, mnemosyne |


**Note:** Some Project 7/8 sub-issues and all Backlog items hit the Linear workspace issue limit. These need to be created after upgrading or archiving old issues.

---

## Key Dependencies

- **LAB-48 (Context API)** blocks Projects 3, 4, 5, 6, 7, 8
- **LAB-184 (Session Layer)** blocks chat interface + voice pipeline
- **LAB-49 (Query Engine)** blocks voice pipeline + agents
- **LAB-121 (Ruflo Spike)** blocks Project 5 architecture

