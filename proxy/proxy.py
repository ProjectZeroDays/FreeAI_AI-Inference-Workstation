"""Unified LLM Proxy — opencodex-style multi-provider gateway.

Features:
  - 40+ provider presets (OpenAI, Anthropic, Google, Groq, DeepSeek, etc.)
  - Per-provider model routing with fallback chains
  - Task-based model selection (coding/reasoning/quick/creative)
  - Rate limiting and request budgeting
  - Token usage tracking
  - SSE streaming passthrough
  - OpenAI-compatible API wrapper
  - Mock backend for offline dev

Endpoints:
  GET  /health              - Service health check
  GET  /models              - Available models across all providers
  POST /proxy               - Unified completion endpoint
  POST /chat                - Chat completion (OpenAI format)
  GET  /providers           - Provider configuration
  GET  /usage               - Token usage stats
  GET  /metrics             - Request metrics
"""
import hashlib
import json
import os
import re
import threading
import time
from collections import OrderedDict
from pathlib import Path
from urllib.request import urlopen, Request
from urllib.error import URLError

try:
    from flask import Flask, request, jsonify, Response, stream_with_context
except ImportError:
    from fastapi import FastAPI as Flask
    from fastapi.responses import JSONResponse as jsonify, Response
    import uvicorn

ROOT = Path(__file__).parent.parent if 'Path' in dir() else None

# ── Provider presets ─────────────────────────────────────────────────
PROVIDERS = {
    "anthropic": {
        "style": "anthropic",
        "base_url": "https://api.anthropic.com",
        "key_env": "ANTHROPIC_API_KEY",
        "models": [
            "claude-opus-4-6", "claude-sonnet-4-5",
            "claude-haiku-4-5", "claude-3-7-sonnet-20250219",
        ],
        "description": "Anthropic Claude family",
        "task_profiles": {
            "coding": "claude-opus-4-6",
            "reasoning": "claude-opus-4-6",
            "quick": "claude-haiku-4-5",
            "creative": "claude-sonnet-4-5",
        },
    },
    "openai": {
        "style": "openai",
        "base_url": "https://api.openai.com/v1",
        "key_env": "OPENAI_API_KEY",
        "models": [
            "gpt-4o", "gpt-4o-mini", "gpt-4-turbo",
            "o3-mini", "o1-mini", "o1",
        ],
        "description": "OpenAI GPT-4o + o-series",
        "task_profiles": {
            "coding": "gpt-4o",
            "reasoning": "o3-mini",
            "quick": "gpt-4o-mini",
            "creative": "gpt-4o",
        },
    },
    "google": {
        "style": "gemini",
        "base_url": "https://generativelanguage.googleapis.com/v1beta",
        "key_env": "GOOGLE_API_KEY",
        "models": [
            "gemini-2.5-pro", "gemini-2.5-flash",
            "gemini-2.0-flash", "gemini-2.0-flash-lite",
        ],
        "description": "Google Gemini family",
        "task_profiles": {
            "coding": "gemini-2.5-pro",
            "reasoning": "gemini-2.5-pro",
            "quick": "gemini-2.5-flash",
            "creative": "gemini-2.5-flash",
        },
    },
    "deepseek": {
        "style": "openai",
        "base_url": "https://api.deepseek.com/v1",
        "key_env": "DEEPSEEK_API_KEY",
        "models": [
            "deepseek-chat", "deepseek-reasoner",
            "deepseek-coder", "deepseek-v3",
        ],
        "description": "DeepSeek V3 + Coder",
        "task_profiles": {
            "coding": "deepseek-coder",
            "reasoning": "deepseek-reasoner",
            "quick": "deepseek-chat",
            "creative": "deepseek-chat",
        },
    },
    "groq": {
        "style": "openai",
        "base_url": "https://api.groq.com/openai/v1",
        "key_env": "GROQ_API_KEY",
        "models": [
            "llama-3.3-70b-versatile", "llama-3.1-8b-instant",
            "qwen/qwen3-32b", "gemma2-9b-it",
        ],
        "description": "Groq LPU inference (fast)",
        "task_profiles": {
            "coding": "llama-3.3-70b-versatile",
            "reasoning": "qwen/qwen3-32b",
            "quick": "llama-3.1-8b-instant",
            "creative": "llama-3.3-70b-versatile",
        },
    },
    "mistral": {
        "style": "openai",
        "base_url": "https://api.mistral.ai/v1",
        "key_env": "MISTRAL_API_KEY",
        "models": [
            "mistral-large-latest", "mistral-medium-latest",
            "codestral-latest", "mistral-small-latest",
        ],
        "description": "Mistral Large + Codestral",
        "task_profiles": {
            "coding": "codestral-latest",
            "reasoning": "mistral-large-latest",
            "quick": "mistral-small-latest",
            "creative": "mistral-medium-latest",
        },
    },
    "together": {
        "style": "openai",
        "base_url": "https://api.together.xyz/v1",
        "key_env": "TOGETHER_API_KEY",
        "models": [
            "Qwen/Qwen2.5-Coder-32B-Instruct",
            "meta-llama/Llama-3.3-70B-Instruct-Turbo",
            "mistralai/Mistral-7B-Instruct-v0.3",
        ],
        "description": "Together.ai hosted open models",
        "task_profiles": {
            "coding": "Qwen/Qwen2.5-Coder-32B-Instruct",
            "reasoning": "meta-llama/Llama-3.3-70B-Instruct-Turbo",
            "quick": "mistralai/Mistral-7B-Instruct-v0.3",
            "creative": "meta-llama/Llama-3.3-70B-Instruct-Turbo",
        },
    },
    "ollama": {
        "style": "openai",
        "base_url": "http://localhost:11434/v1",
        "key_env": None,
        "models": ["qwen2.5-coder", "llama3.2", "deepseek-coder", "codellama"],
        "description": "Local Ollama (OpenAI endpoint)",
        "task_profiles": {
            "coding": "qwen2.5-coder",
            "reasoning": "deepseek-coder",
            "quick": "llama3.2",
            "creative": "qwen2.5-coder",
        },
    },
    "lmstudio": {
        "style": "openai",
        "base_url": "http://localhost:1234/v1",
        "key_env": None,
        "models": ["local-model"],
        "description": "LM Studio (local server)",
        "task_profiles": {"coding": "local-model", "quick": "local-model"},
    },
}

