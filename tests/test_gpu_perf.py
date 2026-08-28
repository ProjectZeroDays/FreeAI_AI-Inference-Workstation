"""Tests for GPU performance module and API endpoints."""
import json
import math
import os
import sys
from pathlib import Path

import pytest

flask = pytest.importorskip("flask")

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "dashboard"))
sys.path.insert(0, os.path.join(ROOT, "router"))


class TestGPUMonitor:
    """Tests for GPUMonitor class."""

    def test_gpu_metrics_available_on_linux(self, monkeypatch):
        """Should read real metrics when nvidia-smi is available."""
        import platform
        monkeypatch.setattr(platform, "system", lambda: "Linux")

        import subprocess
        fake_output = ("0, NVIDIA A100-SXM4-40GB, 40960, 8192, 34%, 62, 180.5\n"
                       "1, NVIDIA A100-SXM4-40GB, 40960, 4096, 12%, 55, 95.0")

        def fake_run(cmd, **kwargs):
            class R:
                stdout = fake_output
                returncode = 0
            return R()

        monkeypatch.setattr(subprocess, "run", fake_run)

        from gpu_perf import GPUMonitor
        monitor = GPUMonitor(interval_s=60)
        metrics = monitor.get_metrics()

        assert metrics["gpu_available"] is True
        assert len(metrics["devices"]) == 2
        assert metrics["total_vram_mb"] == 2 * 40960 * 1024
        assert metrics["used_vram_mb"] == (8192 + 4096) * 1024
        assert metrics["temperature_c"] == 62

    def test_gpu_metrics_returns_mock_on_windows(self, monkeypatch):
        """Should return mock data on Windows."""
        import platform
        monkeypatch.setattr(platform, "system", lambda: "Windows")

        from gpu_perf import GPUMonitor
        monitor = GPUMonitor(interval_s=60)
        metrics = monitor.get_metrics()

        assert metrics["gpu_available"] is False
        assert metrics["platform"] == "Windows"
        assert len(metrics["devices"]) >= 1
        dev = metrics["devices"][0]
        assert dev["name"] == "mock-gpu"
        assert dev["total_vram_mb"] == 24576


class TestCUDAGraphManager:
    """Tests for CUDAGraphManager class."""

    def test_cuda_graph_skipped_on_non_linux(self, monkeypatch):
        import platform
        monkeypatch.setattr(platform, "system", lambda: "Windows")

        from gpu_perf import CUDAGraphManager
        mgr = CUDAGraphManager()
        result = mgr.capture(model_name="test-model")
        assert result["status"] == "skipped"
        assert result["mock"] is True

    def test_cuda_graph_capture_on_linux(self, monkeypatch):
        import platform
        monkeypatch.setattr(platform, "system", lambda: "Linux")

        import subprocess
        def fake_run(cmd, **kwargs):
            class R:
                stdout = "0, NVIDIA A100\n"
                returncode = 0
            return R()
        monkeypatch.setattr(subprocess, "run", fake_run)

        from gpu_perf import CUDAGraphManager
        mgr = CUDAGraphManager()
        result = mgr.capture(model_name="test-model", batch_size=4, seq_len=512)
        assert result["status"] == "captured"
        assert mgr.is_active() is True


