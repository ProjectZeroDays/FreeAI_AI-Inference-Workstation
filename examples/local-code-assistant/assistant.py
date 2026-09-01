"""
Local Code Assistant — Privacy-first, offline-capable code assistant.
Drop-in replacement for local-only development workflows.

Usage:
    python local_code_assistant.py --model meta-llama/llama-3.1-8b-instruct
    python local_code_assistant.py --local  # uses Ollama local models
    python local_code_assistant.py --stream

Requires:
    pip install requests
    Ollama running locally: ollama serve
"""
import argparse
import json
import sys
import time
from pathlib import Path

# ── Configuration ──────────────────────────────────────────────────────────────

DEFAULT_CONFIG = {
    "model": "llama3.1",
    "temperature": 0.2,
    "max_tokens": 2048,
    "stream": False,
    "system_prompt": """You are a helpful coding assistant. You write clean, efficient code
and explain your reasoning concisely. When asked to modify code, show the full
updated file with clear diff annotations. Follow PEP 8, Google Style, or
language-specific conventions unless told otherwise.""",
}

CONFIG_PATH = Path.home() / ".freeai" / "code-assistant.json"


def load_config() -> dict:
    if CONFIG_PATH.exists():
        return json.loads(CONFIG_PATH.read_text())
    CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
    CONFIG_PATH.write_text(json.dumps(DEFAULT_CONFIG, indent=2))
    return DEFAULT_CONFIG.copy()


def save_config(cfg: dict) -> None:
    CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
    CONFIG_PATH.write_text(json.dumps(cfg, indent=2))


# ── Ollama Local API ───────────────────────────────────────────────────────────

def chat_local(system: str, user: str, model: str = "llama3.1", stream: bool = False) -> str:
    import urllib.request
    payload = json.dumps({
        "model": model,
        "messages": [
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
        "stream": stream,
        "options": {
            "temperature": 0.2,
            "num_predict": 2048,
        },
    }).encode()
    req = urllib.request.Request(
        "http://localhost:11434/api/chat",
        data=payload,
        headers={"Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=120) as resp:
        chunks = json.loads(resp.read())
    return chunks["message"]["content"]


def chat_provider(api_key: str, endpoint: str, model: str, system: str, user: str, stream: bool = False) -> str:
    import urllib.request
    payload = json.dumps({
        "model": model,
        "messages": [
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
        "stream": stream,
        "temperature": 0.2,
    }).encode()
    req = urllib.request.Request(
        endpoint,
        data=payload,
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}",
        },
    )
    with urllib.request.urlopen(req, timeout=120) as resp:
        data = json.loads(resp.read())
    return data["choices"][0]["message"]["content"]


# ── CLI Session ────────────────────────────────────────────────────────────────

def repl(cfg: dict) -> None:
    system = cfg.get("system_prompt", DEFAULT_CONFIG["system_prompt"])
    print("=" * 60)
    print("  FreeAI Local Code Assistant")
    print("  Model:  " + cfg.get("model", "llama3.1"))
    print("  Type 'quit' or Ctrl+C to exit")
    print("=" * 60)
    history = [{"role": "system", "content": system}]
    while True:
        try:
            user = input("\n> ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nBye.")
            break
        if not user:
            continue
        if user.lower() in ("quit", "exit", "q"):
            print("Bye.")
            break
        if user.lower() in ("clear", "reset"):
            history = [{"role": "system", "content": system}]
            print("[cleared]")
            continue
        if user.lower() in ("config", "cfg"):
            print(json.dumps(cfg, indent=2))
            continue
        t0 = time.time()
        if cfg.get("local", False):
            reply = chat_local(system, user, cfg["model"], cfg.get("stream", False))
        else:
            api_key = cfg.get("api_key", "")
            endpoint = cfg.get("endpoint", "https://api.agnes-ai.com/v1/chat/completions")
            model = cfg.get("model", "agnes-2.0-flash")
            reply = chat_provider(api_key, endpoint, model, system, user, cfg.get("stream", False))
        elapsed = time.time() - t0
        print(f"\n{reply}")
        print(f"\n[{elapsed:.1f}s]")
        history.append({"role": "user", "content": user})
        history.append({"role": "assistant", "content": reply})


# ── Main ───────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="FreeAI Local Code Assistant")
    parser.add_argument("--local", action="store_true", help="Use Ollama local models")
    parser.add_argument("--model", default=None, help="Model name")
    parser.add_argument("--stream", action="store_true", help="Stream responses")
    parser.add_argument("--prompt", default=None, help="Single-shot prompt (non-interactive)")
    args = parser.parse_args()

    cfg = load_config()
    if args.local:
        cfg["local"] = True
    if args.model:
        cfg["model"] = args.model
    if args.stream:
        cfg["stream"] = True
    save_config(cfg)

    if args.prompt:
        system = cfg.get("system_prompt", DEFAULT_CONFIG["system_prompt"])
        if cfg.get("local", False):
            reply = chat_local(system, args.prompt, cfg["model"], cfg.get("stream", False))
        else:
            api_key = cfg.get("api_key", "")
            endpoint = cfg.get("endpoint", "https://api.agnes-ai.com/v1/chat/completions")
            model = cfg.get("model", "agnes-2.0-flash")
            reply = chat_provider(api_key, endpoint, model, system, args.prompt, cfg.get("stream", False))
        print(reply)
    else:
        repl(cfg)


if __name__ == "__main__":
    main()