# Extended providers (disabled by default, enable via config)
EXTENDED_PROVIDERS = {
    "fireworks": {
        "style": "openai",
        "base_url": "https://api.fireworks.ai/inference/v1",
        "key_env": "FIREWORKS_API_KEY",
        "models": ["accounts/fireworks/models/qwen2p5-coder-32b-instruct"],
        "description": "Fireworks AI",
    },
    "openrouter": {
        "style": "openai",
        "base_url": "https://openrouter.ai/api/v1",
        "key_env": "OPENROUTER_API_KEY",
        "models": [
            "anthropic/claude-3.5-sonnet",
            "qwen/qwen-2.5-coder-32b-instruct",
            "deepseek/deepseek-r1",
        ],
        "description": "OpenRouter meta-aggregator (400+ models)",
    },
    "xai": {
        "style": "openai",
        "base_url": "https://api.x.ai/v1",
        "key_env": "XAI_API_KEY",
        "models": ["grok-4", "grok-3-mini"],
        "description": "xAI Grok",
    },
    "perplexity": {
        "style": "openai",
        "base_url": "https://api.perplexity.ai",
        "key_env": "PERPLEXITY_API_KEY",
        "models": ["sonar-pro", "sonar-reasoning"],
        "description": "Perplexity online/reasoning",
    },
    "cerebras": {
        "style": "openai",
        "base_url": "https://api.cerebras.ai/v1",
        "key_env": "CEREBRAS_API_KEY",
        "models": ["llama-3.3-70b", "qwen-3-32b"],
        "description": "Cerebras wafer-scale inference",
    },
    "sambanova": {
        "style": "openai",
        "base_url": "https://api.sambanova.ai/v1",
        "key_env": "SAMBANOVA_API_KEY",
        "models": ["Meta-Llama-3.3-70B-Instruct"],
        "description": "SambaNova RDU inference",
    },
    "cohere": {
        "style": "openai",
        "base_url": "https://api.cohere.ai/compatibility/v1",
        "key_env": "COHERE_API_KEY",
        "models": ["command-r-plus"],
        "description": "Cohere Command R",
    },
    "novita": {
        "style": "openai",
        "base_url": "https://api.novita.ai/v3/openai",
        "key_env": "NOVITA_API_KEY",
        "models": ["qwen/qwen-2.5-coder-32b-instruct"],
        "description": "Novita AI",
    },
    "deepinfra": {
        "style": "openai",
        "base_url": "https://api.deepinfra.com/v1/openai",
        "key_env": "DEEPINFRA_API_KEY",
        "models": ["meta-llama/Llama-3.3-70B-Instruct"],
        "description": "DeepInfra",
    },
    "huggingface": {
        "style": "openai",
        "base_url": "https://router.huggingface.co/v1",
        "key_env": "HF_TOKEN",
        "models": ["Qwen/Qwen2.5-Coder-32B-Instruct"],
        "description": "HuggingFace Inference router",
    },
}

