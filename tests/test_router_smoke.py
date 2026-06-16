#!/usr/bin/env python3
"""Smoke test: router routes task to a mock node."""

import sys
import time
sys.path.insert(0, "/home/openclaw/projects/decentralized-ai-cluster-for-poor-devs/cluster_router")

from main import pick_model_and_node, NODES, Node


def fresh_node(**kwargs):
    return Node(last_seen=time.time(), **kwargs)


def test_router_picks_smallest_capable_node():
    NODES.clear()
    NODES["cpu-node"] = fresh_node(id="cpu-node", url="http://localhost:8080", gpu_vram_mb=0, models=["qwen2.5-1.5b"])
    NODES["gtx-node"] = fresh_node(id="gtx-node", url="http://localhost:8081", gpu_vram_mb=4096, models=["qwen2.5-3b"])
    NODES["rtx-node"] = fresh_node(id="rtx-node", url="http://localhost:8082", gpu_vram_mb=8192, models=["qwen2.5-coder-7b"])

    class FakeTask:
        task_type = "code"
        preferred_model = None

    model, node_id = pick_model_and_node(FakeTask())
    assert model == "qwen2.5-coder-7b"
    assert node_id == "rtx-node", f"Expected rtx-node, got {node_id}"

    print("PASS: router picks smallest capable node")


def test_router_falls_back_to_loaded_model():
    NODES.clear()
    NODES["rtx-node"] = fresh_node(id="rtx-node", url="http://localhost:8082", gpu_vram_mb=8192, models=["qwen2.5-coder-7b"])

    class FakeTask:
        task_type = "chat-simple"
        preferred_model = None

    model, node_id = pick_model_and_node(FakeTask())
    assert node_id == "rtx-node"
    print("PASS: router falls back to capable node")


if __name__ == "__main__":
    test_router_picks_smallest_capable_node()
    test_router_falls_back_to_loaded_model()
    print("All smoke tests passed.")
