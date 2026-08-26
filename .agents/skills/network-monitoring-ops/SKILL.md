---
name: network-monitoring-ops
description: Professional network monitoring and traffic analysis. Focuses on detecting C2 heartbeats, data exfiltration, and anomalous network behaviors.
---

# Network Monitoring & Ops

This skill provides the capability to analyze network traffic for adversarial signatures.

## Monitoring Objectives
- **C2 Detection**: Identifying beacons, heartbeats, and long-polling connections.
- **Exfiltration Detection**: Spotting data spikes, unusual protocol usage (e.g., ICMP tunneling), and rare destination IPs.
- **Anomaly Detection**: Baseling "normal" traffic and alerting on deviations.

## Analysis Techniques
- **Traffic Pattern Analysis**: Looking for fixed-interval requests (beacons) or jitter-based communication.
- **Protocol Inspection**: Analyzing DoH, DNS, and HTTPS headers for anomalies.
- **Flow Analysis**: Monitoring NetFlow/IPFIX for unusual internal-to-internal movements (lateral movement).

## Tooling Integration
- Use `tcpdump`/`Wireshark` for packet captures.
- Integrate with `Zeek` or `Suricata` for automated IDS/NSM alerts.