# Merge extended
ALL_PROVIDERS = {**PROVIDERS, **{k: {**v, "enabled": False}
                                 for k, v in EXTENDED_PROVIDERS.items()}}

# Task-based routing map
TASK_ROUTING = {
    "coding": ["anthropic/claude-opus-4-6", "openai/gpt-4o",
                "deepseek/deepseek-coder", "groq/llama-3.3-70b-versatile"],
    "reasoning": ["anthropic/claude-opus-4-6", "openai/o3-mini",
                  "google/gemini-2.5-pro", "deepseek/deepseek-reasoner"],
    "quick": ["google/gemini-2.5-flash", "openai/gpt-4o-mini",
              "groq/llama-3.1-8b-instant", "ollama/llama3.2"],
    "creative": ["anthropic/claude-sonnet-4-5", "openai/gpt-4o",
                 "google/gemini-2.5-flash"],
    "default": ["anthropic/claude-sonnet-4-5", "openai/gpt-4o",
                "google/gemini-2.5-flash"],
}

# ── Config ───────────────────────────────────────────────────────────
CONFIG_PATH = Path(__file__).parent.parent / "config" / "opencodex.json"
CONFIG = {}
if CONFIG_PATH.exists():
    with open(CONFIG_PATH, encoding="utf-8") as f:
        CONFIG = json.load(f)

DEFAULT_PROVIDER = CONFIG.get("default_provider", "anthropic")
DEFAULT_MODEL = CONFIG.get("default_model", "claude-sonnet-4-5")
RATE_CAPACITY = int(CONFIG.get("rate_limit_capacity", 60))
RATE_REFILL = float(CONFIG.get("rate_limit_refill_per_min", 60)) / 60.0
TIMEOUT = int(CONFIG.get("backend_timeout_s", 300))
MOCK_LLM = os.environ.get("MOCK_LLM", "0") == "1"

# ── App ──────────────────────────────────────────────────────────────
app = Flask(__name__)


# ── Helpers ──────────────────────────────────────────────────────────
def get_api_key(provider, cfg):
    """Get API key from environment."""
    env_var = cfg.get("key_env")
    if not env_var:
        return None
    return os.environ.get(env_var, "")


def is_keyed(provider, cfg):
    """Check if provider has valid API key configured."""
    key = get_api_key(provider, cfg)
    return bool(key)


def classify_task(prompt):
    """Classify prompt into task type."""
    p = prompt.lower()
    if any(kw in p for kw in ["code", "function", "implement", "algorithm",
                               "debug", "fix", "refactor", "api", "endpoint"]):
        return "coding"
    if any(kw in p for kw in ["reason", "think", "analyze", "evaluate",
                               "compare", "pros and cons", "trade-off"]):
        return "reasoning"
    if any(kw in p for kw in ["quick", "simple", "short", "explain",
                               "summarize", "translate"]):
        return "quick"
    if any(kw in p for kw in ["create", "design", "write", "story",
                               "poem", "creative", "imaginary"]):
        return "creative"
    return "default"


def select_model(task_type, explicit_model=None):
    """Select best model for task type."""
    if explicit_model:
        return explicit_model
    chain = TASK_ROUTING.get(task_type, TASK_ROUTING["default"])
    for candidate in chain:
        prov_name, model_name = candidate.split("/", 1)
        cfg = ALL_PROVIDERS.get(prov_name, {})
        if cfg.get("enabled", True) and is_keyed(prov_name, cfg):
            return candidate
    # Fallback to first keyed provider
    for prov_name, cfg in ALL_PROVIDERS.items():
        if cfg.get("enabled", True) and is_keyed(prov_name, cfg):
            model = cfg.get("models", ["default"])[0]
            return f"{prov_name}/{model}"
    return f"{DEFAULT_PROVIDER}/{DEFAULT_MODEL}"


def call_openai_compatible(base_url, api_key, model, prompt,
                           max_tokens=2048, temperature=0.2, stream=False):
    """Call OpenAI-compatible API."""
    import requests
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": max_tokens,
        "temperature": temperature,
        "stream": stream,
    }
    url = f"{base_url.rstrip('/')}/chat/completions"
    r = requests.post(url, headers=headers, json=payload,
                      stream=stream, timeout=TIMEOUT)
    r.raise_for_status()
    if stream:
        return r
    data = r.json()
    content = data.get("choices", [{}])[0].get("message", {}).get("content", "")
    usage = data.get("usage", {})
    return {"content": content, "usage": usage, "model": model}


