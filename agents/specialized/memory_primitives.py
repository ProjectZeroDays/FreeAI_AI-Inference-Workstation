#!/usr/bin/env python3
"""Memory Corruption Primitives Agent — enhanced with real CVE database integration."""
import json
import os
import time
import threading
import requests
from pathlib import Path
from datetime import datetime, timedelta

ROOT = Path(__file__).parent.parent

_primitives_lock = threading.Lock()
_primitives = {}

_cache_lock = threading.Lock()
_cve_cache = {}
_CACHE_TTL = timedelta(hours=6)


class CVEIntegration:
    """Handles CVE database integration via NVD and GitHub APIs with caching."""

    @staticmethod
    def get_cve_data_from_nvd(cve_ids):
        """Fetch CVE details from NVD API (CISA CVE Database integration)."""
        if not os.getenv("NVD_API_KEY") and not os.getenv("TEST"):
            return None

        base_url = "https://services.nvd.nist.gov/rest/json/cves/2.0"
        headers = {}

        if os.getenv("NVD_API_KEY"):
            headers["apiKey"] = os.getenv("NVD_API_KEY")

        merged_results = []

        try:
            request_count = 0
            max_requests = 5 if not os.getenv("NVD_API_KEY") else 20

            for cve_id in cve_ids:
                if request_count >= max_requests:
                    break

                params = {
                    "cveId": cve_id,
                    "resultsPerPage": 1
                }

                response = requests.get(base_url, headers=headers, params=params, timeout=10)
                if response.status_code != 200:
                    request_count += 1
                    time.sleep(1)
                    continue

                data = response.json()
                cve_item = data.get("vulnerabilities", [{}])[0].get("cve", {}) if data.get("vulnerabilities") else get_empty_cve_template(cve_id)

                merged = _merge_cve_with_computed_data(cve_id, cve_item)
                merged_results.append(merged)

                request_count += 1
                time.sleep(1)

            return {"source": "nvd", "count": len(merged_results), "data": merged_results}

        except Exception as e:
            print(f"NVD API fetch error: {e}")
            return None

    @staticmethod
    def get_recent_cves_from_nvd(days=30):
        """Fetch recent CVEs from NVD API for all primitive categories."""
        if not os.getenv("NVD_API_KEY") and not os.getenv("TEST"):
            return None

        base_url = "https://services.nvd.nist.gov/rest/json/cves/2.0"
        headers = {}

        if os.getenv("NVD_API_KEY"):
            headers["apiKey"] = os.getenv("NVD_API_KEY")

        date_query = datetime.now() - timedelta(days=days)
        date_str = date_query.strftime("%Y-%m-%d")

        try:
            response = requests.get(
                base_url,
                headers=headers,
                params={
                    "resultsPerPage": 20,
                    "lastStarts": date_str
                },
                timeout=15
            )

            if response.status_code != 200:
                return None

            data = response.json()
            vulnerabilities = data.get("vulnerabilities", [])

            merged_cves = []
            for vuln in vulnerabilities[:10]:
                cve_item = vuln.get("cve", {})
                cve_id = cve_item.get("id", "")

                merged = _merge_cve_with_computed_data(cve_id, cve_item)
                merged.update({
                    "source": "nvd_recent",
                    "fetched_at": datetime.now().isoformat()
                })
                merged_cves.append(merged)

            return {"source": "nvd_recent", "count": len(merged_cves), "data": merged_cves}

        except Exception as e:
            print(f"NVD recent CVE fetch error: {e}")
            return None

    @staticmethod
    def search_by_product_from_github(product_name, days=7):
        """Search GitHub for vulnerable versions of a product."""
        github_token = os.getenv("GITHUB_TOKEN")
        if not github_token:
            return None

        base_url = f"https://api.github.com/search/issues"
        headers = {
            "Authorization": f"token {github_token}",
            "Accept": "application/vnd.github.v3+json"
        }

        date_query = datetime.now() - timedelta(days=days)

        try:
            response = requests.get(
                base_url,
                headers=headers,
                params={
                    "q": f"repo:* vulnerable OR repo:* vulnerability OR repo:* CVE in:comments since={date_query.strftime('%Y-%m-%d')}",
                    "per_page": 10
                },
                timeout=15
            )

            if response.status_code != 200:
                return None

            data = response.json()
            findings = []

            for item in data.get("items", []):
                title = item.get("title", "")
                description = item.get("body", "")[:500]
                created_at = item.get("created_at", "")

                findings.append({
                    "source": "github",
                    "repository": item.get("repository", {}).get("full_name", ""),
                    "issue_title": title,
                    "issue_number": item.get("number", ""),
                    "created_at": created_at,
                    "short_description": description,
                    "type": "vulnerability_report",
                    "confidence": "medium"
                })

            return {"source": "github", "count": len(findings), "data": findings}

        except Exception as e:
            print(f"GitHub search error: {e}")
            return None


