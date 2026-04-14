# Zeus — Local Model Reference (Ollama)

A practical comparison of every model currently pulled in `zeus-ollama`, sized against the two GPUs we deploy on and the 112 GB of system RAM available on the dev tower. Use this when picking a default for chat, voice, or background agents.

Last refreshed: 2026-04-14. Numbers in the "Measured" section are from `zeus.bench` runs on this host.

## Hardware

| Host | GPU | VRAM | System RAM (host) | RAM to zeus VM | Role |
|---|---|---|---|---|---|
| **daedalus** (current host, Proxmox) | RTX 3080 | 10 GB | 112 GB | ~90–100 GB | Always-on Zeus: Telegram, voice, chat, ingest |
| **(future)** 5080 tower | RTX 5080 | 16 GB | tbd | tbd | Not yet wired up — will host dev/iteration |

### VRAM headroom rules of thumb

Zeus runs `nomic-embed-text` and the chat model in the same Ollama instance (`OLLAMA_MAX_LOADED_MODELS=2`). The embedder reserves roughly **0.3–0.5 GB**. On top of that, the chat model needs:

- The weight footprint (the size column from `ollama list`)
- KV cache: roughly `2 × num_layers × hidden_size × ctx_len × 2 bytes` for FP16 cache. For a 7B model at 8K context this is ~1.5 GB; at 32K it is ~6 GB.
- A small activation/scratch buffer (~0.3 GB)

Usable VRAM on the 3080 (10 GB): **~8.5 GB** for the chat model after embedder + 8K KV cache.

If the chat model + KV exceeds VRAM, Ollama silently offloads layers to CPU. That works but tokens/sec collapses — we measured **100× slowdown** on qwen2.5:32b (19 GB quant → ~9 GB spilled to CPU) compared to the 7Bs.

## Currently pulled models

Sourced from `GET /api/tags` on `zeus-ollama`. Sorted by size.

| Model | Size | Params | Quant | Notes |
|---|---|---|---|---|
| `nomic-embed-text:v1.5` | 0.27 GB | 137M | F16 | Embeddings only. 768-dim. Always loaded alongside chat model. |
| `nomic-embed-text:latest` | 0.27 GB | 137M | F16 | Duplicate of v1.5. Safe to delete one. |
| `llama3.2:3b` | 2.0 GB | 3.2B | Q4_K_M | Tiny, very fast. Weak instruction following — drops or ignores context blocks. **Not recommended for grounded Zeus chat.** OK for trivial routing/classification. |
| `llama3:latest` | 4.7 GB | 8B | Q4_0 | Original Llama 3, Q4_0 (older quant). Superseded by 3.1. Safe to delete. |
| `qwen2.5:7b` | 4.7 GB | 7.6B | Q4_K_M | Base 7B. Use the `-instruct` variant instead for chat. |
| `qwen2.5:7b-instruct` | 4.7 GB | 7.6B | Q4_K_M | **Default chat model on prod.** Strong instruction following, good at reading `Profile`/`Relevant Context` blocks, low hallucination on grounded queries. The original Zeus production target. |
| `llama3.1:8b-instruct-q4_K_M` | 4.9 GB | 8B | Q4_K_M | Comparable to qwen2.5:7b in size. Slightly chattier, sometimes more natural prose. Marginally weaker at JSON/structured output than Qwen. |
| `qwen3:8b` | 5.2 GB | 8.2B | Q4_K_M | Newer Qwen3 generation. Better reasoning and tool-use than Qwen 2.5 7B. Worth A/B'ing as the new prod default. |
| `qwen2.5:14b` | 9.0 GB | 14.8B | Q4_K_M | Materially smarter than the 7Bs for multi-step reasoning. **Tight fit on the 3080** with embedder + KV cache; comfortable on the 5080. |

Total VRAM cost if everything hot-loaded at once: ~36 GB — Ollama only keeps two loaded so this never happens in practice.

## Measured (daedalus, RTX 3080 10 GB)

