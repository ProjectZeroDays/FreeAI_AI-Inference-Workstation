"""Tests for 9 new zero-click exploit agent skills: iOS, Android, macOS, Windows, Linux, IoT, Bluetooth, NFC, Automobile."""
import pytest
import json

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
    return dash.app.test_client()


# ── iOS ──────────────────────────────────────────────────────────────
class TestIOSExploit:
    def test_describe(self, client):
        r = client.get("/api/ios-exploit/describe")
        assert r.status_code == 200
        data = r.get_json()
        assert data["name"] == "ios_exploit"
        assert "imageio_rce" in data["capabilities"]

    def test_image_exploit(self, client):
        r = client.post("/api/ios-exploit/image",
                        json={"target": "192.168.1.100", "vector": "imageio_overflow"})
        assert r.status_code == 200
        d = r.get_json()
        assert d["zero_click"] is True
        assert d["cve"] == "CVE-2019-8641"

    def test_imessage_exploit(self, client):
        r = client.post("/api/ios-exploit/imessage",
                        json={"target": "+1234567890", "vector": "rtcp_rce"})
        assert r.status_code == 200
        assert r.get_json()["zero_click"] is True

    def test_webkit_exploit(self, client):
        r = client.post("/api/ios-exploit/webkit",
                        json={"target": "https://evil.com"})
        assert r.status_code == 200
        assert r.get_json()["zero_click"] is False

    def test_kernel_exploit(self, client):
        r = client.post("/api/ios-exploit/kernel",
                        json={"target": "192.168.1.100"})
        assert r.status_code == 200
        assert r.get_json()["impact"] == "kernel_root"

    def test_cves(self, client):
        r = client.get("/api/ios-exploit/cves")
        assert r.status_code == 200
        cves = r.get_json()
        assert "CVE-2019-8641" in cves


# ── Android ──────────────────────────────────────────────────────────
class TestAndroidExploit:
    def test_describe(self, client):
        r = client.get("/api/android-exploit/describe")
        assert r.status_code == 200
        assert "mms_rce" in r.get_json()["capabilities"]

    def test_mms(self, client):
        r = client.post("/api/android-exploit/mms",
                        json={"target": "+1234567890"})
        assert r.status_code == 200
        assert r.get_json()["cve"] == "CVE-2021-1055"

    def test_image(self, client):
        r = client.post("/api/android-exploit/image",
                        json={"target": "192.168.1.100"})
        assert r.get_json()["cve"] == "CVE-2022-2051"

    def test_bluetooth(self, client):
        r = client.post("/api/android-exploit/bluetooth",
                        json={"target": "AA:BB:CC:DD:EE:FF"})
        assert r.get_json()["cve"] == "CVE-2017-0781"

    def test_nfc(self, client):
        r = client.post("/api/android-exploit/nfc",
                        json={"target": "nfc_tag"})
        assert r.get_json()["zero_click"] is False

    def test_kernel(self, client):
        r = client.post("/api/android-exploit/kernel",
                        json={"target": "192.168.1.100"})
        assert r.get_json()["impact"] == "root_privilege_escalation"

    def test_cves(self, client):
        r = client.get("/api/android-exploit/cves")
        assert "CVE-2021-1055" in r.get_json()


# ── macOS ────────────────────────────────────────────────────────────
class TestmacOSExploit:
    def test_describe(self, client):
        r = client.get("/api/macos-exploit/describe")
        assert r.status_code == 200
        assert "imageio_rce" in r.get_json()["capabilities"]

    def test_image(self, client):
        r = client.post("/api/macos-exploit/image",
                        json={"target": "192.168.1.100"})
        assert r.get_json()["cve"] == "CVE-2021-30770"

    def test_safari(self, client):
        r = client.post("/api/macos-exploit/safari",
                        json={"target": "https://evil.com"})
        assert r.get_json()["cve"] == "CVE-2022-22616"

    def test_metal(self, client):
        r = client.post("/api/macos-exploit/metal",
                        json={"target": "192.168.1.100"})
        assert r.get_json()["cve"] == "CVE-2023-32629"

    def test_kernel(self, client):
        r = client.post("/api/macos-exploit/kernel",
                        json={"target": "192.168.1.100"})
        assert r.get_json()["impact"] == "kernel_root"

    def test_cves(self, client):
        r = client.get("/api/macos-exploit/cves")
        assert "CVE-2021-30770" in r.get_json()


