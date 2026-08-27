"""GPU stress tests for the router inference path.

Runs multiple concurrent /route requests and reports throughput, VRAM, and
temperature. Falls back to a mock GPU when nvidia-smi is unavailable.
"""
import asyncio
import json
import os
import statistics
import subprocess
import sys
import time
from concurrent.futures import ThreadPoolExecutor

import pytest

flask = pytest.importorskip("flask")

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "router"))

import router as router_mod  # noqa: E402


@pytest.fixture()
def client():
    router_mod.app.config["TESTING"] = True
    with router_mod.app.test_client() as c:
        yield c


def _read_gpu():
    """Read GPU stats via nvidia-smi; returns mock if unavailable."""
    try:
        out = subprocess.check_output(
            ["nvidia-smi", "--query-gpu=index,utilization.gpu,memory.used,memory.total,temperature.gpu,power.draw",
             "--format=csv,noheader,nounits"],
            timeout=5,
        ).decode().strip()
        devices = []
        for line in out.splitlines():
            parts = [p.strip() for p in line.split(",")]
            if len(parts) == 6:
                devices.append({
                    "index": int(parts[0]),
                    "util_pct": float(parts[1]),
                    "mem_used_mb": int(parts[2]) * 1024,
                    "mem_total_mb": int(parts[3]) * 1024,
                    "temp_c": float(parts[4]),
                    "power_w": float(parts[5]),
                })
        if devices:
            return devices
    except Exception:
        pass
    # Mock fallback
    return [{
        "index": 0,
        "util_pct": 0.0,
        "mem_used_mb": 0,
        "mem_total_mb": 8192,
        "temp_c": 35.0,
        "power_w": 0.0,
        "mock": True,
    }]


def _read_gpu_periodic(interval=0.5, duration=5):
    """Sample GPU readings over *duration* seconds."""
    samples = []
    start = time.monotonic()
    while time.monotonic() - start < duration:
        samples.extend(_read_gpu())
        time.sleep(interval)
    return samples


def _compute_stats(samples):
    """Aggregate a list of per-device samples."""
    if not samples:
        return {}
    n = len(samples)
    return {
        "samples": n,
        "avg_temp_c": round(sum(s["temp_c"] for s in samples) / n, 1),
        "max_temp_c": round(max(s["temp_c"] for s in samples), 1),
        "avg_util_pct": round(statistics.mean(s["util_pct"] for s in samples), 1),
        "max_mem_used_mb": max(s["mem_used_mb"] for s in samples),
        "total_mem_mb": samples[0]["mem_total_mb"],
        "mock": any(s.get("mock") for s in samples),
    }


# ── async concurrent inference ──────────────────────────────────────────

@pytest.mark.asyncio
async def test_concurrent_inference_throughput(client, monkeypatch):
    """Fire N requests concurrently and measure throughput."""
    n = 20
    durations = []
    import router as _router
    results = []

    def measure(idx):
        _router.app.config["TESTING"] = True
        with _router.app.test_client() as c:
            t0 = time.monotonic()
            res = c.post("/route", json={
                "prompt": f"concurrent test prompt {idx} — classify this task",
                "max_tokens": 64,
            })
        durations.append(time.monotonic() - t0)
        assert res.status_code == 200
        body = res.get_json()
        assert "task_type" in body
        assert "response" in body
        results.append(body)

    with ThreadPoolExecutor(max_workers=n) as pool:
        futures = [pool.submit(measure, i) for i in range(n)]
        for f in futures:
            f.result()

    assert len(results) == n
    p50 = round(statistics.median(durations) * 1000, 1)
    p95 = round(sorted(durations)[int(n * 0.95)] * 1000, 1)
    p99 = round(sorted(durations)[int(n * 0.99)] * 1000, 1)
    avg = round(statistics.mean(durations) * 1000, 1)
    throughput = round(n / sum(durations), 2)

    print(f"\n--- GPU Stress Report ---")
    print(f"  Requests   : {n}")
    print(f"  Throughput : {throughput} req/s")
    print(f"  Avg latency: {avg} ms")
    print(f"  p95 latency: {p95} ms")
    print(f"  p99 latency: {p99} ms")
    print("---\n")

    assert throughput > 0
    assert p50 >= 0


def test_gpu_stats_read_backend():
    """Verify the GPU read helper returns at least one device."""
    devices = _read_gpu()
    assert len(devices) >= 1
    dev = devices[0]
    assert "index" in dev
    assert "temp_c" in dev
    assert "mem_used_mb" in dev


def test_gpu_stats_report_format():
    """Verify stats aggregation output shape."""
    samples = [
        {"temp_c": 40.0, "util_pct": 75.0, "mem_used_mb": 4000,
         "mem_total_mb": 8192, "power_w": 120.0},
        {"temp_c": 45.0, "util_pct": 80.0, "mem_used_mb": 4500,
         "mem_total_mb": 8192, "power_w": 135.0},
    ]
    stats = _compute_stats(samples)
    assert stats["samples"] == 2
    assert stats["avg_temp_c"] == 42.5
    assert stats["max_temp_c"] == 45.0
    assert stats["avg_util_pct"] == 77.5
    assert stats["max_mem_used_mb"] == 4500
    assert stats["total_mem_mb"] == 8192
    assert stats["mock"] is False


def test_gpu_stats_mock_fallback():
    """When nvidia-smi fails, _read_gpu returns a mock device."""
    if sys.platform != "win32":
        import subprocess as sp
        orig = sp.check_output
        def fake(*a, **k):
            raise sp.CalledProcessError(1, "nvidia-smi")
        sp.check_output = fake
        try:
            devices = _read_gpu()
            assert devices[0]["mock"] is True
        finally:
            sp.check_output = orig
    else:
        # Windows path always falls through to mock
        devices = _read_gpu()
        assert devices[0]["mock"] is True
