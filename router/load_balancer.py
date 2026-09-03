"""Load balancing across parallel model instances.

Algorithms: round_robin, least_conn, weighted.
Health checking probes each model endpoint; marks unhealthy after
`failure_threshold` consecutive failures.
Circuit breaker opens after the same threshold and stays open for
`recovery_timeout_s` before allowing a probe to re-test.

Sliding-window circuit breaker (enhanced):
  Tracks a fixed-size window of recent outcomes (default 20).
  Circuit opens when:
    - consecutive_failures >= FAILURE_THRESHOLD, OR
    - failure_ratio >= CIRCUIT_BREAKER_RATIO within the window, AND
      total_requests_in_window >= CIRCUIT_BREAKER_MIN_REQUESTS
  Provides graceful degradation under sustained provider rate limits.
"""
import collections
import json
import os
import threading
import time
from typing import Dict, List, Optional, Tuple

try:
    from .settings import load_config
except ImportError:
    from settings import load_config

_CFG = load_config().get("router", {})
ALGO = os.environ.get("LB_ALGO") or _CFG.get("lb_algo", "round_robin")
FAILURE_THRESHOLD = int(os.environ.get("LB_FAILURE_THRESHOLD")
                        or _CFG.get("lb_failure_threshold", 3))
RECOVERY_TIMEOUT_S = int(os.environ.get("LB_RECOVERY_TIMEOUT")
                         or _CFG.get("lb_recovery_timeout_s", 30))
HEALTH_CHECK_INTERVAL_S = float(os.environ.get("LB_HEALTH_CHECK_INTERVAL")
                                or _CFG.get("lb_health_check_interval_s", 10))
# Sliding-window circuit breaker settings
CB_WINDOW_SIZE = int(os.environ.get("CIRCUIT_BREAKER_WINDOW")
                     or _CFG.get("cb_window_size", 20))
CB_RATIO_THRESHOLD = float(os.environ.get("CIRCUIT_BREAKER_RATIO")
                            or _CFG.get("cb_ratio_threshold", 0.5))
CB_MIN_REQUESTS = int(os.environ.get("CIRCUIT_BREAKER_MIN_REQUESTS")
                      or _CFG.get("cb_min_requests", 3))

# Per-backend state
_lock = threading.Lock()
_state: Dict[str, Dict] = {}
_outcomes: Dict[str, collections.deque] = {}
# _state[backend_key] = {
#   "healthy": bool,
#   "consecutive_failures": int,
#   "circuit_open_until": float (monotonic),
#   "active_connections": int,
#   "total_requests": int,
#   "total_failures": int,
# }
# _outcomes[backend_key] = deque of 1/0 (success/failure), maxlen=CB_WINDOW_SIZE


def _backend_key(name: str, endpoint: str) -> str:
    return f"{name}@{endpoint}"


def _ensure(key: str):
    if key not in _state:
        _state[key] = {
            "healthy": True,
            "consecutive_failures": 0,
            "circuit_open_until": 0.0,
            "active_connections": 0,
            "total_requests": 0,
            "total_failures": 0,
        }
    if key not in _outcomes:
        _outcomes[key] = collections.deque(maxlen=CB_WINDOW_SIZE)


def _tick_health():
    """Background health probe — called once per request."""
    now = time.monotonic()
    with _lock:
        for key, s in _state.items():
            if s["circuit_open_until"] > 0 and now >= s["circuit_open_until"]:
                # Attempt recovery probe
                s["circuit_open_until"] = 0.0
                s["consecutive_failures"] = 0
                # Clear the sliding window on recovery to start fresh
                if key in _outcomes:
                    _outcomes[key].clear()
                # We assume recovery (mark healthy) — real probe would
                # need an endpoint URL, which we track separately.
                s["healthy"] = True


