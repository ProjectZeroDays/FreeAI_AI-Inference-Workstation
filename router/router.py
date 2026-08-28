# -*- coding: utf-8 -*-
"""FreeAI Router — task classification + fallback routing.

Features:
- Task classification with confidence score
- Fallback chain across the model roster
- Optional API-key auth (X-API-Key header when config/api-keys.json has keys)
- Per-client token-bucket rate limiting
- LRU response cache with TTL for repeated prompts
- Prometheus-style /metrics snapshot
- SSE streaming passthrough via /route and /route/stream
- Mock backend mode (MOCK_LLM=1) for dev/CI without a GPU
"""
import hashlib
import json
import logging
import os
import threading
import time

import requests
from flask import Flask, Response, request, jsonify, stream_with_context

from classifier import classify_task
from switcher import select_chain
from settings import load_config
from providers import (load_providers, is_keyed, keyed_providers,
                       fallback_models, call_provider, parse_response,
                       build_request)
from middleware import (RateLimiter, AuthMiddleware, CacheMiddleware,
                          rate_limiter, auth_middleware, cache_middleware,
                          get_client_api_key)
from load_balancer import (pick_backend, record_success, record_failure,
                           connection_start, connection_end,
                           all_state, get_state, FAILURE_THRESHOLD,
                           RECOVERY_TIMEOUT_S, ALGO as LB_ALGO)

from metrics.prometheus import get_registry, render_metrics
from metrics.middleware import instrument_app

# Tracing integration (no-op fallback if opentelemetry unavailable)
try:
    import tracer.otel as otel
except ImportError:
    otel = None

CFG = load_config().get("router", {})

API_KEY = CFG.get("api_key", "")
RATE_CAPACITY = int(CFG.get("rate_limit_capacity", 100))
RATE_REFILL = float(CFG.get("rate_limit_refill_per_min", 100)) / 60.0
CACHE_ENABLED = bool(CFG.get("cache_enabled", True))
CACHE_SIZE = int(CFG.get("cache_size", 128))
TIMEOUT = int(CFG.get("backend_timeout_s", 300))
MOCK_LLM = bool(CFG.get("mock_llm", False))

_SSE_HEADERS = {
    "Content-Type": "text/event-stream",
    "Cache-Control": "no-cache",
    "X-Accel-Buffering": "no",
    "Connection": "keep-alive",
}


def _send_sse_headers(response_headers: dict) -> dict:
    out = dict(response_headers)
    out.update(_SSE_HEADERS)
    return out


def _sse_event(data: dict) -> str:
    """Format a dict as an SSE data frame with optional retry directive."""
    return f"data: {json.dumps(data, separators=(',', ':'))}\n\n"


def _sse_retry(retry_ms: int = 3000) -> str:
    """Emit an SSE retry directive."""
    return f"retry: {retry_ms}\n\n"

app = Flask(__name__)
instrument_app(app)

# Backwards-compatible aliases for tests
allow_request = rate_limiter.allow
cache_get = cache_middleware.get
cache_put = cache_middleware.put


# ---------------------------------------------------------------- metrics
_METRICS_LOCK = threading.Lock()
METRICS = {
    "requests_total": 0,
    "cache_hits": 0,
    "errors_total": 0,
    "by_task": {},
    "by_model": {},
    "latency_sum_ms": 0,
    "latency_count": 0,
}


def metrics_incr(key, amount=1):
    with _METRICS_LOCK:
        METRICS[key] = METRICS.get(key, 0) + amount


def metrics_task(task):
    with _METRICS_LOCK:
        METRICS["by_task"][task] = METRICS["by_task"].get(task, 0) + 1


def metrics_model(model_key):
    with _METRICS_LOCK:
        METRICS["by_model"][model_key] = \
            METRICS["by_model"].get(model_key, 0) + 1


def metrics_latency(ms):
    with _METRICS_LOCK:
        METRICS["latency_sum_ms"] += ms
        METRICS["latency_count"] += 1


# ------------------------------------------------------------------- auth
@app.before_request
def guard():
    # Skip auth for these endpoints and in testing mode
    if request.path in {"/health", "/models", "/docs",
                        "/api/models/performance", "/api/models/benchmark",
                        "/api/models/rankings"}:
        return None
    if app.config.get("TESTING"):
        return None
    result = auth_middleware.check()
    if result is not None:
        return result
    if not rate_limiter.allow_client(get_client_api_key()):
        return jsonify({"error": "rate limited"}), 429
    return None


# ------------------------------------------------------------------ mock
_MOCK_WORDS = ("As a mock response, this text confirms routing, "
               "classification, caching, and agent plumbing work "
               "without a GPU backend. " * 8)


def mock_completion(payload):
    n = max(1, min(int(payload.get("max_tokens", 64)), len(_MOCK_WORDS)))
    return {"content": _MOCK_WORDS[:n], "mock": True}