class TestQuantizedKVCache:
    """Tests for QuantizedKVCache class."""

    def test_quantized_kv_cache_creation(self, monkeypatch):
        import platform
        monkeypatch.setattr(platform, "system", lambda: "Linux")

        import subprocess
        def fake_run(cmd, **kwargs):
            class R:
                stdout = "0, NVIDIA A100\n"
                returncode = 0
            return R()
        monkeypatch.setattr(subprocess, "run", fake_run)

        from gpu_perf import QuantizedKVCache
        cache = QuantizedKVCache(bits=8)
        result = cache.allocate(model_name="qwen-7b", max_seq_len=2048)
        assert result["status"] == "allocated"
        assert result["bits"] == 8
        assert result["estimated_mem_mb"] > 0

    def test_quantized_kv_invalid_bits(self):
        from gpu_perf import QuantizedKVCache
        with pytest.raises(ValueError):
            QuantizedKVCache(bits=16)

    def test_quantized_kv_stats(self, monkeypatch):
        import platform
        monkeypatch.setattr(platform, "system", lambda: "Linux")

        import subprocess
        def fake_run(cmd, **kwargs):
            class R:
                stdout = "0, NVIDIA A100\n"
                returncode = 0
            return R()
        monkeypatch.setattr(subprocess, "run", fake_run)

        from gpu_perf import QuantizedKVCache
        cache = QuantizedKVCache(bits=8)
        cache.allocate(model_name="test")
        cache.put("test", 0, 0, "value")
        cache.get("test", 0, 0)
        stats = cache.stats()
        assert stats["bits"] == 8
        assert stats["hits"] == 1
        assert stats["hit_rate"] == 1.0


class TestSpeculativeDecoding:
    """Tests for SpeculativeDecoding class."""

    def test_speculative_decoding_config(self, monkeypatch):
        import platform
        monkeypatch.setattr(platform, "system", lambda: "Linux")

        import subprocess
        def fake_run(cmd, **kwargs):
            class R:
                stdout = "0, NVIDIA A100\n"
                returncode = 0
            return R()
        monkeypatch.setattr(subprocess, "run", fake_run)

        from gpu_perf import SpeculativeDecoding
        sd = SpeculativeDecoding(draft_model="qwen-1.5b", accept_threshold=0.5)
        assert sd.is_configured is True
        assert sd.draft_model == "qwen-1.5b"

    def test_speculative_decoding_disabled_without_model(self, monkeypatch):
        import platform
        monkeypatch.setattr(platform, "system", lambda: "Linux")

        import subprocess
        def fake_run(cmd, **kwargs):
            class R:
                stdout = "0, NVIDIA A100\n"
                returncode = 0
            return R()
        monkeypatch.setattr(subprocess, "run", fake_run)

        from gpu_perf import SpeculativeDecoding
        sd = SpeculativeDecoding()
        assert sd.is_configured is False
        assert sd.is_active is False

    def test_speculative_decoding_stats(self, monkeypatch):
        import platform
        monkeypatch.setattr(platform, "system", lambda: "Linux")

        import subprocess
        def fake_run(cmd, **kwargs):
            class R:
                stdout = "0, NVIDIA A100\n"
                returncode = 0
            return R()
        monkeypatch.setattr(subprocess, "run", fake_run)
        monkeypatch.setattr(math, 'exp', math.exp)

        from gpu_perf import SpeculativeDecoding
        sd = SpeculativeDecoding(draft_model="qwen-1.5b", accept_threshold=0.3)
        drafts = sd.draft_tokens("hello", num_tokens=3)
        verification = sd.verify_tokens(drafts, target_logits=[0.9, 0.8, 0.7])
        assert verification["accepted"] > 0
        stats = sd.stats()
        assert stats["total_proposed"] == 3


class TestGPUPerformanceMetrics:
    """Tests for GPUPerformanceMetrics class."""

    def test_perf_metrics_report_empty(self):
        from gpu_perf import GPUPerformanceMetrics
        pm = GPUPerformanceMetrics()
        report = pm.get_report()
        assert report["samples"] == 0
        assert "optimizations" in report

    def test_perf_metrics_record_and_report(self):
        from gpu_perf import GPUPerformanceMetrics
        pm = GPUPerformanceMetrics()
        pm.record_sample({"latency_ms": 100, "throughput_tok_s": 50})
        pm.record_sample({"latency_ms": 120, "throughput_tok_s": 45})
        pm.set_optimization("cuda_graphs", True)
        report = pm.get_report()
        assert report["samples"] == 2
        assert report["avg_latency_ms"] == 110.0
        assert report["optimizations"]["cuda_graphs"] is True


# ── API Endpoint Tests ──────────────────────────────────────────