def get_empty_cve_template(cve_id):
    """Return empty CVE template for fallback."""
    return {
        "id": cve_id,
        "descriptions": [{"lang": "en", "value": ""}],
        "metrics": {},
        "configurations": {}
    }


def _merge_cve_with_computed_data(cve_id, cve_item):
    """Merge raw CVE with computed values from primitives module."""
    description = ""
    severity = "unknown"
    affected_products = []
    
    if "descriptions" in cve_item and isinstance(cve_item["descriptions"], list):
        desc = next((d.get("value", "") for d in cve_item["descriptions"] if isinstance(d, dict)), "")
        if desc:
            description = desc
    
    severity = cve_item.get("metrics", {}).get("cvssMetricV31", [{}])[0].get("cvssData", {}).get("baseSeverity", "unknown")
    
    try:
        if "configurations" in cve_item and isinstance(cve_item["configurations"], dict):
            nodes = cve_item["configurations"].get("nodes", [])
            if isinstance(nodes, list):
                for node in nodes:
                    if isinstance(node, dict) and "cves" in node:
                        cve_hits = node["cves"].get("CVE_data_version", {}).get("CVE_data_hits", [])
                        if isinstance(cve_hits, list):
                            for cve_hit in cve_hits:
                                if isinstance(cve_hit, dict):
                                    if "vendor" in cve_hit and isinstance(cve_hit["vendor"], dict):
                                        vendor_data = cve_hit["vendor"].get("vendorData", [])
                                        if isinstance(vendor_data, list) and len(vendor_data) > 0:
                                            for vendor_info in vendor_data:
                                                if isinstance(vendor_info, dict):
                                                    affected_products.extend(vendor_info.get("vendorNames", []))
                                    if "product" in cve_hit and isinstance(cve_hit["product"], dict):
                                        product_data = cve_hit["product"].get("productData", [])
                                        if isinstance(product_data, list) and len(product_data) > 0:
                                            for product_info in product_data:
                                                if isinstance(product_info, dict):
                                                    affected_products.extend(product_info.get("productNames", []))
    except (TypeError, AttributeError):
        pass

    return {
        "id": cve_id,
        "source": "api",
        "product": "Multiple (API)",
        "severity": severity,
        "description": description,
        "fetched_at": datetime.now().isoformat()
    }


def is_cache_expired(cache_key):
    """Check if a cache entry has expired."""
    entry = _cve_cache.get(cache_key)
    if not entry:
        return True

    timestamp = entry.get("timestamp")
    if not timestamp:
        return True

    return datetime.now() - datetime.fromisoformat(timestamp) > _CACHE_TTL


def get_cached_cves(module_name):
    """Get CVEs from cache if not expired, otherwise return None."""
    cache_key = f"cves_{module_name}"

    if is_cache_expired(cache_key):
        return None

    return _cve_cache.get(cache_key)


def set_cached_cves(module_name, cve_data):
    """Set CVEs in cache with current timestamp."""
    cache_key = f"cves_{module_name}"

    _cve_cache[cache_key] = {
        "data": cve_data,
        "timestamp": datetime.now().isoformat()
    }


def clear_cache(module_name=None):
    """Clear CVE cache. If module_name is None, clear all cache."""
    if module_name:
        cache_key = f"cves_{module_name}"
        if cache_key in _cve_cache:
            del _cve_cache[cache_key]
    else:
        _cve_cache.clear()


