#!/usr/bin/env python3
"""Tests for chained zero-day API routes (simulation-only)."""
import json
import os
import sys
import threading
import unittest
from unittest.mock import patch

# Ensure project root is on path
PROJECT_ROOT = os.path.join(os.path.dirname(__file__), "..")
sys.path.insert(0, PROJECT_ROOT)


class TestChainedZeroDay(unittest.TestCase):
    """Test all 7 chained zero-day API routes return simulated responses."""

    def setUp(self):
        """Set up Flask test client."""
        from dashboard.backend import app
        app.config["TESTING"] = True
        self.client = app.test_client()
        self.base = "/api/exploit-cat/chained-zero-day"

    # ── Describe ──

    def test_chained_zero_day_describe(self):
        resp = self.client.get(f"{self.base}/describe")
        self.assertEqual(resp.status_code, 200)
        data = resp.get_json()
        self.assertEqual(data["name"], "chained_zero_day")
        self.assertIn("build_chain", data["capabilities"])
        self.assertIn("analyze_chain", data["capabilities"])
        self.assertIn("simulate_chain", data["capabilities"])

    # ── Build Chain ──

    def test_chained_zero_day_build_chain(self):
        stages = [
            {"stage": 1, "type": "messaging_rce", "cve": "CVE-2019-8641"},
            {"stage": 2, "type": "kernel_lpe", "cve": "CVE-2019-8646"},
            {"stage": 3, "type": "sandbox_escape", "cve": "CVE-2019-8647"},
            {"stage": 4, "type": "covert_channel", "method": "dns_tunnel"}
        ]
        resp = self.client.post(
            f"{self.base}/build-chain",
            json={"stages": stages},
        )
        self.assertEqual(resp.status_code, 200)
        data = resp.get_json()
        self.assertEqual(data["status"], "simulated")
        self.assertIn("chain_id", data)
        self.assertEqual(data["chain"]["num_stages"], 4)

    # ── Analyze Chain ──

    def test_chained_zero_day_analyze_chain(self):
        # First build a chain
        stages = [
            {"stage": 1, "type": "messaging_rce", "cve": "CVE-2019-8641"},
            {"stage": 2, "type": "kernel_lpe", "cve": "CVE-2019-8646"},
            {"stage": 3, "type": "sandbox_escape", "cve": "CVE-2019-8647"}
        ]
        build_resp = self.client.post(
            f"{self.base}/build-chain",
            json={"stages": stages},
        )
        chain_id = build_resp.get_json()["chain_id"]

        # Then analyze it
        resp = self.client.post(
            f"{self.base}/analyze-chain",
            json={"chain_id": chain_id},
        )
        self.assertEqual(resp.status_code, 200)
        data = resp.get_json()
        self.assertEqual(data["status"], "simulated")
        self.assertIn("viability_score", data)
        self.assertIn("success_probability", data)
        self.assertIsInstance(data["viability_score"], (int, float))
        self.assertGreater(data["viability_score"], 0)

    # ── Simulate Chain ──

    def test_chained_zero_day_simulate_chain(self):
        # First build a chain
        stages = [
            {"stage": 1, "type": "messaging_rce", "cve": "CVE-2019-8641"},
            {"stage": 2, "type": "kernel_lpe", "cve": "CVE-2019-8646"},
            {"stage": 3, "type": "sandbox_escape", "cve": "CVE-2019-8647"},
            {"stage": 4, "type": "covert_channel", "method": "dns_tunnel"}
        ]
        build_resp = self.client.post(
            f"{self.base}/build-chain",
            json={"stages": stages},
        )
        chain_id = build_resp.get_json()["chain_id"]

        # Then simulate it
        resp = self.client.post(
            f"{self.base}/simulate-chain",
            json={"chain_id": chain_id, "target": "192.168.1.100"},
        )
        self.assertEqual(resp.status_code, 200)
        data = resp.get_json()
        self.assertEqual(data["status"], "simulated")
        self.assertEqual(data["stages_executed"], 4)
        self.assertEqual(data["overall_status"], "simulated_success")

    # ── List Chains ──

    def test_chained_zero_day_list_chains(self):
        resp = self.client.get(f"{self.base}/list-chains")
        self.assertEqual(resp.status_code, 200)
        data = resp.get_json()
        self.assertEqual(data["status"], "simulated")
        self.assertIn("chains", data)
        # Should include known real-world chains
        self.assertIn("pegasus", data["chains"])
        self.assertIn("forcedentry", data["chains"])
        self.assertIn("blastpass", data["chains"])

    # ── Optimize Chain ──

    def test_chained_zero_day_optimize_chain(self):
        # First build a chain
        stages = [
            {"stage": 1, "type": "messaging_rce", "cve": "CVE-2019-8641"},
            {"stage": 2, "type": "kernel_lpe", "cve": "CVE-2019-8646"}
        ]
        build_resp = self.client.post(
            f"{self.base}/build-chain",
            json={"stages": stages},
        )
        chain_id = build_resp.get_json()["chain_id"]

        # Then optimize it
        resp = self.client.post(
            f"{self.base}/optimize-chain",
            json={"chain_id": chain_id},
        )
        self.assertEqual(resp.status_code, 200)
        data = resp.get_json()
        self.assertEqual(data["status"], "simulated")
        self.assertIn("suggestions", data)
        self.assertGreater(data["num_suggestions"], 0)

    # ── CVEs ──

    def test_chained_zero_day_cves(self):
        resp = self.client.get(f"{self.base}/cves")
        self.assertEqual(resp.status_code, 200)
        data = resp.get_json()
        self.assertEqual(data["status"], "simulated")
        self.assertIn("cves", data)
        self.assertGreater(len(data["cves"]), 0)
        # Should include known CVEs
        self.assertIn("CVE-2019-8641", data["cves"])
        self.assertIn("CVE-2023-41064", data["cves"])

    # ── Auth rejection (when AUTH_TOKEN is set) ──

    @patch("dashboard.backend.AUTH_TOKEN", "test-token-123")
    def test_chained_zero_day_describe_unauthorized(self):
        resp = self.client.get(f"{self.base}/describe")
        self.assertEqual(resp.status_code, 401)

    @patch("dashboard.backend.AUTH_TOKEN", "test-token-123")
    def test_chained_zero_day_build_chain_unauthorized(self):
        resp = self.client.post(f"{self.base}/build-chain", json={})
        self.assertEqual(resp.status_code, 401)

    @patch("dashboard.backend.AUTH_TOKEN", "test-token-123")
    def test_chained_zero_day_analyze_chain_unauthorized(self):
        resp = self.client.post(f"{self.base}/analyze-chain", json={})
        self.assertEqual(resp.status_code, 401)

    @patch("dashboard.backend.AUTH_TOKEN", "test-token-123")
    def test_chained_zero_day_simulate_chain_unauthorized(self):
        resp = self.client.post(f"{self.base}/simulate-chain", json={})
        self.assertEqual(resp.status_code, 401)

    @patch("dashboard.backend.AUTH_TOKEN", "test-token-123")
    def test_chained_zero_day_list_chains_unauthorized(self):
        resp = self.client.get(f"{self.base}/list-chains")
        self.assertEqual(resp.status_code, 401)

    @patch("dashboard.backend.AUTH_TOKEN", "test-token-123")
    def test_chained_zero_day_optimize_chain_unauthorized(self):
        resp = self.client.post(f"{self.base}/optimize-chain", json={})
        self.assertEqual(resp.status_code, 401)

    @patch("dashboard.backend.AUTH_TOKEN", "test-token-123")
    def test_chained_zero_day_cves_unauthorized(self):
        resp = self.client.get(f"{self.base}/cves")
        self.assertEqual(resp.status_code, 401)


if __name__ == "__main__":
    unittest.main()
