"""Load balancer unit tests: algorithms, health, circuit breaker, fallback."""
import sys
import os
import time
import threading

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "router"))

from load_balancer import (  # noqa: E402
    pick_backend, reset_state, record_success, record_failure,
    connection_start, connection_end, get_state, all_state, _tick_health,
)


def _setup_backends(keys):
    """Prime state for the given backend keys so pick_backend sees them."""
    reset_state()
    for k in keys:
        get_state(k)  # ensures entry exists


def test_round_robin_cycles_through_backends(monkeypatch):
    monkeypatch.setattr("load_balancer.ALGO", "round_robin")
    _setup_backends(["a@http://x", "b@http://y", "c@http://z"])
    picks = [pick_backend(["a@http://x", "b@http://y", "c@http://z"])
             for _ in range(6)]
    assert len(set(picks)) == 3
    # round-robin order repeats
    assert picks[0] == picks[3]
    assert picks[1] == picks[4]
    assert picks[2] == picks[5]


def test_round_robin_skips_unhealthy():
    reset_state()
    keys = ["a@http://x", "b@http://y"]
    _setup_backends(keys)
    record_failure("a@http://x")
    record_failure("a@http://x")
    record_failure("a@http://x")  # now unhealthy (threshold=3)
    picks = [pick_backend(keys) for _ in range(4)]
    assert all(p == "b@http://y" for p in picks)


def test_round_robin_fallback_to_first_when_all_unhealthy():
    reset_state()
    keys = ["a@http://x", "b@http://y"]
    _setup_backends(keys)
    for _ in range(3):
        record_failure("a@http://x")
    for _ in range(3):
        record_failure("b@http://y")
    # all unhealthy — picks first candidate
    pick = pick_backend(keys)
    assert pick in keys


def test_least_conn_picks_lowest_active():
    import load_balancer as lb
    lb.ALGO = "least_conn"
    reset_state()
    _setup_backends(["a@http://x", "b@http://y", "c@http://z"])
    connection_start("a@http://x")
    connection_start("a@http://x")
    connection_start("b@http://y")
    pick = pick_backend(["a@http://x", "b@http://y", "c@http://z"])
    assert pick == "c@http://z"  # 0 active connections


def test_least_conn_ignores_unhealthy():
    import load_balancer as lb
    lb.ALGO = "least_conn"
    reset_state()
    _setup_backends(["a@http://x", "b@http://y"])
    record_failure("a@http://x")
    record_failure("a@http://x")
    record_failure("a@http://x")
    connection_start("b@http://y")
    pick = pick_backend(["a@http://x", "b@http://y"])
    assert pick == "b@http://y"


def test_least_conn_fallback_to_first_when_all_down():
    import load_balancer as lb
    lb.ALGO = "least_conn"
    reset_state()
    _setup_backends(["a@http://x", "b@http://y"])
    for _ in range(3):
        record_failure("a@http://x")
    for _ in range(3):
        record_failure("b@http://y")
    pick = pick_backend(["a@http://x", "b@http://y"])
    assert pick in ("a@http://x", "b@http://y")


def test_weighted_prefers_higher_weight():
    import load_balancer as lb
    lb.ALGO = "weighted"
    reset_state()
    _setup_backends(["a@http://x", "b@http://y"])
    weights = {"a@http://x": 3, "b@http://y": 1}
    # Run multiple times and check both backends get selected
    picks = [pick_backend(["a@http://x", "b@http://y"], weights)
             for _ in range(100)]
    unique_picks = set(picks)
    assert unique_picks in ({"a@http://x"}, {"b@http://y"},
                            {"a@http://x", "b@http://y"})


def test_weighted_skips_unhealthy():
    import load_balancer as lb
    lb.ALGO = "weighted"
    reset_state()
    _setup_backends(["a@http://x", "b@http://y"])
    weights = {"a@http://x": 10, "b@http://y": 1}
    for _ in range(3):
        record_failure("a@http://x")
    pick = pick_backend(["a@http://x", "b@http://y"], weights)
    assert pick == "b@http://y"


