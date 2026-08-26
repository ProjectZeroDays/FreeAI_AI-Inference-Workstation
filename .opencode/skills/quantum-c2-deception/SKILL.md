---
name: quantum-c2-deception
description: >
  Deception, evasion, and honeytrap operations for Quantum C2. Use when the user needs to deploy deception assets (honeypots, honeytokens, canaries), configure evasion techniques, set up event triggers, or simulate attacks to test defenses. Triggers on: "deception", "honeypot", "evasion", "honeytoken", "canary", "tarpit", "attack simulation", "test defenses", "deploy honeypot", "evasion techniques", "event triggers", "intrusion detection".
---

# Quantum C2 Deception & Evasion Skill

Deploy deception infrastructure and configure intelligent evasion responses.

## Deception Assets

### List Assets
```bash
curl -H "Authorization: Bearer $C2_TOKEN" http://localhost:8000/api/forced-entry/deception/assets
```

### Seed Default Assets
```bash
curl -X POST http://localhost:8000/api/forced-entry/deception/assets/seed \
  -H "Authorization: Bearer $C2_TOKEN"
```

### Create Asset
```bash
curl -X POST http://localhost:8000/api/forced-entry/deception/assets \
  -H "Authorization: Bearer $C2_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Fake SSH Honeypot",
    "type": "honeypot",
    "ip_address": "10.0.0.50",
    "port": 22,
    "os_fingerprint": "Debian 11",
    "service_banner": "SSH-2.0-OpenSSH_8.4p1 Debian-5",
    "triggers": ["brute_force", "port_scan"],
    "honeytokens": ["admin:password123", "root:toor"]
  }'
```

### Toggle Asset
```bash
curl -X PUT http://localhost:8000/api/forced-entry/deception/assets/{id}/toggle \
  -H "Authorization: Bearer $C2_TOKEN"
```

### Delete Asset
```bash
curl -X DELETE http://localhost:8000/api/forced-entry/deception/assets/{id} \
  -H "Authorization: Bearer $C2_TOKEN"
```

### Simulate Interaction
```bash
curl -X POST http://localhost:8000/api/forced-entry/deception/assets/{id}/simulate \
  -H "Authorization: Bearer $C2_TOKEN"
```

## Asset Types

| Type | Description | Use Case |
|------|-------------|----------|
| `honeypot` | Fake service | Attract scanners |
| `honeytoken` | Fake credentials | Detect credential use |
| `canary_token` | Data canaries | Detect data access |
| `decoy_system` | Full fake system | Lure attackers in |
| `dark_pattern` | Hidden API endpoints | Trap automated tools |
| `digital_canary` | File/registry canaries | Detect persistence |
| `honeydoor` | Fake open port | Capture probes |
| `honeytrap` | Fake sensitive data | Lure data theft |

## Evasion Techniques

### List Techniques
```bash
curl -H "Authorization: Bearer $C2_TOKEN" http://localhost:8000/api/forced-entry/evasion/techniques
```

### Create Evasion Config
```bash
curl -X POST http://localhost:8000/api/forced-entry/evasion/configs \
  -H "Authorization: Bearer $C2_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "enabled": true,
    "technique": "polymorphic_code",
    "trigger_event": "brute_force",
    "latency_ms": 50,
    "jitter_percent": 30,
    "beacon_intervals": [30, 60, 120, 300],
    "sleep_cycles": [60, 300, 900, 3600]
  }'
```

### Technique Categories

**Code Transformation:**
- `polymorphic_code` — Signature-changing code
- `metamorphic_engine` — Self-modifying logic
- `encoding_obfuscation` — Multi-layer encoding

**Execution:**
- `memory_only` — No disk writes
- `fileless_execution` — Living-off-the-land
- `living_off_the_land` — Legitimate tools

**Communication:**
- `dns_tunneling` — DNS query encoding
- `icmp_tunneling` — ICMP packet hiding
- `https_c2` — TLS-encrypted C2
- `domain_fronting` — CDN domain masking
- `tor_routing` — Tor network routing
- `socks_proxy_chain` — Multi-hop proxies

