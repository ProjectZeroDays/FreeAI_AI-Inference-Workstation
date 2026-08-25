"""External AI provider bridge (llmv-era expansion).

Turns any hosted model API into a Tokugawa backend. Three wire styles
cover effectively every host:

  openai    - OpenAI-compatible /chat/completions (OpenAI, Groq, Mistral,
              DeepSeek, Together, Fireworks, OpenRouter, xAI, Cerebras,
              SambaNova, Novita, DeepInfra, Hyperbolic, Perplexity,
              HuggingFace router, Cohere-compat, Ollama, LM Studio, vLLM)
  anthropic - /v1/messages (x-api-key + anthropic-version)
  gemini    - generateContent (x-goog-api-key)

User config: config/providers.json (see providers.example.json).
API keys come from the environment (never stored in the file).
"""
import json
import os
import time

import requests

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROVIDERS_PATH = os.path.join(ROOT, "config", "providers.json")

# ---------------------------------------------------------------- presets
PRESETS = {
    "openai": {
        "style": "openai", "base_url": "https://api.openai.com/v1",
        "key_env": "OPENAI_API_KEY",
        "models": ["gpt-4o", "gpt-4o-mini", "o3-mini"],
        "description": "OpenAI GPT-4o family + o-series",
    },
    "anthropic": {
        "style": "anthropic", "base_url": "https://api.anthropic.com",
        "key_env": "ANTHROPIC_API_KEY",
        "models": ["claude-sonnet-4-5", "claude-opus-4-1",
                   "claude-haiku-4-5"],
        "description": "Claude Sonnet/Opus/Haiku",
    },
    "google": {
        "style": "gemini",
        "base_url": "https://generativelanguage.googleapis.com/v1beta",
        "key_env": "GOOGLE_API_KEY",
        "models": ["gemini-2.5-pro", "gemini-2.5-flash"],
        "description": "Gemini 2.5 Pro/Flash",
    },
    "groq": {
        "style": "openai", "base_url": "https://api.groq.com/openai/v1",
        "key_env": "GROQ_API_KEY",
        "models": ["llama-3.3-70b-versatile", "qwen/qwen3-32b"],
        "description": "Groq LPU inference (Llama, Qwen)",
    },
    "mistral": {
        "style": "openai", "base_url": "https://api.mistral.ai/v1",
        "key_env": "MISTRAL_API_KEY",
        "models": ["mistral-large-latest", "codestral-latest"],
        "description": "Mistral Large + Codestral",
    },
    "deepseek": {
        "style": "openai", "base_url": "https://api.deepseek.com/v1",
        "key_env": "DEEPSEEK_API_KEY",
        "models": ["deepseek-chat", "deepseek-reasoner"],
        "description": "DeepSeek V3 chat + R1 reasoner",
    },
    "together": {
        "style": "openai", "base_url": "https://api.together.xyz/v1",
        "key_env": "TOGETHER_API_KEY",
        "models": ["Qwen/Qwen2.5-Coder-32B-Instruct",
                   "meta-llama/Llama-3.3-70B-Instruct-Turbo"],
        "description": "Together.ai hosted open models",
    },
    "fireworks": {
        "style": "openai",
        "base_url": "https://api.fireworks.ai/inference/v1",
        "key_env": "FIREWORKS_API_KEY",
        "models": ["accounts/fireworks/models/qwen2p5-coder-32b-instruct"],
        "description": "Fireworks AI",
    },
    "openrouter": {
        "style": "openai", "base_url": "https://openrouter.ai/api/v1",
        "key_env": "OPENROUTER_API_KEY",
        "models": ["anthropic/claude-3.5-sonnet",
                   "qwen/qwen-2.5-coder-32b-instruct"],
        "description": "OpenRouter meta-aggregator (400+ models)",
    },
    "xai": {
        "style": "openai", "base_url": "https://api.x.ai/v1",
        "key_env": "XAI_API_KEY",
        "models": ["grok-4", "grok-3-mini"],
        "description": "xAI Grok",
    },
    "perplexity": {
        "style": "openai", "base_url": "https://api.perplexity.ai",
        "key_env": "PERPLEXITY_API_KEY",
        "models": ["sonar-pro", "sonar-reasoning"],
        "description": "Perplexity online/reasoning models",
    },
    "cerebras": {
        "style": "openai", "base_url": "https://api.cerebras.ai/v1",
        "key_env": "CEREBRAS_API_KEY",
        "models": ["llama-3.3-70b", "qwen-3-32b"],
        "description": "Cerebras wafer-scale inference",
    },
    "sambanova": {
        "style": "openai", "base_url": "https://api.sambanova.ai/v1",
        "key_env": "SAMBANOVA_API_KEY",
        "models": ["Meta-Llama-3.3-70B-Instruct"],
        "description": "SambaNova RDU inference",
    },
    "cohere": {
        "style": "openai",
        "base_url": "https://api.cohere.ai/compatibility/v1",
        "key_env": "COHERE_API_KEY",
        "models": ["command-r-plus"],
        "description": "Cohere Command R (OpenAI-compat)",
    },
    "novita": {
        "style": "openai", "base_url": "https://api.novita.ai/v3/openai",
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
    "hyperbolic": {
        "style": "openai", "base_url": "https://api.hyperbolic.xyz/v1",
        "key_env": "HYPERBOLIC_API_KEY",
        "models": ["meta-llama/Llama-3.3-70B-Instruct"],
        "description": "Hyperbolic",
    },
    "huggingface": {
        "style": "openai", "base_url": "https://router.huggingface.co/v1",
        "key_env": "HF_TOKEN",
        "models": ["Qwen/Qwen2.5-Coder-32B-Instruct"],
        "description": "HuggingFace Inference router",
    },
    "ollama": {
        "style": "openai", "base_url": "http://localhost:11434/v1",
        "key_env": None,
        "models": ["qwen2.5-coder", "llama3.2"],
        "description": "Local Ollama (OpenAI endpoint)",
    },
    "lmstudio": {
        "style": "openai", "base_url": "http://localhost:1234/v1",
        "key_env": None,
        "models": ["local-model"],
        "description": "LM Studio (local server)",
    },
}

# ---------------------------------------------------------------- loading
def load_providers():
    """Presets merged with config/providers.json overrides/additions.

    Each entry: {style, base_url, key_env, models[], description,
    fallback(bool), api_key(opt literal, discouraged), enabled(bool)}.
    """
    merged = {k: dict(v) for k, v in PRESETS.items()}
    try:
        with open(PROVIDERS_PATH) as f:
            user = json.load(f)
        for name, cfg in (user.get("providers") or {}).items():
            if name in merged:
                merged[name].update(cfg)
            else:
                merged[name] = dict(cfg)
    except (OSError, ValueError):
        pass
    for name, cfg in merged.items():
        cfg.setdefault("enabled", True)
        cfg.setdefault("fallback", False)
        cfg.setdefault("style", "openai")
        cfg.setdefault("models", [])
    return merged


def is_keyed(name, cfg):
    key = cfg.get("api_key") or (
        os.environ.get(cfg["key_env"]) if cfg.get("key_env") else None)
    return bool(key)


def get_key(name, cfg):
    return cfg.get("api_key") or (
        os.environ.get(cfg["key_env"]) if cfg.get("key_env") else "") or ""


def keyed_providers():
    out = {}
    for name, cfg in load_providers().items():
        if cfg.get("enabled") and is_keyed(name, cfg):
            out[name] = cfg
    return out


def fallback_models():
    """Provider models appended to local chains (keyed + fallback=true)."""
    ids = []
    for name, cfg in keyed_providers().items():
        if cfg.get("fallback"):
            for m in cfg["models"]:
                ids.append(f"{name}/{m}")
    return ids


# ---------------------------------------------------------------- adapters
def _payload_openai(model, prompt, max_tokens, temperature, stream):
    return {
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": max_tokens,
        "temperature": temperature,
        "stream": bool(stream),
    }


def _payload_anthropic(model, prompt, max_tokens, temperature):
    return {
        "model": model,
        "max_tokens": max_tokens,
        "temperature": temperature,
        "messages": [{"role": "user", "content": prompt}],
    }


def _payload_gemini(model, prompt, max_tokens, temperature):
    return {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {"maxOutputTokens": max_tokens,
                             "temperature": temperature},
    }


def build_request(name, cfg, model, prompt, max_tokens=2048,
                  temperature=0.2, stream=False):
    style = cfg.get("style", "openai")
    key = get_key(name, cfg)
    if style == "anthropic":
        url = cfg["base_url"].rstrip("/") + "/v1/messages"
        headers = {"x-api-key": key,
                   "anthropic-version": "2023-06-01",
                   "Content-Type": "application/json"}
        body = _payload_anthropic(model, prompt, max_tokens, temperature)
    elif style == "gemini":
        url = (cfg["base_url"].rstrip("/")
               + f"/models/{model}:generateContent")
        headers = {"x-goog-api-key": key,
                   "Content-Type": "application/json"}
        body = _payload_gemini(model, prompt, max_tokens, temperature)
    else:
        url = cfg["base_url"].rstrip("/") + "/chat/completions"
        headers = {"Content-Type": "application/json"}
        if key:
            headers["Authorization"] = f"Bearer {key}"
        if name == "openrouter":
            headers["HTTP-Referer"] = "https://tokugawa.local"
            headers["X-Title"] = "Tokugawa Router"
        body = _payload_openai(model, prompt, max_tokens, temperature,
                               stream)
    return url, headers, body


def parse_response(name, cfg, data):
    """Normalize any provider reply to {'content', 'provider', 'model'}."""
    style = cfg.get("style", "openai")
    model = data.get("model") if isinstance(data, dict) else None
    if style == "anthropic":
        blocks = data.get("content") or []
        text = "".join(b.get("text", "") for b in blocks
                       if isinstance(b, dict))
    elif style == "gemini":
        cands = data.get("candidates") or [{}]
        parts = (cands[0].get("content") or {}).get("parts") or []
        text = "".join(p.get("text", "") for p in parts)
    else:
        choices = data.get("choices") or [{}]
        choice = choices[0] or {}
        msg = choice.get("message") or {}
        text = msg.get("content") or choice.get("text") or ""
    return {"content": text, "provider": name, "model": model,
            "usage": data.get("usage") if isinstance(data, dict) else None}


def call_provider(name, cfg, model, prompt, max_tokens=2048,
                  temperature=0.2, timeout=None):
    url, headers, body = build_request(name, cfg, model, prompt,
                                       max_tokens, temperature)
    r = requests.post(url, headers=headers, json=body,
                      timeout=timeout or 120)
    r.raise_for_status()
    return parse_response(name, cfg, r.json())
