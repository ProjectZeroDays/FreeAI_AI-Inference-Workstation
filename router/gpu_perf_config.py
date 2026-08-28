"""GPU performance configuration for FreeAI inference workstation.

Controls CUDA graph capture, quantization settings, speculative decoding,
and GPU monitoring intervals.
"""
import os
import json
from pathlib import Path

ROOT = Path(__file__).parent.parent
DEFAULT_CONFIG_PATH = ROOT / "config" / "gpu-perf.json"

# ── CUDA Graph settings ──────────────────────────────────────────
CUDA_GRAPH_ENABLED = os.environ.get("CUDA_GRAPH_ENABLED", "1").lower() in ("1", "true", "yes")
CUDA_GRAPH_DYNAMIC_SEQ = os.environ.get("CUDA_GRAPH_DYNAMIC_SEQ", "1").lower() in ("1", "true", "yes")
CUDA_GRAPH_CAPTURE_TIMEOUT_S = int(os.environ.get("CUDA_GRAPH_CAPTURE_TIMEOUT_S", "30"))

# ── Quantization settings ───────────────────────────────────────
KV_CACHE_QUANT_BITS = int(os.environ.get("KV_CACHE_QUANT_BITS", "8"))  # 4 or 8
KV_CACHE_QUANT_ENABLED = os.environ.get("KV_CACHE_QUANT_ENABLED", "1").lower() in ("1", "true", "yes")
KV_CACHE_QUANT_THRESHOLD = float(os.environ.get("KV_CACHE_QUANT_THRESHOLD", "0.9"))  # min utilization to enable

# ── Speculative decoding settings ───────────────────────────────
SPECULATIVE_DECODING_ENABLED = os.environ.get("SPECULATIVE_DECODING_ENABLED", "0").lower() in ("1", "true", "yes")
SPECULATIVE_DRAFT_MODEL = os.environ.get("SPECULATIVE_DRAFT_MODEL", "")
SPECULATIVE_ACCEPT_THRESHOLD = float(os.environ.get("SPECULATIVE_ACCEPT_THRESHOLD", "0.5"))
SPECULATIVE_MAX_DRAFT_TOKENS = int(os.environ.get("SPECULATIVE_MAX_DRAFT_TOKENS", "5"))

# ── GPU monitoring settings ─────────────────────────────────────
GPU_MONITOR_INTERVAL_S = int(os.environ.get("GPU_MONITOR_INTERVAL_S", "5"))
GPU_PERF_METRICS_ENABLED = os.environ.get("GPU_PERF_METRICS_ENABLED", "1").lower() in ("1", "true", "yes")


def load_config(path=None):
    """Load GPU perf config from JSON file with env var overrides."""
    cfg_path = path or os.environ.get("GPU_PERF_CONFIG", str(DEFAULT_CONFIG_PATH))
    default = {
        "cuda_graph": {
            "enabled": CUDA_GRAPH_ENABLED,
            "dynamic_seq": CUDA_GRAPH_DYNAMIC_SEQ,
            "capture_timeout_s": CUDA_GRAPH_CAPTURE_TIMEOUT_S,
        },
        "kv_cache_quant": {
            "enabled": KV_CACHE_QUANT_ENABLED,
            "bits": KV_CACHE_QUANT_BITS,
            "threshold": KV_CACHE_QUANT_THRESHOLD,
        },
        "speculative_decoding": {
            "enabled": SPECULATIVE_DECODING_ENABLED,
            "draft_model": SPECULATIVE_DRAFT_MODEL,
            "accept_threshold": SPECULATIVE_ACCEPT_THRESHOLD,
            "max_draft_tokens": SPECULATIVE_MAX_DRAFT_TOKENS,
        },
        "monitoring": {
            "interval_s": GPU_MONITOR_INTERVAL_S,
            "metrics_enabled": GPU_PERF_METRICS_ENABLED,
        },
    }
    try:
        with open(cfg_path) as f:
            file_cfg = json.load(f)
        for section in default:
            if section in file_cfg:
                default[section].update(file_cfg[section])
    except (OSError, ValueError):
        pass
    return default


def save_config(cfg, path=None):
    """Persist GPU perf config to JSON file."""
    cfg_path = path or str(DEFAULT_CONFIG_PATH)
    Path(cfg_path).parent.mkdir(parents=True, exist_ok=True)
    with open(cfg_path, "w") as f:
        json.dump(cfg, f, indent=2)
