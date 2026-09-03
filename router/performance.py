"""Per-model performance scoring.

Tracks latency, throughput, error rate and derives a weighted quality
score after every inference.  Config is read from config/model-performance.json.
"""
import json
import os
import threading
import time
from collections import deque
from pathlib import Path
from typing import Dict, Optional

try:
    from .settings import load_config
except ImportError:
    from settings import load_config

ROOT = Path(__file__).parent.parent
PERF_CONFIG_PATH = ROOT / "config" / "model-performance.json"

_DEFAULT_WEIGHTS = {"latency": 0.30, "tokens_per_sec": 0.30, "error_rate": 0.40}

_CFG = load_config().get("router", {}).get("model_performance", {})
_WEIGHTS = {
    "latency": float(_CFG.get("latency_weight", _DEFAULT_WEIGHTS["latency"])),
    "tokens_per_sec": float(
        _CFG.get("tokens_per_sec_weight", _DEFAULT_WEIGHTS["tokens_per_sec"])
    ),
    "error_rate": float(
        _CFG.get("error_rate_weight", _DEFAULT_WEIGHTS["error_rate"])
    ),
}

# Normalisation targets — lower is better for latency, higher is better
# for the others.  Values are in ms for latency, tok/s for throughput.
_DEFAULT_LATENCY_TARGET_MS = 500.0
_DEFAULT_TPS_TARGET = 50.0
_ERROR_TARGET = 0.05  # 5 %

_latency_target_ms = float(os.environ.get(
    "PERF_LATENCY_TARGET_MS", _CFG.get("latency_target_ms", _DEFAULT_LATENCY_TARGET_MS)))
_tps_target = float(os.environ.get(
    "PERF_TPS_TARGET", _CFG.get("tokens_per_sec_target", _DEFAULT_TPS_TARGET)))
_error_target = float(os.environ.get(
    "PERF_ERROR_TARGET", _CFG.get("error_target", _ERROR_TARGET)))


class _ModelStats:
    __slots__ = ("latency_windows", "tokens_windows", "error_count",
                 "success_count", "total_count", "last_updated")

    def __init__(self, window: int = 20):
        self.latency_windows: deque = deque(maxlen=window)
        self.tokens_windows: deque = deque(maxlen=window)
        self.error_count: int = 0
        self.success_count: int = 0
        self.total_count: int = 0
        self.last_updated: float = 0.0


class PerformanceScorer:
    """Tracks per-model metrics and computes a composite quality score."""

    def __init__(self):
        self._lock = threading.Lock()
        self._stats: Dict[str, _ModelStats] = {}
        self._history: Dict[str, deque] = {}
        self._history_max = 200

    # ---- public API ----

    def record_success(self, model: str, latency_ms: float, tokens: int) -> None:
        s = self._get(model)
        s.latency_windows.append(latency_ms)
        s.tokens_windows.append(tokens)
        s.success_count += 1
        s.total_count += 1
        s.last_updated = time.time()

    def record_error(self, model: str) -> None:
        s = self._get(model)
        s.error_count += 1
        s.total_count += 1
        s.last_updated = time.time()

    def score(self, model: str) -> Dict:
        s = self._stats.get(model)
        if s is None or s.total_count == 0:
            return self._empty_score(model)

        with self._lock:
            avg_latency = sum(s.latency_windows) / len(s.latency_windows) \
                if s.latency_windows else _latency_target_ms
            avg_tps = sum(s.tokens_windows) / len(s.tokens_windows) \
                if s.tokens_windows else _tps_target
            error_rate = s.error_count / s.total_count if s.total_count else 0.0

        # Normalised sub-scores (0-1, higher is better)
        latency_score = max(0.0, 1.0 - (avg_latency / _latency_target_ms))
        tps_score = min(1.0, avg_tps / _tps_target)
        error_score = max(0.0, 1.0 - (error_rate / _error_target))

        w = _WEIGHTS
        quality = (
            w["latency"] * latency_score
            + w["tokens_per_sec"] * tps_score
            + w["error_rate"] * error_score
        )

        entry = {
            "model": model,
            "latency_ms": round(avg_latency, 1),
            "tokens_per_sec": round(avg_tps, 1),
            "error_rate": round(error_rate, 4),
            "success_rate": round(1.0 - error_rate, 4),
            "total_calls": s.total_count,
            "quality_score": round(quality, 4),
            "last_updated": s.last_updated,
            "status": "active" if s.total_count > 0 else "inactive",
        }

        # Append to history
        hist = self._history.setdefault(model, deque(maxlen=self._history_max))
        hist.append({
            "ts": s.last_updated,
            "quality_score": entry["quality_score"],
            "latency_ms": entry["latency_ms"],
            "tokens_per_sec": entry["tokens_per_sec"],
        })

        return entry

    def all_scores(self) -> Dict[str, Dict]:
        with self._lock:
            return {m: self._score_unlocked(m) for m in self._stats}

    def history(self, model: str, limit: int = 50) -> list:
        with self._lock:
            hist = self._history.get(model, deque())
            return list(hist)[-limit:]

    def reset(self, model: Optional[str] = None) -> None:
        with self._lock:
            if model:
                self._stats.pop(model, None)
                self._history.pop(model, None)
            else:
                self._stats.clear()
                self._history.clear()

    # ---- internals ----

    def _get(self, model: str) -> _ModelStats:
        if model not in self._stats:
            self._stats[model] = _ModelStats()
        return self._stats[model]

    def _score_unlocked(self, model: str) -> Dict:
        s = self._stats.get(model)
        if s is None or s.total_count == 0:
            return self._empty_score(model)

        avg_latency = sum(s.latency_windows) / len(s.latency_windows) \
            if s.latency_windows else _latency_target_ms
        avg_tps = sum(s.tokens_windows) / len(s.tokens_windows) \
            if s.tokens_windows else _tps_target
        error_rate = s.error_count / s.total_count if s.total_count else 0.0

        latency_score = max(0.0, 1.0 - (avg_latency / _latency_target_ms))
        tps_score = min(1.0, avg_tps / _tps_target)
        error_score = max(0.0, 1.0 - (error_rate / _error_target))

        w = _WEIGHTS
        quality = (
            w["latency"] * latency_score
            + w["tokens_per_sec"] * tps_score
            + w["error_rate"] * error_score
        )

        entry = {
            "model": model,
            "latency_ms": round(avg_latency, 1),
            "tokens_per_sec": round(avg_tps, 1),
            "error_rate": round(error_rate, 4),
            "success_rate": round(1.0 - error_rate, 4),
            "total_calls": s.total_count,
            "quality_score": round(quality, 4),
            "last_updated": s.last_updated,
            "status": "active" if s.total_count > 0 else "inactive",
        }
        return entry

    @staticmethod
    def _empty_score(model: str) -> Dict:
        return {
            "model": model,
            "latency_ms": None,
            "tokens_per_sec": None,
            "error_rate": None,
            "success_rate": None,
            "total_calls": 0,
            "quality_score": None,
            "last_updated": 0.0,
            "status": "no_data",
        }


# Module-level singleton — imported by router.py and benchmark.py
scorer = PerformanceScorer()