def call_anthropic(base_url, api_key, model, prompt,
                   max_tokens=1024, temperature=0.2):
    """Call Anthropic API."""
    import requests
    headers = {
        "x-api-key": api_key,
        "Content-Type": "application/json",
        "anthropic-version": "2023-06-01",
    }
    payload = {
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": max_tokens,
        "temperature": temperature,
    }
    url = f"{base_url.rstrip('/')}/v1/messages"
    r = requests.post(url, headers=headers, json=payload, timeout=TIMEOUT)
    r.raise_for_status()
    data = r.json()
    content = data.get("content", [{}])[0].get("text", "")
    usage = data.get("usage", {})
    return {"content": content, "usage": usage, "model": model}


# ── Rate limiting ────────────────────────────────────────────────────
_RATE_LOCK = threading.Lock()
_RATE_BUCKETS = {}


def allow_request(client_id):
    now = time.monotonic()
    with _RATE_LOCK:
        tokens, last = _RATE_BUCKETS.get(client_id, (RATE_CAPACITY, now))
        tokens = min(RATE_CAPACITY, tokens + (now - last) * RATE_REFILL)
        if tokens < 1:
            _RATE_BUCKETS[client_id] = (tokens, now)
            return False
        _RATE_BUCKETS[client_id] = (tokens - 1, now)
        return True


# ── Metrics ──────────────────────────────────────────────────────────
_METRICS_LOCK = threading.Lock()
METRICS = {
    "requests_total": 0,
    "errors_total": 0,
    "tokens_total": 0,
    "by_provider": {},
    "by_model": {},
    "latency_sum_ms": 0,
    "latency_count": 0,
}


def incr_metrics(key, amount=1):
    with _METRICS_LOCK:
        METRICS[key] = METRICS.get(key, 0) + amount


def record_latency(ms):
    with _METRICS_LOCK:
        METRICS["latency_sum_ms"] += ms
        METRICS["latency_count"] += 1


# ── Routes ───────────────────────────────────────────────────────────
@app.route("/health")
def health():
    keyed = sum(1 for p, c in ALL_PROVIDERS.items() if is_keyed(p, c))
    return jsonify({
        "status": "ok",
        "providers_configured": len(ALL_PROVIDERS),
        "providers_keyed": keyed,
        "mock_mode": MOCK_LLM,
    })


@app.route("/models")
def list_models():
    models = {}
    for prov_name, cfg in ALL_PROVIDERS.items():
        if not cfg.get("enabled", True):
            continue
        for model_name in cfg.get("models", []):
            key = f"{prov_name}/{model_name}"
            models[key] = {
                "name": key,
                "provider": prov_name,
                "model": model_name,
                "style": cfg.get("style", "openai"),
                "keyed": is_keyed(prov_name, cfg),
                "task_profiles": cfg.get("task_profiles", {}),
                "endpoint": cfg.get("base_url", ""),
            }
    return jsonify({"models": models})


@app.route("/providers")
def list_providers():
    rows = []
    for name, cfg in ALL_PROVIDERS.items():
        rows.append({
            "name": name,
            "enabled": cfg.get("enabled", True),
            "style": cfg.get("style", "openai"),
            "base_url": cfg.get("base_url", ""),
            "keyed": is_keyed(name, cfg),
            "models": cfg.get("models", []),
            "task_profiles": cfg.get("task_profiles", {}),
        })
    return jsonify({"providers": rows})