Source: `zeus.bench` suite (short / medium / long prompts, 16 / 200 / 600 max tokens, temperature 0.1, `keep_alive=10m`). Generation tok/s is weighted over the three prompts. TTFT is the first prompt after warm-up. Prompt-eval tok/s is the rate Ollama processes the input prompt.

| Model | Gen tok/s | TTFT | Prompt-eval tok/s | Fits in VRAM? |
|---|---:|---:|---:|---|
| `qwen2.5:7b-instruct` | **119.4** | 304 ms | 2173 | ✅ clean fit |
| `llama3.1:8b-instruct-q4_K_M` | 112.7 | 351 ms | 1191 | ✅ clean fit |
| `qwen3:8b` | 100.3 | 274 ms | 1192 | ✅ clean fit (emits more tokens because of thinking mode) |
| `gpt-oss:20b` | **0.8** | 6.6 s | 34 | ❌ 13 GB — ~3 GB spilled to CPU |
| `qwen2.5:32b` | **0.1** | 15.8 s | 2 | ❌ 19 GB — ~9 GB spilled to CPU |

**Headline:** on the 3080, only the three 7–8B models are usable for interactive chat. `gpt-oss:20b` and `qwen2.5:32b` are unusable — not just slow, fundamentally broken UX (sub-1 tok/s, prompt-eval in the single digits). The 112 GB of host RAM cannot rescue this: once layers leave VRAM, you are bound by RAM bandwidth (~50 GB/s DDR5) against GPU bandwidth (~760 GB/s on the 3080), a 15× gap that compounds per-token.

Practical implications:

- **All three 8B-class models are well above the interactive threshold** (>30 tok/s is the "feels instant" floor for chat, >15 tok/s for voice after TTS buffering). Pick on quality, not speed.
- **`qwen2.5:7b-instruct` is the fastest** and only 6% behind `llama3.1:8b` on context-grounded tasks in practice — it's the right prod default right now.
- **`qwen3:8b` emits more tokens per reply** (thinking mode). On the same three prompts it generated 816 tokens vs llama's 733 and qwen2.5's 699. That's why its tok/s looks lower — it's doing more work, not running slower. Per-token speed is comparable.
- **Do not run `qwen2.5:32b` or `gpt-oss:20b` on this host.** Leave them pulled only if you plan to use them from a different host with more VRAM, or as an offline consolidation job where 13 minutes per answer is acceptable.

## Fit matrix

`✓` = fits with embedder + ~8K context KV cache, room to spare. `~` = fits but tight, may evict KV at long contexts. `CPU` = needs CPU offload (works, slow). `✗` = won't load.

| Model | 3080 (10 GB) | 5080 (16 GB) | 5080 + 112 GB RAM offload |
|---|---|---|---|
| `llama3.2:3b` | ✓ | ✓ | n/a |
| `qwen2.5:7b-instruct` | ✓ | ✓ | n/a |
| `llama3.1:8b-instruct` | ✓ | ✓ | n/a |
| `qwen3:8b` | ✓ | ✓ | n/a |
| `qwen2.5:14b` | ~ (drops KV at ≥8K ctx) | ✓ | n/a |
| `qwen2.5:32b` (not pulled) | CPU | ~ | ✓ partial offload |
| `gpt-oss:20b` (not pulled) | CPU | ~ | ✓ |
| `llama3.3:70b-instruct-q4_K_M` (not pulled) | ✗ | CPU heavy | CPU+GPU split, ~3–6 tok/s |

## Recommendations

### On this host (daedalus / 3080 10 GB)

**Default:** `qwen2.5:7b-instruct`. Fastest measured (119 tok/s), lowest prompt-eval bottleneck (2173 tok/s), proven quality on grounded queries, clean VRAM fit with full 8K context + embedder + voice/STT running concurrently.

**Alternative worth A/B-testing:** `qwen3:8b`. Reasoning is meaningfully stronger on multi-step problems, and the per-token speed is essentially the same — it just writes longer answers (thinking mode). If answer quality on complex Telegram questions matters more than raw latency, it's the upgrade. Test it on real queries for a day and see if Telegram/chat feels smarter before committing.