# ── Windows ──────────────────────────────────────────────────────────
class TestWindowsExploit:
    def test_describe(self, client):
        r = client.get("/api/windows-exploit/describe")
        assert r.status_code == 200
        assert "eternalblue" in r.get_json()["capabilities"]

    def test_eternalblue(self, client):
        r = client.post("/api/windows-exploit/eternalblue",
                        json={"target": "192.168.1.100"})
        assert r.get_json()["cve"] == "CVE-2017-0144"

    def test_exchange(self, client):
        r = client.post("/api/windows-exploit/exchange",
                        json={"target": "mail.corp.local"})
        assert r.get_json()["cve"] == "CVE-2021-26855"

    def test_printnightmare(self, client):
        r = client.post("/api/windows-exploit/printnightmare",
                        json={"target": "192.168.1.100"})
        assert r.get_json()["cve"] == "CVE-2021-34527"

    def test_doc(self, client):
        r = client.post("/api/windows-exploit/doc",
                        json={"target": "victim@corp.com"})
        assert r.get_json()["zero_click"] is False

    def test_kernel_chain(self, client):
        r = client.post("/api/windows-exploit/kernel-chain",
                        json={"target": "192.168.1.100"})
        assert r.get_json()["impact"] == "nt_system"

    def test_cves(self, client):
        r = client.get("/api/windows-exploit/cves")
        assert "CVE-2017-0144" in r.get_json()


# ── Linux ────────────────────────────────────────────────────────────
class TestLinuxExploit:
    def test_describe(self, client):
        r = client.get("/api/linux-exploit/describe")
        assert r.status_code == 200
        assert "dirty_pipe" in r.get_json()["capabilities"]

    def test_dirty_pipe(self, client):
        r = client.post("/api/linux-exploit/dirty-pipe",
                        json={"target": "192.168.1.100"})
        assert r.get_json()["cve"] == "CVE-2022-0847"

    def test_docker_escape(self, client):
        r = client.post("/api/linux-exploit/docker-escape",
                        json={"target": "192.168.1.100"})
        assert r.get_json()["impact"] == "host_root"

    def test_glibc_heap(self, client):
        r = client.post("/api/linux-exploit/glibc-heap",
                        json={"target": "192.168.1.100"})
        assert r.get_json()["zero_click"] is True

    def test_systemd(self, client):
        r = client.post("/api/linux-exploit/systemd",
                        json={"target": "192.168.1.100"})
        assert r.get_json()["impact"] == "root_persistence"

    def test_cves(self, client):
        r = client.get("/api/linux-exploit/cves")
        assert "CVE-2022-0847" in r.get_json()


# ── IoT ──────────────────────────────────────────────────────────────
class TestIoTExploit:
    def test_describe(self, client):
        r = client.get("/api/iot-exploit/describe")
        assert r.status_code == 200
        assert "firmware_extract" in r.get_json()["capabilities"]

    def test_firmware(self, client):
        r = client.post("/api/iot-exploit/firmware",
                        json={"target_ip": "192.168.1.50"})
        assert r.get_json()["status"] == "simulated"

    def test_hardware_debug(self, client):
        r = client.post("/api/iot-exploit/hardware-debug",
                        json={"target_ip": "192.168.1.50", "interface": "uart"})
        assert r.get_json()["capabilities"]["uart_console"] is True

    def test_default_creds(self, client):
        r = client.post("/api/iot-exploit/default-creds",
                        json={"target_ip": "192.168.1.50"})
        assert len(r.get_json()["credentials_found"]) >= 2

    def test_mqtt(self, client):
        r = client.post("/api/iot-exploit/mqtt",
                        json={"target_ip": "192.168.1.50", "topic": "home/test"})
        assert "topic_enumeration" in r.get_json()["techniques"]

    def test_cves(self, client):
        r = client.get("/api/iot-exploit/cves")
        assert "CVE-2021-3918" in r.get_json()


