---
name: lotl-strategies
description: Advanced "Living off the Land" (LotL) and exotic execution strategies. Focuses on using legitimate system binaries (LOLBins) to perform malicious actions undetected.
---

# Living off the Land (LotL)

This skill focuses on minimizing the footprint by avoiding custom binaries.

## LotL Techniques
- **Binary Proxy Execution**: Using `rundll32.exe`, `msiexec.exe`, or `certutil.exe` to run payloads.
- **Scripting Engines**: Leveraging `PowerShell`, `WMI`, and `bash` for stealthy lateral movement.
- **Registry-Based Persistence**: Storing payloads in the registry to avoid disk-based detection.
- **Exotic Protocols**: Using DNS, ICMP, or custom application protocols for C2 traffic.

## Strategy Selection
1. **Binary Inventory**: Scan the target system for available LOLBins.
2. **Chain Construction**: Build a sequence of legitimate commands that result in the desired outcome.
3. **Evasion Check**: Ensure the chain does not trigger common EDR behavioral alerts.
