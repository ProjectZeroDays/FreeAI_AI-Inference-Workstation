#!/usr/bin/env python3
"""Tests for memory primitives API routes (simulation-only)."""
import json
import os
import sys
import unittest
from unittest.mock import patch

# Ensure project root is on path
PROJECT_ROOT = os.path.join(os.path.dirname(__file__), "..")
sys.path.insert(0, PROJECT_ROOT)


class TestMemoryPrimitives(unittest.TestCase):
    """Test all 7 memory primitives API routes return simulated responses."""

    def setUp(self):
        """Set up Flask test client."""
        from dashboard.backend import app
        app.config["TESTING"] = True
        self.client = app.test_client()
        self.base = "/api/exploit-cat/memory-primitives"

    # ── Describe ──

    def test_memory_primitives_describe(self):
        resp = self.client.get(f"{self.base}/describe")
        self.assertEqual(resp.status_code, 200)
        data = resp.get_json()
        self.assertEqual(data["name"], "memory_primitives")
        self.assertIn("list_primitives", data["capabilities"])
        self.assertIn("simulate_primitive", data["capabilities"])
        self.assertEqual(data["primitive_count"], 10)

    # ── List ──

    def test_memory_primitives_list(self):
        resp = self.client.get(f"{self.base}/list")
        self.assertEqual(resp.status_code, 200)
        data = resp.get_json()
        self.assertEqual(data["status"], "simulated")
        self.assertEqual(data["count"], 10)
        names = [p["name"] for p in data["primitives"]]
        for expected in [
            "buffer_overflow", "use_after_free", "double_free",
            "heap_overflow", "format_string", "integer_overflow",
            "out_of_bounds", "type_confusion", "toctou", "null_pointer",
        ]:
            self.assertIn(expected, names)

    # ── Get Primitive ──

    def test_memory_primitives_get_primitive(self):
        resp = self.client.get(f"{self.base}/buffer_overflow")
        self.assertEqual(resp.status_code, 200)
        data = resp.get_json()
        self.assertEqual(data["status"], "simulated")
        self.assertEqual(data["name"], "Buffer Overflow")
        self.assertIn("exploitation_mechanics", data)
        self.assertIn("mitigations", data)
        self.assertIn("real_world_cves", data)

    def test_memory_primitives_get_primitive_not_found(self):
        resp = self.client.get(f"{self.base}/nonexistent_primitive")
        self.assertEqual(resp.status_code, 200)
        data = resp.get_json()
        self.assertEqual(data["status"], "simulated")
        self.assertIn("error", data)
        self.assertIn("available", data)

    # ── Simulate ──

    def test_memory_primitives_simulate(self):
        resp = self.client.post(
            f"{self.base}/simulate",
            json={"primitive": "buffer_overflow", "target_info": {"target": "192.168.1.10"}},
        )
        self.assertEqual(resp.status_code, 200)
        data = resp.get_json()
        self.assertEqual(data["status"], "simulated")
        self.assertTrue(data["success"])
        self.assertEqual(data["primitive"], "buffer_overflow")

    def test_memory_primitives_simulate_default(self):
        resp = self.client.post(f"{self.base}/simulate", json={})
        self.assertEqual(resp.status_code, 200)
        data = resp.get_json()
        self.assertEqual(data["status"], "simulated")
        self.assertTrue(data["success"])

    def test_memory_primitives_simulate_not_found(self):
        resp = self.client.post(
            f"{self.base}/simulate",
            json={"primitive": "nonexistent"},
        )
        self.assertEqual(resp.status_code, 200)
        data = resp.get_json()
        self.assertEqual(data["status"], "simulated")
        self.assertIn("error", data)

    # ── Map to Exploit ──

    def test_memory_primitives_map_to_exploit(self):
        resp = self.client.post(
            f"{self.base}/map-to-exploit",
            json={"primitive": "use_after_free"},
        )
        self.assertEqual(resp.status_code, 200)
        data = resp.get_json()
        self.assertEqual(data["status"], "simulated")
        self.assertIn("techniques", data)
        self.assertIn("gadget_types", data)
        self.assertIn("reliability", data)
        self.assertGreater(len(data["techniques"]), 0)

    def test_memory_primitives_map_to_exploit_default(self):
        resp = self.client.post(f"{self.base}/map-to-exploit", json={})
        self.assertEqual(resp.status_code, 200)
        data = resp.get_json()
        self.assertEqual(data["status"], "simulated")
        self.assertEqual(data["primitive"], "buffer_overflow")

    def test_memory_primitives_map_to_exploit_not_found(self):
        resp = self.client.post(
            f"{self.base}/map-to-exploit",
            json={"primitive": "nonexistent"},
        )
        self.assertEqual(resp.status_code, 200)
        data = resp.get_json()
        self.assertEqual(data["status"], "simulated")
        self.assertIn("error", data)

    # ── Mitigations ──

    def test_memory_primitives_mitigations(self):
        resp = self.client.get(f"{self.base}/mitigations/format_string")
        self.assertEqual(resp.status_code, 200)
        data = resp.get_json()
        self.assertEqual(data["status"], "simulated")
        self.assertIn("mitigations", data)
        self.assertGreater(data["count"], 0)
        self.assertIn("defense_in_depth", data)
        # Check mitigation structure
        for mit in data["mitigations"]:
            self.assertIn("name", mit)
            self.assertIn("description", mit)

    def test_memory_primitives_mitigations_not_found(self):
        resp = self.client.get(f"{self.base}/mitigations/nonexistent")
        self.assertEqual(resp.status_code, 200)
        data = resp.get_json()
        self.assertEqual(data["status"], "simulated")
        self.assertIn("error", data)

    # ── CVEs ──

    def test_memory_primitives_cves(self):
        resp = self.client.get(f"{self.base}/cves")
        self.assertEqual(resp.status_code, 200)
        data = resp.get_json()
        self.assertEqual(data["status"], "simulated")
        self.assertIn("cves_by_primitive", data)
        self.assertGreater(data["total_cves"], 0)
        # Verify all 10 primitives have CVEs
        for primitive in [
            "buffer_overflow", "use_after_free", "double_free",
            "heap_overflow", "format_string", "integer_overflow",
            "out_of_bounds", "type_confusion", "toctou", "null_pointer",
        ]:
            self.assertIn(primitive, data["cves_by_primitive"])
            self.assertGreater(len(data["cves_by_primitive"][primitive]), 0)

    # ── Auth rejection (when AUTH_TOKEN is set) ──

    @patch("dashboard.backend.AUTH_TOKEN", "test-token-123")
    def test_memory_primitives_describe_unauthorized(self):
        resp = self.client.get(f"{self.base}/describe")
        self.assertEqual(resp.status_code, 401)

    @patch("dashboard.backend.AUTH_TOKEN", "test-token-123")
    def test_memory_primitives_list_unauthorized(self):
        resp = self.client.get(f"{self.base}/list")
        self.assertEqual(resp.status_code, 401)

    @patch("dashboard.backend.AUTH_TOKEN", "test-token-123")
    def test_memory_primitives_get_unauthorized(self):
        resp = self.client.get(f"{self.base}/buffer_overflow")
        self.assertEqual(resp.status_code, 401)

    @patch("dashboard.backend.AUTH_TOKEN", "test-token-123")
    def test_memory_primitives_simulate_unauthorized(self):
        resp = self.client.post(f"{self.base}/simulate", json={})
        self.assertEqual(resp.status_code, 401)

    @patch("dashboard.backend.AUTH_TOKEN", "test-token-123")
    def test_memory_primitives_map_unauthorized(self):
        resp = self.client.post(f"{self.base}/map-to-exploit", json={})
        self.assertEqual(resp.status_code, 401)

    @patch("dashboard.backend.AUTH_TOKEN", "test-token-123")
    def test_memory_primitives_mitigations_unauthorized(self):
        resp = self.client.get(f"{self.base}/mitigations/buffer_overflow")
        self.assertEqual(resp.status_code, 401)

    @patch("dashboard.backend.AUTH_TOKEN", "test-token-123")
    def test_memory_primitives_cves_unauthorized(self):
        resp = self.client.get(f"{self.base}/cves")
        self.assertEqual(resp.status_code, 401)


if __name__ == "__main__":
    unittest.main()
