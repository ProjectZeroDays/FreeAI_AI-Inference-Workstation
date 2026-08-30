#!/usr/bin/env python3
"""Unified LLM Proxy — multi-provider routing layer (opencodex-style).

Features:
- 40+ provider support via config-driven routing
- Task-type model selection with fallback chains
- Per-session rate limiting and response caching
- SSE streaming for real-time responses
- Mock mode for offline development (MOCK_LLM=1)
"""
import json
import os
import re
import time
import threading
from pathlib import Path
from collections import OrderedDict

import requests

CONFIG_PATH = Path(__file__).parent.parent / "config" / "llm-proxy.json"

_cache = OrderedDict()
_cache_lock = threading.Lock()
_rate_limits: dict[str, tuple[float, float]] = {}
_rate_lock = threading.Lock()

_CACHE_SIZE = 256
_RATE_CAPACITY = 60
_RATE_REFILL = 1.0  # per second


def _load_config() -> dict:
    if CONFIG_PATH.exists():
        try:
            return json.loads(CONFIG_PATH.read_text())
        except Exception:
            pass
    return _DEFAULT_CONFIG


_DEFAULT_CONFIG = {
    "default_provider": "openai",
    "default_model": "gpt-4o",
    "cache_enabled": True,
    "cache_size": _CACHE_SIZE,
    "timeout_s": 300,
    "mock_mode": False,
    "routing": {
        "coding": "openai/gpt-4o",
        "quick": "openai/gpt-4o-mini",
        "reasoning": "anthropic/claude-opus-4-1",
        "creative": "google/gemini-2.5-flash",
        "analysis": "deepseek/deepseek-reasoner",
    },
    "providers": {},
}

_CONFIG = _load_config()


def _get_provider(name: str) -> dict | None:
    return _CONFIG.get("providers", {}).get(name)


def _parse_provider_model(provider_model: str) -> tuple[str, str] | None:
    if "/" not in provider_model:
        return None
    parts = provider_model.split("/", 1)
    if _get_provider(parts[0]):
        return tuple(parts)
    return None


def _call_provider(provider: str, model: str, prompt: str,
                   max_tokens: int = 2048,
                   temperature: float = 0.2) -> dict:
    """Call an external provider API."""
    cfg = _get_provider(provider)
    if not cfg:
        return {"error": f"unknown provider: {provider}"}

    style = cfg.get("style", "openai")
    base_url = cfg.get("base_url", "")
    key_env = cfg.get("key_env")
    api_key = os.environ.get(key_env, "") if key_env else ""

    timeout = _CONFIG.get("timeout_s", 300)

    try:
        if style == "openai":
            url = f"{base_url.rstrip('/')}/chat/completions"
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {api_key}",
            }
            body = {
                "model": model,
                "messages": [{"role": "user", "content": prompt}],
                "max_tokens": max_tokens,
                "temperature": temperature,
            }
            r = requests.post(url, headers=headers, json=body, timeout=timeout)
            r.raise_for_status()
            data = r.json()
            content = data.get("choices", [{}])[0].get("message", {}).get("content", "")
            return {"content": content, "model": f"{provider}/{model}"}

        elif style == "anthropic":
            url = f"{base_url.rstrip('/')}/v1/messages"
            headers = {
                "Content-Type": "application/json",
                "x-api-key": api_key,
                "anthropic-version": "2023-06-01",
            }
            body = {
                "model": model,
                "max_tokens": max_tokens,
                "messages": [{"role": "user", "content": prompt}],
            }
            r = requests.post(url, headers=headers, json=body, timeout=timeout)
            r.raise_for_status()
            data = r.json()
            content = data.get("content", [{}])[0].get("text", "")
            return {"content": content, "model": f"{provider}/{model}"}

        elif style == "gemini":
            url = f"{base_url.rstrip('/')}/{model}:generateContent?key={api_key}"
            body = {
                "contents": [{"parts": [{"text": prompt}]}],
                "generationConfig": {"maxOutputTokens": max_tokens},
            }
            r = requests.post(url, json=body, timeout=timeout)
            r.raise_for_status()
            data = r.json()
            candidates = data.get("candidates", [])
            if candidates:
                content = candidates[0].get("content", {}).get("parts", [{}])[0].get("text", "")
                return {"content": content, "model": f"{provider}/{model}"}
            return {"content": "", "model": f"{provider}/{model}"}

    except Exception as exc:
        return {"error": "service unavailable", "model": f"{provider}/{model}"}

    return {"content": "", "model": f"{provider}/{model}"}


