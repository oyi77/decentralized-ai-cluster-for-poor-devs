# Poor Man's AI Cluster — 1-Man Company Engine

## Problem
- Solo founders / 1-man company in Indonesia cannot afford RTX 4090 / cloud API at scale.
- Many already own: old laptop, GTX 1050/1650, RTX 2060 8GB, Intel iGPU, Raspberry Pi.
- Single device is too weak for agentic coding + business automation.

## Solution
Build a **decentralized / home-cluster inference layer** that turns multiple cheap devices into one virtual AI engine.

## Core Architecture

```
User / 1-Man Company Dashboard
    │
    ▼
[ Task Router ]
  ├── tiny  : 1B–3B model on weakest device (reply WA, rewrite caption)
  ├── medium: 7B sharded across 2–3 mini GPUs (coding assistant)
  ├── large : 13B–30B via CPU-offload + distributed devices (rare)
  └── cloud : fallback to free tier API for critical long-context task
    │
    ▼
[ Cluster Orchestrator ]
  registers each device's VRAM / RAM / model loaded
  routes inference request to available shard
    │
    ▼
Device A (RTX 2060 8GB) ─┐
Device B (GTX 1650 4GB)  ─┼──► llama.cpp MPI / RPC / pipeline parallelism
Device C (Intel iGPU + CPU)┘
```

## Technical Stack Options

| Component | Option A | Option B | Option C |
|---|---|---|---|
| Distributed inference | llama.cpp MPI | exo | Petals (peer-to-peer) |
| Model format | GGUF Q4_K_M | GGUF Q4_0 | EXL2 |
| Orchestrator | custom FastAPI/Flask | Dify | n8n + custom node |
| Task routing | rule-based | LLM judge (tiny) | cost/latency optimizer |
| Discovery | local network mDNS | manual registry | simple JSON config |
| Storage | SQLite + file shares | NAS / SMB | local disk each |

## Realistic Device Tiers

| Tier | Devices | Models | Use Case |
|---|---|---|---|
| Tier 0 | 1 old laptop, iGPU/CPU | Qwen2.5 1.5B, Phi-4-mini | Chat simple, rewrite text |
| Tier 1 | 2 devices, 4–8GB VRAM | 7B sharded Q4_K_M | Coding assistant, 1-man ops |
| Tier 2 | 4–6 devices mixed | 13B sharded or 2×7B | Multi-agent company |
| Tier 3 | + free cloud burst | Gemini Flash, Groq | Long context, heavy reasoning |

## Minimum Viable Product (MVP)

1. **Cluster daemon** on each device
   - Report VRAM/RAM/model loaded
   - Expose local inference endpoint (llama.cpp server)

2. **Task router** on "main" machine
   - Receive request
   - Pick model + device(s) based on task complexity
   - Shard request if needed

3. **Starter workflows for 1-man company**
   - Auto-reply customer WhatsApp (tiny model)
   - Generate product caption (tiny model)
   - Coding assistant for one file (7B sharded)
   - Simple bookkeeping parser (small model + deterministic scripts)

4. **One-command installer**
   - Auto-detect GPU/CPU
   - Download matching GGUF
   - Start daemon

## Critical Tradeoffs

- Latency naik 2–5x vs single GPU besar.
- Setup lebih rumit dari Ollama biasa.
- Network (LAN) jadi bottleneck; WiFi bisa lemot.
- Model sharding di llama.cpp masih eksperimental untuk consumer mixed GPU.

## Next Steps

1. Validate llama.cpp RPC/MPI bisa shard 7B ke 2× RTX 2060.
2. Build tiny task router.
3. Build 3 starter workflows.
4. Write setup guide Bahasa Indonesia.
