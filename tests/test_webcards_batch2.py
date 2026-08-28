"""Tests for new dashboard batch2 pages and API routes."""
import pytest
import sys
import os

# Ensure the project root is on the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from dashboard import backend as dash


@pytest.fixture
def client(monkeypatch):
    monkeypatch.setattr(dash, "AUTH_TOKEN", "")
    dash.app.config["TESTING"] = True
    with dash.app.test_client() as c:
        yield c


# ── Wireless Exploitation ───────────────────────────────────────────

class TestWirelessExploitation:
    def test_page_renders(self, client):
        r = client.get("/wireless-exploitation")
        assert r.status_code == 200
        assert b"Wireless Exploitation" in r.data

    def test_wifi_scan_status(self, client):
        r = client.get("/api/wifi-scan/status")
        assert r.status_code == 200
        data = r.get_json()
        assert "networks" in data

    def test_wifi_scan_start(self, client):
        r = client.post("/api/wifi-scan/start", json={})
        assert r.status_code == 200
        data = r.get_json()
        assert data["ok"] is True
        assert data["networks_found"] > 0

    def test_bt_scan_devices(self, client):
        r = client.get("/api/bt-scan/devices")
        assert r.status_code == 200
        data = r.get_json()
        assert "devices" in data

    def test_evil_twin(self, client):
        r = client.post("/api/wireless/evil-twin", json={"target_ssid": "TestNet"})
        assert r.status_code == 200
        data = r.get_json()
        assert data["ok"] is True
        assert "detection" in data


# ── IoT Exploitation ────────────────────────────────────────────────

class TestIoTExploitation:
    def test_page_renders(self, client):
        r = client.get("/iot-exploitation")
        assert r.status_code == 200
        assert b"IoT Exploitation" in r.data

    def test_iot_scan_devices(self, client):
        r = client.get("/api/iot-scan/devices")
        assert r.status_code == 200
        data = r.get_json()
        assert "devices" in data

    def test_iot_scan_start(self, client):
        r = client.post("/api/iot-scan/start", json={"range": "192.168.1.0/24"})
        assert r.status_code == 200
        data = r.get_json()
        assert data["ok"] is True
        assert data["devices_found"] > 0

    def test_iot_firmware(self, client):
        r = client.get("/api/iot/firmware")
        assert r.status_code == 200
        data = r.get_json()
        assert "firmwares" in data

    def test_iot_assess(self, client):
        r = client.post("/api/iot/assess", json={})
        assert r.status_code == 200
        data = r.get_json()
        assert data["ok"] is True
        assert data["vulns_found"] > 0


# ── APT Threat Intelligence ─────────────────────────────────────────

class TestAPTIntelligence:
    def test_page_renders(self, client):
        r = client.get("/apt-intelligence")
        assert r.status_code == 200
        assert b"APT Threat Intelligence" in r.data

    def test_apt_threats(self, client):
        r = client.get("/api/apt/threats")
        assert r.status_code == 200
        data = r.get_json()
        assert "threats" in data
        assert "iocs" in data
        assert "ttps" in data

    def test_apt_groups(self, client):
        r = client.get("/api/apt/groups")
        assert r.status_code == 200
        data = r.get_json()
        assert "groups" in data
        assert len(data["groups"]) > 0

    def test_apt_ttps(self, client):
        r = client.get("/api/apt/ttps")
        assert r.status_code == 200
        data = r.get_json()
        assert "ttps" in data

    def test_apt_feed_refresh(self, client):
        r = client.post("/api/apt/feed/refresh")
        assert r.status_code == 200


# ── Predictive Analytics ────────────────────────────────────────────

class TestPredictiveAnalytics:
    def test_page_renders(self, client):
        r = client.get("/predictive-analytics")
        assert r.status_code == 200
        assert b"Predictive Analytics" in r.data

    def test_analytics_alerts(self, client):
        r = client.get("/api/analytics/alerts")
        assert r.status_code == 200
        data = r.get_json()
        assert "alerts" in data

    def test_analytics_predict(self, client):
        r = client.post("/api/analytics/predict", json={})
        assert r.status_code == 200
        data = r.get_json()
        assert "forecast" in data
        assert "trends" in data

    def test_analytics_trends(self, client):
        r = client.get("/api/analytics/trends")
        assert r.status_code == 200
        data = r.get_json()
        assert "trends" in data

    def test_analytics_risk_score(self, client):
        r = client.get("/api/analytics/risk-score")
        assert r.status_code == 200
        data = r.get_json()
        assert "score" in data


# ── Incident Response ───────────────────────────────────────────────

class TestIncidentResponse:
    def test_page_renders(self, client):
        r = client.get("/incident-response")
        assert r.status_code == 200
        assert b"Incident Response" in r.data

    def test_incidents_list(self, client):
        r = client.get("/api/incidents/list")
        assert r.status_code == 200
        data = r.get_json()
        assert "incidents" in data

    def test_incidents_create(self, client):
        r = client.post("/api/incidents/create", json={
            "title": "Test Incident",
            "severity": "high",
            "description": "Created by test",
        })
        assert r.status_code == 200
        data = r.get_json()
        assert data["ok"] is True
        assert "incident" in data

    def test_incidents_update_status(self, client):
        # Create first
        r = client.post("/api/incidents/create", json={"title": "Status Test", "severity": "low"})
        assert r.status_code == 200
        inc_id = r.get_json()["incident"]["id"]
        # Update
        r = client.put(f"/api/incidents/{inc_id}/status", json={"status": "investigating"})
        assert r.status_code == 200
        data = r.get_json()
        assert data["ok"] is True
        assert data["incident"]["status"] == "investigating"

    def test_incidents_playbooks(self, client):
        r = client.get("/api/incidents/playbooks")
        assert r.status_code == 200
        data = r.get_json()
        assert "playbooks" in data
        assert len(data["playbooks"]) > 0


# ── AI Red Teaming ──────────────────────────────────────────────────

class TestAIRedTeaming:
    def test_page_renders(self, client):
        r = client.get("/ai-red-teaming")
        assert r.status_code == 200
        assert b"AI Red Teaming" in r.data

    def test_redteam_campaigns(self, client):
        r = client.get("/api/ai-redteam/campaigns")
        assert r.status_code == 200
        data = r.get_json()
        assert "campaigns" in data

    def test_redteam_start(self, client):
        r = client.post("/api/ai-redteam/start", json={
            "name": "Test Campaign",
            "target": "test.target",
            "type": "vulnerability_discovery",
        })
        assert r.status_code == 200
        data = r.get_json()
        assert data["ok"] is True
        assert "campaign" in data

    def test_redteam_results(self, client):
        r = client.get("/api/ai-redteam/results")
        assert r.status_code == 200
        data = r.get_json()
        assert "results" in data

    def test_redteam_remediate(self, client):
        r = client.post("/api/ai-redteam/remediate", json={
            "vulnerability": "SQL Injection",
            "remediation": "Apply parameterized queries",
        })
        assert r.status_code == 200
        data = r.get_json()
        assert data["ok"] is True
        assert "remediation" in data
