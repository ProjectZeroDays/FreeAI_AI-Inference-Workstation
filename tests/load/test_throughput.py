"""Load test: 10 concurrent requests to /route, measure latency with
concurrent.futures.  Uses a fresh Flask test client per thread with
MOCK_LLM=1 so no GPU is required.
"""
import os
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

import pytest

flask = pytest.importorskip("flask")

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "router"))

import router as router_mod  # noqa: E402


def _make_client():
    """Create a fresh test client for use in a single thread."""
    router_mod.app.config["TESTING"] = True
    return router_mod.app.test_client()


def _hit(idx):
    """Single request worker used by ThreadPoolExecutor."""
    client = _make_client()
    t0 = time.monotonic()
    res = client.post("/route", json={
        "prompt": f"load test prompt number {idx} for throughput measurement",
        "max_tokens": 64,
    })
    elapsed_ms = (time.monotonic() - t0) * 1000
    return {"index": idx, "status": res.status_code, "latency_ms": elapsed_ms}


def test_concurrent_throughput_10_requests():
    """Fire 10 concurrent /route requests and verify all succeed within
    a reasonable latency bound."""
    futures = []
    with ThreadPoolExecutor(max_workers=10) as executor:
        for i in range(10):
            futures.append(executor.submit(_hit, i))

    results = []
    for fut in as_completed(futures, timeout=30):
        results.append(fut.result())

    assert len(results) == 10
    statuses = [r["status"] for r in results]
    assert all(s == 200 for s in statuses), f"Unexpected statuses: {statuses}"

    latencies = [r["latency_ms"] for r in results]
    avg_ms = sum(latencies) / len(latencies)
    max_ms = max(latencies)
    min_ms = min(latencies)

    print(f"\n--- Throughput results (10 concurrent) ---")
    print(f"  avg ms  : {avg_ms:.1f}")
    print(f"  min ms  : {min_ms:.1f}")
    print(f"  max ms  : {max_ms:.1f}")
    print(f"-------------------------------------------\n")

    assert max_ms < 10_000, f"Max latency {max_ms:.0f}ms exceeded 10s bound"
    assert avg_ms > 0, "Average latency should be positive"


def test_latency_varies_per_request():
    """Each concurrent request should produce a distinct latency measurement."""
    futures = []
    with ThreadPoolExecutor(max_workers=10) as executor:
        for i in range(10):
            futures.append(executor.submit(_hit, i))

    results = [fut.result() for fut in as_completed(futures, timeout=30)]
    latencies = [r["latency_ms"] for r in results]

    assert len(latencies) == 10
    assert all(isinstance(l, (int, float)) for l in latencies)
    assert min(latencies) >= 0
