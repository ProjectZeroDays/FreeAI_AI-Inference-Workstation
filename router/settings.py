"""Centralized configuration loader.

Reads config/config.json from the repo root and applies environment
overrides. Works both when imported as a package and when the module
is executed flat (Docker containers).
"""
import json
import os

_ENV_OVERRIDES = {
    "ROUTER_PORT": ("router", "port", int),
    "ROUTER_API_KEY": ("router", "api_key", str),
    "RATE_LIMIT_CAPACITY": ("router", "rate_limit_capacity", int),
    "RATE_LIMIT_REFILL_PER_MIN": ("router", "rate_limit_refill_per_min", int),
    "CACHE_ENABLED": ("router", "cache_enabled",
                      lambda v: v.lower() in ("1", "true", "yes")),
    "CACHE_SIZE": ("router", "cache_size", int),
    "BACKEND_TIMEOUT": ("router", "backend_timeout_s", int),
    "MOCK_LLM": ("router", "mock_llm",
                 lambda v: v.lower() in ("1", "true", "yes")),
    "AGENT_MODEL_OVERRIDES": ("router", "model_overrides", json.loads),
    "AGENT_API_PORT": ("agents", "port", int),
    "DEFAULT_PROFILE": ("agents", "default_profile", str),
    "MEMORY_MAX_TURNS": ("agents", "memory_max_turns", int),
    "WORKFLOW_PORT": ("workflow", "port", int),
    "WORKFLOW_AUDIT_LOG": ("workflow", "audit_log", str),
    "STEP_RETRIES": ("workflow", "step_retries", int),
    "RETRY_DELAY_S": ("workflow", "retry_delay_s", int),
    "DASHBOARD_PORT": ("dashboard", "port", int),
    "GPU_TEMP_ALERT_C": ("dashboard", "gpu_temp_alert_c", int),
    "GPU_UTIL_ALERT_PCT": ("dashboard", "gpu_util_alert_pct", int),
}


def _repo_root():
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def load_config():
    cfg = {}
    path = os.path.join(_repo_root(), "config", "config.json")
    try:
        with open(path) as f:
            cfg = json.load(f)
    except (OSError, ValueError):
        cfg = {}

    for env, (section, key, cast) in _ENV_OVERRIDES.items():
        raw = os.environ.get(env)
        if raw is None or raw == "":
            continue
        try:
            cfg.setdefault(section, {})[key] = cast(raw)
        except (ValueError, TypeError):
            continue

    # Docker service discovery defaults
    if os.environ.get("LLAMA_BASE"):
        cfg.setdefault("router", {})["llama_base"] = \
            os.environ["LLAMA_BASE"]
    if os.environ.get("AGENT_API"):
        cfg.setdefault("workflow", {})["agent_api"] = \
            os.environ["AGENT_API"]
    return cfg
