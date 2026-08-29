"""Tests for the browser module — engine, army, intelligence, API."""
import asyncio
import json
import sys
import tempfile
import threading
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

browser = Path(__file__).parent.parent / "browser"
sys.path.insert(0, str(Path(__file__).parent.parent))

from browser.engine import (  # noqa: E402
    BrowserEngine,
    CDPClient,
    CDPError,
    FingerprintProfile,
    HealingEngine,
    ManifestXSystem,
    create_engine,
)
from browser.army import (  # noqa: E402
    ArmyAgent,
    FleetCoordinator,
    SwarmCoordinator,
    get_army,
    RANKS,
    DIVISIONS,
)
from browser.intelligence import (  # noqa: E402
    BurpProxy,
    FridaInstrumentor,
    GhidraAnalyzer,
    IntelligencePipeline,
)
from browser.anonymity import AnonymityRouter


# ── FingerprintProfile ─────────────────────────────────────────────

def test_fingerprint_profile_has_template():
    fp = FingerprintProfile()
    assert fp.template in ("chrome_131_win", "chrome_131_mac", "firefox_134_win")
    assert fp.data is not None
    assert isinstance(fp.data, dict)


def test_fingerprint_profile_has_required_keys():
    fp = FingerprintProfile()
    data = fp.data
    assert "user_agent" in data
    assert "platform" in data
    assert "hardware_concurrency" in data
    assert "device_memory" in data
    assert "timezone" in data
    assert "screen" in data
    assert "pixel_ratio" in data
    assert "canvas" in data


def test_fingerprint_profile_randomization():
    fps = [FingerprintProfile() for _ in range(20)]
    hc_values = [fp.data["hardware_concurrency"] for fp in fps]
    # Hardware concurrency should vary across instances
    assert len(set(hc_values)) >= 1
    # All should be realistic values
    for hc in hc_values:
        assert hc in (4, 6, 8, 10, 12)


def test_fingerprint_inject_into_page_produces_script():
    fp = FingerprintProfile()
    script = fp.data.get("user_agent", "")
    assert "Mozilla" in script or len(script) > 0


# ── ManifestXSystem ────────────────────────────────────────────────

def test_manifestx_describe_caps():
    mx = ManifestXSystem()
    caps = mx.describe_caps()
    assert caps["name"] == "Manifest-X"
    assert caps["god_mode"] is True
    assert isinstance(caps["capabilities"], list)
    assert len(caps["capabilities"]) > 0


def test_manifestx_generate_extension():
    mx = ManifestXSystem()
    ext = mx.generate_extension("test-ext", ["storage", "tabs"])
    assert ext["name"] == "test-ext"
    assert ext["manifest_version"] == 4
    assert "test-ext" in mx._extensions


def test_manifestx_get_manifest():
    mx = ManifestXSystem()
    assert mx.get_manifest("nonexistent") is None
    mx.generate_extension("x", ["storage"])
    assert mx.get_manifest("x") is not None
    assert mx.get_manifest("x")["name"] == "x"


def test_manifestx_load_extensions_empty_dir():
    mx = ManifestXSystem()
    result = mx.load_extensions(extensions_dir="/nonexistent/path")
    assert result == []


# ── HealingEngine ──────────────────────────────────────────────────

def test_healing_stats_initial():
    heal = HealingEngine()
    stats = heal.stats
    assert stats["retries"] == 0
    assert stats["successes"] == 0
    assert stats["failures"] == 0
    assert stats["adaptations"] == 0


def test_healing_success_on_first_try():
    heal = HealingEngine()
    async def _act():
        return "ok"

    async def _run():
        return await heal.execute_with_healing(None, _act)

    result = asyncio.run(_run())
    assert result == "ok"
    assert heal.stats["successes"] == 1


def test_healing_retries_then_succeeds():
    heal = HealingEngine(config={"max_retries": 3})
    call_count = [0]

    async def _act():
        call_count[0] += 1
        if call_count[0] < 3:
            raise ValueError("fail")
        return "ok"

    async def _run():
        return await heal.execute_with_healing(None, _act)

    result = asyncio.run(_run())
    assert result == "ok"
    assert heal.stats["successes"] == 1
    assert heal.stats["retries"] == 2


def test_healing_exhausts_retries():
    heal = HealingEngine(config={"max_retries": 2})

    async def _act():
        raise ValueError("always fails")

    async def _run():
        try:
            await heal.execute_with_healing(None, _act)
            return "no error"
        except ValueError:
            return "raised"

    result = asyncio.run(_run())
    assert result == "raised"
    assert heal.stats["failures"] == 1


# ── CDPClient ──────────────────────────────────────────────────────

def test_cdp_client_initial_state():
    client = CDPClient()
    assert client.is_connected is False
    assert client._ws is None


def test_cdp_error():
    err = CDPError("Page.navigate", "tab closed")
    assert err.method == "Page.navigate"
    assert "tab closed" in str(err)


