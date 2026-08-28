"""Tests for batch 3 dashboard pages: vuln-scanner, identity-mgmt,
proxy-chain, realtime-monitor, threat-intel."""
import json
import pytest

flask = pytest.importorskip("flask")

from dashboard import backend as dash  # noqa: E402


@pytest.fixture()
def client(tmp_path, monkeypatch):
    monkeypatch.setattr(dash, "CONFIG_DIR", tmp_path)
    monkeypatch.setattr(dash, "SKILLS_DIR", tmp_path / "skills")
    monkeypatch.setattr(dash, "ACTIVITY_LOG", tmp_path / "activity_log.jsonl")
    monkeypatch.setattr(dash, "UPLOAD_DIR", tmp_path / "uploads")
    monkeypatch.setattr(dash, "SALAD_API_KEY", "")
    monkeypatch.setattr(dash, "_SALAD_API_KEY", "")
    monkeypatch.setattr(dash, "AIKIDO_API_KEY", "")
    monkeypatch.setattr(dash, "AIKIDO_APP_ID", "")
    monkeypatch.setattr(dash, "OPT_SETTINGS_PATH",
                        str(tmp_path / "runtime-settings.json"))
    monkeypatch.setattr(dash, "PRESETS_PATH",
                        str(tmp_path / "presets.json"))
    monkeypatch.setattr(dash, "PROVIDERS_MERGED_PATH",
                        str(tmp_path / "providers-merged.json"))
    monkeypatch.setattr(dash, "HERMES_CONFIG_PATH",
                        tmp_path / "hermes.json")
    monkeypatch.setattr(dash, "_SCHEDULER_CONFIG_PATH",
                        str(tmp_path / "scheduler.json"))
    dash._SUBAGENTS.clear()
    dash._TRAINING_DATA.update({
        "datasets": [], "jobs": {"sft": [], "dpo": [], "abr": []},
        "models": [],
    })
    dash._MEMORY_STATE["projects"].clear()
    dash._MEMORY_STATE["learnings"].clear()
    dash._AUTOMATIONS["jobs"].clear()
    dash._AUTOMATIONS["history"].clear()
    dash._campaigns.clear()
    dash._scheduler_jobs.clear()
    dash._gpu_state["devices"] = []
    dash._gpu_state["total_vram_mb"] = 0
    dash._gpu_state["used_vram_mb"] = 0
    dash._uploads.clear()
    dash._SALAD_API_KEY = ""
    dash._SALAD_CACHE = {"salad": None, "gpu": None, "ts": 0.0}
    dash.app.config["TESTING"] = True
    dash.app.config["SECRET_KEY"] = "test-secret-key-for-evals"
    with dash.app.test_client() as c:
        yield c


# ── Page Routes ──────────────────────────────────────────────────

def test_page_vuln_scanner(client):
    res = client.get("/vuln-scanner")
    assert res.status_code == 200


def test_page_identity_mgmt(client):
    res = client.get("/identity-mgmt")
    assert res.status_code == 200


def test_page_proxy_chain(client):
    res = client.get("/proxy-chain")
    assert res.status_code == 200


def test_page_realtime_monitor(client):
    res = client.get("/realtime-monitor")
    assert res.status_code == 200


def test_page_threat_intel(client):
    res = client.get("/threat-intel")
    assert res.status_code == 200


# ── Vulnerability Scanner API ────────────────────────────────────

def test_vuln_scan_status_empty(client):
    res = client.get("/api/vuln-scan/status")
    assert res.status_code == 200
    body = res.get_json()
    assert body["total_scans"] == 0
    assert body["running"] is False


def test_vuln_scan_start_and_results(client):
    res = client.post("/api/vuln-scan/start", json={"target": "10.0.0.0/24"})
    assert res.status_code == 200
    body = res.get_json()
    assert body["ok"] is True
    assert body["found"] >= 2
    assert body["total_scans"] >= 1
    res = client.get("/api/vuln-scan/results")
    assert res.status_code == 200
    data = res.get_json()
    assert data["total"] >= 2
    assert "cve" in data["results"][0]
    assert "risk" in data["results"][0]


def test_vuln_scan_schedule(client):
    res = client.post("/api/vuln-scan/schedule", json={
        "target": "192.168.1.0/24", "cron": "0 3 * * *", "profile": "deep"})
    assert res.status_code == 200
    body = res.get_json()
    assert body["ok"] is True
    assert body["schedule"]["target"] == "192.168.1.0/24"


def test_vuln_scan_status_after_scan(client):
    client.post("/api/vuln-scan/start", json={"target": "10.0.0.1"})
    res = client.get("/api/vuln-scan/status")
    assert res.status_code == 200
    body = res.get_json()
    assert body["total_scans"] >= 1
    assert body["running"] is False


# ── Identity Management API ──────────────────────────────────────

def test_identity_users_empty(client):
    res = client.get("/api/identity/users")
    assert res.status_code == 200
    body = res.get_json()
    assert body["users"] == []
    assert body["total"] == 0


