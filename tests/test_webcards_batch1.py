"""Tests for new dashboard pages: Device Fingerprint, Social Engineering,
Zero-Day, Malware Analysis, Network Exploitation, Cloud Exploitation."""
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
    monkeypatch.setattr(dash, "OPT_SETTINGS_PATH", str(tmp_path / "runtime-settings.json"))
    monkeypatch.setattr(dash, "PRESETS_PATH", str(tmp_path / "presets.json"))
    monkeypatch.setattr(dash, "PROVIDERS_MERGED_PATH", str(tmp_path / "providers-merged.json"))
    monkeypatch.setattr(dash, "HERMES_CONFIG_PATH", tmp_path / "hermes.json")
    monkeypatch.setattr(dash, "_SCHEDULER_CONFIG_PATH", str(tmp_path / "scheduler.json"))
    dash._SUBAGENTS.clear()
    dash._TRAINING_DATA.update({"datasets": [], "jobs": {"sft": [], "dpo": [], "abr": []}, "models": []})
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
    dash._SALAD_CACHE = {"salad": None, "gpu": None, "ts": 0.0}
    dash.app.config["TESTING"] = True
    dash.app.config["SECRET_KEY"] = "test-secret-key-for-evals"
    with dash.app.test_client() as c:
        yield c


# ── Page Routes ─────────────────────────────────────────────────────

def test_device_fingerprint_page(client):
    res = client.get("/device-fingerprint")
    assert res.status_code == 200
    assert b"Device Fingerprinting" in res.data


def test_social_engineering_page(client):
    res = client.get("/social-engineering")
    assert res.status_code == 200
    assert b"Social Engineering" in res.data


def test_zero_day_page(client):
    res = client.get("/zero-day")
    assert res.status_code == 200
    assert b"Zero-Day Exploits" in res.data


def test_malware_analysis_page(client):
    res = client.get("/malware-analysis")
    assert res.status_code == 200
    assert b"Malware Analysis" in res.data


def test_network_exploitation_page(client):
    res = client.get("/network-exploitation")
    assert res.status_code == 200
    assert b"Network Exploitation" in res.data


def test_cloud_exploitation_page(client):
    res = client.get("/cloud-exploitation")
    assert res.status_code == 200
    assert b"Cloud Exploitation" in res.data


# ── Device Fingerprinting API ───────────────────────────────────────

def test_fingerprint_detect(client):
    res = client.get("/api/fingerprint/detect")
    assert res.status_code == 200
    body = res.get_json()
    assert "hash" in body
    assert "components" in body
    assert len(body["components"]) > 0


def test_fingerprint_compare(client):
    res = client.post("/api/fingerprint/compare", json={"hash_a": "abc123", "hash_b": "abc123"})
    assert res.status_code == 200
    body = res.get_json()
    assert body["match"] is True


def test_fingerprint_compare_different(client):
    res = client.post("/api/fingerprint/compare", json={"hash_a": "abc123", "hash_b": "def456"})
    assert res.status_code == 200
    body = res.get_json()
    assert body["match"] is False


def test_fingerprint_tips(client):
    res = client.get("/api/fingerprint/tips")
    assert res.status_code == 200
    body = res.get_json()
    assert "tips" in body
    assert len(body["tips"]) > 0


# ── Social Engineering API ──────────────────────────────────────────

def test_social_eng_templates(client):
    res = client.get("/api/social-eng/templates")
    assert res.status_code == 200
    body = res.get_json()
    assert "templates" in body
    assert len(body["templates"]) > 0


def test_social_eng_generate(client):
    res = client.post("/api/social-eng/generate", json={"category": "phishing", "target": "test"})
    assert res.status_code == 200
    body = res.get_json()
    assert body["ok"] is True
    assert "template" in body


def test_social_eng_generate_vishing(client):
    res = client.post("/api/social-eng/generate", json={"category": "vishing"})
    assert res.status_code == 200
    body = res.get_json()
    assert body["ok"] is True
    assert body["category"] == "vishing"


def test_social_eng_quiz(client):
    res = client.get("/api/social-eng/quiz")
    assert res.status_code == 200
    body = res.get_json()
    assert "questions" in body
    assert len(body["questions"]) > 0


