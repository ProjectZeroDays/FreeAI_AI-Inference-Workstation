"""FreeAI Router middleware: auth, rate limiting, response caching."""
import hashlib
import json
import os
import time
import threading
from collections import OrderedDict

from flask import request, jsonify, Response

from settings import load_config

CFG = load_config().get("router", {})

# ------------------------------------------------------------------ rate limit
_RATE_CAPACITY = int(CFG.get("rate_limit_capacity", 100))
_RATE_REFILL = float(CFG.get("rate_limit_refill_per_min", 100)) / 60.0

_BUCKETS: dict = {}
_RATE_LOCK = threading.Lock()


class RateLimiter:
    """Per-IP token bucket rate limiter."""

    def __init__(self, capacity: int = _RATE_CAPACITY,
                 refill_per_min: float = _RATE_REFILL):
        self.capacity = capacity
        self.refill_per_min = refill_per_min

    def allow(self, client_id: str) -> bool:
        now = time.monotonic()
        with _RATE_LOCK:
            tokens, last = _BUCKETS.get(client_id, (self.capacity, now))
            tokens = min(self.capacity,
                         tokens + (now - last) * self.refill_per_min)
            if tokens < 1:
                _BUCKETS[client_id] = (tokens, now)
                return False
            _BUCKETS[client_id] = (tokens - 1, now)
            return True


# ----------------------------------------------------------- api key loading
def _load_api_keys() -> list:
    """Load allowed API keys from config/api-keys.json.

    Returns an empty list when the file is missing, empty, or invalid —
    which means auth is skipped (opt-in).
    """
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    path = os.path.join(root, "config", "api-keys.json")
    try:
        with open(path) as f:
            data = json.load(f)
        if isinstance(data, list):
            return [str(k).strip() for k in data if k]
        if isinstance(data, dict):
            return [str(v).strip() for v in data.get("keys", []) if v]
    except (OSError, ValueError, TypeError):
        pass
    return []


_API_KEYS = _load_api_keys()
_AUTH_LOCK = threading.Lock()


class AuthMiddleware:
    """Check X-API-Key header against config/api-keys.json.

    Skips auth for /health, /models, /docs endpoints and when no keys
    are configured (opt-in behaviour, preserves existing test behaviour).
    """

    def check(self):
        skip_paths = {"/health", "/models", "/docs"}
        if request.path in skip_paths:
            return None

        global _API_KEYS
        with _AUTH_LOCK:
            keys = _API_KEYS

        if not keys:
            return None

        key = request.headers.get("X-API-Key", "").strip()
        if key not in keys:
            return jsonify({"error": "unauthorized"}), 401
        return None


# ------------------------------------------------------------------ cache
_CACHE_ENABLED = bool(CFG.get("cache_enabled", True))
_CACHE_SIZE = int(CFG.get("cache_size", 128))
_CACHE_TTL = int(CFG.get("cache_ttl_s", 60))

_CACHE: OrderedDict = OrderedDict()
_CACHE_LOCK = threading.Lock()


class CacheMiddleware:
    """LRU response cache with TTL (max 128 entries, 60s TTL).

    Keys are SHA-256 hashes of (prompt + model).  Expired entries are
    evicted lazily on access.
    """

    def __init__(self, max_size: int = _CACHE_SIZE, ttl: int = _CACHE_TTL):
        self.max_size = max_size
        self.ttl = ttl

    def _key(self, prompt: str, model: str = "") -> str:
        raw = f"{prompt}:{model}"
        return hashlib.sha256(raw.encode()).hexdigest()

    def get(self, prompt: str, model: str = ""):
        if not _CACHE_ENABLED:
            return None
        k = self._key(prompt, model)
        with _CACHE_LOCK:
            if k in _CACHE:
                entry = _CACHE[k]
                if time.monotonic() - entry["ts"] > self.ttl:
                    del _CACHE[k]
                    return None
                _CACHE.move_to_end(k)
                return entry["value"]
        return None

    def put(self, prompt: str, model: str, value):
        if not _CACHE_ENABLED:
            return
        k = self._key(prompt, model)
        with _CACHE_LOCK:
            _CACHE[k] = {"value": value, "ts": time.monotonic()}
            _CACHE.move_to_end(k)
            while len(_CACHE) > self.max_size:
                _CACHE.popitem(last=False)


# Re-export singletons for backward compatibility in router.py
rate_limiter = RateLimiter()
auth_middleware = AuthMiddleware()
cache_middleware = CacheMiddleware()
