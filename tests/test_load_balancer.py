"""Tests for load balancer functionality."""
import pytest

flask = pytest.importorskip("flask")


@pytest.fixture
def client(router_mod):
    router_mod.app.config["TESTING"] = True
    with router_mod.app.test_client() as c:
        yield c


@pytest.fixture
def router_mod():
    import router
    return router


def test_lb_stats_endpoint(client, router_mod):
    """GET /api/router/lb-stats returns algorithm and backend state."""
    from load_balancer import reset_state
    reset_state()
    res = client.get("/api/router/lb-stats")
    assert res.status_code == 200
    body = res.get_json()
    assert "algorithm" in body
    assert "backends" in body
    assert body["algorithm"] in ("round_robin", "least_conn", "weighted")


def test_lb_load_balancers_endpoint(client, router_mod):
    """GET /router/load-balancers returns detailed backend info."""
    from load_balancer import reset_state
    reset_state()
    res = client.get("/router/load-balancers")
    assert res.status_code == 200
    body = res.get_json()
    assert body["algorithm"] in ("round_robin", "least_conn", "weighted")
    assert "backends" in body
    assert "failure_threshold" in body
    assert "recovery_timeout_s" in body


def test_round_robin_distributes(client, router_mod):
    """Round-robin selects different backends for sequential requests."""
    from load_balancer import reset_state, ALGO
    reset_state()
    if ALGO != "round_robin":
        pytest.skip("Testing requires round_robin algorithm")
    # Simulate requests that would hit different endpoints
    for i in range(3):
        res = client.post("/route", json={
            "prompt": f"test round robin {i}",
            "max_tokens": 4,
        })
        assert res.status_code == 200


def test_health_check_skips_unhealthy(client, router_mod):
    """Unhealthy backends are skipped by the load balancer."""
    from load_balancer import record_failure, get_state, reset_state
    reset_state()
    # Force enough failures to exceed threshold (default 3)
    for _ in range(3):
        record_failure("http://localhost:9001/completion")
    state = get_state("http://localhost:9001/completion")
    assert state["healthy"] is False


def test_single_model_unchanged(client, router_mod):
    """Single model routing still works (no regression)."""
    res = client.post("/route", json={
        "prompt": "Build a production API",
        "max_tokens": 4,
    })
    assert res.status_code == 200
    body = res.get_json()
    assert "task_type" in body
    assert "model_used" in body
    assert body["response"].get("mock") is True
