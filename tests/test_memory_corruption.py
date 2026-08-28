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
    """Test all 6 memory corruption API routes return simulated responses."""

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

    # ── Buffer Overflow ──

    def test_memory_corruption_simulate_buffer_overflow(self):
        resp = self.client.post(f"{self.base}/simulate-buffer-overflow",
                                json={"target": "192.168.1.100", "overflow_type": "stack", "size": 512},
                                headers={"X-Auth-Token": "test-key"})
        self.assertEqual(resp.status_code, 200)
        data = resp.get_json()
        self.assertEqual(data["status"], "simulated")
        self.assertEqual(data["target"], "192.168.1.100")
        self.assertEqual(data["type"], "stack")

    # ── Heap Corruption ──

    def test_memory_corruption_simulate_heap_corruption(self):
        resp = self.client.post(f"{self.base}/simulate-heap-corruption",
                                json={"target": "192.168.1.100", "corruption_type": "tcache_poisoning"},
                                headers={"X-Auth-Token": "test-key"})
        self.assertEqual(resp.status_code, 200)
        data = resp.get_json()
        self.assertEqual(data["status"], "simulated")
        self.assertEqual(data["type"], "tcache_poisoning")

    # ── Use-After-Free ──

    def test_memory_corruption_simulate_uaf(self):
        resp = self.client.post(f"{self.base}/simulate-uaf",
                                json={"target": "192.168.1.100", "allocation_pattern": "double_free"},
                                headers={"X-Auth-Token": "test-key"})
        self.assertEqual(resp.status_code, 200)
        data = resp.get_json()
        self.assertEqual(data["status"], "simulated")
        self.assertEqual(data["type"], "double_free")

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
        self.assertEqual(len(data), 5)
        self.assertEqual(data[0]["id"], "CVE-2019-3568")
        self.assertEqual(data[0]["severity"], "critical")


if __name__ == "__main__":
    unittest.main()
