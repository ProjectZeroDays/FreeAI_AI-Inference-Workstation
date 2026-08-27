# -*- coding: utf-8 -*-
"""OpenTelemetry tracing integration for FreeAI router.

Provides a no-op fallback so the router works without opentelemetry installed.
"""
import os
import uuid
import time
from contextlib import contextmanager

_OTEL_AVAILABLE = False
_tracer = None
_provider = None
_service_name = os.environ.get("OTEL_SERVICE_NAME", "freeai-router")
_otlp_endpoint = os.environ.get("OTEL_EXPORTER_OTLP_ENDPOINT", "")
_traces_store = []
_TRACE_STORE_MAX = 200


def _try_init():
    global _OTEL_AVAILABLE, _tracer
    try:
        from opentelemetry import trace
        from opentelemetry.sdk.trace import TracerProvider
        from opentelemetry.sdk.trace.export import (
            BatchSpanProcessor, SimpleSpanProcessor,
        )
        from opentelemetry.trace import SpanKind

        _resource = None
        try:
            from opentelemetry.sdk.resources import Resource
            _resource = Resource.create({"service.name": _service_name})
        except ImportError:
            pass
        _provider = TracerProvider(resource=_resource)

        if _otlp_endpoint:
            try:
                from opentelemetry.exporter.otlp.proto.http.trace_exporter import (
                    OTLPSpanExporter,
                )
                exporter = OTLPSpanExporter(endpoint=_otlp_endpoint)
                _provider.add_span_processor(BatchSpanProcessor(exporter))
            except ImportError:
                try:
                    from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import (
                        OTLPSpanExporter,
                    )
                    exporter = OTLPSpanExporter(endpoint=_otlp_endpoint.replace("http://", "").replace("https://", ""))
                    _provider.add_span_processor(BatchSpanProcessor(exporter))
                except ImportError:
                    from opentelemetry.exporter.otlp.proto.http.trace_exporter import (
                        OTLPSpanExporter,
                    )
                    exporter = OTLPSpanExporter(endpoint=_otlp_endpoint)
                    _provider.add_span_processor(BatchSpanProcessor(exporter))
        else:
            try:
                from opentelemetry.sdk.trace.export import ConsoleSpanExporter
                _provider.add_span_processor(SimpleSpanProcessor(ConsoleSpanExporter()))
            except ImportError:
                pass

        trace.set_tracer_provider(_provider)
        _tracer = trace.get_tracer("freeai.router", "1.0.0")
        _OTEL_AVAILABLE = True
    except ImportError:
        _tracer = None
        _OTEL_AVAILABLE = False


_try_init()


class _NoOpSpan:
    """Minimal no-op span that supports set_attribute and set_status."""

    def __init__(self, name):
        self.name = name
        self._attrs = {}
        self._start_time = time.monotonic()

    def set_attribute(self, key, value):
        self._attrs[key] = value

    def set_status(self, status):
        pass

    def end(self):
        pass

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.end()


class _NoOpTracer:
    def start_span(self, name, **kwargs):
        return _NoOpSpan(name)

    @contextmanager
    def start_as_current_span(self, name, **kwargs):
        span = _NoOpSpan(name)
        yield span
        span.end()


def get_tracer():
    """Return the active tracer (real or no-op)."""
    if _tracer is None:
        _try_init()
    return _tracer or _NoOpTracer()


def record_trace(trace_id, task_type, model_used, latency_ms, status, confidence):
    """Keep an in-memory ring of recent traces for the /api/traces endpoint."""
    entry = {
        "trace_id": trace_id,
        "timestamp": time.time(),
        "task_type": task_type,
        "model_used": model_used or "unknown",
        "latency_ms": latency_ms,
        "status": status,
        "confidence": confidence,
    }
    _traces_store.append(entry)
    if len(_traces_store) > _TRACE_STORE_MAX:
        _traces_store.pop(0)


def get_recent_traces(limit=50):
    """Return the most recent traces, newest first."""
    return list(reversed(_traces_store[-limit:]))


def make_trace_id():
    return uuid.uuid4().hex


@contextmanager
def route_span(trace_id, task_type, confidence):
    """Context manager that starts/ends a span around a /route request."""
    tracer = get_tracer()
    span = tracer.start_span(
        "freeai.route",
        kind=tracer.__class__ is not _NoOpTracer and 2 or None,
    )
    if span is not None:
        span.set_attribute("freeai.task_type", task_type)
        span.set_attribute("freeai.confidence", confidence)
        span.set_attribute("freeai.trace_id", trace_id)
        span.set_attribute("service.name", _service_name)
    try:
        yield span
    finally:
        if span is not None:
            span.end()


def tag_model(span, model_used):
    if span is not None:
        span.set_attribute("freeai.model", model_used)


def tag_status(span, status):
    if span is not None:
        if isinstance(status, int):
            span.set_attribute("http.status_code", status)
            span.set_attribute("freeai.status", str(status))
        else:
            span.set_attribute("freeai.status", str(status))


def tag_latency(span, latency_ms):
    if span is not None:
        span.set_attribute("freeai.latency_ms", int(latency_ms))