# ── Zero-Day Exploits API ───────────────────────────────────────────

def test_exploits_cve_search(client):
    res = client.get("/api/exploits/cve/search")
    assert res.status_code == 200
    body = res.get_json()
    assert isinstance(body, list)
    assert len(body) > 0


def test_exploits_cve_search_with_query(client):
    res = client.get("/api/exploits/cve/search?q=CVE-2024")
    assert res.status_code == 200
    body = res.get_json()
    assert isinstance(body, list)


def test_exploits_db(client):
    res = client.get("/api/exploits/db")
    assert res.status_code == 200
    body = res.get_json()
    assert isinstance(body, list)
    assert len(body) > 0


def test_exploits_poc(client):
    res = client.post("/api/exploits/poc", json={"cve_id": "CVE-2024-9999", "language": "python"})
    assert res.status_code == 200
    body = res.get_json()
    assert body["ok"] is True
    assert "poc" in body


def test_exploits_chains(client):
    res = client.get("/api/exploits/chains")
    assert res.status_code == 200
    body = res.get_json()
    assert isinstance(body, list)
    assert len(body) > 0


# ── Malware Analysis API ────────────────────────────────────────────

def test_malware_hash_lookup(client):
    res = client.get("/api/malware/hash/abc123def456")
    assert res.status_code == 200
    body = res.get_json()
    assert body["hash"] == "abc123def456"
    assert "static_analysis" in body


def test_malware_analyze(client):
    res = client.post("/api/malware/analyze", json={"hash": "test123", "filename": "sample.exe"})
    assert res.status_code == 200
    body = res.get_json()
    assert body["hash"] == "test123"
    assert "static_analysis" in body


def test_malware_yara(client):
    res = client.get("/api/malware/yara")
    assert res.status_code == 200
    body = res.get_json()
    assert isinstance(body, list)
    assert len(body) > 0


def test_malware_classes(client):
    res = client.get("/api/malware/classes")
    assert res.status_code == 200
    body = res.get_json()
    assert isinstance(body, list)
    assert len(body) > 0


# ── Network Exploitation API ────────────────────────────────────────

def test_net_scan_status(client):
    res = client.get("/api/net-scan/status")
    assert res.status_code == 200
    body = res.get_json()
    assert "running" in body
    assert "hosts" in body


def test_net_scan_start(client):
    res = client.post("/api/net-scan/start", json={"target": "192.168.1.0/24", "ports": "1-1024"})
    assert res.status_code == 200
    body = res.get_json()
    assert body["ok"] is True
    assert "hosts" in body
    assert len(body["hosts"]) > 0


def test_wireless_handshakes(client):
    res = client.get("/api/wireless/handshakes")
    assert res.status_code == 200
    body = res.get_json()
    assert "handshakes" in body
    assert len(body["handshakes"]) > 0


def test_wireless_analyze(client):
    res = client.post("/api/wireless/analyze", json={"ssid": "TestNet", "encryption": "WPA2"})
    assert res.status_code == 200
    body = res.get_json()
    assert body["ok"] is True
    assert "analysis" in body


# ── Cloud Exploitation API ──────────────────────────────────────────

def test_cloud_configs(client):
    res = client.get("/api/cloud/configs")
    assert res.status_code == 200
    body = res.get_json()
    assert isinstance(body, list)
    assert len(body) > 0


def test_cloud_scan(client):
    res = client.post("/api/cloud/scan", json={"providers": ["aws", "azure", "gcp"]})
    assert res.status_code == 200
    body = res.get_json()
    assert body["ok"] is True
    assert "findings" in body


def test_cloud_iam(client):
    res = client.get("/api/cloud/iam")
    assert res.status_code == 200
    body = res.get_json()
    assert isinstance(body, list)
    assert len(body) > 0


def test_cloud_exploit_sim(client):
    res = client.post("/api/cloud/exploit-sim", json={"scenario": "metadata_abuse"})
    assert res.status_code == 200
    body = res.get_json()
    assert body["ok"] is True
    assert "steps" in body
