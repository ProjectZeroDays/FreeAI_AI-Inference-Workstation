#!/usr/bin/env python3
"""Memory Corruption Exploit Agent — with real CVE data from NVD API."""
import json
import os
import threading
import time
import urllib.request
import urllib.error
from pathlib import Path

ROOT = Path(__file__).parent.parent

# Cache for NVD API results
_cve_cache = {}
_cache_lock = threading.Lock()
_CACHE_TTL = 3600  # 1 hour


def _fetch_cve_from_nvd(cve_id):
    """Fetch CVE details from NVD API."""
    cache_key = f"nvd:{cve_id}"
    with _cache_lock:
        if cache_key in _cve_cache:
            entry = _cve_cache[cache_key]
            if time.time() - entry["timestamp"] < _CACHE_TTL:
                return entry["data"]
    
    url = f"https://services.nvd.nist.gov/rest/json/cves/2.0?cveId={cve_id}&resultsPerPage=1"
    headers = {"Accept": "application/json"}
    
    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read())
            vulns = data.get("vulnerabilities", [])
            if vulns:
                cve_data = vulns[0].get("cve", {})
                result = {
                    "id": cve_data.get("id", cve_id),
                    "title": cve_data.get("descriptions", [{}])[0].get("value", "")[:100],
                    "severity": _get_severity(cve_data),
                    "published": cve_data.get("publishedDate", ""),
                    "references": [r.get("url", "") for r in cve_data.get("references", [])],
                }
                with _cache_lock:
                    _cve_cache[cache_key] = {"timestamp": time.time(), "data": result}
                return result
    except Exception:
        pass
    return None


def _get_severity(cve_data):
    """Extract severity from CVE data."""
    for metric in cve_data.get("metrics", {}).values():
        for key, val in metric.items():
            if key in ("cvssMetricV31", "cvssMetricV30", "cvssMetricV2"):
                if isinstance(val, list):
                    for v in val:
                        sev = v.get("cvssData", {}).get("baseMetricV3", {}).get("severity", "")
                        if sev:
                            return sev.lower()
                        sev = v.get("cvssData", {}).get("baseMetricV2", {}).get("severity", "")
                        if sev:
                            return sev.lower()
    return "unknown"


class MemoryCorruptionAgent:
    """Memory corruption exploit simulation for defensive research."""

    def __init__(self):
        self.sessions = []
        self.primitives = {}
        self._lock = threading.Lock()

    def describe(self):
        return {
            "name": "memory_corruption",
            "description": "Memory corruption exploit simulation: buffer overflow, heap corruption, use-after-free, format string",
            "category": "red_teaming",
            "capabilities": ["buffer_overflow", "heap_corruption", "use_after_free", "format_string", "rop_chain", "shellcode"],
        }

    def simulate_buffer_overflow(self, target, overflow_type="stack", size=256):
        """Simulate buffer overflow attack."""
        return {
            "status": "simulated",
            "target": target,
            "type": overflow_type,
            "size": size,
            "payload": f"\\x41 * {size} (simulated NOP sled + shellcode placeholder)",
            "overflow_location": f"0x{target}:0x{size:08x}",
        }

    def simulate_heap_corruption(self, target, corruption_type="tcache_poisoning"):
        """Simulate heap corruption attack."""
        return {
            "status": "simulated",
            "target": target,
            "type": corruption_type,
            "chunk_address": f"0x{hash(target) & 0xFFFFFFFF:08x}",
            "victim_chunk": f"0x{hash(target + '_victim') & 0xFFFFFFFF:08x}",
            "corruption_method": f"{corruption_type} (simulated)",
        }

    def simulate_uaf(self, target, allocation_pattern="double_free"):
        """Simulate use-after-free attack."""
        return {
            "status": "simulated",
            "target": target,
            "type": allocation_pattern,
            "freed_pointer": f"0x{hash(target) & 0xFFFFFFFF:08x}",
            "reuse_offset": 0x10,
            "control_gained": True,
        }

    def simulate_format_string(self, target, format_str="%n"):
        """Simulate format string attack."""
        return {
            "status": "simulated",
            "target": target,
            "format_string": format_str,
            "write_address": f"0x{hash(target + '_addr') & 0xFFFFFFFF:08x}",
            "write_value": 0x41414141,
            "overflow_sequence": [
                f"{format_str} * 100",
                "target_address_lsb",
                "target_address_msb",
                "final_write"
            ],
        }

    def generate_payload(self, payload_type="nop_sled", arch="x86_64"):
        """Generate simulated exploit payload."""
        return {
            "status": "simulated",
            "type": payload_type,
            "architecture": arch,
            "size": 1024 if payload_type == "nop_sled" else 512,
            "content": f"{'\\x90' * 100} <shellcode_placeholder> {'\\x41' * (1024 - 100)}",
            "encoding": "raw",
            "encoder": None,
        }

    def get_cves(self):
        """Return CVE references for memory corruption vulnerabilities from NVD API."""
        cve_ids = ["CVE-2019-3568", "CVE-2019-8641", "CVE-2018-4990", "CVE-2017-0144", "CVE-2022-0847"]
        results = []
        for cve_id in cve_ids:
            data = _fetch_cve_from_nvd(cve_id)
            if data:
                results.append(data)
            else:
                # Fallback to simulated data
                results.append({
                    "id": cve_id,
                    "title": f"Simulated memory corruption CVE ({cve_id})",
                    "severity": "critical",
                    "published": "",
                    "references": []
                })
        return results

    def list_primitives(self):
        """Return list of memory corruption primitives."""
        return [
            "buffer_overflow",
            "heap_corruption",
            "use_after_free",
            "format_string",
            "integer_overflow",
            "type_confusion",
            "double_free",
            "heap_overflow",
        ]

    def map_to_exploit(self, primitive):
        """Map primitive to real-world exploit techniques."""
        mappings = {
            "buffer_overflow": ["ROP chain", "JOP chain", "COP chain", "shellcode injection"],
            "heap_corruption": ["tcache poisoning", "house of spirit", "house of orange", "heap feng shui"],
            "use_after_free": ["double free", "fastbin attack", "tcache dup", "overlap attack"],
            "format_string": ["arbitrary write", "info leak", "stack pivot", "return-to-libc"],
        }
        return mappings.get(primitive, ["generic exploitation"])


# Module-level state for Flask
_exploit_lock = threading.Lock()
_exploit_data = {}