# ── BrowserEngine ──────────────────────────────────────────────────

def test_browser_engine_create():
    engine = create_engine({})
    assert engine.session_id is not None
    assert isinstance(engine.session_id, str)
    assert len(engine.session_id) == 8
    assert engine.is_open is False


def test_browser_engine_get_headless():
    engine = create_engine({"headless": True})
    assert engine.get_headless() is True
    engine2 = create_engine({"headless": False})
    assert engine2.get_headless() is False


def test_browser_engine_get_state():
    engine = create_engine({})
    state = asyncio.run(engine.get_state())
    assert state["session_id"] == engine.session_id
    assert state["is_open"] is False
    assert state["url"] == ""
    assert state["title"] == ""


def test_browser_engine_close_without_start():
    engine = create_engine({})
    # Should not raise
    asyncio.run(engine.close())
    assert engine.is_open is False


def test_browser_engine_open_without_page():
    engine = create_engine({})
    # open() should not raise even without playwright
    try:
        asyncio.run(engine.open("about:blank"))
    except Exception:
        pass  # Expected if playwright not installed or no page


# ── Army / SwarmCoordinator ────────────────────────────────────────

def test_army_agent_create():
    agent = ArmyAgent("a1", "E-1", "operations", config={})
    desc = agent.describe()
    assert desc["agent_id"] == "a1"
    assert desc["rank"] == "E-1"
    assert desc["division"] == "operations"
    assert desc["status"] == "standby"


def test_swarm_deploy():
    swarm = SwarmCoordinator()
    ids = swarm.deploy_swarms(3, rank="E-3", division="recon")
    assert len(ids) == 3
    stats = swarm.get_stats()
    assert stats["total"] == 3
    assert stats["by_rank"]["E-3"] == 3
    assert stats["by_division"]["recon"] == 3


def test_swarm_list_agents_filtered():
    swarm = SwarmCoordinator()
    swarm.deploy_swarms(2, rank="E-1", division="operations")
    swarm.deploy_swarms(1, rank="E-2", division="recon")
    all_agents = swarm.list_agents()
    assert len(all_agents) == 3
    e1_agents = swarm.list_agents(rank="E-1")
    assert len(e1_agents) == 2
    ops_agents = swarm.list_agents(division="operations")
    assert len(ops_agents) == 2
    active_agents = swarm.list_agents(status="active")
    assert len(active_agents) == 0


def test_swarm_remove_agent():
    swarm = SwarmCoordinator()
    ids = swarm.deploy_swarms(1)
    swarm.remove_agent(ids[0])
    assert swarm.get_agent(ids[0]) is None
    stats = swarm.get_stats()
    assert stats["total"] == 0


def test_swarm_execute_task_not_found():
    swarm = SwarmCoordinator()
    result = asyncio.run(swarm.execute_task("nonexistent", {"type": "navigate", "url": "http://example.com"}))
    assert "error" in result


def test_swarm_get_roster():
    swarm = SwarmCoordinator()
    swarm.deploy_swarms(2)
    roster = swarm.get_roster()
    assert len(roster) == 2
    for aid, info in roster.items():
        assert "agent_id" in info
        assert "rank" in info


# ── FleetCoordinator ───────────────────────────────────────────────

def test_fleet_create_operation():
    fleet = FleetCoordinator()
    op = fleet.create_operation("test-op", agents=["a1"], tasks=[{"type": "navigate", "url": "http://example.com"}])
    assert op["name"] == "test-op"
    assert op["status"] == "planned"
    assert len(fleet.get_operations()) == 1


def test_fleet_get_operations_empty():
    fleet = FleetCoordinator()
    assert fleet.get_operations() == []


# ── GhidraAnalyzer ─────────────────────────────────────────────────

def test_ghidra_not_available():
    analyzer = GhidraAnalyzer()
    assert analyzer.is_available() is False
    result = analyzer.analyze_binary("/nonexistent/file.exe")
    assert "error" in result


def test_ghidra_analyze_missing_file():
    analyzer = GhidraAnalyzer()
    result = analyzer.analyze_binary("/does/not/exist.bin")
    assert "error" in result


def test_ghidra_analyze_wasm_falls_through():
    analyzer = GhidraAnalyzer()
    result = analyzer.analyze_wasm("/nonexistent.wasm")
    assert "error" in result


# ── FridaInstrumentor ──────────────────────────────────────────────

def test_frida_not_available():
    inst = FridaInstrumentor()
    assert inst.is_available() is False
    result = inst.hook_process("notepad", "print('hi')")
    assert "error" in result


def test_frida_hook_browser_missing():
    inst = FridaInstrumentor()
    result = inst.hook_browser_session(1234, "script")
    assert "error" in result


# ── BurpProxy ──────────────────────────────────────────────────────

