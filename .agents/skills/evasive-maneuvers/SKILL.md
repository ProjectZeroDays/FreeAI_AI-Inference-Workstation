---
name: evasive-maneuvers
description: Advanced evasion and anti-analysis techniques. Focuses on bypassing EDR, AV, and sandbox environments using polymorphic code and stealthy execution.
---

# Evasive Maneuvers

This skill provides the logic for staying undetected on a target system.

## Evasion Categories
- **Anti-Analysis**: Detecting VMs, sandboxes, and debuggers (e.g., checking for specific MAC addresses or timing attacks).
- **Payload Obfuscation**: Using polymorphic engines to change the binary signature of the payload.
- **Execution Stealth**: Utilizing process hollowing, DLL sideloading, or reflective loading to avoid disk-based detection.
- **Traffic Stealth**: Implementing DoH, domain fronting, or custom encryption for C2 communication.

## The Evasion Cycle
1. **Analysis**: Identify the target's security stack (EDR/AV/SIEM).
2. **Tweak**: Adjust the payload's encryption and obfuscation to bypass known signatures.
3. **Test**: Run the payload in a mirrored environment to verify it remains undetected.
4. **Deploy**: Execute the most stealthy version.
