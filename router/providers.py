"""External AI provider bridge (llmv-era expansion).

Turns any hosted model API into a FreeAI backend. Three wire styles
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
    "freetoken": {
        "style": "openai",
        "base_url": os.environ.get("FREETOKEN_BASE_URL",
                                   "http://localhost:9100/v1"),
        "key_env": None,
        "models": ["deepseek-ai/DeepSeek-V4-Flash",
                   "Qwen/Qwen3.6-35B-A3B", "zai-org/GLM-5.2"],
        "description": "FreeToken edge MoE (290B+ on consumer GPUs)",
        "auto_fallback_when_healthy": True,
    },
    "venice": {
        "style": "openai", "base_url": "https://api.venice.ai/api/v1",
        "key_env": "VENICE_API_KEY",
        "models": ["qwen-edit-uncensored", "gemma-4-uncensored", "venice-uncensored-1-2", "llama-3.3-70b"],
        "description": "Venice Uncensored (Red Team Primary)",
    },
    "agnes": {
        "style": "openai", "base_url": "https://apihub.agnes-ai.com/v1",
        "key_env": "AGNES_API_KEY",
        "models": ["agnes-2.0-flash"],
        "description": "Agnes AI Flash",
    },
    "ext001": {
        "style": "openai", "base_url": "https://api.ext001.ai/v1",
        "key_env": "EXT001_API_KEY",
        "models": ["ext001/model-a", "ext001/model-b"],
        "description": "Extended provider 001 (auto-generated, disabled by default)",
        "enabled": False,
    },
    "ext002": {
        "style": "openai", "base_url": "https://api.ext002.ai/v1",
        "key_env": "EXT002_API_KEY",
        "models": ["ext002/model-a", "ext002/model-b"],
        "description": "Extended provider 002 (auto-generated, disabled by default)",
        "enabled": False,
    },
    "ext003": {
        "style": "openai", "base_url": "https://api.ext003.ai/v1",
        "key_env": "EXT003_API_KEY",
        "models": ["ext003/model-a", "ext003/model-b"],
        "description": "Extended provider 003 (auto-generated, disabled by default)",
        "enabled": False,
    },
    "ext004": {
        "style": "openai", "base_url": "https://api.ext004.ai/v1",
        "key_env": "EXT004_API_KEY",
        "models": ["ext004/model-a", "ext004/model-b"],
        "description": "Extended provider 004 (auto-generated, disabled by default)",
        "enabled": False,
    },
    "ext005": {
        "style": "openai", "base_url": "https://api.ext005.ai/v1",
        "key_env": "EXT005_API_KEY",
        "models": ["ext005/model-a", "ext005/model-b"],
        "description": "Extended provider 005 (auto-generated, disabled by default)",
        "enabled": False,
    },
    "ext006": {
        "style": "openai", "base_url": "https://api.ext006.ai/v1",
        "key_env": "EXT006_API_KEY",
        "models": ["ext006/model-a", "ext006/model-b"],
        "description": "Extended provider 006 (auto-generated, disabled by default)",
        "enabled": False,
    },
    "ext007": {
        "style": "openai", "base_url": "https://api.ext007.ai/v1",
        "key_env": "EXT007_API_KEY",
        "models": ["ext007/model-a", "ext007/model-b"],
        "description": "Extended provider 007 (auto-generated, disabled by default)",
        "enabled": False,
    },
    "ext008": {
        "style": "openai", "base_url": "https://api.ext008.ai/v1",
        "key_env": "EXT008_API_KEY",
        "models": ["ext008/model-a", "ext008/model-b"],
        "description": "Extended provider 008 (auto-generated, disabled by default)",
        "enabled": False,
    },
    "ext009": {
        "style": "openai", "base_url": "https://api.ext009.ai/v1",
        "key_env": "EXT009_API_KEY",
        "models": ["ext009/model-a", "ext009/model-b"],
        "description": "Extended provider 009 (auto-generated, disabled by default)",
        "enabled": False,
    },
    "ext010": {
        "style": "openai", "base_url": "https://api.ext010.ai/v1",
        "key_env": "EXT010_API_KEY",
        "models": ["ext010/model-a", "ext010/model-b"],
        "description": "Extended provider 010 (auto-generated, disabled by default)",
        "enabled": False,
    },
    "ext011": {
        "style": "openai", "base_url": "https://api.ext011.ai/v1",
        "key_env": "EXT011_API_KEY",
        "models": ["ext011/model-a", "ext011/model-b"],
        "description": "Extended provider 011 (auto-generated, disabled by default)",
        "enabled": False,
    },
    "ext012": {
        "style": "openai", "base_url": "https://api.ext012.ai/v1",
        "key_env": "EXT012_API_KEY",
        "models": ["ext012/model-a", "ext012/model-b"],
        "description": "Extended provider 012 (auto-generated, disabled by default)",
        "enabled": False,
    },
    "ext013": {
        "style": "openai", "base_url": "https://api.ext013.ai/v1",
        "key_env": "EXT013_API_KEY",
        "models": ["ext013/model-a", "ext013/model-b"],
        "description": "Extended provider 013 (auto-generated, disabled by default)",
        "enabled": False,
    },
    "ext014": {
        "style": "openai", "base_url": "https://api.ext014.ai/v1",
        "key_env": "EXT014_API_KEY",
        "models": ["ext014/model-a", "ext014/model-b"],
        "description": "Extended provider 014 (auto-generated, disabled by default)",
        "enabled": False,
    },
    "ext015": {
        "style": "openai", "base_url": "https://api.ext015.ai/v1",
        "key_env": "EXT015_API_KEY",
        "models": ["ext015/model-a", "ext015/model-b"],
        "description": "Extended provider 015 (auto-generated, disabled by default)",
        "enabled": False,
    },
    "ext016": {
        "style": "openai", "base_url": "https://api.ext016.ai/v1",
        "key_env": "EXT016_API_KEY",
        "models": ["ext016/model-a", "ext016/model-b"],
        "description": "Extended provider 016 (auto-generated, disabled by default)",
        "enabled": False,
    },
    "ext017": {
        "style": "openai", "base_url": "https://api.ext017.ai/v1",
        "key_env": "EXT017_API_KEY",
        "models": ["ext017/model-a", "ext017/model-b"],
        "description": "Extended provider 017 (auto-generated, disabled by default)",
        "enabled": False,
    },
    "ext018": {
        "style": "openai", "base_url": "https://api.ext018.ai/v1",
        "key_env": "EXT018_API_KEY",
        "models": ["ext018/model-a", "ext018/model-b"],
        "description": "Extended provider 018 (auto-generated, disabled by default)",
        "enabled": False,
    },
    "ext019": {
        "style": "openai", "base_url": "https://api.ext019.ai/v1",
        "key_env": "EXT019_API_KEY",
        "models": ["ext019/model-a", "ext019/model-b"],
        "description": "Extended provider 019 (auto-generated, disabled by default)",
        "enabled": False,
    },
    "ext020": {
        "style": "openai", "base_url": "https://api.ext020.ai/v1",
        "key_env": "EXT020_API_KEY",
        "models": ["ext020/model-a", "ext020/model-b"],
        "description": "Extended provider 020 (auto-generated, disabled by default)",
        "enabled": False,
    },
    "ext021": {
        "style": "openai", "base_url": "https://api.ext021.ai/v1",
        "key_env": "EXT021_API_KEY",
        "models": ["ext021/model-a", "ext021/model-b"],
        "description": "Extended provider 021 (auto-generated, disabled by default)",
        "enabled": False,
    },
    "ext022": {
        "style": "openai", "base_url": "https://api.ext022.ai/v1",
        "key_env": "EXT022_API_KEY",
        "models": ["ext022/model-a", "ext022/model-b"],
        "description": "Extended provider 022 (auto-generated, disabled by default)",
        "enabled": False,
    },
    "ext023": {
        "style": "openai", "base_url": "https://api.ext023.ai/v1",
        "key_env": "EXT023_API_KEY",
        "models": ["ext023/model-a", "ext023/model-b"],
        "description": "Extended provider 023 (auto-generated, disabled by default)",
        "enabled": False,
    },
    "ext024": {
        "style": "openai", "base_url": "https://api.ext024.ai/v1",
        "key_env": "EXT024_API_KEY",
        "models": ["ext024/model-a", "ext024/model-b"],
        "description": "Extended provider 024 (auto-generated, disabled by default)",
        "enabled": False,
    },
    "ext025": {
        "style": "openai", "base_url": "https://api.ext025.ai/v1",
        "key_env": "EXT025_API_KEY",
        "models": ["ext025/model-a", "ext025/model-b"],
        "description": "Extended provider 025 (auto-generated, disabled by default)",
        "enabled": False,
    },
    "ext026": {
        "style": "openai", "base_url": "https://api.ext026.ai/v1",
        "key_env": "EXT026_API_KEY",
        "models": ["ext026/model-a", "ext026/model-b"],
        "description": "Extended provider 026 (auto-generated, disabled by default)",
        "enabled": False,
    },
    "ext027": {
        "style": "openai", "base_url": "https://api.ext027.ai/v1",
        "key_env": "EXT027_API_KEY",
        "models": ["ext027/model-a", "ext027/model-b"],
        "description": "Extended provider 027 (auto-generated, disabled by default)",
        "enabled": False,
    },
    "ext028": {
        "style": "openai", "base_url": "https://api.ext028.ai/v1",
        "key_env": "EXT028_API_KEY",
        "models": ["ext028/model-a", "ext028/model-b"],
        "description": "Extended provider 028 (auto-generated, disabled by default)",
        "enabled": False,
    },
    "ext029": {
        "style": "openai", "base_url": "https://api.ext029.ai/v1",
        "key_env": "EXT029_API_KEY",
        "models": ["ext029/model-a", "ext029/model-b"],
        "description": "Extended provider 029 (auto-generated, disabled by default)",
        "enabled": False,
    },
    "ext030": {
        "style": "openai", "base_url": "https://api.ext030.ai/v1",
        "key_env": "EXT030_API_KEY",
        "models": ["ext030/model-a", "ext030/model-b"],
        "description": "Extended provider 030 (auto-generated, disabled by default)",
        "enabled": False,
    },
    "ext031": {
        "style": "openai", "base_url": "https://api.ext031.ai/v1",
        "key_env": "EXT031_API_KEY",
        "models": ["ext031/model-a", "ext031/model-b"],
        "description": "Extended provider 031 (auto-generated, disabled by default)",
        "enabled": False,
    },
    "ext032": {
        "style": "openai", "base_url": "https://api.ext032.ai/v1",
        "key_env": "EXT032_API_KEY",
        "models": ["ext032/model-a", "ext032/model-b"],
        "description": "Extended provider 032 (auto-generated, disabled by default)",
        "enabled": False,
    },
    "ext033": {
        "style": "openai", "base_url": "https://api.ext033.ai/v1",
        "key_env": "EXT033_API_KEY",
        "models": ["ext033/model-a", "ext033/model-b"],
        "description": "Extended provider 033 (auto-generated, disabled by default)",
        "enabled": False,
    },
    "ext034": {
        "style": "openai", "base_url": "https://api.ext034.ai/v1",
        "key_env": "EXT034_API_KEY",
        "models": ["ext034/model-a", "ext034/model-b"],
        "description": "Extended provider 034 (auto-generated, disabled by default)",
        "enabled": False,
    },
    "ext035": {
        "style": "openai", "base_url": "https://api.ext035.ai/v1",
        "key_env": "EXT035_API_KEY",
        "models": ["ext035/model-a", "ext035/model-b"],
        "description": "Extended provider 035 (auto-generated, disabled by default)",
        "enabled": False,
    },
    "ext036": {
        "style": "openai", "base_url": "https://api.ext036.ai/v1",
        "key_env": "EXT036_API_KEY",
        "models": ["ext036/model-a", "ext036/model-b"],
        "description": "Extended provider 036 (auto-generated, disabled by default)",
        "enabled": False,
    },
    "ext037": {
        "style": "openai", "base_url": "https://api.ext037.ai/v1",
        "key_env": "EXT037_API_KEY",
        "models": ["ext037/model-a", "ext037/model-b"],
        "description": "Extended provider 037 (auto-generated, disabled by default)",
        "enabled": False,
    },
    "ext038": {
        "style": "openai", "base_url": "https://api.ext038.ai/v1",
        "key_env": "EXT038_API_KEY",
        "models": ["ext038/model-a", "ext038/model-b"],
        "description": "Extended provider 038 (auto-generated, disabled by default)",
        "enabled": False,
    },
    "ext039": {
        "style": "openai", "base_url": "https://api.ext039.ai/v1",
        "key_env": "EXT039_API_KEY",
        "models": ["ext039/model-a", "ext039/model-b"],
        "description": "Extended provider 039 (auto-generated, disabled by default)",
        "enabled": False,
    },
    "ext040": {
        "style": "openai", "base_url": "https://api.ext040.ai/v1",
        "key_env": "EXT040_API_KEY",
        "models": ["ext040/model-a", "ext040/model-b"],
        "description": "Extended provider 040 (auto-generated, disabled by default)",
        "enabled": False,
    },
    "ext041": {
        "style": "openai", "base_url": "https://api.ext041.ai/v1",
        "key_env": "EXT041_API_KEY",
        "models": ["ext041/model-a", "ext041/model-b"],
        "description": "Extended provider 041 (auto-generated, disabled by default)",
        "enabled": False,
    },
    "ext042": {
        "style": "openai", "base_url": "https://api.ext042.ai/v1",
        "key_env": "EXT042_API_KEY",
        "models": ["ext042/model-a", "ext042/model-b"],
        "description": "Extended provider 042 (auto-generated, disabled by default)",
        "enabled": False,
    },
    "ext043": {
        "style": "openai", "base_url": "https://api.ext043.ai/v1",
        "key_env": "EXT043_API_KEY",
        "models": ["ext043/model-a", "ext043/model-b"],
        "description": "Extended provider 043 (auto-generated, disabled by default)",
        "enabled": False,
    },
    "ext044": {
        "style": "openai", "base_url": "https://api.ext044.ai/v1",
        "key_env": "EXT044_API_KEY",
        "models": ["ext044/model-a", "ext044/model-b"],
        "description": "Extended provider 044 (auto-generated, disabled by default)",
        "enabled": False,
    },
    "ext045": {
        "style": "openai", "base_url": "https://api.ext045.ai/v1",
        "key_env": "EXT045_API_KEY",
        "models": ["ext045/model-a", "ext045/model-b"],
        "description": "Extended provider 045 (auto-generated, disabled by default)",
        "enabled": False,
    },
    "ext046": {
        "style": "openai", "base_url": "https://api.ext046.ai/v1",
        "key_env": "EXT046_API_KEY",
        "models": ["ext046/model-a", "ext046/model-b"],
        "description": "Extended provider 046 (auto-generated, disabled by default)",
        "enabled": False,
    },
    "ext047": {
        "style": "openai", "base_url": "https://api.ext047.ai/v1",
        "key_env": "EXT047_API_KEY",
        "models": ["ext047/model-a", "ext047/model-b"],
        "description": "Extended provider 047 (auto-generated, disabled by default)",
        "enabled": False,
    },
    "ext048": {
        "style": "openai", "base_url": "https://api.ext048.ai/v1",
        "key_env": "EXT048_API_KEY",
        "models": ["ext048/model-a", "ext048/model-b"],
        "description": "Extended provider 048 (auto-generated, disabled by default)",
        "enabled": False,
    },
    "ext049": {
        "style": "openai", "base_url": "https://api.ext049.ai/v1",
        "key_env": "EXT049_API_KEY",
        "models": ["ext049/model-a", "ext049/model-b"],
        "description": "Extended provider 049 (auto-generated, disabled by default)",
        "enabled": False,
    },
    "ext050": {
        "style": "openai", "base_url": "https://api.ext050.ai/v1",
        "key_env": "EXT050_API_KEY",
        "models": ["ext050/model-a", "ext050/model-b"],
        "description": "Extended provider 050 (auto-generated, disabled by default)",
        "enabled": False,
    },
    "ext051": {
        "style": "openai", "base_url": "https://api.ext051.ai/v1",
        "key_env": "EXT051_API_KEY",
        "models": ["ext051/model-a", "ext051/model-b"],
        "description": "Extended provider 051 (auto-generated, disabled by default)",
        "enabled": False,
    },
    "ext052": {
        "style": "openai", "base_url": "https://api.ext052.ai/v1",
        "key_env": "EXT052_API_KEY",
        "models": ["ext052/model-a", "ext052/model-b"],
        "description": "Extended provider 052 (auto-generated, disabled by default)",
        "enabled": False,
    },
    "ext053": {
        "style": "openai", "base_url": "https://api.ext053.ai/v1",
        "key_env": "EXT053_API_KEY",
        "models": ["ext053/model-a", "ext053/model-b"],
        "description": "Extended provider 053 (auto-generated, disabled by default)",
        "enabled": False,
    },
    "ext054": {
        "style": "openai", "base_url": "https://api.ext054.ai/v1",
        "key_env": "EXT054_API_KEY",
        "models": ["ext054/model-a", "ext054/model-b"],
        "description": "Extended provider 054 (auto-generated, disabled by default)",
        "enabled": False,
    },
    "ext055": {
        "style": "openai", "base_url": "https://api.ext055.ai/v1",
        "key_env": "EXT055_API_KEY",
        "models": ["ext055/model-a", "ext055/model-b"],
        "description": "Extended provider 055 (auto-generated, disabled by default)",
        "enabled": False,
    },
    "ext056": {
        "style": "openai", "base_url": "https://api.ext056.ai/v1",
        "key_env": "EXT056_API_KEY",
        "models": ["ext056/model-a", "ext056/model-b"],
        "description": "Extended provider 056 (auto-generated, disabled by default)",
        "enabled": False,
    },
    "ext057": {
        "style": "openai", "base_url": "https://api.ext057.ai/v1",
        "key_env": "EXT057_API_KEY",
        "models": ["ext057/model-a", "ext057/model-b"],
        "description": "Extended provider 057 (auto-generated, disabled by default)",
        "enabled": False,
    },
    "ext058": {
        "style": "openai", "base_url": "https://api.ext058.ai/v1",
        "key_env": "EXT058_API_KEY",
        "models": ["ext058/model-a", "ext058/model-b"],
        "description": "Extended provider 058 (auto-generated, disabled by default)",
        "enabled": False,
    },
    "ext059": {
        "style": "openai", "base_url": "https://api.ext059.ai/v1",
        "key_env": "EXT059_API_KEY",
        "models": ["ext059/model-a", "ext059/model-b"],
        "description": "Extended provider 059 (auto-generated, disabled by default)",
        "enabled": False,
    },
    "ext060": {
        "style": "openai", "base_url": "https://api.ext060.ai/v1",
        "key_env": "EXT060_API_KEY",
        "models": ["ext060/model-a", "ext060/model-b"],
        "description": "Extended provider 060 (auto-generated, disabled by default)",
        "enabled": False,
    },
    "ext061": {
        "style": "openai", "base_url": "https://api.ext061.ai/v1",
        "key_env": "EXT061_API_KEY",
        "models": ["ext061/model-a", "ext061/model-b"],
        "description": "Extended provider 061 (auto-generated, disabled by default)",
        "enabled": False,
    },
    "ext062": {
        "style": "openai", "base_url": "https://api.ext062.ai/v1",
        "key_env": "EXT062_API_KEY",
        "models": ["ext062/model-a", "ext062/model-b"],
        "description": "Extended provider 062 (auto-generated, disabled by default)",
        "enabled": False,
    },
    "ext063": {
        "style": "openai", "base_url": "https://api.ext063.ai/v1",
        "key_env": "EXT063_API_KEY",
        "models": ["ext063/model-a", "ext063/model-b"],
        "description": "Extended provider 063 (auto-generated, disabled by default)",
        "enabled": False,
    },
    "ext064": {
        "style": "openai", "base_url": "https://api.ext064.ai/v1",
        "key_env": "EXT064_API_KEY",
        "models": ["ext064/model-a", "ext064/model-b"],
        "description": "Extended provider 064 (auto-generated, disabled by default)",
        "enabled": False,
    },
    "ext065": {
        "style": "openai", "base_url": "https://api.ext065.ai/v1",
        "key_env": "EXT065_API_KEY",
        "models": ["ext065/model-a", "ext065/model-b"],
        "description": "Extended provider 065 (auto-generated, disabled by default)",
        "enabled": False,
    },
    "ext066": {
        "style": "openai", "base_url": "https://api.ext066.ai/v1",
        "key_env": "EXT066_API_KEY",
        "models": ["ext066/model-a", "ext066/model-b"],
        "description": "Extended provider 066 (auto-generated, disabled by default)",
        "enabled": False,
    },
    "ext067": {
        "style": "openai", "base_url": "https://api.ext067.ai/v1",
        "key_env": "EXT067_API_KEY",
        "models": ["ext067/model-a", "ext067/model-b"],
        "description": "Extended provider 067 (auto-generated, disabled by default)",
        "enabled": False,
    },
    "ext068": {
        "style": "openai", "base_url": "https://api.ext068.ai/v1",
        "key_env": "EXT068_API_KEY",
        "models": ["ext068/model-a", "ext068/model-b"],
        "description": "Extended provider 068 (auto-generated, disabled by default)",
        "enabled": False,
    },
    "ext069": {
        "style": "openai", "base_url": "https://api.ext069.ai/v1",
        "key_env": "EXT069_API_KEY",
        "models": ["ext069/model-a", "ext069/model-b"],
        "description": "Extended provider 069 (auto-generated, disabled by default)",
        "enabled": False,
    },
    "ext070": {
        "style": "openai", "base_url": "https://api.ext070.ai/v1",
        "key_env": "EXT070_API_KEY",
        "models": ["ext070/model-a", "ext070/model-b"],
        "description": "Extended provider 070 (auto-generated, disabled by default)",
        "enabled": False,
    },
    "ext071": {
        "style": "openai", "base_url": "https://api.ext071.ai/v1",
        "key_env": "EXT071_API_KEY",
        "models": ["ext071/model-a", "ext071/model-b"],
        "description": "Extended provider 071 (auto-generated, disabled by default)",
        "enabled": False,
    },
    "ext072": {
        "style": "openai", "base_url": "https://api.ext072.ai/v1",
        "key_env": "EXT072_API_KEY",
        "models": ["ext072/model-a", "ext072/model-b"],
        "description": "Extended provider 072 (auto-generated, disabled by default)",
        "enabled": False,
    },
    "ext073": {
        "style": "openai", "base_url": "https://api.ext073.ai/v1",
        "key_env": "EXT073_API_KEY",
        "models": ["ext073/model-a", "ext073/model-b"],
        "description": "Extended provider 073 (auto-generated, disabled by default)",
        "enabled": False,
    },
    "ext074": {
        "style": "openai", "base_url": "https://api.ext074.ai/v1",
        "key_env": "EXT074_API_KEY",
        "models": ["ext074/model-a", "ext074/model-b"],
        "description": "Extended provider 074 (auto-generated, disabled by default)",
        "enabled": False,
    },
    "ext075": {
        "style": "openai", "base_url": "https://api.ext075.ai/v1",
        "key_env": "EXT075_API_KEY",
        "models": ["ext075/model-a", "ext075/model-b"],
        "description": "Extended provider 075 (auto-generated, disabled by default)",
        "enabled": False,
    },
    "ext076": {
        "style": "openai", "base_url": "https://api.ext076.ai/v1",
        "key_env": "EXT076_API_KEY",
        "models": ["ext076/model-a", "ext076/model-b"],
        "description": "Extended provider 076 (auto-generated, disabled by default)",
        "enabled": False,
    },
    "ext077": {
        "style": "openai", "base_url": "https://api.ext077.ai/v1",
        "key_env": "EXT077_API_KEY",
        "models": ["ext077/model-a", "ext077/model-b"],
        "description": "Extended provider 077 (auto-generated, disabled by default)",
        "enabled": False,
    },
    "ext078": {
        "style": "openai", "base_url": "https://api.ext078.ai/v1",
        "key_env": "EXT078_API_KEY",
        "models": ["ext078/model-a", "ext078/model-b"],
        "description": "Extended provider 078 (auto-generated, disabled by default)",
        "enabled": False,
    },
    "ext079": {
        "style": "openai", "base_url": "https://api.ext079.ai/v1",
        "key_env": "EXT079_API_KEY",
        "models": ["ext079/model-a", "ext079/model-b"],
        "description": "Extended provider 079 (auto-generated, disabled by default)",
        "enabled": False,
    },
    "ext080": {
        "style": "openai", "base_url": "https://api.ext080.ai/v1",
        "key_env": "EXT080_API_KEY",
        "models": ["ext080/model-a", "ext080/model-b"],
        "description": "Extended provider 080 (auto-generated, disabled by default)",
        "enabled": False,
    },
    "ext081": {
        "style": "openai", "base_url": "https://api.ext081.ai/v1",
        "key_env": "EXT081_API_KEY",
        "models": ["ext081/model-a", "ext081/model-b"],
        "description": "Extended provider 081 (auto-generated, disabled by default)",
        "enabled": False,
    },
    "ext082": {
        "style": "openai", "base_url": "https://api.ext082.ai/v1",
        "key_env": "EXT082_API_KEY",
        "models": ["ext082/model-a", "ext082/model-b"],
        "description": "Extended provider 082 (auto-generated, disabled by default)",
        "enabled": False,
    },
    "ext083": {
        "style": "openai", "base_url": "https://api.ext083.ai/v1",
        "key_env": "EXT083_API_KEY",
        "models": ["ext083/model-a", "ext083/model-b"],
        "description": "Extended provider 083 (auto-generated, disabled by default)",
        "enabled": False,
    },
    "ext084": {
        "style": "openai", "base_url": "https://api.ext084.ai/v1",
        "key_env": "EXT084_API_KEY",
        "models": ["ext084/model-a", "ext084/model-b"],
        "description": "Extended provider 084 (auto-generated, disabled by default)",
        "enabled": False,
    },
    "ext085": {
        "style": "openai", "base_url": "https://api.ext085.ai/v1",
        "key_env": "EXT085_API_KEY",
        "models": ["ext085/model-a", "ext085/model-b"],
        "description": "Extended provider 085 (auto-generated, disabled by default)",
        "enabled": False,
    },
    "ext086": {
        "style": "openai", "base_url": "https://api.ext086.ai/v1",
        "key_env": "EXT086_API_KEY",
        "models": ["ext086/model-a", "ext086/model-b"],
        "description": "Extended provider 086 (auto-generated, disabled by default)",
        "enabled": False,
    },
    "ext087": {
        "style": "openai", "base_url": "https://api.ext087.ai/v1",
        "key_env": "EXT087_API_KEY",
        "models": ["ext087/model-a", "ext087/model-b"],
        "description": "Extended provider 087 (auto-generated, disabled by default)",
        "enabled": False,
    },
    "ext088": {
        "style": "openai", "base_url": "https://api.ext088.ai/v1",
        "key_env": "EXT088_API_KEY",
        "models": ["ext088/model-a", "ext088/model-b"],
        "description": "Extended provider 088 (auto-generated, disabled by default)",
        "enabled": False,
    },
    "ext089": {
        "style": "openai", "base_url": "https://api.ext089.ai/v1",
        "key_env": "EXT089_API_KEY",
        "models": ["ext089/model-a", "ext089/model-b"],
        "description": "Extended provider 089 (auto-generated, disabled by default)",
        "enabled": False,
    },
    "ext090": {
        "style": "openai", "base_url": "https://api.ext090.ai/v1",
        "key_env": "EXT090_API_KEY",
        "models": ["ext090/model-a", "ext090/model-b"],
        "description": "Extended provider 090 (auto-generated, disabled by default)",
        "enabled": False,
    },
    "ext091": {
        "style": "openai", "base_url": "https://api.ext091.ai/v1",
        "key_env": "EXT091_API_KEY",
        "models": ["ext091/model-a", "ext091/model-b"],
        "description": "Extended provider 091 (auto-generated, disabled by default)",
        "enabled": False,
    },
    "ext092": {
        "style": "openai", "base_url": "https://api.ext092.ai/v1",
        "key_env": "EXT092_API_KEY",
        "models": ["ext092/model-a", "ext092/model-b"],
        "description": "Extended provider 092 (auto-generated, disabled by default)",
        "enabled": False,
    },
    "ext093": {
        "style": "openai", "base_url": "https://api.ext093.ai/v1",
        "key_env": "EXT093_API_KEY",
        "models": ["ext093/model-a", "ext093/model-b"],
        "description": "Extended provider 093 (auto-generated, disabled by default)",
        "enabled": False,
    },
    "ext094": {
        "style": "openai", "base_url": "https://api.ext094.ai/v1",
        "key_env": "EXT094_API_KEY",
        "models": ["ext094/model-a", "ext094/model-b"],
        "description": "Extended provider 094 (auto-generated, disabled by default)",
        "enabled": False,
    },
    "ext095": {
        "style": "openai", "base_url": "https://api.ext095.ai/v1",
        "key_env": "EXT095_API_KEY",
        "models": ["ext095/model-a", "ext095/model-b"],
        "description": "Extended provider 095 (auto-generated, disabled by default)",
        "enabled": False,
    },
    "ext096": {
        "style": "openai", "base_url": "https://api.ext096.ai/v1",
        "key_env": "EXT096_API_KEY",
        "models": ["ext096/model-a", "ext096/model-b"],
        "description": "Extended provider 096 (auto-generated, disabled by default)",
        "enabled": False,
    },
    "ext097": {
        "style": "openai", "base_url": "https://api.ext097.ai/v1",
        "key_env": "EXT097_API_KEY",
        "models": ["ext097/model-a", "ext097/model-b"],
        "description": "Extended provider 097 (auto-generated, disabled by default)",
        "enabled": False,
    },
    "ext098": {
        "style": "openai", "base_url": "https://api.ext098.ai/v1",
        "key_env": "EXT098_API_KEY",
        "models": ["ext098/model-a", "ext098/model-b"],
        "description": "Extended provider 098 (auto-generated, disabled by default)",
        "enabled": False,
    },
    "ext099": {
        "style": "openai", "base_url": "https://api.ext099.ai/v1",
        "key_env": "EXT099_API_KEY",
        "models": ["ext099/model-a", "ext099/model-b"],
        "description": "Extended provider 099 (auto-generated, disabled by default)",
        "enabled": False,
    },
    "ext100": {
        "style": "openai", "base_url": "https://api.ext100.ai/v1",
        "key_env": "EXT100_API_KEY",
        "models": ["ext100/model-a", "ext100/model-b"],
        "description": "Extended provider 100 (auto-generated, disabled by default)",
        "enabled": False,
    },
    "ext101": {
        "style": "openai", "base_url": "https://api.ext101.ai/v1",
        "key_env": "EXT101_API_KEY",
        "models": ["ext101/model-a", "ext101/model-b"],
        "description": "Extended provider 101 (auto-generated, disabled by default)",
        "enabled": False,
    },
    "ext102": {
        "style": "openai", "base_url": "https://api.ext102.ai/v1",
        "key_env": "EXT102_API_KEY",
        "models": ["ext102/model-a", "ext102/model-b"],
        "description": "Extended provider 102 (auto-generated, disabled by default)",
        "enabled": False,
    },
    "ext103": {
        "style": "openai", "base_url": "https://api.ext103.ai/v1",
        "key_env": "EXT103_API_KEY",
        "models": ["ext103/model-a", "ext103/model-b"],
        "description": "Extended provider 103 (auto-generated, disabled by default)",
        "enabled": False,
    },
    "ext104": {
        "style": "openai", "base_url": "https://api.ext104.ai/v1",
        "key_env": "EXT104_API_KEY",
        "models": ["ext104/model-a", "ext104/model-b"],
        "description": "Extended provider 104 (auto-generated, disabled by default)",
        "enabled": False,
    },
    "ext105": {
        "style": "openai", "base_url": "https://api.ext105.ai/v1",
        "key_env": "EXT105_API_KEY",
        "models": ["ext105/model-a", "ext105/model-b"],
        "description": "Extended provider 105 (auto-generated, disabled by default)",
        "enabled": False,
    },
    "ext106": {
        "style": "openai", "base_url": "https://api.ext106.ai/v1",
        "key_env": "EXT106_API_KEY",
        "models": ["ext106/model-a", "ext106/model-b"],
        "description": "Extended provider 106 (auto-generated, disabled by default)",
        "enabled": False,
    },
    "ext107": {
        "style": "openai", "base_url": "https://api.ext107.ai/v1",
        "key_env": "EXT107_API_KEY",
        "models": ["ext107/model-a", "ext107/model-b"],
        "description": "Extended provider 107 (auto-generated, disabled by default)",
        "enabled": False,
    },
    "ext108": {
        "style": "openai", "base_url": "https://api.ext108.ai/v1",
        "key_env": "EXT108_API_KEY",
        "models": ["ext108/model-a", "ext108/model-b"],
        "description": "Extended provider 108 (auto-generated, disabled by default)",
        "enabled": False,
    },
    "ext109": {
        "style": "openai", "base_url": "https://api.ext109.ai/v1",
        "key_env": "EXT109_API_KEY",
        "models": ["ext109/model-a", "ext109/model-b"],
        "description": "Extended provider 109 (auto-generated, disabled by default)",
        "enabled": False,
    },
    "ext110": {
        "style": "openai", "base_url": "https://api.ext110.ai/v1",
        "key_env": "EXT110_API_KEY",
        "models": ["ext110/model-a", "ext110/model-b"],
        "description": "Extended provider 110 (auto-generated, disabled by default)",
        "enabled": False,
    },
    "ext111": {
        "style": "openai", "base_url": "https://api.ext111.ai/v1",
        "key_env": "EXT111_API_KEY",
        "models": ["ext111/model-a", "ext111/model-b"],
        "description": "Extended provider 111 (auto-generated, disabled by default)",
        "enabled": False,
    },
    "ext112": {
        "style": "openai", "base_url": "https://api.ext112.ai/v1",
        "key_env": "EXT112_API_KEY",
        "models": ["ext112/model-a", "ext112/model-b"],
        "description": "Extended provider 112 (auto-generated, disabled by default)",
        "enabled": False,
    },
    "ext113": {
        "style": "openai", "base_url": "https://api.ext113.ai/v1",
        "key_env": "EXT113_API_KEY",
        "models": ["ext113/model-a", "ext113/model-b"],
        "description": "Extended provider 113 (auto-generated, disabled by default)",
        "enabled": False,
    },
    "ext114": {
        "style": "openai", "base_url": "https://api.ext114.ai/v1",
        "key_env": "EXT114_API_KEY",
        "models": ["ext114/model-a", "ext114/model-b"],
        "description": "Extended provider 114 (auto-generated, disabled by default)",
        "enabled": False,
    },
    "ext115": {
        "style": "openai", "base_url": "https://api.ext115.ai/v1",
        "key_env": "EXT115_API_KEY",
        "models": ["ext115/model-a", "ext115/model-b"],
        "description": "Extended provider 115 (auto-generated, disabled by default)",
        "enabled": False,
    },
    "ext116": {
        "style": "openai", "base_url": "https://api.ext116.ai/v1",
        "key_env": "EXT116_API_KEY",
        "models": ["ext116/model-a", "ext116/model-b"],
        "description": "Extended provider 116 (auto-generated, disabled by default)",
        "enabled": False,
    },
    "ext117": {
        "style": "openai", "base_url": "https://api.ext117.ai/v1",
        "key_env": "EXT117_API_KEY",
        "models": ["ext117/model-a", "ext117/model-b"],
        "description": "Extended provider 117 (auto-generated, disabled by default)",
        "enabled": False,
    },
    "ext118": {
        "style": "openai", "base_url": "https://api.ext118.ai/v1",
        "key_env": "EXT118_API_KEY",
        "models": ["ext118/model-a", "ext118/model-b"],
        "description": "Extended provider 118 (auto-generated, disabled by default)",
        "enabled": False,
    },
    "ext119": {
        "style": "openai", "base_url": "https://api.ext119.ai/v1",
        "key_env": "EXT119_API_KEY",
        "models": ["ext119/model-a", "ext119/model-b"],
        "description": "Extended provider 119 (auto-generated, disabled by default)",
        "enabled": False,
    },
    "ext120": {
        "style": "openai", "base_url": "https://api.ext120.ai/v1",
        "key_env": "EXT120_API_KEY",
        "models": ["ext120/model-a", "ext120/model-b"],
        "description": "Extended provider 120 (auto-generated, disabled by default)",
        "enabled": False,
    },
    "ext121": {
        "style": "openai", "base_url": "https://api.ext121.ai/v1",
        "key_env": "EXT121_API_KEY",
        "models": ["ext121/model-a", "ext121/model-b"],
        "description": "Extended provider 121 (auto-generated, disabled by default)",
        "enabled": False,
    },
    "ext122": {
        "style": "openai", "base_url": "https://api.ext122.ai/v1",
        "key_env": "EXT122_API_KEY",
        "models": ["ext122/model-a", "ext122/model-b"],
        "description": "Extended provider 122 (auto-generated, disabled by default)",
        "enabled": False,
    },
    "ext123": {
        "style": "openai", "base_url": "https://api.ext123.ai/v1",
        "key_env": "EXT123_API_KEY",
        "models": ["ext123/model-a", "ext123/model-b"],
        "description": "Extended provider 123 (auto-generated, disabled by default)",
        "enabled": False,
    },
    "ext124": {
        "style": "openai", "base_url": "https://api.ext124.ai/v1",
        "key_env": "EXT124_API_KEY",
        "models": ["ext124/model-a", "ext124/model-b"],
        "description": "Extended provider 124 (auto-generated, disabled by default)",
        "enabled": False,
    },
    "ext125": {
        "style": "openai", "base_url": "https://api.ext125.ai/v1",
        "key_env": "EXT125_API_KEY",
        "models": ["ext125/model-a", "ext125/model-b"],
        "description": "Extended provider 125 (auto-generated, disabled by default)",
        "enabled": False,
    },
    "ext126": {
        "style": "openai", "base_url": "https://api.ext126.ai/v1",
        "key_env": "EXT126_API_KEY",
        "models": ["ext126/model-a", "ext126/model-b"],
        "description": "Extended provider 126 (auto-generated, disabled by default)",
        "enabled": False,
    },
    "ext127": {
        "style": "openai", "base_url": "https://api.ext127.ai/v1",
        "key_env": "EXT127_API_KEY",
        "models": ["ext127/model-a", "ext127/model-b"],
        "description": "Extended provider 127 (auto-generated, disabled by default)",
        "enabled": False,
    },
    "ext128": {
        "style": "openai", "base_url": "https://api.ext128.ai/v1",
        "key_env": "EXT128_API_KEY",
        "models": ["ext128/model-a", "ext128/model-b"],
        "description": "Extended provider 128 (auto-generated, disabled by default)",
        "enabled": False,
    },
    "ext129": {
        "style": "openai", "base_url": "https://api.ext129.ai/v1",
        "key_env": "EXT129_API_KEY",
        "models": ["ext129/model-a", "ext129/model-b"],
        "description": "Extended provider 129 (auto-generated, disabled by default)",
        "enabled": False,
    },
    "ext130": {
        "style": "openai", "base_url": "https://api.ext130.ai/v1",
        "key_env": "EXT130_API_KEY",
        "models": ["ext130/model-a", "ext130/model-b"],
        "description": "Extended provider 130 (auto-generated, disabled by default)",
        "enabled": False,
    },
    "ext131": {
        "style": "openai", "base_url": "https://api.ext131.ai/v1",
        "key_env": "EXT131_API_KEY",
        "models": ["ext131/model-a", "ext131/model-b"],
        "description": "Extended provider 131 (auto-generated, disabled by default)",
        "enabled": False,
    },
    "ext132": {
        "style": "openai", "base_url": "https://api.ext132.ai/v1",
        "key_env": "EXT132_API_KEY",
        "models": ["ext132/model-a", "ext132/model-b"],
        "description": "Extended provider 132 (auto-generated, disabled by default)",
        "enabled": False,
    },
    "ext133": {
        "style": "openai", "base_url": "https://api.ext133.ai/v1",
        "key_env": "EXT133_API_KEY",
        "models": ["ext133/model-a", "ext133/model-b"],
        "description": "Extended provider 133 (auto-generated, disabled by default)",
        "enabled": False,
    },
    "ext134": {
        "style": "openai", "base_url": "https://api.ext134.ai/v1",
        "key_env": "EXT134_API_KEY",
        "models": ["ext134/model-a", "ext134/model-b"],
        "description": "Extended provider 134 (auto-generated, disabled by default)",
        "enabled": False,
    },
    "ext135": {
        "style": "openai", "base_url": "https://api.ext135.ai/v1",
        "key_env": "EXT135_API_KEY",
        "models": ["ext135/model-a", "ext135/model-b"],
        "description": "Extended provider 135 (auto-generated, disabled by default)",
        "enabled": False,
    },
    "ext136": {
        "style": "openai", "base_url": "https://api.ext136.ai/v1",
        "key_env": "EXT136_API_KEY",
        "models": ["ext136/model-a", "ext136/model-b"],
        "description": "Extended provider 136 (auto-generated, disabled by default)",
        "enabled": False,
    },
    "ext137": {
        "style": "openai", "base_url": "https://api.ext137.ai/v1",
        "key_env": "EXT137_API_KEY",
        "models": ["ext137/model-a", "ext137/model-b"],
        "description": "Extended provider 137 (auto-generated, disabled by default)",
        "enabled": False,
    },
    "ext138": {
        "style": "openai", "base_url": "https://api.ext138.ai/v1",
        "key_env": "EXT138_API_KEY",
        "models": ["ext138/model-a", "ext138/model-b"],
        "description": "Extended provider 138 (auto-generated, disabled by default)",
        "enabled": False,
    },
    "ext139": {
        "style": "openai", "base_url": "https://api.ext139.ai/v1",
        "key_env": "EXT139_API_KEY",
        "models": ["ext139/model-a", "ext139/model-b"],
        "description": "Extended provider 139 (auto-generated, disabled by default)",
        "enabled": False,
    },
    "ext140": {
        "style": "openai", "base_url": "https://api.ext140.ai/v1",
        "key_env": "EXT140_API_KEY",
        "models": ["ext140/model-a", "ext140/model-b"],
        "description": "Extended provider 140 (auto-generated, disabled by default)",
        "enabled": False,
    },
    "ext141": {
        "style": "openai", "base_url": "https://api.ext141.ai/v1",
        "key_env": "EXT141_API_KEY",
        "models": ["ext141/model-a", "ext141/model-b"],
        "description": "Extended provider 141 (auto-generated, disabled by default)",
        "enabled": False,
    },
    "ext142": {
        "style": "openai", "base_url": "https://api.ext142.ai/v1",
        "key_env": "EXT142_API_KEY",
        "models": ["ext142/model-a", "ext142/model-b"],
        "description": "Extended provider 142 (auto-generated, disabled by default)",
        "enabled": False,
    },
    "ext143": {
        "style": "openai", "base_url": "https://api.ext143.ai/v1",
        "key_env": "EXT143_API_KEY",
        "models": ["ext143/model-a", "ext143/model-b"],
        "description": "Extended provider 143 (auto-generated, disabled by default)",
        "enabled": False,
    },
    "ext144": {
        "style": "openai", "base_url": "https://api.ext144.ai/v1",
        "key_env": "EXT144_API_KEY",
        "models": ["ext144/model-a", "ext144/model-b"],
        "description": "Extended provider 144 (auto-generated, disabled by default)",
        "enabled": False,
    },
    "ext145": {
        "style": "openai", "base_url": "https://api.ext145.ai/v1",
        "key_env": "EXT145_API_KEY",
        "models": ["ext145/model-a", "ext145/model-b"],
        "description": "Extended provider 145 (auto-generated, disabled by default)",
        "enabled": False,
    },
    "ext146": {
        "style": "openai", "base_url": "https://api.ext146.ai/v1",
        "key_env": "EXT146_API_KEY",
        "models": ["ext146/model-a", "ext146/model-b"],
        "description": "Extended provider 146 (auto-generated, disabled by default)",
        "enabled": False,
    },
    "ext147": {
        "style": "openai", "base_url": "https://api.ext147.ai/v1",
        "key_env": "EXT147_API_KEY",
        "models": ["ext147/model-a", "ext147/model-b"],
        "description": "Extended provider 147 (auto-generated, disabled by default)",
        "enabled": False,
    },
    "ext148": {
        "style": "openai", "base_url": "https://api.ext148.ai/v1",
        "key_env": "EXT148_API_KEY",
        "models": ["ext148/model-a", "ext148/model-b"],
        "description": "Extended provider 148 (auto-generated, disabled by default)",
        "enabled": False,
    },
    "ext149": {
        "style": "openai", "base_url": "https://api.ext149.ai/v1",
        "key_env": "EXT149_API_KEY",
        "models": ["ext149/model-a", "ext149/model-b"],
        "description": "Extended provider 149 (auto-generated, disabled by default)",
        "enabled": False,
    },
    "ext150": {
        "style": "openai", "base_url": "https://api.ext150.ai/v1",
        "key_env": "EXT150_API_KEY",
        "models": ["ext150/model-a", "ext150/model-b"],
        "description": "Extended provider 150 (auto-generated, disabled by default)",
        "enabled": False,
    },
    "ext151": {
        "style": "openai", "base_url": "https://api.ext151.ai/v1",
        "key_env": "EXT151_API_KEY",
        "models": ["ext151/model-a", "ext151/model-b"],
        "description": "Extended provider 151 (auto-generated, disabled by default)",
        "enabled": False,
    },
    "ext152": {
        "style": "openai", "base_url": "https://api.ext152.ai/v1",
        "key_env": "EXT152_API_KEY",
        "models": ["ext152/model-a", "ext152/model-b"],
        "description": "Extended provider 152 (auto-generated, disabled by default)",
        "enabled": False,
    },
    "ext153": {
        "style": "openai", "base_url": "https://api.ext153.ai/v1",
        "key_env": "EXT153_API_KEY",
        "models": ["ext153/model-a", "ext153/model-b"],
        "description": "Extended provider 153 (auto-generated, disabled by default)",
        "enabled": False,
    },
    "ext154": {
        "style": "openai", "base_url": "https://api.ext154.ai/v1",
        "key_env": "EXT154_API_KEY",
        "models": ["ext154/model-a", "ext154/model-b"],
        "description": "Extended provider 154 (auto-generated, disabled by default)",
        "enabled": False,
    },
    "ext155": {
        "style": "openai", "base_url": "https://api.ext155.ai/v1",
        "key_env": "EXT155_API_KEY",
        "models": ["ext155/model-a", "ext155/model-b"],
        "description": "Extended provider 155 (auto-generated, disabled by default)",
        "enabled": False,
    },
    "ext156": {
        "style": "openai", "base_url": "https://api.ext156.ai/v1",
        "key_env": "EXT156_API_KEY",
        "models": ["ext156/model-a", "ext156/model-b"],
        "description": "Extended provider 156 (auto-generated, disabled by default)",
        "enabled": False,
    },
    "ext157": {
        "style": "openai", "base_url": "https://api.ext157.ai/v1",
        "key_env": "EXT157_API_KEY",
        "models": ["ext157/model-a", "ext157/model-b"],
        "description": "Extended provider 157 (auto-generated, disabled by default)",
        "enabled": False,
    },
    "ext158": {
        "style": "openai", "base_url": "https://api.ext158.ai/v1",
        "key_env": "EXT158_API_KEY",
        "models": ["ext158/model-a", "ext158/model-b"],
        "description": "Extended provider 158 (auto-generated, disabled by default)",
        "enabled": False,
    },
    "ext159": {
        "style": "openai", "base_url": "https://api.ext159.ai/v1",
        "key_env": "EXT159_API_KEY",
        "models": ["ext159/model-a", "ext159/model-b"],
        "description": "Extended provider 159 (auto-generated, disabled by default)",
        "enabled": False,
    },
    "ext160": {
        "style": "openai", "base_url": "https://api.ext160.ai/v1",
        "key_env": "EXT160_API_KEY",
        "models": ["ext160/model-a", "ext160/model-b"],
        "description": "Extended provider 160 (auto-generated, disabled by default)",
        "enabled": False,
    },
    "ext161": {
        "style": "openai", "base_url": "https://api.ext161.ai/v1",
        "key_env": "EXT161_API_KEY",
        "models": ["ext161/model-a", "ext161/model-b"],
        "description": "Extended provider 161 (auto-generated, disabled by default)",
        "enabled": False,
    },
    "ext162": {
        "style": "openai", "base_url": "https://api.ext162.ai/v1",
        "key_env": "EXT162_API_KEY",
        "models": ["ext162/model-a", "ext162/model-b"],
        "description": "Extended provider 162 (auto-generated, disabled by default)",
        "enabled": False,
    },
    "ext163": {
        "style": "openai", "base_url": "https://api.ext163.ai/v1",
        "key_env": "EXT163_API_KEY",
        "models": ["ext163/model-a", "ext163/model-b"],
        "description": "Extended provider 163 (auto-generated, disabled by default)",
        "enabled": False,
    },
    "ext164": {
        "style": "openai", "base_url": "https://api.ext164.ai/v1",
        "key_env": "EXT164_API_KEY",
        "models": ["ext164/model-a", "ext164/model-b"],
        "description": "Extended provider 164 (auto-generated, disabled by default)",
        "enabled": False,
    },
    "ext165": {
        "style": "openai", "base_url": "https://api.ext165.ai/v1",
        "key_env": "EXT165_API_KEY",
        "models": ["ext165/model-a", "ext165/model-b"],
        "description": "Extended provider 165 (auto-generated, disabled by default)",
        "enabled": False,
    },
    "ext166": {
        "style": "openai", "base_url": "https://api.ext166.ai/v1",
        "key_env": "EXT166_API_KEY",
        "models": ["ext166/model-a", "ext166/model-b"],
        "description": "Extended provider 166 (auto-generated, disabled by default)",
        "enabled": False,
    },
    "ext167": {
        "style": "openai", "base_url": "https://api.ext167.ai/v1",
        "key_env": "EXT167_API_KEY",
        "models": ["ext167/model-a", "ext167/model-b"],
        "description": "Extended provider 167 (auto-generated, disabled by default)",
        "enabled": False,
    },
    "ext168": {
        "style": "openai", "base_url": "https://api.ext168.ai/v1",
        "key_env": "EXT168_API_KEY",
        "models": ["ext168/model-a", "ext168/model-b"],
        "description": "Extended provider 168 (auto-generated, disabled by default)",
        "enabled": False,
    },
    "ext169": {
        "style": "openai", "base_url": "https://api.ext169.ai/v1",
        "key_env": "EXT169_API_KEY",
        "models": ["ext169/model-a", "ext169/model-b"],
        "description": "Extended provider 169 (auto-generated, disabled by default)",
        "enabled": False,
    },
    "ext170": {
        "style": "openai", "base_url": "https://api.ext170.ai/v1",
        "key_env": "EXT170_API_KEY",
        "models": ["ext170/model-a", "ext170/model-b"],
        "description": "Extended provider 170 (auto-generated, disabled by default)",
        "enabled": False,
    },
    "ext171": {
        "style": "openai", "base_url": "https://api.ext171.ai/v1",
        "key_env": "EXT171_API_KEY",
        "models": ["ext171/model-a", "ext171/model-b"],
        "description": "Extended provider 171 (auto-generated, disabled by default)",
        "enabled": False,
    },
    "ext172": {
        "style": "openai", "base_url": "https://api.ext172.ai/v1",
        "key_env": "EXT172_API_KEY",
        "models": ["ext172/model-a", "ext172/model-b"],
        "description": "Extended provider 172 (auto-generated, disabled by default)",
        "enabled": False,
    },
    "ext173": {
        "style": "openai", "base_url": "https://api.ext173.ai/v1",
        "key_env": "EXT173_API_KEY",
        "models": ["ext173/model-a", "ext173/model-b"],
        "description": "Extended provider 173 (auto-generated, disabled by default)",
        "enabled": False,
    },
    "ext174": {
        "style": "openai", "base_url": "https://api.ext174.ai/v1",
        "key_env": "EXT174_API_KEY",
        "models": ["ext174/model-a", "ext174/model-b"],
        "description": "Extended provider 174 (auto-generated, disabled by default)",
        "enabled": False,
    },
    "ext175": {
        "style": "openai", "base_url": "https://api.ext175.ai/v1",
        "key_env": "EXT175_API_KEY",
        "models": ["ext175/model-a", "ext175/model-b"],
        "description": "Extended provider 175 (auto-generated, disabled by default)",
        "enabled": False,
    },
    "ext176": {
        "style": "openai", "base_url": "https://api.ext176.ai/v1",
        "key_env": "EXT176_API_KEY",
        "models": ["ext176/model-a", "ext176/model-b"],
        "description": "Extended provider 176 (auto-generated, disabled by default)",
        "enabled": False,
    },
    "ext177": {
        "style": "openai", "base_url": "https://api.ext177.ai/v1",
        "key_env": "EXT177_API_KEY",
        "models": ["ext177/model-a", "ext177/model-b"],
        "description": "Extended provider 177 (auto-generated, disabled by default)",
        "enabled": False,
    },
    "ext178": {
        "style": "openai", "base_url": "https://api.ext178.ai/v1",
        "key_env": "EXT178_API_KEY",
        "models": ["ext178/model-a", "ext178/model-b"],
        "description": "Extended provider 178 (auto-generated, disabled by default)",
        "enabled": False,
    },
    "ext179": {
        "style": "openai", "base_url": "https://api.ext179.ai/v1",
        "key_env": "EXT179_API_KEY",
        "models": ["ext179/model-a", "ext179/model-b"],
        "description": "Extended provider 179 (auto-generated, disabled by default)",
        "enabled": False,
    },
    "ext180": {
        "style": "openai", "base_url": "https://api.ext180.ai/v1",
        "key_env": "EXT180_API_KEY",
        "models": ["ext180/model-a", "ext180/model-b"],
        "description": "Extended provider 180 (auto-generated, disabled by default)",
        "enabled": False,
    },
    "ext181": {
        "style": "openai", "base_url": "https://api.ext181.ai/v1",
        "key_env": "EXT181_API_KEY",
        "models": ["ext181/model-a", "ext181/model-b"],
        "description": "Extended provider 181 (auto-generated, disabled by default)",
        "enabled": False,
    },
    "ext182": {
        "style": "openai", "base_url": "https://api.ext182.ai/v1",
        "key_env": "EXT182_API_KEY",
        "models": ["ext182/model-a", "ext182/model-b"],
        "description": "Extended provider 182 (auto-generated, disabled by default)",
        "enabled": False,
    },
    "ext183": {
        "style": "openai", "base_url": "https://api.ext183.ai/v1",
        "key_env": "EXT183_API_KEY",
        "models": ["ext183/model-a", "ext183/model-b"],
        "description": "Extended provider 183 (auto-generated, disabled by default)",
        "enabled": False,
    },
    "ext184": {
        "style": "openai", "base_url": "https://api.ext184.ai/v1",
        "key_env": "EXT184_API_KEY",
        "models": ["ext184/model-a", "ext184/model-b"],
        "description": "Extended provider 184 (auto-generated, disabled by default)",
        "enabled": False,
    },
    "ext185": {
        "style": "openai", "base_url": "https://api.ext185.ai/v1",
        "key_env": "EXT185_API_KEY",
        "models": ["ext185/model-a", "ext185/model-b"],
        "description": "Extended provider 185 (auto-generated, disabled by default)",
        "enabled": False,
    },
    "ext186": {
        "style": "openai", "base_url": "https://api.ext186.ai/v1",
        "key_env": "EXT186_API_KEY",
        "models": ["ext186/model-a", "ext186/model-b"],
        "description": "Extended provider 186 (auto-generated, disabled by default)",
        "enabled": False,
    },
    "ext187": {
        "style": "openai", "base_url": "https://api.ext187.ai/v1",
        "key_env": "EXT187_API_KEY",
        "models": ["ext187/model-a", "ext187/model-b"],
        "description": "Extended provider 187 (auto-generated, disabled by default)",
        "enabled": False,
    },
    "ext188": {
        "style": "openai", "base_url": "https://api.ext188.ai/v1",
        "key_env": "EXT188_API_KEY",
        "models": ["ext188/model-a", "ext188/model-b"],
        "description": "Extended provider 188 (auto-generated, disabled by default)",
        "enabled": False,
    },
    "ext189": {
        "style": "openai", "base_url": "https://api.ext189.ai/v1",
        "key_env": "EXT189_API_KEY",
        "models": ["ext189/model-a", "ext189/model-b"],
        "description": "Extended provider 189 (auto-generated, disabled by default)",
        "enabled": False,
    },
    "ext190": {
        "style": "openai", "base_url": "https://api.ext190.ai/v1",
        "key_env": "EXT190_API_KEY",
        "models": ["ext190/model-a", "ext190/model-b"],
        "description": "Extended provider 190 (auto-generated, disabled by default)",
        "enabled": False,
    },
    "ext191": {
        "style": "openai", "base_url": "https://api.ext191.ai/v1",
        "key_env": "EXT191_API_KEY",
        "models": ["ext191/model-a", "ext191/model-b"],
        "description": "Extended provider 191 (auto-generated, disabled by default)",
        "enabled": False,
    },
    "ext192": {
        "style": "openai", "base_url": "https://api.ext192.ai/v1",
        "key_env": "EXT192_API_KEY",
        "models": ["ext192/model-a", "ext192/model-b"],
        "description": "Extended provider 192 (auto-generated, disabled by default)",
        "enabled": False,
    },
    "ext193": {
        "style": "openai", "base_url": "https://api.ext193.ai/v1",
        "key_env": "EXT193_API_KEY",
        "models": ["ext193/model-a", "ext193/model-b"],
        "description": "Extended provider 193 (auto-generated, disabled by default)",
        "enabled": False,
    },
    "ext194": {
        "style": "openai", "base_url": "https://api.ext194.ai/v1",
        "key_env": "EXT194_API_KEY",
        "models": ["ext194/model-a", "ext194/model-b"],
        "description": "Extended provider 194 (auto-generated, disabled by default)",
        "enabled": False,
    },
    "ext195": {
        "style": "openai", "base_url": "https://api.ext195.ai/v1",
        "key_env": "EXT195_API_KEY",
        "models": ["ext195/model-a", "ext195/model-b"],
        "description": "Extended provider 195 (auto-generated, disabled by default)",
        "enabled": False,
    },
    "ext196": {
        "style": "openai", "base_url": "https://api.ext196.ai/v1",
        "key_env": "EXT196_API_KEY",
        "models": ["ext196/model-a", "ext196/model-b"],
        "description": "Extended provider 196 (auto-generated, disabled by default)",
        "enabled": False,
    },
    "ext197": {
        "style": "openai", "base_url": "https://api.ext197.ai/v1",
        "key_env": "EXT197_API_KEY",
        "models": ["ext197/model-a", "ext197/model-b"],
        "description": "Extended provider 197 (auto-generated, disabled by default)",
        "enabled": False,
    },
    "ext198": {
        "style": "openai", "base_url": "https://api.ext198.ai/v1",
        "key_env": "EXT198_API_KEY",
        "models": ["ext198/model-a", "ext198/model-b"],
        "description": "Extended provider 198 (auto-generated, disabled by default)",
        "enabled": False,
    },
    "ext199": {
        "style": "openai", "base_url": "https://api.ext199.ai/v1",
        "key_env": "EXT199_API_KEY",
        "models": ["ext199/model-a", "ext199/model-b"],
        "description": "Extended provider 199 (auto-generated, disabled by default)",
        "enabled": False,
    },
    "ext200": {
        "style": "openai", "base_url": "https://api.ext200.ai/v1",
        "key_env": "EXT200_API_KEY",
        "models": ["ext200/model-a", "ext200/model-b"],
        "description": "Extended provider 200 (auto-generated, disabled by default)",
        "enabled": False,
    },
    "ext201": {
        "style": "openai", "base_url": "https://api.ext201.ai/v1",
        "key_env": "EXT201_API_KEY",
        "models": ["ext201/model-a", "ext201/model-b"],
        "description": "Extended provider 201 (auto-generated, disabled by default)",
        "enabled": False,
    },
    "ext202": {
        "style": "openai", "base_url": "https://api.ext202.ai/v1",
        "key_env": "EXT202_API_KEY",
        "models": ["ext202/model-a", "ext202/model-b"],
        "description": "Extended provider 202 (auto-generated, disabled by default)",
        "enabled": False,
    },
    "ext203": {
        "style": "openai", "base_url": "https://api.ext203.ai/v1",
        "key_env": "EXT203_API_KEY",
        "models": ["ext203/model-a", "ext203/model-b"],
        "description": "Extended provider 203 (auto-generated, disabled by default)",
        "enabled": False,
    },
    "ext204": {
        "style": "openai", "base_url": "https://api.ext204.ai/v1",
        "key_env": "EXT204_API_KEY",
        "models": ["ext204/model-a", "ext204/model-b"],
        "description": "Extended provider 204 (auto-generated, disabled by default)",
        "enabled": False,
    },
    "ext205": {
        "style": "openai", "base_url": "https://api.ext205.ai/v1",
        "key_env": "EXT205_API_KEY",
        "models": ["ext205/model-a", "ext205/model-b"],
        "description": "Extended provider 205 (auto-generated, disabled by default)",
        "enabled": False,
    },
    "ext206": {
        "style": "openai", "base_url": "https://api.ext206.ai/v1",
        "key_env": "EXT206_API_KEY",
        "models": ["ext206/model-a", "ext206/model-b"],
        "description": "Extended provider 206 (auto-generated, disabled by default)",
        "enabled": False,
    },
    "ext207": {
        "style": "openai", "base_url": "https://api.ext207.ai/v1",
        "key_env": "EXT207_API_KEY",
        "models": ["ext207/model-a", "ext207/model-b"],
        "description": "Extended provider 207 (auto-generated, disabled by default)",
        "enabled": False,
    },
    "ext208": {
        "style": "openai", "base_url": "https://api.ext208.ai/v1",
        "key_env": "EXT208_API_KEY",
        "models": ["ext208/model-a", "ext208/model-b"],
        "description": "Extended provider 208 (auto-generated, disabled by default)",
        "enabled": False,
    },
    "ext209": {
        "style": "openai", "base_url": "https://api.ext209.ai/v1",
        "key_env": "EXT209_API_KEY",
        "models": ["ext209/model-a", "ext209/model-b"],
        "description": "Extended provider 209 (auto-generated, disabled by default)",
        "enabled": False,
    },
    "ext210": {
        "style": "openai", "base_url": "https://api.ext210.ai/v1",
        "key_env": "EXT210_API_KEY",
        "models": ["ext210/model-a", "ext210/model-b"],
        "description": "Extended provider 210 (auto-generated, disabled by default)",
        "enabled": False,
    },
    "ext211": {
        "style": "openai", "base_url": "https://api.ext211.ai/v1",
        "key_env": "EXT211_API_KEY",
        "models": ["ext211/model-a", "ext211/model-b"],
        "description": "Extended provider 211 (auto-generated, disabled by default)",
        "enabled": False,
    },
    "ext212": {
        "style": "openai", "base_url": "https://api.ext212.ai/v1",
        "key_env": "EXT212_API_KEY",
        "models": ["ext212/model-a", "ext212/model-b"],
        "description": "Extended provider 212 (auto-generated, disabled by default)",
        "enabled": False,
    },
    "ext213": {
        "style": "openai", "base_url": "https://api.ext213.ai/v1",
        "key_env": "EXT213_API_KEY",
        "models": ["ext213/model-a", "ext213/model-b"],
        "description": "Extended provider 213 (auto-generated, disabled by default)",
        "enabled": False,
    },
    "ext214": {
        "style": "openai", "base_url": "https://api.ext214.ai/v1",
        "key_env": "EXT214_API_KEY",
        "models": ["ext214/model-a", "ext214/model-b"],
        "description": "Extended provider 214 (auto-generated, disabled by default)",
        "enabled": False,
    },
    "ext215": {
        "style": "openai", "base_url": "https://api.ext215.ai/v1",
        "key_env": "EXT215_API_KEY",
        "models": ["ext215/model-a", "ext215/model-b"],
        "description": "Extended provider 215 (auto-generated, disabled by default)",
        "enabled": False,
    },
    "ext216": {
        "style": "openai", "base_url": "https://api.ext216.ai/v1",
        "key_env": "EXT216_API_KEY",
        "models": ["ext216/model-a", "ext216/model-b"],
        "description": "Extended provider 216 (auto-generated, disabled by default)",
        "enabled": False,
    },
    "ext217": {
        "style": "openai", "base_url": "https://api.ext217.ai/v1",
        "key_env": "EXT217_API_KEY",
        "models": ["ext217/model-a", "ext217/model-b"],
        "description": "Extended provider 217 (auto-generated, disabled by default)",
        "enabled": False,
    },
    "ext218": {
        "style": "openai", "base_url": "https://api.ext218.ai/v1",
        "key_env": "EXT218_API_KEY",
        "models": ["ext218/model-a", "ext218/model-b"],
        "description": "Extended provider 218 (auto-generated, disabled by default)",
        "enabled": False,
    },
    "ext219": {
        "style": "openai", "base_url": "https://api.ext219.ai/v1",
        "key_env": "EXT219_API_KEY",
        "models": ["ext219/model-a", "ext219/model-b"],
        "description": "Extended provider 219 (auto-generated, disabled by default)",
        "enabled": False,
    },
    "ext220": {
        "style": "openai", "base_url": "https://api.ext220.ai/v1",
        "key_env": "EXT220_API_KEY",
        "models": ["ext220/model-a", "ext220/model-b"],
        "description": "Extended provider 220 (auto-generated, disabled by default)",
        "enabled": False,
    },
    "ext221": {
        "style": "openai", "base_url": "https://api.ext221.ai/v1",
        "key_env": "EXT221_API_KEY",
        "models": ["ext221/model-a", "ext221/model-b"],
        "description": "Extended provider 221 (auto-generated, disabled by default)",
        "enabled": False,
    },
    "ext222": {
        "style": "openai", "base_url": "https://api.ext222.ai/v1",
        "key_env": "EXT222_API_KEY",
        "models": ["ext222/model-a", "ext222/model-b"],
        "description": "Extended provider 222 (auto-generated, disabled by default)",
        "enabled": False,
    },
    "ext223": {
        "style": "openai", "base_url": "https://api.ext223.ai/v1",
        "key_env": "EXT223_API_KEY",
        "models": ["ext223/model-a", "ext223/model-b"],
        "description": "Extended provider 223 (auto-generated, disabled by default)",
        "enabled": False,
    },
    "ext224": {
        "style": "openai", "base_url": "https://api.ext224.ai/v1",
        "key_env": "EXT224_API_KEY",
        "models": ["ext224/model-a", "ext224/model-b"],
        "description": "Extended provider 224 (auto-generated, disabled by default)",
        "enabled": False,
    },
    "ext225": {
        "style": "openai", "base_url": "https://api.ext225.ai/v1",
        "key_env": "EXT225_API_KEY",
        "models": ["ext225/model-a", "ext225/model-b"],
        "description": "Extended provider 225 (auto-generated, disabled by default)",
        "enabled": False,
    },
    "ext226": {
        "style": "openai", "base_url": "https://api.ext226.ai/v1",
        "key_env": "EXT226_API_KEY",
        "models": ["ext226/model-a", "ext226/model-b"],
        "description": "Extended provider 226 (auto-generated, disabled by default)",
        "enabled": False,
    },
    "ext227": {
        "style": "openai", "base_url": "https://api.ext227.ai/v1",
        "key_env": "EXT227_API_KEY",
        "models": ["ext227/model-a", "ext227/model-b"],
        "description": "Extended provider 227 (auto-generated, disabled by default)",
        "enabled": False,
    },
    "ext228": {
        "style": "openai", "base_url": "https://api.ext228.ai/v1",
        "key_env": "EXT228_API_KEY",
        "models": ["ext228/model-a", "ext228/model-b"],
        "description": "Extended provider 228 (auto-generated, disabled by default)",
        "enabled": False,
    },
    "ext229": {
        "style": "openai", "base_url": "https://api.ext229.ai/v1",
        "key_env": "EXT229_API_KEY",
        "models": ["ext229/model-a", "ext229/model-b"],
        "description": "Extended provider 229 (auto-generated, disabled by default)",
        "enabled": False,
    },
    "ext230": {
        "style": "openai", "base_url": "https://api.ext230.ai/v1",
        "key_env": "EXT230_API_KEY",
        "models": ["ext230/model-a", "ext230/model-b"],
        "description": "Extended provider 230 (auto-generated, disabled by default)",
        "enabled": False,
    },
    "ext231": {
        "style": "openai", "base_url": "https://api.ext231.ai/v1",
        "key_env": "EXT231_API_KEY",
        "models": ["ext231/model-a", "ext231/model-b"],
        "description": "Extended provider 231 (auto-generated, disabled by default)",
        "enabled": False,
    },
    "ext232": {
        "style": "openai", "base_url": "https://api.ext232.ai/v1",
        "key_env": "EXT232_API_KEY",
        "models": ["ext232/model-a", "ext232/model-b"],
        "description": "Extended provider 232 (auto-generated, disabled by default)",
        "enabled": False,
    },
    "ext233": {
        "style": "openai", "base_url": "https://api.ext233.ai/v1",
        "key_env": "EXT233_API_KEY",
        "models": ["ext233/model-a", "ext233/model-b"],
        "description": "Extended provider 233 (auto-generated, disabled by default)",
        "enabled": False,
    },
    "ext234": {
        "style": "openai", "base_url": "https://api.ext234.ai/v1",
        "key_env": "EXT234_API_KEY",
        "models": ["ext234/model-a", "ext234/model-b"],
        "description": "Extended provider 234 (auto-generated, disabled by default)",
        "enabled": False,
    },
    "ext235": {
        "style": "openai", "base_url": "https://api.ext235.ai/v1",
        "key_env": "EXT235_API_KEY",
        "models": ["ext235/model-a", "ext235/model-b"],
        "description": "Extended provider 235 (auto-generated, disabled by default)",
        "enabled": False,
    },
    "ext236": {
        "style": "openai", "base_url": "https://api.ext236.ai/v1",
        "key_env": "EXT236_API_KEY",
        "models": ["ext236/model-a", "ext236/model-b"],
        "description": "Extended provider 236 (auto-generated, disabled by default)",
        "enabled": False,
    },
    "ext237": {
        "style": "openai", "base_url": "https://api.ext237.ai/v1",
        "key_env": "EXT237_API_KEY",
        "models": ["ext237/model-a", "ext237/model-b"],
        "description": "Extended provider 237 (auto-generated, disabled by default)",
        "enabled": False,
    },
    "ext238": {
        "style": "openai", "base_url": "https://api.ext238.ai/v1",
        "key_env": "EXT238_API_KEY",
        "models": ["ext238/model-a", "ext238/model-b"],
        "description": "Extended provider 238 (auto-generated, disabled by default)",
        "enabled": False,
    },
    "ext239": {
        "style": "openai", "base_url": "https://api.ext239.ai/v1",
        "key_env": "EXT239_API_KEY",
        "models": ["ext239/model-a", "ext239/model-b"],
        "description": "Extended provider 239 (auto-generated, disabled by default)",
        "enabled": False,
    },
    "ext240": {
        "style": "openai", "base_url": "https://api.ext240.ai/v1",
        "key_env": "EXT240_API_KEY",
        "models": ["ext240/model-a", "ext240/model-b"],
        "description": "Extended provider 240 (auto-generated, disabled by default)",
        "enabled": False,
    },
    "ext241": {
        "style": "openai", "base_url": "https://api.ext241.ai/v1",
        "key_env": "EXT241_API_KEY",
        "models": ["ext241/model-a", "ext241/model-b"],
        "description": "Extended provider 241 (auto-generated, disabled by default)",
        "enabled": False,
    },
    "ext242": {
        "style": "openai", "base_url": "https://api.ext242.ai/v1",
        "key_env": "EXT242_API_KEY",
        "models": ["ext242/model-a", "ext242/model-b"],
        "description": "Extended provider 242 (auto-generated, disabled by default)",
        "enabled": False,
    },
    "ext243": {
        "style": "openai", "base_url": "https://api.ext243.ai/v1",
        "key_env": "EXT243_API_KEY",
        "models": ["ext243/model-a", "ext243/model-b"],
        "description": "Extended provider 243 (auto-generated, disabled by default)",
        "enabled": False,
    },
    "ext244": {
        "style": "openai", "base_url": "https://api.ext244.ai/v1",
        "key_env": "EXT244_API_KEY",
        "models": ["ext244/model-a", "ext244/model-b"],
        "description": "Extended provider 244 (auto-generated, disabled by default)",
        "enabled": False,
    },
    "ext245": {
        "style": "openai", "base_url": "https://api.ext245.ai/v1",
        "key_env": "EXT245_API_KEY",
        "models": ["ext245/model-a", "ext245/model-b"],
        "description": "Extended provider 245 (auto-generated, disabled by default)",
        "enabled": False,
    },
    "ext246": {
        "style": "openai", "base_url": "https://api.ext246.ai/v1",
        "key_env": "EXT246_API_KEY",
        "models": ["ext246/model-a", "ext246/model-b"],
        "description": "Extended provider 246 (auto-generated, disabled by default)",
        "enabled": False,
    },
    "ext247": {
        "style": "openai", "base_url": "https://api.ext247.ai/v1",
        "key_env": "EXT247_API_KEY",
        "models": ["ext247/model-a", "ext247/model-b"],
        "description": "Extended provider 247 (auto-generated, disabled by default)",
        "enabled": False,
    },
    "ext248": {
        "style": "openai", "base_url": "https://api.ext248.ai/v1",
        "key_env": "EXT248_API_KEY",
        "models": ["ext248/model-a", "ext248/model-b"],
        "description": "Extended provider 248 (auto-generated, disabled by default)",
        "enabled": False,
    },
    "ext249": {
        "style": "openai", "base_url": "https://api.ext249.ai/v1",
        "key_env": "EXT249_API_KEY",
        "models": ["ext249/model-a", "ext249/model-b"],
        "description": "Extended provider 249 (auto-generated, disabled by default)",
        "enabled": False,
    },
    "ext250": {
        "style": "openai", "base_url": "https://api.ext250.ai/v1",
        "key_env": "EXT250_API_KEY",
        "models": ["ext250/model-a", "ext250/model-b"],
        "description": "Extended provider 250 (auto-generated, disabled by default)",
        "enabled": False,
    },
    "ext251": {
        "style": "openai", "base_url": "https://api.ext251.ai/v1",
        "key_env": "EXT251_API_KEY",
        "models": ["ext251/model-a", "ext251/model-b"],
        "description": "Extended provider 251 (auto-generated, disabled by default)",
        "enabled": False,
    },
    "ext252": {
        "style": "openai", "base_url": "https://api.ext252.ai/v1",
        "key_env": "EXT252_API_KEY",
        "models": ["ext252/model-a", "ext252/model-b"],
        "description": "Extended provider 252 (auto-generated, disabled by default)",
        "enabled": False,
    },
    "ext253": {
        "style": "openai", "base_url": "https://api.ext253.ai/v1",
        "key_env": "EXT253_API_KEY",
        "models": ["ext253/model-a", "ext253/model-b"],
        "description": "Extended provider 253 (auto-generated, disabled by default)",
        "enabled": False,
    },
    "ext254": {
        "style": "openai", "base_url": "https://api.ext254.ai/v1",
        "key_env": "EXT254_API_KEY",
        "models": ["ext254/model-a", "ext254/model-b"],
        "description": "Extended provider 254 (auto-generated, disabled by default)",
        "enabled": False,
    },
    "ext255": {
        "style": "openai", "base_url": "https://api.ext255.ai/v1",
        "key_env": "EXT255_API_KEY",
        "models": ["ext255/model-a", "ext255/model-b"],
        "description": "Extended provider 255 (auto-generated, disabled by default)",
        "enabled": False,
    },
    "ext256": {
        "style": "openai", "base_url": "https://api.ext256.ai/v1",
        "key_env": "EXT256_API_KEY",
        "models": ["ext256/model-a", "ext256/model-b"],
        "description": "Extended provider 256 (auto-generated, disabled by default)",
        "enabled": False,
    },
    "ext257": {
        "style": "openai", "base_url": "https://api.ext257.ai/v1",
        "key_env": "EXT257_API_KEY",
        "models": ["ext257/model-a", "ext257/model-b"],
        "description": "Extended provider 257 (auto-generated, disabled by default)",
        "enabled": False,
    },
    "ext258": {
        "style": "openai", "base_url": "https://api.ext258.ai/v1",
        "key_env": "EXT258_API_KEY",
        "models": ["ext258/model-a", "ext258/model-b"],
        "description": "Extended provider 258 (auto-generated, disabled by default)",
        "enabled": False,
    },
    "ext259": {
        "style": "openai", "base_url": "https://api.ext259.ai/v1",
        "key_env": "EXT259_API_KEY",
        "models": ["ext259/model-a", "ext259/model-b"],
        "description": "Extended provider 259 (auto-generated, disabled by default)",
        "enabled": False,
    },
    "ext260": {
        "style": "openai", "base_url": "https://api.ext260.ai/v1",
        "key_env": "EXT260_API_KEY",
        "models": ["ext260/model-a", "ext260/model-b"],
        "description": "Extended provider 260 (auto-generated, disabled by default)",
        "enabled": False,
    },
    "ext261": {
        "style": "openai", "base_url": "https://api.ext261.ai/v1",
        "key_env": "EXT261_API_KEY",
        "models": ["ext261/model-a", "ext261/model-b"],
        "description": "Extended provider 261 (auto-generated, disabled by default)",
        "enabled": False,
    },
    "ext262": {
        "style": "openai", "base_url": "https://api.ext262.ai/v1",
        "key_env": "EXT262_API_KEY",
        "models": ["ext262/model-a", "ext262/model-b"],
        "description": "Extended provider 262 (auto-generated, disabled by default)",
        "enabled": False,
    },
    "ext263": {
        "style": "openai", "base_url": "https://api.ext263.ai/v1",
        "key_env": "EXT263_API_KEY",
        "models": ["ext263/model-a", "ext263/model-b"],
        "description": "Extended provider 263 (auto-generated, disabled by default)",
        "enabled": False,
    },
    "ext264": {
        "style": "openai", "base_url": "https://api.ext264.ai/v1",
        "key_env": "EXT264_API_KEY",
        "models": ["ext264/model-a", "ext264/model-b"],
        "description": "Extended provider 264 (auto-generated, disabled by default)",
        "enabled": False,
    },
    "ext265": {
        "style": "openai", "base_url": "https://api.ext265.ai/v1",
        "key_env": "EXT265_API_KEY",
        "models": ["ext265/model-a", "ext265/model-b"],
        "description": "Extended provider 265 (auto-generated, disabled by default)",
        "enabled": False,
    },
    "ext266": {
        "style": "openai", "base_url": "https://api.ext266.ai/v1",
        "key_env": "EXT266_API_KEY",
        "models": ["ext266/model-a", "ext266/model-b"],
        "description": "Extended provider 266 (auto-generated, disabled by default)",
        "enabled": False,
    },
    "ext267": {
        "style": "openai", "base_url": "https://api.ext267.ai/v1",
        "key_env": "EXT267_API_KEY",
        "models": ["ext267/model-a", "ext267/model-b"],
        "description": "Extended provider 267 (auto-generated, disabled by default)",
        "enabled": False,
    },
    "ext268": {
        "style": "openai", "base_url": "https://api.ext268.ai/v1",
        "key_env": "EXT268_API_KEY",
        "models": ["ext268/model-a", "ext268/model-b"],
        "description": "Extended provider 268 (auto-generated, disabled by default)",
        "enabled": False,
    },
    "ext269": {
        "style": "openai", "base_url": "https://api.ext269.ai/v1",
        "key_env": "EXT269_API_KEY",
        "models": ["ext269/model-a", "ext269/model-b"],
        "description": "Extended provider 269 (auto-generated, disabled by default)",
        "enabled": False,
    },
    "ext270": {
        "style": "openai", "base_url": "https://api.ext270.ai/v1",
        "key_env": "EXT270_API_KEY",
        "models": ["ext270/model-a", "ext270/model-b"],
        "description": "Extended provider 270 (auto-generated, disabled by default)",
        "enabled": False,
    },
    "ext271": {
        "style": "openai", "base_url": "https://api.ext271.ai/v1",
        "key_env": "EXT271_API_KEY",
        "models": ["ext271/model-a", "ext271/model-b"],
        "description": "Extended provider 271 (auto-generated, disabled by default)",
        "enabled": False,
    },
    "ext272": {
        "style": "openai", "base_url": "https://api.ext272.ai/v1",
        "key_env": "EXT272_API_KEY",
        "models": ["ext272/model-a", "ext272/model-b"],
        "description": "Extended provider 272 (auto-generated, disabled by default)",
        "enabled": False,
    },
    "ext273": {
        "style": "openai", "base_url": "https://api.ext273.ai/v1",
        "key_env": "EXT273_API_KEY",
        "models": ["ext273/model-a", "ext273/model-b"],
        "description": "Extended provider 273 (auto-generated, disabled by default)",
        "enabled": False,
    },
    "ext274": {
        "style": "openai", "base_url": "https://api.ext274.ai/v1",
        "key_env": "EXT274_API_KEY",
        "models": ["ext274/model-a", "ext274/model-b"],
        "description": "Extended provider 274 (auto-generated, disabled by default)",
        "enabled": False,
    },
    "ext275": {
        "style": "openai", "base_url": "https://api.ext275.ai/v1",
        "key_env": "EXT275_API_KEY",
        "models": ["ext275/model-a", "ext275/model-b"],
        "description": "Extended provider 275 (auto-generated, disabled by default)",
        "enabled": False,
    },
    "ext276": {
        "style": "openai", "base_url": "https://api.ext276.ai/v1",
        "key_env": "EXT276_API_KEY",
        "models": ["ext276/model-a", "ext276/model-b"],
        "description": "Extended provider 276 (auto-generated, disabled by default)",
        "enabled": False,
    },
    "ext277": {
        "style": "openai", "base_url": "https://api.ext277.ai/v1",
        "key_env": "EXT277_API_KEY",
        "models": ["ext277/model-a", "ext277/model-b"],
        "description": "Extended provider 277 (auto-generated, disabled by default)",
        "enabled": False,
    },
    "ext278": {
        "style": "openai", "base_url": "https://api.ext278.ai/v1",
        "key_env": "EXT278_API_KEY",
        "models": ["ext278/model-a", "ext278/model-b"],
        "description": "Extended provider 278 (auto-generated, disabled by default)",
        "enabled": False,
    },
    "ext279": {
        "style": "openai", "base_url": "https://api.ext279.ai/v1",
        "key_env": "EXT279_API_KEY",
        "models": ["ext279/model-a", "ext279/model-b"],
        "description": "Extended provider 279 (auto-generated, disabled by default)",
        "enabled": False,
    },
    "ext280": {
        "style": "openai", "base_url": "https://api.ext280.ai/v1",
        "key_env": "EXT280_API_KEY",
        "models": ["ext280/model-a", "ext280/model-b"],
        "description": "Extended provider 280 (auto-generated, disabled by default)",
        "enabled": False,
    },
    "ext281": {
        "style": "openai", "base_url": "https://api.ext281.ai/v1",
        "key_env": "EXT281_API_KEY",
        "models": ["ext281/model-a", "ext281/model-b"],
        "description": "Extended provider 281 (auto-generated, disabled by default)",
        "enabled": False,
    },
    "ext282": {
        "style": "openai", "base_url": "https://api.ext282.ai/v1",
        "key_env": "EXT282_API_KEY",
        "models": ["ext282/model-a", "ext282/model-b"],
        "description": "Extended provider 282 (auto-generated, disabled by default)",
        "enabled": False,
    },
    "ext283": {
        "style": "openai", "base_url": "https://api.ext283.ai/v1",
        "key_env": "EXT283_API_KEY",
        "models": ["ext283/model-a", "ext283/model-b"],
        "description": "Extended provider 283 (auto-generated, disabled by default)",
        "enabled": False,
    },
    "ext284": {
        "style": "openai", "base_url": "https://api.ext284.ai/v1",
        "key_env": "EXT284_API_KEY",
        "models": ["ext284/model-a", "ext284/model-b"],
        "description": "Extended provider 284 (auto-generated, disabled by default)",
        "enabled": False,
    },
    "ext285": {
        "style": "openai", "base_url": "https://api.ext285.ai/v1",
        "key_env": "EXT285_API_KEY",
        "models": ["ext285/model-a", "ext285/model-b"],
        "description": "Extended provider 285 (auto-generated, disabled by default)",
        "enabled": False,
    },
    "ext286": {
        "style": "openai", "base_url": "https://api.ext286.ai/v1",
        "key_env": "EXT286_API_KEY",
        "models": ["ext286/model-a", "ext286/model-b"],
        "description": "Extended provider 286 (auto-generated, disabled by default)",
        "enabled": False,
    },
    "ext287": {
        "style": "openai", "base_url": "https://api.ext287.ai/v1",
        "key_env": "EXT287_API_KEY",
        "models": ["ext287/model-a", "ext287/model-b"],
        "description": "Extended provider 287 (auto-generated, disabled by default)",
        "enabled": False,
    },
    "ext288": {
        "style": "openai", "base_url": "https://api.ext288.ai/v1",
        "key_env": "EXT288_API_KEY",
        "models": ["ext288/model-a", "ext288/model-b"],
        "description": "Extended provider 288 (auto-generated, disabled by default)",
        "enabled": False,
    },
    "ext289": {
        "style": "openai", "base_url": "https://api.ext289.ai/v1",
        "key_env": "EXT289_API_KEY",
        "models": ["ext289/model-a", "ext289/model-b"],
        "description": "Extended provider 289 (auto-generated, disabled by default)",
        "enabled": False,
    },
    "ext290": {
        "style": "openai", "base_url": "https://api.ext290.ai/v1",
        "key_env": "EXT290_API_KEY",
        "models": ["ext290/model-a", "ext290/model-b"],
        "description": "Extended provider 290 (auto-generated, disabled by default)",
        "enabled": False,
    },
    "ext291": {
        "style": "openai", "base_url": "https://api.ext291.ai/v1",
        "key_env": "EXT291_API_KEY",
        "models": ["ext291/model-a", "ext291/model-b"],
        "description": "Extended provider 291 (auto-generated, disabled by default)",
        "enabled": False,
    },
    "ext292": {
        "style": "openai", "base_url": "https://api.ext292.ai/v1",
        "key_env": "EXT292_API_KEY",
        "models": ["ext292/model-a", "ext292/model-b"],
        "description": "Extended provider 292 (auto-generated, disabled by default)",
        "enabled": False,
    },
    "ext293": {
        "style": "openai", "base_url": "https://api.ext293.ai/v1",
        "key_env": "EXT293_API_KEY",
        "models": ["ext293/model-a", "ext293/model-b"],
        "description": "Extended provider 293 (auto-generated, disabled by default)",
        "enabled": False,
    },
    "ext294": {
        "style": "openai", "base_url": "https://api.ext294.ai/v1",
        "key_env": "EXT294_API_KEY",
        "models": ["ext294/model-a", "ext294/model-b"],
        "description": "Extended provider 294 (auto-generated, disabled by default)",
        "enabled": False,
    },
    "ext295": {
        "style": "openai", "base_url": "https://api.ext295.ai/v1",
        "key_env": "EXT295_API_KEY",
        "models": ["ext295/model-a", "ext295/model-b"],
        "description": "Extended provider 295 (auto-generated, disabled by default)",
        "enabled": False,
    },
    "ext296": {
        "style": "openai", "base_url": "https://api.ext296.ai/v1",
        "key_env": "EXT296_API_KEY",
        "models": ["ext296/model-a", "ext296/model-b"],
        "description": "Extended provider 296 (auto-generated, disabled by default)",
        "enabled": False,
    },
    "ext297": {
        "style": "openai", "base_url": "https://api.ext297.ai/v1",
        "key_env": "EXT297_API_KEY",
        "models": ["ext297/model-a", "ext297/model-b"],
        "description": "Extended provider 297 (auto-generated, disabled by default)",
        "enabled": False,
    },
    "ext298": {
        "style": "openai", "base_url": "https://api.ext298.ai/v1",
        "key_env": "EXT298_API_KEY",
        "models": ["ext298/model-a", "ext298/model-b"],
        "description": "Extended provider 298 (auto-generated, disabled by default)",
        "enabled": False,
    },
    "ext299": {
        "style": "openai", "base_url": "https://api.ext299.ai/v1",
        "key_env": "EXT299_API_KEY",
        "models": ["ext299/model-a", "ext299/model-b"],
        "description": "Extended provider 299 (auto-generated, disabled by default)",
        "enabled": False,
    },
    "ext300": {
        "style": "openai", "base_url": "https://api.ext300.ai/v1",
        "key_env": "EXT300_API_KEY",
        "models": ["ext300/model-a", "ext300/model-b"],
        "description": "Extended provider 300 (auto-generated, disabled by default)",
        "enabled": False,
    },
    "zen": {
        "style": "openai", "base_url": "https://api.opencode.ai/zen/v1",
        "key_env": "ZEN_API_KEY",
        "models": ["zen-coder", "zen-think", "zen-4"],
        "description": "Opencode Zen (local + cloud)",
    },
    "mimocode": {
        "style": "openai", "base_url": "https://api.mimocode.com/v1",
        "key_env": "MIMOCODE_API_KEY",
        "models": ["mimocode-flash", "mimocode-pro", "mimocode-coder"],
        "description": "MiMoCode LLM providers (Xiaomi)",
        "enabled": True,
    },
    "jcode": {
        "style": "openai", "base_url": "https://api.jcode.ai/v1",
        "key_env": "JCODE_API_KEY",
        "models": ["jcode-v1", "jcode-coder"],
        "description": "JCode AI coding models",
        "enabled": True,
    },
    "zcode": {
        "style": "openai", "base_url": "https://api.zcode.ai/v1",
        "key_env": "ZCODE_API_KEY",
        "models": ["zcode-7b", "zcode-32b", "zcode-coder"],
        "description": "ZCode fast inference providers",
        "enabled": True,
    },
    "hermes": {
        "style": "openai", "base_url": "https://api.hermes-ai.dev/v1",
        "key_env": "HERMES_API_KEY",
        "models": ["hermes-2-pro", "hermes-3-flash", "hermes-coder"],
        "description": "Hermes AI platform (uncensored fine-tunes)",
        "enabled": True,
    },
    "opencode": {
        "style": "openai", "base_url": "https://api.opencode.ai/v1",
        "key_env": "OPENCODE_API_KEY",
        "models": ["opencode-coder", "opencode-think", "opencode-uncensored"],
        "description": "OpenCode AI — full uncensored coder stack",
        "enabled": True,
    },
    "openclaw": {
        "style": "openai", "base_url": "https://api.openclaw.ai/v1",
        "key_env": "OPENCLAW_API_KEY",
        "models": ["openclaw-v1", "openclaw-coder", "openclaw-reasoner"],
        "description": "OpenClaw AI — agent-native model providers",
        "enabled": True,
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
    # keyless local providers (ollama, lmstudio, freetoken) are always
    # considered keyed — they need no API key
    if not cfg.get("key_env"):
        return True
    key = cfg.get("api_key") or os.environ.get(cfg["key_env"])
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
    """Provider models appended to local chains.

    Includes explicit fallback=true providers plus any
    auto_fallback_when_healthy provider that currently passes a health
    probe (used for FreeToken local edge MoE).
    """
    ids = []
    for name, cfg in keyed_providers().items():
        if cfg.get("fallback"):
            for m in cfg["models"]:
                ids.append(f"{name}/{m}")
        elif cfg.get("auto_fallback_when_healthy") and is_provider_healthy(name, cfg):
            for m in cfg["models"]:
                ids.append(f"{name}/{m}")
    return ids


_HEALTH_CACHE = {}
_HEALTH_TTL = 30

def is_provider_healthy(name, cfg, timeout=2):
    """Lightweight health probe — tries /health then /v1/models.

    Results cached for _HEALTH_TTL seconds to avoid per-request stalls.
    """
    base = cfg.get("base_url", "").rstrip("/")
    if not base:
        return False
    now = time.time()
    cached = _HEALTH_CACHE.get(name)
    if cached and now - cached[0] < _HEALTH_TTL:
        return cached[1]
    healthy = False
    for suffix in ("/health", "/v1/models", "/models"):
        try:
            url = base + suffix if not base.endswith(suffix) else base
            if base.endswith("/v1") and suffix == "/v1/models":
                url = base + "/models"
            r = requests.get(url, timeout=timeout)
            if r.status_code < 500:
                healthy = True
                break
        except Exception:
            continue
    _HEALTH_CACHE[name] = (now, healthy)
    return healthy


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
            headers["HTTP-Referer"] = "https://freeai.local"
            headers["X-Title"] = "FreeAI Router"
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