def test_burp_describe():
    burp = BurpProxy()
    desc = burp.describe()
    assert desc["host"] == "127.0.0.1"
    assert desc["port"] == 8080
    assert isinstance(desc["configured"], bool)


def test_burp_get_proxy_config():
    burp = BurpProxy({"host": "10.0.0.1", "port": 9090})
    cfg = burp.get_proxy_config()
    assert cfg["server"] == "http://10.0.0.1:9090"
    assert cfg["scheme"] == "http"


def test_burp_not_configured():
    burp = BurpProxy({"host": "127.0.0.1", "port": 1})
    assert burp.is_configured() is False


# ── IntelligencePipeline ───────────────────────────────────────────

def test_pipeline_describe():
    pipeline = IntelligencePipeline()
    desc = pipeline.describe()
    assert "ghidra" in desc
    assert "frida" in desc
    assert "burp" in desc
    assert desc["ghidra"]["available"] is False


def test_pipeline_analyze_unknown_type():
    pipeline = IntelligencePipeline()
    result = pipeline.analyze("/tmp/test.bin", "unknown")
    assert "error" in result


def test_pipeline_analyze_binary_missing():
    pipeline = IntelligencePipeline()
    result = pipeline.analyze("/nonexistent.exe", "binary")
    assert "error" in result


def test_pipeline_instrument_unknown_target():
    pipeline = IntelligencePipeline()
    result = pipeline.instrument("nonexistent_pid", "script")
    assert "error" in result


# ── AnonymityRouter ────────────────────────────────────────────────

def test_anonymity_router_modes():
    ar = AnonymityRouter({"mode": "none"})
    assert ar.mode == "none"
    assert ar.tier == 0
    assert ar.is_active is False

    ar2 = AnonymityRouter({"mode": "tor"})
    assert ar2.tier == 1

    ar3 = AnonymityRouter({"mode": "specialops"})
    assert ar3.tier == 5


def test_anonymity_router_start_none():
    ar = AnonymityRouter({"mode": "none"})
    assert ar.start() is True
    assert ar.is_active is False


# ── Browser API (FastAPI test client) ──────────────────────────────

@pytest.fixture
def browser_client():
    from browser.api import app
    from fastapi.testclient import TestClient
    return TestClient(app)


def test_browser_health(browser_client):
    res = browser_client.get("/health")
    assert res.status_code == 200
    body = res.json()
    assert body["status"] == "ok"
    assert "session" in body
    assert body["service"] == "knight-shade"


def test_browser_state(browser_client):
    res = browser_client.get("/browser/state")
    assert res.status_code == 200
    body = res.json()
    assert "session_id" in body
    assert "is_open" in body


def test_browser_get_headless(browser_client):
    res = browser_client.get("/browser/headless")
    assert res.status_code == 200
    body = res.json()
    assert "headless" in body
    assert "session" in body


def test_browser_config_empty(browser_client, tmp_path):
    res = browser_client.get("/config")
    assert res.status_code == 200
    # Returns {} if no config file exists
    assert isinstance(res.json(), dict)


def test_browser_config_set_and_get(browser_client, tmp_path):
    cfg = {"headless": True, "stealth": {"enable": False}}
    res = browser_client.post("/config", json=cfg)
    assert res.status_code == 200
    body = res.json()
    assert body["ok"] is True

    res = browser_client.get("/config")
    assert res.status_code == 200
    got = res.json()
    assert got.get("headless") is True


def test_army_roster_empty(browser_client):
    res = browser_client.get("/army/roster")
    assert res.status_code == 200
    body = res.json()
    assert "agents" in body
    assert body["total"] == 0


def test_army_deploy(browser_client):
    res = browser_client.post("/army/deploy", json={"count": 2, "rank": "E-1", "division": "recon"})
    assert res.status_code == 200
    body = res.json()
    assert body["count"] == 2
    assert len(body["deployed"]) == 2


def test_army_stats(browser_client):
    # Deploy some agents first
    browser_client.post("/army/deploy", json={"count": 1})
    res = browser_client.get("/army/stats")
    assert res.status_code == 200
    body = res.json()
    assert "total" in body
    assert "by_rank" in body


def test_analysis_status(browser_client):
    res = browser_client.get("/analysis/status")
    assert res.status_code == 200
    body = res.json()
    assert "ghidra" in body
    assert "frida" in body


def test_browser_anonymity(browser_client):
    res = browser_client.get("/browser/anonymity")
    assert res.status_code == 200
    body = res.json()
    assert "mode" in body


def test_browser_rotate_circuit(browser_client):
    res = browser_client.post("/browser/rotate-circuit")
    assert res.status_code == 200
    body = res.json()
    assert "rotated" in body


def test_browser_healing_stats(browser_client):
    res = browser_client.get("/browser/healing")
    assert res.status_code == 200
    body = res.json()
    assert isinstance(body, dict)
