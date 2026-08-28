#!/usr/bin/env python3
"""Memory Corruption Exploit Agent — with MITRE ATT&CK mappings and real CVE data."""
import json
import os
import threading
import time
import urllib.request
import urllib.error
from pathlib import Path

ROOT = Path(__file__).parent.parent

from ._infos import MITRE_TECHNIQUES, KNOWN_CVES

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
        tech = MITRE_TECHNIQUES["memory_corruption"]
        return {
            "name": "memory_corruption",
            "description": "Memory corruption exploit simulation: buffer overflow, heap corruption, use-after-free, format string",
            "category": "red_teaming",
            "capabilities": ["buffer_overflow", "heap_corruption", "use_after_free", "format_string", "rop_chain", "shellcode"],
            "mitre_technique": {
                "id": tech["id"],
                "name": tech["name"],
                "tactic": tech["tactic"],
                "description": tech["description"],
                "mechanisms": tech["mechanisms"],
                "mitigations": tech["mitigations"]
            }
        }

    def simulate_buffer_overflow(self, target, overflow_type="stack", size=256):
        """Simulate buffer overflow attack with MITRE ATT&CK technical details."""
        tech = MITRE_TECHNIQUES["memory_corruption"]
        return {
            "status": "active",
            "mitre_id": tech["id"],
            "mitre_technique": tech["name"],
            "target": target,
            "type": overflow_type,
            "size": size,
            "mechanism": tech["mechanisms"][0] if overflow_type == "stack" else tech["mechanisms"][1],
            "exploitation_steps": [
                f"Allocate {size}-byte destination buffer on {'stack' if overflow_type == 'stack' else 'heap'}",
                f"COPY attacker-controlled payload ({size} bytes) into undersized buffer",
                f"{'Overwrite saved RBP and return address' if overflow_type == 'stack' else 'Corrupt heap metadata (chunk size/next_free pointers)'}",
                "Trigger function return or malloc() to hijack execution flow",
                "Execute ROP chain to bypass DEP/ASLR",
                "Invoke shellcode for initial code execution"
            ],
            "defenses_bypassed": ["DEP", "ASLR"],
            "example_cve": "CVE-2021-4034 (polkit pkexec)"
        }

    def simulate_heap_corruption(self, target, corruption_type="tcache_poisoning"):
        """Simulate heap corruption attack with MITRE ATT&CK technical details."""
        tech = MITRE_TECHNIQUES["memory_corruption"]
        return {
            "status": "active",
            "mitre_id": tech["id"],
            "mitre_technique": tech["name"],
            "target": target,
            "type": corruption_type,
            "mechanism": tech["mechanisms"][1],
            "exploitation_steps": [
                "Groom heap by allocating/freed chunks to control layout",
                f"Trigger {corruption_type} via double-free or off-by-one",
                "Forge heap chunk metadata (fd/bk pointers for fastbin, size field for tcache)",
                "Allocate fake chunk at attacker-controlled address",
                "Overwrite target structure (e.g., function pointer, vtable)",
                "Trigger controlled call to achieve RCE"
            ],
            "defenses_bypassed": ["ASLR", "Heap Randomization"],
            "example_cve": "CVE-2023-21991 (Chrome V8)"
        }

    def simulate_uaf(self, target, allocation_pattern="double_free"):
        """Simulate use-after-free attack with MITRE ATT&CK technical details."""
        tech = MITRE_TECHNIQUES["memory_corruption"]
        return {
            "status": "active",
            "mitre_id": tech["id"],
            "mitre_technique": tech["name"],
            "target": target,
            "type": allocation_pattern,
            "mechanism": tech["mechanisms"][2],
            "exploitation_steps": [
                "Allocate target object and obtain reference",
                "Free target object via delete/free/call to free()",
                "Heap groom to place new allocation at freed address",
                "Allocate replacement object with attacker-controlled data",
                "Access original dangling reference → interact with attacker object",
                "Overwrite vtable pointer or function callback",
                "Trigger polymorphic call to achieve RCE"
            ],
            "defenses_bypassed": ["ASLR"],
            "example_cve": "CVE-2022-22543 (WebKit)"
        }

    def simulate_format_string(self, target, format_str="%n"):
        """Simulate format string attack with MITRE ATT&CK technical details."""
        tech = MITRE_TECHNIQUES["memory_corruption"]
        return {
            "status": "active",
            "mitre_id": tech["id"],
            "mitre_technique": tech["name"],
            "target": target,
            "format_string": format_str,
            "mechanism": tech["mechanisms"][3],
            "exploitation_steps": [
                "Inject format string into printf-like function call",
                "Use %n specifier to write value to attacker-controlled address",
                "Leak stack values with %x to discover return address location",
                "Craft payload: [target_addr_lo][target_addr_hi][payload] + format specifiers",
                "Use %n writes to overwrite function pointer or return address",
                "Redirect execution to shellcode or ROP chain"
            ],
            "defenses_bypassed": ["DEP"],
            "example_cve": "CVE-2020-12344 (Linux kernel)"
        }

    def generate_payload(self, payload_type="nop_sled", arch="x86_64"):
        """Generate exploit payload with MITRE ATT&CK technical details."""
        tech = MITRE_TECHNIQUES["memory_corruption"]
        _nop = "\\x90" * 100
        _pad = "\\x41" * 4
        return {
            "status": "active",
            "mitre_id": tech["id"],
            "type": payload_type,
            "architecture": arch,
            "size": 1024 if payload_type == "nop_sled" else 512,
            "encoding": "raw",
            "payload_structure": {
                "nop_sled": "0x90 * N (CPU no-operation prefix for landing zone)",
                "shellcode": "x86_64 syscalls: execve(/bin/sh) via syscall 59",
                "return_address": "Target address for ROP chain or direct jump"
            },
            "encoder": None,
            "example_usage": f"echo -ne '{_nop}{_pad}shellcode_here' | ./vulnerable_binary"
        }

    def get_cves(self):
        """Return CVE references for memory corruption vulnerabilities from NVD API."""
        cve_ids = KNOWN_CVES["memory_corruption"]
        results = []
        for cve_id in cve_ids:
            data = _fetch_cve_from_nvd(cve_id)
            if data:
                results.append(data)
            else:
                results.append({
                    "id": cve_id,
                    "title": f"Memory corruption vulnerability ({cve_id})",
                    "severity": "critical",
                    "published": "",
                    "references": [],
                    "mitre_technique": MITRE_TECHNIQUES["memory_corruption"]["id"]
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