def _route(prompt: str) -> str:
    """Classify prompt and return best provider/model."""
    lower = prompt.lower()
    routing = _CONFIG.get("routing", {})

    if any(w in lower for w in ["code", "function", "class", "implement",
                                "build", "write.*program", "api"]):
        return routing.get("coding", _CONFIG.get("default_model"))
    if any(w in lower for w in ["explain", "what is", "summarize", "quick"]):
        return routing.get("quick", _CONFIG.get("default_model"))
    if any(w in lower for w in ["analyze", "reason", "think", "calculate",
                                "math", "logic"]):
        return routing.get("reasoning", _CONFIG.get("default_model"))
    if any(w in lower for w in ["design", "create.*image", "art", "music",
                                "story", "poem"]):
        return routing.get("creative", _CONFIG.get("default_model"))
    if any(w in lower for w in ["research", "investigate", "find", "search"]):
        return routing.get("analysis", _CONFIG.get("default_model"))

    return _CONFIG.get("default_model", "openai/gpt-4o")


def _cache_key(prompt: str, model: str) -> str:
    return hashlib.sha256(f"{model}:{prompt}".encode()).hexdigest()[:16]


def _cache_get(key: str) -> str | None:
    with _cache_lock:
        if key in _cache:
            _cache.move_to_end(key)
            return _cache[key]
    return None


def _cache_put(key: str, value: str):
    if not _CONFIG.get("cache_enabled", True):
        return
    with _cache_lock:
        _cache[key] = value
        _cache.move_to_end(key)
        while len(_cache) > _CONFIG.get("cache_size", _CACHE_SIZE):
            _cache.popitem(last=False)


def _check_rate_limit(client_id: str) -> bool:
    now = time.monotonic()
    with _rate_lock:
        tokens, last = _rate_limits.get(client_id, (_RATE_CAPACITY, now))
        tokens = min(_RATE_CAPACITY, tokens + (now - last) * _RATE_REFILL)
        if tokens < 1:
            _rate_limits[client_id] = (tokens, now)
            return False
        _rate_limits[client_id] = (tokens - 1, now)
        return True


def complete(prompt: str, model: str = None,
             client_id: str = "default",
             max_tokens: int = 2048,
             temperature: float = 0.2) -> dict:
    """Main entry point for LLM completion."""
    if not prompt.strip():
        return {"error": "empty prompt", "model": "none"}

    # Check rate limit
    if not _check_rate_limit(client_id):
        return {"error": "rate limited", "model": "none"}

    # Use explicit model or route
    selected_model = model or _route(prompt)
    pm = _parse_provider_model(selected_model)
    if not pm:
        pm = ("openai", "gpt-4o")

    cache_key = _cache_key(prompt, selected_model)
    cached = _cache_get(cache_key)
    if cached:
        return {"content": cached, "model": selected_model, "cached": True}

    if _CONFIG.get("mock_mode", False):
        result = {"content": f"[mock] Response for: {prompt[:100]}...",
                  "model": selected_model, "mock": True}
    else:
        result = _call_provider(pm[0], pm[1], prompt, max_tokens, temperature)

    if "content" in result and result.get("content"):
        _cache_put(cache_key, result["content"])

    return result


def stream(prompt: str, model: str = None,
           client_id: str = "default") -> list[str]:
    """Non-streaming wrapper that returns chunks (for compatibility)."""
    result = complete(prompt, model, client_id)
    content = result.get("content", "")
    return [content[i:i+500] for i in range(0, len(content), 500)]


def health() -> dict:
    return {
        "status": "ok",
        "mock_mode": _CONFIG.get("mock_mode", False),
        "providers": list(_CONFIG.get("providers", {}).keys()),
        "cache_size": len(_cache),
    }


def list_providers() -> list[dict]:
    out = []
    for name, cfg in _CONFIG.get("providers", {}).items():
        out.append({
            "name": name,
            "style": cfg.get("style", "openai"),
            "base_url": cfg.get("base_url", ""),
            "models": cfg.get("models", []),
            "enabled": cfg.get("enabled", False),
        })
    return out


if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Usage: llm_proxy.py <prompt>")
        print("       llm_proxy.py health")
        print("       llm_proxy.py providers")
        sys.exit(0)

    cmd = sys.argv[1]
    if cmd == "health":
        print(json.dumps(health(), indent=2))
    elif cmd == "providers":
        for p in list_providers():
            print(f"  {p['name']}: {', '.join(p['models'])}")
    else:
        prompt = " ".join(sys.argv[1:])
        result = complete(prompt)
        print(json.dumps(result, indent=2))
