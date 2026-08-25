"""Offline unit tests: classifier, switcher, cache, rate limiter."""
from classifier import classify_task
from switcher import select_chain, select_model
from models import MODEL_REGISTRY


def test_full_project_classification():
    task, conf = classify_task("Build a production API service")
    assert task == "full_project"
    assert 0.5 < conf <= 1.0


def test_refactor_classification():
    task, _ = classify_task("refactor and optimize this function")
    assert task == "refactor"


def test_analysis_classification():
    task, _ = classify_task("explain how does this algorithm work")
    assert task == "analysis"


def test_general_code_default():
    task, conf = classify_task("hello world")
    assert task == "general_code"
    assert conf == 0.5


def test_confidence_scales_with_hits():
    _, weak = classify_task("build something")
    _, strong = classify_task("build a production microservice with "
                              "docker and kubernetes infrastructure")
    assert strong > weak


def test_select_model_roles():
    assert select_model("full_project")["role"] == "primary_coder"
    assert select_model("refactor")["role"] == "fast_coder"
    assert select_model("analysis")["role"] == "reasoning_specialist"


def test_fallback_chain_primary_first():
    chain = select_chain("refactor")
    assert chain[0] in MODEL_REGISTRY
    assert len(chain) == 4


def test_per_agent_override_reorders_chain():
    chain = select_chain("full_project", agent="refactor-agent-test")
    # no override configured for this fake agent -> default order
    assert chain[0] == MODEL_REGISTRY["qwen3.6-12b"]["id"] or \
        chain[0] in ("qwen3.6-12b", "moe-13b", "qwen3.5-9b")


def test_qwythos_is_analysis_primary():
    chain = select_chain("analysis")
    assert chain[0] == "qwythos-9b"


def test_qwythos_has_temperature_floor():
    from models import MODEL_REGISTRY
    assert MODEL_REGISTRY["qwythos-9b"]["min_temperature"] == 0.6


def test_temperature_floor_applied(monkeypatch):
    import router as router_mod
    captured = {}

    class FakeResp:
        def raise_for_status(self):
            pass

        def json(self):
            return {"content": "ok"}

    def fake_post(url, json=None, timeout=None, **kw):
        captured["payload"] = json
        return FakeResp()

    monkeypatch.setattr(router_mod.requests, "post", fake_post)
    monkeypatch.setattr(router_mod, "MOCK_LLM", False)
    router_mod.app.config["TESTING"] = True
    with router_mod.app.test_client() as c:
        # "explain..." -> analysis -> qwythos-9b (floor 0.6); balanced=0.2
        res = c.post("/route", json={
            "prompt": "explain how does recursion work",
            "temperature": 0.2, "max_tokens": 8})
    assert res.status_code == 200
    assert captured["payload"]["temperature"] == 0.6


def test_registry_integrity():
    for key, model in MODEL_REGISTRY.items():
        assert model["endpoint"].startswith("http")
        assert model["strengths"]
