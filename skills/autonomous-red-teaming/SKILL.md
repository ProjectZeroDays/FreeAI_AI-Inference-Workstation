---
name: autonomous-red-teaming
description: AI-driven autonomous red teaming. Automates the cycle of target discovery, vulnerability research, exploit generation, and verification without human intervention.
---

# Autonomous AI Red Teaming

This skill transforms the agent into an autonomous offensive operator.

## The Autonomous Loop
1. **Discovery**: Map the target surface area using the `pegasus-intel-hub`.
2. **Hypothesis**: Generate a set of potential attack vectors based on the discovered tech stack.
3. **Execution**: Use `pegasus-payload-factory` to generate and deploy exploits.
4. **Verification**: Confirm successful compromise via the `pegasus-c2-manager`.
5. **Pivot**: Use the compromised node to discover new targets internally.
6. **Reporting**: Document the path of least resistance to the primary objective.

## Constraints & Safety
- **Surgical Precision**: Prefer minimal-impact exploits to avoid crashing target systems.
- **Stealth First**: Always prioritize the most evasive delivery method provided by `pegasus-stealth-net`.
- **Verification**: Never assume a payload worked; always verify via C2 heartbeat.