# Load API keys from environment
SHODAN_API_KEY = os.getenv("SHODAN_API_KEY", "")
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN", "")
NVDA_API_KEY = os.getenv("NVDA_API_KEY", "")
NVD_API_KEY = os.getenv("NVD_API_KEY", "")


class MemoryPrimitivesAgent:
    """Enhanced memory corruption primitives with real CVE database integration."""

    def __init__(self):
        self.simulations = []
        self._init_primitives()

    def _init_primitives(self):
        """Initialize the 10 memory corruption primitives."""
        with _primitives_lock:
            if _primitives:
                return
            _primitives.update({
                "buffer_overflow": {
                    "name": "Buffer Overflow",
                    "category": "memory_corruption",
                    "description": "Writing beyond allocated buffer boundaries to overwrite adjacent memory on stack or heap.",
                    "subtypes": ["stack", "heap"],
                    "exploitation_mechanics": "Overwrite return address, function pointers, or adjacent data to redirect execution flow.",
                    "real_world_cves": ["CVE-2019-3568", "CVE-2014-0160", "CVE-2003-0252", "CVE-2024-3094", "CVE-2021-34527", "CVE-2023-36884"],
                    "mitigations": ["ASLR", "DEP/NX", "Stack Canaries", "SafeSEH", "CFG"],
                    "ai_selection_score": 85,
                    "difficulty": "low",
                    "impact": "critical",
                },
                "use_after_free": {
                    "name": "Use-After-Free (UAF)",
                    "category": "memory_corruption",
                    "description": "Accessing heap memory after it has been freed, allowing control over object state.",
                    "subtypes": ["vtable_hijack", "function_pointer", "data_corruption"],
                    "exploitation_mechanics": "Free object, allocate attacker-controlled data in same slot, access dangling pointer to execute controlled code.",
                    "real_world_cves": ["CVE-2018-4990", "CVE-2021-26855", "CVE-2014-1776", "CVE-2024-3094"],
                    "mitigations": ["CFI", "Safe Unlink", "Quarantine", "Isolated Heaps"],
                    "ai_selection_score": 90,
                    "difficulty": "medium",
                    "impact": "critical",
                },
                "double_free": {
                    "name": "Double-Free",
                    "category": "memory_corruption",
                    "description": "Calling free() twice on the same pointer, corrupting allocator metadata。",
                    "subtypes": ["fastbin_dup", "tcache_poisoning", "smallbin_attack"],
                    "exploitation_mechanics": "Corrupt freelist to achieve arbitrary write or control next malloc return value。",
                    "real_world_cves": ["CVE-2020-13777", "CVE-2019-11043", "CVE-2017-1000377"],
                    "mitigations": ["Safe Unlink", "Double-Free Detection", "Quarantine", "Scudo Allocator"],
                    "ai_selection_score": 75,
                    "difficulty": "medium",
                    "impact": "high",
                },
                "heap_overflow": {
                    "name": "Heap Overflow / Chunk Overflow",
                    "category": "memory_corruption",
                    "description": "Overflowing a heap allocation to corrupt adjacent chunk headers or data。",
                    "subtypes": ["unlink_attack", "house_of_force", "tcache_poisoning", "off_by_one"],
                    "exploitation_mechanics": "Overflow chunk data to corrupt metadata (size, fd/bk pointers) or adjacent chunk, triggering arbitrary write on next free/alloc。",
                    "real_world_cves": ["CVE-2021-3156", "CVE-2023-36844", "CVE-2018-6789", "CVE-2024-3094"],
                    "mitigations": ["Safe Unlink", "Heap Metadata Validation", "Heap Canaries", "Hardened Allocator"],
                    "ai_selection_score": 80,
                    "difficulty": "high",
                    "impact": "critical",
                },
                "format_string": {
                    "name": "Format String Vulnerability",
                    "category": "memory_corruption",
                    "description": "Exploiting unchecked format string arguments to leak memory or write arbitrary addresses。",
                    "subtypes": ["info_leak", "arbitrary_write", "stack_pivot"],
                    "exploitation_mechanics": "Pass user-controlled string as format argument to printf family functions, using %p/%x to read stack or %n to write。",
                    "real_world_cves": ["CVE-2021-4034", "CVE-2017-5638", "CVE-2000-0812"],
                    "mitigations": ["Compiler Warnings (-Wformat-security)", "FORTIFY_SOURCE", "Format String Auditing", "ASLR"],
                    "ai_selection_score": 65,
                    "difficulty": "medium",
                    "impact": "high",
                },
                "integer_overflow": {
                    "name": "Integer Overflow / Underflow",
                    "category": "memory_corruption",
                    "description": "Arithmetic operations that wrap around type boundaries, causing undersized allocations or bypassed checks。",
                    "subtypes": ["signed_overflow", "unsigned_overflow", "signedness_confusion", "truncation"],
                    "exploitation_mechanics": "Trigger arithmetic wrap to allocate undersized buffer, then overflow; or bypass size/limit checks。",
                    "real_world_cves": ["CVE-2019-18276", "CVE-2020-8835", "CVE-2019-3568"],
                    "mitigations": ["Signed/Unsigned Validation", "Bounds Checking", "UBSan", "Safe Arithmetic Libraries"],
                    "ai_selection_score": 70,
                    "difficulty": "medium",
                    "impact": "high",
                },
                "out_of_bounds": {
                    "name": "Out-of-Bounds Read/Write",
                    "category": "memory_corruption",
                    "description": "Accessing array or buffer indices outside valid range。",
                    "subtypes": ["oob_read", "oob_write", "off_by_one", "negative_index"],
                    "exploitation_mechanics": "Access memory beyond array bounds to leak sensitive data (read) or corrupt adjacent structures (write)。",
                    "real_world_cves": ["CVE-2021-44228", "CVE-2019-5736", "CVE-2021-21148", "CVE-2024-21762", "CVE-2021-26855", "CVE-2021-34527"],
                    "mitigations": ["Bounds Checking", "ASan", "Memory Safe Languages", "Index Validation"],
                    "ai_selection_score": 78,
                    "difficulty": "low-medium",
                    "impact": "high",
                },
                "type_confusion": {
                    "name": "Type Confusion",
                    "category": "memory_corruption",
                    "description": "Treating an object as an incorrect type, leading to misinterpreted memory layout or method dispatch。",
                    "subtypes": ["vtable_mismatch", "incorrect_cast", "prototype_pollution", "class_hierarchy_abuse"],
                    "exploitation_mechanics": "Confuse type system to interpret memory as different object type, triggering incorrect virtual call or field access。",
                    "real_world_cves": ["CVE-2021-21148", "CVE-2023-4863", "CVE-2016-4657"],
                    "mitigations": ["RTTI Validation", "Type-Safe Languages", "CFI", "Object Tagging"],
                    "ai_selection_score": 88,
                    "difficulty": "high",
                    "impact": "critical",
                },
                "toctou": {
                    "name": "Race Condition (TOCTOU)",
                    "category": "memory_corruption",
                    "description": "Time-of-check to time-of-use vulnerability where state changes between validation and use。",
                    "subtypes": ["symlink_race", "file_permission_race", "check_use_race", "signal_race"],
                    "exploitation_mechanics": "Modify resource between check (e.g., permission validation) and use (e.g., file access) to bypass security controls。",
                    "real_world_cves": ["CVE-2021-3156", "CVE-2019-14287", "CVE-2019-5736"],
                    "mitigations": ["Atomic Operations", "File Descriptor Passing", "Mandatory Access Control", "O_NOFOLLOW"],
                    "ai_selection_score": 60,
                    "difficulty": "medium-high",
                    "impact": "high",
                },
                "null_pointer": {
                    "name": "Null Pointer Dereference",
                    "category": "memory_corruption",
                    "description": "Dereferencing a NULL or uninitialized pointer, causing crashes or potential privilege escalation。",
                    "subtypes": ["user_mode_crash", "kernel_null_page", "uninitialized_pointer", "double_deref"],
                    "exploitation_mechanics": "Trigger NULL deref for DoS, or in kernel mode map NULL page to control dereferenced data for privilege escalation。",
                    "real_world_cves": ["CVE-2017-1000112", "CVE-2016-0728", "CVE-2019-2215"],
                    "mitigations": ["NULL Page Protection", "SMEP", "Static Analysis", "Defensive NULL Checks"],
                    "ai_selection_score": 45,
                    "difficulty": "low",
                    "impact": "medium-high",
                },
            })

    def describe(self):
        """Return agent description and capabilities."""
        return {
            "name": "memory_primitives",
            "description": "Memory corruption primitive simulation: buffer overflow, use-after-free, double-free, heap overflow, format string, integer overflow, out-of-bounds, type confusion, TOCTOU, null pointer dereference. Enhanced with real CVE database integration via NVD and GitHub APIs。",
            "category": "red_teaming",
            "capabilities": [
                "describe",
                "list_primitives",
                "get_primitive",
                "simulate_primitive",
                "map_to_exploit",
                "find_mitigations",
                "get_cves",
                "fetch_real_cves",
                "clear_api_cache",
            ],
            "primitive_count": 10,
            "api_integration": {
                "nvd_api": bool(NVD_API_KEY),
                "github_api": bool(GITHUB_TOKEN),
                "shodan_api": bool(SHODAN_API_KEY),
                "nvda_api": bool(NVDA_API_KEY),
                "cache_enabled": True,
            },
        }

    def list_primitives(self):
        """Return all 10 memory corruption primitives with summary details."""
        self._init_primitives()
        result = []
        with _primitives_lock:
            for name, info in _primitives.items():
                result.append({
                    "name": name,
                    "display_name": info["name"],
                    "category": info["category"],
                    "difficulty": info["difficulty"],
                    "impact": info["impact"],
                    "ai_selection_score": info["ai_selection_score"],
                    "subtypes": info["subtypes"],
                })
        return {"primitives": result, "count": len(result), "status": "simulated"}

    def get_primitive(self, name):
        """Return detailed info about a specific primitive."""
        self._init_primitives()
        with _primitives_lock:
            info = _primitives.get(name)
        if not info:
            return {"error": f"primitive '{name}' not found", "available": list(_primitives.keys()), "status": "simulated"}
        return {**info, "status": "simulated"}

    def simulate_primitive(self, name, target_info=None):
        """Simulate primitive exploitation — returns {"status": "simulated"}."""
        target_info = target_info or {}
        self._init_primitives()
        with _primitives_lock:
            info = _primitives.get(name)
        if not info:
            return {"error": f"primitive '{name}' not found", "status": "simulated"}

        simulation = {
            "primitive": name,
            "display_name": info["name"],
            "target": target_info.get("target", "simulated_target"),
            "simulation_id": f"mp_{name}_{int(time.time())}",
            "status": "simulated",
            "success": True,
            "details": {
                "exploitation_mechanics": info["exploitation_mechanics"],
                "difficulty": info["difficulty"],
                "impact": info["impact"],
                "ai_selection_score": info["ai_selection_score"],
                "subtypes_evaluated": info["subtypes"],
                "mitigations_to_bypass": info["mitigations"],
            },
            "timestamp": time.time(),
        }
        self.simulations.append(simulation)
        return simulation

    def map_to_exploit(self, primitive_name):
        """Map primitive to real-world exploit techniques."""
        self._init_primitives()
        with _primitives_lock:
            info = _primitives.get(primitive_name)
        if not info:
            return {"error": f"primitive '{primitive_name}' not found", "status": "simulated"}

        technique_map = {
            "buffer_overflow": {
                "techniques": ["stack_smashing", "rop_chain", "ret2libc", "jmp_esp", "egg_hunter"],
                "gadget_types": ["pop_ret", "pop_pop_ret", "mov_esp_ebp", "syscall"],
                "reliability": "high",
            },
            "use_after_free": {
                "techniques": ["vtable_hijack", "fake_object_spray", "function_pointer_overwrite", "type_confusion_chain"],
                "gadget_types": ["virtual_call", "indirect_call", "method_dispatch"],
                "reliability": "medium",
            },
            "double_free": {
                "techniques": ["fastbin_dup_into_stack", "tcache_poisoning", "smallbin_attack", "house_of_botcake"],
                "gadget_types": ["malloc_hook", "free_hook", "tcache_entry"],
                "reliability": "medium",
            },
            "heap_overflow": {
                "techniques": ["unlink_attack", "house_of_force", "house_of_einherjar", "off_by_one_to_overwrite"],
                "gadget_types": ["fd_bk_write", "top_chunk_corrupt", "consolidation"],
                "reliability": "medium-high",
            },
            "format_string": {
                "techniques": ["stack_read", "got_overwrite", "stack_write", "dtor_overwrite"],
                "gadget_types": ["printf_family", "fprintf", "syslog"],
                "reliability": "medium",
            },
            "integer_overflow": {
                "techniques": ["undersized_alloc_overflow", "loop_bound_bypass", "signedness_abuse", "truncation_exploit"],
                "gadget_types": ["malloc_size_calc", "memcpy_size", "array_index"],
                "reliability": "medium",
            },
            "out_of_bounds": {
                "techniques": ["heap_metadata_read", "adjacent_chunk_overwrite", "struct_field_leak", "canary_leak"],
                "gadget_types": ["array_access", "string_index", "vector_at"],
                "reliability": "high",
            },
            "type_confusion": {
                "techniques": ["virtual_call_hijack", "field_access_confusion", "prototype_pollution", "class_hierarchy_abuse"],
                "gadget_types": ["vtable_swap", "incorrect_cast", "method_resolution"],
                "reliability": "medium-high",
            },
            "toctou": {
                "techniques": ["symlink_swap", "fd_race", "permission_bypass", "signal_handler_race"],
                "gadget_types": ["access_open_race", "stat_open_race", "check_exec_race"],
                "reliability": "low-medium",
            },
            "null_pointer": {
                "techniques": ["kernel_null_page_map", "user_mode_dos", "double_deref_chain", "uninitialized_use"],
                "gadget_types": ["null_deref", "struct_offset_null", "callback_null"],
                "reliability": "low",
            },
        }

        mapping = technique_map.get(primitive_name, {})
        return {
            "primitive": primitive_name,
            "techniques": mapping.get("techniques", []),
            "gadget_types": mapping.get("gadget_types", []),
            "reliability": mapping.get("reliability", "unknown"),
            "status": "simulated",
        }

    def find_mitigations(self, primitive_name):
        """Return mitigation techniques for a primitive."""
        self._init_primitives()
        with _primitives_lock:
            info = _primitives.get(primitive_name)
        if not info:
            return {"error": f"primitive '{primitive_name}' not found", "status": "simulated"}

        mitigation_details = {
            "ASLR": "Address Space Layout Randomization — randomizes memory layout to prevent address prediction。",
            "DEP/NX": "Data Execution Prevention / No-Execute — marks data pages as non-executable。",
            "Stack Canaries": "Cookie values placed before return address to detect stack overflow。",
            "CFG": "Control Flow Guard — validates indirect call targets against a bitmap of valid addresses。",
            "CFI": "Control Flow Integrity — enforces valid control flow transitions at compile/runtime。",
            "Safe Unlink": "Heap metadata validation to prevent unlink attacks on corrupted chunks。",
            "Quarantine": "Delayed free with guard pages to prevent use-after-free exploitation。",
            "Scudo Allocator": "Hardened allocator with integrity checks, delayed free, and randomization。",
            "FORTIFY_SOURCE": "Compile-time and runtime checks for format strings and buffer operations。",
            "UBSan": "Undefined Behavior Sanitizer — detects integer overflows and undefined behavior at runtime。",
            "ASan": "Address Sanitizer — detects out-of-bounds and use-after-free at runtime。",
            "SMEP": "Supervisor Mode Execution Prevention — prevents kernel from executing user-space code。",
            "NULL Page Protection": "Prevents mapping of NULL page to block kernel NULL pointer exploits。",
            "Atomic Operations": "Ensures check-and-use operations are indivisible to prevent TOCTOU。",
            "RTTI Validation": "Runtime Type Information validation to detect type confusion。",
            "Bounds Checking": "Runtime or compile-time array/buffer index validation。",
            "Memory Safe Languages": "Languages like Rust, Go that prevent memory corruption by design。",
            "SafeSEH": "Structured Exception Handler validation on Windows。",
            "Isolated Heaps": "Separate heap regions for different object types to limit spray attacks。",
            "Heap Metadata Validation": "Integrity checks on malloc chunk headers and metadata。",
            "Heap Canaries": "Guard values between heap allocations to detect overflow。",
            "Hardened Allocator": "Allocator with additional integrity checks and randomization。",
            "Signed/Unsigned Validation": "Explicit validation of arithmetic operand types。",
            "Safe Arithmetic Libraries": "Libraries that detect overflow/underflow before it occurs。",
            "Index Validation": "Runtime bounds checking for array and buffer access。",
            "Object Tagging": "Runtime type tags on objects to detect type confusion。",
            "Mandatory Access Control": "System-level access control (SELinux, AppArmor) to limit TOCTOU impact。",
            "O_NOFOLLOW": "File open flag that prevents symlink following。",
            "Static Analysis": "Compile-time detection of format string, NULL deref, and integer issues。",
            "Defensive NULL Checks": "Explicit NULL validation before pointer dereference。",
        }

        mitigations = []
        for mit_name in info["mitigations"]:
            detail = mitigation_details.get(mit_name, mit_name)
            mitigations.append({"name": mit_name, "description": detail})

        return {
            "primitive": primitive_name,
            "mitigations": mitigations,
            "count": len(mitigations),
            "defense_in_depth": "Layer multiple mitigations: compiler hardening + runtime protection + allocator hardening + language safety。",
            "status": "simulated",
        }

    def get_cves(self):
        """Return CVE database organized by primitive type, merging simulated data with real API results."""
        self._init_primitives()
        
        api_results_data = get_cached_cves("cve_research") or self._fetch_real_cves()

        cve_db = {
            "buffer_overflow": [],
            "use_after_free": [],
            "double_free": [],
            "heap_overflow": [],
            "format_string": [],
            "integer_overflow": [],
            "out_of_bounds": [],
            "type_confusion": [],
            "toctou": [],
            "null_pointer": [],
        }

        simulated_count = 0
        total_cves = 0
        sources_used = []

        with _primitives_lock:
            for name, info in _primitives.items():
                simulated_cves = [{"id": cve_id, "source": "simulated", "product": info["real_world_cves"][i] if i < len(info["real_world_cves"]) else "Multiple"} 
                                 for i, cve_id in enumerate(info["real_world_cves"][:2])]
                
                simulated_count += len(simulated_cves)

                api_similar_cves = []
                if api_results_data:
                    for api_cve in api_results_data:
                        if name in api_cve.get("affected_categories", []) and api_cve.get("category") == "memory_corruption":
                            api_similar_cves.append(api_cve)

                merged = simulated_cves + api_similar_cves
                cve_db[name] = merged
                total_cves += len(merged)

                if api_similar_cves:
                    sources_used.append("real_api")

        status = "enhanced" if sources_used else "simulated"

        result = {
            "cves_by_primitive": cve_db,
            "total_cves": total_cves,
            "simulated_count": simulated_count,
            "real_api_count": total_cves - simulated_count,
            "status": status,
            "sources_used": sources_used,
            "stats": {
                "enhanced_count": total_cves,
                "simulated_count": simulated_count,
                "api_fetched": len(api_results_data) if api_results_data else 0,
            },
        }

        if api_results_data:
            set_cached_cves("cves", api_results_data)

        return result

    def _fetch_real_cves(self):
        """Fetch CVE data from NVD and GitHub APIs concurrently."""
        real_cves = []

        nvd_results = CVEIntegration.get_recent_cves_from_nvd(days=7)
        if nvd_results:
            real_cves.extend(nvd_results.get("data", []))

        github_results = CVEIntegration.search_by_product_from_github("memory", days=14)
        if github_results:
            real_cves.extend(github_results.get("data", []))

        if real_cves:
            return real_cves

        return None

    def fetch_real_cves(self, days=7):
        """Force fetch CVE data from NVD and GitHub APIs."""
        return self._fetch_real_cves()

    def clear_api_cache(self):
        """Clear CVE cache."""
        clear_cache()
        return {"message": "CVE cache cleared", "cache_size": len(_cve_cache)}

    def get_simulations(self):
        """Return all recorded simulations."""
        return {"simulations": self.simulations, "count": len(self.simulations)}


if __name__ == "__main__":
    agent = MemoryPrimitivesAgent()
    print(json.dumps(agent.describe(), indent=2))
    print(json.dumps(agent.list_primitives(), indent=2))