---
name: quantum-c2-deception
description: >
  Quantum C2 deception, evasion, and forced entry operations skill. Use when the user needs to deploy deception assets (honeypots, honeytokens, canaries), configure evasion techniques, set up event triggers, run Pegasus-style operations, execute full lifecycle exploitation workflows, or generate operational reports. Triggers on: "deception", "honeypot", "evasion", "forced entry", "pegasus", "tarpit", "canary token", "attack simulation", "exploit lifecycle", "operations report", "AI-driven exploitation".
---

# Quantum C2 Deception & Forced Entry Skill

Deploy deception infrastructure, configure intelligent evasion, and execute full-spectrum forced entry operations.

## Deception Grid

### Asset Types
| Type | Description | Use Case |
|------|-------------|----------|
| `honeypot` | Fake service emulating real software | Attract scanners |
| `honeytoken` | Fake credentials/tokens | Detect credential use |
| `canary_token` | Database/data canaries | Detect data access |
| `decoy_system` | Full fake system | Lure attackers in |
| `dark_pattern` | Hidden API endpoints | Trap automated tools |
| `digital_canary` | File/registry canaries | Detect persistence |
| `emoacket` | Fake emergency alert | Test response |
| `honeydoor` | Fake open port | Capture probes |
| `honeytrap` | Fake sensitive data | Lure data theft |

### API Endpoints
```bash
# List assets
GET /api/forced-entry/deception/assets

# Create asset
POST /api/forced-entry/deception/assets

# Seed defaults
POST /api/forced-entry/deception/assets/seed

# Toggle asset
PUT /api/forced-entry/deception/assets/{id}/toggle

# Delete asset
DELETE /api/forced-entry/deception/assets/{id}

# Simulate interaction
POST /api/forced-entry/deception/assets/{id}/simulate
```

### Asset Creation
```bash
curl -X POST http://localhost:8000/api/forced-entry/deception/assets \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Fake SSH Server",
    "type": "honeypot",
    "ip_address": "10.0.0.50",
    "port": 22,
    "os_fingerprint": "Debian 11",
    "service_banner": "SSH-2.0-OpenSSH_8.4p1 Debian-5",
    "triggers": ["brute_force", "port_scan"],
    "honeytokens": ["admin:password123", "root:toor"]
  }'
```

### Seeded Assets
- SSH Honeypot (Debian)
- Fake Admin Portal
- Canary Database
- Decoy File Server
- Fake VPN Gateway
- Shadow API Endpoint
- Canary SSH Key
- Fake Cloud Storage

## Evasion Engine

### Technique Categories
| Category | Techniques |
|----------|------------|
| **Code Transformation** | Polymorphic, Metamorphic, Encoding/Obfuscation |
| **Execution** | Memory-only, Fileless, Living-off-the-Land |
| **Communication** | DNS/ICMP/QUIC/DoH Tunneling, HTTPS C2, Domain Fronting, SSH Jump, SOCKS Chain, Tor, WebSockets |
| **Timing** | Beacon Jitter, Sleep Cycles, Timing Control |
| **Anti-Analysis** | VM/Debug/Sandbox Detection, Anti-Dump, Hash Spoofing |

### Evasion Configuration
```bash
# List configs
GET /api/forced-entry/evasion/configs

# Create config
POST /api/forced-entry/evasion/configs
{
  "enabled": true,
  "technique": "polymorphic_code",
  "trigger_event": "brute_force",
  "latency_ms": 50,
  "jitter_percent": 30,
  "beacon_intervals": [30, 60, 120, 300],
  "sleep_cycles": [60, 300, 900, 3600],
  "environment_checks": {
    "vm_detect": true,
    "debugger_detect": true,
    "sandbox_detect": true
  }
}

# List techniques
GET /api/forced-entry/evasion/techniques
```

## Event Triggers

