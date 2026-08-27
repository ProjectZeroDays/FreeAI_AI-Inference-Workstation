"""External provider bridge tests (no network)."""
import json
import os
import sys

import pytest

requests = pytest.importorskip("requests")

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "router"))

from providers import (load_providers, is_keyed, build_request,  # noqa: E402
                       parse_response, fallback_models, PRESETS)


@pytest.fixture()
def providers_file(tmp_path, monkeypatch):
    import providers as prov
    monkeypatch.setattr(prov, "PROVIDERS_PATH",
                        str(tmp_path / "providers.json"))
    monkeypatch.setenv("OPENAI_API_KEY", "sk-test")
    monkeypatch.setenv("ANTHROPIC_API_KEY", "ak-test")
    monkeypatch.setenv("GOOGLE_API_KEY", "gk-test")
    monkeypatch.delenv("GROQ_API_KEY", raising=False)
    yield prov


def test_presets_cover_major_hosts():
    for name in ("openai", "anthropic", "google", "groq", "mistral",
                 "deepseek", "together", "fireworks", "openrouter",
                 "xai", "perplexity", "cerebras", "sambanova", "cohere",
                 "ollama", "lmstudio"):
        assert name in PRESETS, f"missing preset {name}"


def test_user_overrides_merge(providers_file, tmp_path):
    (tmp_path / "providers.json").write_text(json.dumps({
        "providers": {
            "openai": {"fallback": True},
            "my-custom": {"style": "openai",
                          "base_url": "https://me/v1",
                          "key_env": "MY_KEY", "models": ["m1"]},
        }}))
    provs = providers_file.load_providers()
    assert provs["openai"]["fallback"] is True
    assert provs["my-custom"]["base_url"] == "https://me/v1"


def test_keyed_detection(providers_file):
    provs = providers_file.load_providers()
    assert providers_file.is_keyed("openai", provs["openai"]) is True
    assert providers_file.is_keyed("groq", provs["groq"]) is False


def test_openai_request_shape(providers_file):
    url, headers, body = providers_file.build_request(
        "openai", PRESETS["openai"], "gpt-4o-mini", "hi", 128, 0.1)
    assert url.endswith("/chat/completions")
    assert headers["Authorization"] == "Bearer sk-test"
    assert body["messages"][0]["content"] == "hi"
    assert body["max_tokens"] == 128


def test_anthropic_request_shape(providers_file):
    url, headers, body = providers_file.build_request(
        "anthropic", PRESETS["anthropic"], "claude-sonnet-4-5", "hi")
    assert url.endswith("/v1/messages")
    assert headers["x-api-key"] and headers["anthropic-version"]
    assert body["max_tokens"] and body["messages"][0]["role"] == "user"


def test_gemini_request_shape(providers_file):
    url, headers, body = providers_file.build_request(
        "google", PRESETS["google"], "gemini-2.5-flash", "hi")
    assert "gemini-2.5-flash:generateContent" in url
    assert headers["x-goog-api-key"]
    assert body["contents"][0]["parts"][0]["text"] == "hi"


def test_parse_normalization(providers_file):
    openai = providers_file.parse_response("openai", PRESETS["openai"],
        {"choices": [{"message": {"content": "pong"}}], "model": "gpt-4o-mini"})
    assert openai["content"] == "pong" and openai["provider"] == "openai"

    anthro = providers_file.parse_response("anthropic", PRESETS["anthropic"],
        {"content": [{"type": "text", "text": "hi"}], "model": "claude"})
    assert anthro["content"] == "hi"

    gem = providers_file.parse_response("google", PRESETS["google"],
        {"candidates": [{"content": {"parts": [{"text": "yo"}]}}]})
    assert gem["content"] == "yo"


def test_fallback_models_only_keyed(providers_file, tmp_path):
    (tmp_path / "providers.json").write_text(json.dumps({
        "providers": {"openai": {"fallback": True},
                      "groq": {"fallback": True}}}))
    ids = providers_file.fallback_models()
    assert "openai/gpt-4o" in ids
    assert not any(i.startswith("groq/") for i in ids)


def test_router_models_include_providers(providers_file, monkeypatch):
    flask = pytest.importorskip("flask")
    monkeypatch.syspath_prepend(ROOT)
    import router as router_mod
    router_mod.app.config["TESTING"] = True
    with router_mod.app.test_client() as c:
        res = c.get("/models")
    models = res.get_json()
    assert "openai/gpt-4o-mini" in models
    assert models["openai/gpt-4o-mini"]["keyed"] is True
    assert "groq/llama-3.3-70b-versatile" in models


def test_router_explicit_provider_route(providers_file, monkeypatch):
    flask = pytest.importorskip("flask")
    monkeypatch.syspath_prepend(ROOT)
    import router as router_mod

    captured = {}

    class FakeResp:
        def raise_for_status(self):
            pass

        def json(self):
            return {"choices": [{"message": {"content": "pong from openai"}}],
                    "model": "gpt-4o-mini"}

    def fake_post(url, headers=None, json=None, timeout=None, **kw):
        captured["url"] = url
        return FakeResp()

    monkeypatch.setattr(router_mod.requests, "post", fake_post)

    router_mod.app.config["TESTING"] = True
    with router_mod.app.test_client() as c:
        res = c.post("/route", json={
            "prompt": "say pong", "model": "openai/gpt-4o-mini"})
    assert res.status_code == 200
    body = res.get_json()
    assert body["model_used"] == "openai/gpt-4o-mini"
    assert body["response"]["content"] == "pong from openai"
    assert "api.openai.com" in captured["url"]
    assert res.headers["X-Cache"] == "PASS"
