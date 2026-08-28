---
name: deserialization
description: >
  Deserialization exploit simulation: Java/Python/PHP deserialization RCE, gadget chains,
  ysoserial-style payloads for defensive research and red team planning.
triggers:
  - deserialization
  - gadget chain
  - ysoserial
  - java deserialization
  - python pickle
  - php unserialize
  - CVE-2021-44228
category: red_teaming
auto_generated: false
enabled: true
metadata:
  created_at: "2026-08-28"
  agent: agents/specialized/deserialization.py
---

# Deserialization Exploit Simulation Agent

Simulated deserialization exploitation for defensive research and red team education.

## Purpose
Study and simulate unsafe deserialization vulnerabilities across Java, Python, and PHP: gadget chain generation, RCE patterns, and real-world CVE analysis. All outputs are simulated — no real exploit code or payloads.

## Capabilities
- **Java Deserialization**: CommonsCollections chains, ysoserial-style payloads (simulated)
- **Python Deserialization**: pickle, yaml, marshal unsafe loading (simulated)
- **PHP Deserialization**: unserialize() gadget chains, POP chains (simulated)
- **Gadget Chain Generation**: Object graph construction for RCE (simulated)
- **Log4Shell Analysis**: CVE-2021-44228 JNDI injection patterns (simulated)
- **Detection Patterns**: Signature-based and behavioral detection guidance
- **CVE Reference**: Log4Shell CVE-2021-44228, hypothetical Java app CVEs

## Usage
```python
from agents.specialized.deserialization import DeserializationAgent

agent = DeserializationAgent()
# Describe capabilities
desc = agent.describe()
# Simulate Java deserialization
result = agent.simulate_java_deserialization("CommonsCollections", "6")
# Simulate Python pickle exploit
py_result = agent.simulate_python_deserialization("pickle", "os.system")
# Generate simulated gadget chain
chain = agent.generate_gadget_chain("java", "CommonsCollections7")
# Get CVE references
cves = agent.get_cves()
```

## Simulation Disclaimer
All methods return `{"status": "simulated"}`. No real exploit code or payloads are generated. This agent is for defensive research, vulnerability analysis, and red team planning education only.