### 20 Trigger Types
| Trigger | Severity | Typical Response |
|---------|----------|------------------|
| `port_scan` | medium | rotate_identity, deploy_canary |
| `brute_force` | high | activate_evasion, deploy_honeydoor |
| `vulnerability_scan` | high | activate_evasion, log_indicators |
| `credential_stuffing` | critical | lock_accounts, deploy_honeytoken |
| `ssl_helo_anomaly` | medium | degrade_service |
| `dns_query_pattern` | low | log_indicators |
| `user_agent_anomaly` | low | log_indicators |
| `geo_anomaly` | medium | rotate_identity |
| `behavioral_anomaly` | high | activate_evasion, deploy_decoy |
| `time_anomaly` | low | log_indicators |
| `repetitive_patterns` | medium | deploy_canary |
| `scanner_signature` | low | degrade_service |
| `zero_day_probe` | critical | isolate_target, capture_artifacts |
| `side_channel` | high | activate_evasion |
| `network_probe` | medium | deploy_canary |
| `service_enum` | low | degrade_service |
| `auth_anomaly` | high | lock_accounts |
| `payload_probe` | critical | activate_evasion |
| `encryption_anomaly` | medium | rotate_identity |
| `protocol_violation` | high | activate_evasion |

### Trigger Rules
```bash
# List rules
GET /api/forced-entry/triggers

# Seed defaults
POST /api/forced-entry/triggers/seed

# Create rule
POST /api/forced-entry/triggers
{
  "name": "Brute Force Response",
  "trigger_type": "brute_force",
  "conditions": {"severity": ["high", "critical"], "threshold": 10},
  "actions": ["activate_evasion", "deploy_honeydoor", "alert_operator"],
  "priority": 90,
  "cooldown_seconds": 60
}

# Check triggers
POST /api/forced-entry/triggers/check?event_type=brute_force&source_ip=192.168.1.100
```

## Pegasus Operations

### Module Categories
| Category | Modules |
|----------|---------|
| **Info Collection** | Keystroke logging, screen capture, audio monitoring, camera, contacts, messages, GPS, calls, email, files, cloud, app data |
| **Remote Control** | Remote control, command execution, file management, app management, settings |
| **Exploitation** | Zero-day, CVE exploitation, social engineering, website clone, QR attack, location spoofing, SMS/call interception |
| **Persistence** | Persistence mechanism, bootkit, firmware backdoor, credential theft, keychain access |
| **Evasion** | Anti-forensics, data encryption, log manipulation, timeline manipulation |

### Operation Management
```bash
# List operations
GET /api/forced-entry/pegasus/operations

# Create operation
POST /api/forced-entry/pegasus/operations
{
  "name": "Operation Nightingale",
  "target": "192.168.1.100",
  "objective": "iPhone surveillance via iMessage",
  "modules": ["keystroke_logging", "screen_capture", "location_tracking", "message_sync", "credential_theft"]
}

# Start operation
POST /api/forced-entry/pegasus/operations/{id}/start

# Execute module
POST /api/forced-entry/pegasus/operations/{id}/execute
{
  "module_id": "keystroke_logging",
  "parameters": {}
}

# Complete operation
POST /api/forced-entry/pegasus/operations/{id}/complete

# Seed defaults
POST /api/forced-entry/pegasus/operations/seed
```

## Exploitation Workflows

### Available Workflows
| Workflow | Phases | Use Case |
|----------|--------|----------|
| **Full Lifecycle** | 9 | Complete recon-to-exfil |
| **Quick Access** | 4 | Time-critical operations |
| **Advanced Persistence** | 7 | Deep implant deployment |
| **Data Exfiltration** | 5 | Targeted data theft |

### Workflow Execution
```bash
# List workflows
GET /api/forced-entry/workflows

# Seed workflows
POST /api/forced-entry/workflows/seed

# Execute workflow
POST /api/forced-entry/workflows/{id}/execute?target=192.168.1.100

# Check status
GET /api/forced-entry/workflows/{id}/status
```