# ----------------------------------------------------- degenerate guard
def _text_of(result):
    """Best-effort extraction of generated text from a backend payload."""
    if not isinstance(result, dict):
        return ""
    choices = result.get("choices")
    if choices:
        choice = choices[0] or {}
        msg = choice.get("message") or {}
        return msg.get("content") or choice.get("text") or ""
    return result.get("content") or ""


def is_degenerate(text):
    """Detect repetition loops: a short period repeated many times at
    the tail of the output. Cheap heuristic, tuned for coder models."""
    if not text or len(text) < 120:
        return False
    t = "".join(text.lower().split())
    for period in range(4, 65):
        reps = len(t) // period
        if reps < 5:
            break
        unit = t[-period:]
        tail = t[-(period * min(reps, 8)):]
        if unit * (len(tail) // period) == tail:
            return True
    return False


# ---------------------------------------------------------------- stream
def _sse_frames(resp):
    """Yield normalized data frames from an OpenAI-ish SSE stream."""
    for raw in resp.iter_lines(decode_unicode=True):
        if not raw or not raw.startswith("data: "):
            continue
        payload = raw[len("data: "):]
        if payload.strip() == "[DONE]":
            break
        try:
            obj = json.loads(payload)
        except ValueError:
            continue
        choices = obj.get("choices")
        if choices:
            choice = choices[0] or {}
            msg = choice.get("message") or {}
            delta = choice.get("delta") or {}
            text = (msg.get("content") or delta.get("content")
                    or choice.get("text") or "")
        else:
            text = obj.get("content") or ""
        if text:
            yield text


def stream_provider(provider_model, prompt, payload_base=None):
    """SSE generator for external providers (openai-style streaming;
    anthropic/gemini fall back to single-frame emit)."""
    pname, pcfg, pmodel = provider_model
    payload = dict(payload_base or {})
    started = time.monotonic()
    tokens = 0
    yield _sse_retry(3000)
    try:
        if pcfg.get("style") == "openai":
            url, headers, body = build_request(
                pname, pcfg, pmodel, prompt,
                payload.get("max_tokens", 2048),
                payload.get("temperature", 0.2), stream=True)
            r = requests.post(url, headers=headers, json=body,
                              stream=True, timeout=TIMEOUT)
            r.raise_for_status()
            yield f'data: {json.dumps({"model": f"{pname}/{pmodel}"})}\n\n'
            for text in _sse_frames(r):
                tokens += len(text.split())
                yield f'data: {json.dumps({"content": text})}\n\n'
        else:
            result = call_provider(pname, pcfg, pmodel, prompt,
                                   payload.get("max_tokens", 2048),
                                   payload.get("temperature", 0.2),
                                   timeout=TIMEOUT)
            yield f'data: {json.dumps({"model": f"{pname}/{pmodel}"})}\n\n'
            yield f'data: {json.dumps({"content": result["content"]})}\n\n'
            tokens = len(result["content"].split())
        metrics_model(f"{pname}/{pmodel}")
        metrics_latency(int((time.monotonic() - started) * 1000))
        latency_ms = int((time.monotonic() - started) * 1000)
        yield f'data: {json.dumps({"event": "completion", "model": f"{pname}/{pmodel}", "task_type": "provider", "tokens": tokens, "latency_ms": latency_ms})}\n\n'
        # Prometheus
        reg, helpers = get_registry()
        if helpers is not None:
            helpers["model_calls_total"].labels(model=f"{pname}/{pmodel}").inc()
            helpers["model_latency_seconds"].labels(model=f"{pname}/{pmodel}").observe(
                (time.monotonic() - started))
        yield "data: [DONE]\n\n"
    except Exception as exc:
        yield f'data: {json.dumps({"error": str(exc)})}\n\n'
        yield "data: [DONE]\n\n"


def stream_route(prompt, task_type, agent, payload_base=None):
    """SSE generator: picks the primary model for the task and streams
    normalized frames: data: {"content": "..."} ... data: [DONE]."""
    base = dict(payload_base or {})
    payload = {
        "prompt": prompt,
        "max_tokens": base.get("max_tokens", 2048),
        "temperature": base.get("temperature", 0.2),
    }
    if MOCK_LLM:
        tokens = 0
        yield _sse_retry(3000)
        yield f'data: {json.dumps({"model": "mock-model", "task_type": task_type})}\n\n'
        for word in mock_completion(payload)["content"].split(" ", 24):
            yield f'data: {json.dumps({"content": word + " "})}\n\n'
        yield "data: [DONE]\n\n"
        return

    from models import MODEL_REGISTRY
    started = time.monotonic()
    tokens = 0
    yield _sse_retry(3000)
    for candidate in select_chain(task_type, agent):
        model_meta = MODEL_REGISTRY[candidate]
        endpoint = model_meta["endpoint"]
        try:
            stream_payload = dict(payload, stream=True)
            floor = model_meta.get("min_temperature")
            if floor is not None:
                stream_payload["temperature"] = max(
                    float(stream_payload.get("temperature", 0.2)),
                    float(floor))
            r = requests.post(endpoint, json=stream_payload,
                              stream=True, timeout=TIMEOUT)
            r.raise_for_status()
            first = True
            for text in _sse_frames(r):
                tokens += len(text.split())
                if first:
                    yield f'data: {json.dumps({"model": MODEL_REGISTRY[candidate]["name"], "task_type": task_type})}\n\n'
                    first = False
                yield f'data: {json.dumps({"content": text})}\n\n'
            if first:
                continue  # empty stream from this backend -> try next
            metrics_model(candidate)
            metrics_latency(int((time.monotonic() - started) * 1000))
            latency_ms = int((time.monotonic() - started) * 1000)
            yield f'data: {json.dumps({"event": "completion", "model": MODEL_REGISTRY[candidate]["name"], "task_type": task_type, "tokens": tokens, "latency_ms": latency_ms})}\n\n'
            reg, helpers = get_registry()
            if helpers is not None:
                helpers["model_calls_total"].labels(model=candidate).inc()
                helpers["model_latency_seconds"].labels(model=candidate).observe(
                    (time.monotonic() - started))
            yield "data: [DONE]\n\n"
            return
        except Exception:
            continue
    # provider fallback tail
    for fid in fallback_models():
        fname, fmodel = fid.split("/", 1)
        fcfg = load_providers()[fname]
        try:
            result = call_provider(fname, fcfg, fmodel, prompt,
                                   payload.get("max_tokens", 2048),
                                   payload.get("temperature", 0.2),
                                   timeout=TIMEOUT)
            yield f'data: {json.dumps({"model": fid})}\n\n'
            yield f'data: {json.dumps({"content": result["content"]})}\n\n'
            metrics_model(fid)
            yield "data: [DONE]\n\n"
            return
        except Exception:
            continue
    yield f'data: {json.dumps({"error": "all backends failed"})}\n\n'
    yield "data: [DONE]\n\n"


# ---------------------------------------------------------------- routes
def _endpoint_pool(candidate: str):
    """Return ordered list of endpoint URLs for *candidate*.

    When multiple parallel instances exist (e.g. _llama_bases), all are
    included so the load balancer can spread traffic across them.
    """
    from models import MODEL_REGISTRY, _llama_bases
    meta = MODEL_REGISTRY.get(candidate)
    if meta is None:
        return []
    base = meta["endpoint"]
    # Collect all bases that share this model's endpoint prefix
    pool = []
    seen = set()
    for lb in _llama_bases:
        ep = f"{lb.rstrip('/')}/completion"
        if ep not in seen:
            seen.add(ep)
            pool.append(ep)
    if base not in seen:
        pool.append(base)
    return pool


def _try_candidate(candidate, payload, stream=False):
    """Attempt one candidate model across its endpoint pool.

    Returns (result_or_None, model_used_or_None, error_or_None).
    On success records a load-balancer success; on failure records a
    failure and returns the last error so the caller can fall through.
    """
    from models import MODEL_REGISTRY
    pool = _endpoint_pool(candidate)
    if not pool:
        return None, None, "no endpoints"
    lb_key = pick_backend(pool)
    model = MODEL_REGISTRY[candidate]
    call_payload = dict(payload)
    floor = model.get("min_temperature")
    if floor is not None:
        call_payload["temperature"] = max(
            float(call_payload.get("temperature", 0.2)), float(floor))
    try:
        connection_start(lb_key)
        if stream:
            r = requests.post(lb_key, json=call_payload, stream=True,
                              timeout=TIMEOUT)
            r.raise_for_status()
            # caller consumes the stream directly; record on completion
            return r, f"{candidate}@{lb_key}", None
        r = requests.post(lb_key, json=call_payload, timeout=TIMEOUT)
        r.raise_for_status()
        record_success(lb_key)
        return r.json(), f"{candidate}@{lb_key}", None
    except Exception as exc:
        record_failure(lb_key)
        return None, None, str(exc)
@app.route("/health")
def health():
    return jsonify({"status": "ok", "mock": MOCK_LLM})


@app.route("/models")
def models():
    from models import MODEL_REGISTRY, ConfidenceScorer
    scorer = ConfidenceScorer()
    out = {}
    for key, m in MODEL_REGISTRY.items():
        scores = {
            tt: scorer.score(key, tt)
            for tt in ["full_project", "refactor", "analysis", "general_code"]
        }
        out[key] = {
            "name": m["name"],
            "role": m["role"],
            "strengths": m["strengths"],
            "endpoint": m["endpoint"],
            "confidence": scores,
        }
    for name, cfg in load_providers().items():
        if not cfg.get("enabled"):
            continue
        keyed = is_keyed(name, cfg)
        for m in cfg.get("models", []):
            out[f"{name}/{m}"] = {
                "name": f"{cfg.get('description', name)} - {m}",
                "role": f"provider:{name}",
                "strengths": ["external"],
                "endpoint": cfg.get("base_url", ""),
                "keyed": keyed,
                "confidence": {
                    tt: 0.5 for tt in [
                        "full_project", "refactor", "analysis", "general_code"
                    ]
                },
            }
    return jsonify(out)


@app.route("/providers")
def providers():
    rows = []
    for name, cfg in load_providers().items():
        rows.append({
            "name": name,
            "style": cfg.get("style", "openai"),
            "base_url": cfg.get("base_url", ""),
            "description": cfg.get("description", ""),
            "models": cfg.get("models", []),
            "enabled": bool(cfg.get("enabled")),
            "keyed": is_keyed(name, cfg),
            "fallback": bool(cfg.get("fallback")),
            "key_env": cfg.get("key_env"),
        })
    return jsonify({"providers": rows})


@app.route("/router/load-balancers")
def lb_load_balancers():
    """Show current load-balancer state for all registered backends."""
    from models import MODEL_REGISTRY, _llama_bases
    rows = []
    endpoints_by_key: dict = {}
    for key, meta in MODEL_REGISTRY.items():
        ep = meta.get("endpoint", "")
        endpoints_by_key.setdefault(ep, []).append(key)
    # also include hot-shard bases
    for base in _llama_bases:
        ep = f"{base}/completion"
        endpoints_by_key.setdefault(ep, []).append(f"hot-shard:{base}")
    for ep, keys in endpoints_by_key.items():
        state = get_state(ep)
        rows.append({
            "endpoint": ep,
            "model_keys": keys,
            **state,
        })
    return jsonify({"algorithm": LB_ALGO,
                    "failure_threshold": FAILURE_THRESHOLD,
                    "recovery_timeout_s": RECOVERY_TIMEOUT_S,
                    "backends": rows})


@app.route("/api/router/lb-stats")
def lb_stats():
    """Compact LB stats for the dashboard."""
    return jsonify({"algorithm": LB_ALGO,
                    "failure_threshold": FAILURE_THRESHOLD,
                    "recovery_timeout_s": RECOVERY_TIMEOUT_S,
                    "backends": all_state()})


@app.route("/metrics")
def metrics():
    # Prometheus scrapes with Accept: text/plain; version=0.0.4; charset=utf-8
    # all other clients get legacy JSON for backward compatibility
    accept = request.headers.get("Accept", "")
    prom_text = render_metrics()
    if prom_text is not None and "text/plain" in accept:
        from flask import Response
        return Response(prom_text, mimetype="text/plain; version=0.0.4; charset=utf-8")
    with _METRICS_LOCK:
        snap = dict(METRICS)
        snap["by_task"] = dict(METRICS["by_task"])
        snap["by_model"] = dict(METRICS["by_model"])
    if snap["latency_count"]:
        snap["latency_avg_ms"] = round(
            snap["latency_sum_ms"] / snap["latency_count"], 1)
    else:
        snap["latency_avg_ms"] = 0
    snap.pop("latency_sum_ms", None)
    return jsonify(snap)


@app.route("/admin/model-switch", methods=["POST"])
def model_switch():
    """Dynamic LLAMA_MODEL_PATH hot-swap (requires restart of llama container).

    Body: {"model_path": "/models/Other-Q4_K_M.gguf"}
    Returns 202 with restart instruction; actual swap is env-driven.
    """
    data = request.get_json(silent=True) or {}
    path = data.get("model_path", "").strip()
    if not path:
        return jsonify({"error": "model_path required"}), 400
    # validate path is inside /models to avoid traversal
    if ".." in path or not path.startswith("/models/"):
        return jsonify({"error": "path must be under /models/"}), 400
    return jsonify({"status": "accepted", "model_path": path,
                    "hint": "set LLAMA_MODEL_PATH and restart llama: "
                            "docker compose restart llama"}), 202


@app.route("/admin/hot-models")
def hot_models():
    from models import _llama_bases
    out = []
    for base in _llama_bases:
        try:
            import requests as _r
            r = _r.get(f"{base}/health", timeout=2)
            out.append({"base": base, "healthy": r.status_code == 200})
        except Exception:
            out.append({"base": base, "healthy": False})
    return jsonify({"shards": out})


@app.route("/api/traces")
def api_traces():
    """List recent traces with latency, model, and status info."""
    limit = request.args.get("limit", 50, type=int)
    if otel is not None:
        traces = otel.get_recent_traces(limit=limit)
    else:
        traces = []
    return jsonify({"traces": traces})


@app.route("/route", methods=["POST"])
def route():
    data = request.get_json(silent=True) or {}
    prompt = data.get("prompt", "")
    agent = data.get("agent")  # optional per-agent model override hint
    if not prompt:
        return jsonify({"error": "prompt is required"}), 400

    metrics_incr("requests_total")
    task_type, confidence = classify_task(prompt)
    metrics_task(task_type)
    # Prometheus: task distribution + confidence
    reg, ph = get_registry()
    if ph is not None:
        ph["task_type_total"].labels(task_type=task_type).inc()
        ph["confidence_bucket"].labels(task_type=task_type).observe(confidence)

    # Tracing for route endpoint
    trace_id = otel.make_trace_id() if otel else "noop"
    span = None
    if otel:
        span = otel.route_span(trace_id, task_type, confidence).__enter__()

    explicit = data.get("model") or ""
    provider_model = None
    if "/" in explicit:
        pname, pmodel = explicit.split("/", 1)
        pcfg = load_providers().get(pname)
        if pcfg and pcfg.get("enabled") and is_keyed(pname, pcfg):
            provider_model = (pname, pcfg, pmodel)

    if data.get("stream"):
        headers = _send_sse_headers({})
        if provider_model:
            return Response(stream_with_context(
                stream_provider(provider_model, prompt,
                                payload_base=data)),
                mimetype="text/event-stream",
                headers=headers)
        return Response(stream_with_context(
            stream_route(prompt, task_type, agent, payload_base=data)),
            mimetype="text/event-stream",
            headers=headers)
        if span:
            span.end()
            if otel:
                otel.record_trace(trace_id, task_type, None,
                                  0, "streaming", confidence)

    model_used = None
    elapsed_ms = 0
    status = "ok"
    error = None

    if provider_model is not None:
        pname, pcfg, pmodel = provider_model
        started = time.monotonic()
        try:
            result = call_provider(pname, pcfg, pmodel, prompt,
                                   data.get("max_tokens", 2048),
                                   data.get("temperature", 0.2),
                                   timeout=TIMEOUT)
        except Exception as exc:
            metrics_incr("errors_total")
            error = str(exc)
            status = "error"
            elapsed_ms = int((time.monotonic() - started) * 1000)
            if span:
                otel.tag_status(span, 502)
                otel.tag_latency(span, elapsed_ms)
                span.end()
            if otel:
                otel.record_trace(trace_id, task_type, None,
                                  elapsed_ms, "error", confidence)
            return jsonify({"error": error, "provider": pname,
                            "task_type": task_type, "trace_id": trace_id}), 502
        elapsed_ms = int((time.monotonic() - started) * 1000)
        metrics_latency(elapsed_ms)
        metrics_model(f"{pname}/{pmodel}")
        if ph is not None:
            ph["model_calls_total"].labels(model=f"{pname}/{pmodel}").inc()
            ph["model_latency_seconds"].labels(model=f"{pname}/{pmodel}").observe(
                elapsed_ms / 1000.0)
        model_used = f"{pname}/{pmodel}"
        if span:
            otel.tag_model(span, model_used)
            otel.tag_status(span, 200)
            otel.tag_latency(span, elapsed_ms)
            span.end()
        if otel:
            otel.record_trace(trace_id, task_type, model_used,
                              elapsed_ms, "ok", confidence)
        resp = jsonify({"model_used": model_used,
                        "task_type": task_type,
                        "confidence": confidence,
                        "elapsed_ms": elapsed_ms,
                        "response": result,
                        "trace_id": trace_id})
        resp.headers["X-Cache"] = "PASS"   # external calls not cached
        return resp

    cache_prompt = data.get("model") or ""
    cached = cache_get(prompt, model="")
    if cached is not None:
        metrics_incr("cache_hits")
        elapsed_ms = 0
        if span:
            otel.tag_status(span, 200)
            otel.tag_latency(span, elapsed_ms)
            span.end()
        if otel:
            otel.record_trace(trace_id, task_type, "cache",
                              elapsed_ms, "cache_hit", confidence)
        resp = jsonify({**cached, "trace_id": cached.get("trace_id", trace_id)})
        resp.headers["X-Cache"] = "HIT"
        return resp

    payload = {
        "prompt": prompt,
        "max_tokens": data.get("max_tokens", 2048),
        "temperature": data.get("temperature", 0.2),
    }

    started = time.monotonic()
    chain = select_chain(task_type, agent)
    if MOCK_LLM:
        result = mock_completion(payload)
        model_used = chain[0]
        error = None
        degenerate_retries = 0
    else:
        import requests
        from models import MODEL_REGISTRY
        result = None
        model_used = None
        model_used_prev = None
        error = None
        degenerate_retries = 0
        best_effort = None          # (payload, name) if all answers loop
        candidates = list(chain)
        while candidates:
            candidate = candidates.pop(0)
            attempt, model_used, error = _try_candidate(
                candidate, payload)
            if attempt is None:
                model_used_prev = candidate
                continue
            if is_degenerate(_text_of(attempt)) and candidates \
                    and best_effort is None:
                # looks like a repetition loop — try next backend,
                # but keep this as a last-resort answer
                best_effort = (attempt, model_used)
                metrics_incr("degenerate_skips")
                degenerate_retries += 1
                continue
            result = attempt
            metrics_model(candidate)
            if ph is not None:
                ph["model_calls_total"].labels(model=candidate).inc()
            break
        if result is None and best_effort is not None:
            result, model_used = best_effort

        # parallel hot model: try secondary llama shard
        if result is None:
            try:
                from models import _llama_bases
                hot_payload = dict(payload)
                first = MODEL_REGISTRY.get(candidates[-1]) if candidates else None
                if first:
                    floor = first.get("min_temperature")
                    if floor is not None:
                        hot_payload["temperature"] = max(
                            float(hot_payload.get("temperature", 0.2)),
                            float(floor))
                for base in _llama_bases[1:]:
                    try:
                        r = requests.post(f"{base}/completion",
                                          json=hot_payload, timeout=TIMEOUT)
                        r.raise_for_status()
                        result, model_used = r.json(), f"hot-shard:{base}"
                        metrics_model("hot-shard")
                        if ph is not None:
                            ph["model_calls_total"].labels(model="hot-shard").inc()
                        break
                    except Exception:
                        continue
            except Exception:
                pass

        # provider fallback tail: keyed providers flagged fallback=true
        if result is None:
            for fid in fallback_models():
                fname, fmodel = fid.split("/", 1)
                fcfg = load_providers()[fname]
                try:
                    result = call_provider(
                        fname, fcfg, fmodel, prompt,
                        payload.get("max_tokens", 2048),
                        payload.get("temperature", 0.2), timeout=TIMEOUT)
                    model_used = fid
                    metrics_model(fid)
                    if ph is not None:
                        ph["model_calls_total"].labels(model=fid).inc()
                        ph["model_latency_seconds"].labels(model=fid).observe(
                            elapsed_ms / 1000.0)
                        if model_used_prev is not None:
                            ph["fallback_count"].labels(
                                from_model=model_used_prev, to_model=fid).inc()
                    break
                except Exception as exc:
                    error = str(exc)
                    continue

        if result is None:
            metrics_incr("errors_total")
            status = "error"
            elapsed_ms = int((time.monotonic() - started) * 1000)
            if span:
                otel.tag_status(span, 502)
                otel.tag_latency(span, elapsed_ms)
                span.end()
            if otel:
                otel.record_trace(trace_id, task_type, None,
                                  elapsed_ms, "error", confidence)
            return jsonify({
                "error": error or "all backends failed",
                "task_type": task_type,
                "trace_id": trace_id,
            }), 502

    elapsed_ms = int((time.monotonic() - started) * 1000)
    metrics_latency(elapsed_ms)
    if ph is not None and model_used is not None:
        ph["model_calls_total"].labels(model=model_used).inc()
        ph["model_latency_seconds"].labels(model=model_used).observe(
            elapsed_ms / 1000.0)
    body = {
        "model_used": model_used,
        "task_type": task_type,
        "confidence": confidence,
        "elapsed_ms": elapsed_ms,
        "response": result,
        "trace_id": trace_id,
    }
    cache_put(prompt, "", body)
    resp = jsonify(body)
    resp.headers["X-Cache"] = "MISS"
    if degenerate_retries:
        resp.headers["X-Coherence-Retries"] = str(degenerate_retries)
    if span:
        otel.tag_model(span, model_used)
        otel.tag_status(span, 200 if status == "ok" else 502)
        otel.tag_latency(span, elapsed_ms)
        span.end()
    if otel:
        otel.record_trace(trace_id, task_type, model_used,
                          elapsed_ms, status, confidence)
    return resp


@app.route("/route/stream", methods=["POST"])
def route_stream():
    """Dedicated SSE streaming endpoint. Equivalent to POST /route with
    stream=true but with a stable URL for streaming clients."""
    data = request.get_json(silent=True) or {}
    data["stream"] = True
    prompt = data.get("prompt", "")
    agent = data.get("agent")
    if not prompt:
        return jsonify({"error": "prompt is required"}), 400

    metrics_incr("requests_total")
    task_type, confidence = classify_task(prompt)
    metrics_task(task_type)

    # Tracing for stream endpoint
    trace_id = otel.make_trace_id() if otel else "noop"
    span = None
    if otel:
        span = otel.route_span(trace_id, task_type, confidence).__enter__()

    explicit = data.get("model") or ""
    provider_model = None
    if "/" in explicit:
        pname, pmodel = explicit.split("/", 1)
        pcfg = load_providers().get(pname)
        if pcfg and pcfg.get("enabled") and is_keyed(pname, pcfg):
            provider_model = (pname, pcfg, pmodel)

    def _wrap_stream(stream_gen):
        started = time.monotonic()
        model_set = False
        try:
            for frame in stream_gen:
                yield frame
                # Capture model from first model frame for tracing
                if not model_set:
                    try:
                        raw = frame.split("data: ", 1)[-1].strip()
                        obj = json.loads(raw)
                        if "model" in obj:
                            if otel:
                                otel.tag_model(span, obj["model"])
                            model_set = True
                    except (ValueError, IndexError):
                        pass
        finally:
            elapsed_ms = int((time.monotonic() - started) * 1000)
            if span:
                otel.tag_status(span, 200)
                otel.tag_latency(span, elapsed_ms)
                span.end()
            if otel:
                otel.record_trace(trace_id, task_type,
                                  "streaming", elapsed_ms, "ok", confidence)

    sse_headers = _send_sse_headers({})
    if provider_model:
        return Response(stream_with_context(
            _wrap_stream(stream_provider(provider_model, prompt, payload_base=data))),
            mimetype="text/event-stream",
            headers=sse_headers)

    return Response(stream_with_context(
        _wrap_stream(stream_route(prompt, task_type, agent, payload_base=data))),
        mimetype="text/event-stream",
        headers=sse_headers)


# ---------------------------------------------------------------- model performance
@app.route("/api/models/performance")
def api_models_performance():
    """Current per-model performance scores."""
    from models import MODEL_REGISTRY
    from performance import scorer
    out = {}
    for key in MODEL_REGISTRY:
        out[key] = scorer.score(key)
    # also include external providers
    for name, cfg in load_providers().items():
        if not cfg.get("enabled"):
            continue
        for m in cfg.get("models", []):
            mk = f"{name}/{m}"
            if mk not in out:
                out[mk] = scorer.score(mk)
    return jsonify(out)


@app.route("/api/models/rankings")
def api_models_rankings():
    """Models sorted by quality score descending."""
    from models import MODEL_REGISTRY
    from performance import scorer
    entries = []
    for key, meta in MODEL_REGISTRY.items():
        s = scorer.score(key)
        entries.append({
            "key": key,
            "name": meta.get("name", key),
            "role": meta.get("role", ""),
            **s,
        })
    for name, cfg in load_providers().items():
        if not cfg.get("enabled"):
            continue
        for m in cfg.get("models", []):
            mk = f"{name}/{m}"
            s = scorer.score(mk)
            entries.append({
                "key": mk,
                "name": f"{cfg.get('description', name)} - {m}",
                "role": f"provider:{name}",
                **s,
            })
    entries.sort(key=lambda e: (e.get("quality_score") or -1), reverse=True)
    return jsonify({"rankings": entries})


@app.route("/api/models/benchmark", methods=["POST"])
def api_models_benchmark():
    """Run benchmark against one or all registered models."""
    from models import MODEL_REGISTRY
    from benchmark import run_benchmark, save_report
    data = request.get_json(silent=True) or {}
    target = data.get("model")  # None = all
    results = {}
    if target:
        if target not in MODEL_REGISTRY:
            return jsonify({"error": f"unknown model: {target}"}), 404
        models_to_run = {target: MODEL_REGISTRY[target]}
    else:
        models_to_run = MODEL_REGISTRY
    for key, meta in models_to_run.items():
        endpoint = meta.get("endpoint", "")
        if not endpoint:
            results[key] = {"error": "no endpoint configured"}
            continue
        r = run_benchmark(endpoint, meta.get("name", key))
        results[key] = r
        save_report(r)
    return jsonify({"results": results, "completed_at": time.strftime(
        "%Y-%m-%dT%H:%M:%SZ", time.gmtime())})


@app.route("/api/models/benchmark/report")
def api_models_benchmark_report():
    """Return the last saved benchmark report."""
    from benchmark import load_report
    return jsonify(load_report())


# ── GODMODE & Catalog endpoints ──────────────────────────────────
@app.route("/api/godmode", methods=["GET"])
def api_godmode_status():
    """Check GODMODE status (delegates to agents/godmode.py)."""
    try:
        import importlib.util as _iu
        import pathlib as _pl
        p = _pl.Path(__file__).parent.parent / "agents" / "godmode.py"
        spec = _iu.spec_from_file_location("gm_mod", p)
        mod = _iu.module_from_spec(spec)
        spec.loader.exec_module(mod)
        state = mod._load_state()
        return jsonify({"enabled": state.get("enabled", False),
                        "state": state})
    except Exception as e:
        logging.getLogger(__name__).exception("API error")
        return jsonify({"enabled": False, "error": "An internal error occurred"})


@app.route("/api/godmode/toggle", methods=["POST"])
def api_godmode_toggle():
    """Toggle GODMODE for agent or model."""
    try:
        import importlib.util as _iu
        import pathlib as _pl
        p = _pl.Path(__file__).parent.parent / "agents" / "godmode.py"
        spec = _iu.spec_from_file_location("gm_mod", p)
        mod = _iu.module_from_spec(spec)
        spec.loader.exec_module(mod)
        data = request.get_json(silent=True) or {}
        result = mod.toggle_godmode(
            agent=data.get("agent", ""),
            model=data.get("model", ""),
            enable=data.get("enable", True),
        )
        return jsonify(result)
    except Exception as e:
        logging.getLogger(__name__).exception("API error")
        return jsonify({"error": "An internal error occurred"})


@app.route("/api/godmode/campaign", methods=["POST"])
def api_godmode_campaign():
    """Set GODMODE campaign."""
    try:
        import importlib.util as _iu
        import pathlib as _pl
        p = _pl.Path(__file__).parent.parent / "agents" / "godmode.py"
        spec = _iu.spec_from_file_location("gm_mod", p)
        mod = _iu.module_from_spec(spec)
        spec.loader.exec_module(mod)
        data = request.get_json(silent=True) or {}
        result = mod.set_campaign(data.get("name", ""), data.get("enable", True))
        return jsonify(result)
    except Exception as e:
        logging.getLogger(__name__).exception("API error")
        return jsonify({"error": "An internal error occurred"})


@app.route("/api/catalog", methods=["GET"])
def api_catalog_summary():
    """Unified catalog summary."""
    try:
        import importlib.util as _iu
        import pathlib as _pl
        p = _pl.Path(__file__).parent.parent / "skills" / "catalog_api.py"
        spec = _iu.spec_from_file_location("catalog_mod", p)
        mod = _iu.module_from_spec(spec)
        spec.loader.exec_module(mod)
        return jsonify({"summary": mod.get_stats(), "timestamp": int(time.time())})
    except Exception as e:
        logging.getLogger(__name__).exception("API error")
        return jsonify({"error": "An internal error occurred"})


@app.route("/api/catalog/dropdowns", methods=["GET"])
def api_catalog_dropdowns():
    """Dropdown-ready catalog data for dashboard."""
    try:
        import importlib.util as _iu
        import pathlib as _pl
        p = _pl.Path(__file__).parent.parent / "skills" / "catalog_api.py"
        spec = _iu.spec_from_file_location("catalog_mod", p)
        mod = _iu.module_from_spec(spec)
        spec.loader.exec_module(mod)
        return jsonify(mod.get_dropdowns())
    except Exception as e:
        logging.getLogger(__name__).exception("API error")
        return jsonify({"error": "An internal error occurred"})


@app.route("/api/catalog/auto-install", methods=["POST"])
def api_catalog_auto_install():
    """Auto-install missing catalog items."""
    try:
        import importlib.util as _iu
        import pathlib as _pl
        p = _pl.Path(__file__).parent.parent / "skills" / "catalog_api.py"
        spec = _iu.spec_from_file_location("catalog_mod", p)
        mod = _iu.module_from_spec(spec)
        spec.loader.exec_module(mod)
        data = request.get_json(silent=True) or {}
        return jsonify(mod.auto_install(missing_only=data.get("missing_only", True)))
    except Exception as e:
        logging.getLogger(__name__).exception("API error")
        return jsonify({"error": "An internal error occurred"})


@app.route("/api/mcps", methods=["GET"])
def api_mcps_list():
    """List cataloged MCPs."""
    try:
        import importlib.util as _iu
        import pathlib as _pl
        p = _pl.Path(__file__).parent.parent / "mcp" / "catalog_api.py"
        spec = _iu.spec_from_file_location("mcp_catalog_mod", p)
        mod = _iu.module_from_spec(spec)
        spec.loader.exec_module(mod)
        category = request.args.get("category")
        return jsonify({"mcps": mod.list_mcps(category), "total": len(mod.list_mcps(category))})
    except Exception as e:
        logging.getLogger(__name__).exception("API error")
        return jsonify({"error": "An internal error occurred"})


@app.route("/api/mcps/install", methods=["POST"])
def api_mcp_install():
    """Install an MCP from catalog."""
    try:
        import importlib.util as _iu
        import pathlib as _pl
        p = _pl.Path(__file__).parent.parent / "mcp" / "catalog_api.py"
        spec = _iu.spec_from_file_location("mcp_catalog_mod", p)
        mod = _iu.module_from_spec(spec)
        spec.loader.exec_module(mod)
        data = request.get_json(silent=True) or {}
        return jsonify(mod.install_mcp(data.get("id", ""), data.get("config")))
    except Exception as e:
        logging.getLogger(__name__).exception("API error")
        return jsonify({"error": "An internal error occurred"})


@app.route("/api/providers", methods=["GET"])
def api_providers_list():
    """List all configured providers."""
    providers = load_providers()
    out = []
    for name, cfg in providers.items():
        out.append({"id": name, **cfg, "keyed": is_keyed(name, cfg)})
    return jsonify({"providers": out, "total": len(out)})


if __name__ == "__main__":
    app.run(host="0.0.0.0",
            port=int(os.environ.get("ROUTER_PORT",
                                    str(CFG.get("port", 8010)))),
            threaded=True)
