# -*- coding: utf-8 -*-
"""Tests for tracer/otel.py."""
import json
import os
import sys
import time

import pytest

# Ensure router dir is on path so we can import tracer relative to it
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

import tracer.otel as otel  # noqa: E402


def test_noop_tracer_works_without_opentelemetry():
    """Even if opentelemetry is installed, the no-op path must work."""
    span = otel.get_tracer().start_span("test")
    assert span is not None
    span.set_attribute("foo", "bar")
    span.set_status("ok")
    span.end()


def test_route_span_context_manager():
    with otel.route_span("trace-123", "full_project", 0.85) as span:
        assert span is not None
        otel.tag_model(span, "qwen3.6-12b")
        otel.tag_status(span, 200)
        otel.tag_latency(span, 42)
    # span ended without error


def test_record_and_retrieve_traces():
    otel._traces_store.clear()
    tid = otel.make_trace_id()
    otel.record_trace(tid, "refactor", "claude-code-9b", 150, 200, 0.9)
    otel.record_trace(tid + "x", "analysis", "qwythos-v2", 300, 200, 0.85)
    recent = otel.get_recent_traces()
    assert len(recent) == 2
    assert recent[0]["trace_id"] == tid + "x"
    assert recent[1]["trace_id"] == tid
    assert recent[0]["model_used"] == "qwythos-v2"
    assert recent[1]["latency_ms"] == 150


def test_traces_ring_buffer():
    otel._traces_store.clear()
    for i in range(250):
        otel.record_trace(f"t-{i}", "general_code", "moe-13b", 10, 200, 0.5)
    recent = otel.get_recent_traces(limit=50)
    assert len(recent) == 50
    assert recent[0]["trace_id"] == "t-249"


def test_make_trace_id_is_hex():
    tid = otel.make_trace_id()
    assert len(tid) == 32
    int(tid, 16)  # must be valid hex


def test_service_name_default():
    """Default service name when OTEL_SERVICE_NAME is not set."""
    assert otel._service_name == "freeai-router"


def test_empty_endpoint_no_crash():
    """With no OTEL_EXPORTER_OTLP_ENDPOINT, init should not raise."""
    otel._traces_store.clear()
    tracer = otel.get_tracer()
    assert tracer is not None