def test_identity_add_user(client):
    res = client.post("/api/identity/monitor", json={
        "action": "add_user", "username": "alice", "role": "admin",
        "email": "alice@example.com"})
    assert res.status_code == 200
    body = res.get_json()
    assert body["ok"] is True
    assert body["user"]["username"] == "alice"
    assert body["user"]["role"] == "admin"
    res = client.get("/api/identity/users")
    assert res.get_json()["total"] == 1


def test_identity_sessions_empty(client):
    res = client.get("/api/identity/sessions")
    assert res.status_code == 200
    body = res.get_json()
    assert body["sessions"] == []


def test_identity_log_event(client):
    res = client.post("/api/identity/monitor", json={
        "username": "bob", "event_type": "login",
        "ip": "10.0.0.5", "status": "success"})
    assert res.status_code == 200
    body = res.get_json()
    assert body["ok"] is True
    assert body["events"] >= 1


def test_identity_update_role(client):
    client.post("/api/identity/monitor", json={
        "action": "add_user", "username": "charlie", "role": "viewer"})
    res = client.get("/api/identity/users")
    user_id = res.get_json()["users"][0]["id"]
    res = client.put("/api/identity/roles", json={
        "user_id": user_id, "role": "admin"})
    assert res.status_code == 200
    body = res.get_json()
    assert body["user"]["role"] == "admin"


def test_identity_role_not_found(client):
    res = client.put("/api/identity/roles", json={
        "user_id": 9999, "role": "admin"})
    assert res.status_code == 404


# ── Proxy Chain API ──────────────────────────────────────────────

def test_proxy_chain_status_empty(client):
    res = client.get("/api/proxy-chain/status")
    assert res.status_code == 200
    body = res.get_json()
    assert body["chain"] == []
    assert body["rotations"] == 0


def test_proxy_chain_rotate(client):
    res = client.get("/api/proxy-chain/rotate")
    assert res.status_code == 200
    body = res.get_json()
    assert body["ok"] is True
    assert body["rotations"] >= 1
    assert len(body["chain"]) == 3


def test_proxy_chain_rotate_post(client):
    res = client.post("/api/proxy-chain/rotate")
    assert res.status_code == 200
    body = res.get_json()
    assert body["rotations"] >= 1


def test_proxy_chain_configure(client):
    proxies = [
        {"address": "1.2.3.4:9050", "type": "tor", "location": "US",
         "latency_ms": 50, "health": "good"},
        {"address": "5.6.7.8:3128", "type": "http", "location": "UK",
         "latency_ms": 30, "health": "good"},
    ]
    res = client.post("/api/proxy-chain/configure", json={"proxies": proxies})
    assert res.status_code == 200
    body = res.get_json()
    assert body["ok"] is True
    assert len(body["chain"]) == 2


def test_proxy_chain_health(client):
    client.get("/api/proxy-chain/rotate")
    res = client.get("/api/proxy-chain/health")
    assert res.status_code == 200
    body = res.get_json()
    assert "total_latency_ms" in body
    assert "chain_length" in body
    assert body["chain_length"] == 3


# ── Real-Time Monitoring API ─────────────────────────────────────

def test_monitor_metrics(client):
    res = client.get("/api/monitor/metrics")
    assert res.status_code == 200
    body = res.get_json()
    assert "cpu_percent" in body
    assert "memory_percent" in body
    assert "bytes_sent" in body
    assert "timestamp" in body


def test_monitor_alerts_empty(client):
    res = client.get("/api/monitor/alerts")
    assert res.status_code == 200
    body = res.get_json()
    assert body["alerts"] == []


def test_monitor_configure(client):
    res = client.post("/api/monitor/configure", json={
        "cpu_threshold": 95, "mem_threshold": 90})
    assert res.status_code == 200
    body = res.get_json()
    assert body["ok"] is True
    assert body["config"]["cpu_threshold"] == 95


def test_monitor_anomalies_empty(client):
    res = client.get("/api/monitor/anomalies")
    assert res.status_code == 200
    body = res.get_json()
    assert body["anomalies"] == []


# ── Threat Intelligence API ──────────────────────────────────────

def test_threat_intel_feeds(client):
    res = client.get("/api/threat-intel/feeds")
    assert res.status_code == 200
    body = res.get_json()
    assert body["total"] >= 3
    assert any(f["name"] == "AlienVault OTX" for f in body["feeds"])


def test_threat_intel_iocs(client):
    res = client.get("/api/threat-intel/iocs")
    assert res.status_code == 200
    body = res.get_json()
    assert body["total"] >= 4
    assert any(i["ioc_type"] == "ip" for i in body["iocs"])


def test_threat_intel_actors(client):
    res = client.get("/api/threat-intel/actors")
    assert res.status_code == 200
    body = res.get_json()
    assert body["total"] >= 3
    assert any(a["actor_name"] == "APT-28" for a in body["actors"])


def test_threat_intel_refresh(client):
    res = client.post("/api/threat-intel/refresh")
    assert res.status_code == 200
    body = res.get_json()
    assert body["ok"] is True
    assert body["new_iocs"] >= 2
    assert body["last_refresh"] > 0


def test_threat_intel_iocs_after_refresh(client):
    client.post("/api/threat-intel/refresh")
    res = client.get("/api/threat-intel/iocs")
    assert res.status_code == 200
    body = res.get_json()
    assert body["total"] >= 6  # 4 initial + 2 from refresh
