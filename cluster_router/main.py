#!/usr/bin/env python3
"""
Decentralized AI Cluster — Task Router
Matches AI tasks to the cheapest node that can run them.
"""

import time
import httpx
import asyncio
from dataclasses import dataclass, field
from typing import Optional
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI(title="Decentralized AI Cluster Router")


@dataclass
class Node:
    id: str
    url: str
    gpu_vram_mb: int
    gpu_name: str = ""
    models: list = field(default_factory=list)
    last_seen: float = 0.0


class TaskRequest(BaseModel):
    messages: list[dict]
    task_type: str = "chat"        # chat | code | rewrite | summarize
    preferred_model: Optional[str] = None
    max_tokens: int = 512
    temperature: float = 0.7


NODES: dict[str, Node] = {}

# Approx VRAM in MB for Q4_K_M quantized models
MODEL_VRAM_MB = {
    "qwen2.5-1.5b": 1100,
    "qwen2.5-3b":   2200,
    "qwen2.5-7b":   5000,
    "llama3.1-8b":  5500,
    "mistral-7b":   4800,
    "deepseek-r1-7b": 5000,
    "qwen2.5-coder-7b": 5000,
    "qwen2.5-14b":  9000,
}


def pick_model_and_node(task: TaskRequest) -> tuple[str, str]:
    if task.preferred_model:
        model = task.preferred_model
    elif task.task_type in ("rewrite", "summarize", "chat-simple"):
        model = "qwen2.5-1.5b"
    elif task.task_type == "code":
        model = "qwen2.5-coder-7b"
    else:
        model = "qwen2.5-7b"

    required_vram = MODEL_VRAM_MB.get(model, 999999)

    candidates = []
    for node in NODES.values():
        if time.time() - node.last_seen > 60:
            continue
        if node.gpu_vram_mb >= required_vram and model in node.models:
            candidates.append(node)

    if candidates:
        best = min(candidates, key=lambda n: n.gpu_vram_mb)
        return model, best.id

    candidates = [
        n for n in NODES.values()
        if time.time() - n.last_seen <= 60 and n.gpu_vram_mb >= required_vram
    ]
    if candidates:
        best = min(candidates, key=lambda n: n.gpu_vram_mb)
        return model, best.id

    raise HTTPException(
        503,
        f"No node can run {model} (needs {required_vram}MB VRAM). "
        "Add a stronger node or reduce task complexity."
    )


@app.post("/v1/chat/completions")
async def chat_completions(req: TaskRequest):
    model, node_id = pick_model_and_node(req)
    node = NODES[node_id]

    payload = {
        "model": model,
        "messages": req.messages,
        "max_tokens": req.max_tokens,
        "temperature": req.temperature,
        "stream": False,
    }

    async with httpx.AsyncClient(timeout=300.0) as client:
        r = await client.post(f"{node.url}/v1/chat/completions", json=payload)
        r.raise_for_status()
        return r.json()


@app.get("/nodes")
async def list_nodes():
    return {
        nid: {
            "id": n.id,
            "url": n.url,
            "gpu_vram_mb": n.gpu_vram_mb,
            "gpu_name": n.gpu_name,
            "models": n.models,
            "last_seen": n.last_seen,
        }
        for nid, n in NODES.items()
    }


@app.post("/nodes/register")
async def register_node(payload: dict):
    node = Node(
        id=payload["id"],
        url=payload["url"],
        gpu_vram_mb=payload.get("gpu_vram_mb", 0),
        gpu_name=payload.get("gpu_name", ""),
        models=payload.get("models", []),
        last_seen=time.time(),
    )
    NODES[node.id] = node
    return {"status": "ok", "registered": node.id}


@app.post("/nodes/heartbeat")
async def heartbeat(node_id: str):
    if node_id not in NODES:
        raise HTTPException(404, "Node not found")
    NODES[node_id].last_seen = time.time()
    return {"status": "ok"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
