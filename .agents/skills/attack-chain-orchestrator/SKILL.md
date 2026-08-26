---
name: attack-chain-orchestrator
description: End-to-end orchestration of the Cyber Kill Chain. Coordinates the transition between reconnaissance, weaponization, delivery, exploitation, installation, C2, and actions on objectives.
---

# Attack Chain Orchestrator

This skill acts as the "brain" that connects individual tools into a seamless attack flow.

## The Pegasus Kill Chain
1. **Reconnaissance**: Use `pegasus-intel-hub` to map the target.
2. **Weaponization**: Use `pegasus-payload-factory` to create a tailored exploit.
3. **Delivery**: Use `pegasus-stealth-net` to deliver the payload via the optimal vector.
4. **Exploitation**: Trigger the zero-click exploit to gain initial access.
5. **Installation**: Use `pegasus-post-ex` to install persistence (Rootkits).
6. **C2 Establishment**: Connect the agent to `pegasus-c2-manager`.
7. **Actions on Objectives**: Execute the final mission (exfiltration, sabotage, or surveillance).

## Orchestration Logic
- **Conditional Branching**: If "Delivery" fails, the orchestrator automatically pivots to a different vector.
- **State Management**: Tracks the current phase and ensures all prerequisites (e.g., persistence) are met before advancing.
- **Stealth Synchronization**: Ensures all actions are aligned with the current `evasive-maneuvers` profile.