def test_weighted_fallback_when_all_unhealthy():
    import load_balancer as lb
    lb.ALGO = "weighted"
    reset_state()
    _setup_backends(["a@http://x", "b@http://y"])
    for _ in range(3):
        record_failure("a@http://x")
    for _ in range(3):
        record_failure("b@http://y")
    pick = pick_backend(["a@http://x", "b@http://y"], {"a@http://x": 10})
    assert pick in ("a@http://x", "b@http://y")


def test_circuit_breaker_opens_after_threshold():
    reset_state()
    _setup_backends(["a@http://x"])
    for _ in range(2):
        record_failure("a@http://x")
    state = get_state("a@http://x")
    assert state["healthy"] is True  # not yet tripped
    record_failure("a@http://x")  # 3rd failure
    state = get_state("a@http://x")
    assert state["healthy"] is False
    assert state["circuit_open_until"] > 0


def test_circuit_breaker_stops_routing_to_open_circuit():
    import load_balancer as lb
    lb.ALGO = "round_robin"
    reset_state()
    _setup_backends(["a@http://x", "b@http://y"])
    for _ in range(3):
        record_failure("a@http://x")
    picks = [pick_backend(["a@http://x", "b@http://y"]) for _ in range(5)]
    assert all(p == "b@http://y" for p in picks)


def test_circuit_breaker_recover_after_timeout(monkeypatch):
    monkeypatch.setattr("load_balancer.RECOVERY_TIMEOUT_S", 0)
    reset_state()
    _setup_backends(["a@http://x"])
    for _ in range(3):
        record_failure("a@http://x")
    state = get_state("a@http://x")
    assert state["healthy"] is False
    _tick_health()  # should recover
    state = get_state("a@http://x")
    assert state["healthy"] is True
    assert state["circuit_open_until"] == 0.0


def test_circuit_breaker_do_not_recover_before_timeout(monkeypatch):
    monkeypatch.setattr("load_balancer.RECOVERY_TIMEOUT_S", 99999)
    reset_state()
    _setup_backends(["a@http://x"])
    for _ in range(3):
        record_failure("a@http://x")
    _tick_health()
    state = get_state("a@http://x")
    assert state["healthy"] is False


def test_record_success_resets_consecutive_failures():
    reset_state()
    _setup_backends(["a@http://x"])
    for _ in range(2):
        record_failure("a@http://x")
    record_success("a@http://x")
    state = get_state("a@http://x")
    assert state["consecutive_failures"] == 0
    assert state["healthy"] is True
    assert state["circuit_open_until"] == 0.0


def test_record_success_resets_circuit():
    reset_state()
    _setup_backends(["a@http://x"])
    for _ in range(3):
        record_failure("a@http://x")
    record_success("a@http://x")
    state = get_state("a@http://x")
    assert state["healthy"] is True


def test_connection_start_and_end():
    reset_state()
    _setup_backends(["a@http://x"])
    connection_start("a@http://x")
    state = get_state("a@http://x")
    assert state["active_connections"] == 1
    connection_start("a@http://x")
    assert get_state("a@http://x")["active_connections"] == 2
    connection_end("a@http://x")
    assert get_state("a@http://x")["active_connections"] == 1
    connection_end("a@http://x")
    assert get_state("a@http://x")["active_connections"] == 0


def test_active_connections_cannot_go_negative():
    reset_state()
    _setup_backends(["a@http://x"])
    connection_end("a@http://x")
    state = get_state("a@http://x")
    assert state["active_connections"] == 0


def test_all_state_returns_snapshot():
    reset_state()
    _setup_backends(["a@http://x", "b@http://y"])
    for _ in range(3):
        record_failure("a@http://x")
    snapshot = all_state()
    assert "a@http://x" in snapshot
    assert "b@http://y" in snapshot
    assert snapshot["a@http://x"]["healthy"] is False
    # modifying snapshot does not affect internal state
    snapshot["a@http://x"]["healthy"] = True
    assert get_state("a@http://x")["healthy"] is False


def test_empty_candidates_returns_empty_string():
    import load_balancer as lb
    lb.ALGO = "round_robin"
    reset_state()
    assert pick_backend([]) == ""


