#!/usr/bin/env python3
"""
Decentralized AI Cluster — Agent Templates for 1-Man Companies
Ready-to-use workflows that route through the cluster.
"""

import httpx
import json

ROUTER = "http://localhost:8000"


def chat(messages: list[dict], task_type: str = "chat", model: str | None = None, max_tokens: int = 512):
    payload = {
        "messages": messages,
        "task_type": task_type,
        "max_tokens": max_tokens,
        "temperature": 0.2 if task_type == "code" else 0.7,
    }
    if model:
        payload["preferred_model"] = model

    r = httpx.post(f"{ROUTER}/v1/chat/completions", json=payload, timeout=300.0)
    r.raise_for_status()
    data = r.json()
    return data["choices"][0]["message"]["content"]


def reply_whatsapp(customer_message: str, product_name: str, faq: str = "") -> str:
    messages = [
        {"role": "system", "content": f"Kamu customer service ramah untuk {product_name}. Jawab singkat, sopan, dalam Bahasa Indonesia. FAQ: {faq}"},
        {"role": "user", "content": customer_message},
    ]
    return chat(messages, task_type="chat-simple", model="qwen2.5-1.5b", max_tokens=256)


def generate_caption(product: str, tone: str = "viral", platform: str = "instagram") -> str:
    messages = [
        {"role": "system", "content": f"Buat caption {platform} yang {tone}. Bahasa Indonesia. Tambahkan CTA."},
        {"role": "user", "content": f"Produk: {product}"},
    ]
    return chat(messages, task_type="rewrite", model="qwen2.5-3b", max_tokens=300)


def code_assistant(instruction: str, existing_code: str = "", language: str = "python") -> str:
    user_prompt = f"Bahasa: {language}\n\nInstruksi: {instruction}\n\nKode existing:\n```\n{existing_code}\n```"
    messages = [
        {"role": "system", "content": "Kamu programmer senior. Tulis kode bersih, terdokumentasi, dengan komentar Bahasa Indonesia. Hanya output kode, tanpa penjelasan panjang."},
        {"role": "user", "content": user_prompt},
    ]
    return chat(messages, task_type="code", model="qwen2.5-coder-7b", max_tokens=1024)


def summarize_text(text: str, max_bullet: int = 5) -> str:
    messages = [
        {"role": "system", "content": f"Ringkas teks berikut dalam {max_bullet} poin penting. Bahasa Indonesia."},
        {"role": "user", "content": text[:12000]},
    ]
    return chat(messages, task_type="summarize", model="qwen2.5-1.5b", max_tokens=512)


def extract_invoice(text: str) -> dict:
    messages = [
        {"role": "system", "content": "Ekstrak field dari invoice: total, vendor, tanggal, item_list. Output hanya JSON valid."},
        {"role": "user", "content": text[:4000]},
    ]
    raw = chat(messages, task_type="chat-simple", model="qwen2.5-3b", max_tokens=400)
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        return {"raw": raw, "error": "JSON parse failed"}


if __name__ == "__main__":
    print("--- WhatsApp reply ---")
    print(reply_whatsapp("Halo, harga berapa?", "Kaos Polos Premium"))

    print("\n--- Caption ---")
    print(generate_caption("Kaos katun combed 30s, sablon custom"))

    print("\n--- Code ---")
    print(code_assistant("Buat fungsi Python validasi email dengan regex"))
