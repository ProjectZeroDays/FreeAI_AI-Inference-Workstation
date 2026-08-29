---
name: MessagingRCEAgent
description: >
  Messaging protocol RCE exploitation
triggers:
  - exploit
  - MessagingRCEAgent
  - attack
  - vulnerability
category: red_teaming
auto_generated: true
enabled: true
metadata:
  created_at: "2026-08-28"
  agent: agents/specialized/messagingrceagent.py
---

# MessagingRCEAgent

Messaging protocol RCE exploitation.

## Capabilities
- Vulnerability scanning and exploitation
- Payload generation and delivery
- Post-exploitation and persistence
- Evasion techniques

## Usage
```python
from messagingrceagent import MessagingRCEAgent
agent = MessagingRCEAgent()
result = agent.describe()
```
