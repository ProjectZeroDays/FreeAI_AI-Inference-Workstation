---
name: quantum-c2-network-security-hardening
description: >
  Quantum C2 network security hardening skill. Use when the user asks about network hardening, firewall configuration, security scanning, or network defense. Triggers on: "network hardening", "firewall", "IDS", "IPS", "network segmentation", "port knocking", "threat detection", "network defense", "security scanning".
---

# Quantum C2 Network Security Hardening

Configure and manage network security hardening across Quantum C2 infrastructure.

## Firewall Management

### iptables Configuration
```bash
# List current rules
GET /api/hardening/firewall/iptables/rules
```

**Response:**
```json
{
  "tables": {
    "filter": {
      "chains": {
        "INPUT": [
          {"rule": "-A INPUT -m state --state ESTABLISHED,RELATED -j ACCEPT", "num": 1},
          {"rule": "-A INPUT -p tcp --dport 22 -j ACCEPT", "num": 2},
          {"rule": "-A INPUT -j DROP", "num": 3}
        ],
        "FORWARD": [{"rule": "-A FORWARD -j DROP", "num": 1}],
        "OUTPUT": [{"rule": "-A OUTPUT -j ACCEPT", "num": 1}]
      }
    },
    "nat": {
      "chains": {
        "PREROUTING": [],
        "OUTPUT": [],
        "POSTROUTING": []
      }
    }
  }
}
```

### nftables Configuration
```bash
# List sets and rules
GET /api/hardening/firewall/nftables/sets
GET /api/hardening/firewall/nftables/rules
```

### UFW Configuration
```bash
# List rules
GET /api/hardening/firewall/ufw/rules

# Enable UFW
POST /api/hardening/firewall/ufw/enable

# Set default policy
POST /api/hardening/firewall/ufw/default-policy
{"direction": "incoming", "policy": "deny"}
```

## Network Segmentation

### Create Segments
```bash
POST /api/hardening/network-segments
{
  "name": "DMZ",
  "subnet": "172.16.0.0/24",
  "description": "Demilitarized zone for public services",
  "rules": [
    {"source": "any", "destination": "172.16.0.0/24", "ports": [80, 443], "action": "allow"},
    {"source": "172.16.0.0/24", "destination": "10.0.0.0/8", "ports": [], "action": "deny"}
  ]
}
```

### Get Segments
```bash
GET /api/hardening/network-segments
GET /api/hardening/network-segments/{segment_id}
```

### Segment Analysis
```bash
GET /api/hardening/network-segments/{segment_id}/analysis
```

**Response:**
```json
{
  "segment_id": "seg-dmz",
  "host_count": 5,
  "open_ports": [80, 443],
  "risk_score": 3,
  "recommendations": [
    "Enable network-level encryption",
    "Add intrusion detection monitoring"
  ]
}
```

## IDS/IPS Configuration

### Suricata Configuration
```bash
# Get current config
GET /api/hardening/ids/suricata/config

# Update config
PUT /api/hardening/ids/suricata/config
{
  "HOME_NET": "10.0.0.0/8,172.16.0.0/12,192.168.0.0/16",
  "EXTERNAL_NET": "!$HOME_NET",
  "RULE_PATH": "/etc/suricata/rules",
  "LOG_PATH": "/var/log/suricata"
}
```

### Snort Configuration
```bash
GET /api/hardening/ids/snort/config
PUT /api/hardening/ids/snort/config
```

### Detection Rules
```bash
# List rules
GET /api/hardening/ids/rules

# Add rule
POST /api/hardening/ids/rules
{"rule": "alert tcp any any -> $HOME_NET 443 (msg:\"Suspicious TLS\"; sid:1000001; rev:1;)", "type": "suricata"}

# Test rule
POST /api/hardening/ids/rules/test
{"rule": "alert tcp any any -> $HOME_NET 80 (msg:\"Test Rule\"; sid:1000002;)", "capture": true}
```

## Port Knocking

### Configure Sequence
```bash
POST /api/hardening/port-knocking/sequence
{
  "name": "SSH Access",
  "sequence": [
    {"port": 7, "protocol": "tcp", "wait_ms": 500},
    {"port": 443, "protocol": "tcp", "wait_ms": 500},
    {"port": 80, "protocol": "tcp", "wait_ms": 1000}
  ],
  "target_port": 22,
  "timeout_seconds": 30,
  "whitelist_ips": ["192.168.1.100"]
}
```

