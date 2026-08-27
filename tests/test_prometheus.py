"""Prometheus metrics registry tests."""
import sys
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "router"))

import pytest
flask = pytest.importorskip("flask")

import router as router_mod  # noqa: E402


def test_prometheus_module_importable():
    """The prometheus module should be importable even without library."""
    from metrics import prometheus
    assert hasattr(prometheus, "get_registry")
    assert hasattr(prometheus, "render_metrics")


def test_get_registry_returns_helpers():
    from metrics.prometheus import get_registry
    reg, helpers = get_registry()
    if reg is not None:
        assert "requests_total" in helpers
        assert "request_duration" in helpers
        assert "active_requests" in helpers
        assert "model_calls_total" in helpers
        assert "model_latency_seconds" in helpers
        assert "fallback_count" in helpers
        assert "task_type_total" in helpers
        assert "confidence_bucket" in helpers
        assert "gpu_utilization" in helpers


def test_render_metrics_returns_text_when_available():
    from metrics.prometheus import render_metrics
    result = render_metrics()
    if result is not None:
        assert isinstance(result, str)
        assert "requests_total" in result
        assert "# HELP" in result
        assert "# TYPE" in result


def test_render_metrics_returns_none_when_library_absent(monkeypatch):
    from metrics import prometheus
    monkeypatch.setattr(prometheus, "Counter", None)
    monkeypatch.setattr(prometheus, "Histogram", None)
    monkeypatch.setattr(prometheus, "Gauge", None)
    monkeypatch.setattr(prometheus, "CollectorRegistry", None)
    monkeypatch.setattr(prometheus, "generate_latest", None)
    # Reset registry so it re-evaluates
    prometheus._registry = None
    assert prometheus.render_metrics() is None


def test_counter_increments(monkeypatch):
    from metrics import prometheus
    reg, helpers = prometheus.get_registry()
    if reg is None:
        pytest.skip("prometheus_client not installed")
    helpers["requests_total"].labels("test", "GET", "200").inc(1)
    helpers["requests_total"].labels("test", "GET", "200").inc(2)
    text = prometheus.render_metrics()
    assert "requests_total{endpoint=\"test\",method=\"GET\",status=\"200\"} 3" in text


def test_histogram_records_buckets(monkeypatch):
    from metrics import prometheus
    reg, helpers = prometheus.get_registry()
    if reg is None:
        pytest.skip("prometheus_client not installed")
    helpers["request_duration"].labels("test").observe(0.1)
    helpers["request_duration"].labels("test").observe(0.25)
    helpers["request_duration"].labels("test").observe(0.5)
    text = prometheus.render_metrics()
    assert "request_duration_seconds_bucket" in text
    assert "request_duration_seconds_sum" in text
    assert "request_duration_seconds_count" in text


def test_gauge_set_and_get(monkeypatch):
    from metrics import prometheus
    reg, helpers = prometheus.get_registry()
    if reg is None:
        pytest.skip("prometheus_client not installed")
    helpers["gpu_utilization"].set(75.5)
    text = prometheus.render_metrics()
    assert "gpu_utilization_percent 75.5" in text


def test_label_filtering_in_metrics_text(monkeypatch):
    from metrics import prometheus
    reg, helpers = prometheus.get_registry()
    if reg is None:
        pytest.skip("prometheus_client not installed")
    helpers["requests_total"].labels("/route", "POST", "200").inc(1)
    helpers["requests_total"].labels("/health", "GET", "200").inc(1)
    text = prometheus.render_metrics()
    assert 'endpoint="/route"' in text
    assert 'endpoint="/health"' in text


def test_metrics_endpoint_via_flask_client():
    """Test that /metrics returns JSON with requests_total key."""
    router_mod.app.config["TESTING"] = True
    router_mod.metrics_incr("requests_total")
    with router_mod.app.test_client() as c:
        res = c.get("/metrics")
    assert res.status_code == 200
    body = res.get_json()
    assert body is not None
    assert "requests_total" in body


def test_metrics_incr_and_read():
    """Test that metrics_incr increments the counter."""
    router_mod.app.config["TESTING"] = True
    initial = router_mod.METRICS.get("requests_total", 0)
    router_mod.metrics_incr("requests_total")
    router_mod.metrics_incr("requests_total")
    assert router_mod.METRICS["requests_total"] == initial + 2


def test_metrics_latency_recorded():
    """Test that metrics_latency records sum and count."""
    router_mod.app.config["TESTING"] = True
    # Reset to isolate from other tests
    router_mod.METRICS["latency_sum_ms"] = 0.0
    router_mod.METRICS["latency_count"] = 0
    router_mod.metrics_latency(42.5)
    assert router_mod.METRICS["latency_sum_ms"] == 42.5
    assert router_mod.METRICS["latency_count"] == 1


def test_metrics_model_tracked():
    """Test that metrics_model tracks model calls."""
    router_mod.app.config["TESTING"] = True
    router_mod.metrics_model("openai/gpt-4o-mini")
    models = router_mod.METRICS.get("by_model", {})
    assert models.get("openai/gpt-4o-mini", 0) >= 1


def test_metrics_error_counter():
    """Test that metrics_incr tracks errors."""
    router_mod.app.config["TESTING"] = True
    initial = router_mod.METRICS.get("errors_total", 0)
    router_mod.metrics_incr("errors_total")
    assert router_mod.METRICS["errors_total"] == initial + 1


def test_metrics_task_tracked():
    """Test that metrics_task tracks task types."""
    router_mod.app.config["TESTING"] = True
    router_mod.metrics_task("full_project")
    by_task = router_mod.METRICS.get("by_task", {})
    assert by_task.get("full_project", 0) >= 1


def test_metrics_cache_hits():
    """Test that cache hits are tracked."""
    router_mod.app.config["TESTING"] = True
    initial = router_mod.METRICS.get("cache_hits", 0)
    router_mod.metrics_incr("cache_hits")
    assert router_mod.METRICS["cache_hits"] == initial + 1