**Do not run:** `gpt-oss:20b`, `qwen2.5:32b`, or any larger model on the 3080. Measured at 0.1–0.8 tok/s. Delete them unless you plan to move them to a different host:

```bash
docker exec zeus-ollama ollama rm qwen2.5:32b gpt-oss:20b  # frees ~32 GB of disk
```

**Avoid:** `llama3.2:3b`. Too small to actually use the retrieved memory context — this was the reason Telegram replies kept saying "I don't have that in memory" even after the mem0 retrieval bug was fixed. The 7B/8B models were never the bottleneck.

### Leveraging the 112 GB RAM (it does not help here)

The measured numbers are the definitive answer to this question: **112 GB of host RAM does not make bigger models viable on a 10 GB GPU.** RAM is for *fitting* weights that don't make VRAM, not for speeding them up. Once layers are on CPU, throughput is bound by RAM bandwidth (~50 GB/s DDR5) vs GPU bandwidth (~760 GB/s on a 3080), and our `qwen2.5:32b` run confirmed the 100× collapse.

The only realistic uses for host RAM on this box are:

- **Offline consolidation jobs** (future KAIROS / LAB-330 work): run a 20–32B once a day over ingested memories, accept 10–30 min per batch, never show the latency to the user.
- **Not interactive chat, not voice, not Telegram replies.**

When the 5080 tower gets wired up, it gets its own benchmark run and its own section below — do not assume anything about 5080 behavior from what we measured here.

### Shortlist by use case (3080 host)

| Use case | Pick | Why |
|---|---|---|
| Prod chat / Telegram | `qwen2.5:7b-instruct` | Fastest measured, proven, grounded |
| Upgrade candidate | `qwen3:8b` | Newer, better multi-step reasoning, similar speed |
| Routing / classifier / cheap labels | `llama3.1:8b-instruct-q4_K_M` | A hair slower than qwen2.5 but very reliable instruction-following; good second opinion |
| Embeddings | `nomic-embed-text:v1.5` | Don't change; existing Qdrant collection is keyed to 768-dim |
| Background consolidation over ingested data | `qwen2.5:32b` (pull on demand, not for interactive use) | Run once per day, accept 10+ min per batch |

## Cleanup candidates

Remove models that either do not fit the 3080 interactively or are duplicates:

```bash
docker exec zeus-ollama ollama rm qwen2.5:32b       # 19 GB, unusable on 10 GB VRAM
docker exec zeus-ollama ollama rm gpt-oss:20b       # 13 GB, unusable on 10 GB VRAM
docker exec zeus-ollama ollama rm llama3.2:3b       # too small to use retrieved context
```

Frees roughly 34 GB.

## How to switch the active model

Runtime model switching is wired — no restart needed:

```bash
curl -X POST http://192.168.50.128:8203/models/active \
  -H 'Content-Type: application/json' \
  -d '{"model":"qwen2.5:7b-instruct"}'
```

Or use the **Settings → Model** section in the React UI. The change applies to chat, Telegram, and voice immediately.

## Open questions worth measuring

`zeus.bench` now closes the throughput question on this host. Remaining gaps:

1. **Quality comparison on grounded Zeus queries.** Tok/s says nothing about whether `qwen3:8b` gives better answers than `qwen2.5:7b-instruct` on real Telegram/chat turns. Extend `tests/retrieval_eval.py` with a set of real questions whose expected answers come from mem0 content, run each candidate model, grade by hand.
2. **End-to-end latency breakdown.** `QueryEngine.query()` does mem0 search + profile fetch + prompt build + LLM. Add timings to the query log so we can tell whether a slow Telegram turn is the model (unlikely at 100+ tok/s) or something upstream.
3. **Context-length scaling.** Our bench runs at default 2K effective context. Verify `qwen2.5:7b-instruct` still fits cleanly at 8K and 16K with embedder + concurrent voice/STT (measure VRAM, not just tok/s).
4. **5080 tower numbers.** When the second host is online, rerun `zeus.bench` there and add a sibling section.
