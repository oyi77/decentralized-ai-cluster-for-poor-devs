# Decentralized AI Cluster for Broke Developers

> Run LLMs like a 1-man company — even if all you have is an old laptop, a GTX 1050, or a Raspberry Pi.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
![Python](https://img.shields.io/badge/python-3.10%2B-blue)
![Made for Kali/Ubuntu/Debian](https://img.shields.io/badge/Linux-Kali%2FUbuntu%2FDebian-green)

**Decentralized AI Cluster for Broke Developers** (DAICBD — yeah we need a shorter name) is an open-source project that turns multiple cheap, old devices into a single AI inference cluster. No RTX 4090. No $500/month API bill. No cloud lock-in.

---

## Why This Exists

Most AI tools today assume you either:
- Own an RTX 4090 / A100, or
- Pay OpenAI/Anthropic/Google every month.

That leaves out millions of solo founders, indie hackers, and 1-man company builders — especially in places where hardware and cloud APIs are expensive.

This project is for people who:
- Have an old gaming laptop with a 4GB GPU
- Bought a used GTX 1650 or RTX 2060
- Have a Raspberry Pi or Intel NUC sitting around
- Want to run local LLMs for coding, customer support, content, and automation
- Refuse to pay recurring API fees for basic AI tasks

---

## What It Does

```
Your 1-Man Company Dashboard
         │
         ▼
    Cluster Router
    (picks the best device + model)
         │
    ┌────┴────┐
    ▼         ▼         ▼
Laptop 1   PC B     Old PC C
GTX 1650   RTX 2060  iGPU/CPU
4 GB VRAM  8 GB VRAM  CPU only
qwen1.5b   qwen7b    qwen1.5b
```

The router sends each task to the cheapest device that can handle it:
- **Customer chat / auto-reply** → tiny 1.5B model on any device
- **Coding assistant / one-file refactor** → 7B coding model on the best GPU
- **Long-context planning / reasoning** → optional free cloud fallback
- **Invoice extraction / data parsing** → 3B model, CPU-friendly

---

## Features

- **No cloud required** — run everything on your LAN
- **Device auto-discovery** — register old PCs and laptops as cluster nodes
- **Task router** — matches prompt complexity to available hardware
- **Agent templates** — ready workflows for 1-man companies:
  - WhatsApp/Telegram customer auto-reply
  - Product caption generator
  - Python/JS coding assistant
  - Meeting notes summarizer
  - Invoice field extractor
- **One-command node installer** — detects GPU, downloads the right model
- **OpenAI-compatible API** — drop-in for Continue.dev, OpenWebUI, Cursor, etc.

---

## Quick Start

### 1. Start the cluster router (on your main machine)

```bash
cd cluster_router
pip install -r requirements.txt
python main.py
# or: uvicorn main:app --host 0.0.0.0 --port 8000
```

### 2. Add a node (on any old device)

Make sure `llama.cpp` is installed with `llama-server`. Then:

```bash
cd scripts
ROUTER_URL=http://MAIN_MACHINE_IP:8000 ./install_node.sh
```

This script will:
- Detect your GPU / CPU
- Download the best-fitting GGUF model
- Start `llama-server`
- Register the device to the router
- Keep a heartbeat alive

### 3. Run a workflow

```bash
cd agent_templates
pip install -r requirements.txt
python workflows.py
```

Or call the cluster API directly:

```bash
curl -X POST http://localhost:8000/v1/chat/completions \
  -H 'Content-Type: application/json' \
  -d '{
    "messages": [{"role":"user","content":"buatkan fungsi python validasi email"}],
    "task_type": "code"
  }'
```

---

## Minimum Hardware

| Device | GPU / RAM | Can Run | Role in Cluster |
|---|---|---|---|
| Old laptop | Intel iGPU / 8 GB RAM | 1.5B Q4 model | Customer reply, caption |
| GTX 1050 Ti | 4 GB VRAM | 1.5B–3B Q4 | Small coding, parsing |
| GTX 1650 / 1060 6GB | 4–6 GB VRAM | 3B–7B Q4 | General coding assistant |
| RTX 2060 / 3050 | 6–8 GB VRAM | 7B–8B Q4 | Main coding node |
| 2× RTX 2060 / 3060 | 12–16 GB total | 13B sharded | Heavy reasoning |
| CPU-only 16 GB RAM | CPU | 1.5B–3B slow | Fallback node |

---

## Project Structure

```
decentralized-ai-cluster-for-poor-devs/
├── cluster_router/      # Task router + node registry
├── cluster_nodes/       # Node daemon + hardware detection
├── agent_templates/     # 1-man company workflows
├── scripts/             # One-command installer
├── examples/            # Usage examples
├── docs/                # Guides in English + Bahasa Indonesia
└── tests/               # Smoke + benchmark tests
```

---

## Roadmap

- [x] Router with model-to-node matching
- [x] Node daemon with GPU detection
- [x] Starter agent templates
- [ ] llama.cpp RPC sharding for 7B+ across 2 devices
- [ ] LAN auto-discovery (mDNS)
- [ ] Web dashboard
- [ ] Continue.dev / OpenWebUI plugin
- [ ] RAG pipeline for codebase indexing
- [ ] Benchmarks on GTX 1650 / RTX 2060 mixed clusters

---

## Contributing

This is a project for broke developers by broke developers. PRs welcome, especially:
- Better routing logic
- Cheaper/faster GGUF defaults
- Agent templates for local businesses
- Setup guides for non-technical users
- Indonesian language docs

---

## License

MIT — use it, fork it, sell tools built on top of it.

---

## Related / Inspired By

- [llama.cpp](https://github.com/ggerganov/llama.cpp)
- [Ollama](https://ollama.com/)
- [exo](https://github.com/exo-explore/exo)
- [Petals](https://github.com/petals-infra/chat.petals.dev)

---

## Keywords

local llm cluster, cheap ai inference, distributed llm at home, poor man ai cluster, low budget llm, gtx 1650 llm, rtx 2060 llm, 1 man company ai, indie hacker ai, open source ai agent, offline ai, no api key ai, Indonesia ai developer
