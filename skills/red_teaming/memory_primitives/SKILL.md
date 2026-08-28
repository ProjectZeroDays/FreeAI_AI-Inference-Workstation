---
name: memory_primitives
description: >
  Memory corruption primitive simulation: buffer overflow, use-after-free, double-free,
  heap overflow, format string, integer overflow, out-of-bounds, type confusion,
  TOCTOU race condition, and null pointer dereference.
triggers:
  - memory corruption
  - buffer overflow
  - use-after-free
  - double free
  - heap overflow
  - format string
  - integer overflow
  - out-of-bounds
  - type confusion
  - TOCTOU
  - race condition
  - null pointer
  - primitive selection
  - gadget discovery
category: red_teaming
auto_generated: false
enabled: true
metadata:
  created_at: "2026-08-28"
  agent: agents/specialized/memory_primitives.py
---

# Memory Corruption Primitives Agent

Comprehensive simulation of memory corruption primitives for defensive research and red team education.

## Purpose

Model, simulate, and analyze the 10 fundamental memory corruption primitives that underlie real-world exploits. Each primitive is simulated — no actual exploit code or payloads are generated.

## Primitives

1. **Buffer Overflow (Stack/Heap)** — Writing beyond allocated buffer boundaries to overwrite adjacent memory. Stack overflows target return addresses and local variables; heap overflows target malloc metadata and adjacent chunks.
2. **Use-After-Free (UAF)** — Accessing heap memory after it has been freed, allowing attackers to control object state and achieve arbitrary code execution via vtable hijacking or function pointer overwrite.
3. **Double-Free** — Calling free() twice on the same pointer, corrupting allocator metadata (fastbin/tcache) to achieve arbitrary write or allocation control.
4. **Heap Overflow / Chunk Overflow** — Overflowing a heap allocation to corrupt adjacent chunk headers or data, enabling unlink attacks, tcache poisoning, or house-of-* techniques.
5. **Format String Vulnerability** — Exploiting unchecked format string arguments (printf family) to leak stack memory (%p/%x), write arbitrary addresses (%n), or control execution flow.
6. **Integer Overflow / Underflow** — Arithmetic operations that wrap around type boundaries, causing undersized allocations, incorrect loop bounds, or bypassed security checks.
7. **Out-of-Bounds Read/Write** — Accessing array or buffer indices outside valid range, enabling information disclosure (OOB read) or memory corruption (OOB write).
8. **Type Confusion** — Treating an object as an incorrect type, leading to misinterpreted memory layout, vtable mismatch, or incorrect method dispatch.
9. **Race Condition (TOCTOU)** — Time-of-check to time-of-use vulnerabilities where state changes between validation and use, enabling privilege escalation or file system attacks.
10. **Null Pointer Dereference** — Dereferencing a NULL or uninitialized pointer, causing crashes (DoS) or, in kernel mode, potential privilege escalation via NULL page mapping.

## AI-Assisted Analysis

- **Primitive Selection**: AI analyzes target binary characteristics (architecture, mitigations, input vectors) to recommend the most viable primitive.
- **Automatic Gadget Discovery**: Simulated ROP/JOP gadget enumeration for chain construction.
- **Exploit Viability Scoring**: 0-100 score based on mitigation bypass difficulty, reliability, and impact.

## Primitive-to-Exploit Mapping

| Primitive | Common Exploit Technique | Real-World CVEs |
|-----------|------------------------|-----------------|
| Buffer Overflow | Stack smashing, ROP chains, ret2libc | CVE-2019-3568, CVE-2014-0160 |
| Use-After-Free | Vtable hijacking, fake objects | CVE-2018-4990, CVE-2021-26855 |
| Double-Free | Fastbin dup, tcache poisoning | CVE-2020-13777, CVE-2019-11043 |
| Heap Overflow | Unlink attack, house-of-force | CVE-2021-3156, CVE-2023-36844 |
| Format String | Stack read/write, GOT overwrite | CVE-2021-4034, CVE-2017-5638 |
| Integer Overflow | Undersized allocation, loop bypass | CVE-2019-18276, CVE-2020-8835 |
| Out-of-Bounds | Info leak, arbitrary write | CVE-2021-44228, CVE-2019-5736 |
| Type Confusion | Virtual call hijacking | CVE-2021-21148, CVE-2023-4863 |
| TOCTOU | Symlink race, permission bypass | CVE-2021-3156, CVE-2019-14287 |
| Null Pointer | Kernel NULL page mapping | CVE-2017-1000112, CVE-2016-0728 |

## Mitigation Techniques

- **ASLR** — Address Space Layout Randomization (bypassed via info leaks, partial overwrites)
- **DEP/NX** — Data Execution Prevention / No-Execute (bypassed via ROP, JOP, ret2libc)
- **Stack Canaries** — Cookie values before return address (bypassed via info leak, brute force)
- **CFG/CFI** — Control Flow Guard / Integrity (bypassed via type confusion, COOP)
- **Safe Unlink** — Heap metadata validation (bypassed via house-of-* techniques)
- **Quarantine** — Delayed free with guard pages (bypassed via spray, timing)
- **Hardened Allocator** — Scudo, hardened_malloc (bypassed via novel primitives)
- **SMEP/SMAP** — Supervisor Memory Execute/Access Prevent (kernel mode)
- **PAC** — Pointer Authentication Codes (ARM, bypassed via pointer reuse)
- **KASLR** — Kernel ASLR (bypassed via kernel info leaks)

## Usage

```python
from agents.specialized.memory_primitives import MemoryPrimitivesAgent

agent = MemoryPrimitivesAgent()

# List all primitives
primitives = agent.list_primitives()

# Get details on a specific primitive
details = agent.get_primitive("buffer_overflow")

# Simulate exploitation (returns {"status": "simulated"})
result = agent.simulate_primitive("buffer_overflow", {
    "target": "192.168.1.10",
    "overflow_type": "stack",
    "buffer_size": 256
})

# Map primitive to exploit techniques
mapping = agent.map_to_exploit("use_after_free")

# Find mitigations
mitigations = agent.find_mitigations("format_string")

# Get CVE database
cves = agent.get_cves()
```

## Simulation Guarantee

All methods return `{"status": "simulated"}` — no real exploit code, no actual payloads, no working attack mechanisms. This agent is for defensive research and red team planning only.
