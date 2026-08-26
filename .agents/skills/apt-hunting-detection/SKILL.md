---
name: apt-hunting-detection
description: Advanced Persistent Threat (APT) hunting and threat detection. Focuses on identifying stealthy intruders using TTP mapping, IoC analysis, and behavioral anomalies.
---

# APT Hunting & Threat Detection

This skill focuses on finding the "unfindable" intruders.

## Hunting Methodologies
- **Indicator-Based Hunting**: Searching for known hashes, IPs, and domains (IoCs).
- **Behavioral Hunting**: Identifying anomalous patterns (e.g., unusual PowerShell usage, unexpected outbound traffic to rare TLDs).
- **TTP Mapping**: Aligning observed behaviors to the MITRE ATT&CK framework to predict the attacker's next move.

## Detection Focus Areas
- **Persistence**: Hunting for unusual scheduled tasks, registry keys, or WMI event consumers.
- **Lateral Movement**: Monitoring for abnormal SMB/RPC traffic or credential dumping (LSASS access).
- **Exfiltration**: Detecting high-volume data transfers or "heartbeat" patterns in DoH/DNS traffic.

## The Hunting Loop
1. **Hypothesis**: "I believe an attacker is using [TTP] to maintain persistence."
2. **Data Collection**: Gather logs (Event Logs, Sysmon, Network PCAPs).
3. **Analysis**: Filter noise and look for the hypothesis pattern.
4. **Verification**: Confirm the finding is malicious and not a system fluke.
