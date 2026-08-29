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
    """Test all 6 messaging RCE API routes."""

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

    # ── iMessage ──

    def test_messaging_rce_simulate_imessage(self):
        resp = self.client.post(f"{self.base}/simulate-imessage",
                                json={"target": "iphone_user", "exploit_type": "rce"},
                                headers={"X-Auth-Token": "test-key"})
        self.assertEqual(resp.status_code, 200)
        data = resp.get_json()
        self.assertEqual(data["status"], "pending_real_execution")
        self.assertEqual(data["target"], "iphone_user")
        self.assertEqual(data["vector"], "iMessage media processing")

    # ── WhatsApp ──

    def test_messaging_rce_simulate_whatsapp(self):
        resp = self.client.post(f"{self.base}/simulate-whatsapp",
                                json={"target": "whatsapp_user", "exploit_type": "rce"},
                                headers={"X-Auth-Token": "test-key"})
        self.assertEqual(resp.status_code, 200)
        data = resp.get_json()
        self.assertEqual(data["status"], "pending_real_execution")
        self.assertEqual(data["target"], "whatsapp_user")

    # ── Signal ──

    def test_messaging_rce_simulate_signal(self):
        resp = self.client.post(f"{self.base}/simulate-signal",
                                json={"target": "signal_user", "exploit_type": "rce"},
                                headers={"X-Auth-Token": "test-key"})
        self.assertEqual(resp.status_code, 200)
        data = resp.get_json()
        self.assertEqual(data["status"], "pending_real_execution")
        self.assertEqual(data["target"], "signal_user")

    # ── Telegram ──

    def test_messaging_rce_simulate_telegram(self):
        resp = self.client.post(f"{self.base}/simulate-telegram",
                                json={"target": "telegram_user", "exploit_type": "rce"},
                                headers={"X-Auth-Token": "test-key"})
        self.assertEqual(resp.status_code, 200)
        data = resp.get_json()
        self.assertEqual(data["status"], "pending_real_execution")
        self.assertEqual(data["target"], "telegram_user")

    # ── Generate Payload ──

    def test_messaging_rce_generate_payload(self):
        resp = self.client.post(f"{self.base}/generate-payload",
                                json={"platform": "imessage", "payload_type": "rce"},
                                headers={"X-Auth-Token": "test-key"})
        self.assertEqual(resp.status_code, 200)
        data = resp.get_json()
        self.assertEqual(data["status"], "pending_real_execution")
        self.assertEqual(data["platform"], "imessage")
        self.assertEqual(data["format"], "crafted_media")

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

    # ── Map to Exploit ──

    def test_messaging_rce_map_to_exploit(self):
        from agents.specialized.messaging_rce import MessagingRCEAgent
        agent = MessagingRCEAgent()
        result = agent.map_to_exploit("media_processing")
        self.assertIsInstance(result, list)
        self.assertGreater(len(result), 0)
        result2 = agent.map_to_exploit("nonexistent")
        self.assertEqual(result2, ["generic messaging exploitation"])


if __name__ == "__main__":
    unittest.main()