# ── Bluetooth ────────────────────────────────────────────────────────
class TestBluetoothExploit:
    def test_describe(self, client):
        r = client.get("/api/bluetooth-exploit/describe")
        assert r.status_code == 200
        assert "blueborne" in r.get_json()["capabilities"]

    def test_blueborne(self, client):
        r = client.post("/api/bluetooth-exploit/blueborne",
                        json={"target_mac": "AA:BB:CC:DD:EE:FF"})
        assert r.get_json()["cve"] == "CVE-2017-0781"
        assert r.get_json()["range_meters"] == 100

    def test_ble_sniff(self, client):
        r = client.post("/api/bluetooth-exploit/ble-sniff",
                        json={"target_mac": "AA:BB:CC:DD:EE:FF"})
        assert "access_address_prediction" in r.get_json()["techniques"]

    def test_ble_deauth(self, client):
        r = client.post("/api/bluetooth-exploit/ble-deauth",
                        json={"target_mac": "AA:BB:CC:DD:EE:FF"})
        assert r.get_json()["status"] == "simulated"

    def test_keyless(self, client):
        r = client.post("/api/bluetooth-exploit/keyless",
                        json={"target_vehicle": "Tesla Model 3"})
        assert r.get_json()["impact"] == "vehicle_compromise"

    def test_cves(self, client):
        r = client.get("/api/bluetooth-exploit/cves")
        assert "CVE-2017-0781" in r.get_json()


# ── NFC ──────────────────────────────────────────────────────────────
class TestNFCExploit:
    def test_describe(self, client):
        r = client.get("/api/nfc-exploit/describe")
        assert r.status_code == 200
        assert "emv_clone" in r.get_json()["capabilities"]

    def test_emv_clone(self, client):
        r = client.post("/api/nfc-exploit/emv-clone",
                        json={"target_card": "visa_contactless"})
        assert "atr_parsing" in r.get_json()["techniques"]

    def test_relay(self, client):
        r = client.post("/api/nfc-exploit/relay",
                        json={"target_reader": "terminal1", "target_card": "card1"})
        assert r.get_json()["techniques"][0] == "real_time_relay"

    def test_rfid_skim(self, client):
        r = client.post("/api/nfc-exploit/rfid-skim",
                        json={"target_card": "prox_card"})
        assert "EM4100" in r.get_json()["supported_formats"]

    def test_ndef_inject(self, client):
        r = client.post("/api/nfc-exploit/ndef-inject",
                        json={"target_tag": "smart_poster", "new_url": "http://evil.com"})
        assert "tag_rewrite" in r.get_json()["techniques"]

    def test_payment_intercept(self, client):
        r = client.post("/api/nfc-exploit/payment-intercept",
                        json={"target_terminal": "pos_terminal"})
        assert "amount_manipulation" in r.get_json()["techniques"]

    def test_cves(self, client):
        r = client.get("/api/nfc-exploit/cves")
        assert "CVE-2020-8903" in r.get_json()


# ── Automobile ───────────────────────────────────────────────────────
class TestAutomobileExploit:
    def test_describe(self, client):
        r = client.get("/api/automobile-exploit/describe")
        assert r.status_code == 200
        assert "can_inject" in r.get_json()["capabilities"]

    def test_can_inject(self, client):
        r = client.post("/api/automobile-exploit/can-inject",
                        json={"target_vid": "Tesla Model 3", "vector": "brake_cmd_replay"})
        assert "frame_replay" in r.get_json()["techniques"]

    def test_obd2(self, client):
        r = client.post("/api/automobile-exploit/obd2",
                        json={"target_vid": "Ford F-150", "session": 16, "subfunc": 1})
        assert r.get_json()["diagnostic_modes"]["0x10"] == "Diagnostic Session Control"

    def test_keyless(self, client):
        r = client.post("/api/automobile-exploit/keyless",
                        json={"target_vid": "BMW 5 Series"})
        assert r.get_json()["range_meters"] == 50

    def test_infotainment(self, client):
        r = client.post("/api/automobile-exploit/infotainment",
                        json={"target_vid": "Tesla Model 3"})
        assert "QNX" in r.get_json()["platforms"]

    def test_telematics(self, client):
        r = client.post("/api/automobile-exploit/telematics",
                        json={"target_vid": "Chevy Bolt EV"})
        assert "OnStar" in r.get_json()["services"]

    def test_cves(self, client):
        r = client.get("/api/automobile-exploit/cves")
        assert "CVE-2015-5227" in r.get_json()
