# -*- coding: utf-8 -*-
"""Prometheus metrics registry for FreeAI Router.

Exposes standard Prometheus counters, histograms, and gauges alongside the
legacy in-process METRICS dict so /metrics renders both legacy JSON and
Prometheus text format.
"""
import threading

try:
    from prometheus_client import Counter, Histogram, Gauge, CollectorRegistry, generate_latest
except ImportError:
    Counter = Histogram = Gauge = CollectorRegistry = generate_latest = None  # type: ignore

_registry = None
_lock = threading.Lock()


def get_registry():
    """Return (registry, helpers) or (None, None) if prometheus_client absent."""
    global _registry
    if _registry is not None:
        return _registry
    if Counter is None:
        return None, None
    with _lock:
        if _registry is not None:
            return _registry
        reg = CollectorRegistry()
        requests_total = Counter(
            "requests_total",
            "Total HTTP requests to the router",
            labelnames=["endpoint", "method", "status"],
            registry=reg,
        )
        request_duration = Histogram(
            "request_duration_seconds",
            "Request latency in seconds",
            labelnames=["endpoint"],
            buckets=(0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0),
            registry=reg,
        )
        active_requests = Gauge(
            "active_requests",
            "Number of requests currently being processed",
            registry=reg,
        )
        model_calls_total = Counter(
            "model_calls_total",
            "Total model inference calls",
            labelnames=["model"],
            registry=reg,
        )
        model_latency_seconds = Histogram(
            "model_latency_seconds",
            "Model inference latency",
            labelnames=["model"],
            buckets=(0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0, 30.0),
            registry=reg,
        )
        fallback_count = Counter(
            "fallback_count",
            "Number of fallback chain transitions",
            labelnames=["from_model", "to_model"],
            registry=reg,
        )
        task_type_total = Counter(
            "task_type_total",
            "Total requests by classified task type",
            labelnames=["task_type"],
            registry=reg,
        )
        confidence_bucket = Histogram(
            "classification_confidence",
            "Task classification confidence score",
            labelnames=["task_type"],
            buckets=(0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0),
            registry=reg,
        )
        gpu_utilization = Gauge(
            "gpu_utilization_percent",
            "GPU utilization percentage (0-100), 0 if unavailable",
            registry=reg,
        )
        _registry = (
            reg,
            dict(
                requests_total=requests_total,
                request_duration=request_duration,
                active_requests=active_requests,
                model_calls_total=model_calls_total,
                model_latency_seconds=model_latency_seconds,
                fallback_count=fallback_count,
                task_type_total=task_type_total,
                confidence_bucket=confidence_bucket,
                gpu_utilization=gpu_utilization,
            ),
        )
    return _registry


def render_metrics():
    """Return Prometheus text-format metrics or None if library unavailable."""
    reg, _ = get_registry()
    if reg is None:
        return None
    return generate_latest(reg).decode("utf-8")
