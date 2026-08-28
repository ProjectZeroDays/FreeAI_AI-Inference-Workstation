#!/usr/bin/env python3
"""Tests for Messaging RCE Agent."""
import json
import os
import sys
import unittest
from unittest.mock import patch

# Ensure project root is on path
PROJECT_ROOT = os.path.join(os.path.dirname(__file__), "..")
sys.path.insert(0, PROJECT_ROOT)


class TestMessagingRCE(unittest.TestCase):
    """Test all 6 messaging RCE API routes return active responses with MITRE mappings."""

    def setUp(self):
        """Set up Flask test client."""
        from dashboard.backend import app
        app.config["TESTING"] = True
        self.client = app.test_client()
        self.base = "/api/exploit-cat/messaging-rce"

    # ── Describe ──

    def test_messaging_rce_describe(self):
        resp = self.client.get(f"{self.base}/describe")
        self.assertEqual(resp.status_code, 200)
        data = resp.get_json()
        self.assertEqual(data["name"], "messaging_rce")
        self.assertIn("imessage_exploit", data["capabilities"])
        self.assertIn("mitre_technique", data)
        self.assertEqual(data["mitre_technique"]["id"], "T1203")

    # ── iMessage ──

    def test_messaging_rce_simulate_imessage(self):
        resp = self.client.post(f"{self.base}/simulate-imessage",
                                json={"target": "iphone_user", "exploit_type": "rce"},
                                headers={"X-Auth-Token": "test-key"})
        self.assertEqual(resp.status_code, 200)
        data = resp.get_json()
        self.assertEqual(data["status"], "active")
        self.assertEqual(data["target"], "iphone_user")
        self.assertEqual(data["vector"], "iMessage media processing")
        self.assertEqual(data["mitre_id"], "T1203")
        self.assertIn("exploitation_steps", data)

    # ── WhatsApp ──

    def test_messaging_rce_simulate_whatsapp(self):
        resp = self.client.post(f"{self.base}/simulate-whatsapp",
                                json={"target": "whatsapp_user", "exploit_type": "rce"},
                                headers={"X-Auth-Token": "test-key"})
        self.assertEqual(resp.status_code, 200)
        data = resp.get_json()
        self.assertEqual(data["status"], "active")
        self.assertEqual(data["target"], "whatsapp_user")
        self.assertEqual(data["mitre_id"], "T1203")

    # ── Signal ──

    def test_messaging_rce_simulate_signal(self):
        resp = self.client.post(f"{self.base}/simulate-signal",
                                json={"target": "signal_user", "exploit_type": "rce"},
                                headers={"X-Auth-Token": "test-key"})
        self.assertEqual(resp.status_code, 200)
        data = resp.get_json()
        self.assertEqual(data["status"], "active")
        self.assertEqual(data["target"], "signal_user")
        self.assertEqual(data["mitre_id"], "T1203")

    # ── Generate Payload ──

    def test_messaging_rce_generate_payload(self):
        resp = self.client.post(f"{self.base}/generate-payload",
                                json={"platform": "imessage", "payload_type": "rce"},
                                headers={"X-Auth-Token": "test-key"})
        self.assertEqual(resp.status_code, 200)
        data = resp.get_json()
        self.assertEqual(data["status"], "active")
        self.assertEqual(data["platform"], "imessage")
        self.assertEqual(data["format"], "crafted_media")
        self.assertEqual(data["mitre_id"], "T1203")

    # ── Primitives ──

    def test_messaging_rce_primitives(self):
        resp = self.client.get(f"{self.base}/primitives")
        self.assertEqual(resp.status_code, 200)
        data = resp.get_json()
        self.assertIsInstance(data, list)
        self.assertIn("media_processing", data)
        self.assertIn("protocol_parsing", data)

    # ── CVEs ──

    def test_messaging_rce_cves(self):
        resp = self.client.get(f"{self.base}/cves")
        self.assertEqual(resp.status_code, 200)
        data = resp.get_json()
        self.assertIsInstance(data, list)
        self.assertEqual(len(data), 5)
        self.assertEqual(data[0]["id"], "CVE-2019-8641")
        self.assertEqual(data[0]["severity"], "critical")


if __name__ == "__main__":
    unittest.main()
