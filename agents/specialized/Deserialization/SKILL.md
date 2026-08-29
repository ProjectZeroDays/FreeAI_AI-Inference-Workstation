---
name: DeserializationAgent
description: >
  Deserialization vulnerability exploitation
triggers:
  - exploit
  - DeserializationAgent
  - attack
  - vulnerability
category: red_teaming
auto_generated: true
enabled: true
metadata:
  created_at: "2026-08-28"
  agent: agents/specialized/deserializationagent.py
---

# DeserializationAgent

Deserialization vulnerability exploitation.

## Capabilities
- Vulnerability scanning and exploitation
- Payload generation and delivery
- Post-exploitation and persistence
- Evasion techniques

## Usage
```python
from deserializationagent import DeserializationAgent
agent = DeserializationAgent()
result = agent.describe()
```
