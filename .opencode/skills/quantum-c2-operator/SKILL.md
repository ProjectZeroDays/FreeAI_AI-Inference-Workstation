---
name: quantum-c2-operator
description: >
  Master operator skill for the Quantum C2 framework. Use when the user wants to operate, manage, configure, or understand Quantum C2 capabilities. Covers all operations including reconnaissance, exploitation, post-exploitation, deception, evasion, AI agent teams, session management, device control, and reporting. Triggers on: "operate Quantum C2", "run Quantum C2", "Quantum C2 operations", "C2 framework", "cyber operations", "pentest operations", "red team ops", "execute operation", "deploy C2", "Quantum dashboard".
---

# Quantum C2 Operator Skill

Complete operator guide for the Quantum C2 v5.0.1 framework. Operate all capabilities via API calls from the CLI.

## Framework Overview

| Component | Port | URL |
|-----------|------|-----|
| Backend API | 8000 | http://localhost:8000 |
| Swagger Docs | 8000 | http://localhost:8000/docs |
| Frontend | 3000 | http://localhost:3000 |
| Health Check | 8000 | http://localhost:8000/health |

**Default Credentials:** `admin` / `cyber-warfare-7`

## Authentication

```bash
# Login and save token
TOKEN=$(curl -s -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"cyber-warfare-7"}' \
  | python -c "import sys,json; print(json.load(sys.stdin)['access_token'])")

# Use token in all requests
export C2_TOKEN="$TOKEN"
```

## Quick Operations

### System Status
```bash
curl -H "Authorization: Bearer $C2_TOKEN" http://localhost:8000/api/health
curl -H "Authorization: Bearer $C2_TOKEN" http://localhost:8000/api/dashboard/
curl -H "Authorization: Bearer $C2_TOKEN" http://localhost:8000/api/status
```

### Reconnaissance
```bash
# Network scan
curl -X POST http://localhost:8000/api/network/ \
  -H "Authorization: Bearer $C2_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"target":"192.168.1.0/24","scan_type":"quick"}'

# Domain recon
curl -X POST http://localhost:8000/api/recon/domain/dns \
  -H "Authorization: Bearer $C2_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"domain":"target.com"}'

# OSINT search
curl -H "Authorization: Bearer $C2_TOKEN" \
  "http://localhost:8000/api/osint/search?query=target.com&type=domain"
```

### Exploitation
```bash
# List exploits
curl -H "Authorization: Bearer $C2_TOKEN" http://localhost:8000/api/exploits/

# Deploy exploit
curl -X POST http://localhost:8000/api/exploits/run \
  -H "Authorization: Bearer $C2_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"exploit_name":"force_entry","target":"192.168.1.100"}'

# Generate payload
curl -X POST http://localhost:8000/api/exploits/payload/generate \
  -H "Authorization: Bearer $C2_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"exploit_name":"force_entry","platform":"linux","encoder":"base64"}'
```

### Session Management
```bash
# List sessions
curl -H "Authorization: Bearer $C2_TOKEN" http://localhost:8000/api/sessions/

# Execute command
curl -X POST http://localhost:8000/api/sessions/{id}/execute \
  -H "Authorization: Bearer $C2_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"command":"whoami"}'

# Screenshot
curl -X POST http://localhost:8000/api/sessions/{id}/screenshot \
  -H "Authorization: Bearer $C2_TOKEN"
```

### AI Chatbot
```bash
# Chat with AI
curl -X POST http://localhost:8000/api/chatbot/ \
  -H "Authorization: Bearer $C2_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"message":"Scan 192.168.1.0/24 for vulnerabilities"}'
```

### FORCED ENTRY Operations
```bash
# Seed deception assets
curl -X POST http://localhost:8000/api/forced-entry/deception/assets/seed \
  -H "Authorization: Bearer $C2_TOKEN"

# Seed trigger rules
curl -X POST http://localhost:8000/api/forced-entry/triggers/seed \
  -H "Authorization: Bearer $C2_TOKEN"

# Simulate attack
curl -X POST "http://localhost:8000/api/forced-entry/simulate/attack?attack_type=brute_force&source_ip=192.168.1.100" \
  -H "Authorization: Bearer $C2_TOKEN"

# Run full lifecycle workflow
curl -X POST http://localhost:8000/api/forced-entry/workflows/{id}/execute?target=192.168.1.0/24 \
  -H "Authorization: Bearer $C2_TOKEN"
```

