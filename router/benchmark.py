"""Standardised benchmark runner for model performance comparison.

Runs a fixed set of prompts through each registered model, measures cold
start, warm inference latency and throughput, and writes a report to
config/models.json (benchmark section) and prints a summary.
"""
import json
import os
import time
import threading
from pathlib import Path
from typing import Dict, List, Optional

from settings import load_config

ROOT = Path(__file__).parent.parent
REPORT_PATH = ROOT / "config" / "models-benchmark.json"

_BENCHMARK_PROMPTS = [
    "Write a Python function that reverses a linked list iteratively.",
    "Explain the difference between multiprocessing and multithreading in Python.",
    "Design a REST API for a URL shortening service with rate limiting.",
    "Implement a basic HTTP server in Python without external libraries.",
    "Write a SQL query to find the second highest salary from an Employee table.",
    "Describe how a B-tree index works and when to use it over a hash index.",
    "Refactor this code to use comprehensions: result = []; for x in range(10): result.append(x**2)",
    "What are the time and space complexities of merge sort? Explain why.",
]

_cfg = load_config().get("router", {}).get("model_benchmark", {})
_MAX_TOKENS = int(os.environ.get("BENCHMARK_MAX_TOKENS",
                                  _cfg.get("max_tokens", 256)))
_TIMEOUT_S = int(os.environ.get("BENCHMARK_TIMEOUT_S",
                                 _cfg.get("timeout_s", 60)))
_COLD_RUNS = int(os.environ.get("BENCHMARK_COLD_RUNS",
                                 _cfg.get("cold_runs", 1)))
_WARM_RUNS = int(os.environ.get("BENCHMARK_WARM_RUNS",
                                 _cfg.get("warm_runs", 3)))


class BenchmarkRunner:
    """Run benchmark tasks against a model endpoint and collect metrics."""

    def __init__(self, endpoint: str, model_name: str,
                 max_tokens: int = _MAX_TOKENS,
                 timeout_s: int = _TIMEOUT_S):
        self.endpoint = endpoint
        self.model_name = model_name
        self.max_tokens = max_tokens
        self.timeout_s = timeout_s
        self._lock = threading.Lock()
        self._results: Dict = {}

    def run(self) -> Dict:
        """Run all benchmark prompts and return aggregated results."""
        import requests

        results: Dict = {
            "model": self.model_name,
            "endpoint": self.endpoint,
            "cold_start": {"latency_ms": None, "success": False},
            "warm_inference": {"latency_ms_avg": None, "token_rates": []},
            "throughput": {"tokens_per_sec": None, "requests": []},
            "errors": 0,
            "samples": [],
        }

        # --- cold start: first request after "no traffic" ---
        for i in range(_COLD_RUNS):
            prompt = _BENCHMARK_PROMPTS[i % len(_BENCHMARK_PROMPTS)]
            t0 = time.monotonic()
            try:
                r = requests.post(self.endpoint, json={
                    "prompt": prompt,
                    "max_tokens": self.max_tokens,
                    "temperature": 0.2,
                }, timeout=self.timeout_s)
                r.raise_for_status()
                body = r.json()
                elapsed_ms = (time.monotonic() - t0) * 1000
                text = self._extract_text(body)
                tokens = max(1, len(text.split()))
                results["cold_start"] = {
                    "latency_ms": round(elapsed_ms, 1),
                    "success": True,
                    "tokens_generated": tokens,
                }
                results["samples"].append({
                    "prompt_idx": i,
                    "type": "cold",
                    "latency_ms": round(elapsed_ms, 1),
                    "tokens": tokens,
                    "ok": True,
                })
                break
            except Exception as exc:
                results["errors"] += 1
                results["samples"].append({
                    "prompt_idx": i,
                    "type": "cold",
                    "error": str(exc),
                    "ok": False,
                })

        # --- warm inference: fire multiple prompts back-to-back ---
        latencies: List[float] = []
        tps_list: List[float] = []
        for i in range(_WARM_RUNS):
            prompt = _BENCHMARK_PROMPTS[(i + 2) % len(_BENCHMARK_PROMPTS)]
            t0 = time.monotonic()
            try:
                r = requests.post(self.endpoint, json={
                    "prompt": prompt,
                    "max_tokens": self.max_tokens,
                    "temperature": 0.2,
                }, timeout=self.timeout_s)
                r.raise_for_status()
                body = r.json()
                elapsed_ms = (time.monotonic() - t0) * 1000
                text = self._extract_text(body)
                tokens = max(1, len(text.split()))
                tps = tokens / (elapsed_ms / 1000) if elapsed_ms > 0 else 0
                latencies.append(elapsed_ms)
                tps_list.append(tps)
                results["samples"].append({
                    "prompt_idx": i + _COLD_RUNS,
                    "type": "warm",
                    "latency_ms": round(elapsed_ms, 1),
                    "tokens": tokens,
                    "tokens_per_sec": round(tps, 1),
                    "ok": True,
                })
            except Exception as exc:
                results["errors"] += 1
                results["samples"].append({
                    "prompt_idx": i + _COLD_RUNS,
                    "type": "warm",
                    "error": str(exc),
                    "ok": False,
                })

        if latencies:
            results["warm_inference"] = {
                "latency_ms_avg": round(sum(latencies) / len(latencies), 1),
                "latency_ms_p50": round(sorted(latencies)[len(latencies) // 2], 1),
                "tokens_per_sec_avg": round(sum(tps_list) / len(tps_list), 1),
            }
            results["throughput"] = {
                "tokens_per_sec": round(sum(tps_list) / len(tps_list), 1),
                "requests": len(latencies),
            }

        self._results = results
        return results

    def _extract_text(self, body: dict) -> str:
        choices = body.get("choices")
        if choices:
            msg = choices[0].get("message") or {}
            return msg.get("content") or choices[0].get("text") or ""
        return body.get("content") or ""

    def get_results(self) -> Dict:
        return self._results


def run_benchmark(endpoint: str, model_name: str) -> Dict:
    runner = BenchmarkRunner(endpoint, model_name)
    return runner.run()


def save_report(report: Dict) -> Path:
    """Append a benchmark run to config/models-benchmark.json."""
    try:
        existing = {}
        if REPORT_PATH.exists():
            existing = json.loads(REPORT_PATH.read_text())
    except (json.JSONDecodeError, OSError):
        existing = {}

    runs = existing.get("runs", [])
    runs.append({
        "timestamp": time.time(),
        "date": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "results": report,
    })
    existing["runs"] = runs[-50:]  # keep last 50 runs
    existing["latest"] = report
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text(json.dumps(existing, indent=2))
    return REPORT_PATH


def load_report() -> Dict:
    try:
        return json.loads(REPORT_PATH.read_text())
    except (json.JSONDecodeError, OSError):
        return {"runs": [], "latest": None}