### Execute Knock
```bash
POST /api/hardening/port-knocking/knock
{
  "sequence_name": "SSH Access",
  "target": "192.168.1.1"
}
```

### Status Check
```bash
GET /api/hardening/port-knocking/status
```

## Network Encryption

### VPN Configuration
```bash
# OpenVPN
POST /api/hardening/vpn/openvpn/config
{
  "mode": "server",
  "subnet": "10.8.0.0/24",
  "encrypt": "aes-256-gcm",
  "auth": "sha512",
  "tls_version": "1.3"
}

# WireGuard
POST /api/hardening/vpn/wireguard/config
{
  "listen_port": 51820,
  "private_key": "<generated>",
  "peers": [
    {"public_key": "<key>", "allowed_ips": ["10.8.0.2/32"]}
  ]
}
```

### TLS Configuration
```bash
GET /api/hardening/tls/config
PUT /api/hardening/tls/config
{
  "min_version": "TLS1.2",
  "ciphers": ["TLS_AES_256_GCM_SHA384", "TLS_CHACHA20_POLY1305_SHA256"],
  "hsts_enabled": true,
  "hsts_max_age": 31536000
}
```

## Traffic Analysis

### Capture Configuration
```bash
POST /api/hardening/traffic/capture
{
  "interface": "eth0",
  "filter": "tcp port 443",
  "duration_seconds": 300,
  "output_path": "/tmp/capture.pcap"
}
```

### Analysis
```bash
GET /api/hardening/traffic/analysis/{capture_id}
GET /api/hardening/traffic/analysis/{capture_id}/statistics
```

### Anomaly Detection
```bash
POST /api/hardening/traffic/anomaly-detect
{
  "baseline_period_hours": 24,
  "sensitivity": "medium",
  "alert_channels": ["websocket", "email"]
}
```

## Threat Detection

### Live Monitoring
```bash
# WebSocket for real-time
ws://localhost:8000/api/hardening/monitor/ws

# Current threats
GET /api/hardening/threats/active
```

### Threat History
```bash
GET /api/hardening/threats/history?hours=24
GET /api/hardening/threats/history?days=7
```

### Threat Response
```bash
# Acknowledge threat
POST /api/hardening/threats/{threat_id}/acknowledge

# Respond to threat
POST /api/hardening/threats/{threat_id}/respond
{"action": "block_ip", "params": {"ip": "1.2.3.4"}}
```

## Automated Hardening Recommendations

### Full Audit
```bash
POST /api/hardening/audit/full
{
  "scope": "network",
  "checklist": ["firewall", "ids", "encryption", "segmentation", "monitoring"]
}
```

### Quick Check
```bash
GET /api/hardening/audit/quick
```

### Apply Recommendations
```bash
POST /api/hardening/audit/recommendations/apply
{
  "ids": ["rec-001", "rec-002"],
  "dry_run": false
}
```

### Scheduled Audits
```bash
POST /api/hardening/audit/schedule
{
  "type": "cron",
  "cron": "0 3 * * *",
  "scope": "full",
  "notify": true
}
```

## API Reference

### Firewall
```
GET    /api/hardening/firewall/iptables/rules
POST   /api/hardening/firewall/iptables/rules
PUT    /api/hardening/firewall/iptables/rules/{rule_num}
DELETE /api/hardening/firewall/iptables/rules/{rule_num}
GET    /api/hardening/firewall/nftables/sets
POST   /api/hardening/firewall/nftables/sets
GET    /api/hardening/firewall/ufw/rules
POST   /api/hardening/firewall/ufw/enable
```

### Network Segments
```
GET    /api/hardening/network-segments
POST   /api/hardening/network-segments
GET    /api/hardening/network-segments/{id}
PUT    /api/hardening/network-segments/{id}
DELETE /api/hardening/network-segments/{id}
```

### IDS/IPS
```
GET    /api/hardening/ids/suricata/config
PUT    /api/hardening/ids/suricata/config
GET    /api/hardening/ids/rules
POST   /api/hardening/ids/rules
POST   /api/hardening/ids/rules/test
```

### Port Knocking
```
GET    /api/hardening/port-knocking/sequences
POST   /api/hardening/port-knocking/sequence
POST   /api/hardening/port-knocking/knock
GET    /api/hardening/port-knocking/status
```

### VPN/TLS
```
POST   /api/hardening/vpn/openvpn/config
POST   /api/hardening/vpn/wireguard/config
GET    /api/hardening/tls/config
PUT    /api/hardening/tls/config
```

