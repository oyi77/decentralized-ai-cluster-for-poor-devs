#!/usr/bin/env python3
"""
Decentralized AI Cluster — Node Daemon
Runs on every device. Reports capacity and keeps llama.cpp server alive.
"""

import time
import socket
import subprocess
import argparse
import httpx
import asyncio


def get_gpu_info():
    info = {"name": "CPU", "vram_mb": 0}
    try:
        result = subprocess.run(
            ["nvidia-smi", "--query-gpu=name,memory.total", "--format=csv,noheader,nounits"],
            capture_output=True, text=True, timeout=5
        )
        if result.returncode == 0:
            line = result.stdout.strip().split("\n")[0]
            name, vram = [x.strip() for x in line.split(",")]
            info = {"name": name, "vram_mb": int(float(vram))}
    except Exception:
        pass
    return info


def find_free_port(start=8080):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    port = start
    while True:
        try:
            s.bind(("0.0.0.0", port))
            s.close()
            return port
        except OSError:
            port += 1


class NodeDaemon:
    def __init__(self, node_id: str, router_url: str, model: str, gguf_path: str,
                 port: int = 0, ngl: int = 999):
        self.node_id = node_id
        self.router_url = router_url
        self.model = model
        self.gguf_path = gguf_path
        self.port = port or find_free_port()
        self.ngl = ngl
        self.server_proc = None
        self.gpu = get_gpu_info()

    def start_server(self):
        cmd = [
            "llama-server",
            "-m", self.gguf_path,
            "--port", str(self.port),
            "-ngl", str(self.ngl),
            "-c", "4096",
            "-n", "2048",
        ]
        print("Starting:", " ".join(cmd))
        self.server_proc = subprocess.Popen(cmd)
        for _ in range(30):
            try:
                r = httpx.get(f"http://localhost:{self.port}/health", timeout=2.0)
                if r.status_code == 200:
                    print("llama-server ready")
                    return
            except Exception:
                pass
            time.sleep(1)
        raise RuntimeError("llama-server failed to start")

    async def register(self):
        payload = {
            "id": self.node_id,
            "url": f"http://{self.get_ip()}:{self.port}",
            "gpu_vram_mb": self.gpu["vram_mb"],
            "gpu_name": self.gpu["name"],
            "models": [self.model],
        }
        async with httpx.AsyncClient() as client:
            r = await client.post(f"{self.router_url}/nodes/register", json=payload)
            r.raise_for_status()
            print("Registered:", r.json())

    async def heartbeat_loop(self):
        async with httpx.AsyncClient() as client:
            while True:
                try:
                    await client.post(
                        f"{self.router_url}/nodes/heartbeat",
                        params={"node_id": self.node_id},
                        timeout=10.0
                    )
                except Exception as e:
                    print("Heartbeat failed:", e)
                await asyncio.sleep(10)

    def get_ip(self):
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
            s.close()
            return ip
        except Exception:
            return "127.0.0.1"

    async def run(self):
        self.start_server()
        await self.register()
        await self.heartbeat_loop()


async def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--id", required=True)
    parser.add_argument("--router", default="http://localhost:8000")
    parser.add_argument("--model", required=True)
    parser.add_argument("--gguf", required=True)
    parser.add_argument("--port", type=int, default=0)
    parser.add_argument("--ngl", type=int, default=999)
    args = parser.parse_args()

    daemon = NodeDaemon(
        node_id=args.id,
        router_url=args.router,
        model=args.model,
        gguf_path=args.gguf,
        port=args.port,
        ngl=args.ngl,
    )
    await daemon.run()


if __name__ == "__main__":
    asyncio.run(main())