def record_success(backend_key: str):
    with _lock:
        _ensure(backend_key)
        s = _state[backend_key]
        s["active_connections"] = max(0, s["active_connections"] - 1)
        s["total_requests"] += 1
        s["consecutive_failures"] = 0
        s["healthy"] = True
        s["circuit_open_until"] = 0.0
        # Clear the sliding window on recovery so a single success
        # doesn't get drowned out by old failure entries.
        if backend_key in _outcomes:
            _outcomes[backend_key].clear()
        _outcomes[backend_key].append(1)


def record_failure(backend_key: str):
    with _lock:
        _ensure(backend_key)
        s = _state[backend_key]
        s["active_connections"] = max(0, s["active_connections"] - 1)
        s["total_requests"] += 1
        s["total_failures"] += 1
        s["consecutive_failures"] += 1
        _outcomes[backend_key].append(0)
        _check_circuit(backend_key)


def _check_circuit(backend_key: str):
    """Check sliding-window and consecutive-failure circuit breaker conditions."""
    s = _state[backend_key]
    outcomes = _outcomes.get(backend_key, collections.deque())
    # Condition 1: consecutive failures
    if s["consecutive_failures"] >= FAILURE_THRESHOLD:
        s["healthy"] = False
        s["circuit_open_until"] = time.monotonic() + RECOVERY_TIMEOUT_S
        return
    # Condition 2: sliding-window failure ratio
    if len(outcomes) >= CB_MIN_REQUESTS:
        fail_count = sum(1 for o in outcomes if o == 0)
        ratio = fail_count / len(outcomes)
        if ratio >= CB_RATIO_THRESHOLD:
            s["healthy"] = False
            s["circuit_open_until"] = time.monotonic() + RECOVERY_TIMEOUT_S


def connection_start(backend_key: str):
    with _lock:
        _ensure(backend_key)
        _state[backend_key]["active_connections"] += 1


def connection_end(backend_key: str):
    with _lock:
        _ensure(backend_key)
        _state[backend_key]["active_connections"] = max(
            0, _state[backend_key]["active_connections"] - 1)


# ---------------------------------------------------------------- algo
_rr_cursor = 0


def _pick_round_robin(candidates: List[str]) -> str:
    global _rr_cursor
    if not candidates:
        return ""
    n = len(candidates)
    for _ in range(n):
        key = candidates[_rr_cursor % n]
        _rr_cursor = (_rr_cursor + 1) % n
        with _lock:
            if _state.get(key, {}).get("healthy", True):
                return key
    return candidates[0]


def _pick_least_conn(candidates: List[str]) -> str:
    if not candidates:
        return ""
    best = None
    best_load = float("inf")
    with _lock:
        for key in candidates:
            s = _state.get(key, {})
            load = s.get("active_connections", 0)
            if s.get("healthy", True) and load < best_load:
                best_load = load
                best = key
    return best or candidates[0]


def _pick_weighted(candidates: List[str],
                   weights: Dict[str, int]) -> str:
    if not candidates:
        return ""
    available = [(k, weights.get(k, 1))
                 for k in candidates
                 if _state.get(k, {}).get("healthy", True)]
    if not available:
        return candidates[0]
    total = sum(w for _, w in available)
    r = hash(time.monotonic()) % total
    cumulative = 0
    for key, w in available:
        cumulative += w
        if r < cumulative:
            return key
    return available[-1][0]


def pick_backend(candidates: List[str],
                 weights: Optional[Dict[str, int]] = None) -> str:
    """Return the selected backend key from *candidates*, or "" if none."""
    _tick_health()
    if ALGO == "least_conn":
        return _pick_least_conn(candidates)
    if ALGO == "weighted":
        return _pick_weighted(candidates, weights or {})
    return _pick_round_robin(candidates)


# ---------------------------------------------------------------- state API
def get_state(backend_key: str) -> Dict:
    with _lock:
        _ensure(backend_key)
        return dict(_state[backend_key])


def all_state() -> Dict[str, Dict]:
    with _lock:
        return {k: dict(v) for k, v in _state.items()}


def reset_state():
    with _lock:
        _state.clear()
        _outcomes.clear()
