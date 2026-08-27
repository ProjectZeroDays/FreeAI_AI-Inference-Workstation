"""Locust load tests for the /route endpoint.

Usage:
    locust -f tests/load/test_router.py --host http://localhost:8010
    locust -f tests/load/test_router.py --headless -u 100 -r 10 -t 60s --host http://localhost:8010
"""
import sys
import os

locust = None
try:
    from locust import HttpUser, task, between, events
    import locust
except ImportError:
    locust = None


def _make_classes():
    """Build locust user classes; returns None if locust unavailable."""
    if locust is None:
        return None

    class RouterUser(HttpUser):
        wait_time = between(0.1, 0.5)
        host = "http://localhost:8010"

        @task(3)
        def route(self):
            self.client.post("/route", json={
                "prompt": "refactor this function for clarity and performance",
                "max_tokens": 128,
            })

        @task(1)
        def health(self):
            self.client.get("/health")

        @task(1)
        def metrics(self):
            self.client.get("/metrics")

    return RouterUser


RouterUser = _make_classes()


def print_stats(stats):
    """Human-readable summary after a load-test run."""
    entries = list(stats.entries.values())
    if not entries:
        return
    print(f"\n--- Load-test summary ---")
    print(f"Total requests : {sum(e.num_requests for e in entries)}")
    print(f"Failures       : {sum(e.failure_count for e in entries)}")
    print("---\n")


def on_request(request_type, name, response_time, response_length,
               exception, context, elapsed=None, **kwargs):
    """Hook point for custom stats collection."""
    pass


def on_test_start(environment, **kwargs):
    print(f"\nStarting load test: {environment.host}")


def on_test_stop(environment, **kwargs):
    stats = environment.runner.stats
    print("\n--- Final Statistics ---")
    for method, path in sorted(stats.entries.keys()):
        entry = stats.entries[(method, path)]
        avg = entry.avg_response_time
        p95 = entry.response_time_percentiles.get(95, 0)
        p99 = entry.response_time_percentiles.get(99, 0)
        print(f"  {method} {path}")
        print(f"    avg ms   : {avg:.1f}")
        print(f"    p95 ms   : {p95:.1f}")
        print(f"    p99 ms   : {p99:.1f}")
        print(f"    total    : {entry.num_requests}")
    print("---\n")


# Register hooks only when locust is available
if locust is not None:
    events.request += on_request
    events.test_start += on_test_start
    events.test_stop += on_test_stop