### Traffic
```
POST   /api/hardening/traffic/capture
GET    /api/hardening/traffic/analysis/{id}
POST   /api/hardening/traffic/anomaly-detect
```

### Threats
```
GET    /api/hardening/threats/active
GET    /api/hardening/threats/history
POST   /api/hardening/threats/{id}/acknowledge
POST   /api/hardening/threats/{id}/respond
```

### Audit
```
POST   /api/hardening/audit/full
GET    /api/hardening/audit/quick
POST   /api/hardening/audit/recommendations/apply
POST   /api/hardening/audit/schedule
```

## Workflows

### Full Hardening Audit
```bash
# 1. Run quick check
curl http://localhost:8000/api/hardening/audit/quick

# 2. Run full audit
curl -X POST http://localhost:8000/api/hardening/audit/full \
  -H "Content-Type: application/json" \
  -d '{"scope": "network", "checklist": ["firewall", "ids", "encryption"]}'

# 3. Apply recommendations
curl -X POST http://localhost:8000/api/hardening/audit/recommendations/apply \
  -H "Content-Type: application/json" \
  -d '{"ids": ["rec-001", "rec-002"], "dry_run": false}'

# 4. Schedule recurring audits
curl -X POST http://localhost:8000/api/hardening/audit/schedule \
  -H "Content-Type: application/json" \
  -d '{"type": "cron", "cron": "0 3 * * *"}'
```

### Configure Firewall Rules
```bash
# 1. List current rules
curl http://localhost:8000/api/hardening/firewall/iptables/rules

# 2. Add allow rule
curl -X POST http://localhost:8000/api/hardening/firewall/iptables/rules \
  -H "Content-Type: application/json" \
  -d '{"chain": "INPUT", "protocol": "tcp", "dport": 443, "action": "ACCEPT"}'

# 3. Add deny rule
curl -X POST http://localhost:8000/api/hardening/firewall/iptables/rules \
  -H "Content-Type: application/json" \
  -d '{"chain": "INPUT", "protocol": "tcp", "dport": 23, "action": "DROP"}'

# 4. Set default policy
curl -X POST http://localhost:8000/api/hardening/firewall/iptables/default-policy \
  -H "Content-Type: application/json" \
  -d '{"chain": "INPUT", "policy": "DROP"}'
```

### Setup IDS Monitoring
```bash
# 1. Configure Suricata
curl -X PUT http://localhost:8000/api/hardening/ids/suricata/config \
  -H "Content-Type: application/json" \
  -d '{"HOME_NET": "10.0.0.0/8", "RULE_PATH": "/etc/suricata/rules"}'

# 2. Add custom rule
curl -X POST http://localhost:8000/api/hardening/ids/rules \
  -H "Content-Type: application/json" \
  -d '{"rule": "alert tcp any any -> $HOME_NET 443 (msg:\"Test\"; sid:1000001;)", "type": "suricata"}'

# 3. Monitor live threats
curl http://localhost:8000/api/hardening/threats/active
```

## Best Practices

1. **Default deny** — Block all traffic not explicitly allowed
2. **Layer defense** — Multiple security layers
3. **Regular audits** — Schedule periodic hardening checks
4. **Monitor actively** — Real-time threat detection
5. **Document changes** — Track all modifications
6. **Test in staging** — Validate before production
7. **Encrypt everything** — VPN for all external traffic
8. **Segment networks** — Isolate sensitive systems

## Troubleshooting

### Firewall Blocking Legitimate Traffic
```bash
# Check rules
curl http://localhost:8000/api/hardening/firewall/iptables/rules

# Add exception
curl -X POST http://localhost:8000/api/hardening/firewall/iptables/rules \
  -H "Content-Type: application/json" \
  -d '{"chain": "INPUT", "protocol": "tcp", "dport": 8080, "action": "ACCEPT"}'
```

### IDS Not Detecting
```bash
# Check config
curl http://localhost:8000/api/hardening/ids/suricata/config

# Test rules
curl -X POST http://localhost:8000/api/hardening/ids/rules/test \
  -H "Content-Type: application/json" \
  -d '{"rule": "alert tcp any any -> any 80 (msg:\"Test\"; sid:9999999;)", "capture": true}'
```

### VPN Connection Issues
```bash
# Check VPN status
curl http://localhost:8000/api/hardening/vpn/openvpn/status

# Restart VPN
curl -X POST http://localhost:8000/api/hardening/vpn/openvpn/restart
```
