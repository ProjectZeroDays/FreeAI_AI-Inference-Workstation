#!/usr/bin/env python3
"""FreeAI Router — task classification + fallback routing.

Features:
- Task classification with confidence score
- Fallback chain across the model roster
- Optional API-key auth (X-API-Key header when ROUTER_API_KEY is set)
- Per-client token-bucket rate limiting
- LRU response cache for repeated prompts
- Prometheus-style /metrics snapshot
- SSE streaming passthrough
- Mock backend mode (MOCK_LLM=1) for dev/CI without a GPU
"""
import hashlib
import json
import os
import threading
import time
from collections import OrderedDict

import requests
from flask import Flask, Response, request, jsonify, stream_with_context

from classifier import classify_task
from switcher import select_chain
from settings import load_config
from providers import (load_providers, is_keyed, keyed_providers,
                       fallback_models, call_provider, parse_response,
                       build_request)

CFG = load_config().get("router", {})

API_KEY = CFG.get("api_key", "")
RATE_CAPACITY = int(CFG.get("rate_limit_capacity", 60))
RATE_REFILL = float(CFG.get("rate_limit_refill_per_min", 60)) / 60.0
CACHE_ENABLED = bool(CFG.get("cache_enabled", True))
CACHE_SIZE = int(CFG.get("cache_size", 128))
TIMEOUT = int(CFG.get("backend_timeout_s", 300))
MOCK_LLM = bool(CFG.get("mock_llm", False))

app = Flask(__name__)

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


# ------------------------------------------------------------- rate limit
_BUCKETS = {}
_RATE_LOCK = threading.Lock()


def allow_request(client_id):
    now = time.monotonic()
    with _RATE_LOCK:
        tokens, last = _BUCKETS.get(client_id, (RATE_CAPACITY, now))
        tokens = min(RATE_CAPACITY, tokens + (now - last) * RATE_REFILL)
        if tokens < 1:
            _BUCKETS[client_id] = (tokens, now)
            return False
        _BUCKETS[client_id] = (tokens - 1, now)
        return True


# ------------------------------------------------------------------ cache
_CACHE = OrderedDict()
_CACHE_LOCK = threading.Lock()


def cache_get(key):
    if not CACHE_ENABLED:
        return None
    with _CACHE_LOCK:
        if key in _CACHE:
            _CACHE.move_to_end(key)
            return _CACHE[key]
    return None


def cache_put(key, value):
    if not CACHE_ENABLED:
        return
    with _CACHE_LOCK:
        _CACHE[key] = value
        _CACHE.move_to_end(key)
        while len(_CACHE) > CACHE_SIZE:
            _CACHE.popitem(last=False)


# ------------------------------------------------------------------- auth
@app.before_request
def guard():
    if request.path == "/health":
        return None
    # Fail-secure: reject requests when API_KEY is not configured or empty
    if not API_KEY:
        return jsonify({"error": "unauthorized - API key not configured"}), 401
    if request.headers.get("X-API-Key") != API_KEY:
        return jsonify({"error": "unauthorized"}), 401
    if not allow_request(request.remote_addr or "unknown"):
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
                yield f'data: {json.dumps({"content": text})}\n\n'
        else:
            result = call_provider(pname, pcfg, pmodel, prompt,
                                   payload.get("max_tokens", 2048),
                                   payload.get("temperature", 0.2),
                                   timeout=TIMEOUT)
            yield f'data: {json.dumps({"model": f"{pname}/{pmodel}"})}\n\n'
            yield f'data: {json.dumps({"content": result["content"]})}\n\n'
        metrics_model(f"{pname}/{pmodel}")
        metrics_latency(int((time.monotonic() - started) * 1000))
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
        yield f'data: {json.dumps({"model": "mock-model", "task_type": task_type})}\n\n'
        for word in mock_completion(payload)["content"].split(" ", 24):
            yield f'data: {json.dumps({"content": word + " "})}\n\n'
        yield "data: [DONE]\n\n"
        return

    from models import MODEL_REGISTRY
    started = time.monotonic()
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
                if first:
                    yield f'data: {json.dumps({"model": MODEL_REGISTRY[candidate]["name"], "task_type": task_type})}\n\n'
                    first = False
                yield f'data: {json.dumps({"content": text})}\n\n'
            if first:
                continue  # empty stream from this backend -> try next
            metrics_model(candidate)
            metrics_latency(int((time.monotonic() - started) * 1000))
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
@app.route("/health")
def health():
    return jsonify({"status": "ok", "mock": MOCK_LLM})