### Agent Teams
```bash
# Create team
curl -X POST http://localhost:8000/api/agents/teams \
  -H "Authorization: Bearer $C2_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"team_size":"standard","model":"agnes-pro"}'

# Run template
curl -X POST http://localhost:8000/api/agents/teams/{id}/run-template \
  -H "Authorization: Bearer $C2_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"template":"full_recon","params":{"target":"192.168.1.0/24"}}'
```

### Device Control
```bash
# List devices
curl -H "Authorization: Bearer $C2_TOKEN" http://localhost:8000/api/devices/

# Execute command
curl -X POST http://localhost:8000/api/devices/{id}/command \
  -H "Authorization: Bearer $C2_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"command":"ls -la /tmp"}'

# Screenshot
curl -X POST http://localhost:8000/api/devices/{id}/screenshot \
  -H "Authorization: Bearer $C2_TOKEN"
```

### Vault & Credentials
```bash
# List credentials
curl -H "Authorization: Bearer $C2_TOKEN" http://localhost:8000/api/vault/credentials

# Add credential
curl -X POST http://localhost:8000/api/vault/credentials \
  -H "Authorization: Bearer $C2_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"name":"Target SSH Key","username":"admin","type":"ssh_key","value":"ssh-rsa ..."}'
```

### Reporting
```bash
# Generate report
curl -X POST http://localhost:8000/api/reports/generate \
  -H "Authorization: Bearer $C2_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"type":"operations","format":"json"}'

# Get audit log
curl -H "Authorization: Bearer $C2_TOKEN" "http://localhost:8000/api/audit/?limit=50"
```

## Deployment
```bash
# One-command deploy (Hetzner)
HETZNER_TOKEN=token ./scripts/deploy-all.sh hetzner cx22 nbg1 c2.yourdomain.com

# Manual deploy (existing server)
./scripts/deploy-all.sh manual 198.51.100.42 c2.yourdomain.com

# Docker local
docker-compose up -d
```

## All API Categories
- `/api/auth` — Authentication (login, register, 2FA)
- `/api/sessions` — C2 session management
- `/api/listeners` — C2 channel listeners
- `/api/network` — Network scanning
- `/api/recon/*` — Domain and OSINT recon
- `/api/exploits/*` — Exploit catalog and deployment
- `/api/postex/*` — Post-exploitation tools
- `/api/forced-entry/*` — Deception, evasion, Pegasus ops
- `/api/agents/*` — AI agent team orchestration
- `/api/devices/*` — Device control
- `/api/vault/*` — Credential vault
- `/api/chatbot/*` — AI chatbot
- `/api/reports/*` — Report generation
- `/api/audit` — Audit logging
- `/api/telemetry/*` — System telemetry
- `/api/dashboard/*` — Dashboard statistics

## Operational Workflows

### Full Exploitation Lifecycle
```
1. Recon: POST /api/network/ (quick scan)
2. Vuln Check: GET /api/vulnerabilities/?target=<ip>
3. Deploy Exploit: POST /api/exploits/run
4. Generate Payload: POST /api/exploits/payload/generate
5. Start Listener: POST /api/listeners/
6. Execute Implant: Run payload
7. Monitor Session: WS /api/sessions/ws/{id}
8. Post-Exploit: POST /api/postex/full-lifecycle
```

### Deception Network Deployment
```
1. Seed Assets: POST /api/forced-entry/deception/assets/seed
2. Seed Triggers: POST /api/forced-entry/triggers/seed
3. Simulate Attack: POST /api/forced-entry/simulate/attack
4. Monitor: GET /api/forced-entry/events
```

### AI Agent Team Operation
```
1. Create Team: POST /api/agents/teams
2. Run Template: POST /api/agents/teams/{id}/run-template
3. Monitor: GET /api/agents/teams/{id}
4. Results: GET /api/agents/teams/{id}/tasks
```

## Skills Reference
- `quantum-c2-recon` — Reconnaissance operations
- `quantum-c2-exploit` — Exploitation and payload generation
- `quantum-c2-postex` — Post-exploitation and session management
- `quantum-c2-deception` — Deception and evasion operations
- `quantum-c2-forced-entry` — Full lifecycle exploitation
- `quantum-c2-agents` — AI agent team orchestration
- `quantum-c2-sessions` — C2 session management
- `quantum-c2-devices` — Device control operations
- `quantum-c2-listeners` — C2 listener management
- `quantum-c2-vault` — Credential management
- `quantum-c2-reporting` — Report generation
- `quantum-c2-deploy` — Deployment and configuration
