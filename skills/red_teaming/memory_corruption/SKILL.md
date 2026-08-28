---
name: memory_corruption
description: >
  Memory corruption exploit simulation: buffer overflow, heap corruption, use-after-free, format string,
  ROP chains, and shellcode templates for defensive research and red team planning.
triggers:
  - memory corruption
  - buffer overflow
  - heap corruption
  - use-after-free
  - format string
  - rop chain
  - shellcode
  - CVE-2019-3568
category: red_teaming
auto_generated: false
enabled: true
metadata:
  created_at: "2026-08-28"
  agent: agents/specialized/memory_corruption.py
---

# Memory Corruption Exploit Simulation Agent

Simulated memory corruption exploitation for defensive research and red team education.

## Purpose
Study and simulate memory corruption vulnerabilities: buffer overflows, heap corruption, use-after-free, and format string attacks. All outputs are simulated — no real exploit code or payloads.

## Capabilities
- **Buffer Overflow Simulation**: Stack-based and heap-based overflow scenarios
- **Heap Corruption**: Chunk manipulation, unlink attacks, tcache poisoning (simulated)
- **Use-After-Free**: Dangling pointer exploitation patterns (simulated)
- **Format String Attacks**: %n write primitives, info leak patterns (simulated)
- **Payload Generation**: NOP sleds, ROP chains, shellcode templates (simulated)
- **Evasion Techniques**: Polymorphic shellcode, metamorphic code, anti-analysis (simulated)
- **CVE Reference**: CVE-2019-3568 (WhatsApp), CVE-2019-8641 (iMessage), CVE-2018-4990 (Acrobat)

## Usage
```python
from agents.specialized.memory_corruption import MemoryCorruptionAgent

agent = MemoryCorruptionAgent()
# Describe capabilities
desc = agent.describe()
# Simulate buffer overflow
result = agent.simulate_buffer_overflow("192.168.1.10", "stack", 256)
# Simulate heap corruption
heap = agent.simulate_heap_corruption("tcache_poisoning")
# Generate simulated payload
payload = agent.generate_payload("nop_sled", arch="x86_64")
# Get CVE references
cves = agent.get_cves()
```

## Simulation Disclaimer
All methods return `{"status": "simulated"}`. No real exploit code, payloads, or attack mechanisms are generated. This agent is for defensive research, vulnerability analysis, and red team planning education only.