@app.route("/models")
def models():
    from models import MODEL_REGISTRY
    out = {
        key: {"name": m["name"], "role": m["role"],
              "strengths": m["strengths"], "endpoint": m["endpoint"]}
        for key, m in MODEL_REGISTRY.items()
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


@app.route("/metrics")
def metrics():
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

    # explicit external-model selection: "provider/model" wins over chain
    explicit = data.get("model") or ""
    provider_model = None
    if "/" in explicit:
        pname, pmodel = explicit.split("/", 1)
        pcfg = load_providers().get(pname)
        if pcfg and pcfg.get("enabled") and is_keyed(pname, pcfg):
            provider_model = (pname, pcfg, pmodel)

    if data.get("stream"):
        if provider_model:
            return Response(stream_with_context(
                stream_provider(provider_model, prompt,
                                payload_base=data)),
                mimetype="text/event-stream",
                headers={"Cache-Control": "no-cache",
                         "X-Accel-Buffering": "no"})
        return Response(stream_with_context(
            stream_route(prompt, task_type, agent, payload_base=data)),
            mimetype="text/event-stream",
            headers={"Cache-Control": "no-cache",
                     "X-Accel-Buffering": "no"})

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
            return jsonify({"error": str(exc), "provider": pname}), 502
        elapsed_ms = int((time.monotonic() - started) * 1000)
        metrics_latency(elapsed_ms)
        metrics_model(f"{pname}/{pmodel}")
        resp = jsonify({"model_used": f"{pname}/{pmodel}",
                        "task_type": task_type,
                        "confidence": confidence,
                        "elapsed_ms": elapsed_ms,
                        "response": result})
        resp.headers["X-Cache"] = "PASS"   # external calls not cached
        return resp

    cache_key = hashlib.sha256(
        f"{task_type}:{agent}:{prompt}".encode()).hexdigest()
    cached = cache_get(cache_key)
    if cached is not None:
        metrics_incr("cache_hits")
        resp = jsonify(cached)
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
        error = None
        degenerate_retries = 0
        best_effort = None          # (payload, name) if all answers loop
        candidates = list(chain)
        while candidates:
            candidate = candidates.pop(0)
            model = MODEL_REGISTRY[candidate]
            # reasoning models (e.g. Qwythos) need a temperature floor to
            # avoid greedy-decode repetition loops
            call_payload = dict(payload)
            floor = model.get("min_temperature")
            if floor is not None:
                call_payload["temperature"] = max(
                    float(call_payload.get("temperature", 0.2)), float(floor))
            try:
                r = requests.post(model["endpoint"], json=call_payload,
                                  timeout=TIMEOUT)
                r.raise_for_status()
                attempt = r.json()
                if is_degenerate(_text_of(attempt)) and candidates \
                        and best_effort is None:
                    # looks like a repetition loop — try next backend,
                    # but keep this as a last-resort answer
                    best_effort = (attempt, model["name"])
                    metrics_incr("degenerate_skips")
                    degenerate_retries += 1
                    continue
                result, model_used = attempt, model["name"]
                metrics_model(candidate)
                break
            except Exception as exc:
                error = str(exc)
                continue
        if result is None and best_effort is not None:
            result, model_used = best_effort

        # parallel hot model: try secondary llama shard
        if result is None:
            try:
                from models import _llama_bases
                for base in _llama_bases[1:]:
                    try:
                        r = requests.post(f"{base}/completion",
                                          json=call_payload, timeout=TIMEOUT)
                        r.raise_for_status()
                        result, model_used = r.json(), f"hot-shard:{base}"
                        metrics_model("hot-shard")
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
                    break
                except Exception as exc:
                    error = str(exc)
                    continue

        if result is None:
            metrics_incr("errors_total")
            return jsonify({
                "error": error or "all backends failed",
                "task_type": task_type,
            }), 502

    elapsed_ms = int((time.monotonic() - started) * 1000)
    metrics_latency(elapsed_ms)

    body = {
        "model_used": model_used,
        "task_type": task_type,
        "confidence": confidence,
        "elapsed_ms": elapsed_ms,
        "response": result,
    }
    cache_put(cache_key, body)
    resp = jsonify(body)
    resp.headers["X-Cache"] = "MISS"
    if degenerate_retries:
        resp.headers["X-Coherence-Retries"] = str(degenerate_retries)
    return resp


if __name__ == "__main__":
    app.run(host="0.0.0.0",
            port=int(os.environ.get("ROUTER_PORT",
                                    str(CFG.get("port", 8010)))),
            threaded=True)
