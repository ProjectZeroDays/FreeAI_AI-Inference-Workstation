---
name: VulnScannerAgent
description: >
  CVE vulnerability scanning
triggers:
  - exploit
  - VulnScannerAgent
  - attack
  - vulnerability
category: red_teaming
auto_generated: true
enabled: true
metadata:
  created_at: "2026-08-28"
  agent: agents/specialized/vulnscanneragent.py
---

# VulnScannerAgent

CVE vulnerability scanning.

## Capabilities
- Vulnerability scanning and exploitation
- Payload generation and delivery
- Post-exploitation and persistence
- Evasion techniques

## Usage
```python
from vulnscanneragent import VulnScannerAgent
agent = VulnScannerAgent()
result = agent.describe()
```