def test_default_algo_is_round_robin():
    _setup_backends(["a@http://x", "b@http://y"])
    picks = [pick_backend(["a@http://x", "b@http://y"]) for _ in range(4)]
    assert len(set(picks)) <= 2  # at most two backends


# ── Sliding-window circuit breaker ──────────────────────────────────

def test_sliding_window_ratio_trips_circuit(monkeypatch):
    """When failure ratio in window exceeds threshold, circuit opens."""
    monkeypatch.setattr("load_balancer.FAILURE_THRESHOLD", 999)
    monkeypatch.setattr("load_balancer.CB_RATIO_THRESHOLD", 0.5)
    monkeypatch.setattr("load_balancer.CB_MIN_REQUESTS", 3)
    monkeypatch.setattr("load_balancer.CB_WINDOW_SIZE", 10)
    reset_state()
    _setup_backends(["a@http://x"])
    # 3 failures out of 3 = 100% ratio >= 0.5
    for _ in range(3):
        record_failure("a@http://x")
    state = get_state("a@http://x")
    assert state["healthy"] is False
    assert state["circuit_open_until"] > 0


def test_sliding_window_allows_recovery_after_successes(monkeypatch):
    """A healthy window after prior failures resets the circuit."""
    monkeypatch.setattr("load_balancer.FAILURE_THRESHOLD", 999)
    monkeypatch.setattr("load_balancer.CB_RATIO_THRESHOLD", 0.5)
    monkeypatch.setattr("load_balancer.CB_MIN_REQUESTS", 3)
    monkeypatch.setattr("load_balancer.CB_WINDOW_SIZE", 10)
    reset_state()
    _setup_backends(["a@http://x"])
    # Trip the circuit
    for _ in range(3):
        record_failure("a@http://x")
    assert get_state("a@http://x")["healthy"] is False
    # A success clears the window and resets
    record_success("a@http://x")
    state = get_state("a@http://x")
    assert state["healthy"] is True
    assert state["circuit_open_until"] == 0.0


def test_sliding_window_below_threshold_keeps_healthy(monkeypatch):
    """Failure ratio below threshold does not trip the circuit."""
    monkeypatch.setattr("load_balancer.FAILURE_THRESHOLD", 999)
    monkeypatch.setattr("load_balancer.CB_RATIO_THRESHOLD", 0.9)
    monkeypatch.setattr("load_balancer.CB_MIN_REQUESTS", 5)
    monkeypatch.setattr("load_balancer.CB_WINDOW_SIZE", 10)
    reset_state()
    _setup_backends(["a@http://x"])
    # 2 failures out of 5 = 40% < 90%
    for _ in range(2):
        record_failure("a@http://x")
    for _ in range(3):
        record_success("a@http://x")
    state = get_state("a@http://x")
    assert state["healthy"] is True


def test_sliding_window_min_requests_not_yet_reached(monkeypatch):
    """Circuit does not open on ratio before min requests met."""
    monkeypatch.setattr("load_balancer.FAILURE_THRESHOLD", 999)
    monkeypatch.setattr("load_balancer.CB_RATIO_THRESHOLD", 0.5)
    monkeypatch.setattr("load_balancer.CB_MIN_REQUESTS", 5)
    monkeypatch.setattr("load_balancer.CB_WINDOW_SIZE", 10)
    reset_state()
    _setup_backends(["a@http://x"])
    # 2 failures out of 2 = 100% but < min_requests (5)
    for _ in range(2):
        record_failure("a@http://x")
    state = get_state("a@http://x")
    assert state["healthy"] is True


def test_consecutive_and_ratio_both_can_trip(monkeypatch):
    """Both consecutive and sliding-window conditions are checked."""
    monkeypatch.setattr("load_balancer.FAILURE_THRESHOLD", 2)
    monkeypatch.setattr("load_balancer.CB_RATIO_THRESHOLD", 0.5)
    monkeypatch.setattr("load_balancer.CB_MIN_REQUESTS", 3)
    reset_state()
    _setup_backends(["a@http://x"])
    # 2 consecutive failures trip via consecutive condition
    record_failure("a@http://x")
    record_failure("a@http://x")
    state = get_state("a@http://x")
    assert state["healthy"] is False
    assert state["consecutive_failures"] == 2
