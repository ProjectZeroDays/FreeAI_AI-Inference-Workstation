"""Coherence guard tests: degenerate detection + router fallback retry."""
import pytest

flask = pytest.importorskip("flask")
requests = pytest.importorskip("requests")

import router as router_mod  # noqa: E402


def test_is_degenerate_repetition_loop():
    loop = ("the quick brown fox jumps over the lazy dog. " * 8)
    assert router_mod.is_degenerate(loop)


def test_is_degenerate_short_normal_text():
    text = "Refactored the parser into three modules and added unit tests."
    assert not router_mod.is_degenerate(text)


def test_is_degenerate_long_coherent_text():
    text = ("The router classifies each prompt by keyword hits, then "
            "walks a fallback chain across healthy backends. Caching "
            "keys include the task type so profile changes invalidate "
            "naturally. ") * 3
    assert not router_mod.is_degenerate(text)


def test_is_degenerate_empty():
    assert not router_mod.is_degenerate("")


def test_is_degenerate_tail_only_loop():
    good = "Here is the fixed function:\n\n"
    bad = "aaaa bbbb " * 40
    assert router_mod.is_degenerate(good + bad)


@pytest.fixture()
def client(monkeypatch):
    calls = {"n": 0}

    class FakeResp:
        def raise_for_status(self):
            pass

        def __init__(self, payload):
            self._p = payload

        def json(self):
            return self._p

    degenerate = {"content": "lorem ipsum dolor " * 60}
    healthy = {"content": "value = 42  # fixed"}

    def fake_post(url, json=None, timeout=None):
        calls["n"] += 1
        if calls["n"] == 1:
            return FakeResp(degenerate)
        return FakeResp(healthy)

    monkeypatch.setattr(requests, "post", fake_post)
    monkeypatch.setattr(router_mod, "MOCK_LLM", False)
    router_mod.app.config["TESTING"] = True
    with router_mod.app.test_client() as c:
        yield c, calls


def test_route_retries_past_degenerate_answer(client):
    c, calls = client
    res = c.post("/route", json={"prompt": "unique probe prompt alpha"})
    assert res.status_code == 200
    body = res.get_json()
    assert body["response"]["content"].startswith("value")
    assert calls["n"] == 2
    assert res.headers.get("X-Coherence-Retries") == "1"
