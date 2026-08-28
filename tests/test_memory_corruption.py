#!/usr/bin/env python3
"""Tests for Memory Corruption Exploit Agent."""
import json
import os
import sys
import unittest
from unittest.mock import patch

# Ensure project root is on path
PROJECT_ROOT = os.path.join(os.path.dirname(__file__), "..")
sys.path.insert(0, PROJECT_ROOT)


class TestMemoryCorruption(unittest.TestCase):
    """Test all 6 memory corruption API routes return active responses with MITRE mappings."""

    def setUp(self):
        """Set up Flask test client."""
        from dashboard.backend import app
        app.config["TESTING"] = True
        self.client = app.test_client()
        self.base = "/api/exploit-cat/memory-corruption"

    # ── Describe ──

    def test_memory_corruption_describe(self):
        resp = self.client.get(f"{self.base}/describe")
        self.assertEqual(resp.status_code, 200)
        data = resp.get_json()
        self.assertEqual(data["name"], "memory_corruption")
        self.assertIn("buffer_overflow", data["capabilities"])
        self.assertIn("mitre_technique", data)
        self.assertEqual(data["mitre_technique"]["id"], "T1203")

    # ── Buffer Overflow ──

    def test_memory_corruption_simulate_buffer_overflow(self):
        resp = self.client.post(f"{self.base}/simulate-buffer-overflow",
                                json={"target": "192.168.1.100", "overflow_type": "stack", "size": 512},
                                headers={"X-Auth-Token": "test-key"})
        self.assertEqual(resp.status_code, 200)
        data = resp.get_json()
        self.assertEqual(data["status"], "active")
        self.assertEqual(data["target"], "192.168.1.100")
        self.assertEqual(data["type"], "stack")
        self.assertEqual(data["mitre_id"], "T1203")
        self.assertIn("exploitation_steps", data)
        self.assertEqual(len(data["exploitation_steps"]), 6)

    # ── Heap Corruption ──

    def test_memory_corruption_simulate_heap_corruption(self):
        resp = self.client.post(f"{self.base}/simulate-heap-corruption",
                                json={"target": "192.168.1.100", "corruption_type": "tcache_poisoning"},
                                headers={"X-Auth-Token": "test-key"})
        self.assertEqual(resp.status_code, 200)
        data = resp.get_json()
        self.assertEqual(data["status"], "active")
        self.assertEqual(data["type"], "tcache_poisoning")
        self.assertEqual(data["mitre_id"], "T1203")
        self.assertIn("exploitation_steps", data)

    # ── Use-After-Free ──

    def test_memory_corruption_simulate_uaf(self):
        resp = self.client.post(f"{self.base}/simulate-uaf",
                                json={"target": "192.168.1.100", "allocation_pattern": "double_free"},
                                headers={"X-Auth-Token": "test-key"})
        self.assertEqual(resp.status_code, 200)
        data = resp.get_json()
        self.assertEqual(data["status"], "active")
        self.assertEqual(data["type"], "double_free")
        self.assertEqual(data["mitre_id"], "T1203")
        self.assertIn("exploitation_steps", data)

    # ── Format String ──

    def test_memory_corruption_simulate_format_string(self):
        resp = self.client.post(f"{self.base}/simulate-format-string",
                                json={"target": "192.168.1.100", "format_str": "%n"},
                                headers={"X-Auth-Token": "test-key"})
        self.assertEqual(resp.status_code, 200)
        data = resp.get_json()
        self.assertEqual(data["status"], "active")
        self.assertEqual(data["format_string"], "%n")
        self.assertEqual(data["mitre_id"], "T1203")
        self.assertIn("exploitation_steps", data)

    # ── Primitives ──

    def test_memory_corruption_primitives(self):
        resp = self.client.get(f"{self.base}/primitives")
        self.assertEqual(resp.status_code, 200)
        data = resp.get_json()
        self.assertIsInstance(data, list)
        self.assertIn("buffer_overflow", data)
        self.assertIn("heap_corruption", data)
        self.assertIn("use_after_free", data)

    # ── CVEs ──

    def test_memory_corruption_cves(self):
        resp = self.client.get(f"{self.base}/cves")
        self.assertEqual(resp.status_code, 200)
        data = resp.get_json()
        self.assertIsInstance(data, list)
        self.assertEqual(len(data), 6)
        self.assertEqual(data[0]["id"], "CVE-2023-21991")

    # ── Generate Payload ──

    def test_memory_corruption_generate_payload(self):
        resp = self.client.post(f"{self.base}/generate-payload",
                                json={"payload_type": "nop_sled", "arch": "x86_64"},
                                headers={"X-Auth-Token": "test-key"})
        self.assertEqual(resp.status_code, 200)
        data = resp.get_json()
        self.assertEqual(data["status"], "active")
        self.assertEqual(data["type"], "nop_sled")
        self.assertEqual(data["architecture"], "x86_64")
        self.assertEqual(data["mitre_id"], "T1203")


if __name__ == "__main__":
    unittest.main()