**Anti-Analysis:**
- `vm_detect` — Virtual machine detection
- `debugger_detect` — Debugger detection
- `sandbox_escape` — Sandbox identification
- `anti_dump` — Memory protection

## Event Triggers

### List Triggers
```bash
curl -H "Authorization: Bearer $C2_TOKEN" http://localhost:8000/api/forced-entry/triggers
```

### Seed Default Triggers
```bash
curl -X POST http://localhost:8000/api/forced-entry/triggers/seed \
  -H "Authorization: Bearer $C2_TOKEN"
```

### Check Triggers
```bash
curl -X POST "http://localhost:8000/api/forced-entry/triggers/check?event_type=brute_force&source_ip=192.168.1.100" \
  -H "Authorization: Bearer $C2_TOKEN"
```

### 20 Trigger Types

| Trigger | Severity | Typical Response |
|---------|----------|------------------|
| `port_scan` | medium | rotate_identity, deploy_canary |
| `brute_force` | high | activate_evasion, deploy_honeydoor |
| `vulnerability_scan` | high | activate_evasion, log_indicators |
| `credential_stuffing` | critical | lock_accounts, deploy_honeytoken |
| `zero_day_probe` | critical | isolate_target, capture_artifacts |
| `behavioral_anomaly` | high | activate_evasion, deploy_decoy |
| `scanner_signature` | low | degrade_service |
| `auth_anomaly` | high | lock_accounts |
| `payload_probe` | critical | activate_evasion |
| `protocol_violation` | high | activate_evasion |

## Attack Simulation

### Simulate Single Attack
```bash
curl -X POST "http://localhost:8000/api/forced-entry/simulate/attack?attack_type=brute_force&source_ip=192.168.1.100" \
  -H "Authorization: Bearer $C2_TOKEN"
```

### Simulate Burst (1-500 attacks)
```bash
curl -X POST "http://localhost:8000/api/forced-entry/simulate/burst?count=50&source_ip=10.0.0.1" \
  -H "Authorization: Bearer $C2_TOKEN"
```

## Analytics & Reporting

### Get Summary
```bash
curl -H "Authorization: Bearer $C2_TOKEN" http://localhost:8000/api/forced-entry/analytics/summary
```

### Get Events
```bash
curl -H "Authorization: Bearer $C2_TOKEN" "http://localhost:8000/api/forced-entry/events?limit=100"
```

### Reset Analytics
```bash
curl -X POST http://localhost:8000/api/forced-entry/analytics/reset \
  -H "Authorization: Bearer $C2_TOKEN"
```

## Configuration

```bash
# Get config
curl -H "Authorization: Bearer $C2_TOKEN" http://localhost:8000/api/forced-entry/config

# Update config
curl -X PUT http://localhost:8000/api/forced-entry/config \
  -H "Authorization: Bearer $C2_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "auto_start": false,
    "max_concurrent_ops": 5,
    "deception_enabled": true,
    "evasion_enabled": true,
    "trigger_sensitivity": "medium",
    "auto_evasion_response": true
  }'
```

## Deception Deployment Workflow

```bash
# 1. Seed assets and triggers
curl -X POST http://localhost:8000/api/forced-entry/deception/assets/seed
curl -X POST http://localhost:8000/api/forced-entry/triggers/seed

# 2. Verify deployment
curl -H "Authorization: Bearer $C2_TOKEN" http://localhost:8000/api/forced-entry/deception/assets
curl -H "Authorization: Bearer $C2_TOKEN" http://localhost:8000/api/forced-entry/triggers

# 3. Simulate attack to test
curl -X POST "http://localhost:8000/api/forced-entry/simulate/attack?attack_type=brute_force&source_ip=192.168.1.100"

# 4. Check results
curl -H "Authorization: Bearer $C2_TOKEN" "http://localhost:8000/api/forced-entry/events?limit=50"
curl -H "Authorization: Bearer $C2_TOKEN" http://localhost:8000/api/forced-entry/analytics/summary
```
