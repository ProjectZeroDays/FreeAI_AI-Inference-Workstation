#!/usr/bin/env python3
"""Memory Corruption Primitives Agent — simulation-only for defensive research and red team education."""
import json
import threading
import time
from pathlib import Path

ROOT = Path(__file__).parent.parent

_primitives_lock = threading.Lock()
_primitives = {}


class MemoryPrimitivesAgent:
    """Simulated memory corruption primitives for defensive research and red team education."""

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
                    "real_world_cves": ["CVE-2019-3568", "CVE-2014-0160", "CVE-2003-0252"],
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
                    "real_world_cves": ["CVE-2018-4990", "CVE-2021-26855", "CVE-2014-1776"],
                    "mitigations": ["CFI", "Safe Unlink", "Quarantine", "Isolated Heaps"],
                    "ai_selection_score": 90,
                    "difficulty": "medium",
                    "impact": "critical",
                },
                "double_free": {
                    "name": "Double-Free",
                    "category": "memory_corruption",
                    "description": "Calling free() twice on the same pointer, corrupting allocator metadata.",
                    "subtypes": ["fastbin_dup", "tcache_poisoning", "smallbin_attack"],
                    "exploitation_mechanics": "Corrupt freelist to achieve arbitrary write or control next malloc return value.",
                    "real_world_cves": ["CVE-2020-13777", "CVE-2019-11043", "CVE-2017-1000377"],
                    "mitigations": ["Safe Unlink", "Double-Free Detection", "Quarantine", "Scudo Allocator"],
                    "ai_selection_score": 75,
                    "difficulty": "medium",
                    "impact": "high",
                },
                "heap_overflow": {
                    "name": "Heap Overflow / Chunk Overflow",
                    "category": "memory_corruption",
                    "description": "Overflowing a heap allocation to corrupt adjacent chunk headers or data.",
                    "subtypes": ["unlink_attack", "house_of_force", "tcache_poisoning", "off_by_one"],
                    "exploitation_mechanics": "Overflow chunk data to corrupt metadata (size, fd/bk pointers) or adjacent chunk, triggering arbitrary write on next free/alloc.",
                    "real_world_cves": ["CVE-2021-3156", "CVE-2023-36844", "CVE-2018-6789"],
                    "mitigations": ["Safe Unlink", "Heap Metadata Validation", "Heap Canaries", "Hardened Allocator"],
                    "ai_selection_score": 80,
                    "difficulty": "high",
                    "impact": "critical",
                },
                "format_string": {
                    "name": "Format String Vulnerability",
                    "category": "memory_corruption",
                    "description": "Exploiting unchecked format string arguments to leak memory or write arbitrary addresses.",
                    "subtypes": ["info_leak", "arbitrary_write", "stack_pivot"],
                    "exploitation_mechanics": "Pass user-controlled string as format argument to printf family functions, using %p/%x to read stack or %n to write.",
                    "real_world_cves": ["CVE-2021-4034", "CVE-2017-5638", "CVE-2000-0812"],
                    "mitigations": ["Compiler Warnings (-Wformat-security)", "FORTIFY_SOURCE", "Format String Auditing", "ASLR"],
                    "ai_selection_score": 65,
                    "difficulty": "medium",
                    "impact": "high",
                },
                "integer_overflow": {
                    "name": "Integer Overflow / Underflow",
                    "category": "memory_corruption",
                    "description": "Arithmetic operations that wrap around type boundaries, causing undersized allocations or bypassed checks.",
                    "subtypes": ["signed_overflow", "unsigned_overflow", "signedness_confusion", "truncation"],
                    "exploitation_mechanics": "Trigger arithmetic wrap to allocate undersized buffer, then overflow; or bypass size/limit checks.",
                    "real_world_cves": ["CVE-2019-18276", "CVE-2020-8835", "CVE-2019-3568"],
                    "mitigations": ["Signed/Unsigned Validation", "Bounds Checking", "UBSan", "Safe Arithmetic Libraries"],
                    "ai_selection_score": 70,
                    "difficulty": "medium",
                    "impact": "high",
                },
                "out_of_bounds": {
                    "name": "Out-of-Bounds Read/Write",
                    "category": "memory_corruption",
                    "description": "Accessing array or buffer indices outside valid range.",
                    "subtypes": ["oob_read", "oob_write", "off_by_one", "negative_index"],
                    "exploitation_mechanics": "Access memory beyond array bounds to leak sensitive data (read) or corrupt adjacent structures (write).",
                    "real_world_cves": ["CVE-2021-44228", "CVE-2019-5736", "CVE-2021-21148"],
                    "mitigations": ["Bounds Checking", "ASan", "Memory Safe Languages", "Index Validation"],
                    "ai_selection_score": 78,
                    "difficulty": "low-medium",
                    "impact": "high",
                },
                "type_confusion": {
                    "name": "Type Confusion",
                    "category": "memory_corruption",
                    "description": "Treating an object as an incorrect type, leading to misinterpreted memory layout or method dispatch.",
                    "subtypes": ["vtable_mismatch", "incorrect_cast", "prototype_pollution", "class_hierarchy_abuse"],
                    "exploitation_mechanics": "Confuse type system to interpret memory as different object type, triggering incorrect virtual call or field access.",
                    "real_world_cves": ["CVE-2021-21148", "CVE-2023-4863", "CVE-2016-4657"],
                    "mitigations": ["RTTI Validation", "Type-Safe Languages", "CFI", "Object Tagging"],
                    "ai_selection_score": 88,
                    "difficulty": "high",
                    "impact": "critical",
                },
                "toctou": {
                    "name": "Race Condition (TOCTOU)",
                    "category": "memory_corruption",
                    "description": "Time-of-check to time-of-use vulnerability where state changes between validation and use.",
                    "subtypes": ["symlink_race", "file_permission_race", "check_use_race", "signal_race"],
                    "exploitation_mechanics": "Modify resource between check (e.g., permission validation) and use (e.g., file access) to bypass security controls.",
                    "real_world_cves": ["CVE-2021-3156", "CVE-2019-14287", "CVE-2019-5736"],
                    "mitigations": ["Atomic Operations", "File Descriptor Passing", "Mandatory Access Control", "O_NOFOLLOW"],
                    "ai_selection_score": 60,
                    "difficulty": "medium-high",
                    "impact": "high",
                },
                "null_pointer": {
                    "name": "Null Pointer Dereference",
                    "category": "memory_corruption",
                    "description": "Dereferencing a NULL or uninitialized pointer, causing crashes or potential privilege escalation.",
                    "subtypes": ["user_mode_crash", "kernel_null_page", "uninitialized_pointer", "double_deref"],
                    "exploitation_mechanics": "Trigger NULL deref for DoS, or in kernel mode map NULL page to control dereferenced data for privilege escalation.",
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
            "description": "Memory corruption primitive simulation: buffer overflow, use-after-free, double-free, heap overflow, format string, integer overflow, out-of-bounds, type confusion, TOCTOU, null pointer dereference.",
            "category": "red_teaming",
            "capabilities": [
                "describe",
                "list_primitives",
                "get_primitive",
                "simulate_primitive",
                "map_to_exploit",
                "find_mitigations",
                "get_cves",
            ],
            "primitive_count": 10,
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
            "ASLR": "Address Space Layout Randomization — randomizes memory layout to prevent address prediction.",
            "DEP/NX": "Data Execution Prevention / No-Execute — marks data pages as non-executable.",
            "Stack Canaries": "Cookie values placed before return address to detect stack overflow.",
            "CFG": "Control Flow Guard — validates indirect call targets against a bitmap of valid addresses.",
            "CFI": "Control Flow Integrity — enforces valid control flow transitions at compile/runtime.",
            "Safe Unlink": "Heap metadata validation to prevent unlink attacks on corrupted chunks.",
            "Quarantine": "Delayed free with guard pages to prevent use-after-free exploitation.",
            "Scudo Allocator": "Hardened allocator with integrity checks, delayed free, and randomization.",
            "FORTIFY_SOURCE": "Compile-time and runtime checks for format strings and buffer operations.",
            "UBSan": "Undefined Behavior Sanitizer — detects integer overflows and undefined behavior at runtime.",
            "ASan": "Address Sanitizer — detects out-of-bounds and use-after-free at runtime.",
            "SMEP": "Supervisor Mode Execution Prevention — prevents kernel from executing user-space code.",
            "NULL Page Protection": "Prevents mapping of NULL page to block kernel NULL pointer exploits.",
            "Atomic Operations": "Ensures check-and-use operations are indivisible to prevent TOCTOU.",
            "RTTI Validation": "Runtime Type Information validation to detect type confusion.",
            "Bounds Checking": "Runtime or compile-time array/buffer index validation.",
            "Memory Safe Languages": "Languages like Rust, Go that prevent memory corruption by design.",
            "SafeSEH": "Structured Exception Handler validation on Windows.",
            "Isolated Heaps": "Separate heap regions for different object types to limit spray attacks.",
            "Heap Metadata Validation": "Integrity checks on malloc chunk headers and metadata.",
            "Heap Canaries": "Guard values between heap allocations to detect overflow.",
            "Hardened Allocator": "Allocator with additional integrity checks and randomization.",
            "Signed/Unsigned Validation": "Explicit validation of arithmetic operand types.",
            "Safe Arithmetic Libraries": "Libraries that detect overflow/underflow before it occurs.",
            "Index Validation": "Runtime bounds checking for array and buffer access.",
            "Object Tagging": "Runtime type tags on objects to detect type confusion.",
            "Mandatory Access Control": "System-level access control (SELinux, AppArmor) to limit TOCTOU impact.",
            "O_NOFOLLOW": "File open flag that prevents symlink following.",
            "Static Analysis": "Compile-time detection of format string, NULL deref, and integer issues.",
            "Defensive NULL Checks": "Explicit NULL validation before pointer dereference.",
            "Heap Canaries": "Guard values between heap allocations to detect overflow.",
        }

        mitigations = []
        for mit_name in info["mitigations"]:
            detail = mitigation_details.get(mit_name, mit_name)
            mitigations.append({"name": mit_name, "description": detail})

        return {
            "primitive": primitive_name,
            "mitigations": mitigations,
            "count": len(mitigations),
            "defense_in_depth": "Layer multiple mitigations: compiler hardening + runtime protection + allocator hardening + language safety.",
            "status": "simulated",
        }

    def get_cves(self):
        """Return CVE database organized by primitive type."""
        self._init_primitives()
        cve_db = {
            "buffer_overflow": [
                {"id": "CVE-2019-3568", "product": "WhatsApp", "severity": "critical", "description": "Integer overflow in VOIP stack leading to buffer overflow and RCE"},
                {"id": "CVE-2014-0160", "product": "OpenSSL (Heartbleed)", "severity": "critical", "description": "Buffer over-read in TLS heartbeat extension"},
                {"id": "CVE-2003-0252", "product": "Blaster Worm", "severity": "critical", "description": "Stack buffer overflow in Windows RPC DCOM"},
            ],
            "use_after_free": [
                {"id": "CVE-2018-4990", "product": "Adobe Acrobat", "severity": "high", "description": "Use-after-free in PDF parsing allowed arbitrary code execution"},
                {"id": "CVE-2021-26855", "product": "Microsoft Exchange", "severity": "critical", "description": "UAF in Exchange server deserialization"},
                {"id": "CVE-2014-1776", "product": "Internet Explorer", "severity": "critical", "description": "Use-after-free in CDisplayPointer enabling sandbox escape"},
            ],
            "double_free": [
                {"id": "CVE-2020-13777", "product": "GnuTLS", "severity": "high", "description": "Double-free in certificate parsing"},
                {"id": "CVE-2019-11043", "product": "PHP-FPM", "severity": "critical", "description": "Double-free in fastcgi handling leading to RCE"},
                {"id": "CVE-2017-1000377", "product": "Sudo", "severity": "high", "description": "Double-free in get_process_ttyname"},
            ],
            "heap_overflow": [
                {"id": "CVE-2021-3156", "product": "Sudo (Baron Samedit)", "severity": "critical", "description": "Heap-based buffer overflow in sudoers parsing"},
                {"id": "CVE-2023-36844", "product": "Windows Error Reporting", "severity": "critical", "description": "Heap overflow in WER service"},
                {"id": "CVE-2018-6789", "product": "Exim", "severity": "critical", "description": "Heap overflow in base64 decoding"},
            ],
            "format_string": [
                {"id": "CVE-2021-4034", "product": "Polkit (PwnKit)", "severity": "high", "description": "Format string / injection in pkexec environment handling"},
                {"id": "CVE-2017-5638", "product": "Apache Struts", "severity": "critical", "description": "Format string in Content-Type header parsing"},
                {"id": "CVE-2000-0812", "product": "Wu-FTP", "severity": "high", "description": "Format string in site exec command"},
            ],
            "integer_overflow": [
                {"id": "CVE-2019-18276", "product": "Bash", "severity": "high", "description": "Integer overflow in funcname stack array index"},
                {"id": "CVE-2020-8835", "product": "Linux Kernel (BPF)", "severity": "critical", "description": "Integer overflow in BPF verifier leading to OOB write"},
                {"id": "CVE-2019-3568", "product": "WhatsApp", "severity": "critical", "description": "Integer overflow in VOIP RTP packet size calculation"},
            ],
            "out_of_bounds": [
                {"id": "CVE-2021-44228", "product": "Apache Log4j", "severity": "critical", "description": "OOB read in JNDI lookup processing"},
                {"id": "CVE-2019-5736", "product": "runc", "severity": "high", "description": "OOB write in container process re-execution"},
                {"id": "CVE-2021-21148", "product": "Chrome V8", "severity": "high", "description": "OOB access in V8 TypedArray"},
            ],
            "type_confusion": [
                {"id": "CVE-2021-21148", "product": "Chrome V8", "severity": "high", "description": "Type confusion in V8 object handling"},
                {"id": "CVE-2023-4863", "product": "Chrome WebP", "severity": "critical", "description": "Type confusion in WebP image parsing"},
                {"id": "CVE-2016-4657", "product": "iOS Kernel", "severity": "critical", "description": "Type confusion in IOKit driver"},
            ],
            "toctou": [
                {"id": "CVE-2021-3156", "product": "Sudo", "severity": "critical", "description": "TOCTOU in sudoers file parsing"},
                {"id": "CVE-2019-14287", "product": "Sudo", "severity": "high", "description": "TOCTOU in user ID validation"},
                {"id": "CVE-2019-5736", "product": "runc", "severity": "high", "description": "TOCTOU in container file descriptor handling"},
            ],
            "null_pointer": [
                {"id": "CVE-2017-1000112", "product": "Linux Kernel (Netfilter)", "severity": "high", "description": "NULL pointer dereference in nf_nat_manip_pkt"},
                {"id": "CVE-2016-0728", "product": "Linux Kernel (Keyring)", "severity": "high", "description": "NULL dereference in keyring reference counting"},
                {"id": "CVE-2019-2215", "product": "Android Kernel (Binder)", "severity": "critical", "description": "NULL dereference in binder driver"},
            ],
        }

        total = sum(len(v) for v in cve_db.values())
        return {"cves_by_primitive": cve_db, "total_cves": total, "status": "simulated"}

    def get_simulations(self):
        """Return all recorded simulations."""
        return {"simulations": self.simulations, "count": len(self.simulations)}


if __name__ == "__main__":
    agent = MemoryPrimitivesAgent()
    print(json.dumps(agent.describe(), indent=2))
    print(json.dumps(agent.list_primitives(), indent=2))
