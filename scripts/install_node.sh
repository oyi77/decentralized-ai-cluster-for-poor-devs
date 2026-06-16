#!/bin/bash
# Decentralized AI Cluster for Broke Developers
# One-command node installer. Detects hardware, downloads model, joins cluster.

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
MODEL_DIR="$HOME/.daicbd/models"
mkdir -p "$MODEL_DIR"

GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m'

info() { echo -e "${GREEN}[daicbd]${NC} $1"; }
error() { echo -e "${RED}[daicbd]${NC} $1"; }

VRAM_MB=0
GPU_NAME="CPU"
if command -v nvidia-smi &> /dev/null; then
    VRAM_MB=$(nvidia-smi --query-gpu=memory.total --format=csv,noheader,nounits | head -n1 | cut -d. -f1)
    GPU_NAME=$(nvidia-smi --query-gpu=name --format=csv,noheader | head -n1)
fi

info "Detected: $GPU_NAME (${VRAM_MB}MB VRAM)"

if [ "$VRAM_MB" -ge 5500 ]; then
    MODEL="qwen2.5-coder-7b"
    GGUF_URL="https://huggingface.co/Qwen/Qwen2.5-Coder-7B-Instruct-GGUF/resolve/main/qwen2.5-coder-7b-instruct-q4_k_m.gguf"
    NGL=999
elif [ "$VRAM_MB" -ge 2500 ]; then
    MODEL="qwen2.5-3b"
    GGUF_URL="https://huggingface.co/Qwen/Qwen2.5-3B-Instruct-GGUF/resolve/main/qwen2.5-3b-instruct-q4_k_m.gguf"
    NGL=999
elif [ "$VRAM_MB" -ge 1200 ]; then
    MODEL="qwen2.5-1.5b"
    GGUF_URL="https://huggingface.co/Qwen/Qwen2.5-1.5B-Instruct-GGUF/resolve/main/qwen2.5-1.5b-instruct-q4_k_m.gguf"
    NGL=999
else
    MODEL="qwen2.5-1.5b"
    GGUF_URL="https://huggingface.co/Qwen/Qwen2.5-1.5B-Instruct-GGUF/resolve/main/qwen2.5-1.5b-instruct-q4_k_m.gguf"
    NGL=0
fi

GGUF_NAME=$(basename "$GGUF_URL")
GGUF_PATH="$MODEL_DIR/$GGUF_NAME"

if [ ! -f "$GGUF_PATH" ]; then
    info "Downloading $MODEL GGUF..."
    if command -v wget &> /dev/null; then
        wget --show-progress -O "$GGUF_PATH" "$GGUF_URL"
    elif command -v curl &> /dev/null; then
        curl -L --progress-bar -o "$GGUF_PATH" "$GGUF_URL"
    else
        error "Need wget or curl to download model."
        exit 1
    fi
fi

if ! command -v llama-server &> /dev/null; then
    error "llama-server not found. Install llama.cpp first:"
    error "  git clone https://github.com/ggerganov/llama.cpp"
    error "  cmake -B build -DLLAMA_CUDA=ON"
    error "  cmake --build build --config Release -j"
    error "  cp build/bin/llama-server ~/.local/bin/"
    exit 1
fi

ROUTER_URL="${ROUTER_URL:-http://localhost:8000}"
NODE_ID="${NODE_ID:-$(hostname)}"

info "Starting node '$NODE_ID' serving '$MODEL'..."
info "Router: $ROUTER_URL"

exec python3 "$SCRIPT_DIR/../cluster_nodes/daemon.py" \
    --id "$NODE_ID" \
    --router "$ROUTER_URL" \
    --model "$MODEL" \
    --gguf "$GGUF_PATH" \
    --ngl "$NGL"
