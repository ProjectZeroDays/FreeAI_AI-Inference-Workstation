"""Workflow engine tests: validation, retries, extraction, definitions."""
import pytest

requests = pytest.importorskip("requests")

try:
    from workflow.engine import (Step, Workflow, InlineStep,
                                 _extract_text, validate_workflow,
                                 from_definition)
except ImportError:
    from engine import (Step, Workflow, InlineStep,
                        _extract_text, validate_workflow,
                        from_definition)


def _noop(ctx):
    return {"prompt": ctx.get("spec", "")}


def test_extract_text_choices():
    assert _extract_text(
        {"response": {"choices": [{"text": "hi"}]}}) == "hi"


def test_extract_text_message_content():
    assert _extract_text({"response": {"choices": [
        {"message": {"content": "hello"}}]}}) == "hello"


def test_extract_text_legacy_content():
    assert _extract_text({"response": {"content": "yo"}}) == "yo"


def test_extract_text_empty():
    assert _extract_text({}) == ""
    assert _extract_text("not-a-dict") == ""


def test_validate_detects_missing_dependency():
    steps = [Step("b", "orchestrate", _noop, consumes=["a"])]
    warnings = validate_workflow(steps, initial_keys=[])
    assert any("'a'" in w for w in warnings)


def test_validate_ok_chain():
    steps = [
        Step("a", "analyze", _noop),
        Step("b", "orchestrate", _noop, consumes=["a"]),
    ]
    assert validate_workflow(steps, initial_keys=[]) == []


def test_validate_accepts_initial_context_keys():
    steps = [Step("b", "orchestrate", _noop, consumes=["spec"])]
    assert validate_workflow(steps, initial_keys=["spec"]) == []


def test_step_retries_then_raises(monkeypatch):
    calls = {"n": 0}

    def boom(*args, **kwargs):
        calls["n"] += 1
        raise ConnectionError("no backend")

    monkeypatch.setattr(requests, "post", boom)
    step = Step("s", "orchestrate", _noop)
    with pytest.raises(ConnectionError):
        step.run({"spec": "x"}, workflow_id="test")
    assert calls["n"] == 3


def test_inline_step_sends_payload_verbatim(monkeypatch):
    captured = {}

    def fake_post(url, json=None, timeout=None):
        captured["url"] = url
        captured["json"] = json

        class R:
            def raise_for_status(self):
                pass

            def json(self):
                return {"ok": True}

        return R()

    monkeypatch.setattr(requests, "post", fake_post)
    step = InlineStep("probe", "debug", {"code": "x", "error": "y"})
    out = step.run({}, workflow_id="t")
    assert out["probe"] == {"ok": True}
    assert captured["json"] == {"code": "x", "error": "y"}
    assert captured["url"].endswith("/agent/debug")


def test_definition_roundtrip():
    wf = from_definition({
        "name": "mini",
        "steps": [
            {"name": "one", "agent": "analyze",
             "payload": {"context": "c", "question": "q"}},
            {"name": "two", "agent": "orchestrate",
             "consumes": ["one"], "payload": {"prompt": "p"}},
        ],
    })
    assert wf.name == "mini"
    assert len(wf.steps) == 2
    assert isinstance(wf.steps[0], InlineStep)