### Full Lifecycle Phases
1. **Reconnaissance** — nmap, OS fingerprint, service enum
2. **Weaponization** — exploit selection, payload generation
3. **Delivery** — payload delivery, vector selection
4. **Exploitation** — exploit execution, access confirmation
5. **Installation** — persistence setup, backdoor install
6. **Command & Control** — C2 establishment, beacon config
7. **Actions on Objectives** — lateral movement, priv esc, data access
8. **Exfiltration** — data staging, transfer channel, data transfer
9. **Cleanup** — log cleanup, artifact removal, trace elimination

## Attack Simulation

```bash
# Simulate single attack
POST /api/forced-entry/simulate/attack?attack_type=brute_force&source_ip=192.168.1.100

# Simulate burst (1-500 attacks)
POST /api/forced-entry/simulate/burst?count=50&source_ip=10.0.0.1

# Response includes:
{
  "attack_type": "brute_force",
  "source_ip": "192.168.1.100",
  "actions_fired": ["activate_evasion", "deploy_honeydoor"],
  "severity": "high"
}
```

## AI-Driven Full Lifecycle

### Web Card Features
- **AI Model Selection** — Choose from available providers (Venice, OpenAI, Agnes, etc.)
- **Target Configuration** — Set target IP/network
- **Workflow Selection** — Choose exploitation workflow
- **Autonomous Execution** — AI drives each phase
- **Progress Visualization** — Real-time phase tracking
- **Phase-by-Phase Execution** — Each phase executes with status updates

### Execution Flow
```
1. Select AI model
2. Input target
3. Select workflow
4. Click "Launch Autonomous Execution"
5. Monitor progress through phases
6. Review results
```

## Reporting

### Generate Report
```bash
POST /api/forced-entry/analytics/summary
```

### Report Contents
- Operations summary
- Asset statistics
- Trigger firing history
- Evasion configuration
- Pegasus operation results
- Event timeline

### Export
- JSON format for analysis
- Includes all operational metadata

## Configuration

```bash
# Get config
GET /api/forced-entry/config

# Update config
PUT /api/forced-entry/config
{
  "auto_start": false,
  "max_concurrent_ops": 5,
  "deception_enabled": true,
  "evasion_enabled": true,
  "pegasus_enabled": true,
  "trigger_sensitivity": "medium",
  "log_level": "INFO",
  "retention_days": 30,
  "alert_on_detection": true,
  "auto_evasion_response": true
}
```

## Operational Playbook

### 1. Deploy Deception Network
```bash
# Seed assets and triggers
POST /api/forced-entry/deception/assets/seed
POST /api/forced-entry/triggers/seed

# Verify deployment
GET /api/forced-entry/deception/assets
GET /api/forced-entry/triggers
```

### 2. Configure Evasion
```bash
# Create evasion configs
POST /api/forced-entry/evasion/configs
{
  "technique": "polymorphic_code",
  "trigger_event": "brute_force",
  "enabled": true
}
```

### 3. Run Full Lifecycle Operation
```bash
# Seed workflows
POST /api/forced-entry/workflows/seed

# Execute via AI
POST /api/forced-entry/workflows/{id}/execute?target=192.168.1.0/24
```

### 4. Monitor & Report
```bash
# Check analytics
GET /api/forced-entry/analytics/summary

# View events
GET /api/forced-entry/events?limit=100

# Generate report
POST /api/forced-entry/analytics/summary (with export)
```

## Integration with Chatbot

The AI chatbot can execute FORCED ENTRY operations via tool calls:
```
User: "Deploy deception assets on 10.0.0.0/24"
→ AI calls: POST /api/forced-entry/deception/assets/seed
→ Returns: Asset deployment status
```

Available chatbot tools:
- `scan_network` — Network reconnaissance
- `device_screenshot` — Capture device screen
- `device_camera` — Activate camera
- `device_microphone` — Activate microphone
- `postex_privilege_escalation` — Privilege escalation
- `postex_credential_dump` — Credential harvesting
- `postex_persistence` — Establish persistence
- `postex_data_exfil` — Data exfiltration
