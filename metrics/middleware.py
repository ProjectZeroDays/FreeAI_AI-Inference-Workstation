# -*- coding: utf-8 -*-
"""Flask middleware for auto-instrumenting FreeAI Router requests.

Wired into router.py via app.before_request / after_request hooks.
Tracks per-endpoint request counts, durations, and active-concurrent count.
"""
import time
import threading

from flask import request

from .prometheus import get_registry

_service_name = "freeai-router"
_lock = threading.Lock()
_active = 0


def instrument_app(app):
    """Attach before/after request hooks to a Flask app for Prometheus metrics."""

    @app.before_request
    def _prom_before():
        if request.path == "/metrics":
            return
        reg, helpers = get_registry()
        if reg is None:
            return
        global _active
        with _lock:
            _active += 1
        helpers["active_requests"].set(_active)

    @app.after_request
    def _prom_after(response):
        if request.path == "/metrics":
            return response
        reg, helpers = get_registry()
        if reg is None:
            return
        try:
            endpoint = _sanitize_endpoint(request.path)
            method = request.method.lower()
            status = str(response.status_code)
            helpers["requests_total"].labels(
                endpoint=endpoint, method=method, status=status
            ).inc()
            helpers["request_duration"].labels(endpoint=endpoint).observe(
                request.elapsed.total_seconds()
                if hasattr(request, "elapsed")
                else 0
            )
        except Exception:
            pass
        finally:
            global _active
            with _lock:
                _active -= 1
            reg, helpers = get_registry()
            if helpers is not None:
                helpers["active_requests"].set(max(_active, 0))
        return response

    return app


def _sanitize_endpoint(path):
    """Collapse path into a stable label value, stripping UUIDs and IDs."""
    parts = path.strip("/").split("/")
    out = []
    for p in parts:
        if p and all(c in "0123456789abcdef-" for c in p.replace("-", "")) and len(p) > 8:
            out.append("{id}")
        else:
            out.append(p)
    return "/".join(out) or "root"