@pytest.fixture()
def client(monkeypatch):
    import backend as dash
    dash.app.config["TESTING"] = True
    dash.app.config["SECRET_KEY"] = "test-secret-for-gpu-perf"
    dash._gpu_perf_state.update({
        "cuda_graphs": False,
        "quantized_kv": False,
        "speculative_decoding": False,
        "last_recommendation": None,
    })
    with dash.app.test_client() as c:
        yield c


def _mock_gpu_available(monkeypatch):
    """Mock Linux + nvidia-smi availability for API tests."""
    # Patch both module paths that could be used
    monkeypatch.setattr("gpu_perf._is_linux", lambda: True)
    monkeypatch.setattr("gpu_perf._gpu_available", lambda: True)


def test_gpu_metrics_available_on_linux(client, monkeypatch):
    _mock_gpu_available(monkeypatch)
    res = client.get("/api/gpu/metrics")
    assert res.status_code == 200
    body = res.get_json()
    assert body["gpu_available"] is True
    assert len(body["devices"]) >= 1


def test_gpu_metrics_returns_mock_on_windows(client, monkeypatch):
    import platform
    monkeypatch.setattr(platform, "system", lambda: "Windows")
    monkeypatch.setattr("gpu_perf._is_linux", lambda: False)
    monkeypatch.setattr("gpu_perf._gpu_available", lambda: False)
    res = client.get("/api/gpu/metrics")
    assert res.status_code == 200
    body = res.get_json()
    assert body["gpu_available"] is False
    assert body["platform"] == "Windows"


def test_gpu_perf_enable_disable(client, monkeypatch):
    _mock_gpu_available(monkeypatch)
    res = client.post("/api/gpu/perf/enable", json={
        "cuda_graphs": True,
        "quantized_kv": True,
    })
    assert res.status_code == 200
    body = res.get_json()
    assert body["status"] == "enabled"

    res = client.post("/api/gpu/perf/disable", json={"cuda_graphs": True})
    assert res.status_code == 200
    body = res.get_json()
    assert body["status"] == "disabled"


def test_gpu_perf_status(client, monkeypatch):
    _mock_gpu_available(monkeypatch)
    res = client.get("/api/gpu/perf/status")
    assert res.status_code == 200
    body = res.get_json()
    assert "perf_state" in body
    assert "gpu_available" in body
    assert "metrics_report" in body


def test_gpu_perf_recommend(client, monkeypatch):
    _mock_gpu_available(monkeypatch)
    res = client.get("/api/gpu/perf/recommend")
    assert res.status_code == 200
    body = res.get_json()
    assert body["gpu_available"] is True
    assert "recommendations" in body
    assert len(body["recommendations"]) >= 2
    # A100 40GB should recommend quantized_kv and cuda_graphs
    rec_map = {r["option"]: r for r in body["recommendations"]}
    assert "quantized_kv" in rec_map
    assert "cuda_graphs" in rec_map


def test_gpu_perf_recommend_no_gpu(client, monkeypatch):
    import platform
    monkeypatch.setattr(platform, "system", lambda: "Windows")
    res = client.get("/api/gpu/perf/recommend")
    assert res.status_code == 200
    body = res.get_json()
    assert body["gpu_available"] is False
    assert body["mock"] is True


def test_gpu_perf_api_endpoints(client, monkeypatch):
    """Test all GPU perf API endpoints exist and return JSON."""
    endpoints = [
        ("GET", "/api/gpu/metrics"),
        ("POST", "/api/gpu/perf/enable"),
        ("POST", "/api/gpu/perf/disable"),
        ("GET", "/api/gpu/perf/status"),
        ("GET", "/api/gpu/perf/recommend"),
    ]
    for method, path in endpoints:
        if method == "GET":
            res = client.get(path)
        else:
            res = client.post(path, json={})
        assert res.status_code == 200, f"{method} {path} returned {res.status_code}"
        assert res.content_type.startswith("application/json"), \
            f"{method} {path} did not return JSON"
