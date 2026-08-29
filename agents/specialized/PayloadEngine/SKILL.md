---
name: PayloadEngineAgent
description: >
  Payload generation and obfuscation
triggers:
  - exploit
  - PayloadEngineAgent
  - attack
  - vulnerability
category: red_teaming
auto_generated: true
enabled: true
metadata:
  created_at: "2026-08-28"
  agent: agents/specialized/payloadengineagent.py
---

# PayloadEngineAgent

Payload generation and obfuscation.

## Capabilities
- Vulnerability scanning and exploitation
- Payload generation and delivery
- Post-exploitation and persistence
- Evasion techniques

## Usage
```python
from payloadengineagent import PayloadEngineAgent
agent = PayloadEngineAgent()
result = agent.describe()
```