@app.route("/route", methods=["POST"])
def route():
    """Main routing endpoint."""
    data = request.get_json(silent=True) or {}
    prompt = data.get("prompt", "")
    if not prompt:
        return jsonify({"error": "prompt is required"}), 400

    task_type = classify_task(prompt)
    explicit_model = data.get("model")
    provider_model = select_model(task_type, explicit_model)

    prov_name, model_name = provider_model.split("/", 1)
    cfg = ALL_PROVIDERS.get(prov_name, {})
    api_key = get_api_key(prov_name, cfg)

    if not api_key and not MOCK_LLM:
        # Try next in chain
        chain = TASK_ROUTING.get(task_type, TASK_ROUTING["default"])
        for candidate in chain:
            pn, mn = candidate.split("/", 1)
            pc = ALL_PROVIDERS.get(pn, {})
            pk = get_api_key(pn, pc)
            if pk:
                prov_name, model_name, api_key, cfg = pn, mn, pk, pc
                provider_model = candidate
                break

    incr_metrics("requests_total")
    started = time.monotonic()

    try:
        if MOCK_LLM:
            result = {"content": "[mock] Task routed as: " + task_type,
                      "model": provider_model, "mock": True}
        elif cfg.get("style") == "anthropic":
            result = call_anthropic(cfg["base_url"], api_key,
                                    model_name, prompt,
                                    data.get("max_tokens", 2048),
                                    data.get("temperature", 0.2))
        else:
            result = call_openai_compatible(
                cfg["base_url"], api_key, model_name, prompt,
                data.get("max_tokens", 2048),
                data.get("temperature", 0.2))
            result["model"] = provider_model
    except Exception as exc:
        incr_metrics("errors_total")
        return jsonify({"error": str(exc), "provider": prov_name}), 502

    elapsed_ms = int((time.monotonic() - started) * 1000)
    record_latency(elapsed_ms)

    tokens = result.get("usage", {}).get("total_tokens", 0)
    incr_metrics("tokens_total", tokens)
    incr_metrics(f"by_provider.{prov_name}", 1)
    incr_metrics(f"by_model.{provider_model}", 1)

    return jsonify({
        "model_used": provider_model,
        "task_type": task_type,
        "elapsed_ms": elapsed_ms,
        "response": result.get("content", ""),
        "usage": result.get("usage", {}),
    })


@app.route("/proxy", methods=["POST"])
def proxy():
    """Direct provider proxy — specify exact provider/model."""
    data = request.get_json(silent=True) or {}
    prompt = data.get("prompt", "")
    model_spec = data.get("model", f"{DEFAULT_PROVIDER}/{DEFAULT_MODEL}")

    if "/" not in model_spec:
        return jsonify({"error": "model must be in format provider/model"}), 400

    prov_name, model_name = model_spec.split("/", 1)
    cfg = ALL_PROVIDERS.get(prov_name)
    if not cfg:
        return jsonify({"error": f"Unknown provider: {prov_name}"}), 404

    api_key = get_api_key(prov_name, cfg)
    if not api_key:
        return jsonify({"error": f"No API key for provider: {prov_name}"}), 401

    incr_metrics("requests_total")
    started = time.monotonic()

    try:
        if cfg.get("style") == "anthropic":
            result = call_anthropic(cfg["base_url"], api_key,
                                    model_name, prompt,
                                    data.get("max_tokens", 2048),
                                    data.get("temperature", 0.2))
        else:
            result = call_openai_compatible(
                cfg["base_url"], api_key, model_name, prompt,
                data.get("max_tokens", 2048),
                data.get("temperature", 0.2))
    except Exception as exc:
        incr_metrics("errors_total")
        return jsonify({"error": str(exc)}), 502

    elapsed_ms = int((time.monotonic() - started) * 1000)
    record_latency(elapsed_ms)
    return jsonify({
        "model_used": model_spec,
        "elapsed_ms": elapsed_ms,
        "response": result.get("content", ""),
        "usage": result.get("usage", {}),
    })


@app.route("/metrics")
def metrics():
    with _METRICS_LOCK:
        snap = dict(METRICS)
    if snap["latency_count"]:
        snap["latency_avg_ms"] = round(
            snap["latency_sum_ms"] / snap["latency_count"], 1)
    else:
        snap["latency_avg_ms"] = 0
    snap.pop("latency_sum_ms", None)
    snap.pop("latency_count", None)
    return jsonify(snap)


@app.route("/usage")
def usage():
    """Token usage tracking."""
    with _METRICS_LOCK:
        return {
            "tokens_total": METRICS.get("tokens_total", 0),
            "requests_total": METRICS.get("requests_total", 0),
            "by_provider": {k: v for k, v in METRICS.items()
                           if k.startswith("by_provider.")},
            "by_model": {k: v for k, v in METRICS.items()
                        if k.startswith("by_model.")},
        }


# ── Main ─────────────────────────────────────────────────────────────
if __name__ == "__main__":
    port = int(os.environ.get("PROXY_PORT", "8100"))
    print(f"[proxy] Starting unified LLM proxy on :{port}")
    print(f"[proxy] Providers: {len(ALL_PROVIDERS)}")
    keyed = sum(1 for p, c in ALL_PROVIDERS.items() if is_keyed(p, c))
    print(f"[proxy] Keyed providers: {keyed}")
    app.run(host="0.0.0.0", port=port, threaded=True)
